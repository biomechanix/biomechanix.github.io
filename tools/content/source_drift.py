#!/usr/bin/env python3
"""Content audit helper: find claims whose SOURCE may have changed, and check
external links the site depends on.

1. For every claims.yml entry whose source names a sibling repo path
   (e.g. "mm-selfassess/README.md"), list commits to that path since the
   claim's `verified` date. A commit means: re-read the source and re-verify
   the claim, then bump `verified`.
2. Fetch external links from the pages (biomechanix.ai, Google Play listings,
   support URL) and report HTTP status. A Play listing that 404s means that
   app isn't published under that package id.
3. Check each app's in-app privacy-policy URL (brand configs) points at the
   site's /privacy.

Usage: python3 tools/content/source_drift.py [--no-net]
Repos are expected as siblings of this repo (~/code/projects/<repo>).
"""
import datetime, glob, os, re, subprocess, sys, urllib.request
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PROJECTS = os.path.dirname(ROOT)
ledger = yaml.safe_load(open(os.path.join(ROOT, 'tools', 'content', 'claims.yml')))
config = yaml.safe_load(open(os.path.join(ROOT, '_config.yml')))
net = '--no-net' not in sys.argv
problems = 0

print('== 1. Sources changed since last verification')
for c in ledger['claims']:
    for repo, path in re.findall(r'\b(mm-[a-z]+)/([\w./-]+\.\w+)', c.get('source', '')):
        rdir = os.path.join(PROJECTS, repo)
        if not os.path.isdir(rdir):
            print(f'  ?  {c["id"]}: repo {repo} not checked out at {rdir}')
            continue
        fpath = os.path.join(rdir, path)
        if not os.path.exists(fpath):
            print(f'  !! {c["id"]}: source file gone: {repo}/{path}')
            problems += 1
            continue
        r = subprocess.run(['git', '-C', rdir, 'log', '--oneline', f'--since={c["verified"]}', '--', path],
                           capture_output=True, text=True)
        if r.returncode != 0:
            # Not a git repo (e.g. mm-business): fall back to the file's mtime.
            # An empty `git log` from a failed command is NOT "unchanged".
            mtime = datetime.date.fromtimestamp(os.path.getmtime(fpath))
            if str(mtime) > str(c['verified']):
                print(f'  !! {c["id"]}: {repo}/{path} modified {mtime} (after {c["verified"]}; no git history) — re-verify')
                problems += 1
            else:
                print(f'  ok {c["id"]}: {repo}/{path} not modified since {c["verified"]} (mtime; no git history)')
            continue
        log = r.stdout.strip()
        if log:
            print(f'  !! {c["id"]}: {repo}/{path} changed since {c["verified"]} — re-verify:')
            for line in log.splitlines()[:5]:
                print('       ' + line)
            problems += 1
        else:
            print(f'  ok {c["id"]}: {repo}/{path} unchanged since {c["verified"]}')

print('\n== 2. External links')
if net:
    urls = set()
    for f in glob.glob(os.path.join(ROOT, '*.html')) + [os.path.join(ROOT, '_layouts', 'default.html')]:
        # skip <link rel="preconnect"> hints — bare font hosts aren't pages
        urls.update(u for u in re.findall(r'<a [^>]*href="(https?://[^"]+)"', open(f).read()))
    for app, pkg in (config.get('play') or {}).items():
        urls.add(f'https://play.google.com/store/apps/details?id={pkg}')
    urls.add(config.get('support_url', ''))
    for u in sorted(filter(None, urls)):
        if '{{' in u:
            continue
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}, method='GET')
            code = urllib.request.urlopen(req, timeout=20).status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:
            code = f'ERR {type(e).__name__}'
        ok = code == 200
        problems += not ok
        note = (' — NOT publicly listed (unpublished, or closed/internal testing only); the site\'s Play button 404s'
                if 'play.google.com' in u and code == 404 else '')
        print(f'  {"ok" if ok else "!!"} {code} {u}{note}')
else:
    print('  skipped (--no-net)')

print('\n== 3. In-app privacy policy URLs')
want = config.get('url', 'https://biomechanix.github.io').rstrip('/') + '/privacy'
for repo in ('mm-fitness', 'mm-physio', 'mm-selfassess'):
    for f in glob.glob(os.path.join(PROJECTS, repo, 'android', 'app', 'src', '**', '*BrandConfig.kt'), recursive=True):
        if 'FitPro' in f:      # separate white-label brand (disabled flavor), not a Biomechanix app on this site
            continue
        for url in re.findall(r'privacyPolicyUrl\s*=\s*"([^"]+)"', open(f).read()):
            ok = url.rstrip('/') == want
            problems += not ok
            print(f'  {"ok" if ok else "!!"} {os.path.relpath(f, PROJECTS)}: {url}')

print(f'\n{problems} item(s) need attention')
sys.exit(1 if problems else 0)
