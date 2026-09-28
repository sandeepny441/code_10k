# Markdown → HTML experiment (file:// friendly)

Edit topics under `content/` (and `content/manifest.json` if you change the order).

Then bake Markdown into the JS bundle **and** a shareable standalone HTML:

```bash
python3 build.py
```

(or `./build.sh`)

## Local workflow

Open `index.html` by double-clicking it — no localhost / static server required. The page loads `content-bundle.js` (`window.CONTENT_BUNDLE`) so browsers never need to `fetch` Markdown over `file://`.

## To share

**Send only `report-standalone.html`.** Recipient needs that one file — no `content/`, no `content-bundle.js`, no localhost. CSS, JS, and `CONTENT_BUNDLE` are all inlined. Fonts use a `system-ui` stack (Inter Tight if installed) so the file works fully offline.

## To rebuild after MD edits

```bash
python3 build.py
```

## Scale

Designed for **10+ chapters × 10 topics (100+ rows)**. All topics are embedded as one compact JSON object (no per-file fetch). **100 topics is fine** — bundle size is typically tens of KB to low hundreds of KB for normal topic data.
