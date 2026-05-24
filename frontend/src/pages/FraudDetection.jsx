import { useState } from 'react'
import { ShieldAlert, Shield, AlertTriangle, CheckCircle, Eye, Lock } from 'lucide-react'

const MOCK_ALERTS = [
  { id: 1, type: 'warning', title: 'Unusual Login Location', desc: 'Login attempt from Mumbai, India at 2:34 AM', time: '2 hours ago', status: 'active' },
  { id: 2, type: 'info', title: 'New Device Detected', desc: 'Chrome on Windows — not your usual device', time: '1 day ago', status: 'resolved' },
  { id: 3, type: 'success', title: 'Transaction Verified', desc: 'Purchase of $1,924 AAPL — confirmed by you', time: '2 days ago', status: 'resolved' },
]

export default function FraudDetection() {
  const [alerts, setAlerts] = useState(MOCK_ALERTS)
  const [score] = useState(92)

  const dismiss = (id) => setAlerts(a => a.filter(x => x.id !== id))

  const scoreColor = score >= 80 ? 'var(--success)' : score >= 60 ? 'var(--warning)' : 'var(--danger)'

  return (
    <div>
      <div className="grid-4" style={{ marginBottom: 20 }}>
        {[
          { label: 'Security Score', value: `${score}/100`, color: scoreColor, icon: Shield },
          { label: 'Active Alerts', value: alerts.filter(a => a.status === 'active').length, color: 'var(--warning)', icon: AlertTriangle },
          { label: 'Blocked Attempts', value: 3, color: 'var(--danger)', icon: ShieldAlert },
          { label: 'Transactions Safe', value: '100%', color: 'var(--success)', icon: CheckCircle },
        ].map(({ label, value, color, icon: Icon }) => (
          <div className="stat-card" key={label}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
              <Icon size={16} style={{ color }} />
              <div className="stat-label">{label}</div>
            </div>
            <div className="stat-value" style={{ color }}>{value}</div>
          </div>
        ))}
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header"><span className="card-title">Security Score</span></div>
          <div style={{ textAlign: 'center', padding: '20px 0' }}>
            <div style={{ position: 'relative', width: 140, height: 140, margin: '0 auto 16px' }}>
              <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                <circle cx="18" cy="18" r="15.915" fill="none" stroke="var(--border)" strokeWidth="2.5" />
                <circle cx="18" cy="18" r="15.915" fill="none" stroke={scoreColor} strokeWidth="2.5"
                  strokeDasharray={`${score} ${100 - score}`} strokeLinecap="round" />
              </svg>
              <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }}>
                <div style={{ fontSize: 28, fontWeight: 700, color: scoreColor }}>{score}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>/ 100</div>
              </div>
            </div>
            <div style={{ fontSize: 16, fontWeight: 600, color: scoreColor, marginBottom: 4 }}>
              {score >= 80 ? 'Excellent' : score >= 60 ? 'Good' : 'Needs Attention'}
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Your account is well protected</div>
          </div>
          <div style={{ display: 'grid', gap: 10 }}>
            {[
              { label: '2FA Enabled', done: false },
              { label: 'Strong Password', done: true },
              { label: 'Email Verified', done: true },
              { label: 'Suspicious Activity Off', done: true },
            ].map(({ label, done }) => (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 13 }}>
                {done ? <CheckCircle size={15} style={{ color: 'var(--success)', flexShrink: 0 }} /> : <AlertTriangle size={15} style={{ color: 'var(--warning)', flexShrink: 0 }} />}
                <span style={{ color: done ? 'var(--text-primary)' : 'var(--warning)' }}>{label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Security Alerts</span>
            <span className="badge badge-warning">{alerts.filter(a => a.status === 'active').length} active</span>
          </div>
          {alerts.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
              <Shield size={32} style={{ marginBottom: 8, opacity: 0.3 }} />
              <p style={{ fontSize: 13 }}>No alerts — all clear!</p>
            </div>
          ) : alerts.map(a => (
            <div key={a.id} style={{ padding: '12px 0', borderBottom: '1px solid var(--border-light)' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: a.type === 'warning' ? 'var(--warning-bg)' : a.type === 'success' ? 'var(--success-bg)' : 'var(--info-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  {a.type === 'warning' ? <AlertTriangle size={14} style={{ color: 'var(--warning)' }} /> : a.type === 'success' ? <CheckCircle size={14} style={{ color: 'var(--success)' }} /> : <Eye size={14} style={{ color: 'var(--info)' }} />}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{a.title}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>{a.desc}</div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{a.time}</div>
                </div>
                {a.status === 'active' && (
                  <button className="btn btn-ghost btn-sm" onClick={() => dismiss(a.id)} style={{ fontSize: 11 }}>Dismiss</button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
