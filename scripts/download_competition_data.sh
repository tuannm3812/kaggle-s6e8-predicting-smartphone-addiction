#!/usr/bin/env bash
# Download playground-series-s6e8 competition files into data/.
# Requires Kaggle CLI auth (kaggle auth login, or KAGGLE_API_TOKEN / ~/.kaggle/access_token).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$REPO_ROOT/data"
mkdir -p "$OUT"

if command -v kaggle >/dev/null 2>&1; then
  KAGGLE=kaggle
elif [ -x "$HOME/.local/bin/kaggle" ]; then
  KAGGLE="$HOME/.local/bin/kaggle"
else
  echo "kaggle CLI not found" >&2
  exit 1
fi

"$KAGGLE" competitions download -c playground-series-s6e8 -p "$OUT"
unzip -o "$OUT/playground-series-s6e8.zip" -d "$OUT"
rm -f "$OUT/playground-series-s6e8.zip" "$OUT/SMOKE_DATA_ONLY.txt"
ls -la "$OUT"
