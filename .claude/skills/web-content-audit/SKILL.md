---
name: web-content-audit
description: "Use to audit the whole Biomechanix website for content that is stale, inconsistent, broken or no longer true — periodically, before or after an app release, when an app repo changes behaviour, when a Play listing goes live, after a rebrand, or when someone asks \"is the website still accurate?\". Re-verifies ledger claims whose sources changed, checks store and external links, compares in-app privacy URLs with the site, sweeps for cross-page inconsistencies and missing disclaimers, and produces a prioritized audit report. Trigger phrases: \"audit the website\", \"is the site up to date\", \"content review\", \"check for broken links\", \"stale content\", \"before the release\", \"site health\", \"what's wrong with the website\"."
---

# web-content-audit

Content goes stale when the apps change and the site doesn't. The audit's job
is to find every place where the site and reality have drifted, then rank the
fixes by harm: false health or privacy claims first, broken paths second,
polish last.

## Run the checks

```bash
cd ~/code/projects/biomechanix.github.io && git pull
python3 tools/content/content_lint.py          # rules, ledger coverage, links, anchors, naming, counts
python3 tools/content/source_drift.py          # sources changed since verification, external links, in-app privacy URLs
python3 tools/content/outline.py --md          # IA snapshot: pages, headings, description lengths
```

Then work through the manual checks the scripts can't do:

1. **Re-verify drifted claims.** For each `!!` in section 1 of `source_drift`,
   re-read the source. If the claim still holds, bump `verified` in
   `claims.yml`. If it doesn't, fix the page (`web-content-validation`).
2. **Capability drift.** Scan each app repo's recent history for shipped
   behaviour the site doesn't mention, or mentions differently:
   `git -C ../mm-<app> log --oneline --since=<last audit> -- android/ docs/`.
   Pay most attention to anything touching uploads, sync, accounts, deletion
   or clinical wording. Those change /privacy.
3. **Cross-page consistency.** For each fact with summaries (see the
   canonical-home table in `web-information-architecture`), open every page
   that states it and compare the wording and numbers. Typical drift: an app
   described one way on its page and another way in the /applications row, or
   the home card.
4. **Store reality.** Every "Get it on Google Play" button must resolve (200).
   If a listing 404s, the button sends visitors to a Google error page. Raise
   it with the owner (remove the button, or say "coming soon") rather than
   leaving it.
5. **Policy alignment.** In-app `privacyPolicyUrl` values must be
   `https://biomechanix.github.io/privacy`. Compare /privacy with each app's
   Play *Data safety* answers (`store/play/*/data-safety.md`).
6. **Approvals still valid.** The team list matches `claims.yml people`, and
   nobody has left or changed title. There's no pending-review comment left in
   /privacy after approval.
7. **Dates.** Effective dates, "© <year>" in the footer, and any "new" or
   "coming soon" wording.

## Report format

Write the result as a short report (in chat, or as a PR description if you're
fixing things):

```
Website content audit — <date>
Critical (false/unsafe claims, compliance): …
Broken (links, store buttons, anchors): …
Stale (changed sources, outdated facts): …
Inconsistent (same fact, different wording): …
Polish (descriptions > 160 chars, headings, alt text): …
Verified OK: <what was checked and passed>
Needs the owner: <decisions only they can make>
```

Every item names the page, quotes the text, and gives the source that
contradicts it. Fix what's clearly wrong in a PR. Put decisions (removing a
store button, policy changes, people) under *Needs the owner*.

## Known open items (as of 2026-09-25)

- All three Google Play ids (`com.biomechanix.mmfitness`, `.physiotherapy`,
  `.selfassess`) return 404. The site's Play buttons are broken for the public.
- `mm-physio` `PhysioTherapyBrandConfig.kt` has `privacyPolicyUrl =
  https://movementor.health/privacy`, a parked domain.
- Page descriptions on /applications, /fitness, /physio and /sameeksha are
  over 160 characters.
