"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

import type { Message } from "@/lib/types";

interface Props {
  messages: Message[];
  streaming: string;
  busy: boolean;
  onSend: (text: string) => void;
}

export function ChatPanel({ messages, streaming, busy, onSend }: Props) {
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streaming]);

  const submit = () => {
    const text = draft.trim();
    if (!text || busy) return;
    onSend(text);
    setDraft("");
  };

  return (
    <div className="flex h-full flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto p-1">
        {messages.length === 0 && !streaming && (
          <div className="flex h-full flex-col items-center justify-center text-center text-slate-500">
            <p className="text-lg font-medium">Say “Hey Nova” or type below</p>
            <p className="text-sm">Ask anything, or try “what can you do?”</p>
          </div>
        )}
        <AnimatePresence initial={false}>
          {messages.map((m) => (
            <motion.div
              key={m.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[75%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm shadow ${
                  m.role === "user"
                    ? "bg-nova-600 text-white"
                    : "glass"
                }`}
              >
                {m.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {streaming && (
          <div className="flex justify-start">
            <div className="glass max-w-[75%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-sm shadow">
              {streaming}
              <span className="ml-0.5 inline-block animate-pulse">▍</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="mt-3 flex items-end gap-2">
        <textarea
          className="input max-h-40 min-h-[48px] resize-none"
          placeholder="Message Nova…"
          rows={1}
          value={draft}
          aria-label="Message Nova"
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
        />
        <button
          type="button"
          className="btn-primary h-12"
          onClick={submit}
          disabled={busy || !draft.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}
