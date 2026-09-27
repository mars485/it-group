#!/bin/sh
set -eu
BASE=/DATA/AppData/it-group-preview
URL=https://github.com/mars485/it-group/releases/download/site-preview-latest/it-group-site.tar.gz
mkdir -p "$BASE"
TMP=$(mktemp -d "$BASE/.download.XXXXXX")
trap 'rm -rf "$TMP"' EXIT HUP INT TERM
echo "Downloading IT GROUP preview..."
curl -fL --retry 3 --connect-timeout 15 "$URL" -o "$TMP/site.tar.gz"
mkdir "$TMP/site"
tar -xzf "$TMP/site.tar.gz" -C "$TMP/site"
test -s "$TMP/site/index.html" || { echo "Invalid site archive: index.html missing"; exit 1; }
# Keep previous preview until the new download is fully validated.
if [ -d "$BASE/site" ]; then
  rm -rf "$BASE/site.previous"
  mv "$BASE/site" "$BASE/site.previous"
fi
mv "$TMP/site" "$BASE/site"
echo "Preview updated: $BASE/site"
echo "Previous version (if any): $BASE/site.previous"
