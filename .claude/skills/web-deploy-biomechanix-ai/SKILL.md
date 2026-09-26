---
name: web-deploy-biomechanix-ai
description: "Use when deploying, previewing, rolling back or troubleshooting the website on biomechanix.ai (Firebase Hosting, project/site biomechanixdev) — including the GitHub Action that deploys on merge, its FIREBASE_SERVICE_ACCOUNT_BIOMECHANIXDEV secret, preview channels, redirects for old URLs, the canonical domain, and 'the change is on github.io but not on biomechanix.ai'. Encodes the preview-before-live rule, the verified rollback path, and the traps hit when this was first set up (missing secret with no error, redirect propagation delay, fragment+query redirects, permission blocks on production deploys). Trigger phrases: \"deploy to biomechanix.ai\", \"push the website live\", \"firebase deploy\", \"preview the site\", \"roll back the website\", \"biomechanix.ai is out of date\", \"set up the deploy action\", \"deploy workflow\", \"firebase secret\"."
---

# web-deploy-biomechanix-ai

The same Jekyll site is served in two places:

| Host | How it updates | Why it exists |
|---|---|---|
| **biomechanix.github.io** | GitHub Pages builds `main` automatically | The apps and store listings link to its `/privacy` and `/delete-account`. **It must stay up.** |
| **biomechanix.ai** + www | Firebase Hosting, project/site `biomechanixdev` | The public company domain, and the **canonical** URL (`site.canonical_url`) |

Firebase config: `deploy/firebase/firebase.json` (+ `.firebaserc`).
- `cleanUrls: true`, so `/company` serves `company.html`.
- 301 redirects:
  - `.html` URLs → the clean URL
  - `/company/about`, `/company/careers` → `/company`
  - `/company/contact`, `/demo` → `/company#contact`
  - `/platform/features`, `/platform/technology` → `/#platform`
  - `/solutions/physical-therapy` → `/physio`
  - `/solutions/sports`, `/pricing` → `/applications`
  - `/logo-preview` → `/`
- No catch-all rewrite. That was the old single-page React app's setup.

## Normal path: merge, and the Action deploys

`.github/workflows/deploy-biomechanix-ai.yml` builds with **GitHub's own Jekyll
builder** (`actions/jekyll-build-pages`, identical to Pages output) into
`deploy/firebase/public`, then checks it:
- content lint passes
- all 9 pages are present
- `tools`, `CLAUDE.md`, `deploy` and `.claude` are **not** published
- the canonical tag is present
- no raw Liquid

Then it deploys:
- **pull_request** → a preview channel (7 days). The action comments the URL on the PR.
- **push to `main`** → live.

Deploy steps run only if the repo secret **`FIREBASE_SERVICE_ACCOUNT_BIOMECHANIXDEV`**
exists. Without it the job still passes, and prints the notice *"not set: built and
checked, not deployed"*. **A green run is not proof of a deploy. Read the log.**

After a merge, verify the live site yourself:
```bash
curl -s "https://biomechanix.ai/company?cb=$RANDOM" | grep -o 'rel="canonical"[^>]*'
tools/publish/wait_deploy.sh /company "<text you changed>"      # github.io side
```

## Manual path (no secret yet, or the Action is broken)

```bash
tools/publish/deploy_firebase.sh preview    # exports LIVE github.io → preview channel, prints URL
tools/publish/deploy_firebase.sh live       # same export → biomechanix.ai (type "live" to confirm)
tools/publish/deploy_firebase.sh rollback   # restores the saved React site channel to live
```
- The export crawls **live** biomechanix.github.io (exact Jekyll output), so
  merge and wait for Pages first.
- Always deploy to a **preview first**. Check every page and old-URL redirect on
  the preview (loop over the URLs with `curl -sL -o /dev/null -w '%{http_code} %{url_effective}'`)
  and compare with `tools/template/side_by_side.py`. Get the owner's go-ahead,
  then go live.
- Going live replaces a public site. Do it only on the owner's explicit
  instruction in the current session. The permission classifier may block
  `firebase deploy` and even `firebase hosting:channel:list`, calling it a
  "Production Deploy". If blocked, give the owner the exact `! cd … && firebase …`
  command. Don't work around it.

## Rollback

- The original React site is saved on channel **`react-site-backup`**
  (https://biomechanixdev--react-site-backup-e79psw24.web.app) **until 2026-10-25**.
  Restore it with `firebase hosting:clone biomechanixdev:react-site-backup biomechanixdev:live`,
  run from `deploy/firebase`.
- For a bad release of *this* site, Firebase console → Hosting → release
  history → roll back. Or re-run the Action or `deploy_firebase.sh live` from a
  good commit.
- Before any risky change, snapshot live first:
  `firebase hosting:channel:create backup-<date> --expires 30d && firebase hosting:clone biomechanixdev:live biomechanixdev:backup-<date>`.

## Setting up (or repairing) the deploy secret

The owner runs this interactively in their own terminal. It opens a browser
for GitHub OAuth, and Claude can't answer its prompts:
```bash
cd deploy/firebase && firebase init hosting:github
```
Answers: repository `biomechanix/biomechanix.github.io`. Build script: **No**.
Auto-deploy on merge: **No** (our workflow already does it). Delete any workflow
files it writes under `deploy/firebase/.github/`. Success prints
`Uploaded service account JSON to GitHub as secret FIREBASE_SERVICE_ACCOUNT_BIOMECHANIXDEV`.

Alternative with no GitHub OAuth: in Google Cloud Console (project
`biomechanixdev`), create a service account with **Firebase Hosting Admin**, add a
JSON key, then run
`gh secret set FIREBASE_SERVICE_ACCOUNT_BIOMECHANIXDEV --repo biomechanix/biomechanix.github.io < key.json`
and delete the key file. Never print, commit or paste the key.

**Verifying the secret:** `gh secret list` can print nothing without making
clear why. Use the API, and positive-control it on a repo known to have secrets:
```bash
gh api repos/biomechanix/biomechanix.github.io/actions/secrets --jq '.total_count, [.secrets[].name]'
gh api repos/biomechanix/mm-fitness/actions/secrets --jq '[.secrets[].name]'      # control: shows MM_CORE_PAT
```
History: on 2026-09-25 `firebase init hosting:github` was run twice and **created
no secret** in any org or personal repo (57 searched), and it showed no obvious
error. The most likely cause is the biomechanix org's **OAuth app policy**
blocking the Firebase CLI. Approve it under org Settings → Third-party access,
or use the Cloud Console key path.

## Traps seen when this was first set up

- **Redirect propagation:** right after a deploy, new redirects returned 404
  for about a minute. Wait and retest with a cache-busting query before
  changing config.
- **Fragment + query:** Firebase appends the incoming query string after the
  destination's `#fragment` (`/demo?x=1` → `/company#contact?x=1`). The page
  loads, but it doesn't scroll to the anchor. That's acceptable, just know about it.
- **CDN staleness:** github.io serves HTML with `max-age=600`, and the export
  script cache-busts every request. Check that exported pages contain the new
  text before deploying.
- `.html` URLs don't exist in a crawled export (it writes `page/index.html`),
  which is why the explicit `/:page.html` redirect exists. Jekyll builds in CI
  produce `page.html`, and `cleanUrls` handles those.
- **Old-site inbound links:** when replacing a site, list its routes first (for
  an SPA, grep the JS bundle for `path:"…"`) and redirect each to its closest
  new page, so bookmarks and search results don't 404.
