---
name: web-template-alignment
description: "Use when the Biomechanix website must be aligned to a given template or design — an HTML/CSS theme (folder or zip), a Figma/Webflow/Framer HTML export, an SVG design export, a single mockup page or URL, a screenshot, or an XML sitemap/content model defining pages and sections. Inventories the template, writes a mapping plan (template pages, components, tokens and assets onto this site's pages and sections) for owner approval, implements it with the template's LOOK while preserving the site's verified CONTENT, permanent URLs and anchors, then proves it with text-diff, content lint, contrast, overflow and side-by-side screenshots. Trigger phrases: \"apply this template\", \"make the site look like\", \"use this theme\", \"match this design\", \"restyle the website\", \"here is the new design\", \"migrate to this template\", \"align with this sitemap\", \"Figma export\", \"new layout\"."
---

# web-template-alignment

**Rule of precedence (owner decision):** take the **look** from the template
(layout, components, spacing, type scale, styling, imagery style) and keep the
**content** from the site (every claim, disclaimer, name, number, URL and
anchor). Brand colours and the logo come from the template **only if the owner
says so**. Otherwise the biomechanix.ai brand tokens stay (see `CLAUDE.md`).

**Workflow:** inventory → plan (owner approves) → implement → verify → PR.
Don't start implementing before the plan is approved. A template touches every
page, and a wrong mapping is expensive to unwind.

## 1. Intake and inventory

Put the template in the session scratchpad (never in the repo, until the plan
says which assets are adopted). Then run:

```bash
python3 tools/template/inventory.py <dir | .zip | page.html | https://url | sitemap.xml | model.xml | design.svg> --out $TMPDIR/tpl-inventory.md
```

The report lists the template's pages (outline, regions, nav, section
patterns), components (class frequency), design tokens (custom properties,
colours, fonts, sizes, radii, shadows, breakpoints), assets (with dimensions),
XML structure, licence terms and risks. Read all of it. By template type:

| Template | What to take from it |
|---|---|
| HTML/CSS theme | Layout grid, header/footer/nav patterns, section patterns, component styles, type scale, spacing, breakpoints |
| Design-tool export | The same, but exports carry absolute positioning and generated class names (`framer-1x2y3z`). Take the tokens and structure, and rebuild with semantic HTML. Never paste export markup. |
| XML sitemap / content model | Only **IA**: which pages and sections should exist. Map them with `web-information-architecture`. The model's placeholder text is not content. |
| SVG export / mockup page / URL | Tokens (colours, fonts), plus the layout read from a screenshot |
| Screenshot only | Read the image. Estimate tokens and patterns by eye, and say they're estimates in the plan. |

**Stop and ask the owner** when the inventory shows:
- A licence that is non-commercial, or doesn't allow this use. A CC-BY
  template needs visible credit (e.g. "Design based on X by Y", in the
  footer). A marketplace theme needs the purchase licence.
- Trackers or analytics (GTM, Meta pixel, Hotjar…). Remove them. The privacy
  policy promises no third-party analytics.
- Required JavaScript behaviour (mobile menu, carousels, parallax). The site
  is currently JS-free. Each behaviour is a decision, not a default.

## 2. Mapping plan (owner approves)

Write the plan with `references/mapping-plan-template.md`. It must map:
1. **Pages:** template page type → site page (`outline.py` shows ours). Our
   URLs are permanent. Template page names never rename our pages. Template
   pages with no counterpart go under *Gaps* (proposals only).
2. **Regions and components:** template header/nav/footer/section patterns →
   `_layouts/default.html` and our section types (hero, cards, steps, table,
   FAQ, team, callout, privacy card).
3. **Tokens:** template values → `:root` variables in `assets/site.css`. List
   old → new for colour, type, spacing, radius and shadow, and mark which stay
   brand-locked.
4. **Assets:** adopt, replace or drop, for each image, font and icon set.
   Template stock photos and demo images are **dropped**. Real product
   screenshots stay.
5. **Content impact:** "none" is the target. Any text change is listed and goes
   through `web-content-validation` separately.
6. **Risks and decisions for the owner:** licence, JS, brand, gaps.

## 3. Implement (after approval)

Work in this order, and re-render the preview after each step
(`tools/preview/render.py`):
1. **Tokens.** Update `:root` in `assets/site.css`. Keep the variable names,
   so every existing rule picks up the new look.
2. **Shell.** Header/nav/footer in `_layouts/default.html`. The nav *items*
   and order are IA, so leave them unless the plan changes them.
3. **Components.** Restyle the existing classes to match the template's
   patterns. Add new classes only for patterns we don't have. Prefer
   translating the template's CSS into our classes over vendoring its whole
   stylesheet (Massively's is 144 KB, mostly unused). If you vendor, put it in
   `assets/vendor/<template>/`, scope it, and keep its licence file.
4. **Assets.** Self-host fonts or use Google Fonts. Optimise images and give
   them real `width`/`height` attributes. Put the licence and credit where the
   licence requires.
5. **Behaviour.** Only approved JS, small and progressive: the page must work
   without it.

Never carry over template copy (lorem ipsum, demo headlines, fake
testimonials, dates, social links to `#`). Keep the front matter, `section:`
keys, breadcrumbs, `id`s, disclaimers and the privacy/delete-account structure.

## 4. Verify: all must pass before the PR

```bash
python3 tools/template/text_diff.py                  # content preserved: no text, page or anchor changes vs origin/main
python3 tools/content/content_lint.py                # claims, disclaimers, forbidden content, links, anchors
python3 tools/template/contrast.py                   # WCAG AA for the new tokens (pass --pairs for new colour pairs)
python3 tools/preview/check_widths.py http://localhost:8765 --dir $TMPDIR/site-preview
python3 tools/template/side_by_side.py <template page> http://localhost:8765/<page>.html $TMPDIR/cmp-<page> --widths 1280,390
node tools/preview/image_ratios.cjs http://localhost:8765/fitness.html
```

Make a side-by-side for every mapped page type (home, a product page,
/applications, /company, a legal page). Read the images and compare them
region by region against the plan. Note any intentional differences (our
content is longer, the brand colours are kept). `text_diff.py` failing means
content changed. Revert it, or move the change to a separate, validated PR.

## 5. PR

Body: link or name the template and its licence, the approved plan (or a
summary), the token table old → new, what was dropped and why, the
verification results, and the side-by-side images attached or described.
Hand the merge to the owner, per the publishing reference in `CLAUDE.md`.

## Tooling notes

- Every tool was validated against planted failures:
  - `text_diff.py` catches copy edits, removed anchors and removed pages, and passes class-only changes.
  - `contrast.py` fails on low-contrast and alpha pairs, and on undefined tokens (never silently defaults).
  - `inventory.py` detects CC-BY terms, lorem ipsum, trackers, remote imports and missing alt text.
- `side_by_side.py` uses Playwright, so 390px is a real phone viewport.
  Headless Chrome's CLI clamps windows to about 500px.
- Test template used while building this skill: HTML5 UP "Massively"
  (CC BY 3.0). The inventory flagged its attribution requirement, the lorem
  ipsum on all three pages, and its remote Google Fonts `@import`.
