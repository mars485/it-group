#!/bin/sh
set -eu
# Preview only: run on ZimaOS after extracting GitHub artifact into /DATA/AppData/it-group-preview/site
SITE=/DATA/AppData/it-group-preview/site
[ -f "$SITE/index.html" ] || { echo "Missing $SITE/index.html. Extract GitHub Actions artifact there first."; exit 1; }
cd "$SITE"
# Bind to loopback only: reverse proxy can expose this later, after review.
exec python3 -m http.server 18001 --bind 127.0.0.1
