import { describe, it, expect, vi } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useChat } from "../src/hooks/use-chat";

vi.mock("../src/lib/api", () => ({
  streamChat: vi.fn(async (_body, onToken, onDone) => {
    onToken("Hello");
    onToken(" world");
    onDone();
  }),
}));

describe("useChat", () => {
  it("adds user and assistant messages on send", async () => {
    const { result } = renderHook(() => useChat("test-bot"));

    await act(async () => {
      await result.current.sendMessage("Hi");
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0].role).toBe("user");
    expect(result.current.messages[0].content).toBe("Hi");
    expect(result.current.messages[1].role).toBe("assistant");
    expect(result.current.messages[1].content).toBe("Hello world");
  });

  it("clears messages", async () => {
    const { result } = renderHook(() => useChat("test-bot"));

    await act(async () => {
      await result.current.sendMessage("Hi");
    });
    expect(result.current.messages).toHaveLength(2);

    act(() => {
      result.current.clearMessages();
    });
    expect(result.current.messages).toHaveLength(0);
  });
});
