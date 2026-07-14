import { afterEach, describe, expect, it, vi } from "vitest";

import { setAccessToken, streamMessage } from "@/lib/api";

function sseStream(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      for (const c of chunks) controller.enqueue(encoder.encode(c));
      controller.close();
    },
  });
}

describe("streamMessage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    setAccessToken(null);
  });

  it("accumulates SSE deltas and invokes the callback", async () => {
    const body = sseStream([
      'data: {"delta": "Hello"}\n\n',
      'data: {"delta": " world"}\n\n',
      "event: done\ndata: {}\n\n",
    ]);
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(body, { status: 200 })),
    );

    const deltas: string[] = [];
    const full = await streamMessage("c1", "hi", (d) => deltas.push(d));

    expect(deltas).toEqual(["Hello", " world"]);
    expect(full).toBe("Hello world");
  });

  it("throws on non-ok responses", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response(null, { status: 500 })),
    );
    await expect(streamMessage("c1", "hi", () => {})).rejects.toThrow();
  });
});
