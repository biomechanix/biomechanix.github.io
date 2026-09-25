---
name: web-information-architecture
description: "Use when deciding WHERE content goes or HOW the Biomechanix website is organized — adding a page vs a section, restructuring navigation, adding/removing/renaming an app, company or platform content, footer links, page hierarchy, URLs, anchors, breadcrumbs, cross-links, page titles/descriptions, or when the site feels duplicated, hard to navigate or inconsistent. Holds the current site map and the rules behind it (one canonical home per fact, apps live under Applications, legal pages never move) plus a decision procedure for placing new content. Trigger phrases: \"where should this go\", \"add a page\", \"new section\", \"restructure the site\", \"navigation\", \"menu\", \"sitemap\", \"information architecture\", \"move X under Y\", \"remove from the nav\", \"company page\", \"applications page\"."
---

# web-information-architecture

Good IA here means a visitor finds the answer in one hop, and every fact has
**one canonical home** that other pages summarise and link to. Most IA bugs
on this site were the same fact written two ways on two pages, or an item
living in two nav places.

## Current site map (verify with `python3 tools/content/outline.py`)

```
/                     Home: hero · #apps (3 cards) · how it works · #platform · privacy + hardware · #company (teaser)
├── /applications     Overview of all apps: one row per app + comparison table
│   ├── /fitness        MoveMentor Fitness (training)
│   ├── /physio         MoveMentor Physio (rehabilitation, clinician + patient)
│   └── /sameeksha      Sameeksha (musculoskeletal self-screening)
├── /company          #about · #team · #values · #contact
├── /support          FAQ by topic and app, plus contact
└── legal (footer only)
    ├── /privacy          per-app sections #fitness #physio #sameeksha; #face-data #on-device-ai
    └── /delete-account
```

**Primary nav** (4 items, in this order): Platform (`/#platform`) · Applications · Company · Support.
**Footer**: Company & apps (all applications, each app, platform, about, team, biomechanix.ai) · Help & legal.

Owner decisions that shaped this (don't undo without asking):
- Individual apps are **not** in the top nav. They sit under Applications.
- The Company page holds About and Team. The homepage keeps only a teaser.
- The "Built on MoveMentor" row lists **shipped apps only**. Sports coaching
  was removed.

## Placement rules

1. **One canonical home per fact.** Full detail lives in one place. Elsewhere,
   write a one-line summary plus a link.
   | Fact type | Canonical home | May be summarised on |
   |---|---|---|
   | What an app does | its product page | /applications row, home card |
   | Comparing apps | /applications table | — |
   | How the engine/platform works | home `#platform` | /applications hero |
   | Company, mission, team | /company | home `#company` teaser |
   | What data an app collects | /privacy `#<app>` | product page privacy card (link to the anchor) |
   | How to do X / troubleshooting | /support | product page "good to know" card |
2. **Make a new page only if** it serves a distinct audience or task, has at
   least three sections of its own, and people will share or link to it
   directly. Otherwise add a section with an `id` to an existing page.
3. **Hierarchy is shown, not just implied.** A child page sets `section:` in
   its front matter (nav highlight) and shows a breadcrumb
   (`<a class="crumb" href="/applications">Applications</a>`).
4. **Nav stays at 5 items or fewer**, labelled with nouns the visitor uses
   ("Applications", not "Solutions"). Legal pages go in the footer only.
5. **Every page links onward.** A product page links to its privacy anchor,
   /support and back to /applications. An overview links down to each child.
   No page should be a dead end.

## URLs and anchors: permanent once published

- `/privacy`, `/delete-account` and the anchors `#face-data`, `#on-device-ai`,
  `#fitness`, `#physio`, `#sameeksha` are linked from the Android apps and Play
  listings. **Never rename or move them.** The content lint enforces this.
- URLs are flat, lowercase and hyphenated (`/delete-account`), with no `.html`
  in links. App URLs keep their short names even though the apps sit under
  Applications. Hierarchy comes from nav and breadcrumbs, not from path depth.
- Anchor ids are lowercase and hyphenated, and describe the topic
  (`#team`, not `#section3`). Add an `id` to any section you link to or expect
  others to link to.
- GitHub Pages can't do server redirects. If a page must move, leave a stub at
  the old URL that links to the new one, or ask before deleting.

## Page metadata

Front matter per page: `title` (2–4 words, the page's name; the layout
appends "— Biomechanix"), `nav` (the page's own key), `section` (the parent
nav item), `description` (one sentence, ideally ≤160 characters; `outline.py
--md` shows the lengths). Several descriptions currently run 185–227
characters. Shorten them when those pages are next edited.

## Procedure for a content request

1. Run `outline.py` and find where the topic already appears. If it appears
   in two places, fix that first.
2. Classify the content using the table above, and decide between a page and
   a section (rule 2).
3. List every place that must change: canonical home, summaries, nav/footer,
   cross-links, privacy/support. For a new app, see `web-content-writing`
   § *Adding an app*.
4. Draft (`web-content-writing`), validate (`web-content-validation`), then
   run `python3 tools/content/content_lint.py`. It checks internal links and
   anchors too.
5. In the PR, state the IA change in one line, e.g. "Company moved from a home
   section to /company. Home keeps a teaser."
