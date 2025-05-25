import { useState } from "react";

export function QAWidget() {
  const [q, setQ] = useState("");
  const [a, setA] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    setLoading(true); setA(null);
    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      const { answer } = await res.json();
      setA(answer);
    } catch (err: any) {
      setA("Error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <textarea
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="w-full border p-2 rounded"
        rows={3}
        placeholder="Ask the manual…"
      />
      <button
        disabled={!q.trim() || loading}
        onClick={ask}
        className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
      >
        {loading ? "Thinking…" : "Ask"}
      </button>
      {a && <div className="p-4 bg-gray-100 rounded whitespace-pre-wrap">{a}</div>}
    </div>
  );
}
