import { useState, useRef, useEffect } from "react";

export default function ChatPanel({ onSend, messages, loading, storeName }) {
  const [input, setInput] = useState("");
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim() || loading) return;
    onSend(input.trim());
    setInput("");
  };

  const suggestions = [
    "Calculate the compliance trend",
    "Which zones fail most often?",
    "Generate a full audit report",
    "What violations were found?",
  ];

  return (
    <div
      className="bg-dark-800 border border-dark-600 rounded-2xl flex flex-col animate-fade-up delay-200"
      style={{ height: "520px" }}
    >
      {/* Header */}
      <div className="px-5 py-4 border-b border-dark-600 flex items-center gap-3">
        <div
          className="w-8 h-8 rounded-full bg-brand-500/20 border border-brand-500/30
                        flex items-center justify-center"
        >
          <span className="text-brand-400 text-xs font-bold">AI</span>
        </div>
        <div>
          <p className="text-sm font-display font-semibold text-white">
            ShelfVision Agent
          </p>
          <p className="text-xs text-zinc-500">
            {storeName ? `Analyzing: ${storeName}` : "No shelf loaded"}
          </p>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          <span className="text-xs text-zinc-500">Active</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <p className="text-zinc-500 text-sm">
              Analyze a shelf to start chatting
            </p>
            <div className="grid grid-cols-2 gap-2 w-full">
              {suggestions.map((s) => (
                <button
                  key={s}
                  onClick={() => onSend(s)}
                  disabled={!storeName}
                  className="text-xs text-zinc-400 bg-dark-700 border border-dark-500
                             hover:border-brand-500 hover:text-brand-400 rounded-lg
                             px-3 py-2 text-left transition-colors disabled:opacity-30
                             disabled:cursor-not-allowed"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-xl px-4 py-2.5 text-sm leading-relaxed
                ${
                  msg.role === "user"
                    ? "bg-brand-500 text-white rounded-br-sm"
                    : "bg-dark-700 text-zinc-200 rounded-bl-sm border border-dark-500"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="flex justify-start">
            <div
              className="bg-dark-700 border border-dark-500 rounded-xl rounded-bl-sm
                            px-4 py-3 flex items-center gap-2"
            >
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    className="w-1.5 h-1.5 rounded-full bg-zinc-400 animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
              </div>
              <span className="text-xs text-zinc-500">Agent thinking...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3 border-t border-dark-600">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder={
              storeName ? "Ask about this shelf..." : "Analyze a shelf first"
            }
            disabled={!storeName || loading}
            className="flex-1 bg-dark-700 border border-dark-500 rounded-lg px-4 py-2.5
                       text-sm text-white placeholder-zinc-600
                       focus:outline-none focus:border-brand-500 transition-colors
                       disabled:opacity-40 disabled:cursor-not-allowed"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || !storeName || loading}
            className="bg-brand-500 hover:bg-brand-600 disabled:opacity-40
                       disabled:cursor-not-allowed text-white px-4 py-2.5
                       rounded-lg transition-colors"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
