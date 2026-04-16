const API_BASE = "/api";

export async function postChat(body: {
  session_id: string;
  bot_id: string;
  message: string;
}) {
  const resp = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) throw new Error(`Chat failed: ${resp.status}`);
  return resp.json();
}

export async function streamChat(
  body: { session_id: string; bot_id: string; message: string },
  onToken: (token: string) => void,
  onDone: () => void
) {
  const resp = await fetch(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) throw new Error(`Stream failed: ${resp.status}`);
  const reader = resp.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const payload = line.slice(6);
        if (payload === "[DONE]") {
          onDone();
          return;
        }
        const data = JSON.parse(payload);
        if (data.token) onToken(data.token);
      }
    }
  }
  onDone();
}

export async function uploadFile(file: File, botId: string) {
  const form = new FormData();
  form.append("file", file);
  form.append("bot_id", botId);
  const resp = await fetch(`${API_BASE}/ingest`, {
    method: "POST",
    body: form,
  });
  if (!resp.ok) throw new Error(`Upload failed: ${resp.status}`);
  return resp.json();
}

export async function fetchModels() {
  const resp = await fetch(`${API_BASE}/models`);
  if (!resp.ok) throw new Error(`Models failed: ${resp.status}`);
  return resp.json();
}
