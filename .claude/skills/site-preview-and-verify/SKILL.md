---
name: site-preview-and-verify
description: "Use before opening any PR on the biomechanix.github.io site, and whenever someone reports a layout problem (\"stretched\", \"cut off\", \"overflows on my phone\", \"logo messed up\", \"looks broken on Safari\"). Renders the Jekyll site locally without Jekyll, screenshots it with headless Chrome, checks every page for horizontal overflow at true phone widths, and measures real image aspect ratios in WebKit and Chromium. Encodes the measurement traps that produced false \"looks fine\" results in this repo — headless Chrome's 500px minimum width, lazy images that never load, a silent harness, Chrome-only testing. Trigger phrases: \"preview the site\", \"check on mobile\", \"screenshot the page\", \"does it look right\", \"images stretched\", \"responsive\", \"check Safari\"."
---

# site-preview-and-verify

Jekyll isn't installed locally (system Ruby 2.6), so the site is previewed
with a small renderer and checked with headless browsers. All tools are in
`tools/preview/` and were validated against known-bad inputs.

## 1. Render and serve

```bash
cd ~/code/projects/biomechanix.github.io
P=$TMPDIR/site-preview
python3 tools/preview/render.py . $P            # warns on any unrendered Liquid
python3 -m http.server 8765 --directory $P &     # /fitness and /fitness.html both work
```

`render.py` implements only the Liquid this site uses (front matter, the
default layout, `{{ page.x }}`, `{{ site.x.y }}`, `| default:`, `| date: '%s'`,
`{% if a == "b" %}`, `{% if a %}`). If you introduce other Liquid, extend the
renderer — otherwise the preview shows raw tags while the live site is fine
(or vice versa). A `WARN ... unrendered Liquid` line is a real signal; read it.

## 2. Look at it

```bash
C="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$C" --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=5000 \
  --window-size=1280,2600 --screenshot=$TMPDIR/shot.png http://localhost:8765/company.html
```
Then Read the PNG. Tips:
- The site is **dark-only**; the default screenshot is what users see.
- For tall pages, crop with PIL (`Image.open(p).crop((0,y0,1280,y1))`) rather
  than one unreadable 6000px image.
- `--force-device-scale-factor=3` with a small window to inspect the logo.
- `--blink-settings=preferredColorScheme=1` forces light mode if a light
  theme ever returns.

**Do not judge phone layouts from a `--window-size=390,...` screenshot.**
Headless Chrome clamps the window to ~500px, so that PNG is a crop of a
500px layout: content looks cut off when it isn't, and real overflow hides.

## 3. Overflow at true phone widths

```bash
python3 tools/preview/check_widths.py http://localhost:8765 --dir $P            # all pages, 360 + 768
python3 tools/preview/check_widths.py http://localhost:8765 company --widths 360 --dir $P
```
Loads each page in an iframe of the exact width; `innerWidth` must equal
`scrollWidth`. On failure it names the offending elements. Exit 1 = overflow,
exit 2 = fewer results than expected — the harness didn't run (server down,
page error). **Exit 2 is not a pass**; an empty result once looked like
success in this repo. `.shots` and `.table-wrap` scroll by design and are
excluded.

## 4. Image proportions (when images or their CSS change)

```bash
node tools/preview/image_ratios.cjs http://localhost:8765/fitness.html
node tools/preview/image_ratios.cjs https://biomechanix.github.io/fitness     # live
```
Measures rendered vs natural ratio in **WebKit (Safari) and Chromium**, on
desktop and iPhone 13, after forcing lazy images to load (they otherwise
report nothing and silently drop out). Needs `playwright-core` — resolved
from `$PLAYWRIGHT_CORE`, then `../mm-frontend/node_modules`; install engines
with `npx playwright install webkit` (Chromium falls back to local Chrome).

Why both engines: "images are stretched" reports can be engine-specific
(flex/grid stretch in WebKit) or just a stale cached stylesheet. Two known
causes are already guarded in `site.css` — keep them:
- `img { height: auto }`, because `<img width height>` attributes plus a
  CSS width alone leave the attribute height in force (the original bug).
- `.shots img, .hero-phone { aspect-ratio: 506/900; object-fit: contain }`
  plus `align-self`, so no layout engine can distort phone screenshots.
Give every `<img>` its real `width`/`height` attributes (`sips -g pixelWidth
-g pixelHeight file`) to avoid layout shift.

## 5. Before claiming "verified"

Say what you actually checked (which pages, widths, engines) in the PR body.
If a check could not run, say that instead of implying a pass.
Stop the server afterwards: `pkill -f "http.server 8765"`.
