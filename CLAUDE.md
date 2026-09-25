# CLAUDE.md — biomechanix.github.io

Public website for Biomechanix Inc. and its MoveMentor apps. Plain Jekyll on
GitHub Pages (legacy build) from `main`. **Merging to `main` publishes
immediately. There is no staging.**

## Layout

- `_layouts/default.html`: head, header/nav (Platform · Applications · Company · Support), footer
- `assets/site.css`: all styles (biomechanix.ai brand, dark only); `assets/img/`: logo, favicon, screenshots
- `_config.yml`: Play package ids (`site.play.*`), `support_url`, Jekyll `exclude`
- Pages: `index` (with `#platform`, `#company`), `applications`, `fitness`, `physio`,
  `sameeksha`, `company`, `support`, `privacy`, `delete-account`
- `tools/`: preview, verification, logo and deploy scripts (not published)

`/privacy` and `/delete-account` (and their anchors) are linked from the apps and
store listings. Never rename or move them.

## Skills (`.claude/skills/`): use the matching one before doing the work by hand

| Skill | Use when |
|---|---|
| `site-change-workflow` | Any change: branch → preview → PR → user merges → verify live. Stacked-PR and cache traps. |
| `site-preview-and-verify` | Before every PR, and for any "looks wrong / stretched / overflows" report. |
| `site-content-accuracy` | Writing any claim about the apps, privacy, company or team. What never gets published. |
| `site-add-application` | Adding, removing or renaming an app, or changing a Play id. |
| `site-privacy-and-deletion` | Any change to `/privacy` or `/delete-account`. Owner approval gate. |
| `site-brand-and-design` | Colors, fonts, logo/favicon, CSS components, matching biomechanix.ai. |
| `site-company-and-team` | `/company`, team members/bios, homepage platform and company sections. |

## Quick commands

```bash
python3 tools/preview/render.py . $TMPDIR/site-preview && python3 -m http.server 8765 --directory $TMPDIR/site-preview &
python3 tools/preview/check_widths.py http://localhost:8765 --dir $TMPDIR/site-preview
node tools/preview/image_ratios.cjs http://localhost:8765/fitness.html
tools/publish/wait_deploy.sh /company "expected text"
```
