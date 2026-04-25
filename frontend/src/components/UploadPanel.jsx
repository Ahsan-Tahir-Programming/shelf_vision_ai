import { useState, useRef } from "react";

export default function UploadPanel({ onAnalyze, loading }) {
  const [storeName, setStoreName] = useState("");
  const [notes, setNotes] = useState("");
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  const handleFile = (f) => {
    if (!f || !f.type.startsWith("image/")) return;
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    handleFile(e.dataTransfer.files[0]);
  };

  const handleSubmit = () => {
    if (!file || !storeName.trim()) return;
    onAnalyze(file, storeName.trim().toLowerCase(), notes);
  };

  return (
    <div className="bg-dark-800 border border-dark-600 rounded-2xl p-6 animate-fade-up">
      <h2 className="font-display font-bold text-white text-lg mb-5">
        New Shelf Audit
      </h2>

      {/* Image Drop Zone */}
      <div
        onClick={() => inputRef.current.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-xl cursor-pointer
          transition-all duration-200 overflow-hidden mb-4
          ${
            dragging
              ? "border-brand-500 bg-brand-500/10"
              : "border-dark-500 hover:border-dark-400 bg-dark-700"
          }
        `}
        style={{ height: preview ? "200px" : "140px" }}
      >
        {preview ? (
          <img
            src={preview}
            alt="shelf preview"
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full gap-2">
            <div className="w-10 h-10 rounded-full bg-dark-600 flex items-center justify-center">
              <svg
                className="w-5 h-5 text-zinc-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <p className="text-sm text-zinc-400">
              Drop shelf image or <span className="text-brand-400">browse</span>
            </p>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
      </div>

      {/* Store Name */}
      <input
        type="text"
        placeholder="Store name (e.g. store lahore)"
        value={storeName}
        onChange={(e) => setStoreName(e.target.value)}
        className="w-full bg-dark-700 border border-dark-500 rounded-lg px-4 py-2.5
                   text-sm text-white placeholder-zinc-500 mb-3
                   focus:outline-none focus:border-brand-500 transition-colors"
      />

      {/* Notes */}
      <input
        type="text"
        placeholder="Notes (optional — e.g. morning audit)"
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        className="w-full bg-dark-700 border border-dark-500 rounded-lg px-4 py-2.5
                   text-sm text-white placeholder-zinc-500 mb-4
                   focus:outline-none focus:border-brand-500 transition-colors"
      />

      {/* Submit */}
      <button
        onClick={handleSubmit}
        disabled={!file || !storeName.trim() || loading}
        className="w-full bg-brand-500 hover:bg-brand-600 disabled:opacity-40
                   disabled:cursor-not-allowed text-white font-display font-semibold
                   py-3 rounded-lg transition-all duration-200 text-sm"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <svg
              className="w-4 h-4 animate-spin"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8z"
              />
            </svg>
            Analyzing...
          </span>
        ) : (
          "Analyze Shelf"
        )}
      </button>
    </div>
  );
}
