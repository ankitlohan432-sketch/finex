import { useEffect, useState } from 'react'
import { portfolioAPI, transactionAPI, stockAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'
import { TrendingUp, TrendingDown, DollarSign, Activity, ArrowUpRight, ArrowDownRight } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const mockChart = Array.from({ length: 12 }, (_, i) => ({
  month: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][i],
  value: 8000 + Math.random() * 6000
}))

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload?.length) {
    return (
      <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '8px 12px' }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{label}</div>
        <div style={{ fontFamily: 'DM Mono', fontSize: 14, color: 'var(--accent)' }}>
          ${payload[0].value.toFixed(2)}
        </div>
      </div>
    )
  }
  return null
}

export default function Dashboard() {
  const { user } = useAuth()
  const [portfolio, setPortfolio] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [movers, setMovers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      portfolioAPI.get(),
      transactionAPI.getAll(),
      stockAPI.getTopMovers(),
    ]).then(([p, t, m]) => {
      if (p.status === 'fulfilled') setPortfolio(p.value.data)
      if (t.status === 'fulfilled') setTransactions((t.value.data || []).slice(0, 5))
      if (m.status === 'fulfilled') setMovers((m.value.data || []).slice(0, 4))
    }).finally(() => setLoading(false))
  }, [])

  const greeting = () => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 17) return 'Good afternoon'
    return 'Good evening'
  }

  const fmt = (n) => n != null ? `$${Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—'
  const fmtPct = (n) => n != null ? `${n >= 0 ? '+' : ''}${Number(n).toFixed(2)}%` : '—'

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 300 }}>
      <div className="spinner" style={{ width: 32, height: 32 }} />
    </div>
  )

  return (
    <div>
      {/* Greeting */}
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ fontFamily: 'Syne', fontSize: 22, fontWeight: 700, marginBottom: 4 }}>
          {greeting()}, {user?.full_name?.split(' ')[0] || 'Investor'} 👋
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>Here's your portfolio overview for today.</p>
      </div>

      {/* Stats */}
      <div className="grid-4" style={{ marginBottom: 20 }}>
        <div className="stat-card">
          <div className="stat-label">Total Balance</div>
          <div className="stat-value">{fmt(portfolio?.total_balance)}</div>
          <div className={`stat-change ${(portfolio?.profit_loss ?? 0) >= 0 ? 'up' : 'down'}`}>
            {(portfolio?.profit_loss ?? 0) >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {fmtPct(portfolio?.profit_loss_percentage)} this month
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Invested</div>
          <div className="stat-value">{fmt(portfolio?.invested_amount)}</div>
          <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
            <Activity size={12} /> Total deployed
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">P&L</div>
          <div className="stat-value" style={{ color: (portfolio?.profit_loss ?? 0) >= 0 ? 'var(--success)' : 'var(--danger)' }}>
            {fmt(portfolio?.profit_loss)}
          </div>
          <div className={`stat-change ${(portfolio?.profit_loss ?? 0) >= 0 ? 'up' : 'down'}`}>
            {(portfolio?.profit_loss ?? 0) >= 0 ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}
            {fmtPct(portfolio?.profit_loss_percentage)}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Cash Available</div>
          <div className="stat-value">{fmt(portfolio?.cash_available)}</div>
          <div className="stat-change" style={{ color: 'var(--text-muted)' }}>
            <DollarSign size={12} /> Ready to invest
          </div>
        </div>
      </div>

      <div className="grid-2-1" style={{ marginBottom: 20 }}>
        {/* Chart */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Portfolio Performance</span>
            <span className="badge badge-success">+12.4% YTD</span>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={mockChart}>
              <XAxis dataKey="month" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis hide />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="value" stroke="var(--accent)" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Top Movers */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Top Movers</span>
          </div>
          {movers.length > 0 ? movers.map((m, i) => (
            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 0', borderBottom: i < movers.length - 1 ? '1px solid var(--border)' : 'none' }}>
              <div>
                <div style={{ fontFamily: 'DM Mono', fontSize: 13, fontWeight: 500 }}>{m.symbol}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{m.name}</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontFamily: 'DM Mono', fontSize: 13 }}>${m.price?.toFixed(2)}</div>
                <div style={{ fontSize: 12, color: m.change >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                  {m.change >= 0 ? '+' : ''}{m.change?.toFixed(2)}%
                </div>
              </div>
            </div>
          )) : (
            <div style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', padding: '20px 0' }}>
              Market data unavailable
            </div>
          )}
        </div>
      </div>

      {/* Recent Transactions */}
      <div className="card">
        <div className="card-header">
          <span className="card-title">Recent Transactions</span>
        </div>
        {transactions.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Symbol</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map(tx => (
                  <tr key={tx.id}>
                    <td><span className={`badge ${tx.type === 'BUY' ? 'badge-success' : tx.type === 'SELL' ? 'badge-danger' : 'badge-info'}`}>{tx.type}</span></td>
                    <td className="mono">{tx.symbol || '—'}</td>
                    <td className="mono">{fmt(tx.total_amount)}</td>
                    <td><span className={`badge ${tx.status === 'COMPLETED' ? 'badge-success' : tx.status === 'FAILED' ? 'badge-danger' : 'badge-warning'}`}>{tx.status}</span></td>
                    <td style={{ color: 'var(--text-muted)' }}>{new Date(tx.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ color: 'var(--text-muted)', fontSize: 13, textAlign: 'center', padding: '20px 0' }}>
            No transactions yet
          </div>
        )}
      </div>
    </div>
  )
}
