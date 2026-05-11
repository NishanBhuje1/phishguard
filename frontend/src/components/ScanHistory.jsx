const VERDICT_COLORS = {
  phishing: 'bg-red-100 text-red-700',
  suspicious: 'bg-amber-100 text-amber-700',
  safe: 'bg-emerald-100 text-emerald-700',
}

export default function ScanHistory({ scans }) {
  if (!scans || scans.length === 0) {
    return <p className="text-slate-500 text-sm text-center py-4">No scans yet.</p>
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 text-slate-600 text-left">
          <tr>
            <th className="px-4 py-3 font-semibold">URL Hash</th>
            <th className="px-4 py-3 font-semibold">Verdict</th>
            <th className="px-4 py-3 font-semibold">Confidence</th>
            <th className="px-4 py-3 font-semibold">Scanned At</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {scans.map(s => (
            <tr key={s.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 font-mono text-xs text-slate-600">{s.url_hash?.slice(0, 12)}…</td>
              <td className="px-4 py-3">
                <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${VERDICT_COLORS[s.verdict] || 'bg-slate-100 text-slate-600'}`}>
                  {s.verdict}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-600">{Math.round(s.confidence * 100)}%</td>
              <td className="px-4 py-3 text-slate-500 text-xs">
                {s.scanned_at ? new Date(s.scanned_at).toLocaleString() : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
