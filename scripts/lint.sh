#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Ruff (API) ==="
cd "$ROOT/apps/api"
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -e ".[dev]"
ruff check app tests
ruff format --check app tests

echo ""
echo "=== ESLint (Web) ==="
cd "$ROOT/apps/web"
if [[ ! -d node_modules ]]; then
  npm install
fi
npm run lint

echo ""
echo "Lint passed."
