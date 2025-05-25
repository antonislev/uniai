// src/App.tsx
import { useState, useEffect } from "react";
import { ChatOnly } from "./components/ChatOnly";

export function App() {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate any async init (e.g. connecting to your backend, fetching config)
    // Replace this with your real initialization promise if you have one
    const timer = setTimeout(() => setLoading(false), 1500);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="text-2xl font-medium text-gray-700 animate-pulse">
          Loading Chat…
        </div>
      </div>
    );
  }
  return <ChatOnly />;
}






