// src/components/Chat.tsx
import { useState } from "react";

type Message = { role: "user" | "assistant"; content: string };

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const send = async () => {
    if (!draft.trim()) return;
    setError(null);
    const userMsg: Message = { role: "user", content: draft };
    setMessages((prev) => [...prev, userMsg]);
    setDraft("");
    setLoading(true);

    try {
      const resp = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: [...messages, userMsg] }),
      });

      // Αν το status δεν είναι 2xx, διαβάζουμε το JSON με το detail
      if (!resp.ok) {
        let detail = `Error ${resp.status}`;
        try {
          const errJson = await resp.json();
          detail = errJson.detail ?? JSON.stringify(errJson);
        } catch {} 
        throw new Error(detail);
      }

      // Κανονική 2xx απάντηση
      const data = await resp.json();
      const assistantMsg: Message = {
        role: "assistant",
        content: data.reply,
      };
      setMessages((prev) => [...prev, assistantMsg]);

    } catch (e: any) {
      // Αν έχουμε λάθος, εμφανίζουμε το πραγματικό μήνυμα
      const msg = e?.message || "Unknown error";
      setError(msg);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `⚠️ ${msg}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full p-4 bg-white">
      {error && (
        <div className="mb-2 text-red-600 text-sm">{error}</div>
      )}
      <div className="flex-1 overflow-auto space-y-2 mb-4">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-xs px-3 py-1 rounded ${
                m.role === "user"
                  ? "bg-blue-500 text-white"
                  : "bg-gray-200 text-gray-800"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="text-gray-500 italic">AI is typing…</div>
        )}
      </div>
      <div className="flex">
        <input
          className="flex-1 border rounded-l px-2 py-1 focus:outline-none"
          value={draft}
          onChange={(e) => setDraft(e.currentTarget.value)}
          onKeyDown={(e) => e.key === "Enter" && !loading && send()}
          placeholder="Type your question…"
          disabled={loading}
        />
        <button
          className="bg-blue-600 text-white px-4 rounded-r disabled:opacity-50"
          onClick={send}
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}


