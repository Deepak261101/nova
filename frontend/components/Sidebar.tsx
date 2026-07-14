"use client";

import Link from "next/link";
import { motion } from "framer-motion";

import { ThemeToggle } from "@/components/ThemeToggle";
import type { ConversationSummary, User } from "@/lib/types";

interface Props {
  user: User | null;
  conversations: ConversationSummary[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  onLogout: () => void;
}

export function Sidebar({
  user,
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
  onLogout,
}: Props) {
  return (
    <aside className="glass flex h-full w-72 shrink-0 flex-col gap-4 rounded-2xl p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-2xl">✦</span>
          <span className="text-lg font-semibold tracking-tight">Nova</span>
        </div>
        <ThemeToggle />
      </div>

      <button type="button" className="btn-primary w-full" onClick={onNew}>
        + New chat
      </button>

      <nav className="flex flex-col gap-1 text-sm" aria-label="Primary">
        <Link href="/dashboard" className="btn-ghost justify-start !py-2">
          🏠 Dashboard
        </Link>
        <Link href="/settings" className="btn-ghost justify-start !py-2">
          ⚙️ Settings
        </Link>
      </nav>

      <div className="mt-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
        Conversations
      </div>
      <div className="-mr-2 flex-1 overflow-y-auto pr-2">
        <ul className="flex flex-col gap-1">
          {conversations.length === 0 && (
            <li className="px-2 py-3 text-sm text-slate-500">No conversations yet.</li>
          )}
          {conversations.map((c) => (
            <motion.li
              key={c.id}
              layout
              className={`group flex items-center justify-between rounded-xl px-3 py-2 text-sm transition ${
                c.id === activeId
                  ? "bg-nova-500/20 font-medium"
                  : "hover:bg-white/40 dark:hover:bg-white/10"
              }`}
            >
              <button
                type="button"
                className="flex-1 truncate text-left"
                onClick={() => onSelect(c.id)}
                title={c.title}
              >
                {c.title}
              </button>
              <button
                type="button"
                aria-label={`Delete ${c.title}`}
                className="ml-2 opacity-0 transition group-hover:opacity-100"
                onClick={() => onDelete(c.id)}
              >
                🗑️
              </button>
            </motion.li>
          ))}
        </ul>
      </div>

      <div className="border-t border-white/20 pt-3">
        <div className="mb-2 flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-nova-500 text-white">
            {user?.display_name?.[0]?.toUpperCase() ?? "?"}
          </div>
          <div className="min-w-0">
            <div className="truncate text-sm font-medium">{user?.display_name}</div>
            <div className="truncate text-xs text-slate-500">{user?.email}</div>
          </div>
        </div>
        <button type="button" className="btn-ghost w-full !py-2 text-sm" onClick={onLogout}>
          Log out
        </button>
      </div>
    </aside>
  );
}
