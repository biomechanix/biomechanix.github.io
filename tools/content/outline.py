#!/usr/bin/env python3
"""Print the site's information architecture: every page with its front
matter (title, nav, section), its heading outline, and its anchor ids.

Use it before deciding where new content goes, and to spot duplicated or
orphaned sections. Output is plain text; add --md for a Markdown table of pages.

Usage: python3 tools/content/outline.py [SITE_DIR] [--md]
"""
import glob, html, os, re, sys

args = [a for a in sys.argv[1:] if not a.startswith('--')]
root = os.path.abspath(args[0] if args else os.path.join(os.path.dirname(__file__), '..', '..'))
md = '--md' in sys.argv

layout = open(os.path.join(root, '_layouts', 'default.html')).read()
nav = re.findall(r'<nav class="nav".*?</nav>', layout, re.S)
nav_items = re.findall(r'href="([^"]+)"[^>]*>([^<]+)</a>', nav[0]) if nav else []
footer = re.findall(r'<footer.*?</footer>', layout, re.S)
footer_items = re.findall(r'href="([^"]+)"[^>]*>([^<]+)</a>', footer[0]) if footer else []

print('Primary nav: ' + ' · '.join(f'{t} ({h})' for h, t in nav_items))
print('Footer links: ' + ', '.join(f'{t} ({h})' for h, t in footer_items))
print()
rows = []
for f in sorted(glob.glob(os.path.join(root, '*.html'))):
    raw = open(f).read()
    fm = dict(re.findall(r'^(\w+):\s*(.*)$', (re.match(r'^---\n(.*?)\n---', raw, re.S) or [None, ''])[1], re.M))
    name = os.path.basename(f)
    url = '/' if name == 'index.html' else '/' + name[:-5]
    heads = [(lvl, re.sub(r'<[^>]+>', '', html.unescape(t)).strip())
             for lvl, t in re.findall(r'<h([123])[^>]*>(.*?)</h\1>', raw, re.S)]
    ids = re.findall(r'\bid="([^"]+)"', raw)
    rows.append((url, fm.get('title', '(home)'), fm.get('section', fm.get('nav', '')), len(heads), fm.get('description', '')))
    if md:
        continue
    print(f'{url}  title="{fm.get("title", "(home)")}"  nav={fm.get("nav", "-")}  section={fm.get("section", "-")}')
    if fm.get('description'):
        print(f'   description ({len(fm["description"])} chars): {fm["description"][:110]}{"…" if len(fm["description"]) > 110 else ""}')
    for lvl, t in heads:
        print('   ' + '  ' * (int(lvl) - 1) + f'h{lvl} {t}')
    print('   ids: ' + (', '.join(ids) or '-'))
    print()

if md:
    print('| URL | Title | Nav section | Headings | Description length |')
    print('|---|---|---|---|---|')
    for url, title, sec, n, desc in rows:
        print(f'| `{url}` | {title} | {sec or "-"} | {n} | {len(desc)} |')
