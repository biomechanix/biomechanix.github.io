---
name: web-content-writing
description: "Use when writing or rewriting copy for the Biomechanix website — product/app pages, the applications overview, homepage sections, company and team text, FAQs, privacy or deletion wording, headlines, button labels, image alt text, page descriptions — or when adding a new app's content. Gives the voice, the section patterns each page type uses, health-and-privacy wording rules that are about accuracy not style, and before/after examples of copy that had to be corrected. Trigger phrases: \"write copy\", \"website content\", \"rewrite this section\", \"headline\", \"make this clearer\", \"FAQ\", \"about us text\", \"product page\", \"marketing copy\", \"content for the new app\"."
---

# web-content-writing

Audience, in order: people who might use an app (individuals, patients,
caregivers), clinicians and coaches evaluating it, and app-store/legal
reviewers who read /privacy and /delete-account. Write for someone deciding
whether to trust a camera-based health app.

## Voice

- **Plain and concrete.** Say what happens: "The camera measures peak range
  of motion, left–right symmetry and hold time", not "AI-powered insights".
- **Second person, active.** "You get a clear report", "Your clinician sees…".
- **Benefit first, then the mechanism, then the limit.** For example: "Reps are
  counted from your movement, with no tapping. A rep only counts when you reach
  the target range."
- **Short sentences, no hype.** Avoid "revolutionary", "seamless", "cutting-edge"
  and "clinical-grade". Avoid numbers that aren't in the claims ledger.
- **Spelling:** match the page you're editing. The site uses British forms in
  places ("programme", "practise"). Don't mix forms within a page.

## Page patterns (reuse the existing CSS components)

| Page type | Sections, in order |
|---|---|
| Product (`/fitness`…) | breadcrumb → eyebrow `<App> · <Category>` → h1 promise → lede (what, who, how) → Play CTA → 3–6 feature cards (title = benefit, body = mechanism + limit) → how-to steps → privacy card (links to `/privacy#<app>`) → scope/limits card |
| Overview (`/applications`) | h1 → lede tying the apps to the platform → one row per app (For / The camera / Highlights / You get) → comparison table → "not sure where to start" guidance |
| Home | hero → apps → how it works → platform → privacy + hardware → company teaser |
| Company | mission hero → why we exist + roots → team cards → values → contact routes |
| Support | FAQs grouped by topic, then by app, as `<details>` → contact |
| Legal | plain-language summary first, then detail tables (Data / Where it lives / Why) |

Headlines are sentences, not taglines: "Examine, prescribe and follow up,
all with one camera." Eyebrows are short labels in the mono style. Buttons
start with a verb ("Explore Physio", "Get support").

## Accuracy wording rules (apply everywhere)

- **Sameeksha screens; it doesn't diagnose.** Findings are "possibilities for
  a qualified professional to confirm". Warning signs route to medical care
  and override all scores.
- **Physio supports a clinician.** Dosing and interpretation stay with the clinician.
- **Fitness is fitness and wellness**, not medical advice.
- **Camera privacy:** "Live camera video is never uploaded." Don't write "the
  video never leaves your phone". Physio clinicians can deliberately create a
  clip share link, which does upload a clip.
- **Accounts are optional** in all three apps.
- **People:** name only approved team members. Use their exact titles. Never
  invent credentials.
- **Availability:** a store button implies the app is publicly listed. Check
  the listing actually resolves (`tools/content/source_drift.py`).

## Corrections made on this site (learn from them)

| Draft | Problem | Shipped |
|---|---|---|
| "The video never leaves your phone." | False for Physio clip shares | "Live camera video is never uploaded." |
| "Five short steps, about as long as a cup of tea." / "About 15–20 minutes" | Unsourced timing | "Five guided steps, one joint at a time." |
| "From camera frame to coaching cue in under a twentieth of a second." | A latency *budget* is not a measurement | "…in time for your next rep." |
| "The apps tell you if the framing or lighting needs fixing" | The app checks framing, not lighting | "The app waits until it can see the joints each movement needs…" |
| "Led by Dr. Gaurav Sharma and Raghunandan S K" | Implies they run the company | "Meet Dr. Gaurav Sharma, …, and Raghunandan S K, …" |
| biomechanix.ai testimonials, "40% fewer no-shows" | Placeholders with no source | Left out |

## Images and accessibility

- Alt text describes what the screenshot shows ("Workout library grouped by
  category"), not "screenshot". Use `alt=""` for decorative images (the logo
  is next to its wordmark).
- One h1 per page, and headings in order. Link text says where it goes
  ("Read the privacy policy", not "click here").
- Don't rely on colour alone. Every lime or cyan label also has text.

## Adding an app (content checklist)

Product page (pattern above) · /applications row plus a comparison column for
every row, including **Medical use** · home card and "Built on MoveMentor"
item · footer link · `_config.yml` `play:` id · /privacy `#<slug>` section
(approval gate, see `web-content-validation`) · /delete-account list ·
/support FAQs · update every count word ("three apps"). The lint cross-checks
counts against `_config.yml`.

Then validate every claim (`web-content-validation`) and run the lint.
