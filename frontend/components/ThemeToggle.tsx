"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ThemeToggle() {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const isDark = resolvedTheme === "dark";

  return (
    <button
      type="button"
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      className="btn-ghost h-10 w-10 !px-0"
      onClick={() => setTheme(isDark ? "light" : "dark")}
    >
      {mounted ? (isDark ? "🌙" : "☀️") : "•"}
    </button>
  );
}
