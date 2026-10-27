# GoodRx Weight Loss — Prototype

Clickable mobile prototype (MetaLab). Live at https://simonrobinson-lgtm.github.io/goodrx-weightloss-prototype/

Desktop homepage prototype: https://simonrobinson-lgtm.github.io/goodrx-weightloss-prototype/homepage/ (same password).

Deep links: append `#progress`, `#symptom`, `#journey`, `#care`, `#support`, `#session` or `#notifs`.

The published page is password protected: the prototype is AES-encrypted into `index.html` and unlocked in the browser. The password is not stored in this repo — builds read it from `src/.proto-pass` (git-ignored) or the `PROTO_PASS` environment variable.

## Editing
- `src/src.html` — the prototype source (HTML, CSS, JS). Icons live in `src/sprite.min.svg` (injected at `{{SPRITE}}`), images in `src/img/`, fonts in `src/fonts/`.
- Rebuild the published page: `python3 src/bundle.py site .` (needs `cryptography`; set `NO_PASS=1` for an unprotected local build).
- Commit and push to `main`; GitHub Pages redeploys in about a minute.

Search engines are asked not to index the site (`robots.txt` + `noindex`).

## Desktop homepage (`homepage/`)
- `homepage/src/src.html` — page source (HTML, CSS, JS). Images in `homepage/img/`, fonts in `homepage/fonts/`, smooth scrolling from `homepage/lenis.min.js`.
- Rebuild: `python3 homepage/src/build.py` (uses the same password as the mobile prototype; `NO_PASS=1` for an unprotected local build).
