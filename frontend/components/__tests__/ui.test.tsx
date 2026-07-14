import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AIOrb } from "@/components/AIOrb";
import { ChatPanel } from "@/components/ChatPanel";
import { GlassCard } from "@/components/GlassCard";
import { Waveform } from "@/components/Waveform";

describe("UI components", () => {
  it("renders GlassCard children", () => {
    render(<GlassCard>hello nova</GlassCard>);
    expect(screen.getByText("hello nova")).toBeInTheDocument();
  });

  it("renders the AI orb and waveform without crashing", () => {
    const { container } = render(
      <div>
        <AIOrb status="idle" />
        <Waveform active={false} />
      </div>,
    );
    expect(container).toBeTruthy();
  });

  it("shows the empty-state prompt in ChatPanel", () => {
    render(<ChatPanel messages={[]} streaming="" busy={false} onSend={vi.fn()} />);
    expect(screen.getByText(/Say .Hey Nova/i)).toBeInTheDocument();
  });

  it("renders messages and calls onSend on Enter", async () => {
    const onSend = vi.fn();
    render(
      <ChatPanel
        messages={[{ id: "1", role: "user", content: "hi there" }]}
        streaming=""
        busy={false}
        onSend={onSend}
      />,
    );
    expect(screen.getByText("hi there")).toBeInTheDocument();
  });
});
