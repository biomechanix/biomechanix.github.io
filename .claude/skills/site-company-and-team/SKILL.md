---
name: site-company-and-team
description: "Use when editing the Company page (/company) or the company/platform sections of the biomechanix.github.io homepage — adding, removing or retitling a team member, adding a bio or photo, changing the mission/about copy, values, locations, or the MoveMentor platform description. Encodes the rule that only people the owner names are listed, that bios come from an approved source or the owner (never invented), how the team card and homepage teaser stay in sync, and what company information must stay private. Trigger phrases: \"team page\", \"add to the team\", \"about us\", \"company page\", \"leadership\", \"bio\", \"headshot\", \"our mission\", \"values\", \"platform section\"."
---

# site-company-and-team

## Where it lives

- `company.html` — hero, `#about` (why we exist + roots + `.facts`),
  `#team` (`.person` cards), `#values` (`ol.steps`), `#contact`.
- `index.html` — `#platform` (MoveMentor platform: four cards + `.built-on`
  row) and `#company` (short about + a Team teaser card linking
  `/company#team`).
- Nav "Company" → `/company` (front matter `section: company` highlights it);
  footer links About + Team.

## Team rules

- **List only the people the owner has asked to show.** The mm-business
  one-pagers mention others (e.g. a CEO/CTO and an advisor); being in an
  investor document is not consent to be on the public site. Ask before adding
  anyone.
- **Bios**: use the owner's words or an approved company source, lightly
  edited into third person. If there's none, either ask or use a short line
  describing the role (and say so in the PR). Never invent credentials, years,
  employers or degrees.
- **Photos**: none by default — cards show initials in `.avatar`. Only add a
  headshot the owner provides for the site (put it in `assets/img/team/`,
  square, ~240px, with real width/height attributes and `alt="<Name>"`).
- Titles exactly as given ("Chief Revenue Officer", not "CRO", unless asked).
- When the team changes, update the homepage teaser sentence in `#company`
  ("Meet … and …") in the same PR.

Current team (as approved 2026-09-23): **Dr. Gaurav Sharma**, Chief Revenue
Officer (bio from the company one-pager: sports physiotherapist, 15+ years,
mental agility and performance vision); **Raghunandan S K**, Head of Research
and Development (role-description line only — replace when a bio arrives).

Card template:
```html
<article class="card person">
  <span class="avatar" aria-hidden="true">AB</span>
  <h3>Full Name</h3>
  <p class="role">Exact Title</p>
  <p>Bio…</p>
</article>
```
Keep `.grid-2` for two people; switch to `.grid-3` at three.

## Company copy

Public, reusable: the mission ("expert movement coaching, for everyone"), the
problem framing, "deep roots in physiotherapy, sports science and
rehabilitation … more than a decade of hands-on clinical experience" (the
company's own public claim on biomechanix.ai), "India & USA, remote-friendly",
"sports & therapy, one engine", "camera only", the four values.

Private — never on the site: funding, revenue/MRR/ARR, projections, patent
counts, hardware roadmap (haptic wearable), pricing bundles, hiring plans,
investor contacts. See `site-content-accuracy`.

Platform section claims must match shipped behaviour (shared on-device
engine; expert-authored movements via capture → proposed model → expert
refines/publishes; expert in the loop; private by design). Sports coaching
was removed from the "Built on MoveMentor" row at the owner's request — don't
reintroduce unreleased products there.
