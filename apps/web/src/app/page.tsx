"use client";

import { useCallback, useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type HealthResponse = {
  status: string;
  service?: string;
  version?: string;
  timestamp?: string;
};

type ConnectionState = "idle" | "loading" | "ok" | "error";

export default function HomePage() {
  const [state, setState] = useState<ConnectionState>("idle");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = useCallback(async () => {
    setState("loading");
    setError(null);
    try {
      const res = await fetch(`${API_URL}/health`, {
        method: "GET",
        headers: { Accept: "application/json" },
        cache: "no-store",
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = (await res.json()) as HealthResponse;
      setHealth(data);
      setState("ok");
    } catch (e) {
      setHealth(null);
      setError(e instanceof Error ? e.message : "Unknown error");
      setState("error");
    }
  }, []);

  useEffect(() => {
    void checkHealth();
  }, [checkHealth]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-6">
      <div className="w-full max-w-lg rounded-2xl border border-zinc-800 bg-[var(--card)] p-8 shadow-xl">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold tracking-tight">Agentic IDE</h1>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Foundation infrastructure — frontend ↔ backend connectivity
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between rounded-lg bg-zinc-900/60 px-4 py-3">
            <span className="text-sm text-[var(--muted)]">API URL</span>
            <code className="text-sm text-zinc-200">{API_URL}</code>
          </div>

          <div className="flex items-center justify-between rounded-lg bg-zinc-900/60 px-4 py-3">
            <span className="text-sm text-[var(--muted)]">Connection</span>
            <StatusBadge state={state} />
          </div>

          {state === "ok" && health && (
            <div className="rounded-lg border border-emerald-900/50 bg-emerald-950/30 px-4 py-3 text-sm">
              <div className="grid grid-cols-2 gap-2">
                <span className="text-[var(--muted)]">Status</span>
                <span className="text-emerald-400">{health.status}</span>
                <span className="text-[var(--muted)]">Service</span>
                <span>{health.service ?? "—"}</span>
                <span className="text-[var(--muted)]">Version</span>
                <span>{health.version ?? "—"}</span>
                <span className="text-[var(--muted)]">Timestamp</span>
                <span className="truncate text-xs">{health.timestamp ?? "—"}</span>
              </div>
            </div>
          )}

          {state === "error" && (
            <div className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300">
              <p className="font-medium">Cannot reach API</p>
              <p className="mt-1 text-xs opacity-80">{error}</p>
              <p className="mt-2 text-xs text-[var(--muted)]">
                Start the backend: <code className="text-zinc-300">./scripts/dev-api.sh</code>
              </p>
            </div>
          )}

          <button
            type="button"
            onClick={() => void checkHealth()}
            disabled={state === "loading"}
            className="w-full rounded-lg bg-[var(--accent)] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-600 disabled:opacity-50"
          >
            {state === "loading" ? "Checking…" : "Recheck health"}
          </button>
        </div>

        <p className="mt-6 text-center text-xs text-[var(--muted)]">
          Agent runtime, MCP, plugins & model routing are not implemented yet.
        </p>
      </div>
    </main>
  );
}

function StatusBadge({ state }: { state: ConnectionState }) {
  const map = {
    idle: { label: "Idle", className: "bg-zinc-700 text-zinc-200" },
    loading: { label: "Checking…", className: "bg-amber-900/60 text-amber-200" },
    ok: { label: "Connected", className: "bg-emerald-900/60 text-emerald-300" },
    error: { label: "Disconnected", className: "bg-red-900/60 text-red-300" },
  } as const;
  const { label, className } = map[state];
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`}>{label}</span>
  );
}
