#!/usr/bin/env python3
"""Content lint for biomechanix.github.io — validates what the site SAYS.

Checks every page's visible text (not markup) for:
  1. Unsourced numbers    — every number must be covered by an entry in
                            tools/content/claims.yml for that page.
  2. Required statements  — disclaimers/positioning that must stay on a page
                            (e.g. Sameeksha "Screening, not diagnosis").
  3. Forbidden content    — placeholders, investor material, unverifiable or
                            unsafe health claims, the over-broad privacy phrase.
  4. Naming               — exact app names; only approved people named.
  5. Consistency          — app-count words match the apps in _config.yml.
  6. Links                — internal links resolve to a page and, if given,
                            an anchor id on that page; load-bearing anchors exist.

Usage: python3 tools/content/content_lint.py [SITE_DIR]      (default: repo root)
Exit 0 = clean, 1 = errors. Warnings don't fail the run.
Needs PyYAML (python3 -m pip install pyyaml).
"""
import glob, html, os, re, sys
import yaml

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..'))
LEDGER = yaml.safe_load(open(os.path.join(ROOT, 'tools', 'content', 'claims.yml')))
CONFIG = yaml.safe_load(open(os.path.join(ROOT, '_config.yml')))

NUMBER_WORDS = {'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                'dozen', 'hundred', 'thousand', 'million', 'billion', 'twice', 'half'}
COUNT_WORDS = {2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six'}

# Statements that must remain on a page (why: domain/safety/compliance rules).
REQUIRED = {
    'sameeksha.html': ['Screening, not diagnosis'],
    'applications.html': ['Screening, not diagnosis', 'Fitness and wellness only', 'Supports a qualified clinician'],
    'fitness.html': ["doesn't provide medical advice"],
    'physio.html': ['remain the clinician'],
}
# Anchors other sites/apps link to — renaming them breaks store/app links.
REQUIRED_IDS = {
    'privacy.html': ['summary', 'all-apps', 'face-data', 'on-device-ai', 'fitness', 'physio', 'sameeksha', 'deletion'],
    'company.html': ['about', 'team'],
    'index.html': ['apps', 'platform', 'company'],
}
# (pattern, reason). Case-insensitive, matched against visible text.
FORBIDDEN = [
    (r'\b(TODO|TBD|FIXME|XXX|lorem ipsum|placeholder|\[insert)\b', 'placeholder text'),
    (r'\b(MRR|ARR|seed round|SAFE notes?|series a|pre-money|valuation|runway)\b', 'investor material'),
    (r'\bpatent', 'patent claims (investor material; not for the site)'),
    (r'\bhaptic (wearable|device|band|hardware|bracelet)', 'unreleased hardware (haptic wearable); phone haptics are fine'),
    (r'\$\s?\d', 'prices/financial figures'),
    (r'\b(clinical[- ]grade|clinically (proven|validated)|FDA|CE[- ]marked|HIPAA[- ]compliant|medical device)\b',
     'regulatory/clinical claim with no evidence on file'),
    (r'\b(cures?|guarantee[sd]?|100% accurate|no side effects)\b', 'absolute health claim'),
    (r'\b(sub-?\s?\d+\s?ms|less than half a second|real-time diagnosis)\b', 'unverified performance claim'),
    (r'\b(will|can|helps? to|helps?) diagnos', 'diagnostic claim (Sameeksha screens, it does not diagnose)'),
    (r'\bthe video never leaves\b|\bvideo never leaves your phone\b',
     'over-broad privacy claim — say "live camera video is never uploaded" (Physio clip shares upload)'),
    (r'\b(testimonial|customers say|trusted by \d)', 'testimonial/social proof with no source'),
]
# Exact product names; left = wrong forms to flag.
NAMING = [
    (r'\bMovementor\b', 'MoveMentor'),
    (r'\bMove Mentor\b', 'MoveMentor'),
    (r'\bPhysioTherapy\b', 'MoveMentor Physio'),
    (r'\bSameksha\b|\bSamiksha\b', 'Sameeksha'),
    (r'\bBioMechanix\b|\bBiomechanics Inc', 'Biomechanix'),
]

errors, warnings = [], []


def visible_text(raw):
    s = re.sub(r'^---\n.*?\n---\n', '', raw, flags=re.S)
    s = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<!--.*?-->', ' ', s, flags=re.S)
    s = re.sub(r'<span class="n">.*?</span>', ' ', s, flags=re.S)       # card labels 01..06 / ENGINE
    s = re.sub(r'\{\{.*?\}\}|\{%.*?%\}', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'\s+', ' ', html.unescape(s))


def number_tokens(text):
    for m in re.finditer(r'(?<![\w.])(\d+(?:\.\d+)?)|\b([a-z]+)\b', text, re.I):
        if m.group(1):
            yield m.group(1), m.start()
        elif m.group(2).lower() in NUMBER_WORDS:
            yield m.group(2).lower(), m.start()


pages = {os.path.basename(f): open(f).read() for f in sorted(glob.glob(os.path.join(ROOT, '*.html')))}
ids = {p: set(re.findall(r'\bid="([^"]+)"', raw)) for p, raw in pages.items()}
layout = open(os.path.join(ROOT, '_layouts', 'default.html')).read()
layout_ids = set(re.findall(r'\bid="([^"]+)"', layout))

covered = {}
for c in LEDGER['claims']:
    for p in c['pages']:
        covered.setdefault(p, set()).update(str(n).lower() for n in c.get('numbers', []))

app_count = len(CONFIG.get('play', {}))

for page, raw in pages.items():
    text = visible_text(raw)
    ctx = lambda i: '…' + text[max(0, i - 40):i + 40] + '…'

    # 1. numbers
    allowed = covered.get(page, set()) | covered.get('*', set())
    for tok, i in number_tokens(text):
        if tok not in allowed:
            errors.append(f'{page}: unsourced number "{tok}" — add a claims.yml entry after verifying it: {ctx(i)}')

    # 2. required statements
    for req in REQUIRED.get(page, []):
        if req.lower() not in text.lower():
            errors.append(f'{page}: required statement missing: "{req}"')

    # 3. forbidden
    for pat, why in FORBIDDEN:
        for m in re.finditer(pat, text, re.I):
            errors.append(f'{page}: {why}: "{m.group(0)}" {ctx(m.start())}')

    # 4. naming + people
    for pat, right in NAMING:
        for m in re.finditer(pat, text):
            errors.append(f'{page}: write "{right}", not "{m.group(0)}" {ctx(m.start())}')
    for name in LEDGER.get('not_approved_names', []):
        if re.search(r'\b' + re.escape(name) + r'\b', text):
            errors.append(f'{page}: names "{name}", who is not approved for the site (claims.yml people)')
    approved_words = {w for p in LEDGER['people'] for w in p['name'].replace('Dr.', '').split()}
    for m in re.finditer(r'\bDr\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text):
        if not set(m.group(1).split()) <= approved_words:     # "Dr. Sharma" ok if Sharma is approved
            errors.append(f'{page}: "{m.group(0)}" is not in the approved people list')

    # 5. consistency: "<count word> apps" must equal the number of apps
    for m in re.finditer(r'\b(two|three|four|five|six)\s+(apps|applications)\b', text, re.I):
        if m.group(1).lower() != COUNT_WORDS.get(app_count):
            errors.append(f'{page}: says "{m.group(0)}" but _config.yml lists {app_count} apps {ctx(m.start())}')

    # 6. links
    for href in re.findall(r'href="([^"]+)"', raw):
        if href.startswith(('http', 'mailto:', '{{')):
            continue
        path, _, anchor = href.partition('#')
        target = page if path == '' else ('index.html' if path in ('/', '/index.html') else path.strip('/').removesuffix('.html') + '.html')
        if path.startswith('/assets/'):
            if not os.path.exists(os.path.join(ROOT, path.lstrip('/'))):
                errors.append(f'{page}: broken asset link {href}')
            continue
        if target not in pages:
            errors.append(f'{page}: broken link {href} (no {target})')
        elif anchor and anchor not in ids[target] and anchor not in layout_ids:
            errors.append(f'{page}: link {href} points at missing anchor #{anchor} on {target}')

# links in the shared layout (header/footer) must resolve too
for href in re.findall(r'href="([^"]+)"', layout):
    if href.startswith(('http', 'mailto:', '{{', '#')) or href.startswith('/assets/'):
        continue
    path, _, anchor = href.partition('#')
    target = 'index.html' if path in ('/', '/index.html') else path.strip('/').removesuffix('.html') + '.html'
    if target not in pages:
        errors.append(f'_layouts/default.html: broken link {href}')
    elif anchor and anchor not in ids[target]:
        errors.append(f'_layouts/default.html: link {href} points at missing anchor #{anchor}')

for page, want in REQUIRED_IDS.items():
    for i in want:
        if page in pages and i not in ids[page]:
            errors.append(f'{page}: load-bearing anchor id="{i}" is missing (external links depend on it)')

# ledger hygiene: entries pointing at pages that don't exist
for c in LEDGER['claims']:
    for p in c['pages']:
        if p != '*' and p not in pages:
            warnings.append(f'claims.yml {c["id"]}: page {p} does not exist')
    if not c.get('source'):
        errors.append(f'claims.yml {c["id"]}: no source')

for w in warnings:
    print('WARN ', w)
for e in errors:
    print('ERROR', e)
print(f'{len(pages)} pages, {len(LEDGER["claims"])} claims, {len(errors)} errors, {len(warnings)} warnings')
sys.exit(1 if errors else 0)
