# Scripts

| Script | Purpose |
|--------|---------|
| `dev-api.sh` | Create venv (if needed), install API deps, run uvicorn with reload |
| `dev-web.sh` | Install npm deps (if needed), run Next.js dev server |
| `test.sh` | Run API pytest + web TypeScript check |
| `lint.sh` | Run ruff (API) + ESLint (web) |

Make executable once:

```bash
chmod +x scripts/*.sh
```
