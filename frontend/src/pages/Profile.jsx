import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { userAPI } from '../services/api'
import { User, Mail, Phone, Shield, Edit2, Check, X } from 'lucide-react'

export default function Profile() {
  const { user, login } = useAuth()
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({ full_name: user?.full_name || '', phone: user?.phone || '' })
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(false)

  const initials = user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'FX'

  const save = async () => {
    setLoading(true)
    try {
      await userAPI.updateMe(form)
      setMsg('Profile updated successfully!')
      setEditing(false)
    } catch { setMsg('Failed to update profile.') }
    finally { setLoading(false); setTimeout(() => setMsg(''), 3000) }
  }

  return (
    <div style={{ maxWidth: 600, margin: '0 auto' }}>
      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 24 }}>
          <div style={{ width: 72, height: 72, borderRadius: '50%', background: 'var(--accent)', color: '#001f24', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, fontWeight: 700 }}>
            {initials}
          </div>
          <div>
            <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>{user?.full_name}</div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>{user?.is_admin ? 'Administrator' : 'Investor'}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 6 }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: user?.is_verified ? 'var(--success)' : 'var(--warning)' }} />
              <span style={{ fontSize: 12, color: user?.is_verified ? 'var(--success)' : 'var(--warning)' }}>
                {user?.is_verified ? 'Verified' : 'Unverified'}
              </span>
            </div>
          </div>
          <button className="btn btn-ghost btn-sm" style={{ marginLeft: 'auto' }} onClick={() => setEditing(!editing)}>
            {editing ? <X size={14} /> : <Edit2 size={14} />}
            {editing ? 'Cancel' : 'Edit'}
          </button>
        </div>

        {msg && <div className={`msg ${msg.includes('success') ? 'msg-success' : 'msg-error'}`} style={{ marginBottom: 16 }}>{msg}</div>}

        <div style={{ display: 'grid', gap: 16 }}>
          {[
            { icon: User, label: 'Full Name', field: 'full_name', value: user?.full_name },
            { icon: Mail, label: 'Email', field: 'email', value: user?.email, readonly: true },
            { icon: Phone, label: 'Phone', field: 'phone', value: user?.phone || '—' },
          ].map(({ icon: Icon, label, field, value, readonly }) => (
            <div key={field} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '14px 0', borderBottom: '1px solid var(--border-light)' }}>
              <div style={{ width: 36, height: 36, borderRadius: 10, background: 'var(--accent-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Icon size={16} style={{ color: 'var(--accent)' }} />
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 3, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{label}</div>
                {editing && !readonly ? (
                  <input className="form-input" value={form[field] || ''} onChange={e => setForm({ ...form, [field]: e.target.value })} style={{ padding: '6px 10px', fontSize: 13 }} />
                ) : (
                  <div style={{ fontSize: 14, color: 'var(--text-primary)', fontWeight: 500 }}>{value}</div>
                )}
              </div>
            </div>
          ))}
        </div>

        {editing && (
          <button className="btn btn-primary" style={{ width: '100%', marginTop: 16 }} onClick={save} disabled={loading}>
            <Check size={14} /> {loading ? 'Saving...' : 'Save Changes'}
          </button>
        )}
      </div>

      <div className="card">
        <div className="card-header"><span className="card-title">Account Details</span></div>
        <div style={{ display: 'grid', gap: 12 }}>
          {[
            { label: 'Member Since', value: user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '—' },
            { label: 'Last Login', value: user?.last_login ? new Date(user.last_login).toLocaleString() : '—' },
            { label: 'Account Status', value: user?.is_active ? 'Active' : 'Inactive', color: user?.is_active ? 'var(--success)' : 'var(--danger)' },
            { label: 'Account Type', value: user?.is_admin ? 'Administrator' : 'Standard Investor' },
          ].map(({ label, value, color }) => (
            <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid var(--border-light)' }}>
              <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{label}</span>
              <span style={{ fontSize: 13, fontWeight: 500, color: color || 'var(--text-primary)' }}>{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
