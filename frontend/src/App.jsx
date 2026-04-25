import { useState, useEffect } from "react";
import { analyzeShelf, sendChatMessage, getHistory, getStats } from "./api";
import Header from "./components/Header";
import UploadPanel from "./components/UploadPanel";
import ScoreCard from "./components/ScoreCard";
import ChatPanel from "./components/ChatPanel";
import HistoryPanel from "./components/HistoryPanel";

export default function App() {
  const [stats, setStats] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState(null);
  const [messages, setMessages] = useState([]);
  const [storeName, setStoreName] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load stats on mount
  useEffect(() => {
    getStats().then(setStats).catch(console.error);
  }, []);

  const handleAnalyze = async (file, store, notes) => {
    setAnalyzing(true);
    setError(null);
    setMessages([]);
    try {
      const result = await analyzeShelf(file, store, notes);
      setAnalysis(result);
      setStoreName(store);
      const hist = await getHistory(store);
      setHistory(hist);
      const updatedStats = await getStats();
      setStats(updatedStats);
    } catch (e) {
      setError(
        e.response?.data?.detail || "Analysis failed. Is the server running?",
      );
    } finally {
      setAnalyzing(false);
    }
  };

  const handleChat = async (message) => {
    if (!storeName) return;
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setChatLoading(true);
    try {
      const result = await sendChatMessage(storeName, message);
      setMessages((prev) => [
        ...prev,
        { role: "ai", content: result.response },
      ]);
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          content:
            "Error: " + (e.response?.data?.detail || "Something went wrong"),
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dark-900">
      <Header stats={stats} />

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Page Title */}
        <div className="mb-8 animate-fade-up">
          <h2 className="font-display font-bold text-3xl text-white mb-1">
            Shelf Compliance Dashboard
          </h2>
          <p className="text-zinc-500">
            Upload a shelf image to analyze planogram compliance with AI
          </p>
        </div>

        {/* Error Banner */}
        {error && (
          <div
            className="mb-6 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3
                          text-red-400 text-sm animate-fade-up"
          >
            ⚠ {error}
          </div>
        )}

        {/* Main Grid */}
        <div className="grid grid-cols-12 gap-5">
          {/* Left Column */}
          <div className="col-span-3 space-y-5">
            <UploadPanel onAnalyze={handleAnalyze} loading={analyzing} />
            <HistoryPanel history={history} />
          </div>

          {/* Middle Column */}
          <div className="col-span-5">
            {analysis ? (
              <ScoreCard analysis={analysis} />
            ) : (
              <div
                className="bg-dark-800 border border-dark-600 rounded-2xl
                              flex flex-col items-center justify-center animate-fade-up"
                style={{ height: "480px" }}
              >
                <div
                  className="w-16 h-16 rounded-2xl bg-dark-700 border border-dark-600
                                flex items-center justify-center mb-4"
                >
                  <span className="text-2xl">🏪</span>
                </div>
                <p className="font-display font-semibold text-white text-lg mb-1">
                  No Analysis Yet
                </p>
                <p className="text-zinc-500 text-sm text-center max-w-xs">
                  Upload a shelf image to see the compliance analysis here
                </p>
              </div>
            )}
          </div>

          {/* Right Column */}
          <div className="col-span-4">
            <ChatPanel
              onSend={handleChat}
              messages={messages}
              loading={chatLoading}
              storeName={storeName}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
