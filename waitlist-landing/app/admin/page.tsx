"use client";

import { useState } from "react";

interface Signup {
  email: string;
  joinedAt: string;
}

export default function AdminPage() {
  const [password, setPassword] = useState("");
  const [signups, setSignups] = useState<Signup[] | null>(null);
  const [source, setSource] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/admin/signups", {
        headers: { "x-admin-password": password },
        cache: "no-store",
      });
      if (res.status === 401) {
        setError(
          "Wrong password (or ADMIN_PASSWORD isn't set in the environment)."
        );
        return;
      }
      if (!res.ok) {
        setError("Failed to load signups.");
        return;
      }
      const json = await res.json();
      setSignups(json.signups);
      setSource(json.source);
    } catch {
      setError("Failed to load signups.");
    } finally {
      setLoading(false);
    }
  }

  async function downloadCsv() {
    const res = await fetch("/api/admin/signups?format=csv", {
      headers: { "x-admin-password": password },
      cache: "no-store",
    });
    if (!res.ok) return;
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "signups.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  if (signups === null) {
    return (
      <main className="container-narrow flex min-h-svh flex-col justify-center py-16">
        <h1 className="font-display text-2xl">Admin</h1>
        <form onSubmit={handleLogin} className="mt-8 flex flex-col gap-3">
          <label htmlFor="password" className="sr-only">
            Admin password
          </label>
          <input
            id="password"
            type="password"
            autoFocus
            placeholder="Admin password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="h-12 border border-ink/20 bg-white px-4 text-base focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
          />
          <button
            type="submit"
            disabled={loading || !password}
            className="h-12 bg-accent px-6 text-sm font-semibold uppercase tracking-widest2 text-ink hover:bg-accent-dark disabled:opacity-60"
          >
            {loading ? "Checking…" : "View signups"}
          </button>
          {error && (
            <p role="alert" className="text-sm text-red-700">
              {error}
            </p>
          )}
        </form>
      </main>
    );
  }

  return (
    <main className="container-wide py-16">
      <div className="flex flex-wrap items-baseline justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl">Signups</h1>
          <p className="mt-1 text-sm text-stone-mid">
            {signups.length} shown · source: {source}
          </p>
        </div>
        <button
          onClick={downloadCsv}
          className="border border-accent px-5 py-3 text-[11px] font-semibold uppercase tracking-widest2 text-accent-deep hover:bg-accent hover:text-ink"
        >
          Export CSV
        </button>
      </div>

      <div className="mt-8 overflow-x-auto border border-ink/10">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-ink/10 bg-white">
            <tr>
              <th className="px-4 py-3 font-medium">#</th>
              <th className="px-4 py-3 font-medium">Email</th>
              <th className="px-4 py-3 font-medium">Joined</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-ink/10">
            {signups.length === 0 && (
              <tr>
                <td colSpan={3} className="px-4 py-8 text-center text-stone-mid">
                  No signups yet.
                </td>
              </tr>
            )}
            {signups.map((s, i) => (
              <tr key={`${s.email}-${i}`}>
                <td className="px-4 py-3 text-stone-mid">{i + 1}</td>
                <td className="px-4 py-3">{s.email}</td>
                <td className="px-4 py-3 text-stone-mid">
                  {s.joinedAt ? new Date(s.joinedAt).toLocaleString() : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
