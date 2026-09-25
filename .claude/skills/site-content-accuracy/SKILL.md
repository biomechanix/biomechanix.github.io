---
name: site-content-accuracy
description: "Use whenever writing or changing claims on the biomechanix.github.io website — product features, what an app does, privacy statements, company facts, team bios, numbers, availability — and whenever pulling copy from biomechanix.ai, the mm-business decks/one-pagers, or the app repos (mm-fitness, mm-physio, mm-selfassess). Says where each kind of fact lives, how to verify it in code rather than docs, which sources must never be published (investor financials, placeholder testimonials), and the domain wording rules (Sameeksha is screening not diagnosis; \"live camera video\" never uploaded). Trigger phrases: \"website copy\", \"write content for\", \"add a feature to the site\", \"update the app page\", \"what does the app do\", \"marketing text\", \"about us\", \"is this claim true\"."
---

# site-content-accuracy — say only what the apps actually do

This is a public site for health and fitness apps. An overstated privacy or
clinical claim is worse than a missing feature bullet. Verify, then write.

## Where facts live (siblings under `~/code/projects/`)

| Fact | Source of truth | Check in code |
|---|---|---|
| Fitness features | `mm-fitness/FEATURES.md`, `docs/USE_CASES.md`, Play listing `store/play/mmfitness/listing/en-US/` | `android/app/src/main/java/com/biomechanix/mmmusic/` |
| Fitness data/privacy | `mm-fitness/store/play/mmfitness/data-safety.md` | clip storage = `VideoRecordingManager` |
| Physio features | `mm-physio/docs/app/PHYSIOTHERAPY_APP_PLAN.md` §7 stage table (✅ = shipped) | `git -C mm-physio ls-tree -r --name-only main \| grep <Class>` — handoff docs describe *branches*, not main |
| Physio uploads | `docs/app/CLOUD_VIDEO_STORAGE_DESIGN.md` (clip shares: 30-day link, purged 90 days after archive) | `data/**/**RemoteSource.kt`, `*OnlineSync.kt` |
| Sameeksha | `mm-selfassess/README.md` (+ "Before this ships"), `docs/data/*.md` | strings: `android/app/src/selfassess/res/values/strings_assessment.xml` |
| App names / ids | brand configs `*BrandConfig.kt`, `app_name` strings, `_config.yml` `play:` | — |
| Brand + company copy | biomechanix.ai (React SPA — extract strings from its JS bundle) | — |

Positive-control your greps: an empty grep for an analytics SDK only counts
once the same grep finds something you know is there (e.g. `supabase` in
`gradle/libs.versions.toml`). See the `probe-discipline` skill.

## Never publish

- **Investor material** from `mm-business/` (one-pagers, pitch decks, business
  plan): funding round, MRR/ARR, projections, margins, user targets, patent
  counts, the haptic wearable, pricing bundles, use of funds. Only the public
  positioning ("one engine for sports and therapy", "expert in the loop",
  "camera only") and approved team bios may come from there.
- **biomechanix.ai placeholders**: its testimonials, "40% fewer no-shows",
  ROI calculator figures and pricing are labelled/obviously placeholder
  ("All pricing is placeholder"). Don't quote them without a real source.
- **Invented facts**: bios, credentials, timings ("15–20 minutes"),
  latencies, counts. If there's no source, leave it out or ask.

## Wording rules (domain rules, not style)

- **Sameeksha is screening, not diagnosis.** Findings are *possibilities for a
  qualified professional to confirm*. Keep the "Screening, not diagnosis"
  callout on `/sameeksha` and the "Medical use" row on `/applications`.
  Red flags always override scores and route to medical care.
- **Physio supports a clinician**; dosing and interpretation stay the
  clinician's judgement.
- **Fitness is fitness and wellness**, not medical advice.
- **Camera privacy**: say *live* camera video / camera frames are never
  uploaded. Plain "video never leaves your phone" is false for Physio, where
  a clinician can deliberately create a clip share link (an opt-in upload).
  Fitness rep clips stay on device unless the user shares them.
- **Accounts are optional** in all three (guest / offline / backup-when-signed-in).
- **No third-party analytics or ad SDKs** — verified for all three apps; re-verify
  before repeating it if dependencies change.
- **Positioning claims the platform can't show** (sub-500ms latency, "clinical
  grade", "progressive mastery gates") — don't adopt from biomechanix.ai
  unless the code does it.

## Hygiene

- App names: **MoveMentor Fitness**, **MoveMentor Physio**, **Sameeksha**.
- Keep British/US spelling consistent with nearby text (the site mixes
  "programme"/"practise" — match the page you're editing).
- When unsure whether a claim is true, ask the user rather than hedge-writing
  it. List anything you deliberately excluded in the PR body.
