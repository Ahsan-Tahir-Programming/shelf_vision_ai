export default function ScoreCard({ analysis }) {
  const score = analysis.compliance_score;
  const color = score >= 90 ? "#22c55e" : score >= 70 ? "#f97316" : "#ef4444";
  const label = score >= 90 ? "Excellent" : score >= 70 ? "Good" : "Critical";
  const circumference = 2 * Math.PI * 45;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="bg-dark-800 border border-dark-600 rounded-2xl p-6 animate-fade-up delay-100">
      {/* Score Ring */}
      <div className="flex items-center gap-6 mb-5">
        <div className="relative w-24 h-24 flex-shrink-0">
          <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="#242424"
              strokeWidth="8"
            />
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke={color}
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              strokeLinecap="round"
              style={{ transition: "stroke-dashoffset 1s ease" }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="font-display font-bold text-white text-xl leading-none">
              {score}
            </span>
            <span className="text-xs text-zinc-500">/100</span>
          </div>
        </div>

        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="font-display font-bold text-white text-2xl">
              {label}
            </span>
            <span
              className="text-xs px-2 py-0.5 rounded-full font-mono"
              style={{ background: color + "20", color }}
            >
              {score >= 90 ? "✓ Pass" : score >= 70 ? "⚠ Review" : "✗ Fail"}
            </span>
          </div>
          <p className="text-sm text-zinc-400 leading-relaxed">
            {analysis.summary}
          </p>
          <p className="text-xs text-zinc-600 mt-1 font-mono">
            ID: {analysis.audit_id} · {analysis.audit_date}
          </p>
        </div>
      </div>

      {/* Zones */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        {Object.entries(analysis.zones).map(([zone, data]) => (
          <div
            key={zone}
            className="bg-dark-700 rounded-lg px-3 py-2 flex items-center justify-between"
          >
            <span className="text-xs text-zinc-400 capitalize">
              {zone.replace("_", " ")}
            </span>
            <span
              className={`text-xs font-mono font-medium ${
                data.status === "pass" ? "text-green-400" : "text-red-400"
              }`}
            >
              {data.status === "pass" ? "✓ Pass" : "✗ Fail"}
            </span>
          </div>
        ))}
      </div>

      {/* Brands */}
      <div className="mb-4">
        <p className="text-xs text-zinc-500 mb-2 font-mono uppercase tracking-wider">
          Brands Detected
        </p>
        <div className="flex flex-wrap gap-1.5">
          {analysis.brands_detected.map((brand) => (
            <span
              key={brand}
              className="text-xs bg-dark-600 text-zinc-300 px-2.5 py-1 rounded-full border border-dark-500"
            >
              {brand}
            </span>
          ))}
        </div>
      </div>

      {/* Violations */}
      {analysis.violations.length > 0 && (
        <div>
          <p className="text-xs text-zinc-500 mb-2 font-mono uppercase tracking-wider">
            Violations
          </p>
          {analysis.violations.map((v, i) => (
            <div
              key={i}
              className="flex gap-2 text-sm text-red-300 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2 mb-1.5"
            >
              <span className="text-red-400 flex-shrink-0">⚠</span>
              {v}
            </div>
          ))}
        </div>
      )}

      {/* Recommendations */}
      <div className="mt-3">
        <p className="text-xs text-zinc-500 mb-2 font-mono uppercase tracking-wider">
          Recommendations
        </p>
        {analysis.recommendations.map((r, i) => (
          <div key={i} className="flex gap-2 text-sm text-zinc-300 mb-1.5">
            <span className="text-brand-400 flex-shrink-0 font-mono">
              {i + 1}.
            </span>
            {r}
          </div>
        ))}
      </div>
    </div>
  );
}
