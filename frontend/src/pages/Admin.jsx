import { useEffect, useState } from 'react'
import { adminAPI } from '../services/api'
import { Shield, UserCheck, UserX, RefreshCw } from 'lucide-react'

export default function Admin() {
  const [users, setUsers] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [msg, setMsg] = useState('')

  const load = () => {
    setLoading(true)
    Promise.allSettled([adminAPI.getUsers(), adminAPI.getPlatformStats()])
      .then(([u, s]) => {
        if (u.status === 'fulfilled') setUsers(u.value.data || [])
        if (s.status === 'fulfilled') setStats(s.value.data)
      }).finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleSuspend = async (id) => {
    try { await adminAPI.suspendUser(id); setMsg('User suspended'); load() }
    catch { setMsg('Action failed') }
    setTimeout(() => setMsg(''), 3000)
  }

  const handleActivate = async (id) => {
    try { await adminAPI.activateUser(id); setMsg('User activated'); load() }
    catch { setMsg('Action failed') }
    setTimeout(() => setMsg(''), 3000)
  }

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 24 }}>
        <Shield size={20} style={{ color: 'var(--accent)' }} />
        <h2 style={{ fontFamily: 'Syne', fontSize: 18, fontWeight: 700 }}>Admin Panel</h2>
        <span className="badge badge-danger">Restricted</span>
      </div>

      {msg && <div className="msg msg-success" style={{ marginBottom: 16 }}>{msg}</div>}

      {/* Platform stats */}
      {stats && (
        <div className="grid-4" style={{ marginBottom: 20 }}>
          {[
            { label: 'Total Users', value: stats.total_users },
            { label: 'Active Users', value: stats.active_users },
            { label: 'Fraud Attempts', value: stats.fraud_attempts, color: 'var(--danger)' },
            { label: 'Daily Signups', value: stats.daily_signups, color: 'var(--success)' },
          ].map(({ label, value, color }) => (
            <div className="stat-card" key={label}>
              <div className="stat-label">{label}</div>
              <div className="stat-value" style={color ? { color } : {}}>{value ?? '—'}</div>
            </div>
          ))}
        </div>
      )}

      {/* Users table */}
      <div className="card">
        <div className="card-header">
          <span className="card-title">User Management</span>
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
                  <th>Name</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Joined</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map(u => (
                  <tr key={u.id}>
                    <td className="mono" style={{ color: 'var(--text-muted)' }}>{u.id}</td>
                    <td style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{u.full_name}</td>
                    <td className="mono" style={{ fontSize: 12 }}>{u.email}</td>
                    <td><span className={`badge ${u.is_admin ? 'badge-warning' : 'badge-muted'}`}>{u.is_admin ? 'ADMIN' : 'USER'}</span></td>
                    <td><span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'}`}>{u.is_active ? 'ACTIVE' : 'SUSPENDED'}</span></td>
                    <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{new Date(u.created_at).toLocaleDateString()}</td>
                    <td>
                      <div style={{ display: 'flex', gap: 6 }}>
                        {u.is_active
                          ? <button className="btn btn-danger btn-sm" onClick={() => handleSuspend(u.id)}><UserX size={11} /> Suspend</button>
                          : <button className="btn btn-success btn-sm" onClick={() => handleActivate(u.id)}><UserCheck size={11} /> Activate</button>
                        }
                      </div>
                    </td>
                  </tr>
                ))}
                {users.length === 0 && (
                  <tr><td colSpan={7} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>No users found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
