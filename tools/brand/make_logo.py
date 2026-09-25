#!/usr/bin/env python3
"""Regenerate assets/img/logo.svg and assets/img/favicon.svg.

The biomechanix.ai mark is a lime (#CCFF00) rounded square with a black "B"
set in Arial Black. Android and iOS don't ship Arial Black, so a live-text "B"
renders in a fallback font on phones. This outlines the glyph into an SVG
path, so the mark is identical everywhere.

  favicon.svg — exact biomechanix.ai/favicon.svg geometry
                (100x100, rx 20, font-size 60, baseline y=68)
  logo.svg    — biomechanix.ai header proportions
                (40px square, 6px radius, 32px B -> rx 15, glyph 80/100, centered)

Usage: python3 tools/brand/make_logo.py [--font PATH] [--color #CCFF00]
Needs fontTools (pip install fonttools) and Arial Black (macOS ships it at the
default path).
"""
import argparse, os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

ap = argparse.ArgumentParser()
ap.add_argument('--font', default='/System/Library/Fonts/Supplemental/Arial Black.ttf')
ap.add_argument('--color', default='#CCFF00')
ap.add_argument('--out', default=os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'img'))
a = ap.parse_args()

f = TTFont(a.font)
gs = f.getGlyphSet()
g = gs[f.getBestCmap()[ord('B')]]
upm = f['head'].unitsPerEm


def glyph_path(size, base=None, center_y=None):
    sc = size / upm
    x0 = 50 - g.width * sc / 2                      # text-anchor: middle
    if center_y is not None:
        bp = BoundsPen(gs)
        g.draw(TransformPen(bp, (sc, 0, 0, -sc, 0, 0)))
        _, ymin, _, ymax = bp.bounds
        base = center_y - (ymin + ymax) / 2
    pen = SVGPathPen(gs, ntos=lambda v: ('%.2f' % v).rstrip('0').rstrip('.'))
    g.draw(TransformPen(pen, (sc, 0, 0, -sc, x0, base)))
    return pen.getCommands()


def svg(rx, d, note):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <rect width="100" height="100" rx="{rx}" fill="{a.color}"/>
  <!-- {note} -->
  <path fill="#000" d="{d}"/>
</svg>
'''


out = os.path.abspath(a.out)
open(os.path.join(out, 'favicon.svg'), 'w').write(
    svg(20, glyph_path(60, base=68), 'Arial Black "B" outlined; same geometry as biomechanix.ai/favicon.svg'))
open(os.path.join(out, 'logo.svg'), 'w').write(
    svg(15, glyph_path(80, center_y=50), 'Arial Black "B" outlined; header proportions of biomechanix.ai (40px square, 32px B)'))
print('wrote', os.path.join(out, 'favicon.svg'), 'and logo.svg')
