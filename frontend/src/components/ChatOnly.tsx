// src/components/ChatOnly.tsx
import { useState, useRef, useEffect } from "react";

type Message = 
  | { role: "user"; content: string }
  | { role: "assistant"; content: string };

export function ChatOnly() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  // auto‐scroll on new message
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    if (!draft.trim()) return;
    const userMsg: Message = { role: "user", content: draft };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setDraft("");
    setLoading(true);

    try {
      const resp = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: updated }),
      });
      const text = await resp.text();
      let data: any = {};
      if (text) {
        try { data = JSON.parse(text); } catch {}
      }
      if (!resp.ok) {
        const err = data.detail || data.error?.message || resp.statusText;
        throw new Error(err);
      }
      const botMsg: Message = { role: "assistant", content: data.reply };
      setMessages((m) => [...m, botMsg]);
    } catch (e: any) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `⚠️ ${e.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="bg-blue-700 text-white py-4 text-center text-xl font-semibold shadow">
        BMW X1 Manual Assistant
      </header>

      {/* Messages */}
       <div className="flex-1 overflow-auto p-4 space-y-4 bg-gray-100">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[75%] px-4 py-2 rounded-lg shadow
                ${m.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-white text-gray-800"}
              `}
            >
              <div className="whitespace-pre-wrap">{m.content}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="text-center text-gray-500 italic">AI is typing…</div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="border-t p-4 bg-white flex">
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.currentTarget.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Ask your BMW X1 question…"
          disabled={loading}
          className="flex-1 border border-gray-300 rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        <button
          onClick={send}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 rounded-r-lg disabled:opacity-50 transition"
        >
          Send
        </button>
      </div>
    </div>
  );
}




