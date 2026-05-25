import { useEffect, useState } from 'react'
import { analyticsAPI } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts'

const mockGrowth = Array.from({ length: 8 }, (_, i) => ({ week: `W${i + 1}`, users: 20 + i * 8 + Math.floor(Math.random() * 10) }))
const mockTraffic = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map(d => ({ day: d, visits: Math.floor(Math.random() * 400) + 100 }))

export default function Analytics() {
  const [dashboard, setDashboard] = useState(null)
  const [growth, setGrowth] = useState(mockGrowth)
  const [traffic, setTraffic] = useState(mockTraffic)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      analyticsAPI.getDashboard(),
      analyticsAPI.getUsersGrowth(),
      analyticsAPI.getTrafficOverview(),
    ]).then(([d, g, t]) => {
      if (d.status === 'fulfilled') setDashboard(d.value.data)
      if (g.status === 'fulfilled' && g.value.data?.length) setGrowth(g.value.data)
      if (t.status === 'fulfilled' && t.value.data?.length) setTraffic(t.value.data)
    }).finally(() => setLoading(false))
  }, [])

  const tooltipStyle = { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }

  return (
    <div>
      <div className="grid-4" style={{ marginBottom: 20 }}>
        {[
          { label: 'Total Users', value: dashboard?.total_users ?? '—' },
          { label: 'Active Users', value: dashboard?.active_users ?? '—' },
          { label: 'Total Transactions', value: dashboard?.total_transactions ?? '—' },
          { label: 'Platform Uptime', value: dashboard?.api_uptime ? `${dashboard.api_uptime}%` : '99.9%' },
        ].map(({ label, value }) => (
          <div className="stat-card" key={label}>
            <div className="stat-label">{label}</div>
            <div className="stat-value">{value}</div>
          </div>
        ))}
      </div>

      <div className="grid-2" style={{ marginBottom: 20 }}>
        <div className="card">
          <div className="card-header"><span className="card-title">User Growth</span></div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={growth}>
              <CartesianGrid stroke="rgba(255,255,255,0.04)" vertical={false} />
              <XAxis dataKey="week" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey="users" stroke="var(--accent-2)" strokeWidth={2} dot={{ fill: 'var(--accent-2)', r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-header"><span className="card-title">Daily Traffic</span></div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={traffic} barSize={28}>
              <XAxis dataKey="day" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="visits" fill="var(--accent)" radius={[4, 4, 0, 0]} fillOpacity={0.8} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {dashboard && (
        <div className="card">
          <div className="card-header"><span className="card-title">Platform Health</span></div>
          <div className="grid-4">
            {[
              { label: 'Total Volume', value: dashboard.total_volume ? `$${Number(dashboard.total_volume).toLocaleString()}` : '—' },
              { label: 'Fraud Attempts', value: dashboard.fraud_attempts ?? 0, color: 'var(--danger)' },
              { label: 'Fraud Blocked', value: dashboard.fraud_blocked ?? 0, color: 'var(--success)' },
              { label: 'Avg Response', value: dashboard.avg_response_time ? `${dashboard.avg_response_time}ms` : '—' },
            ].map(({ label, value, color }) => (
              <div key={label} style={{ textAlign: 'center', padding: '12px 0' }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>{label}</div>
                <div style={{ fontFamily: 'Syne', fontSize: 22, fontWeight: 700, color: color || 'var(--text-primary)' }}>{value}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
