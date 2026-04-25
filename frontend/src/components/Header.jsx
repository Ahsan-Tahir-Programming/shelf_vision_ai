export default function Header({ stats }) {
  return (
    <header className="border-b border-dark-600 bg-dark-800 px-8 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center">
            <span className="text-white text-sm font-bold">SV</span>
          </div>
          <div>
            <h1 className="font-display font-bold text-white text-lg leading-none">
              ShelfVision AI
            </h1>
            <p className="text-xs text-zinc-500 mt-0.5">
              Retail Compliance Analyzer
            </p>
          </div>
        </div>

        {stats && (
          <div className="flex items-center gap-6">
            <Stat label="Total Audits" value={stats.total_audits} />
            <Stat label="Avg Score" value={`${stats.average_score}/100`} />
            <Stat label="Best Score" value={`${stats.highest_score}/100`} />
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
              <span className="text-xs text-zinc-400 font-mono">API Live</span>
            </div>
          </div>
        )}
      </div>
    </header>
  );
}

function Stat({ label, value }) {
  return (
    <div className="text-right">
      <div className="font-display font-bold text-white text-sm">{value}</div>
      <div className="text-xs text-zinc-500">{label}</div>
    </div>
  );
}
