---
name: site-privacy-and-deletion
description: "Use when changing the privacy policy (/privacy) or account-deletion page (/delete-account) on biomechanix.github.io — a new app, a new data type, a sync/upload feature, a retention change, a store-review request (Google Play Data safety, Apple App Review 5.1.x), or a legal edit. Covers which URLs and anchors are load-bearing for the apps and store listings, how to derive statements from what the code actually collects, the per-app table format, and the owner-approval gate before a policy goes live. Trigger phrases: \"privacy policy\", \"data safety\", \"delete account page\", \"account deletion\", \"what data do we collect\", \"GDPR\", \"App Store privacy\", \"update the policy\"."
---

# site-privacy-and-deletion

These pages are compliance artefacts, not marketing. The Android apps link to
them from Settings (`*BrandConfig.privacyPolicyUrl`), and the Play/App Store
listings point at them. A wrong sentence here is a store-policy or legal
problem, so every statement must trace to code.

## Load-bearing URLs and anchors — never rename

- `https://biomechanix.github.io/privacy` and `/delete-account`
- `#face-data` and `#on-device-ai` (cited in App Store review responses),
  `#fitness`, `#physio`, `#sameeksha`, `#deletion`, `#summary`, `#all-apps`

Known drift to watch: mm-physio's `PhysioTherapyBrandConfig.kt` has pointed
at the parked domain `movementor.health/privacy` — every app should use
`https://biomechanix.github.io/privacy`.

## Structure of /privacy

1. Short version (4 bullets) · 2. What applies to all apps (account info,
camera/pose/face data, on-device AI, storage with Supabase, what we don't
collect) · 3. One `<h2 id="<app>">` per app with a **Data / Where it lives /
Why** table · 4. Deleting your data · Children · Changes · Contact.

Effective date line: `Effective <date> · Replaces the policy of <previous date>`.

## Deriving statements from code

- **Collected & synced**: `*RemoteSource.kt`, `*Sync.kt`, Supabase tables in
  `mm-model/supabase/migrations/` (RLS tells you who can read it).
- **On-device only**: Room entities with no remote source.
- **Uploads of media**: grep `storage.from`, `ClipShare`, bucket names. Physio
  clip shares are the one video upload (opt-in, link-accessible, 30-day link,
  purged 90 days after archive) — the "live camera video is never uploaded"
  wording exists because of it.
- **Third-party SDKs**: grep `gradle/libs.versions.toml` and
  `app/build.gradle.kts` for analytics/crash/ads (none today). Positive-
  control the grep.
- **Store forms**: keep consistent with `mm-fitness/store/play/*/data-safety.md`.
- Clinician-entered patient data (Physio): the clinician is responsible for
  having a basis to record it — keep that sentence.

## Approval gate

A policy change is published the moment it merges. So:
1. Draft it in a PR, and put an HTML comment at the top of `privacy.html`:
   `<!-- <date>: <what changed>. Pending legal / privacy review — <focus>. -->`
2. In the PR body, list every new commitment you introduced (e.g. an
   under-13 clause, "we'll notify you in the app", retention periods, the
   effective date) so the owner can accept or strike each.
3. Don't merge until the owner says it's approved. Then remove the pending
   comment in a small follow-up commit (it's visible in page source).

The current policy (per-app sections, effective 2026-10-01) was approved by
the owner on 2026-09-23.

## /delete-account

Must keep: in-app path (Settings → Delete account), web request path
(support URL from `_config.yml`, 30-day completion, confirmation), a
"What gets deleted" list per app, and the device-data note (uninstall doesn't
delete the account). Sameeksha also has "Delete all my data" and "Export my
data" — keep those accurate to its strings file.

Note: web requests go through public GitHub issues, so users post their
account email publicly. If a support email address is ever provided, switch
`support_url` in `_config.yml` — it updates every page at once.
