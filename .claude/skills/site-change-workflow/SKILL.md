---
name: site-change-workflow
description: "Use for ANY change to the biomechanix.github.io website — copy edits, new pages, styling, nav, images, privacy text — from branching through preview, PR, merge and confirming it is live. Encodes how this Jekyll/GitHub Pages repo actually ships (merging to main IS publishing), the PR-per-change habit, the stacked-PR trap that silently closed a PR, test-merging concurrent PRs, and the deploy check that proves a change is live rather than cached. Trigger phrases: \"update the website\", \"change the site\", \"add a page\", \"publish\", \"deploy\", \"stage on biomechanix.github.io\", \"is it live\", \"merge the PR\", \"fix the site\"."
---

# site-change-workflow — how a change gets onto biomechanix.github.io

The site is plain Jekyll served by GitHub Pages (legacy build) from `main`
of `biomechanix/biomechanix.github.io`. There is no staging: **merging to
`main` publishes to the world within ~1 minute.** Everything below exists
because of that.

Local clone: `~/code/projects/biomechanix.github.io`. Working dir for the
Claude session is usually `~/code/projects/biomechanix-github` (the org
`.github` repo) — a different repo. Pass `--repo biomechanix/biomechanix.github.io`
to every `gh` command, or `gh` will look in the wrong repo ("Could not
resolve to a PullRequest").

## The loop

1. **Branch from fresh main**, one branch per change:
   ```bash
   cd ~/code/projects/biomechanix.github.io
   git checkout main && git pull && git checkout -b <type>/<slug>   # feat/ fix/ chore/ style/ docs/
   ```
2. **Edit.** Shared chrome lives in `_layouts/default.html` (header, nav,
   footer); styles in `assets/site.css`; per-app Play ids and the support URL
   in `_config.yml`. Every page is `*.html` with front matter
   (`layout: default`, `title`, `nav`, `section`, `description`).
3. **Check facts** before writing product claims → `site-content-accuracy`.
4. **Preview and verify** → `site-preview-and-verify` (render, eyeball
   screenshots, `check_widths.py`, `image_ratios.cjs` if images changed).
5. **Commit** with a Conventional-Commit subject and a body that says *why*,
   ending with the session's Co-Authored-By line. **Push, open a PR** against
   `main` with a body covering what changed, what was verified, and anything
   deliberately left out.
6. **Hand the merge to the user.** In auto mode the permission classifier
   blocks self-merging a PR without review, so don't loop on it. Give them
   the exact command:
   ```
   ! gh pr merge <N> --repo biomechanix/biomechanix.github.io --squash --delete-branch
   ```
   If the user explicitly tells you to run the merge, do it.
7. **Confirm it's live** after the merge:
   ```bash
   tools/publish/wait_deploy.sh /company "Raghunandan S K" /applications "Which app"
   ```
   It waits until the Pages build for *main's current HEAD* is `built` (an
   older `built` is the previous deploy), then fetches each path cache-busted
   and checks for the text. Then sync and prune locally:
   `git checkout main && git pull && git branch -D <merged branches>`.

## Several PRs open at once

- **Test-merge before telling the user "either order works":**
  ```bash
  git fetch origin && git checkout -b tmp-mt origin/main
  git merge --no-edit origin/<branch-A> && git merge --no-edit origin/<branch-B> \
    && echo clean || { echo CONFLICT; git merge --abort; }
  git checkout - && git branch -D tmp-mt
  ```
  `_layouts/default.html` and `index.html` are hot spots; adjacent-line edits
  conflict even when they look unrelated.
- **Don't stack PRs on each other's branches.** `gh pr merge --delete-branch`
  on the base PR *closes* the stacked PR instead of retargeting it to `main`
  (that happened to PR #6). If two changes conflict, rebase the second onto
  `origin/main` **after** the first merges, force-push with
  `--force-with-lease`, and keep the PR's base as `main`. If a PR does get
  closed this way, rebase onto main and open a replacement PR — and say so.

## "It's still wrong on the live site"

Check before assuming the fix failed:
- Pages sends `cache-control: max-age=600` for HTML. A user can see the old
  page for ~10 minutes; ask them to hard-refresh. The stylesheet link carries
  `?v={{ site.time | date: '%s' }}`, so CSS is fresh per build.
- Fetch the live HTML/CSS with a `?x=$RANDOM` query and grep for the change.
- Reproduce in the engine they use (`image_ratios.cjs` runs WebKit = Safari).
  If you can't reproduce, say so, harden the fix anyway, and ask for device +
  browser. Don't claim "fixed" on the strength of Chrome alone.

## URLs that must never move

`/privacy` (anchors `#face-data`, `#on-device-ai`, `#fitness`, `#physio`,
`#sameeksha`) and `/delete-account` are linked from the Android apps' brand
configs and Play Store listings. Renaming or moving them breaks store
compliance links. Keep `/fitness`, `/physio`, `/sameeksha` stable too.
