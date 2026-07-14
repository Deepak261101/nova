"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { GlassCard } from "@/components/GlassCard";
import { api, ApiError } from "@/lib/api";
import { API_URL } from "@/lib/config";
import { useAuthStore } from "@/lib/store";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const setSession = useAuthStore((s) => s.setSession);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const isRegister = mode === "register";

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const res = isRegister
        ? await api.register(email, password, displayName)
        : await api.login(email, password);
      setSession(res.user, res.tokens);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  };

  const oauth = (provider: "google" | "github") => {
    window.location.href = `${API_URL}/auth/oauth/${provider}/login`;
  };

  return (
    <GlassCard strong className="w-full max-w-md p-8">
      <div className="mb-6 text-center">
        <div className="mb-2 text-4xl">✦</div>
        <h1 className="text-2xl font-semibold tracking-tight">
          {isRegister ? "Create your Nova account" : "Welcome back to Nova"}
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          {isRegister ? "Your personal AI voice assistant" : "Sign in to continue"}
        </p>
      </div>

      <div className="mb-4 grid grid-cols-2 gap-2">
        <button type="button" className="btn-ghost" onClick={() => oauth("google")}>
          Google
        </button>
        <button type="button" className="btn-ghost" onClick={() => oauth("github")}>
          GitHub
        </button>
      </div>

      <div className="my-4 flex items-center gap-3 text-xs text-slate-400">
        <div className="h-px flex-1 bg-white/30" />
        or
        <div className="h-px flex-1 bg-white/30" />
      </div>

      <form className="space-y-3" onSubmit={submit}>
        {isRegister && (
          <input
            className="input"
            placeholder="Display name"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            aria-label="Display name"
          />
        )}
        <input
          className="input"
          type="email"
          required
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          aria-label="Email"
        />
        <input
          className="input"
          type="password"
          required
          minLength={8}
          placeholder="Password (min 8 chars)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          aria-label="Password"
        />
        {error && (
          <p role="alert" className="text-sm text-rose-500">
            {error}
          </p>
        )}
        <button type="submit" className="btn-primary w-full" disabled={busy}>
          {busy ? "Please wait…" : isRegister ? "Create account" : "Sign in"}
        </button>
      </form>

      <p className="mt-4 text-center text-sm text-slate-500">
        {isRegister ? (
          <>
            Already have an account?{" "}
            <Link href="/login" className="text-nova-500 hover:underline">
              Sign in
            </Link>
          </>
        ) : (
          <>
            New to Nova?{" "}
            <Link href="/register" className="text-nova-500 hover:underline">
              Create an account
            </Link>
          </>
        )}
      </p>
    </GlassCard>
  );
}
