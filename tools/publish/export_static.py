#!/usr/bin/env python3
"""Export the live GitHub Pages site (exact Jekyll output) as static files.

Crawls https://biomechanix.github.io from "/", following internal links and
assets (including url() references in CSS), with cache-busting so a fresh
Pages build isn't masked by the CDN. Used by deploy_firebase.sh to publish
the same site at biomechanix.ai. The CI workflow builds with GitHub's own
Jekyll action instead, so this is only for local deploys.

Only what is LIVE on github.io is exported: merge and let Pages build first
(tools/publish/wait_deploy.sh).

Usage: python3 tools/publish/export_static.py [--out deploy/firebase/public] [--base https://biomechanix.github.io]
"""
import os, re, shutil, sys, time, urllib.request

argv = sys.argv[1:]
opt = lambda k, d: argv[argv.index(k) + 1] if k in argv else d
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
out = os.path.abspath(opt('--out', os.path.join(ROOT, 'deploy', 'firebase', 'public')))
base = opt('--base', 'https://biomechanix.github.io').rstrip('/')
bust = str(int(time.time()))

shutil.rmtree(out, ignore_errors=True)
seen, queue, pages, errors = set(), ['/'], 0, []
while queue:
    u = queue.pop(0).split('#')[0].split('?')[0] or '/'
    if u in seen:
        continue
    seen.add(u)
    req = urllib.request.Request(f'{base}{u}?cb={bust}', headers={'User-Agent': 'biomechanix-export', 'Cache-Control': 'no-cache'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            ctype, body = r.headers.get('Content-Type', ''), r.read()
    except Exception as e:
        errors.append(f'{u}: {e}')
        continue
    if 'text/html' in ctype:
        path = os.path.join(out, 'index.html') if u == '/' else os.path.join(out, u.strip('/'), 'index.html')
        queue += [x for x in re.findall(r'(?:href|src)="(/[^"]*)"', body.decode('utf-8', 'replace')) if not x.startswith('//')]
        pages += 1
    else:
        path = os.path.join(out, u.strip('/'))
        if u.endswith('.css'):
            queue += re.findall(r'url\((/[^)]+)\)', body.decode('utf-8', 'replace'))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(body)

for e in errors:
    print('ERROR', e)
print(f'exported {len(seen) - len(errors)} paths ({pages} pages) from {base} -> {os.path.relpath(out, ROOT)}')
sys.exit(1 if errors or pages == 0 else 0)
