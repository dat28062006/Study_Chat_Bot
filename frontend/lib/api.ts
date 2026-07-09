const API_BASE = "/api";

export interface Document {
  id: string;
  filename: string;
  status: string;
  chunk_count: number;
  error_message: string | null;
  created_at: string;
}

export async function uploadDocument(
  file: File
): Promise<{ document_id: string; status: string }> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function listDocuments(): Promise<Document[]> {
  const res = await fetch(`${API_BASE}/documents`);
  if (!res.ok) throw new Error("Failed to fetch documents");
  return res.json();
}

export async function deleteDocument(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete");
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export async function loginUser(email: string): Promise<{ email: string; message: string }> {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getChatHistory(email: string): Promise<ChatMessage[]> {
  const res = await fetch(`${API_BASE}/chat/history/${encodeURIComponent(email)}`);
  if (!res.ok) throw new Error("Failed to fetch chat history");
  return res.json();
}

export async function streamChat(
  messages: ChatMessage[],
  documentIds: string[],
  agentType: string,
  email: string | null,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (err: string) => void
): Promise<void> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, document_ids: documentIds, agent_type: agentType, email }),
  });

  if (!res.ok) {
    onError(await res.text());
    return;
  }

  const reader = res.body?.getReader();
  if (!reader) {
    onError("No response body");
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const rawLine of lines) {
      const line = rawLine.replace(/\r/g, "");
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") {
          onDone();
          return;
        }
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) {
            onError(parsed.error);
            return;
          }
          onToken(parsed.token);
        } catch (e) {
          onToken(data);
        }
      }
    }
  }
  onDone();
}
