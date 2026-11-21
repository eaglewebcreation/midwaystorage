#!/usr/bin/env python3
"""Build the static Midway Storage site into /public.

Plain HTML/CSS/JS, nothing runs on the server. This script keeps the shared
pieces (header, footer, unit cards, schema) and the owner facts in
/site-config.json consistent across every page.

    python3 tools/build_site.py                       # production (midwaystoragewy.com)
    SITE_URL=https://midwaystorage.eaglewebcreation.com python3 tools/build_site.py   # preview
"""
import datetime
import hashlib
import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
C = json.loads((ROOT / "site-config.json").read_text())
K = C["CONFIRM"]
SITE = (os.environ.get("SITE_URL") or C["siteUrl"]).rstrip("/")
TODAY = datetime.date.today().isoformat()
YEAR = datetime.date.today().year
BIZ_ID = SITE + "/#business"
PHONE = C["phoneDisplay"]
TEL = "tel:" + C["phoneTel"]
RENT = html.escape(C["rentUrl"], quote=True)
SIGNIN = html.escape(C["signInUrl"], quote=True)
VRENT = html.escape(C["venturesRentUrl"], quote=True)
ADDR_LINE = f'{C["street"]}, {C["city"]}, {C["region"]} {C["zip"]}'
DIRECTIONS = ("https://www.google.com/maps/dir/?api=1&amp;destination="
              "Midway+Storage,+1780+US-310,+Lovell,+WY+82431")
AS_OF = C["pricesAsOf"]
UNITS = {u["id"]: u for u in C["units"]}

PH_TEXT = "[waiting on owner confirmation]"


def ph(todo):
    """Visible placeholder plus an HTML TODO comment that says what is missing."""
    return f'<!-- TODO: confirm with owner: {todo} --><span class="tbd">{PH_TEXT}</span>'


def minify_css(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([{};:,>])\s*", r"\1", s)
    return s.replace(";}", "}").strip()


JS_V = hashlib.sha1((PUB / "assets" / "js" / "site.js").read_bytes()).hexdigest()[:8]
CSS_MIN = minify_css((ROOT / "src" / "site.css").read_text())

ICON = {
    "phone": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z"/></svg>',
    "key": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3"/></svg>',
    "left": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><path d="M15 5l-7 7 7 7"/></svg>',
    "right": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6"><path d="M9 5l7 7-7 7"/></svg>',
}

# ---------------------------------------------------------------- towns
# drive = fastest Google Maps route from the facility, read 2026-11-21
TOWNS = [
    {"slug": "lovell", "url": "/storage-lovell-wy/", "name": "Lovell", "st": "WY", "drive": "about 5 minutes", "mi": "about 3 miles", "short": "3 mi"},
    {"slug": "powell", "url": "/storage-powell-wy/", "name": "Powell", "st": "WY", "drive": "22 minutes", "mi": "19.6 miles", "short": "22 min"},
    {"slug": "cody", "url": "/storage-cody-wy/", "name": "Cody", "st": "WY", "drive": "47 minutes", "mi": "43.4 miles", "short": "47 min"},
    {"slug": "greybull", "url": "/storage-greybull-wy/", "name": "Greybull", "st": "WY", "drive": "36 minutes", "mi": "35.2 miles", "short": "36 min"},
    {"slug": "basin", "url": "/storage-basin-wy/", "name": "Basin", "st": "WY", "drive": "44 minutes", "mi": "42.8 miles", "short": "44 min"},
    {"slug": "bridger", "url": "/storage-bridger-mt/", "name": "Bridger", "st": "MT", "drive": "42 minutes", "mi": "43.8 miles", "short": "42 min"},
    {"slug": "billings", "url": "/storage-billings-mt/", "name": "Billings", "st": "MT", "drive": "1 hour 27 minutes", "mi": "88.3 miles", "short": "1 hr 27 min"},
]
TOWN = {t["slug"]: t for t in TOWNS}
STATE = {"WY": "Wyoming", "MT": "Montana"}


def city(name, st):
    return {"@type": "City", "name": f"{name}, {st}", "containedInPlace": {"@type": "State", "name": STATE[st]}}


# ---------------------------------------------------------------- shell pieces
NAV = [
    ("/storage-units/", "Units &amp; Prices"),
    ("/storage-units/#shops", "Shops &amp; Parking"),
    ("/#reviews", "Reviews"),
    ("/contact/", "Contact"),
]


def header(current):
    items = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == current else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    items.append(f'<li class="nav-extra"><a href="{SIGNIN}">Pay Bill / Tenant Sign In</a></li>')
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/" aria-label="Midway Storage home"><img src="/assets/img/logo.svg" width="138" height="55" alt="Midway Storage logo"></a>
    <nav class="main-nav" id="main-nav" aria-label="Main"><ul>{"".join(items)}</ul></nav>
    <div class="header-actions">
      <a class="btn btn-line btn-pay" href="{SIGNIN}">Pay Bill</a>
      <a class="btn btn-red" href="{RENT}">Rent a Unit</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="main-nav"><span class="nav-toggle-bars" aria-hidden="true"></span><span class="nav-label">Menu</span></button>
    </div>
  </div>
</header>'''


def footer():
    towns = "".join(f'<li><a href="{t["url"]}">Storage near {t["name"]}, {t["st"]}</a></li>' for t in TOWNS)
    email = (f'<a href="mailto:{html.escape(K["email"])}">{html.escape(K["email"])}</a>' if K.get("email")
             else '<!-- TODO: confirm with owner: email address for the footer -->')
    return f'''<footer class="site-footer">
  <div class="trust"><div class="wrap">Rated {C["google"]["rating"]} out of 5 on Google from {C["google"]["count"]} reviews</div></div>
  <div class="wrap footer-grid">
    <div>
      <a class="footer-logo" href="/"><img src="/assets/img/logo-white.svg" width="170" height="67" alt="Midway Storage logo" loading="lazy"></a>
      <address>
        <p><strong style="color:#fff">Midway Storage</strong><br>{C["street"]}<br>{C["city"]}, {C["region"]} {C["zip"]}</p>
        <p><a href="{TEL}">{PHONE}</a><br>{email}</p>
        <p>Access 24 hours a day, 7 days a week</p>
      </address>
    </div>
    <div>
      <h2>Tenants</h2>
      <ul>
        <li><a href="{RENT}">Rent a unit online</a></li>
        <li><a href="{SIGNIN}">Pay bill / tenant sign in</a></li>
        <li><a href="/storage-units/">Unit sizes &amp; prices</a></li>
        <li><a href="/faq/">FAQ</a></li>
      </ul>
    </div>
    <div>
      <h2>Midway Storage</h2>
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/storage-units/#shops">Shops, warehouse &amp; parking</a></li>
        <li><a href="/contact/">Contact &amp; directions</a></li>
        <li><a href="{DIRECTIONS}">Open in Google Maps</a></li>
      </ul>
    </div>
    <div>
      <h2>Nearby towns</h2>
      <ul>{towns}</ul>
    </div>
  </div>
  <div class="wrap footer-bottom">
    <span>&copy; {YEAR} Midway Storage, a division of {C["legalName"]}</span>
    <span>Built by <a href="https://eaglewebcreation.com/">Eagle Web Creations</a></span>
  </div>
</footer>
<nav class="mobile-bar" aria-label="Quick actions">
  <a class="mb-call" href="{TEL}">{ICON["phone"]}Call</a>
  <a class="mb-rent" href="{RENT}">Rent a Unit</a>
</nav>'''


def breadcrumbs_html(trail):
    lis = []
    for i, (n, u) in enumerate(trail):
        if i == len(trail) - 1:
            lis.append(f'<li><span aria-current="page">{n}</span></li>')
        else:
            lis.append(f'<li><a href="{u}">{n}</a></li>')
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'


def page_hero(kicker, h1, intro, trail):
    return f'''<section class="page-hero">
  <div class="wrap">
    {breadcrumbs_html(trail)}
    <span class="kicker">{kicker}</span>
    <h1>{h1}</h1>
    <p>{intro}</p>
  </div>
</section>'''


def cta_band(heading, text, sid="cta"):
    return f'''<section class="cta-band" aria-labelledby="{sid}-h">
  <div class="wrap">
    <h2 id="{sid}-h">{heading}</h2>
    <p>{text}</p>
    <div class="btn-row"><a class="btn btn-red" href="{RENT}">Rent a Unit</a><a class="btn btn-line" href="{TEL}">{ICON["phone"]}Call {PHONE}</a></div>
  </div>
</section>'''


def map_embed():
    q = f'{C["lat"]},{C["lng"]}'
    return f'''<div class="map-embed"><iframe src="https://maps.google.com/maps?q={q}&amp;z=13&amp;output=embed" title="Map: Midway Storage, {ADDR_LINE}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
<p class="note"><a href="{DIRECTIONS}">Get driving directions to Midway Storage</a></p>'''


def faq_html(items, hl="h3"):
    out = ['<div class="faq-list">']
    for q, a, slug in items:
        out.append(f'<details class="faq-item" id="{slug}"><summary><{hl}>{q}</{hl}></summary><div class="faq-a">{a}</div></details>')
    out.append("</div>")
    return "\n".join(out)


def strip_tags(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(re.sub(r"\s+", " ", s)).strip()


def faq_schema(items, url):
    return {"@context": "https://schema.org", "@type": "FAQPage", "@id": url + "#faq",
            "mainEntity": [{"@type": "Question", "name": strip_tags(q),
                            "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}}
                           for q, a, _ in items if PH_TEXT not in a]}


def breadcrumb_schema(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": html.unescape(n), "item": SITE + u}
                                for i, (n, u) in enumerate(trail)]}


def num(p):
    return float(p.replace(",", ""))


def business_schema():
    low = min(num(u["rent"]) for u in C["units"])
    high = max(num(u["rent"]) for u in C["units"])
    s = {
        "@context": "https://schema.org",
        "@type": "SelfStorage",
        "@id": BIZ_ID,
        "name": C["name"],
        "legalName": C["legalName"],
        "url": SITE + "/",
        "logo": SITE + "/assets/img/logo-640.png",
        "image": [SITE + "/assets/img/exterior-blue-1045.jpg", SITE + "/assets/img/unit-l12-593.jpg"],
        "description": "Drive-up storage units, shop space and outdoor parking on US-310 in Lovell, Wyoming. "
                       "Eleven unit sizes from 8x15 to 14x45, units up to 15 ft tall, 24/7 access, no long-term "
                       "commitment, rent and pay online.",
        "telephone": C["phoneTel"],
        "address": {"@type": "PostalAddress", "streetAddress": C["street"], "addressLocality": C["city"],
                    "addressRegion": C["region"], "postalCode": C["zip"], "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": C["lat"], "longitude": C["lng"]},
        "hasMap": html.unescape(DIRECTIONS),
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "opens": "00:00", "closes": "23:59"}],
        "areaServed": [city(t["name"], t["st"]) for t in TOWNS] + [
            {"@type": "AdministrativeArea", "name": "Big Horn County, Wyoming"},
            {"@type": "AdministrativeArea", "name": "Park County, Wyoming"},
            {"@type": "AdministrativeArea", "name": "Carbon County, Montana"}],
        "priceRange": f"${low:,.0f} - ${high:,.0f} per month",
        "currenciesAccepted": "USD",
        "paymentAccepted": "Credit card, debit card, ACH bank draft",
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True}
                           for n in ["24-hour access", "Drive-up units", "Online rental", "Online bill pay",
                                     "Automatic payments", "Units up to 15 ft tall", "Heated shop available"]],
        "hasOfferCatalog": {
            "@type": "OfferCatalog", "name": "Storage units and shop space",
            "itemListElement": [{
                "@type": "Offer",
                "name": unit_title(u),
                "url": C["rentUrl"],
                "availability": "https://schema.org/InStock" if u["status"] == "rent" else "https://schema.org/LimitedAvailability",
                "priceSpecification": {"@type": "UnitPriceSpecification", "price": num(u["rent"]),
                                       "priceCurrency": "USD", "unitCode": "MON",
                                       "description": "Base monthly rent before card or ACH payment fees."},
            } for u in C["units"]]},
    }
    if K.get("email"):
        s["email"] = K["email"]
    if K.get("sameAs"):
        s["sameAs"] = K["sameAs"]
    return s


def service_schema(url, name, t):
    return {"@context": "https://schema.org", "@type": "Service", "@id": SITE + url + "#service",
            "name": name, "serviceType": "Self storage", "url": SITE + url, "provider": {"@id": BIZ_ID},
            "areaServed": city(t["name"], t["st"])}


# ---------------------------------------------------------------- units
def unit_title(u):
    if u.get("kind") == "parking":
        return f'{u["name"]}, {u["w"]} x {u["d"]} ft'
    return f'{u["name"]}, {u["w"]} x {u["d"]} x {u["h"]} ft'


def plan_svg(u, scale=5.4):
    """Top-down floor plan to a shared scale: door on the left, red guide line down the middle."""
    W, H = 300, 96
    dw, dh = u["d"] * scale, u["w"] * scale
    x, y = 12, (H - dh) / 2
    mid = y + dh / 2
    return (f'<svg class="plan" viewBox="0 0 {W} {H}" preserveAspectRatio="xMinYMid meet" role="img" aria-label="Floor plan to scale: '
            f'{u["w"]} feet wide by {u["d"]} feet deep">'
            f'<rect class="slab" x="{x}" y="{y:.1f}" width="{dw:.1f}" height="{dh:.1f}"/>'
            f'<line class="guide" x1="{x + 4}" y1="{mid:.1f}" x2="{x + dw - 4:.1f}" y2="{mid:.1f}"/>'
            f'<line class="doorline" x1="{x}" y1="{y + 3:.1f}" x2="{x}" y2="{y + dh - 3:.1f}"/>'
            f'<text class="lbl" x="{x + dw + 6:.1f}" y="{mid + 4:.1f}">{u["d"]} ft</text></svg>')


def unit_group(u):
    if u.get("kind"):
        return u["kind"]
    if u["h"] >= 14:
        return "tall"
    if u["w"] <= 10 and u["h"] <= 8:
        return "small"
    return "medium"


def unit_card(u, h="h3", plan=True):
    rent = u["status"] == "rent"
    badge = ('<span class="badge badge-rent">Open to rent</span>' if rent
             else '<span class="badge badge-wait">Waitlist</span>')
    if u.get("kind") == "parking":
        dims = f'{u["w"]} &times; {u["d"]} ft<small>Outdoor space</small>'
    else:
        dims = f'{u["w"]} &times; {u["d"]} ft<small>{u["h"]} ft tall inside</small>'
    extra = f'<p class="unit-extra">{html.escape(u["note"])}</p>' if u.get("note") else ""
    btn = "Rent online" if rent else "Join the waitlist"
    pic = plan_svg(u) if plan and not u.get("kind") else ""
    return f'''<article class="unit-card" data-group="{unit_group(u)}" data-status="{u["status"]}">
  <div class="unit-top"><div><{h}>{html.escape(u["name"])}</{h}><p class="unit-dims">{dims}</p></div>{badge}</div>
  {pic}{extra}
  <div class="unit-price"><p class="price-main"><strong>${u["rent"]}</strong><span>/month</span></p><p class="price-ach">Before card or ACH payment fees</p></div>
  <a class="btn btn-dark btn-sm" href="{RENT}">{btn}<span class="visually-hidden">: {html.escape(u["name"])}</span></a>
</article>'''


def units_grid(ids, h="h3"):
    return '<div class="units">' + "".join(unit_card(UNITS[i], h) for i in ids) + "</div>"


# ---------------------------------------------------------------- reviews (verbatim 5-star Google reviews)
REVIEWS = [
    ("Carleen Lynch", "Clean, spacious units. Very easy access at all times &amp; close to town. Excellent customer service. Auto Payments easy to set up and always accurate. Reasonable rates. Enjoyed our experience with Midway."),
    ("Josh Paumer", "Rented from Midway for two year never had a problem, great service and rates, new and well kept facilities, large units held all my toys with extra room. Auto pay worked like a charm all web based. with no hassle and 24 hour access, Best storage place around. Highly recommend giving it a try"),
    ("Sweet Fantasy", "What a blessing Midway Storage was for us. Pricing was fair for the HUGE unit we rented for our two and half households, making payments was easy, and communication through email and texting was awesome! The facility was easy to get to, clean and VERY accessible. Highly recommend using them!"),
    ("Sonya Koltes", "Midway Storage ower was a very friendly person. I had an ex-large shed for 3+ years. Never had any issues. I then moved to a smaller shed.... again, no issues. It is located in a very safe place with easy access. I WILL do business here again if I need a safe place to store my important stuff. Thanks to Midway Storage for such a positive experience...."),
    ("Lori Welch", "Great place to store our large boat plus a few other things. Midway storage is very accommodating. The units are tall and spacious and even have a red line painted on the concrete to help you back in. Genius. Payment is easy which is a huge plus. Highly recommend."),
    ("Lowen", "Very clean and secure storage. Brand new facility and all smooth concrete inside. No rodents or signs of them. Easy to pay and manage the storage rental process all online. It was a great peace of mind having my stuff securely stored here. Highly recommended."),
    ("Lisa Gernant", "Rented an M unit, later upgraded to L. Very clean and good dimensions for large toy and trailer storage. Great location, secure storage. Communication and payment were easy."),
    ("Alena Brendle", "Lovell&rsquo;s Midway Storage facility gets more than 5 &#9733; from me! The secure units are very well-made and have 24 hour access at a great location! The ladies are so helpful and polite! And, as a customer, its refreshing and greatly appreciated to be treated so nicely!"),
]
REV = {n: t for n, t in REVIEWS}


def reviews_carousel(dark=False):
    cards = "".join(f'''<figure class="rv"><div class="rv-stars" aria-label="5 out of 5 stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
<blockquote><p>{t}</p></blockquote><button class="rv-more" type="button" aria-expanded="false" hidden>Read more</button>
<figcaption>{n}<span>Google review</span></figcaption></figure>''' for n, t in REVIEWS)
    return f'''<div class="reviews" data-carousel>
<div class="rv-track" tabindex="0" role="region" aria-label="Customer reviews, scroll sideways for more">{cards}</div>
</div>'''


def quote(name):
    return f'<blockquote class="quote"><p>&ldquo;{REV[name]}&rdquo;</p><footer>{name}, Google review</footer></blockquote>'


# ---------------------------------------------------------------- page shell
def page(path, title, desc, body, *, current=None, schema=(), door=False, noindex=False, preload=None):
    if len(title) > 60:
        print(f"WARN title {len(title)} chars on {path}: {title}")
    if len(desc) > 155:
        print(f"WARN desc {len(desc)} chars on {path}: {desc}")
    url = SITE + path
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False, separators=(",", ":"))}</script>'
                   for s in [business_schema()] + list(schema))
    boot = ("(function(d){d.className+=' js';try{if(!matchMedia('(prefers-reduced-motion: reduce)').matches)"
            "{d.className+=' door-wait';setTimeout(function(){if(!window.MW)d.classList.remove('door-wait')},6000)}}catch(e){}})(document.documentElement)") if door else \
        "document.documentElement.className+=' js'"
    staging = SITE != C["siteUrl"].rstrip("/")
    robots = ('<meta name="robots" content="noindex, nofollow">' if noindex or staging
              else '<meta name="robots" content="index, follow, max-image-preview:large">')
    canonical = "" if noindex else f'<link rel="canonical" href="{url}">'
    pre = f'<link rel="preload" as="image" type="image/webp" href="{preload}" fetchpriority="high">' if preload else ""
    verif = ""
    if K.get("googleSiteVerification"):
        verif += f'<meta name="google-site-verification" content="{html.escape(K["googleSiteVerification"])}">'
    if K.get("bingSiteVerification"):
        verif += f'<meta name="msvalidate.01" content="{html.escape(K["bingSiteVerification"])}">'
    ga = ""
    if K.get("ga4MeasurementId"):
        g = html.escape(K["ga4MeasurementId"])
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={g}"></script>'
              f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}"
              f"gtag('js',new Date());gtag('config','{g}');</script>")
    og = SITE + "/assets/img/share-1200x630.jpg"
    t, d = html.escape(title), html.escape(desc)
    doc = f'''<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
{robots}
{canonical}
<script>{boot}</script>
<link rel="preload" href="/assets/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/source-sans-3-var.woff2" as="font" type="font/woff2" crossorigin>
{pre}
<style>{CSS_MIN}</style>
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta name="theme-color" content="#2b2b2b">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Midway Storage">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Midway Storage logo over the storage buildings in Lovell, Wyoming">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{t}">
<meta name="twitter:description" content="{d}">
<meta name="twitter:image" content="{og}">
<!-- Search Console / Bing: set "googleSiteVerification" / "bingSiteVerification" in site-config.json CONFIRM and rebuild. GA4: set "ga4MeasurementId". -->
{verif}{ga}
{ld}
<script src="/assets/js/site.js?v={JS_V}" defer></script>
</head>
<body>
{header(current)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
'''
    doc = re.sub(r"\n{2,}", "\n", doc)
    out = PUB / ("404.html" if path == "/404.html" else "index.html" if path == "/" else path.strip("/") + "/index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc)
    return path


def pic(name, w_small, w_big, alt, w, h, sizes="(max-width: 820px) 100vw, 50vw", lazy=True, cls=""):
    lz = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return (f'<picture><source type="image/webp" srcset="/assets/img/{name}-{w_small}.webp {w_small}w, '
            f'/assets/img/{name}-{w_big}.webp {w_big}w" sizes="{sizes}">'
            f'<img{cls} src="/assets/img/{name}-{w_small}.jpg" srcset="/assets/img/{name}-{w_small}.jpg {w_small}w, '
            f'/assets/img/{name}-{w_big}.jpg {w_big}w" sizes="{sizes}" width="{w}" height="{h}" alt="{alt}"{lz} decoding="async"></picture>')


# ---------------------------------------------------------------- general FAQ
def office_hours_html():
    return html.escape(K["officeHours"]) if K.get("officeHours") else ph("office hours (when someone answers the phone)")


FAQ = [
    ("How do I rent a storage unit?",
     f'<p>Pick a size on our <a href="{RENT}">online rental page</a> and follow the steps there, any time of day. '
     f'If you would rather talk it through, call <a href="{TEL}">{PHONE}</a>.</p>', "how-to-rent"),
    ("Can I get to my unit any time?",
     "<p>Yes. Access is 24 hours a day, 7 days a week. There is no fence or gate, so there is no code to punch in "
     "when you pull up late at night or early in the morning.</p>", "access"),
    ("Do I have to sign a long-term contract?",
     "<p>No. There is no long-term commitment. Rent for as long as you need the space.</p>", "contract"),
    ("How do I pay my bill?",
     f'<p>Sign in to the <a href="{SIGNIN}">tenant portal</a> to pay online. Tenants tell us automatic payments '
     "are easy to set up there, so you never have to think about the due date.</p>", "pay"),
    ("Why is the total on the rental site a little higher?",
     "<p>Prices on this site are the base monthly rent. The rental site adds a small payment fee, and the fee is "
     f"lower for ACH bank draft than for a credit or debit card. See every size on the <a href=\"/storage-units/\">units and prices page</a> (prices as of {AS_OF}).</p>",
     "two-prices"),
    ("What if the size I want shows Waitlist?",
     f'<p>Join the waitlist for that size on the <a href="{RENT}">rental page</a> and you will be contacted when '
     "one opens up. Sizes that say Open to rent can be rented right away.</p>", "waitlist"),
    ("Will my RV, camper or boat fit?",
     "<p>The M, L and XL units are 14 feet wide and 14 to 15 feet tall inside, and 30, 34 and 45 feet deep. The XL "
     "door is 12 feet wide and 14 feet tall. Measure your rig's height to the top of the AC unit or tower, and its "
     "length from hitch to bumper, then pick a unit with room to spare. Each tall unit has a red guide line painted "
     "on the floor to help you back in straight.</p>", "rv-fit"),
    ("Are any of the units heated?",
     "<p>The 42 x 42 heated shop is the only space we list as heated. The standard drive-up units are not heated.</p>"
     "<!-- TODO: confirm with owner that the heated shop is the only heated space -->", "heated"),
    ("Do you have outdoor parking?",
     "<p>Yes, 8 x 25 foot outdoor spaces for trailers and vehicles. They are open, unsecured spaces, not inside a "
     "building.</p>", "parking"),
    ("Do you rent shop or warehouse space?",
     "<p>Yes. There is a 12 x 40 shop storage unit, a 42 x 42 heated shop and a 36 x 45 shop with 16-foot ceilings. A "
     "36 x 45 warehouse at 1781 US Highway 310 is rented through Midway Ventures. See "
     '<a href="/storage-units/#shops">shops and parking</a>.</p>', "shops"),
    ("When can I reach someone in the office?",
     f'<p>Call <a href="{TEL}">{PHONE}</a>. Office hours: {office_hours_html()}</p>', "office"),
    ("Where are you located?",
     f"<p>{ADDR_LINE}, on US-310 just west of downtown Lovell, between Lovell and Cowley. "
     f'<a href="{DIRECTIONS}">Get directions</a>.</p>', "location"),
]


# ---------------------------------------------------------------- pages
def build_home():
    feats = [UNITS[i] for i in ("A", "G", "S", "M", "L", "XL")]
    body = f'''<section class="hero" aria-labelledby="hero-h">
  <div class="hero-bg" aria-hidden="true"><picture><source type="image/webp" srcset="/assets/img/hero-bg-1045.webp"><img src="/assets/img/hero-bg-1045.jpg" alt="" width="1045" height="700" decoding="async"></picture></div>
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <span class="kicker">Lovell, Wyoming &middot; US-310</span>
      <h1 id="hero-h">Storage units in Lovell, WY <span class="accent">with room for the big stuff</span></h1>
      <p class="hero-sub">Drive-up units from 8 x 15 to 14 x 45, shop space and outdoor parking. Get in any hour of the day, skip the long-term contract, and rent and pay online.</p>
      <div class="btn-row"><a class="btn btn-red" href="{RENT}">{ICON["key"]}Rent a Unit Online</a><a class="btn btn-line" href="/storage-units/">See Sizes &amp; Prices</a></div>
      <ul class="hero-points"><li>24/7 access</li><li>No long-term commitment</li><li>Units up to 15 ft tall</li></ul>
    </div>
    <figure class="bay">
      <div class="bay-head" aria-hidden="true"><span class="bay-no">L12</span><span class="bay-size">14 &times; 34 &times; 14 FT</span></div>
      <div class="bay-opening">
        <picture><source type="image/webp" srcset="/assets/img/unit-l12-400.webp 400w, /assets/img/unit-l12-593.webp 593w" sizes="(max-width: 860px) 92vw, 45vw"><img src="/assets/img/unit-l12-593.jpg" srcset="/assets/img/unit-l12-400.jpg 400w, /assets/img/unit-l12-593.jpg 593w" sizes="(max-width: 860px) 92vw, 45vw" width="593" height="700" alt="Inside an open L unit at Midway Storage: smooth concrete floor with a red guide line for backing in" fetchpriority="high" decoding="async"></picture>
        <figcaption class="bay-cap">L unit: 14 ft wide, 34 ft deep, 14 ft tall</figcaption>
        <div class="door" aria-hidden="true"><div class="door-bar"></div></div>
      </div>
    </figure>
  </div>
</section>
<section class="stats" aria-label="Midway Storage at a glance">
  <ul class="wrap">
    <li><strong>24<em>/</em>7</strong><span>Access, every day</span></li>
    <li><strong>11</strong><span>Drive-up unit sizes</span></li>
    <li><strong>15<em> ft</em></strong><span>Tallest units inside</span></li>
    <li><strong>{C["google"]["rating"]}<em>&#9733;</em></strong><span>{C["google"]["count"]} Google reviews</span></li>
  </ul>
</section>
<section class="section" aria-labelledby="sizes-h">
  <div class="wrap">
    <div class="section-head row">
      <div><span class="kicker">Popular sizes</span><h2 id="sizes-h">From a garage clean-out to a 40-foot fifth wheel</h2>
      <p class="lead">Every floor plan below is drawn to the same scale, so you can see how the sizes compare. The blue edge is the roll-up door and the red line is the guide line painted on the floor.</p></div>
      <a class="btn btn-line" href="/storage-units/">All 15 sizes &amp; prices</a>
    </div>
    {"<div class='units'>" + "".join(unit_card(u) for u in feats) + "</div>"}
    <p class="note mt">Prices and availability as shown on our rental site in {AS_OF}. The rental page always has the current price.</p>
  </div>
</section>
<section class="section section-concrete" aria-labelledby="why-h">
  <div class="wrap split">
    <div class="photo-frame">{pic("exterior-blue", 640, 1045, "Rows of steel storage buildings with blue roll-up doors at Midway Storage in Lovell, Wyoming", 1045, 700)}</div>
    <div>
      <span class="kicker">Why Midway</span>
      <h2 id="why-h">Built for the way people store things out here</h2>
      <div class="guide-wrap" data-draw>
        <ul class="feature-list">
          <li><strong>Pull straight in</strong>Every unit is drive-up. Back the trailer to the door, or drive the side-by-side right inside.</li>
          <li><strong>Tall, wide units</strong>The M, L and XL units are 14 feet wide and 14 to 15 feet tall, with a red line painted on the concrete so you back in straight the first time.</li>
          <li><strong>Come and go on your schedule</strong>Open 24/7 with no gate and no code. Hook up at 5 a.m. for opening day or drop off after a late shift.</li>
          <li><strong>Everything online</strong>Rent, sign in, pay and set up automatic payments from your phone. No trip to an office.</li>
        </ul>
      </div>
    </div>
  </div>
</section>
<section class="section" aria-labelledby="shops-h">
  <div class="wrap split flip">
    <div class="photo-frame">{pic("exterior-red", 640, 917, "Storage building with red roll-up doors and a concrete apron at Midway Storage", 917, 650)}</div>
    <div>
      <span class="kicker">Bigger than a unit</span>
      <h2 id="shops-h">Shop space, a heated shop and outdoor parking</h2>
      <p>Need room to work, not just to store? Midway also rents a 12 x 40 shop, a 42 x 42 heated shop and a 36 x 45 shop with 16-foot ceilings. Outdoor 8 x 25 spaces hold trailers and work rigs.</p>
      <p>Shops fill up and usually run on a waitlist, so get your name on the list early.</p>
      <div class="btn-row"><a class="btn btn-dark" href="/storage-units/#shops">See shop &amp; parking prices</a></div>
    </div>
  </div>
</section>
<section class="section section-dark" id="reviews" aria-labelledby="rev-h">
  <div class="wrap">
    <div class="section-head row">
      <div><span class="kicker">Reviews</span><h2 id="rev-h">{C["google"]["rating"]} stars from {C["google"]["count"]} Google reviews</h2>
      <p>What renters say, word for word.</p></div>
      <div class="rv-nav" hidden><button type="button" data-dir="-1" aria-label="Previous reviews">{ICON["left"]}</button><button type="button" data-dir="1" aria-label="Next reviews">{ICON["right"]}</button></div>
    </div>
    {reviews_carousel(dark=True)}
  </div>
</section>
<section class="section" aria-labelledby="how-h">
  <div class="wrap">
    <div class="section-head"><span class="kicker">How it works</span><h2 id="how-h">Rent a unit in three steps</h2></div>
    <ol class="steps">
      <li><h3>Pick your size</h3><p>Compare sizes and prices on the <a href="/storage-units/">units page</a>, or call us for help choosing.</p></li>
      <li><h3>Rent online</h3><p>Choose your unit on our <a href="{RENT}">rental site</a> and finish the steps there. Full sizes take a waitlist sign-up.</p></li>
      <li><h3>Move in, pay online</h3><p>Load up any time, day or night. Pay through the <a href="{SIGNIN}">tenant portal</a> or set up autopay.</p></li>
    </ol>
  </div>
</section>
<section class="section section-concrete" aria-labelledby="find-h">
  <div class="wrap split">
    <div>
      <span class="kicker">Find us</span>
      <h2 id="find-h">On US-310, just west of Lovell</h2>
      <p><strong>{ADDR_LINE}</strong></p>
      <p>Look for the Midway Storage sign on the highway between Lovell and Cowley.</p>
      <p><a href="{TEL}">{PHONE}</a></p>
      <div class="btn-row"><a class="btn btn-dark" href="{DIRECTIONS}">Get Directions</a><a class="btn btn-line" href="/contact/">Contact Us</a></div>
    </div>
    {map_embed()}
  </div>
</section>
{cta_band("Got stuff that needs a home?", "Units from $" + UNITS["A"]["rent"] + " a month with 24/7 access and no long-term commitment.")}'''
    page("/", "Storage Units in Lovell, WY | Midway Storage",
         "Drive-up storage units in Lovell, WY from 8x15 to 14x45, up to 15 ft tall, plus shops and parking. 24/7 access, no long-term contract, rent online.",
         body, current="/", door=True, preload="/assets/img/unit-l12-593.webp")


def build_units():
    std = [u for u in C["units"] if not u.get("kind")]
    other = [u for u in C["units"] if u.get("kind")]
    v = C["ventures"]
    rows = "".join(
        f'<tr><td>{html.escape(u["name"])}</td><td>{u["w"]} x {u["d"]}' + (f' x {u["h"]}' if u["h"] else "")
        + f' ft</td><td class="num">${u["rent"]}/mo</td>'
        + (f'<td class="st-rent">Open to rent</td></tr>' if u["status"] == "rent" else '<td class="st-wait">Waitlist</td></tr>')
        for u in C["units"])
    trail = [("Home", "/"), ("Units &amp; Prices", "/storage-units/")]
    body = f'''{page_hero("Units &amp; prices", "Storage unit sizes and prices", f"Eleven drive-up unit sizes, three shops and outdoor parking at Midway Storage in Lovell. Prices below are monthly, as shown on our rental site in {AS_OF}.", trail)}
<section class="section" aria-labelledby="std-h">
  <div class="wrap">
    <div class="section-head"><h2 id="std-h">Drive-up storage units</h2>
    <p>Floor plans are drawn to the same scale. The blue edge is the door; the red line is the guide line on the floor.</p></div>
    <ul class="filters" hidden aria-label="Filter units">
      <li><button type="button" data-filter="all" aria-pressed="true">All sizes</button></li>
      <li><button type="button" data-filter="small" aria-pressed="false">Small (8 ft tall)</button></li>
      <li><button type="button" data-filter="medium" aria-pressed="false">Medium (9 to 11 ft)</button></li>
      <li><button type="button" data-filter="tall" aria-pressed="false">RV &amp; boat (14 ft+)</button></li>
      <li><button type="button" data-filter="open" aria-pressed="false">Open to rent now</button></li>
    </ul>
    <p class="filter-count" aria-live="polite"></p>
    <div class="units" data-units>{"".join(unit_card(u) for u in std)}</div>
  </div>
</section>
<section class="section section-concrete" id="shops" aria-labelledby="shops-h">
  <div class="wrap">
    <div class="section-head"><span class="kicker">Shops &amp; parking</span><h2 id="shops-h">Shop space, warehouse and outdoor parking</h2>
    <p>For contractors, ranch and farm equipment, or anyone who needs room to work.</p></div>
    <div class="units">{"".join(unit_card(u, plan=False) for u in other)}
      <article class="unit-card">
        <div class="unit-top"><div><h3>{v["name"]}</h3><p class="unit-dims">{v["w"]} &times; {v["d"]} ft<small>{v["h"]} ft tall inside</small></p></div><span class="badge badge-rent">Open to rent</span></div>
        <p class="unit-extra">At {v["street"]}, rented through Midway Ventures</p>
        <div class="unit-price"><p class="price-main"><strong>${v["rent"]}</strong><span>/month</span></p><p class="price-ach">Before card or ACH payment fees</p></div>
        <a class="btn btn-dark btn-sm" href="{VRENT}">Rent the warehouse</a>
        <!-- TODO: confirm with owner how Midway Ventures LLC relates to Midway Storage, and whether to keep this card -->
      </article>
    </div>
    <p class="note mt">Midway Ventures warehouse questions: <a href="tel:{C["venturesPhoneTel"]}">{C["venturesPhoneDisplay"]}</a>.</p>
  </div>
</section>
<section class="section" aria-labelledby="all-h">
  <div class="wrap">
    <div class="section-head"><h2 id="all-h">Every size at a glance</h2></div>
    <div class="table-scroll"><table class="price-table">
      <caption class="visually-hidden">Monthly prices at Midway Storage, {AS_OF}</caption>
      <thead><tr><th scope="col">Space</th><th scope="col">Size (W x D x H)</th><th scope="col" class="num">Monthly rent</th><th scope="col">Status</th></tr></thead>
      <tbody>{rows}</tbody></table></div>
    <p class="note">Prices and availability as shown on our rental site in {AS_OF}. The <a href="{RENT}">rental page</a> always has the current price.</p>
  </div>
</section>
<section class="section section-concrete" aria-labelledby="how-h">
  <div class="wrap narrow">
    <h2 id="how-h">How renting works</h2>
    <ul class="check-list">
      <li>Choose a size on the <a href="{RENT}">rental site</a>. Sizes marked Open to rent can be rented right away.</li>
      <li>A size marked Waitlist takes a sign-up on the same site, and you will be contacted when one opens.</li>
      <li>Pay by ACH bank draft for the smaller payment fee, or by card. Set up autopay in the <a href="{SIGNIN}">tenant portal</a>.</li>
      <li>No long-term commitment. Access is 24/7 from the day you move in.</li>
    </ul>
  </div>
</section>
{cta_band("Found your size?", "Rent it online now, or call and we will help you pick.")}'''
    page("/storage-units/", "Storage Unit Sizes & Prices in Lovell, WY | Midway",
         f"Monthly prices for 11 drive-up storage unit sizes, shops and outdoor parking at Midway Storage in Lovell, WY. Rent or join a waitlist online.",
         body, current="/storage-units/", schema=[breadcrumb_schema(trail)])


def build_contact():
    trail = [("Home", "/"), ("Contact", "/contact/")]
    email = (f'<a href="mailto:{html.escape(K["email"])}">{html.escape(K["email"])}</a>' if K.get("email")
             else ph("email address"))
    body = f'''{page_hero("Contact &amp; directions", "Contact Midway Storage", "Call, rent online, or stop by the units on US-310 just west of Lovell.", trail)}
<section class="section" aria-labelledby="nap-h">
  <div class="wrap split">
    <div>
      <div class="nap-card">
        <h2 id="nap-h">Midway Storage</h2>
        <dl>
          <dt>Address</dt><dd>{C["street"]}<br>{C["city"]}, {C["region"]} {C["zip"]}<!-- TODO: confirm with owner: Google lists 1780 US-310, the rental site lists 1775 US Highway 310 --></dd>
          <dt>Phone</dt><dd><a href="{TEL}">{PHONE}</a></dd>
          <dt>Email</dt><dd>{email}</dd>
          <dt>Unit access</dt><dd>24 hours a day, 7 days a week</dd>
          <dt>Office</dt><dd>{office_hours_html()}</dd>
        </dl>
        <div class="btn-row mt"><a class="btn btn-red" href="{RENT}">Rent a Unit</a><a class="btn btn-line" href="{SIGNIN}">Pay Bill</a></div>
      </div>
    </div>
    {map_embed()}
  </div>
</section>
<section class="section section-concrete" aria-labelledby="dir-h">
  <div class="wrap">
    <h2 id="dir-h">Getting here</h2>
    <div class="grid g3">
      <div><h3>From Powell or Cody</h3><p>Take US-14A east through Byron and Cowley. Midway Storage is on the highway past Cowley, before you reach Lovell.</p></div>
      <div><h3>From Greybull or Basin</h3><p>Take US-310 north to Lovell, then keep going west through town toward Cowley. The units are just past the west edge of town.</p></div>
      <div><h3>From Billings or Bridger</h3><p>Follow US-310 south into Wyoming through Frannie, Deaver and Cowley. Watch for the Midway Storage sign before Lovell.</p></div>
    </div>
    <p class="note mt"><a href="{DIRECTIONS}">Open turn-by-turn directions in Google Maps</a></p>
  </div>
</section>'''
    page("/contact/", "Contact & Directions | Midway Storage, Lovell WY",
         f"Call Midway Storage at {PHONE} or find us at {ADDR_LINE}. 24/7 unit access, rent and pay online.",
         body, current="/contact/", schema=[breadcrumb_schema(trail)])


def build_faq():
    trail = [("Home", "/"), ("FAQ", "/faq/")]
    towns = "".join(f'<li><a href="{t["url"]}">{t["name"]}, {t["st"]}<span>{t["drive"]}</span></a></li>' for t in TOWNS)
    body = f'''{page_hero("FAQ", "Storage questions, answered", "Renting, access, payments and fitting an RV or boat at Midway Storage in Lovell, WY.", trail)}
<section class="section" aria-labelledby="faq-h">
  <div class="wrap narrow">
    <h2 id="faq-h" class="visually-hidden">Frequently asked questions</h2>
    {faq_html(FAQ)}
  </div>
</section>
<section class="section section-concrete" aria-labelledby="towns-h">
  <div class="wrap">
    <div class="section-head"><h2 id="towns-h">Renters come from all over the Big Horn Basin and southern Montana</h2>
    <p>Drive times from each town to our Lovell units on the fastest route.</p></div>
    <ul class="area-links">{towns}</ul>
  </div>
</section>
{cta_band("Still have a question?", "Call us, or look over every size and price before you rent.")}'''
    page("/faq/", "Storage FAQ | Midway Storage, Lovell WY",
         "Answers about renting, 24/7 access, payments, waitlists, RV and boat fit, shops and parking at Midway Storage in Lovell, WY.",
         body, schema=[faq_schema(FAQ, SITE + "/faq/"), breadcrumb_schema(trail)])


# ---------------------------------------------------------------- town pages
# Each town has its own angle, route, unit picks, questions and review so no two pages share much text.
TOWN_PAGES = {
    "lovell": dict(
        title="Storage Units in Lovell, WY | Midway Storage",
        desc="Storage units a few minutes from downtown Lovell, WY. Small 8x15 units to 14-ft-tall bays, 24/7 access, no long-term contract.",
        kicker="Hometown storage",
        h1="Storage units in Lovell, Wyoming",
        intro="Midway Storage sits on the edge of town, a few minutes from Main Street. Store the overflow from the house without driving to another town.",
        drive_head="A few minutes from downtown",
        route=["Head west out of downtown Lovell on US-310", "Pass the last of the houses at the west edge of town", "Turn in at the Midway Storage sign"],
        story_h="What Lovell renters keep here",
        story=["For a lot of Lovell households, storage just means clearing room at home. Furniture between moves, the holiday boxes, the garage that stopped fitting a car years ago. The A and C units, 9 by 15 and 8 by 15, handle that without paying for space you won't use.",
               "Being this close changes how people use a unit. You can run over on a lunch break for the camp chairs, or drop off a load after work and still be home for supper. With no gate and no code, a quick trip really is quick.",
               "When the stuff gets bigger, the M units give you 14 feet of height for the camper or the ranch truck with a rack."],
        units=["A", "C", "M"],
        faq=[("Is there storage right in Lovell?", "<p>Yes. Midway Storage is on US-310 at the west edge of Lovell, a few minutes from downtown.</p>", "lovell-close"),
             ("What is the smallest unit?", f"<p>The C unit is 8 x 15 feet with 8-foot ceilings, ${UNITS['C']['rent']} a month before payment fees as of {AS_OF}.</p>", "lovell-small"),
             ("Can I move to a bigger or smaller unit later?", "<p>Yes. Renters have moved up and down in size as their needs changed. Call and we will help you switch.</p>", "lovell-switch")],
        review="Carleen Lynch",
        cta=("Close to home, open all night", "Rent a Lovell storage unit online in a few minutes."),
    ),
    "powell": dict(
        title="Storage Units Near Powell, WY | Midway Storage",
        desc="Storage near Powell, WY, 22 minutes away in Lovell. Units for students, apartment moves and household items. 24/7 access, rent online.",
        kicker="Storage near Powell",
        h1="Storage units for Powell, Wyoming renters",
        intro="Can't find the size you need in Powell? Midway Storage is a 22-minute drive east on US-14A.",
        drive_head="22 minutes from Powell",
        route=["Leave Powell on US-14A heading east", "Drive through Byron and on to Cowley", "Continue toward Lovell; Midway Storage is on the highway"],
        story_h="Built for moves, semesters and in-between apartments",
        story=["Powell sees a lot of short moves. Northwest College students heading home for summer, families between rentals, couples combining two households into one. A D or B unit holds a room or two of furniture and boxes until the next lease starts.",
               "There's no long-term commitment, so a summer break or a three-month gap between houses is easy. You sign up online, pay online, and stop paying when you move out.",
               "Since you're driving 20 minutes, load once and load well. Units have smooth concrete floors and drive-up doors, so the truck or trailer backs right to the opening."],
        units=["D", "G", "B"],
        faq=[("How far is Midway Storage from Powell?", "<p>About 22 minutes and 19.6 miles on US-14A, on the fastest Google Maps route.</p>", "powell-far"),
             ("Can I store things just for the summer?", "<p>Yes. There is no long-term commitment, so you can rent for a few months and move out when school starts.</p>", "powell-summer"),
             ("Which size fits a dorm room or small apartment?", "<p>A dorm room usually fits in our smallest units. For a one- or two-bedroom apartment, look at the 10 x 20 B unit or the 11 x 20 F unit.</p>", "powell-size")],
        review="Sweet Fantasy",
        cta=("Moving out of Powell for a while?", "Grab a unit online and keep your things safe until you are settled."),
    ),
    "cody": dict(
        title="RV & Camper Storage Near Cody, WY | Midway Storage",
        desc="Enclosed RV and camper storage for Cody, WY, 47 minutes away. 14-ft-wide units up to 45 ft deep and 15 ft tall. 24/7 access, rent online.",
        kicker="Storage near Cody",
        h1="RV and camper storage for Cody, Wyoming",
        intro="Cody's summers are short and its winters are hard on a camper. Our tallest units keep a travel trailer or fifth wheel under a roof between trips.",
        drive_head="47 minutes from Cody",
        route=["Take US-14A east out of Cody to Powell", "Stay on US-14A through Byron and Cowley", "Pull in at Midway Storage before Lovell"],
        story_h="Room for the camper, inside a building",
        story=["The L and XL units were built for rigs. They're 14 feet wide, 14 and 15 feet tall inside, and 34 and 45 feet deep. The XL door is 12 feet wide and 14 feet tall, tall enough for most fifth wheels with the AC on the roof.",
               "Every tall unit has a red guide line painted down the concrete. Line your mirrors up on it and the trailer goes in straight, even on the first try with a crowd of family watching.",
               "Store it at Midway after the last fall trip, then hook up any morning in spring. Access is 24/7, so leaving at dawn for Yellowstone isn't a problem."],
        units=["L", "XL"],
        faq=[("What is the biggest RV you can store?", "<p>The XL unit is 14 feet wide, 45 feet deep and 15 feet tall inside, with a door 12 feet wide and 14 feet tall. Measure your rig, including the AC unit and the hitch, before you rent.</p>", "cody-biggest"),
             ("Is the RV storage indoors?", "<p>Yes. The L and XL units are enclosed steel buildings with a roll-up door, so your RV sits out of the sun, hail and snow.</p>", "cody-indoor"),
             ("Is it worth the drive from Cody?", "<p>Most RV owners only make the trip a few times a year, at the start and end of camping season. That makes 47 minutes each way an easy trade for a unit tall enough for the camper.</p>", "cody-drive")],
        review="Lisa Gernant",
        cta=("Get the camper out of the weather", "Rent an L or XL unit online, or join the waitlist for the next opening."),
    ),
    "greybull": dict(
        title="Shop & Contractor Storage Near Greybull, WY | Midway",
        desc="Shop space and storage near Greybull, WY, 36 minutes away. 12x40 shop, heated 42x42 shop, tall units for tools and equipment. 24/7 access.",
        kicker="Storage near Greybull",
        h1="Shop space and storage near Greybull, Wyoming",
        intro="For contractors and small outfits around Greybull, Midway is a place for what won't fit in the pickup: tools, materials and equipment between jobs.",
        drive_head="36 minutes from Greybull",
        route=["Take US-310 north out of Greybull", "Follow it into Lovell", "Continue west through town to Midway Storage"],
        story_h="A place to park the gear between jobs",
        story=["The 12 by 40 shop storage unit gives a crew room for a trailer, lumber racks and tool boxes in one spot. For bigger operations, the 42 by 42 heated shop means you can work on equipment in January without losing feeling in your hands.",
               "Need clearance more than floor space? The S unit is 14 feet wide and 11 feet tall inside, a good fit for a skid steer on a trailer or a stack of material.",
               "Open 24 hours, so an early start or a late return from a job site is never a problem. The shops tend to run on a waitlist, so sign up before you need one."],
        units=["SHOP", "HEAT", "S"],
        faq=[("Do you rent heated shop space?", "<p>Yes, a 42 x 42 heated shop with 13-foot ceilings. It usually has a waitlist, so sign up on the rental site.</p>", "greybull-heat"),
             ("Can I store a work trailer?", "<p>Yes. A trailer fits in the 12 x 40 shop storage unit or an S unit, and 8 x 25 outdoor spaces are also available.</p>", "greybull-trailer"),
             ("How do I get on the shop waitlist?", f'<p>Pick the shop on our <a href="{RENT}">rental site</a> and sign up for the waitlist there. You will be contacted when it opens.</p>', "greybull-waitlist")],
        review="Josh Paumer",
        cta=("Get your equipment under a roof", "Join the shop waitlist or rent an S unit online today."),
    ),
    "basin": dict(
        title="Storage Units Near Basin, WY | Midway Storage",
        desc="Household and estate storage near Basin, WY, 44 minutes away. Clean 10x20 and 11x20 units, no long-term contract, 24/7 access.",
        kicker="Storage near Basin",
        h1="Storage units near Basin, Wyoming",
        intro="Sorting out a parent's house, downsizing, or holding furniture for family? A clean, dry unit at Midway buys you time to decide what to keep.",
        drive_head="44 minutes from Basin",
        route=["Take US-16/20 north from Basin to Greybull", "Pick up US-310 north to Lovell", "Drive west through town to Midway Storage"],
        story_h="Room to sort things out",
        story=["Settling an estate rarely happens in a weekend. The B unit at 10 by 20 and the F unit at 11 by 20 hold the furniture, dishes and boxes of a full house while the family works out who gets what.",
               "Renters often mention how clean the units are. Concrete floors, solid steel walls and a building you can drive right up to make loading heirlooms less stressful.",
               "Because there's no long-term commitment, you rent only as long as the sorting takes. Family members in other towns can help with payments online."],
        units=["F", "E"],
        faq=[("What size unit holds a house full of furniture?", "<p>For most two- to three-bedroom homes, start with the 10 x 20 B unit or the 11 x 20 F unit. A larger household may need the 12 x 30 E unit.</p>", "basin-house"),
             ("Can someone else pay for the unit?", f'<p>Payments are made online through the <a href="{SIGNIN}">tenant portal</a>. Call us if a family member will be paying and we will help set it up.</p>', "basin-pay"),
             ("How long can I rent for?", "<p>As long as you need. There is no long-term commitment, so you can move out when the sorting is done.</p>", "basin-long")],
        review="Lowen",
        cta=("Take your time with it", "Rent a clean unit online and sort things out at your own pace."),
    ),
    "bridger": dict(
        title="Equipment & Trailer Storage Near Bridger, MT | Midway",
        desc="Equipment, trailer and side-by-side storage near Bridger, MT, 42 minutes south. 36x45 shop, 14-ft-tall units and outdoor parking.",
        kicker="Storage near Bridger",
        h1="Equipment and trailer storage near Bridger, Montana",
        intro="Ranch gear, side-by-sides and trailers need room. Midway Storage is 42 minutes south of Bridger on US-310, just over the Wyoming line.",
        drive_head="42 minutes from Bridger",
        route=["Head south on US-310 out of Bridger", "Cross into Wyoming at Frannie", "Continue through Deaver and Cowley to Midway Storage"],
        story_h="Space for what doesn't fit in the barn",
        story=["Out here a lot of what needs storing has wheels: the side-by-side, the stock trailer, the snowmobile sled. The M unit's 14-foot ceiling and 30-foot depth hold a side-by-side on its trailer with room for the gear behind it.",
               "For a whole fleet, the 36 by 45 shop has 16-foot ceilings, enough to park a tractor or a hay truck inside. Outdoor 8 by 25 spaces hold trailers that just need a spot to sit.",
               "It's one straight road from Bridger, US-310, the whole way down. Renting and paying happen online, so you only make the drive when you need your equipment."],
        units=["M", "BIG", "PARK"],
        faq=[("Do you take renters from Montana?", "<p>Yes. Renting and paying are done online, so it doesn't matter which side of the state line you live on.</p>", "bridger-mt"),
             ("Can I store a side-by-side or ATV?", "<p>Yes. A side-by-side fits in most of our units. The M unit is 14 feet wide and 14 feet tall, with room for the trailer too.</p>", "bridger-sxs"),
             ("How big is your largest shop?", "<p>The largest shop is 36 x 45 feet with 16-foot ceilings. It usually runs on a waitlist.</p>", "bridger-shop")],
        review="Sonya Koltes",
        cta=("Find a home for the equipment", "Rent online or get on the waitlist for the big shop."),
    ),
    "billings": dict(
        title="Boat & Seasonal Storage for Billings, MT | Midway",
        desc="Boat and seasonal storage for Billings, MT renters, close to Bighorn Lake. 14-ft-wide units, 24/7 access, rent and pay fully online.",
        kicker="Storage for Billings",
        h1="Boat and seasonal storage for Billings, Montana",
        intro="If you boat on Bighorn Lake, storing near the south end saves towing the boat back and forth all summer. Midway Storage is just outside Lovell.",
        drive_head="About an hour and a half from Billings",
        route=["Take I-90 west from Billings to Laurel", "Follow US-310 south through Bridger", "Cross into Wyoming and continue to Midway Storage"],
        story_h="Keep the boat close to the water",
        story=["The south end of Bighorn Lake, with Horseshoe Bend, is a short drive from Lovell. Store here and the boat is already in Wyoming when the weekend comes.",
               "The S unit at 14 by 26 and the E unit at 12 by 30 fit most fishing and ski boats on their trailers, with 11-foot ceilings for a tower or bimini. Tenants have praised the tall units and the red line that helps you back the trailer in.",
               "You never have to visit an office. Rent online, pay online, and come and go 24 hours a day."],
        units=["S", "E"],
        faq=[("Can I rent a unit without coming in first?", f'<p>Yes. Rent online on our <a href="{RENT}">rental site</a> and pay through the tenant portal, so you can set everything up from Billings.</p>', "billings-online"),
             ("Will my boat and trailer fit?", "<p>The S unit is 14 x 26 feet and the E unit is 12 x 30 feet, both 11 feet tall inside. Measure your boat on its trailer, tongue to stern and to the top of any tower.</p>", "billings-boat"),
             ("Can I store a boat over the winter?", "<p>Yes. Store a boat year-round or just for the off-season. There is no long-term commitment either way.</p>", "billings-winter")],
        review="Lori Welch",
        cta=("Store the boat where you use it", "Set it all up online from Billings."),
    ),
}


def town_page(slug):
    t, d = TOWN[slug], TOWN_PAGES[slug]
    trail = [("Home", "/"), (f"Storage near {t['name']}, {t['st']}", t["url"])]
    route = "".join(f"<li>{r}</li>" for r in d["route"])
    story = "".join(f"<p>{p}</p>" for p in d["story"])
    others = "".join(f'<li><a href="{o["url"]}">{o["name"]}, {o["st"]}<span>{o["drive"]}</span></a></li>'
                     for o in TOWNS if o["slug"] != slug)
    drive_line = (f'<p class="big">{t["short"]}</p><p>From downtown {t["name"]}, about 5 minutes</p>' if slug == "lovell"
                  else f'<p class="big">{t["short"]}</p><p>{t["mi"]} on the fastest route</p>')
    body = f'''{page_hero(d["kicker"], d["h1"], d["intro"], trail)}
<section class="section" aria-labelledby="story-h">
  <div class="wrap split">
    <div class="prose"><h2 id="story-h">{d["story_h"]}</h2>{story}</div>
    <aside class="drive-card" aria-labelledby="drive-h">
      <h2 id="drive-h" class="h3">The drive from {t["name"]}</h2>
      {drive_line}
      <ol class="route">{route}</ol>
      <a class="btn btn-line btn-sm" href="{DIRECTIONS}">Directions</a>
    </aside>
  </div>
</section>
<section class="section section-concrete" aria-labelledby="picks-h">
  <div class="wrap">
    <div class="section-head"><h2 id="picks-h">Good fits for {t["name"]} renters</h2></div>
    {units_grid(d["units"])}
    <p class="note mt">As of {AS_OF}. <a href="/storage-units/">Compare every size</a>.</p>
  </div>
</section>
<section class="section" aria-labelledby="q-h">
  <div class="wrap split">
    <div><h2 id="q-h">{t["name"]} questions</h2>{faq_html(d["faq"])}</div>
    <div>{quote(d["review"])}</div>
  </div>
</section>
<section class="section section-concrete" aria-labelledby="other-h">
  <div class="wrap"><h2 id="other-h" class="h3">Other towns we serve</h2><ul class="area-links">{others}</ul></div>
</section>
{cta_band(d["cta"][0], d["cta"][1])}'''
    page(t["url"], d["title"], d["desc"], body,
         schema=[service_schema(t["url"], f"Storage units near {t['name']}, {t['st']}", t),
                 faq_schema(d["faq"], SITE + t["url"]), breadcrumb_schema(trail)])


def build_404():
    body = f'''<section class="page-hero notfound">
  <div class="wrap">
    <span class="kicker">Error 404</span>
    <h1>This unit is empty</h1>
    <p>The page you were looking for isn't here. Try one of these instead.</p>
    <div class="btn-row"><a class="btn btn-red" href="{RENT}">Rent a Unit</a><a class="btn btn-line" href="/storage-units/">Sizes &amp; Prices</a></div>
  </div>
</section>
<section class="section"><div class="wrap narrow"><ul>
  <li><a href="/">Home</a></li><li><a href="/storage-units/">Units &amp; prices</a></li>
  <li><a href="/contact/">Contact &amp; directions</a></li><li><a href="/faq/">FAQ</a></li>
  <li><a href="{SIGNIN}">Pay bill / tenant sign in</a></li></ul></div></section>'''
    page("/404.html", "Page Not Found | Midway Storage",
         f"That page isn't here. See storage unit sizes in Lovell, WY or call {PHONE}.", body, noindex=True)


PAGES = ["/", "/storage-units/", "/contact/", "/faq/"] + [t["url"] for t in TOWNS]


def build_root_files():
    urls = "\n".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>" for p in PAGES)
    (PUB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "\n</urlset>\n")
    if SITE != C["siteUrl"].rstrip("/"):
        (PUB / "robots.txt").write_text("# Preview copy. Not for search engines.\nUser-agent: *\nDisallow:\n")
    else:
        (PUB / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    (PUB / "site.webmanifest").write_text(json.dumps({
        "name": "Midway Storage", "short_name": "Midway Storage",
        "icons": [{"src": "/android-chrome-192x192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/android-chrome-512x512.png", "sizes": "512x512", "type": "image/png"}],
        "theme_color": "#2b2b2b", "background_color": "#ffffff", "display": "browser", "start_url": "/"}, indent=2))
    units = "\n".join(f'- {u["name"]}: {u["w"]} x {u["d"]}' + (f' x {u["h"]}' if u["h"] else "")
                      + f' ft, ${u["rent"]}/mo before payment fees, {"open to rent" if u["status"] == "rent" else "waitlist"}'
                      for u in C["units"])
    drives = "\n".join(f'- {t["name"]}, {t["st"]}: {t["drive"]} ({t["mi"]})' for t in TOWNS)
    pages = "\n".join(f"- {SITE}{p}" for p in PAGES)
    (PUB / "llms.txt").write_text(f"""# Midway Storage

> Drive-up self storage units, shop space and outdoor parking on US-310 in Lovell, Wyoming (Big Horn Basin). Eleven unit sizes from 8x15 to 14x45 ft, up to 15 ft tall. 24/7 access, no long-term commitment, rent and pay online.

## Business facts
- Name: Midway Storage, a division of {C["legalName"]}
- Address: {ADDR_LINE}
- Phone: {PHONE}
- Coordinates: {C["lat"]}, {C["lng"]}
- Access: 24 hours a day, 7 days a week; no fence or gate
- Contract: no long-term commitment
- Payment: credit/debit card or ACH bank draft; prices listed are base rent and the rental site adds a payment fee (smaller for ACH); autopay available in the tenant portal
- Rent a unit or join a waitlist: {C["rentUrl"]}
- Tenant sign in / pay bill: {C["signInUrl"]}
- Heated: only the 42x42 heated shop is listed as heated
- Google rating: {C["google"]["rating"]} from {C["google"]["count"]} reviews

## Units and monthly prices (as of {AS_OF})
{units}
- Midway Ventures warehouse (1781 US Highway 310, rented through Midway Ventures LLC): 36 x 45 x 16 ft, ${C["ventures"]["rent"]}/mo before payment fees: {C["venturesRentUrl"]}

## Drive times to the facility (fastest Google Maps route)
{drives}

## Pages
{pages}
""")


def main():
    build_home()
    build_units()
    build_contact()
    build_faq()
    for t in TOWNS:
        town_page(t["slug"])
    build_404()
    build_root_files()
    print("built", len(PAGES) + 1, "pages into", PUB, "for", SITE)


if __name__ == "__main__":
    main()
