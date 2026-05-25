import { useState } from 'react'
import { Bug, Send, CheckCircle } from 'lucide-react'

export default function Report() {
  const [form, setForm] = useState({ type: 'bug', title: '', desc: '', priority: 'medium' })
  const [done, setDone] = useState(false)
  const [loading, setLoading] = useState(false)
  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = () => {
    if (!form.title || !form.desc) return
    setLoading(true)
    setTimeout(() => { setLoading(false); setDone(true) }, 1200)
  }

  if (done) return (
    <div style={{ maxWidth: 480, margin: '60px auto', textAlign: 'center' }}>
      <div className="card">
        <CheckCircle size={48} style={{ color: 'var(--success)', marginBottom: 12 }} />
        <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>Report Submitted!</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 20 }}>Our team will review your report within 24 hours. Thank you for helping us improve!</p>
        <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => { setDone(false); setForm({ type: 'bug', title: '', desc: '', priority: 'medium' }) }}>Submit Another</button>
      </div>
    </div>
  )

  return (
    <div style={{ maxWidth: 560, margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <div style={{ width: 44, height: 44, borderRadius: 12, background: 'var(--danger-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Bug size={22} style={{ color: 'var(--danger)' }} />
        </div>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>Report an Issue</h2>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Help us improve by reporting bugs or problems</p>
        </div>
      </div>

      <div className="card">
        <div className="form-group">
          <label className="form-label">Issue Type</label>
          <select value={form.type} onChange={set('type')}>
            <option value="bug">Bug / Error</option>
            <option value="fraud">Suspicious Activity</option>
            <option value="payment">Payment Issue</option>
            <option value="account">Account Problem</option>
            <option value="feature">Feature Request</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Priority</label>
          <select value={form.priority} onChange={set('priority')}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High — Urgent</option>
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Issue Title</label>
          <input className="form-input" placeholder="Brief description of the issue" value={form.title} onChange={set('title')} />
        </div>
        <div className="form-group">
          <label className="form-label">Detailed Description</label>
          <textarea className="form-input" rows={5} placeholder="Describe what happened, when it occurred, and what you expected..." value={form.desc} onChange={set('desc')} style={{ resize: 'vertical' }} />
        </div>
        <button className="btn btn-primary" style={{ width: '100%' }} onClick={submit} disabled={!form.title || !form.desc || loading}>
          <Send size={14} /> {loading ? 'Submitting...' : 'Submit Report'}
        </button>
      </div>
    </div>
  )
}
