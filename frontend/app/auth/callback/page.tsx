"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect } from "react";

import { api, setAccessToken } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

function CallbackInner() {
  const router = useRouter();
  const params = useSearchParams();
  const setSession = useAuthStore((s) => s.setSession);

  useEffect(() => {
    const access = params.get("access_token");
    const refresh = params.get("refresh_token");
    if (!access || !refresh) {
      router.replace("/login");
      return;
    }
    setAccessToken(access);
    void (async () => {
      try {
        const user = await api.me();
        setSession(user, {
          access_token: access,
          refresh_token: refresh,
          token_type: "bearer",
        });
        router.replace("/dashboard");
      } catch {
        router.replace("/login");
      }
    })();
  }, [params, router, setSession]);

  return (
    <main className="flex min-h-screen items-center justify-center">
      <p className="text-slate-500">Signing you in…</p>
    </main>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={null}>
      <CallbackInner />
    </Suspense>
  );
}
