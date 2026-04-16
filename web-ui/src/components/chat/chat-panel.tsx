import { useState } from "react";
import { useChat } from "@/hooks/use-chat";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { BotSelector } from "./bot-selector";

export function ChatPanel() {
  const [botId, setBotId] = useState("default");
  const { messages, isStreaming, sendMessage, clearMessages } = useChat(botId);

  return (
    <div className="flex flex-1 flex-col">
      <div className="flex items-center gap-3 border-b bg-white px-4 py-2">
        <span className="text-sm text-neutral-500">Bot:</span>
        <BotSelector value={botId} onChange={setBotId} />
        <button
          onClick={clearMessages}
          className="ml-auto text-xs text-neutral-400 hover:text-neutral-600"
        >
          Clear chat
        </button>
      </div>
      <MessageList messages={messages} />
      <MessageInput onSend={sendMessage} disabled={isStreaming} />
    </div>
  );
}
