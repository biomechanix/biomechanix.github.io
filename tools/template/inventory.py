#!/usr/bin/env python3
"""Inventory a website template so it can be mapped onto this site.

Accepts:
  - a directory or .zip of an HTML/CSS theme or design-tool export (Figma/Webflow/Framer)
  - a single .html page (a mockup) or an http(s) URL of one (its stylesheets are fetched too)
  - an .xml file: a sitemap (<urlset>) or any content/structure model
  - an .svg design export

Reports (Markdown by default, --json for machine use):
  pages      title, headings outline, landmark regions, sections, nav links, forms
  components class-name frequency across pages (what the template is built from)
  tokens     CSS custom properties, colour/font/size/radius/shadow values by frequency, breakpoints, @font-face
  assets     images (dimensions), fonts, icons, scripts — with sizes
  risks      external scripts, trackers, remote fonts/CDNs, lorem ipsum, missing alt, license/attribution terms
  xml        sitemap URLs, or an element-path outline with counts and sample values

Usage: python3 tools/template/inventory.py PATH_OR_URL [--json] [--out FILE]
"""
import collections, html, json, os, re, sys, tempfile, urllib.parse, urllib.request, zipfile
import xml.etree.ElementTree as ET

args = [a for a in sys.argv[1:] if not a.startswith('--')]
if not args:
    sys.exit(__doc__)
SRC = args[0]
AS_JSON = '--json' in sys.argv
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None

TRACKERS = {
    'googletagmanager': 'Google Tag Manager', 'google-analytics': 'Google Analytics', 'gtag(': 'Google Analytics (gtag)',
    'connect.facebook.net': 'Meta pixel', 'fbq(': 'Meta pixel', 'hotjar': 'Hotjar', 'clarity.ms': 'Microsoft Clarity',
    'segment.com': 'Segment', 'mixpanel': 'Mixpanel', 'intercom': 'Intercom', 'hs-scripts': 'HubSpot',
    'plausible.io': 'Plausible', 'cdn.amplitude': 'Amplitude', 'linkedin.com/insight': 'LinkedIn Insight',
}
IMG_EXT = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.svg', '.ico'}
FONT_EXT = {'.woff', '.woff2', '.ttf', '.otf', '.eot'}


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'replace')


# ---------- load sources ----------
root, files = None, {}          # relpath -> text (for html/css/js/xml/svg), assets listed separately
assets = []                     # (relpath, bytes, kind)
if SRC.startswith(('http://', 'https://')):
    page = fetch(SRC)
    files['index.html'] = page
    for href in re.findall(r'<link[^>]+rel=["\']?stylesheet[^>]*href=["\']([^"\']+)', page, re.I) + \
            re.findall(r'<link[^>]+href=["\']([^"\']+\.css[^"\']*)', page, re.I):
        u = urllib.parse.urljoin(SRC, href)
        if 'fonts.googleapis' in u:
            continue
        try:
            files['css/' + os.path.basename(urllib.parse.urlparse(u).path) or 'style.css'] = fetch(u)
        except Exception as e:
            files.setdefault('_errors', '')
            files['_errors'] += f'could not fetch {u}: {e}\n'
    root = SRC
else:
    p = os.path.abspath(SRC)
    if p.endswith('.zip'):
        tmp = tempfile.mkdtemp(prefix='tpl-')
        zipfile.ZipFile(p).extractall(tmp)
        p = tmp
    if os.path.isdir(p):
        root = p
        for dp, dn, fn in os.walk(p):
            dn[:] = [d for d in dn if d not in ('node_modules', '.git', '__MACOSX')]
            for f in fn:
                full = os.path.join(dp, f)
                rel = os.path.relpath(full, p)
                ext = os.path.splitext(f)[1].lower()
                size = os.path.getsize(full)
                if ext in ('.html', '.htm', '.css', '.xml', '.svg', '.js', '.txt', '.md', '.json') and size < 3_000_000:
                    files[rel] = open(full, encoding='utf-8', errors='replace').read()
                if ext in IMG_EXT:
                    assets.append((rel, size, 'image'))
                elif ext in FONT_EXT:
                    assets.append((rel, size, 'font'))
                elif ext == '.js':
                    assets.append((rel, size, 'script'))
    else:
        root = os.path.dirname(p)
        files[os.path.basename(p)] = open(p, encoding='utf-8', errors='replace').read()

report = {'source': SRC, 'pages': [], 'components': [], 'tokens': {}, 'assets': {}, 'risks': [], 'xml': [], 'license': []}

# ---------- license / attribution ----------
for rel, text in files.items():
    if re.search(r'(^|/)(license|licence|readme|credits?)[^/]*$', rel, re.I):
        terms = []
        for pat, label in [(r'CC BY(?![- ]?NC)[- ]?\d', 'Creative Commons Attribution — credit required'),
                           (r'Creative Commons Attribution', 'Creative Commons Attribution — credit required'),
                           (r'NonCommercial|CC BY-NC', 'NON-COMMERCIAL licence — not usable for a company site'),
                           (r'\bMIT License\b', 'MIT — keep the copyright notice'),
                           (r'regular license|extended license|envato|themeforest', 'Marketplace licence — check purchase terms'),
                           (r'attribution|credit', 'mentions attribution/credit')]:
            if re.search(pat, text, re.I):
                terms.append(label)
        report['license'].append({'file': rel, 'terms': sorted(set(terms)) or ['(no licence terms recognised — read it)'],
                                  'excerpt': re.sub(r'\s+', ' ', text[:300])})
if not report['license']:
    report['risks'].append('No LICENSE/README found — confirm you have the right to use this template.')

# ---------- HTML pages ----------
class_freq = collections.Counter()
for rel, text in sorted(files.items()):
    if not rel.lower().endswith(('.html', '.htm')):
        continue
    t = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    title = html.unescape(re.sub(r'\s+', ' ', (re.search(r'<title[^>]*>(.*?)</title>', t, re.S | re.I) or [None, ''])[1])).strip()
    heads = [(int(l), html.unescape(re.sub(r'<[^>]+>|\s+', ' ', h)).strip())
             for l, h in re.findall(r'<h([1-3])[^>]*>(.*?)</h\1>', t, re.S | re.I)]
    landmarks = {tag: len(re.findall(rf'<{tag}\b', t, re.I)) for tag in ('header', 'nav', 'main', 'section', 'article', 'aside', 'footer', 'form')}
    nav_links = []
    for nav in re.findall(r'<nav\b.*?</nav>', t, re.S | re.I)[:2]:
        nav_links += [(h, html.unescape(re.sub(r'<[^>]+>|\s+', ' ', x)).strip()) for h, x in re.findall(r'<a[^>]+href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', nav, re.S | re.I)]
    sections = [(tag, cls) for tag, cls in re.findall(r'<(section|article|header|footer|div)\b[^>]*\bclass=["\']([^"\']+)["\']', t, re.I)
                if tag.lower() != 'div' or re.search(r'\b(section|hero|banner|feature|cta|card|grid|wrapper|container|intro|pricing|team|testimonial)', cls, re.I)]
    for cls in re.findall(r'\bclass=["\']([^"\']+)["\']', t):
        class_freq.update(cls.split())
    imgs = re.findall(r'<img\b[^>]*>', t, re.I)
    no_alt = [i for i in imgs if not re.search(r'\balt=', i, re.I)]
    text_only = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style)\b.*?</\1>', ' ', t, flags=re.S | re.I)))
    report['pages'].append({
        'file': rel, 'title': title, 'outline': heads[:40], 'landmarks': {k: v for k, v in landmarks.items() if v},
        'nav': nav_links[:15], 'sections': collections.Counter(f'{a}.{b.split()[0]}' for a, b in sections).most_common(15),
        'images': len(imgs), 'images_missing_alt': len(no_alt), 'words': len(text_only.split()),
        'lorem': bool(re.search(r'lorem ipsum|dolor sit amet', text_only, re.I)),
    })
    for s in re.findall(r'<script\b[^>]*\bsrc=["\']([^"\']+)', t, re.I):
        if s.startswith(('http', '//')):
            report['risks'].append(f'{rel}: external script {s}')
    for key, name in TRACKERS.items():
        if key in t:
            report['risks'].append(f'{rel}: tracker — {name} ("{key}"). Remove; the privacy policy says no third-party analytics.')
    for href in re.findall(r'<link\b[^>]+href=["\']((?:https?:)?//[^"\']+)', t, re.I):
        report['risks'].append(f'{rel}: remote asset {href}')
    if report['pages'][-1]['lorem']:
        report['risks'].append(f'{rel}: contains lorem ipsum placeholder copy — never carry template copy over')
    if no_alt:
        report['risks'].append(f'{rel}: {len(no_alt)} <img> without alt')
report['components'] = class_freq.most_common(60)

# ---------- CSS tokens ----------
css = '\n'.join(v for k, v in files.items() if k.lower().endswith('.css'))
css += '\n'.join(s for v in files.values() for s in re.findall(r'<style[^>]*>(.*?)</style>', v, re.S | re.I))
css_nc = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
tok = report['tokens']
tok['custom_properties'] = sorted(set(re.findall(r'(--[\w-]+)\s*:\s*([^;}{]+)', css_nc)))[:120]
colors = re.findall(r'#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|hsla?\([^)]*\)', css_nc)
tok['colors'] = collections.Counter(c.lower().replace(' ', '') for c in colors).most_common(30)
tok['font_families'] = collections.Counter(re.sub(r'\s+', ' ', f.strip().strip(';')) for f in re.findall(r'font-family\s*:\s*([^;}]+)', css_nc)).most_common(12)
tok['font_sizes'] = collections.Counter(re.findall(r'font-size\s*:\s*([^;}]+)', css_nc)).most_common(20)
tok['font_weights'] = collections.Counter(re.findall(r'font-weight\s*:\s*([^;}]+)', css_nc)).most_common(10)
tok['line_heights'] = collections.Counter(re.findall(r'line-height\s*:\s*([^;}]+)', css_nc)).most_common(10)
tok['radii'] = collections.Counter(re.findall(r'border-radius\s*:\s*([^;}]+)', css_nc)).most_common(12)
tok['shadows'] = collections.Counter(re.findall(r'box-shadow\s*:\s*([^;}]+)', css_nc)).most_common(8)
tok['max_widths'] = collections.Counter(re.findall(r'(?<![(\w-])max-width\s*:\s*([^;}{)]+)', css_nc)).most_common(10)   # not inside @media (...)
tok['breakpoints'] = collections.Counter(re.findall(r'@media[^{]*?\(\s*(?:min|max)-width\s*:\s*([\d.]+(?:px|em|rem))', css_nc)).most_common(12)
tok['font_face'] = sorted(set(re.findall(r'@font-face\s*{[^}]*font-family\s*:\s*([^;]+)', css_nc)))
tok['imports'] = sorted(set(re.findall(r'@import\s+(?:url\()?["\']?([^"\')\s;]+)', css_nc)))
for i in tok['imports']:
    if i.startswith(('http', '//')):
        report['risks'].append(f'CSS @import of remote resource {i}')
tok['css_bytes'] = len(css)

# ---------- assets ----------
def dims(rel):
    try:
        from PIL import Image
        with Image.open(os.path.join(root, rel)) as im:
            return f'{im.width}x{im.height}'
    except Exception:
        return ''
report['assets'] = {
    'images': [(r, s, dims(r)) for r, s, k in sorted(assets) if k == 'image'][:80],
    'fonts': [(r, s) for r, s, k in sorted(assets) if k == 'font'],
    'scripts': [(r, s) for r, s, k in sorted(assets) if k == 'script'],
    'total_bytes': sum(s for _, s, _ in assets),
}

# ---------- XML / SVG ----------
for rel, text in sorted(files.items()):
    low = rel.lower()
    if low.endswith('.svg'):
        report['xml'].append({'file': rel, 'kind': 'svg',
                              'colors': collections.Counter(re.findall(r'(?:fill|stroke|stop-color)\s*[:=]\s*["\']?(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\))', text)).most_common(15),
                              'fonts': sorted(set(re.findall(r'font-family\s*[:=]\s*["\']?([^;"\']+)', text))),
                              'viewBox': (re.search(r'viewBox=["\']([^"\']+)', text) or [None, ''])[1]})
    elif low.endswith('.xml'):
        try:
            tree = ET.fromstring(text.encode('utf-8'))
        except ET.ParseError as e:
            report['xml'].append({'file': rel, 'kind': 'invalid', 'error': str(e)})
            continue
        strip = lambda t: t.split('}', 1)[-1]
        if strip(tree.tag) == 'urlset':
            urls = [(strip(u.tag), {strip(c.tag): (c.text or '').strip() for c in u}) for u in tree]
            report['xml'].append({'file': rel, 'kind': 'sitemap', 'urls': [d.get('loc') for _, d in urls],
                                  'paths': sorted({urllib.parse.urlparse(d.get('loc', '')).path for _, d in urls})})
        else:
            counts, samples = collections.Counter(), {}
            def walk(el, path, depth):
                p = f'{path}/{strip(el.tag)}'
                counts[p] += 1
                val = (el.text or '').strip()
                if p not in samples and (val or el.attrib):
                    samples[p] = (val[:60], {strip(k): v[:40] for k, v in list(el.attrib.items())[:4]})
                if depth < 8:
                    for c in el:
                        walk(c, p, depth + 1)
            walk(tree, '', 0)
            report['xml'].append({'file': rel, 'kind': 'structure', 'root': strip(tree.tag),
                                  'paths': [(p, n, samples.get(p)) for p, n in counts.items()][:150]})

report['risks'] = sorted(set(report['risks']))

# ---------- output ----------
if AS_JSON:
    out = json.dumps(report, indent=2, default=str)
else:
    L = [f'# Template inventory: {SRC}', '']
    L += ['## Licence', *(f'- `{l["file"]}`: {"; ".join(l["terms"])}' for l in report['license']), ''] if report['license'] else []
    L += [f'## Pages ({len(report["pages"])})']
    for p in report['pages']:
        L.append(f'### `{p["file"]}` — "{p["title"]}" ({p["words"]} words, {p["images"]} images{", LOREM IPSUM" if p["lorem"] else ""})')
        L.append('- regions: ' + (', '.join(f'{k}×{v}' for k, v in p['landmarks'].items()) or '-'))
        if p['nav']:
            L.append('- nav: ' + ' · '.join(f'{t or "(icon)"} → {h}' for h, t in p['nav']))
        if p['sections']:
            L.append('- section patterns: ' + ', '.join(f'{s}×{n}' for s, n in p['sections']))
        for lvl, h in p['outline'][:20]:
            L.append('  ' * lvl + f'- h{lvl} {h}')
    L += ['', '## Components (class frequency, top 60)', ', '.join(f'`{c}`×{n}' for c, n in report['components']), '']
    t = report['tokens']
    L += ['## Design tokens', f'- CSS size: {t["css_bytes"]:,} bytes']
    if t['custom_properties']:
        L.append('- custom properties: ' + ', '.join(f'`{k}: {v.strip()}`' for k, v in t['custom_properties'][:60]))
    for key in ('colors', 'font_families', 'font_sizes', 'font_weights', 'line_heights', 'radii', 'shadows', 'max_widths', 'breakpoints'):
        if t[key]:
            L.append(f'- {key.replace("_", " ")}: ' + ', '.join(f'`{v.strip()}`×{n}' for v, n in t[key]))
    for key in ('font_face', 'imports'):
        if t[key]:
            L.append(f'- {key.replace("_", " ")}: ' + ', '.join(f'`{v.strip()}`' for v in t[key]))
    a = report['assets']
    L += ['', f'## Assets ({a["total_bytes"]:,} bytes)']
    L += [f'- image `{r}` {d} {s:,}B' for r, s, d in a['images']]
    L += [f'- font `{r}` {s:,}B' for r, s in a['fonts']]
    L += [f'- script `{r}` {s:,}B' for r, s in a['scripts']]
    for x in report['xml']:
        L += ['', f'## XML `{x["file"]}` ({x["kind"]})']
        if x['kind'] == 'sitemap':
            L += [f'- {u}' for u in x['urls']]
        elif x['kind'] == 'structure':
            L += [f'- `{p}` ×{n}' + (f' — "{s[0]}" {s[1] or ""}' if s else '') for p, n, s in x['paths']]
        elif x['kind'] == 'svg':
            L += [f'- viewBox {x["viewBox"]}; colours ' + ', '.join(f'`{c}`×{n}' for c, n in x['colors']) + '; fonts ' + ', '.join(x['fonts'])]
        else:
            L.append(f'- {x.get("error")}')
    L += ['', f'## Risks ({len(report["risks"])})', *(f'- {r}' for r in report['risks'])]
    if files.get('_errors'):
        L += ['', '## Fetch errors', files['_errors']]
    out = '\n'.join(L) + '\n'

if OUT:
    open(OUT, 'w').write(out)
    print(f'wrote {OUT} ({len(out):,} chars)')
else:
    print(out)
