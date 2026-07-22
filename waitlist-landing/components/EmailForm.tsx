"use client";

import { useState } from "react";

type Status = "idle" | "loading" | "success" | "error";

export default function EmailForm() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (status === "loading") return;
    setStatus("loading");
    setMessage("");

    try {
      const res = await fetch("/api/subscribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });
      const json = await res.json();
      if (!res.ok) {
        setStatus("error");
        setMessage(json.error || "Something went wrong — please try again.");
        return;
      }
      setStatus("success");
      setMessage(
        "You're on the founding list. We'll email you before launch with your 30% off."
      );
      setEmail("");
    } catch {
      setStatus("error");
      setMessage("Something went wrong — please try again.");
    }
  }

  if (status === "success") {
    return (
      <p
        role="status"
        className="border border-accent bg-accent/10 px-5 py-4 text-sm leading-relaxed text-accent-deep"
      >
        {message}
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <div className="flex flex-col gap-3 sm:flex-row">
        <label htmlFor="email" className="sr-only">
          Email address
        </label>
        <input
          id="email"
          type="email"
          required
          autoComplete="email"
          inputMode="email"
          placeholder="Your email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="h-12 flex-1 border border-ink/20 bg-white px-4 text-base text-ink placeholder:text-stone-mid focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
        />
        <button
          type="submit"
          disabled={status === "loading"}
          className="h-12 whitespace-nowrap bg-accent px-6 text-sm font-semibold uppercase tracking-widest2 text-ink transition-colors hover:bg-accent-dark disabled:opacity-60"
        >
          {status === "loading" ? "Joining…" : "Join the founding list"}
        </button>
      </div>
      {status === "error" && (
        <p role="alert" className="mt-3 text-sm text-red-700">
          {message}
        </p>
      )}
      <p className="mt-3 text-xs leading-relaxed text-stone-mid">
        No spam. Launch news and your founding-member offer only. Unsubscribe
        any time.
      </p>
    </form>
  );
}
