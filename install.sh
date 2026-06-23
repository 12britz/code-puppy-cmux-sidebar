#!/usr/bin/env bash
#
# Install the cmux_sidebar plugin into Code Puppy's user plugin tier.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${HOME}/.code_puppy/plugins"

mkdir -p "$DEST"
rm -rf "$DEST/cmux_sidebar"
cp -R "$SCRIPT_DIR/cmux_sidebar" "$DEST/"
rm -rf "$DEST/cmux_sidebar/__pycache__"

echo "Installed cmux_sidebar -> $DEST/cmux_sidebar"
echo "Restart Code Puppy inside a cmux pane to activate."
