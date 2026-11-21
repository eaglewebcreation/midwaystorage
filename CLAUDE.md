# Midway Storage website

Static site for Midway Storage (Lovell, WY), built by Eagle Web Creation.

- Edit owner facts, units and prices in `site-config.json`; edit layout and copy in `tools/build_site.py`; styles in `src/site.css` (inlined into every page); behavior in `public/assets/js/site.js`.
- Build: `python3 tools/build_site.py` (production URLs). Preview build: `SITE_URL=https://midwaystorage.eaglewebcreation.com python3 tools/build_site.py`.
- Check: `python3 tools/verify.py` (town pages must stay under 25% shared text, titles <=60, descriptions <=155, no broken links).
- `public/` is the deploy root (Hostinger static auto-deploy). `.htaccess` noindexes every host except midwaystoragewy.com.
- Rules: never claim climate-controlled, gated, cameras or lighting. No aggregateRating/Review schema. Unconfirmed facts stay as `[waiting on owner confirmation]` with an HTML TODO comment. Nothing goes on midwaystoragewy.com until Talon approves.
- Images: `python3 tools/build_images.py` regenerates sizes from `assets/source/`.
