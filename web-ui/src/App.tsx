import { useState } from "react";
import { ChatPanel } from "@/components/chat/chat-panel";
import { UploadWidget } from "@/components/upload/upload-widget";

export default function App() {
  const [botId] = useState("default");

  return (
    <div className="flex h-screen bg-neutral-50">
      <aside className="flex w-72 flex-col gap-4 border-r bg-white p-4">
        <h2 className="text-sm font-semibold text-neutral-700">Tools</h2>
        <UploadWidget botId={botId} />
      </aside>
      <main className="flex flex-1 flex-col">
        <header className="flex h-14 items-center border-b bg-white px-6">
          <h1 className="text-lg font-semibold">ChatForge</h1>
        </header>
        <ChatPanel />
      </main>
    </div>
  );
}
