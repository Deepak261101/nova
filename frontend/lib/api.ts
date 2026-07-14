import { API_URL } from "@/lib/config";
import type {
  AuthResponse,
  ConversationDetail,
  ConversationSummary,
  MemoryItem,
  Message,
  Tokens,
  User,
} from "@/lib/types";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  // Auth
  register: (email: string, password: string, display_name: string) =>
    request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name }),
    }),
  login: (email: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  refresh: (refresh_token: string) =>
    request<Tokens>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token }),
    }),
  me: () => request<User>("/auth/me"),

  // Users
  updateProfile: (data: { display_name?: string; avatar_url?: string }) =>
    request<User>("/users/me", { method: "PATCH", body: JSON.stringify(data) }),
  updateSettings: (settings: Record<string, unknown>) =>
    request<User>("/users/me/settings", {
      method: "PUT",
      body: JSON.stringify({ settings }),
    }),

  // Conversations
  listConversations: () =>
    request<ConversationSummary[]>("/conversations"),
  createConversation: (title = "New conversation") =>
    request<ConversationDetail>("/conversations", {
      method: "POST",
      body: JSON.stringify({ title }),
    }),
  getConversation: (id: string) =>
    request<ConversationDetail>(`/conversations/${id}`),
  renameConversation: (id: string, title: string) =>
    request<void>(`/conversations/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ title }),
    }),
  deleteConversation: (id: string) =>
    request<void>(`/conversations/${id}`, { method: "DELETE" }),
  sendMessage: (id: string, message: string) =>
    request<Message>(`/conversations/${id}/messages`, {
      method: "POST",
      body: JSON.stringify({ message }),
    }),

  // Memory
  listMemory: () => request<MemoryItem[]>("/memory"),
  upsertMemory: (key: string, value: string, importance = 1) =>
    request<MemoryItem>("/memory", {
      method: "PUT",
      body: JSON.stringify({ key, value, importance }),
    }),
  deleteMemory: (key: string) =>
    request<void>(`/memory/${encodeURIComponent(key)}`, { method: "DELETE" }),
};

/**
 * Stream an assistant reply via Server-Sent Events, invoking onDelta for each
 * token chunk. Returns the full concatenated reply.
 */
export async function streamMessage(
  conversationId: string,
  message: string,
  onDelta: (delta: string) => void,
  signal?: AbortSignal,
): Promise<string> {
  const res = await fetch(
    `${API_URL}/conversations/${conversationId}/stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      },
      body: JSON.stringify({ message }),
      signal,
    },
  );
  if (!res.ok || !res.body) {
    throw new ApiError(res.status, "stream failed");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let full = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";
    for (const evt of events) {
      const line = evt.split("\n").find((l) => l.startsWith("data: "));
      if (!line) continue;
      const payload = line.slice(6).trim();
      if (!payload || payload === "{}") continue;
      try {
        const parsed = JSON.parse(payload) as { delta?: string };
        if (parsed.delta) {
          full += parsed.delta;
          onDelta(parsed.delta);
        }
      } catch {
        /* ignore malformed chunk */
      }
    }
  }
  return full;
}
