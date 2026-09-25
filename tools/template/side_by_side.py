#!/usr/bin/env python3
"""Screenshot a template page and the matching page of this site at the same
viewport widths, and compose them side by side (template left, site right)
into one PNG per width — the artefact you review and attach to the PR.

Uses Playwright (Chromium, falling back to installed Google Chrome) so phone
widths are real viewports — headless Chrome's CLI clamps windows to ~500px.

Usage: python3 tools/template/side_by_side.py TEMPLATE SITE OUT_PREFIX [--widths 1280,390] [--height 2400]
  TEMPLATE / SITE   URL or local .html path (file:// is added for paths)
  OUT_PREFIX        e.g. $TMPDIR/compare-home  ->  compare-home-1280.png, compare-home-390.png
Serve the site preview first (tools/preview/render.py + http.server) and pass its URL.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
argv = [a for a in sys.argv[1:]]
if len([a for a in argv if not a.startswith('--')]) < 3:
    sys.exit(__doc__)
opts = {argv[i]: argv[i + 1] for i in range(len(argv) - 1) if argv[i].startswith('--')}
pos = [a for i, a in enumerate(argv) if not a.startswith('--') and (i == 0 or not argv[i - 1].startswith('--'))]
tpl, site, prefix = pos[:3]
widths = [int(w) for w in opts.get('--widths', '1280,390').split(',')]
max_h = int(opts.get('--height', '2400'))
as_url = lambda s: s if s.startswith(('http://', 'https://', 'file://')) else 'file://' + os.path.abspath(s)

tmp = tempfile.mkdtemp(prefix='sbs-')
jobs = [{'url': as_url(u), 'width': w, 'out': os.path.join(tmp, f'{tag}-{w}.png')}
        for w in widths for tag, u in (('template', tpl), ('site', site))]
r = subprocess.run(['node', os.path.join(HERE, 'shoot.cjs'), json.dumps(jobs)], capture_output=True, text=True)
if r.returncode != 0:
    sys.exit('screenshot failed:\n' + r.stdout + r.stderr)

for w in widths:
    a = Image.open(os.path.join(tmp, f'template-{w}.png'))
    b = Image.open(os.path.join(tmp, f'site-{w}.png'))
    a = a.crop((0, 0, a.width, min(a.height, max_h)))
    b = b.crop((0, 0, b.width, min(b.height, max_h)))
    gap, label = 24, 36
    canvas = Image.new('RGB', (a.width + b.width + gap, max(a.height, b.height) + label), (128, 128, 128))
    canvas.paste(a, (0, label))
    canvas.paste(b, (a.width + gap, label))
    d = ImageDraw.Draw(canvas)
    d.text((8, 10), f'TEMPLATE  {w}px', fill=(255, 255, 255))
    d.text((a.width + gap + 8, 10), f'SITE  {w}px', fill=(255, 255, 255))
    out = f'{prefix}-{w}.png'
    canvas.save(out)
    print(f'wrote {out}  ({canvas.width}x{canvas.height}; template page {a.width}x{a.height}, site {b.width}x{b.height})')
