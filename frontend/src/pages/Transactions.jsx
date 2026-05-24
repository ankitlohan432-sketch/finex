import { useEffect, useState } from 'react'
import { transactionAPI } from '../services/api'
import { ArrowUpRight, ArrowDownRight, RefreshCw } from 'lucide-react'

export default function Transactions() {
  const [txs, setTxs] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    Promise.allSettled([transactionAPI.getAll(), transactionAPI.getStats()])
      .then(([t, s]) => {
        if (t.status === 'fulfilled') setTxs(t.value.data || [])
        if (s.status === 'fulfilled') setStats(s.value.data)
      }).finally(() => setLoading(false))
  }

  useEffect(load, [])

  const fmt = (n) => n != null ? `$${Number(n).toLocaleString('en-US', { minimumFractionDigits: 2 })}` : '—'

  const typeColor = (t) => t === 'BUY' ? 'badge-success' : t === 'SELL' ? 'badge-danger' : 'badge-info'
  const statusColor = (s) => s === 'COMPLETED' ? 'badge-success' : s === 'FAILED' ? 'badge-danger' : s === 'PENDING' ? 'badge-warning' : 'badge-muted'

  return (
    <div>
      {/* Stats */}
      <div className="grid-4" style={{ marginBottom: 20 }}>
        <div className="stat-card">
          <div className="stat-label">Total Transactions</div>
          <div className="stat-value">{stats?.total_count ?? txs.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Volume</div>
          <div className="stat-value">{fmt(stats?.total_volume)}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Buys</div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>{stats?.buy_count ?? txs.filter(t => t.type === 'BUY').length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Sells</div>
          <div className="stat-value" style={{ color: 'var(--danger)' }}>{stats?.sell_count ?? txs.filter(t => t.type === 'SELL').length}</div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <span className="card-title">All Transactions</span>
          <button className="btn btn-ghost btn-sm" onClick={load}>
            <RefreshCw size={13} />
          </button>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: 40 }}><div className="spinner" style={{ margin: 'auto' }} /></div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Type</th>
                  <th>Symbol</th>
                  <th>Qty</th>
                  <th>Price/Unit</th>
                  <th>Total</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {txs.map(tx => (
                  <tr key={tx.id}>
                    <td className="mono" style={{ color: 'var(--text-muted)' }}>#{tx.id}</td>
                    <td><span className={`badge ${typeColor(tx.type)}`}>{tx.type}</span></td>
                    <td className="mono" style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{tx.symbol || '—'}</td>
                    <td className="mono">{tx.quantity ?? '—'}</td>
                    <td className="mono">{fmt(tx.price_per_unit)}</td>
                    <td className="mono" style={{ color: 'var(--text-primary)' }}>{fmt(tx.total_amount)}</td>
                    <td><span className={`badge ${statusColor(tx.status)}`}>{tx.status}</span></td>
                    <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                      {new Date(tx.created_at).toLocaleDateString()} {new Date(tx.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                  </tr>
                ))}
                {txs.length === 0 && (
                  <tr><td colSpan={8} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>No transactions found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
