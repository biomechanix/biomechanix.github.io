#!/usr/bin/env bash
# Wait for GitHub Pages to finish building the current main, then check the
# live site. A merge is not "deployed" until the Pages build for main's HEAD
# reports `built` — an older `built` status is a previous deploy.
#
# Usage: tools/publish/wait_deploy.sh [path "expected text"]...
#   e.g. tools/publish/wait_deploy.sh /company "Raghunandan S K" / 'id="platform"'
# Each path must return 200 and contain its expected text (cache-busted fetch).
# Exit 0 = built and all checks passed.
set -u
REPO=biomechanix/biomechanix.github.io
SITE=https://biomechanix.github.io

main=$(gh api "repos/$REPO/commits/main" --jq '.sha[0:7]') || exit 2
for i in $(seq 1 30); do
  st=$(gh api "repos/$REPO/pages/builds/latest" --jq '.status+" "+.commit[0:7]')
  case "$st" in
    "built $main") echo "pages: built $main"; break ;;
    errored*) echo "pages: BUILD ERRORED ($st) — check the Actions/Pages tab" >&2; exit 1 ;;
  esac
  [ "$i" = 30 ] && { echo "pages: timed out waiting (last: $st, main=$main)" >&2; exit 1; }
  sleep 10
done

fail=0
while [ $# -ge 2 ]; do
  path=$1 want=$2; shift 2
  code=$(curl -s -o /dev/null -w '%{http_code}' "$SITE$path")
  hits=$(curl -s "$SITE$path?nocache=$RANDOM$RANDOM" | grep -cF -- "$want")
  if [ "$code" = 200 ] && [ "$hits" -gt 0 ]; then
    echo "ok   $path ($code) contains: $want"
  else
    echo "FAIL $path ($code) hits=$hits for: $want" >&2; fail=1
  fi
done
echo "note: browsers may cache HTML up to 10 min (Pages max-age=600); CSS is cache-busted per build."
exit $fail
