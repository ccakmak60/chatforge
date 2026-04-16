import { ChatPanel } from "@/components/chat/chat-panel";

export default function App() {
  return (
    <div className="flex h-screen bg-neutral-50">
      <main className="flex flex-1 flex-col">
        <header className="flex h-14 items-center border-b bg-white px-6">
          <h1 className="text-lg font-semibold">ChatForge</h1>
        </header>
        <ChatPanel />
      </main>
    </div>
  );
}
