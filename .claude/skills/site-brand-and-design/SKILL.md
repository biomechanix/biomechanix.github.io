---
name: site-brand-and-design
description: "Use for any visual change to biomechanix.github.io — colors, fonts, logo, favicon, buttons, cards, spacing, new CSS, a new section layout — or when someone says the logo looks wrong, the site doesn't match biomechanix.ai, or asks to rebrand. Holds the biomechanix.ai brand tokens this site uses (lime #CCFF00 on black, cyan #00D4FF, Space Grotesk / Inter / JetBrains Mono, dark-only), the component classes in site.css, and the script that regenerates the font-independent logo SVG. Trigger phrases: \"logo\", \"favicon\", \"brand colors\", \"match biomechanix.ai\", \"styling\", \"CSS\", \"design\", \"theme\", \"dark mode\", \"font\"."
---

# site-brand-and-design

The site follows the **biomechanix.ai** brand (not the cream MoveMentor app
theme it launched with). biomechanix.ai is dark-only, so this site is too —
`color-scheme: dark`, no light variant.

## Tokens (`:root` in `assets/site.css`)

| Token | Value | Use |
|---|---|---|
| `--bg` / `--bg2` | `#000` / `#0A0A0A` | page / alternate section (`.section-alt`) |
| `--card` | `#0F0F0F` | cards, details, table rows |
| `--line` / `--line-strong` | `rgba(255,255,255,.10)` / `#2E2E2E` | hairlines / borders |
| `--ink` `--ink2` `--ink3` `--muted` | `#FFF` → `#A6A6A6` | text hierarchy |
| `--lime` (+ `--lime-hover` `#D9FF52`) | `#CCFF00` | primary buttons, links, eyebrow numbers, active nav |
| `--cyan` | `#00D4FF` | secondary accent (tags, roles, callout variant) |
| `--glow` | `0 0 15px rgba(163,230,53,.5)` | lime glow on logo + primary button |
| fonts | Space Grotesk (display), Inter (body), JetBrains Mono (eyebrows/labels) | loaded from Google Fonts in the layout |

Rules of thumb: one atmospheric lime/cyan glow per hero (`.hero::before`);
lime is for action and emphasis, not large fills; body copy in `--ink3`.

## Components already in site.css — reuse before adding

`.hero` (+ `.hero-grid`, `.hero-phone`) · `.section-alt` · `.section-head` ·
`.eyebrow` · `.lede` · `.btn` / `.btn-primary` · `.grid .grid-2/.grid-3` ·
`.card` / `.card-dark` (lime-tinted gradient) / `.feature` (`.n` label) /
`.product-card` (`.tag`) · `ol.steps` · `.callout` / `.callout-amber` (cyan) ·
`.shots` · `.built-on` · `.facts` · `.app-row` / `.app-points` · `table.compare`
· `.person` / `.avatar` / `.role` · `.crumb` · `.prose` (legal/support pages)
· `details/summary` FAQ.

Layout constraints: 16px side gutter under 720px (`.wrap`), no horizontal
page scroll (`check_widths.py`), wide tables inside `.table-wrap`.

## Logo and favicon

The mark is a lime rounded square with a black **"B" in Arial Black** plus the
**BIOMECHANIX** wordmark in Space Grotesk bold. The "B" must be an outlined
SVG path, never live text: Android and iOS don't ship Arial Black, and a text
"B" rendered in a fallback font on phones ("logo messed up").

```bash
python3 tools/brand/make_logo.py            # rewrites assets/img/logo.svg + favicon.svg
```
- `favicon.svg`: exact biomechanix.ai favicon geometry (rx 20, size 60, baseline 68).
- `logo.svg`: header proportions of biomechanix.ai (40px square, 6px radius,
  32px B, centred). The layout uses `<img class="brand-mark" src="/assets/img/logo.svg" width="40" height="40">`.
Re-running on unchanged inputs is byte-identical — a quick sanity check.

## Re-syncing with biomechanix.ai

It's a Vite/React SPA; the HTML is empty. Pull the bundle and read it:
```bash
curl -sL https://biomechanix.ai/ | grep -o '/assets/[^"]*\.\(css\|js\)'
# CSS: HSL custom properties (--primary: 72 100% 50% = #CCFF00) and rgb() uses;
# JS: header component (search "BIOMECHANIX", "bg-lime-400") for the live logo.
```
biomechanix.ai also has a "Logo & Tagline Options" page with candidate marks
(one labelled Recommended). Use what its header actually renders, not a
candidate, unless the owner picks one.

## After any visual change

Run `site-preview-and-verify` (screenshots of affected pages, `check_widths`,
`image_ratios` if images/their CSS changed). The stylesheet URL is
cache-busted per build, so CSS changes reach users on the next load.
