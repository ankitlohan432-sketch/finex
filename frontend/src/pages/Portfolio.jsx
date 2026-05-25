import { useEffect, useState } from 'react'
import { portfolioAPI } from '../services/api'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { TrendingUp, TrendingDown } from 'lucide-react'

const COLORS = ['#63b3ed', '#68d391', '#f6c90e', '#fc8181', '#b794f4', '#f6ad55']

export default function Portfolio() {
  const [portfolio, setPortfolio] = useState(null)
  const [overview, setOverview] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([portfolioAPI.get(), portfolioAPI.getOverview()])
      .then(([p, o]) => {
        if (p.status === 'fulfilled') setPortfolio(p.value.data)
        if (o.status === 'fulfilled') setOverview(o.value.data)
      }).finally(() => setLoading(false))
  }, [])

  const fmt = (n) => n != null ? `$${Number(n).toLocaleString('en-US', { minimumFractionDigits: 2 })}` : '$0.00'
  const fmtPct = (n) => n != null ? `${n >= 0 ? '+' : ''}${Number(n).toFixed(2)}%` : '0.00%'

  const pieData = overview?.holdings?.length > 0
    ? overview.holdings.map(h => ({ name: h.symbol, value: h.current_value }))
    : [
        { name: 'Cash', value: portfolio?.cash_available || 1 },
        { name: 'Invested', value: portfolio?.invested_amount || 0 },
      ]

  if (loading) return <div style={{ textAlign: 'center', padding: 60 }}><div className="spinner" style={{ margin: 'auto' }} /></div>

  return (
    <div>
      <div className="grid-4" style={{ marginBottom: 20 }}>
        {[
          { label: 'Total Value', value: fmt(portfolio?.total_balance), sub: 'Portfolio worth' },
          { label: 'Invested', value: fmt(portfolio?.invested_amount), sub: 'Capital deployed' },
          { label: 'P&L', value: fmt(portfolio?.profit_loss), color: (portfolio?.profit_loss ?? 0) >= 0 ? 'var(--success)' : 'var(--danger)', sub: fmtPct(portfolio?.profit_loss_percentage) },
          { label: 'Cash', value: fmt(portfolio?.cash_available), sub: 'Available' },
        ].map(({ label, value, color, sub }) => (
          <div className="stat-card" key={label}>
            <div className="stat-label">{label}</div>
            <div className="stat-value" style={color ? { color } : {}}>{value}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>{sub}</div>
          </div>
        ))}
      </div>

      <div className="grid-2">
        {/* Allocation chart */}
        <div className="card">
          <div className="card-header"><span className="card-title">Allocation</span></div>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={70} outerRadius={110} paddingAngle={3} dataKey="value">
                {pieData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(v) => fmt(v)} contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Holdings table */}
        <div className="card">
          <div className="card-header"><span className="card-title">Holdings</span></div>
          {overview?.holdings?.length > 0 ? (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Qty</th>
                    <th>Avg Cost</th>
                    <th>Value</th>
                    <th>P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {overview.holdings.map((h, i) => (
                    <tr key={i}>
                      <td className="mono" style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{h.symbol}</td>
                      <td className="mono">{h.quantity}</td>
                      <td className="mono">{fmt(h.avg_cost)}</td>
                      <td className="mono">{fmt(h.current_value)}</td>
                      <td style={{ color: (h.profit_loss ?? 0) >= 0 ? 'var(--success)' : 'var(--danger)', fontFamily: 'DM Mono', fontSize: 12 }}>
                        {fmtPct(h.profit_loss_pct)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', padding: '40px 0' }}>
              No holdings yet. Start trading in Markets.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
