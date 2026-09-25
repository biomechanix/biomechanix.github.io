#!/usr/bin/env python3
"""Render the site to static HTML for local preview, without Jekyll.

GitHub Pages builds this repo with Jekyll, but Jekyll isn't installed locally.
This handles exactly the Liquid the site uses — front matter, the default
layout, {{ page.x }}, {{ site.x.y }}, `| default:`, `| date:`, and
{% if a == "b" %} / {% if a %} blocks. If you add other Liquid, extend this
(or the preview will show raw tags — grep the output for "{{" / "{%").

Usage: python3 tools/preview/render.py [SITE_DIR] [OUT_DIR]
  Writes OUT_DIR/<page>.html and OUT_DIR/<page>/index.html (so /fitness works).
Serve with: python3 -m http.server 8765 --directory OUT_DIR
"""
import os, re, shutil, sys, time

src = sys.argv[1] if len(sys.argv) > 1 else '.'
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.environ.get('TMPDIR', '/tmp'), 'site-preview')

shutil.rmtree(out, ignore_errors=True)
os.makedirs(out)
shutil.copytree(os.path.join(src, 'assets'), os.path.join(out, 'assets'))

# _config.yml: flat keys plus one level of nesting is all the site uses.
site, cur = {'time': str(int(time.time()))}, None
for line in open(os.path.join(src, '_config.yml')):
    if not line.strip() or line.lstrip().startswith('#'):
        continue
    m = re.match(r'^(\s*)([\w-]+):\s*(.*)$', line.rstrip())
    if not m:
        continue
    ind, k, v = m.groups()
    if not ind:
        if v:
            site[k] = v
        else:
            site[k] = {}
            cur = k
    elif isinstance(site.get(cur), dict):
        site[cur][k] = v

layout = open(os.path.join(src, '_layouts', 'default.html')).read()


def get(ctx, path):
    o = ctx
    for p in path.split('.'):
        o = o.get(p) if isinstance(o, dict) else None
    return o


def liquid(t, ctx):
    t = re.sub(r'\{% if ([\w.]+) == "(\w+)" %\}(.*?)\{% endif %\}',
               lambda m: m.group(3) if get(ctx, m.group(1)) == m.group(2) else '', t, flags=re.S)
    t = re.sub(r'\{% if ([\w.]+) %\}(.*?)\{% endif %\}',
               lambda m: m.group(2) if get(ctx, m.group(1)) else '', t, flags=re.S)
    # {{ site.time | date: '%s' }} -> the timestamp (only format the site uses)
    t = re.sub(r"\{\{\s*([\w.]+)\s*\|\s*date:\s*'%s'\s*\}\}", lambda m: str(get(ctx, m.group(1)) or ''), t)

    def var(m):
        v = get(ctx, m.group(1))
        if not v and m.group(2):
            v = get(ctx, m.group(2))
        return str(v or '')
    return re.sub(r'\{\{\s*([\w.]+)(?:\s*\|\s*default:\s*([\w.]+))?\s*\}\}', var, t)


pages = []
for f in sorted(os.listdir(src)):
    if not f.endswith('.html'):
        continue
    s = open(os.path.join(src, f)).read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', s, re.S)
    if not m:
        continue
    fm, body = m.groups()
    ctx = {'site': site, 'page': dict(re.findall(r'^(\w+):\s*(.*)$', fm, re.M))}
    html = liquid(layout.replace('{{ content }}', liquid(body, ctx)), ctx)
    open(os.path.join(out, f), 'w').write(html)
    name = f[:-5]
    if name != 'index':
        os.makedirs(os.path.join(out, name), exist_ok=True)
        open(os.path.join(out, name, 'index.html'), 'w').write(html)
    pages.append(name)
    leftover = re.findall(r'\{\{[^}]*\}\}|\{%[^%]*%\}', html)
    if leftover:
        print(f'WARN {f}: unrendered Liquid {leftover[:3]}', file=sys.stderr)

print(f'rendered {len(pages)} pages -> {out}: {" ".join(pages)}')
