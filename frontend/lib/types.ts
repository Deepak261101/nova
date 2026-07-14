export type Role = "system" | "user" | "assistant" | "tool";

export interface User {
  id: string;
  email: string;
  display_name: string;
  role: string;
  auth_provider: string;
  avatar_url?: string | null;
  settings: Record<string, unknown>;
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResponse {
  user: User;
  tokens: Tokens;
}

export interface Message {
  id: string;
  role: Role;
  content: string;
  meta?: Record<string, unknown>;
  created_at?: string | null;
}

export interface ConversationSummary {
  id: string;
  title: string;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface ConversationDetail extends ConversationSummary {
  messages: Message[];
}

export interface MemoryItem {
  id: string;
  key: string;
  value: string;
  importance: number;
}
