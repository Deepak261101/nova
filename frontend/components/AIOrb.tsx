"use client";

import { motion } from "framer-motion";

import type { VoiceStatus } from "@/lib/useVoice";

const STATUS_COLOR: Record<VoiceStatus, string> = {
  idle: "from-nova-400 to-indigo-500",
  "wake-listening": "from-emerald-400 to-nova-500",
  listening: "from-nova-400 to-fuchsia-500",
  thinking: "from-amber-400 to-nova-500",
  speaking: "from-fuchsia-400 to-nova-500",
  unsupported: "from-slate-400 to-slate-600",
};

export function AIOrb({ status }: { status: VoiceStatus }) {
  const active = status === "listening" || status === "speaking";
  return (
    <div className="relative flex items-center justify-center" aria-hidden>
      <motion.div
        className={`absolute h-48 w-48 rounded-full bg-gradient-to-br ${STATUS_COLOR[status]} blur-2xl`}
        animate={{ opacity: active ? [0.5, 0.8, 0.5] : [0.3, 0.5, 0.3], scale: active ? [1, 1.15, 1] : [1, 1.05, 1] }}
        transition={{ duration: active ? 1.6 : 3.4, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className={`relative h-40 w-40 rounded-full bg-gradient-to-br ${STATUS_COLOR[status]} shadow-2xl`}
        animate={{ scale: active ? [1, 1.06, 1] : [1, 1.03, 1] }}
        transition={{ duration: active ? 1.2 : 3, repeat: Infinity, ease: "easeInOut" }}
      >
        <div className="absolute inset-3 rounded-full bg-white/20 backdrop-blur-md" />
        <div className="absolute inset-0 flex items-center justify-center text-4xl">✦</div>
      </motion.div>
    </div>
  );
}
