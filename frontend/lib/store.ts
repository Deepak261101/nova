"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import { api, setAccessToken } from "@/lib/api";
import type { Tokens, User } from "@/lib/types";

interface AuthState {
  user: User | null;
  tokens: Tokens | null;
  hydrated: boolean;
  setSession: (user: User, tokens: Tokens) => void;
  setTokens: (tokens: Tokens) => void;
  logout: () => void;
  bootstrap: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      hydrated: false,
      setSession: (user, tokens) => {
        setAccessToken(tokens.access_token);
        set({ user, tokens });
      },
      setTokens: (tokens) => {
        setAccessToken(tokens.access_token);
        set({ tokens });
      },
      logout: () => {
        setAccessToken(null);
        set({ user: null, tokens: null });
      },
      bootstrap: async () => {
        const tokens = get().tokens;
        if (!tokens) {
          set({ hydrated: true });
          return;
        }
        setAccessToken(tokens.access_token);
        try {
          const user = await api.me();
          set({ user, hydrated: true });
        } catch {
          // Try refresh once, else clear.
          try {
            const refreshed = await api.refresh(tokens.refresh_token);
            setAccessToken(refreshed.access_token);
            const user = await api.me();
            set({ user, tokens: refreshed, hydrated: true });
          } catch {
            setAccessToken(null);
            set({ user: null, tokens: null, hydrated: true });
          }
        }
      },
    }),
    {
      name: "nova-auth",
      partialize: (state) => ({ tokens: state.tokens }),
    },
  ),
);
