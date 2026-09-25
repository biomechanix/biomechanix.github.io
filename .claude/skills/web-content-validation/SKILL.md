---
name: web-content-validation
description: "Use before publishing ANY content change on the Biomechanix website, and whenever a claim's truth is in question — product capabilities, numbers, privacy and data statements, clinical/medical wording, availability on Google Play, company facts, team bios. Defines the claim → source → ledger → lint workflow: where each kind of fact is proven (app repos on main, not plans or branches), what may never be published (investor material, biomechanix.ai placeholders, invented bios), the owner-approval gates for privacy/legal and people, and how to use tools/content/claims.yml and content_lint.py. Trigger phrases: \"is this true\", \"fact-check\", \"validate the content\", \"check the claims\", \"can we say\", \"source for this\", \"before we publish\", \"review the copy\", \"content lint\"."
---

# web-content-validation

A claim on this site is published only when it can be traced to a source
that proves it. For health and privacy statements, an unverified claim is a
liability, not just a style problem. The workflow is: **extract claims →
classify → verify against the right source → record in the ledger → lint.**

## 1. Extract the claims

Before editing, list every checkable statement in the draft:
- **Numbers** of any kind (counts, durations, distances, ages, dates, "six languages")
- **Capabilities** ("measures range of motion", "works offline")
- **Data and privacy** (what is collected, uploaded, stored, retained, and who can see it)
- **Clinical positioning** (screening, diagnosis, treatment, "supports a clinician")
- **Availability** (on Google Play, supported languages and platforms)
- **Company and people** (locations, experience, titles, bios)

## 2. Verify against the right source

Sibling repos live under `~/code/projects/`. A source ranks higher when it is
closer to shipped behaviour.

| Claim | Prove it with (best first) |
|---|---|
| App capability | Code on `main`: `git -C <repo> ls-tree -r --name-only main \| grep <Class>`, strings files, then `FEATURES.md` / plan stage tables marked ✅. **Handoff docs and branches don't count.** They describe unmerged work. |
| Data / privacy | `*RemoteSource.kt`, `*Sync.kt`, Supabase migrations + RLS (`mm-model/supabase/migrations/`), `store/play/*/data-safety.md`, dependency files for SDKs |
| Sameeksha specifics | `mm-selfassess/README.md`, `docs/clinical/`, `strings_assessment.xml` |
| Numbers in setup guidance | `mm-fitness/MoveMentorFitness_USER_GUIDE.md` |
| Store availability | The Play URL must return 200 (`tools/content/source_drift.py`). A 404 means it isn't publicly listed. |
| Company positioning | biomechanix.ai (the company's own public copy): its JS bundle holds the text |
| Team bios | The owner's own words, or an approved company document. Otherwise use a role-description line and say so. |
| Policy terms (retention, age, SLAs, effective dates) | The owner's approval, recorded in the ledger as `owner-approved <date>` |

**Positive-control every search.** An empty grep ("no analytics SDK")
counts only after the same grep finds something you know is present. A
failed `git log` (e.g. `mm-business` isn't a git repo) prints nothing, and
that is not the same as "unchanged".

## 3. Never publish

- **Investor material** (`mm-business/` one-pagers, pitch decks, business
  plan): funding, revenue, MRR/ARR, projections, margins, targets, patents,
  pricing bundles, the haptic wearable, use of funds, and anyone named there
  who the owner hasn't approved for the site.
- **biomechanix.ai placeholders:** testimonials, "40% fewer no-shows", ROI
  figures and pricing. The site labels its own pricing as placeholder.
- **Claims the code can't show:** "clinical-grade", "clinically proven",
  "sub-500ms", FDA/HIPAA/CE, "cures", "guaranteed", "diagnoses".
- **Invented specifics:** timings, bios, credentials, counts.

If you can't verify a claim, cut it or ask the owner. List what you cut in
the PR body. Don't soften an unverified claim with "may" or "up to".

## 4. Approval gates (owner sign-off before merge)

- **/privacy and /delete-account:** put a `<!-- … Pending legal / privacy
  review … -->` comment at the top of the page, and list every new commitment
  in the PR (ages, retention periods, notification promises, effective dates).
  Remove the comment once approved.
- **People:** adding a person, changing a title, adding a bio or a photo.
  The approved list lives in `claims.yml` → `people`. Names from internal
  documents go in `not_approved_names`.
- **Availability claims:** a store button for an app whose listing 404s.

## 5. Record and lint

Add or update the entry in `tools/content/claims.yml`: `id`, `claim`,
`numbers` (tokens exactly as written, including words like "six"), `pages`,
`source` (repo path, URL or `owner-approved <date>`), and `verified` (today's
date). Then:

```bash
python3 tools/content/content_lint.py
```

| Lint error | Fix |
|---|---|
| `unsourced number "X"` | Verify it, then add or extend a ledger entry for that page. Or remove the number. |
| `required statement missing` | Restore the disclaimer. It's a domain rule, not optional copy. |
| forbidden-content errors | Rewrite per the error's reason. Don't just add an exception. |
| `write "MoveMentor", not …` | Use the exact product name |
| `not in the approved people list` | Get approval, then add the person to `people` |
| `says "four apps" but _config.yml lists 3` | Fix the count, or the app list |
| broken link / missing anchor | Fix the link. Never rename a load-bearing anchor. |

The lint is proven against planted violations (unsourced number, missing
disclaimer, placeholder, clinical-grade, the over-broad video claim, wrong
app count, unapproved name, misspelled app name, "can diagnose", a bad
anchor, a broken nav link, a missing load-bearing id). If you change a rule,
re-plant a violation to prove it still fires.
