#!/usr/bin/env python3
"""WCAG 2.x contrast check for a stylesheet's colour tokens.

Reads the first `:root { ... }` block of a CSS file, resolves var(--x)
references and alpha colours (composited over the background), and checks
text/background pairs against WCAG AA (4.5:1 body text, 3:1 large text / UI).

Usage: python3 tools/template/contrast.py [CSS] [--pairs fg:bg,fg:bg ...]
  CSS      default assets/site.css
  --pairs  token names without "--". Defaults cover this site's text tokens on
           every surface, plus the button (black on lime).
Exit 1 if a body-text pair is below 4.5:1.
"""
import os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
argv = sys.argv[1:]
css_path = next((a for a in argv if a.endswith('.css')), os.path.join(ROOT, 'assets', 'site.css'))
pairs_arg = argv[argv.index('--pairs') + 1] if '--pairs' in argv else None
DEFAULT_PAIRS = ('ink:bg ink2:bg ink3:bg muted:bg ink:bg2 ink3:bg2 muted:bg2 ink:card ink3:card muted:card '
                 'lime:bg cyan:bg link:bg lime:card cyan:card #000:lime').split()
LARGE_OR_UI = {'lime:bg', 'cyan:bg', 'lime:card', 'cyan:card'}      # accents used for labels/large text

css = re.sub(r'/\*.*?\*/', '', open(css_path).read(), flags=re.S)
m = re.search(r':root\s*{(.*?)}', css, re.S)
if not m:
    sys.exit(f'no :root block in {css_path}')
tokens = dict((k.strip(), v.strip()) for k, v in re.findall(r'--([\w-]+)\s*:\s*([^;]+?)\s*(?:;|$)', m.group(1).strip()))


def parse(value, depth=0):
    value = value.strip()
    v = re.match(r'var\(--([\w-]+)\)', value)
    if v and depth < 10:
        if v.group(1) not in tokens:          # never silently default — a missing token is an error
            raise ValueError(f'token --{v.group(1)} not defined in :root')
        return parse(tokens[v.group(1)], depth + 1)
    if value in tokens and depth < 10 and not value.startswith('#'):
        return parse(tokens[value], depth + 1)
    h = re.match(r'#([0-9a-fA-F]{3,8})$', value)
    if h:
        x = h.group(1)
        if len(x) in (3, 4):
            x = ''.join(c * 2 for c in x)
        r, g, b = (int(x[i:i + 2], 16) for i in (0, 2, 4))
        a = int(x[6:8], 16) / 255 if len(x) == 8 else 1.0
        return r, g, b, a
    f = re.match(r'rgba?\(([^)]+)\)', value)
    if f:
        parts = [p.strip() for p in re.split(r'[,\s/]+', f.group(1)) if p.strip()]
        r, g, b = (float(p) for p in parts[:3])
        a = float(parts[3].rstrip('%')) / (100 if parts[3].endswith('%') else 1) if len(parts) > 3 else 1.0
        return r, g, b, a
    if value.lower() in ('white', '#fff'):
        return 255, 255, 255, 1.0
    if value.lower() == 'black':
        return 0, 0, 0, 1.0
    raise ValueError(f'unsupported colour: {value}')


def over(fg, bg):
    a = fg[3]
    return tuple(fg[i] * a + bg[i] * (1 - a) for i in range(3))


def lum(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def colour(name):
    return parse(name if name.startswith('#') else f'var(--{name})')


fails = 0
print(f'{css_path}')
for pair in (pairs_arg.split(',') if pairs_arg else DEFAULT_PAIRS):
    fg_n, bg_n = pair.split(':')
    try:
        bg = colour(bg_n)
        bg_rgb = over(bg, (0, 0, 0, 1)) if bg[3] < 1 else bg[:3]
        fg_rgb = over(colour(fg_n), bg_rgb + (1,))
    except ValueError as e:
        print(f'  FAIL {pair}: {e}')
        fails += 1
        continue
    l1, l2 = sorted((lum(fg_rgb), lum(bg_rgb)), reverse=True)
    ratio = (l1 + 0.05) / (l2 + 0.05)
    need = 3.0 if pair in LARGE_OR_UI else 4.5
    ok = ratio >= need
    fails += (not ok) and need == 4.5
    print(f'  {"ok  " if ok else "FAIL"} {pair:14} {ratio:5.2f}:1  (needs {need}:1{" large/UI" if need == 3 else ""})')
sys.exit(1 if fails else 0)
