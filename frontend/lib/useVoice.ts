"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { WAKE_WORD } from "@/lib/config";
import { getSpeechRecognition, type SpeechRecognitionLike } from "@/lib/speech";

export type VoiceStatus =
  | "idle"
  | "wake-listening"
  | "listening"
  | "thinking"
  | "speaking"
  | "unsupported";

interface UseVoiceOptions {
  onCommand: (text: string) => Promise<void> | void;
}

/**
 * Wake-word ("Hey Nova") + command capture using the browser SpeechRecognition
 * API, with speechSynthesis for spoken replies. Falls back to "unsupported"
 * where the API is unavailable (the chat text input still works).
 */
export function useVoice({ onCommand }: UseVoiceOptions) {
  const [status, setStatus] = useState<VoiceStatus>("idle");
  const [transcript, setTranscript] = useState("");
  const [wakeEnabled, setWakeEnabled] = useState(false);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const modeRef = useRef<"wake" | "command">("wake");

  const supported = typeof window !== "undefined" && getSpeechRecognition() !== null;

  const speak = useCallback((text: string) => {
    if (typeof window === "undefined" || !window.speechSynthesis) return;
    const utter = new SpeechSynthesisUtterance(text);
    utter.rate = 1.02;
    utter.pitch = 1;
    setStatus("speaking");
    utter.onend = () => setStatus(wakeEnabled ? "wake-listening" : "idle");
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
  }, [wakeEnabled]);

  const buildRecognition = useCallback(() => {
    const Ctor = getSpeechRecognition();
    if (!Ctor) return null;
    const rec = new Ctor();
    rec.lang = "en-US";
    rec.continuous = true;
    rec.interimResults = true;
    return rec;
  }, []);

  const startCommandCapture = useCallback(() => {
    modeRef.current = "command";
    setTranscript("");
    setStatus("listening");
  }, []);

  const handleResult = useCallback(
    async (finalText: string) => {
      const text = finalText.trim();
      if (!text) return;
      if (modeRef.current === "wake") {
        if (text.toLowerCase().includes(WAKE_WORD)) {
          startCommandCapture();
        }
        return;
      }
      // command mode
      modeRef.current = "wake";
      setStatus("thinking");
      await onCommand(text);
    },
    [onCommand, startCommandCapture],
  );

  const attachHandlers = useCallback(
    (rec: SpeechRecognitionLike) => {
      rec.onresult = (event) => {
        let interim = "";
        let final = "";
        for (let i = event.resultIndex; i < event.results.length; i += 1) {
          const chunk = event.results[i][0].transcript;
          if (i >= event.resultIndex) final += chunk;
          interim += chunk;
        }
        setTranscript(interim);
        // Heuristic: treat a pause-terminated phrase as final.
        if (final) void handleResult(final);
      };
      rec.onerror = () => {
        setStatus((s) => (s === "speaking" ? s : wakeEnabled ? "wake-listening" : "idle"));
      };
      rec.onend = () => {
        if (wakeEnabled && recognitionRef.current) {
          try {
            recognitionRef.current.start();
          } catch {
            /* already started */
          }
        }
      };
    },
    [handleResult, wakeEnabled],
  );

  const enableWake = useCallback(() => {
    if (!supported) {
      setStatus("unsupported");
      return;
    }
    const rec = buildRecognition();
    if (!rec) return;
    recognitionRef.current = rec;
    attachHandlers(rec);
    modeRef.current = "wake";
    setWakeEnabled(true);
    setStatus("wake-listening");
    try {
      rec.start();
    } catch {
      /* ignore */
    }
  }, [attachHandlers, buildRecognition, supported]);

  const disableWake = useCallback(() => {
    setWakeEnabled(false);
    setStatus("idle");
    recognitionRef.current?.abort();
    recognitionRef.current = null;
  }, []);

  const pushToTalk = useCallback(() => {
    if (!supported) {
      setStatus("unsupported");
      return;
    }
    if (!recognitionRef.current) {
      const rec = buildRecognition();
      if (!rec) return;
      recognitionRef.current = rec;
      attachHandlers(rec);
      try {
        rec.start();
      } catch {
        /* ignore */
      }
    }
    startCommandCapture();
  }, [attachHandlers, buildRecognition, startCommandCapture, supported]);

  useEffect(() => {
    return () => {
      recognitionRef.current?.abort();
      if (typeof window !== "undefined") window.speechSynthesis?.cancel();
    };
  }, []);

  return {
    status,
    setStatus,
    transcript,
    wakeEnabled,
    supported,
    enableWake,
    disableWake,
    pushToTalk,
    speak,
  };
}
