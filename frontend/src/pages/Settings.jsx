import { useState } from 'react'
import { Bell, Shield, Eye, EyeOff, Moon, Globe, Save } from 'lucide-react'

export default function Settings() {
  const [settings, setSettings] = useState({
    emailNotifications: true,
    tradeAlerts: true,
    priceAlerts: false,
    securityAlerts: true,
    twoFactor: false,
    darkMode: true,
    language: 'en',
    currency: 'USD',
  })
  const [saved, setSaved] = useState(false)

  const toggle = key => setSettings(s => ({ ...s, [key]: !s[key] }))
  const save = () => { setSaved(true); setTimeout(() => setSaved(false), 2000) }

  const Toggle = ({ k }) => (
    <div onClick={() => toggle(k)} style={{ width: 44, height: 24, borderRadius: 12, background: settings[k] ? 'var(--accent)' : 'var(--border)', cursor: 'pointer', position: 'relative', transition: 'all 0.2s', flexShrink: 0 }}>
      <div style={{ width: 18, height: 18, borderRadius: '50%', background: '#fff', position: 'absolute', top: 3, left: settings[k] ? 23 : 3, transition: 'left 0.2s' }} />
    </div>
  )

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      {saved && <div className="msg msg-success" style={{ marginBottom: 16 }}>Settings saved successfully!</div>}

      {[
        {
          title: 'Notifications', icon: Bell,
          items: [
            { key: 'emailNotifications', label: 'Email notifications', desc: 'Receive updates via email' },
            { key: 'tradeAlerts', label: 'Trade alerts', desc: 'Get notified on buy/sell orders' },
            { key: 'priceAlerts', label: 'Price alerts', desc: 'Alerts when stocks hit target price' },
            { key: 'securityAlerts', label: 'Security alerts', desc: 'Login and security notifications' },
          ]
        },
        {
          title: 'Security', icon: Shield,
          items: [
            { key: 'twoFactor', label: 'Two-factor authentication', desc: 'Extra security on login' },
          ]
        },
        {
          title: 'Preferences', icon: Globe,
          items: [
            { key: 'darkMode', label: 'Dark mode', desc: 'Use dark color theme' },
          ]
        },
      ].map(({ title, icon: Icon, items }) => (
        <div className="card" key={title} style={{ marginBottom: 16 }}>
          <div className="card-header">
            <span className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Icon size={16} style={{ color: 'var(--accent)' }} /> {title}
            </span>
          </div>
          {items.map(({ key, label, desc }) => (
            <div key={key} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 0', borderBottom: '1px solid var(--border-light)' }}>
              <div>
                <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-primary)', marginBottom: 2 }}>{label}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{desc}</div>
              </div>
              <Toggle k={key} />
            </div>
          ))}
        </div>
      ))}

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-header"><span className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}><Globe size={16} style={{ color: 'var(--accent)' }} /> Regional</span></div>
        <div style={{ display: 'grid', gap: 12 }}>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Language</label>
            <select value={settings.language} onChange={e => setSettings(s => ({ ...s, language: e.target.value }))}>
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="es">Spanish</option>
            </select>
          </div>
          <div className="form-group" style={{ margin: 0 }}>
            <label className="form-label">Currency</label>
            <select value={settings.currency} onChange={e => setSettings(s => ({ ...s, currency: e.target.value }))}>
              <option value="USD">USD ($)</option>
              <option value="INR">INR (₹)</option>
              <option value="EUR">EUR (€)</option>
            </select>
          </div>
        </div>
      </div>

      <button className="btn btn-primary" style={{ width: '100%' }} onClick={save}>
        <Save size={14} /> Save Settings
      </button>
    </div>
  )
}
