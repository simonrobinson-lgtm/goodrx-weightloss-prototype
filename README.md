# GoodRx Weight Loss — Prototype

Clickable mobile prototype (MetaLab). Live at https://simonrobinson-lgtm.github.io/goodrx-weightloss-prototype/

Deep links: append `#progress`, `#symptom`, `#journey`, `#care`, `#support` or `#session`.

## Editing
- `src/src.html` — the prototype source (HTML, CSS, JS). Icons live in `src/sprite.min.svg` (injected at `{{SPRITE}}`), images in `src/img/`, fonts in `src/fonts/`.
- Rebuild the published page: `python3 src/bundle.py index.html` — inlines fonts, images and icons into one self-contained `index.html`.
- Commit and push to `main`; GitHub Pages redeploys in about a minute.

Search engines are asked not to index the site (`robots.txt` + `noindex`).
