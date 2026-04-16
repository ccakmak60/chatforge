import { Message } from "@/hooks/use-chat";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import { useEffect, useRef } from "react";

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center text-neutral-400">
        <p>Send a message to start chatting.</p>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1 p-4">
      <div className="mx-auto flex max-w-3xl flex-col gap-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={cn(
              "flex gap-3",
              msg.role === "user" ? "justify-end" : "justify-start"
            )}
          >
            {msg.role === "assistant" && (
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-blue-600 text-white text-xs">
                  AI
                </AvatarFallback>
              </Avatar>
            )}
            <div
              className={cn(
                "max-w-[80%] rounded-lg px-4 py-2 text-sm",
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-white border text-neutral-900"
              )}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}
