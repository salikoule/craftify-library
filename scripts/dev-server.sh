#!/usr/bin/env bash
# Local Anvil app server for craftify-library (after git clone from Anvil).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if ! command -v anvil-app-server >/dev/null 2>&1; then
  echo "Install: pip install anvil-app-server"
  exit 1
fi
exec anvil-app-server --app "$ROOT"
