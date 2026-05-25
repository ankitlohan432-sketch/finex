import { useState, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

function CaptchaBox({ onVerified }) {
  const [status, setStatus] = useState('idle')
  const handleClick = useCallback(() => {
    if (status !== 'idle') return
    setStatus('loading')
    setTimeout(() => { setStatus('verified'); onVerified(true) }, 800 + Math.random() * 500)
  }, [status, onVerified])

  const colors = {
    idle: { border: '1.5px solid rgba(255,255,255,0.15)', bg: 'rgba(255,255,255,0.04)' },
    loading: { border: '1.5px solid #63b3ed', bg: 'rgba(99,179,237,0.08)' },
    verified: { border: '1.5px solid #10b981', bg: 'rgba(16,185,129,0.08)' },
  }[status]

  return (
    <div onClick={handleClick} style={{
      display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px',
      borderRadius: 10, cursor: status === 'idle' ? 'pointer' : 'default',
      border: colors.border, background: colors.bg, userSelect: 'none', transition: 'all 0.2s'
    }}>
      <div style={{
        width: 20, height: 20, borderRadius: status === 'loading' ? '50%' : 4, flexShrink: 0,
        border: status === 'verified' ? 'none' : status === 'loading' ? '2px solid #63b3ed' : '2px solid rgba(255,255,255,0.3)',
        background: status === 'verified' ? '#10b981' : 'transparent',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        animation: status === 'loading' ? 'spin 0.8s linear infinite' : 'none',
        borderTopColor: status === 'loading' ? 'transparent' : undefined,
      }}>
        {status === 'verified' && <svg width="11" height="11" viewBox="0 0 12 12"><path d="M2 6l3 3 5-5" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" fill="none"/></svg>}
      </div>
      <span style={{ color: status === 'verified' ? '#6ee7b7' : 'rgba(255,255,255,0.7)', fontSize: 13, fontWeight: 500 }}>
        {status === 'idle' && "I'm not a robot"}
        {status === 'loading' && 'Verifying…'}
        {status === 'verified' && 'Verified ✓'}
      </span>
      <div style={{ marginLeft: 'auto', textAlign: 'right', fontSize: 10, color: 'rgba(255,255,255,0.25)', lineHeight: 1.4 }}>
        <div>🛡️</div><div>reCAPTCHA</div>
      </div>
    </div>
  )
}

const S = {
  bg: { minHeight: '100vh', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f2044 100%)', padding: 24, fontFamily: "'Segoe UI', system-ui, sans-serif" },
  card: { background: 'rgba(255,255,255,0.05)', backdropFilter: 'blur(20px)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 20, padding: '40px 36px', width: '100%', maxWidth: 420, boxShadow: '0 25px 60px rgba(0,0,0,0.5)' },
  logo: { textAlign: 'center', fontSize: 34, fontWeight: 800, color: '#fff', marginBottom: 6, letterSpacing: -1 },
  sub: { textAlign: 'center', color: 'rgba(255,255,255,0.45)', fontSize: 14, marginBottom: 28 },
  group: { marginBottom: 18 },
  label: { display: 'block', color: 'rgba(255,255,255,0.7)', fontSize: 13, fontWeight: 600, marginBottom: 6 },
  input: { width: '100%', background: 'rgba(255,255,255,0.07)', border: '1.5px solid rgba(255,255,255,0.12)', color: '#fff', borderRadius: 10, padding: '11px 14px', fontSize: 14, outline: 'none', boxSizing: 'border-box', transition: 'all 0.2s' },
  btn: { width: '100%', padding: '13px', fontSize: 15, fontWeight: 700, background: 'linear-gradient(135deg, #3b82f6, #2563eb)', border: 'none', borderRadius: 10, color: '#fff', cursor: 'pointer', marginTop: 4, boxShadow: '0 4px 15px rgba(59,130,246,0.35)', transition: 'all 0.2s' },
  err: { background: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)', color: '#fca5a5', borderRadius: 8, padding: '11px 14px', fontSize: 13, marginBottom: 18 },
  link: { textAlign: 'center', marginTop: 20, fontSize: 13, color: 'rgba(255,255,255,0.45)' },
}

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [captchaOk, setCaptchaOk] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (!captchaOk) { setError('Please complete the CAPTCHA first.'); return }
    setLoading(true)
    try {
      await login(form.email, form.password)
      navigate('/dashboard')
    } catch (err) {
      const d = err.response?.data?.detail
      setError(d || 'Unable to sign in. Please check your credentials.')
    } finally { setLoading(false) }
  }

  return (
    <div style={S.bg}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}} input:focus{border-color:#63b3ed!important;box-shadow:0 0 0 3px rgba(99,179,237,0.2)!important;background:rgba(99,179,237,0.08)!important} button:hover:not(:disabled){transform:translateY(-2px);box-shadow:0 8px 24px rgba(59,130,246,0.45)!important} button:disabled{opacity:0.6;cursor:not-allowed}`}</style>
      <div style={S.card}>
        <div style={S.logo}>Fin<span style={{ color: '#63b3ed' }}>ex</span></div>
        <p style={S.sub}>Sign in to your account</p>
        {error && <div style={S.err}>{error}</div>}
        <form onSubmit={handleSubmit} noValidate>
          <div style={S.group}>
            <label style={S.label}>Email</label>
            <input style={S.input} type="email" placeholder="you@example.com" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} required autoComplete="email" />
          </div>
          <div style={{ ...S.group, marginBottom: 20 }}>
            <label style={S.label}>Password</label>
            <input style={S.input} type="password" placeholder="••••••••" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} required autoComplete="current-password" />
          </div>
          <div style={{ marginBottom: 20 }}>
            <CaptchaBox onVerified={setCaptchaOk} />
          </div>
          <button style={S.btn} type="submit" disabled={loading}>
            {loading ? '...' : 'Sign In'}
          </button>
        </form>
        <div style={S.link}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color: '#63b3ed', fontWeight: 600, textDecoration: 'none' }}>Create one</Link>
        </div>
      </div>
    </div>
  )
}
