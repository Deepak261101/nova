"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useEffect } from "react";

import { AIOrb } from "@/components/AIOrb";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useAuthStore } from "@/lib/store";

const FEATURES = [
  ["🎙️", "Wake word", "Just say “Hey Nova” to start talking, hands-free."],
  ["⚡", "Streaming voice chat", "Real-time speech-to-text and natural replies."],
  ["🧠", "Long-term memory", "Nova remembers your preferences across sessions."],
  ["🔒", "Secure auth", "Email, Google & GitHub login with JWT sessions."],
  ["📄", "RAG & knowledge", "Upload docs and ask grounded questions (Phase 2)."],
  ["🤖", "Multi-agent", "Research, browser, file & coding agents (Phase 3+)."],
];

export default function LandingPage() {
  const router = useRouter();
  const tokens = useAuthStore((s) => s.tokens);
  const hydrated = useAuthStore((s) => s.hydrated);

  useEffect(() => {
    if (hydrated && tokens) router.replace("/dashboard");
  }, [hydrated, tokens, router]);

  return (
    <main className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-8">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xl font-semibold">
          <span className="text-2xl">✦</span> Nova
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle />
          <Link href="/login" className="btn-ghost">
            Sign in
          </Link>
          <Link href="/register" className="btn-primary">
            Get started
          </Link>
        </div>
      </header>

      <section className="grid flex-1 items-center gap-10 py-16 md:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-5xl font-bold leading-tight tracking-tight">
            Your production-grade{" "}
            <span className="bg-gradient-to-r from-nova-500 to-fuchsia-500 bg-clip-text text-transparent">
              AI voice assistant
            </span>
          </h1>
          <p className="mt-4 max-w-md text-lg text-slate-500">
            Nova listens, thinks and speaks. Wake word, streaming conversations,
            memory, and a growing set of agents — all in one beautiful app.
          </p>
          <div className="mt-8 flex gap-3">
            <Link href="/register" className="btn-primary">
              Start free
            </Link>
            <Link href="/login" className="btn-ghost">
              I have an account
            </Link>
          </div>
        </motion.div>

        <div className="flex items-center justify-center">
          <div className="animate-float">
            <AIOrb status="idle" />
          </div>
        </div>
      </section>

      <section className="grid gap-4 pb-12 sm:grid-cols-2 lg:grid-cols-3">
        {FEATURES.map(([icon, title, desc]) => (
          <div key={title} className="glass rounded-2xl p-5">
            <div className="text-2xl">{icon}</div>
            <h3 className="mt-2 font-semibold">{title}</h3>
            <p className="mt-1 text-sm text-slate-500">{desc}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
