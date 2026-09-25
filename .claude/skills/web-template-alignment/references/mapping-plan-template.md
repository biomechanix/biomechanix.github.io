# Template alignment plan: <template name>

- **Template:** <source (path, URL or zip)>, type <theme | design export | XML model | mockup | screenshot>
- **Licence:** <terms>. Credit needed: <yes: where and how / no>
- **Inventory:** <path to inventory.py output>
- **Brand:** <keep biomechanix.ai colours and logo | adopt template colours (owner approved on <date>)>

## 1. Pages

| Template page / type | Site page (URL unchanged) | Notes |
|---|---|---|
| index.html (landing) | `/` | hero + post grid → hero + app cards |
| generic.html (text page) | `/privacy`, `/delete-account`, `/support` | prose layout |
| — | `/applications` | no template equivalent; compose from its card + table styles |

**Gaps** (template pages with no counterpart; proposals only, not built):
- <e.g. blog/posts listing>: <recommendation>

## 2. Regions and components

| Template pattern (class) | Site target | Change |
|---|---|---|
| `#header` + `#nav` | `.site-header`, `.nav` | … |
| `section.post` / `article` | `.card`, `.feature` | … |
| `header.major` | `.hero h1` | … |
| footer | `.site-footer` | … |

## 3. Tokens (`assets/site.css :root`)

| Variable | Old | New | Source in template |
|---|---|---|---|
| `--bg` | `#000000` | … | … |
| `--display` | Space Grotesk | … | `font-family` ×N |
| `--radius` | 16px | … | `border-radius` |
| breakpoints | 640 / 720 / 900px | … | `@media` ×N |

Brand-locked (not changed): <list>

## 4. Assets

| Asset | Decision | Reason |
|---|---|---|
| template fonts | adopt via Google Fonts / self-host / drop | … |
| template images (pic01–09, bg.jpg) | drop | stock/demo imagery |
| icon font | drop or adopt (size cost) | … |
| our screenshots, logo | keep | real product assets |

## 5. Content impact

Target: **none**. Proven by `text_diff.py`. Any exceptions:
- <page>: <change>. Validated separately via web-content-validation.

## 6. Behaviour (JavaScript)

| Template behaviour | Decision |
|---|---|
| mobile menu toggle | … |
| parallax / animations | … |
| trackers found | removed |

## 7. Risks and decisions for the owner

- [ ] Licence/credit: …
- [ ] Brand colours: keep / adopt
- [ ] JS behaviours: …
- [ ] Gaps: …

## 8. Verification plan

text_diff · content_lint · contrast (pairs: …) · check_widths 360/768 ·
side_by_side for: home, /fitness, /applications, /company, /privacy at 1280 and 390 ·
image_ratios on /fitness
