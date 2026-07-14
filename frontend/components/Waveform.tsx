"use client";

import { motion } from "framer-motion";

export function Waveform({ active }: { active: boolean }) {
  const bars = Array.from({ length: 24 });
  return (
    <div className="flex h-12 items-center justify-center gap-1" aria-hidden>
      {bars.map((_, i) => (
        <motion.span
          key={i}
          className="w-1 rounded-full bg-nova-400 dark:bg-nova-300"
          animate={{
            height: active
              ? [6, 10 + ((i * 7) % 34), 6]
              : [4, 6, 4],
          }}
          transition={{
            duration: 0.9 + (i % 5) * 0.12,
            repeat: Infinity,
            ease: "easeInOut",
            delay: (i % 6) * 0.05,
          }}
        />
      ))}
    </div>
  );
}
