"use client";

import { motion } from "framer-motion";

import type { VoiceStatus } from "@/lib/useVoice";

interface Props {
  status: VoiceStatus;
  onClick: () => void;
}

export function MicButton({ status, onClick }: Props) {
  const listening = status === "listening";
  return (
    <motion.button
      type="button"
      onClick={onClick}
      aria-label="Push to talk"
      aria-pressed={listening}
      whileTap={{ scale: 0.92 }}
      className="relative flex h-16 w-16 items-center justify-center rounded-full
        bg-nova-600 text-2xl text-white shadow-xl transition hover:bg-nova-500
        focus:outline-none focus-visible:ring-4 focus-visible:ring-nova-300"
    >
      {listening && (
        <motion.span
          className="absolute inset-0 rounded-full bg-nova-400"
          animate={{ scale: [1, 1.5], opacity: [0.6, 0] }}
          transition={{ duration: 1.2, repeat: Infinity }}
        />
      )}
      <span className="relative">🎙️</span>
    </motion.button>
  );
}
