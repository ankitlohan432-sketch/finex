import { useState } from 'react'
import { BarChart3, TrendingUp, TrendingDown, AlertTriangle, Shield } from 'lucide-react'
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts'

const radarData = [
  { metric: 'Diversification', value: 65 },
  { metric: 'Volatility', value: 45 },
  { metric: 'Liquidity', value: 80 },
  { metric: 'Credit Risk', value: 70 },
  { metric: 'Market Risk', value: 55 },
  { metric: 'Growth', value: 75 },
]

const sectorData = [
  { name: 'Tech', value: 45, color: '#00e5ff' },
  { name: 'Finance', value: 20, color: '#00e5a0' },
  { name: 'Health', value: 15, color: '#f6c90e' },
  { name: 'Energy', value: 12, color: '#fc8181' },
  { name: 'Other', value: 8, color: '#b794f4' },
]

export default function RiskAnalysis() {
  const [riskLevel] = useState('Moderate')

  const riskColor = { Low: 'var(--success)', Moderate: 'var(--warning)', High: 'var(--danger)' }[riskLevel]

  return (
    <div>
      <div className="grid-4" style={{ marginBottom: 20 }}>
        {[
          { label: 'Risk Level', value: riskLevel, color: riskColor },
          { label: 'Beta', value: '1.24', color: 'var(--warning)' },
          { label: 'Sharpe Ratio', value: '0.87', color: 'var(--success)' },
          { label: 'Max Drawdown', value: '-12.4%', color: 'var(--danger)' },
        ].map(({ label, value, color }) => (
          <div className="stat-card" key={label}>
            <div className="stat-label">{label}</div>
            <div className="stat-value" style={{ color }}>{value}</div>
          </div>
        ))}
      </div>

      <div className="grid-2" style={{ marginBottom: 20 }}>
        <div className="card">
          <div className="card-header"><span className="card-title">Risk Profile Radar</span></div>
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="var(--border)" />
              <PolarAngleAxis dataKey="metric" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
              <Radar dataKey="value" stroke="var(--accent)" fill="var(--accent)" fillOpacity={0.15} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <div className="card-header"><span className="card-title">Sector Exposure</span></div>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={sectorData} barSize={32}>
              <XAxis dataKey="name" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} formatter={v => [`${v}%`]} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {sectorData.map((entry, i) => <Cell key={i} fill={entry.color} fillOpacity={0.8} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="card-header"><span className="card-title">Risk Recommendations</span></div>
        <div style={{ display: 'grid', gap: 12 }}>
          {[
            { icon: AlertTriangle, color: 'var(--warning)', title: 'High Tech Concentration', desc: '45% in technology sector. Consider diversifying into other sectors to reduce concentration risk.' },
            { icon: TrendingUp, color: 'var(--success)', title: 'Good Liquidity', desc: 'Your portfolio has 80% liquidity score. You can easily convert holdings to cash.' },
            { icon: Shield, color: 'var(--info)', title: 'Add Defensive Stocks', desc: 'Consider adding healthcare or utilities for stability during market downturns.' },
            { icon: BarChart3, color: 'var(--accent)', title: 'Rebalance Quarterly', desc: 'Your portfolio drifted from target allocation. Schedule a quarterly rebalancing.' },
          ].map(({ icon: Icon, color, title, desc }) => (
            <div key={title} style={{ display: 'flex', gap: 14, padding: '14px', borderRadius: 10, background: 'var(--bg-secondary)', border: '1px solid var(--border-light)' }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: `rgba(0,0,0,0.2)`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Icon size={16} style={{ color }} />
              </div>
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>{title}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
