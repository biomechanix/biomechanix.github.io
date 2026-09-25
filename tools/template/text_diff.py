#!/usr/bin/env python3
"""Prove a template alignment changed the LOOK, not the CONTENT.

Compares this repo's working tree with a git ref (default: origin/main) and
reports, per page:
  - visible text differences (word-level; markup/class changes are ignored)
  - pages added or removed (URLs are permanent — removals are errors)
  - anchor ids removed (links from the apps/stores/other pages depend on them)
  - nav / footer labels changed (layout text counts as content too)

Usage: python3 tools/template/text_diff.py [--ref origin/main] [--allow page.html ...]
  --allow   pages whose text is expected to change (e.g. a deliberate copy edit
            reviewed separately); they're reported but don't fail the run.
Exit 0 = content preserved; 1 = unexpected content change.
"""
import difflib, html, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
argv = sys.argv[1:]
ref = argv[argv.index('--ref') + 1] if '--ref' in argv else 'origin/main'
allow = set(argv[argv.index('--allow') + 1:]) if '--allow' in argv else set()


def git_show(path):
    r = subprocess.run(['git', '-C', ROOT, 'show', f'{ref}:{path}'], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def git_ls():
    r = subprocess.run(['git', '-C', ROOT, 'ls-tree', '--name-only', ref], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f'cannot read ref {ref}: {r.stderr.strip()}')
    return r.stdout.split()


def words(raw):
    s = re.sub(r'^---\n.*?\n---\n', '', raw, flags=re.S)                     # front matter handled separately
    s = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<!--.*?-->', ' ', s, flags=re.S)
    alts = re.findall(r'\balt="([^"]*)"', s)                                  # alt text is content
    s = re.sub(r'\{\{.*?\}\}|\{%.*?%\}', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    return html.unescape(s + ' ' + ' '.join(alts)).split()


def front_matter(raw):
    m = re.match(r'^---\n(.*?)\n---\n', raw, re.S)
    return dict(re.findall(r'^(title|description):\s*(.*)$', m.group(1), re.M)) if m else {}


before_pages = {f for f in git_ls() if f.endswith('.html')}
after_pages = {f for f in os.listdir(ROOT) if f.endswith('.html')}
errors, notes = [], []

for f in sorted(before_pages - after_pages):
    errors.append(f'{f}: page REMOVED — its URL is permanent (leave a stub that links to the new location)')
for f in sorted(after_pages - before_pages):
    notes.append(f'{f}: page added (new content must go through web-content-validation)')

for f in sorted(before_pages & after_pages) + ['_layouts/default.html']:
    old = git_show(f)
    new_path = os.path.join(ROOT, f)
    if old is None or not os.path.exists(new_path):
        continue
    new = open(new_path).read()
    ow, nw = words(old), words(new)
    lost_ids = set(re.findall(r'\bid="([^"]+)"', old)) - set(re.findall(r'\bid="([^"]+)"', new))
    if lost_ids:
        errors.append(f'{f}: anchor id(s) removed: {", ".join(sorted(lost_ids))}')
    ofm, nfm = front_matter(old), front_matter(new)
    for k in ofm:
        if ofm.get(k) != nfm.get(k):
            (notes if f in allow else errors).append(f'{f}: front-matter {k} changed: "{ofm.get(k)}" -> "{nfm.get(k)}"')
    if ow == nw:
        print(f'same  {f}')
        continue
    sm = difflib.SequenceMatcher(a=ow, b=nw, autojunk=False)
    changes = []
    for op, a1, a2, b1, b2 in sm.get_opcodes():
        if op != 'equal':
            changes.append(f'      {op}: "{" ".join(ow[a1:a2])[:120]}" -> "{" ".join(nw[b1:b2])[:120]}"')
    label = 'ALLOW' if f in allow else 'DIFF '
    print(f'{label} {f}: {len(changes)} text change(s), similarity {sm.ratio():.3f}')
    print('\n'.join(changes[:15]) + ('\n      …' if len(changes) > 15 else ''))
    if f not in allow:
        errors.append(f'{f}: visible text changed ({len(changes)} change(s)) — a template alignment should not change content')

for n in notes:
    print('NOTE ', n)
for e in errors:
    print('ERROR', e)
print(f'compared against {ref}: {len(errors)} error(s)')
sys.exit(1 if errors else 0)
