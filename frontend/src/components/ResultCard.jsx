const RISK_FEATURES = ['has_ip_address', 'has_brand_typo', 'suspicious_tld', 'is_url_shortener', 'phishtank_match']

const FEATURE_LABELS = {
  has_ip_address: 'IP Address',
  has_brand_typo: 'Brand Typo',
  suspicious_tld: 'Suspicious TLD',
  is_url_shortener: 'URL Shortener',
  phishtank_match: 'PhishTank Match',
}

const VERDICT_STYLES = {
  phishing: {
    bg: 'bg-red-50 border-red-300',
    badge: 'bg-red-600 text-white',
    icon: '⚠',
    label: 'PHISHING',
  },
  suspicious: {
    bg: 'bg-amber-50 border-amber-300',
    badge: 'bg-amber-500 text-white',
    icon: '⚡',
    label: 'SUSPICIOUS',
  },
  safe: {
    bg: 'bg-emerald-50 border-emerald-300',
    badge: 'bg-emerald-600 text-white',
    icon: '✓',
    label: 'SAFE',
  },
}

export default function ResultCard({ result }) {
  if (!result) return null
  const style = VERDICT_STYLES[result.verdict] || VERDICT_STYLES.safe
  const pct = Math.round(result.confidence * 100)

  return (
    <div className={`border-2 rounded-xl p-6 ${style.bg}`}>
      <div className="flex items-center gap-4 mb-4">
        <span className={`text-4xl font-bold px-4 py-2 rounded-lg ${style.badge}`}>
          {style.icon}
        </span>
        <div>
          <div className={`text-2xl font-extrabold ${style.badge.includes('red') ? 'text-red-700' : style.badge.includes('amber') ? 'text-amber-700' : 'text-emerald-700'}`}>
            {style.label}
          </div>
          <div className="text-slate-600 text-sm">
            Confidence: <span className="font-bold">{pct}%</span>
          </div>
        </div>
      </div>

      <div>
        <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Risk Signals</p>
        <div className="flex flex-wrap gap-2">
          {RISK_FEATURES.map(key => {
            const active = result.features?.[key]
            return (
              <span
                key={key}
                className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                  active ? 'bg-red-100 text-red-700 border border-red-300' : 'bg-slate-100 text-slate-500 border border-slate-200'
                }`}
              >
                {active ? '✗ ' : '✓ '}{FEATURE_LABELS[key]}
              </span>
            )
          })}
        </div>
      </div>
    </div>
  )
}
