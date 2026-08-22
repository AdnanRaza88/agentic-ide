# Web (`apps/web`)

Next.js + TypeScript + Tailwind frontend for Agentic IDE.

## Run locally

```bash
cd apps/web
cp .env.example .env.local   # optional
npm install
npm run dev
```

Open http://localhost:3000

The home page calls `GET {NEXT_PUBLIC_API_URL}/health` so you can verify frontend ↔ backend connectivity.

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Dev server (port 3000) |
| `npm run build` | Production build |
| `npm run start` | Serve production build |
| `npm run lint` | ESLint |
| `npm run typecheck` | TypeScript check |

## Notes

- No agent UI, Monaco, or shadcn components yet — foundation only.
- Ensure the API is running on port 8000 (or update `NEXT_PUBLIC_API_URL`).
