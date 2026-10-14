#!/usr/bin/env bash
# Odoo extractor + validator loop (extractor-quality-loop.md). Exit 0 when the score >= 95%.
# Usage: pipelines/odoo/run.sh [source-addons-dir] [knowledge-base-dir]
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
SOURCE="${1:-$ROOT/sources/odoo/addons}"
KB="${2:-$ROOT/analysis/odoo/knowledge-base}"
cd "$ROOT"
echo "=== Running extractor ==="
python3 -I "$HERE/extractor.py" --source "$SOURCE" --out "$KB" | sed -n '1,20p'
echo
echo "=== Running validator ==="
python3 -I "$HERE/validator.py" --source "$SOURCE" --kb "$KB" --out "$KB/extracted"
