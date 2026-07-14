"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

import { GlassCard } from "@/components/GlassCard";
import { ThemeToggle } from "@/components/ThemeToggle";
import { api } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import type { MemoryItem } from "@/lib/types";

export default function SettingsPage() {
  const router = useRouter();
  const { user, tokens, hydrated, setSession } = useAuthStore();

  const [displayName, setDisplayName] = useState("");
  const [saved, setSaved] = useState(false);
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [memKey, setMemKey] = useState("");
  const [memValue, setMemValue] = useState("");

  useEffect(() => {
    if (hydrated && !tokens) router.replace("/login");
  }, [hydrated, tokens, router]);

  useEffect(() => {
    if (user) setDisplayName(user.display_name);
  }, [user]);

  const loadMemory = useCallback(async () => {
    setMemories(await api.listMemory());
  }, []);

  useEffect(() => {
    if (user) void loadMemory();
  }, [user, loadMemory]);

  const saveProfile = async () => {
    const updated = await api.updateProfile({ display_name: displayName });
    if (tokens) setSession(updated, tokens);
    setSaved(true);
    setTimeout(() => setSaved(false), 1500);
  };

  const addMemory = async () => {
    if (!memKey.trim() || !memValue.trim()) return;
    await api.upsertMemory(memKey.trim(), memValue.trim());
    setMemKey("");
    setMemValue("");
    await loadMemory();
  };

  const removeMemory = async (key: string) => {
    await api.deleteMemory(key);
    await loadMemory();
  };

  if (!hydrated || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center text-slate-500">
        Loading…
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl space-y-6 p-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Settings</h1>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Link href="/dashboard" className="btn-ghost">
            ← Back
          </Link>
        </div>
      </header>

      <GlassCard className="space-y-4 p-6">
        <h2 className="text-lg font-semibold">Profile</h2>
        <div>
          <label className="mb-1 block text-sm text-slate-500" htmlFor="displayName">
            Display name
          </label>
          <input
            id="displayName"
            className="input"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
          />
        </div>
        <div className="text-sm text-slate-500">Email: {user.email}</div>
        <button type="button" className="btn-primary" onClick={saveProfile}>
          {saved ? "Saved ✓" : "Save profile"}
        </button>
      </GlassCard>

      <GlassCard className="space-y-4 p-6">
        <h2 className="text-lg font-semibold">Appearance</h2>
        <p className="text-sm text-slate-500">
          Toggle dark / light mode using the button in the header.
        </p>
      </GlassCard>

      <GlassCard className="space-y-4 p-6">
        <h2 className="text-lg font-semibold">Long-term memory</h2>
        <p className="text-sm text-slate-500">
          Facts Nova remembers about you and uses to personalize replies.
        </p>
        <div className="flex flex-col gap-2 sm:flex-row">
          <input
            className="input sm:flex-1"
            placeholder="Key (e.g. favorite_language)"
            value={memKey}
            onChange={(e) => setMemKey(e.target.value)}
            aria-label="Memory key"
          />
          <input
            className="input sm:flex-1"
            placeholder="Value (e.g. Python)"
            value={memValue}
            onChange={(e) => setMemValue(e.target.value)}
            aria-label="Memory value"
          />
          <button type="button" className="btn-primary" onClick={addMemory}>
            Add
          </button>
        </div>
        <ul className="divide-y divide-white/10">
          {memories.length === 0 && (
            <li className="py-2 text-sm text-slate-500">No memories yet.</li>
          )}
          {memories.map((m) => (
            <li key={m.id} className="flex items-center justify-between py-2 text-sm">
              <span>
                <span className="font-medium">{m.key}</span>: {m.value}
              </span>
              <button
                type="button"
                className="text-rose-500 hover:underline"
                onClick={() => removeMemory(m.key)}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      </GlassCard>
    </main>
  );
}
