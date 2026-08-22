#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/apps/web"

if [[ ! -d node_modules ]]; then
  echo "Installing npm dependencies…"
  npm install
fi

if [[ ! -f .env.local ]] && [[ -f .env.example ]]; then
  cp .env.example .env.local
fi

echo "Starting Next.js on http://localhost:3000 …"
exec npm run dev
