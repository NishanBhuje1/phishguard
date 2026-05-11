import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { scanAPI } from '../services/api'
import ResultCard from '../components/ResultCard'
import ScanHistory from '../components/ScanHistory'

export default function Scanner() {
  const navigate = useNavigate()
  const [url, setUrl] = useState('')
  const [result, setResult] = useState(null)
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const email = localStorage.getItem('email') || 'User'
  const role = localStorage.getItem('role')

  useEffect(() => { loadHistory() }, [])

  async function loadHistory() {
    try {
      const res = await scanAPI.history()
      setScans(res.data)
    } catch {
      // ignore — history is non-critical
    }
  }

  async function handleScan(e) {
    e.preventDefault()
    setError('')
    setResult(null)
    setLoading(true)
    try {
      const res = await scanAPI.scan(url)
      setResult(res.data)
      loadHistory()
    } catch (err) {
      setError(err.response?.data?.detail || 'Scan failed')
    } finally {
      setLoading(false)
    }
  }

  function logout() {
    localStorage.clear()
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-slate-100">
      {/* Header */}
      <header className="bg-slate-900 text-white px-6 py-4 flex items-center justify-between shadow">
        <h1 className="text-xl font-bold tracking-tight">PhishGuard</h1>
        <div className="flex items-center gap-4">
          {role === 'admin' && (
            <button
              onClick={() => navigate('/admin')}
              className="text-sm text-emerald-400 hover:text-emerald-300 transition-colors"
            >
              Admin Dashboard
            </button>
          )}
          <span className="text-slate-400 text-sm">{email}</span>
          <button
            onClick={logout}
            className="text-sm bg-slate-700 hover:bg-slate-600 px-3 py-1.5 rounded-lg transition-colors"
          >
            Logout
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-4 py-10 space-y-8">
        {/* Scan form */}
        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Scan a URL</h2>
          <form onSubmit={handleScan} className="flex gap-3">
            <input
              type="text"
              value={url}
              onChange={e => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="flex-1 border border-slate-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
            <button
              type="submit"
              disabled={loading || !url.trim()}
              className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold px-5 py-2.5 rounded-lg transition-colors whitespace-nowrap"
            >
              {loading ? 'Scanning…' : 'Scan URL'}
            </button>
          </form>
          {error && (
            <p className="mt-3 text-red-600 text-sm">{error}</p>
          )}
        </div>

        {/* Result */}
        {result && <ResultCard result={result} />}

        {/* History */}
        <div className="bg-white rounded-2xl shadow p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-4">Scan History</h2>
          <ScanHistory scans={scans} />
        </div>
      </main>
    </div>
  )
}
