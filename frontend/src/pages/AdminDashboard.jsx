import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { adminAPI } from '../services/api'

const VERDICT_COLORS = {
  phishing: 'bg-red-100 text-red-700',
  suspicious: 'bg-amber-100 text-amber-700',
  safe: 'bg-emerald-100 text-emerald-700',
}

export default function AdminDashboard() {
  const navigate = useNavigate()
  const role = localStorage.getItem('role')
  const [tab, setTab] = useState('scans')
  const [scans, setScans] = useState([])
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  // Redirect non-admins immediately
  useEffect(() => {
    if (role !== 'admin') {
      navigate('/scanner')
      return
    }
    Promise.all([adminAPI.scans(), adminAPI.users()])
      .then(([s, u]) => { setScans(s.data); setUsers(u.data) })
      .catch(() => navigate('/scanner'))
      .finally(() => setLoading(false))
  }, [])

  if (role !== 'admin') return null

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between shadow">
        <h1 className="text-xl font-bold tracking-tight">PhishGuard — Admin</h1>
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/scanner')} className="text-sm text-emerald-400 hover:text-emerald-300">
            Scanner
          </button>
          <button
            onClick={() => { localStorage.clear(); navigate('/') }}
            className="text-sm bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-lg transition-colors"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-10">
        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-white rounded-xl shadow p-1 w-fit">
          {['scans', 'users'].map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-5 py-2 rounded-lg text-sm font-semibold transition-colors capitalize ${
                tab === t ? 'bg-slate-900 text-white' : 'text-slate-500 hover:text-slate-700'
              }`}
            >
              {t === 'scans' ? 'All Scans' : 'All Users'}
            </button>
          ))}
        </div>

        {loading ? (
          <p className="text-slate-500">Loading…</p>
        ) : tab === 'scans' ? (
          <div className="bg-white rounded-2xl shadow overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600 text-left">
                <tr>
                  {['User ID', 'URL Hash', 'Verdict', 'Confidence', 'IP Hash', 'Scanned At'].map(h => (
                    <th key={h} className="px-4 py-3 font-semibold">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {scans.map(s => (
                  <tr key={s.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-slate-600">{s.user_id}</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-600">{s.url_hash?.slice(0, 12)}…</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${VERDICT_COLORS[s.verdict] || ''}`}>
                        {s.verdict}
                      </span>
                    </td>
                    <td className="px-4 py-3">{Math.round(s.confidence * 100)}%</td>
                    <td className="px-4 py-3 font-mono text-xs text-slate-600">{s.ip_hash?.slice(0, 12)}…</td>
                    <td className="px-4 py-3 text-xs text-slate-500">
                      {s.scanned_at ? new Date(s.scanned_at).toLocaleString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {scans.length === 0 && <p className="text-center py-8 text-slate-400">No scans yet.</p>}
          </div>
        ) : (
          <div className="bg-white rounded-2xl shadow overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-slate-600 text-left">
                <tr>
                  {['ID', 'Email', 'Role', 'Created At'].map(h => (
                    <th key={h} className="px-4 py-3 font-semibold">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map(u => (
                  <tr key={u.id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 text-slate-600">{u.id}</td>
                    <td className="px-4 py-3">{u.email}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                        u.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-slate-100 text-slate-600'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-500">
                      {u.created_at ? new Date(u.created_at).toLocaleString() : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  )
}
