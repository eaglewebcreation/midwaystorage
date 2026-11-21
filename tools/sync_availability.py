#!/usr/bin/env python3
"""Sync each unit's Open to rent / Waitlist status from the public CCStorage rental pages.

Reads the two public "find units" pages (Midway Storage and Midway Ventures), finds each
unit type by its CCStorage unit-type id, and reads whether its button says "Rent Now" or
"Join Waiting List". Updates "status" in site-config.json only when every unit was read.

Exit codes:
  0  read every unit (prints changed=true/false to $GITHUB_OUTPUT when set)
  2  could not read one or more units: nothing is changed, the site keeps its last labels

Runs plain HTTP first. If the page only fills in with JavaScript, it falls back to a
headless browser (playwright), when that is installed.
"""
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "site-config.json"

STORAGE_URL = "https://midwaystorage.ccstorage.com/find_units/loc_5a534a739fbe3eda662020b16b544b64"
VENTURES_URL = "https://midwayventuresllc.ccstorage.com/find_units/loc_b07c6c20aebd052257591ce9104c7cea"

# site-config unit id -> CCStorage unit-type id (from the Rent Now / Join Waiting List links)
STORAGE_TYPES = {
    "A": "sut_f6593b398d92dd881fdbb19a817eaab4",
    "B": "sut_6b8ff7b58d7ac6618500f79da7c5480f",
    "C": "sut_5083a066e6630b03c31ece837d37feea",
    "D": "sut_01e4c29bbd04fbab2a2d14ff2cf0d5d5",
    "E": "sut_112aea48a2bf5a8ac51a1deb01839bf2",
    "F": "sut_c6fee50368942ddc4bee1753918c94a7",
    "G": "sut_2a6f811cd62b78c47717d67e9c89c16d",
    "L": "sut_1aeced30fbf04cc48bb7dd4577373e94",
    "M": "sut_c251ca667f50bbe522546cf66bc7f58b",
    "S": "sut_76263921f2cd70d1187e3286a4f03a93",
    "XL": "sut_6146cfc167c6e0ddffbd7e352731b49a",
    "SHOP": "sut_a7c75da29271d6b12410c872f2088419",
    "HEAT": "sut_df754bcd75d56487981756bc745fc229",
    "BIG": "sut_3bd3f8c30e4fdd90a8cf1e2c0f8616d8",
    "PARK": "sut_647a3cd7344759d3c9cbb4f0f109a28d",
}
VENTURES_TYPE = "sut_79fc62e42b027741d8a8c5c8484f78e5"

UA = "Mozilla/5.0 (compatible; MidwayStorageSiteSync/1.0)"


def fetch_plain(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def fetch_rendered(url):
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(user_agent=UA)
        page.goto(url, wait_until="networkidle", timeout=60000)
        out = page.content()
        b.close()
        return out


def status_for(page_html, type_id):
    """Return 'rent', 'waitlist' or None, from the link that carries this unit-type id."""
    for m in re.finditer(r"<a\b[^>]*storage_unit_type_id=" + re.escape(type_id) + r"[^>]*>(.*?)</a>",
                         page_html, re.S | re.I):
        text = html.unescape(re.sub(r"<[^>]+>", " ", m.group(1)))
        text = " ".join(text.split()).lower()
        if "waiting list" in text or "waitlist" in text:
            return "waitlist"
        if "rent now" in text or text == "rent":
            return "rent"
    return None


def read_page(url, wanted):
    """wanted: {key: type_id}. Returns ({key: status}, method)."""
    found, method = {}, "plain"
    try:
        page = fetch_plain(url)
        found = {k: status_for(page, t) for k, t in wanted.items()}
    except Exception as e:  # network error: try the browser before giving up
        print(f"plain fetch failed for {url}: {e}", file=sys.stderr)
    if any(v is None for v in found.values()) or not found:
        page = fetch_rendered(url)
        if page:
            method = "browser"
            found = {k: status_for(page, t) for k, t in wanted.items()}
    return found, method


def main():
    cfg = json.loads(CONFIG.read_text())
    storage, m1 = read_page(STORAGE_URL, STORAGE_TYPES)
    ventures, m2 = read_page(VENTURES_URL, {"ventures": VENTURES_TYPE})
    print(f"read storage page via {m1}, ventures page via {m2}")

    missing = [k for k in STORAGE_TYPES if storage.get(k) is None]
    if ventures.get("ventures") is None:
        missing.append("ventures")
    if missing:
        print("COULD NOT READ: " + ", ".join(missing) + ". Keeping the last labels; nothing changed.")
        return 2

    changes = []
    for u in cfg["units"]:
        new = storage[u["id"]]
        if u["status"] != new:
            changes.append(f'{u["name"]}: {u["status"]} -> {new}')
            u["status"] = new
    v = cfg["ventures"]
    if v["status"] != ventures["ventures"]:
        changes.append(f'{v["name"]}: {v["status"]} -> {ventures["ventures"]}')
        v["status"] = ventures["ventures"]

    for u in cfg["units"]:
        print(f'  {u["id"]:5} {u["status"]}')
    print(f'  {"VENT":5} {v["status"]}')

    if changes:
        # Edit only the status values, in file order (units, then the Ventures warehouse),
        # so the rest of site-config.json stays exactly as written.
        text = CONFIG.read_text()
        order = [u["status"] for u in cfg["units"]] + [v["status"]]
        spots = list(re.finditer(r'"status": "(rent|waitlist)"', text))
        if len(spots) != len(order):
            print(f"site-config.json has {len(spots)} status fields, expected {len(order)}; not writing.")
            return 2
        for m, new in reversed(list(zip(spots, order))):
            text = text[:m.start(1)] + new + text[m.end(1):]
        CONFIG.write_text(text)
        print("CHANGED: " + "; ".join(changes))
    else:
        print("No changes.")
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a") as f:
            f.write(f"changed={'true' if changes else 'false'}\n")
            f.write("summary=" + ("; ".join(changes) if changes else "none") + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
