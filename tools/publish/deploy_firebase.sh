#!/usr/bin/env bash
# Deploy the site to biomechanix.ai (Firebase Hosting, project/site "biomechanixdev").
#
#   tools/publish/deploy_firebase.sh preview   # export live github.io -> preview channel (7 days), prints URL
#   tools/publish/deploy_firebase.sh live      # same export -> biomechanix.ai (asks for confirmation)
#   tools/publish/deploy_firebase.sh rollback  # restore the saved React site backup channel to live
#
# Normally the GitHub Action (.github/workflows/deploy-biomechanix-ai.yml) deploys on
# merge. Use this when the Action isn't set up, or to re-deploy by hand.
# Exports what is LIVE on github.io, so merge and wait for Pages first
# (tools/publish/wait_deploy.sh). Requires `firebase login` with access to biomechanixdev.
set -euo pipefail
mode=${1:-preview}
root=$(cd "$(dirname "$0")/../.." && pwd)
cd "$root"

case "$mode" in
  preview|live)
    python3 tools/publish/export_static.py --out deploy/firebase/public
    python3 tools/content/content_lint.py >/dev/null || { echo "content_lint failed; not deploying" >&2; exit 1; }
    cd deploy/firebase
    if [ "$mode" = preview ]; then
      firebase hosting:channel:deploy preview --expires 7d
    else
      read -r -p "Deploy to biomechanix.ai LIVE? Type 'live' to confirm: " answer
      [ "$answer" = live ] || { echo "aborted"; exit 1; }
      firebase deploy --only hosting
    fi
    ;;
  rollback)
    cd deploy/firebase
    firebase hosting:clone biomechanixdev:react-site-backup biomechanixdev:live
    ;;
  *) echo "usage: $0 preview|live|rollback" >&2; exit 2 ;;
esac
