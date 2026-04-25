export default function HistoryPanel({ history }) {
  if (!history || history.audits?.length === 0) {
    return (
      <div className="bg-dark-800 border border-dark-600 rounded-2xl p-6 animate-fade-up delay-300">
        <h2 className="font-display font-bold text-white text-lg mb-4">
          Audit History
        </h2>
        <p className="text-zinc-500 text-sm text-center py-8">
          No audit history yet
        </p>
      </div>
    );
  }

  return (
    <div className="bg-dark-800 border border-dark-600 rounded-2xl p-6 animate-fade-up delay-300">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-display font-bold text-white text-lg">
          Audit History
        </h2>
        <span className="text-xs font-mono text-zinc-500 bg-dark-700 px-2.5 py-1 rounded-full">
          {history.total_audits} audits
        </span>
      </div>

      {/* Mini trend chart */}
      <div className="flex items-end gap-1 h-12 mb-4 bg-dark-700 rounded-lg px-3 py-2">
        {[...history.audits].reverse().map((audit, i) => {
          const h = (audit.compliance_score / 100) * 100;
          const color =
            audit.compliance_score >= 90
              ? "#22c55e"
              : audit.compliance_score >= 70
                ? "#f97316"
                : "#ef4444";
          return (
            <div
              key={audit.audit_id}
              className="flex-1 rounded-sm transition-all"
              style={{ height: `${h}%`, backgroundColor: color, opacity: 0.8 }}
              title={`${audit.audit_date}: ${audit.compliance_score}/100`}
            />
          );
        })}
      </div>

      {/* Audit list */}
      <div className="space-y-2 max-h-52 overflow-y-auto">
        {history.audits.map((audit) => {
          const color =
            audit.compliance_score >= 90
              ? "text-green-400"
              : audit.compliance_score >= 70
                ? "text-brand-400"
                : "text-red-400";
          return (
            <div
              key={audit.audit_id}
              className="flex items-center justify-between bg-dark-700
                         rounded-lg px-3 py-2.5 border border-dark-600"
            >
              <div>
                <span className="text-xs font-mono text-zinc-500">
                  {audit.audit_date}
                </span>
                {audit.violations_count > 0 && (
                  <span className="ml-2 text-xs text-red-400">
                    {audit.violations_count} violation
                    {audit.violations_count > 1 ? "s" : ""}
                  </span>
                )}
              </div>
              <span className={`font-display font-bold text-sm ${color}`}>
                {audit.compliance_score}/100
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
