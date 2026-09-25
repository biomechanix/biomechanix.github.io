#!/usr/bin/env python3
"""Check pages for horizontal overflow at real phone widths.

Headless Chrome clamps its window to ~500px, so a 390px --window-size
screenshot is silently a crop of a 500px layout — it hides overflow instead
of showing it. This loads each page in an iframe of the exact width and
reports innerWidth x scrollWidth; they must be equal.

Usage: python3 tools/preview/check_widths.py BASE_URL [page ...] [--widths 360,768]
  BASE_URL  e.g. http://localhost:8765 (a served preview) — the harness is
            written into the served directory, so it must be a local preview.
  --dir     preview directory being served (default: $TMPDIR/site-preview)
Exit code 1 if any page overflows. Prints the widest offending elements.
"""
import argparse, os, re, subprocess, sys

CHROME = os.environ.get('CHROME', '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')

ap = argparse.ArgumentParser()
ap.add_argument('base')
ap.add_argument('pages', nargs='*')
ap.add_argument('--widths', default='360,768')
ap.add_argument('--dir', default=os.path.join(os.environ.get('TMPDIR', '/tmp'), 'site-preview'))
a = ap.parse_args()

pages = a.pages or sorted(f[:-5] for f in os.listdir(a.dir) if f.endswith('.html') and not f.startswith(('m-', 'frame')))
widths = [int(w) for w in a.widths.split(',')]

probe = ("<script>addEventListener('load',()=>{const w=innerWidth,s=document.documentElement.scrollWidth;"
         "const bad=[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>w+1"
         "&&!e.closest('.shots,.table-wrap')).slice(0,3).map(e=>e.tagName+'.'+e.className).join(',');"
         "parent.postMessage('%s '+w+'x'+s+(bad?' '+bad:''),'*')})</script></body>")
for p in pages:
    html = open(os.path.join(a.dir, p + '.html')).read()
    open(os.path.join(a.dir, f'm-{p}.html'), 'w').write(html.replace('</body>', probe % p))

frames = ''.join(f'<iframe style="width:{w}px;height:600px" src="m-{p}.html"></iframe>' for w in widths for p in pages)
open(os.path.join(a.dir, 'frame.html'), 'w').write(
    '<html><body><div id=o></div><script>addEventListener("message",e=>{o.textContent+=e.data+" | "})</script>'
    + frames + '</body></html>')

dom = subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--virtual-time-budget=10000',
                      '--dump-dom', a.base.rstrip('/') + '/frame.html'],
                     capture_output=True, text=True, timeout=120).stdout
m = re.search(r'<div id="o">([^<]*)', dom)
results = [r.strip() for r in (m.group(1) if m else '').split('|') if r.strip()]
expected = len(pages) * len(widths)
bad = 0
for r in results:
    name, dims = r.split()[:2]
    w, s = dims.split('x')
    ok = w == s
    bad += not ok
    print(('ok   ' if ok else 'FAIL ') + r)
if len(results) != expected:
    # A silent harness is not a pass — see the probe-discipline skill.
    print(f'ERROR: expected {expected} results, got {len(results)} (server down? page errors?)', file=sys.stderr)
    sys.exit(2)
sys.exit(1 if bad else 0)
