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

# _config.yml parsed as real YAML (inline comments etc. behave as in Jekyll)
import yaml
site = yaml.safe_load(open(os.path.join(src, '_config.yml'))) or {}
site['time'] = str(int(time.time()))

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

    def expr(m):
        """{{ var | default: other | replace: 'a', 'b' }} — the filters this site uses."""
        parts = [p.strip() for p in m.group(1).split('|')]
        v = get(ctx, parts[0])
        for f in parts[1:]:
            name, _, arg = f.partition(':')
            name, arg = name.strip(), arg.strip()
            if name == 'default':
                v = v or get(ctx, arg)
            elif name == 'replace':
                a, b = [x.strip().strip("'\"") for x in re.findall(r"'[^']*'|\"[^\"]*\"", arg)][:2]
                v = str(v or '').replace(a, b)
            else:
                return m.group(0)          # unknown filter: leave it visible (render.py warns)
        return str(v or '')
    return re.sub(r'\{\{\s*([\w.]+(?:\s*\|[^}]*)?)\s*\}\}', expr, t)


pages = []
for f in sorted(os.listdir(src)):
    if not f.endswith('.html'):
        continue
    s = open(os.path.join(src, f)).read()
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', s, re.S)
    if not m:
        continue
    fm, body = m.groups()
    page = dict(re.findall(r'^(\w+):\s*(.*)$', fm, re.M))
    page['url'] = '/' if f == 'index.html' else '/' + f                 # Jekyll's page.url for these files
    ctx = {'site': site, 'page': page}
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
