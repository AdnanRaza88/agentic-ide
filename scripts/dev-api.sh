#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/apps/api"

if [[ ! -d .venv ]]; then
  echo "Creating virtualenv…"
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

pip install -q -e ".[dev]"

echo "Starting API on http://0.0.0.0:8000 …"
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
