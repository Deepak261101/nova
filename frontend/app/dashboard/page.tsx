"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

import { AIOrb } from "@/components/AIOrb";
import { ChatPanel } from "@/components/ChatPanel";
import { GlassCard } from "@/components/GlassCard";
import { MicButton } from "@/components/MicButton";
import { Sidebar } from "@/components/Sidebar";
import { Waveform } from "@/components/Waveform";
import { api, streamMessage } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import type { ConversationSummary, Message } from "@/lib/types";
import { useVoice } from "@/lib/useVoice";

let tempId = 0;
const nextId = () => `tmp-${Date.now()}-${tempId++}`;

const STATUS_LABEL: Record<string, string> = {
  idle: "Idle",
  "wake-listening": "Listening for “Hey Nova”…",
  listening: "Listening…",
  thinking: "Thinking…",
  speaking: "Speaking…",
  unsupported: "Voice not supported in this browser",
};

export default function DashboardPage() {
  const router = useRouter();
  const { user, tokens, hydrated, logout } = useAuthStore();

  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [streaming, setStreaming] = useState("");
  const [busy, setBusy] = useState(false);
  const activeIdRef = useRef<string | null>(null);
  activeIdRef.current = activeId;

  useEffect(() => {
    if (hydrated && !tokens) router.replace("/login");
  }, [hydrated, tokens, router]);

  const refreshConversations = useCallback(async () => {
    const list = await api.listConversations();
    setConversations(list);
    return list;
  }, []);

  const ensureConversation = useCallback(async (): Promise<string> => {
    if (activeIdRef.current) return activeIdRef.current;
    const convo = await api.createConversation();
    setActiveId(convo.id);
    setMessages([]);
    await refreshConversations();
    return convo.id;
  }, [refreshConversations]);

  const loadConversation = useCallback(async (id: string) => {
    const convo = await api.getConversation(id);
    setActiveId(id);
    setMessages(convo.messages);
    setStreaming("");
  }, []);

  useEffect(() => {
    if (!user) return;
    void (async () => {
      const list = await refreshConversations();
      if (list.length > 0) await loadConversation(list[0].id);
    })();
  }, [user, refreshConversations, loadConversation]);

  const send = useCallback(
    async (text: string): Promise<string> => {
      const id = await ensureConversation();
      setBusy(true);
      setMessages((m) => [
        ...m,
        { id: nextId(), role: "user", content: text },
      ]);
      setStreaming("");
      let full = "";
      try {
        full = await streamMessage(id, text, (delta) => {
          full += delta;
          setStreaming((s) => s + delta);
        });
      } catch {
        full = "Sorry, I couldn't reach the server.";
      }
      setMessages((m) => [
        ...m,
        { id: nextId(), role: "assistant", content: full },
      ]);
      setStreaming("");
      setBusy(false);
      void refreshConversations();
      return full;
    },
    [ensureConversation, refreshConversations],
  );

  const voice = useVoice({
    onCommand: async (text) => {
      const reply = await send(text);
      voice.speak(reply);
    },
  });

  const handleNew = useCallback(async () => {
    const convo = await api.createConversation();
    await refreshConversations();
    await loadConversation(convo.id);
  }, [refreshConversations, loadConversation]);

  const handleDelete = useCallback(
    async (id: string) => {
      await api.deleteConversation(id);
      const list = await refreshConversations();
      if (id === activeIdRef.current) {
        if (list.length > 0) await loadConversation(list[0].id);
        else {
          setActiveId(null);
          setMessages([]);
        }
      }
    },
    [refreshConversations, loadConversation],
  );

  const handleLogout = useCallback(() => {
    logout();
    router.replace("/login");
  }, [logout, router]);

  // Keyboard shortcut: Ctrl/Cmd + M toggles wake listening.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "m") {
        e.preventDefault();
        voice.wakeEnabled ? voice.disableWake() : voice.enableWake();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [voice]);

  if (!hydrated || !user) {
    return (
      <main className="flex min-h-screen items-center justify-center text-slate-500">
        Loading…
      </main>
    );
  }

  const active = voice.status === "listening" || voice.status === "speaking";

  return (
    <main className="flex h-screen gap-4 p-4">
      <Sidebar
        user={user}
        conversations={conversations}
        activeId={activeId}
        onSelect={loadConversation}
        onNew={handleNew}
        onDelete={handleDelete}
        onLogout={handleLogout}
      />

      <div className="flex flex-1 flex-col gap-4">
        <GlassCard className="flex items-center justify-between p-4">
          <div>
            <h1 className="text-lg font-semibold">Nova Assistant</h1>
            <p className="text-sm text-slate-500" aria-live="polite">
              {STATUS_LABEL[voice.status]}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden sm:block">
              <AIOrb status={voice.status} />
            </div>
            <div className="flex flex-col items-center gap-2">
              <MicButton status={voice.status} onClick={voice.pushToTalk} />
              <button
                type="button"
                className="text-xs text-nova-500 hover:underline"
                onClick={() =>
                  voice.wakeEnabled ? voice.disableWake() : voice.enableWake()
                }
              >
                {voice.wakeEnabled ? "Disable wake word" : "Enable “Hey Nova”"}
              </button>
            </div>
          </div>
        </GlassCard>

        <GlassCard className="px-4 py-2">
          <Waveform active={active} />
          {voice.transcript && (
            <p className="pb-2 text-center text-sm text-slate-500">
              “{voice.transcript}”
            </p>
          )}
        </GlassCard>

        <GlassCard className="flex-1 overflow-hidden p-4">
          <ChatPanel
            messages={messages}
            streaming={streaming}
            busy={busy}
            onSend={(t) => void send(t)}
          />
        </GlassCard>
      </div>
    </main>
  );
}
