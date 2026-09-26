# CLAUDE.md — biomechanix.github.io

Public website for Biomechanix Inc. and its MoveMentor apps (MoveMentor
Fitness, MoveMentor Physio, Sameeksha). Plain Jekyll on GitHub Pages from
`main`. **Merging to `main` publishes immediately. There is no staging.**

## Content skills (`.claude/skills/`): use them for any content work

| Skill | Use when |
|---|---|
| `web-information-architecture` | Deciding where content goes. Pages vs sections, nav, URLs and anchors, cross-links, page metadata. Holds the site map. |
| `web-content-writing` | Writing or rewriting copy. Voice, page patterns, health and privacy wording rules, the adding-an-app checklist. |
| `web-content-validation` | Before publishing any claim. Claim → source → `claims.yml` → `content_lint.py`, never-publish list, approval gates. |
| `web-content-audit` | Periodic or pre-release accuracy review. Source drift, store links, consistency, report format. |
| `web-template-alignment` | Aligning the site to a given template (HTML/CSS theme, design export, XML sitemap/model, mockup). Inventory → approved plan → implement look, keep content → verify. |

Content tools (`tools/content/`):

```bash
python3 tools/content/content_lint.py      # must pass before any PR (claims ledger, disclaimers, forbidden content, names, links)
python3 tools/content/source_drift.py      # audit: changed sources, external/store links, in-app privacy URLs
python3 tools/content/outline.py [--md]    # site map: pages, headings, anchors, nav
```
Template tools (`tools/template/`): `inventory.py` (template → pages/components/tokens/assets/risks),
`text_diff.py` (content preserved vs origin/main), `contrast.py` (WCAG AA for tokens),
`side_by_side.py` (template vs site screenshots at real viewport widths).
`tools/content/claims.yml` is the claims ledger. Every number on the site is
registered there with its source.

## Structure

- `_layouts/default.html`: head, nav (Platform · Applications · Company · Support), footer
- `assets/site.css`: styles (biomechanix.ai brand, dark only). `assets/img/`: logo, favicon, screenshots
- `_config.yml`: Play ids (`site.play.*`), `contact_email` (all contact, support and deletion requests), Jekyll `exclude` (keeps `tools/` and this file off the site)
- `/privacy` and `/delete-account` and their anchors are linked from the apps and store listings. **Never move them.**

## Publishing reference

1. Branch from fresh `main` (`feat/…`, `fix/…`, `docs/…`), one change per branch.
2. Preview without Jekyll:
   `python3 tools/preview/render.py . $TMPDIR/site-preview && python3 -m http.server 8765 --directory $TMPDIR/site-preview &`
   - Screenshots: headless Chrome. It clamps windows to about 500px, so check phone widths with
     `python3 tools/preview/check_widths.py http://localhost:8765 --dir $TMPDIR/site-preview`
     (exit 2 means the harness didn't run. That is not a pass.)
   - Images: `node tools/preview/image_ratios.cjs <url>` (WebKit + Chromium, desktop + iPhone).
3. Run `content_lint.py`, open a PR (`gh … --repo biomechanix/biomechanix.github.io`). The owner merges.
   Self-merge is blocked in auto mode, so give them the `! gh pr merge <N> … --squash --delete-branch` command.
4. Don't stack PRs. `--delete-branch` closes a PR based on that branch. Test-merge concurrent
   PRs on a scratch branch before saying they're independent.
5. After the merge: `tools/publish/wait_deploy.sh /<path> "<expected text>"`. HTML may be cached for 10 minutes.
   CSS is cache-busted per build.
6. Logo/favicon: `python3 tools/brand/make_logo.py`. The "B" is an outlined path because phones lack Arial Black.
