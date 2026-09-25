---
name: site-add-application
description: "Use when adding a new app to the biomechanix.github.io website (e.g. a table-tennis, cricket, yoga or dance app built on MoveMentor), renaming an app, removing one, or changing an app's Play package id. Lists every place an app appears — its own page, the Applications page row and comparison column, homepage cards, \"Built on MoveMentor\" row, footer, _config.yml, privacy policy section, delete-account list, support FAQ — so nothing is left half-updated. Trigger phrases: \"add an app to the website\", \"new app page\", \"launch page for\", \"list the app under applications\", \"remove the app from the site\", \"rename the app\"."
---

# site-add-application — every place an app lives on the site

Apps sit under **Applications** in the nav (`Platform · Applications · Company · Support`).
Individual apps are deliberately *not* in the top nav. Existing app pages:
`fitness.html`, `physio.html`, `sameeksha.html` — copy the closest one.

## Checklist (new app `<slug>`)

1. **Facts first.** Read the app repo (`../mm-<slug>/`) per
   `site-content-accuracy`: what ships on `main`, data collected, whether it
   uploads anything, account model, medical positioning. Confirm the public
   name and whether it's actually on Google Play.
2. **`_config.yml`** → add `play: <slug>: <applicationId>` (from the app's
   `build.gradle.kts` flavor / brand config). Buttons read
   `https://play.google.com/store/apps/details?id={{ site.play.<slug> }}`.
3. **`<slug>.html`** — front matter:
   ```yaml
   layout: default
   title: <Public App Name>
   nav: <slug>
   section: applications      # keeps "Applications" highlighted in the nav
   description: <one sentence for search/social>
   ```
   First line inside the hero wrap:
   `<a class="crumb" href="/applications">Applications</a><br>` then the
   eyebrow. Sections: hero (+ Play button), features (`grid grid-3` of
   `card feature`), how-to/steps (`ol.steps`), privacy card (`card card-dark`)
   linking `/privacy#<slug>`, a scope/limits card. Screenshots: see
   `site-preview-and-verify` §4 (real width/height attributes, `.shots` /
   `.hero-phone` classes).
4. **`applications.html`** — add an `article.app-row` (tag, h2, lede,
   Explore + Google Play buttons, four `app-points`: For / The camera /
   Highlights / You get) and a column in `table.compare` for every row
   (Best for, Who uses it, Account, Camera analysis, Medical use). Update the
   hero if it says "Three apps".
5. **`index.html`** — product card in `#apps` (tag class: `tag-blue` lime,
   `tag-teal` cyan, `tag-amber` neutral), and an `<li>` in the
   `.built-on` list. Adjust `.built-on ul` column count in `site.css`
   (`repeat(N, 1fr)`) so the row doesn't leave a hole. Fix counts in copy
   ("Three apps · one movement platform", meta description).
6. **`_layouts/default.html`** footer "Company & apps" list.
7. **`privacy.html`** — a `<h2 id="<slug>">` section with the Data / Where it
   lives / Why table, and the app name in the intro list. This is a policy
   change → follow `site-privacy-and-deletion` (owner approval before merge).
8. **`delete-account.html`** — the app in the intro and in "What gets deleted".
9. **`support.html`** — an `<h2>` with the app's real FAQs.
10. **Verify** (`site-preview-and-verify`): render, check_widths on all
    pages, screenshot `/applications` and the new page. Ship via
    `site-change-workflow`.

## Removing or renaming

Grep first — `grep -rn -i "<name>" --include=*.html --include=*.yml --include=*.css .`
(run it from the repo root; in zsh a bare `--include=*.html` glob errors with
"no matches found" — quote it or use `grep -rn ... .` with `--exclude-dir=.git`).
Keep the old page URL working if anything external links to it (store
listings, the app's brand config); otherwise remove it from every place in the
checklist, including the privacy section (policy change).
