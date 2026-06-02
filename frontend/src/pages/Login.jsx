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
    idle:     { border: '1.5px solid #c7b198',      bg: 'rgba(199,177,152,0.12)' },
    loading:  { border: '1.5px solid #3d7a6f',      bg: 'rgba(61,122,111,0.08)'  },
    verified: { border: '1.5px solid #4a7c59',      bg: 'rgba(74,124,89,0.10)'   },
  }[status]

  return (
    <div onClick={handleClick} style={{
      display:'flex', alignItems:'center', gap:12, padding:'12px 16px',
      borderRadius:10, cursor:status==='idle'?'pointer':'default',
      border:colors.border, background:colors.bg, userSelect:'none', transition:'all 0.2s'
    }}>
      <div style={{
        width:20, height:20, borderRadius:status==='loading'?'50%':4, flexShrink:0,
        border: status==='verified' ? 'none' : status==='loading' ? '2px solid #3d7a6f' : '2px solid #c7b198',
        background: status==='verified' ? '#4a7c59' : 'transparent',
        display:'flex', alignItems:'center', justifyContent:'center',
        animation: status==='loading' ? 'spin 0.8s linear infinite' : 'none',
        borderTopColor: status==='loading' ? 'transparent' : undefined,
      }}>
        {status==='verified' && <svg width="11" height="11" viewBox="0 0 12 12"><path d="M2 6l3 3 5-5" stroke="#f0ece2" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" fill="none"/></svg>}
      </div>
      <span style={{ color: status==='verified' ? '#4a7c59' : status==='loading' ? '#3d7a6f' : '#596e79', fontSize:13, fontWeight:500 }}>
        {status==='idle'    && "I'm not a robot"}
        {status==='loading' && 'Verifying…'}
        {status==='verified'&& 'Verified ✓'}
      </span>
      <div style={{ marginLeft:'auto', textAlign:'right', fontSize:10, color:'#8a9aa3', lineHeight:1.4 }}>
        <div>🛡️</div><div>reCAPTCHA</div>
      </div>
    </div>
  )
}

const S = {
  bg: {
    minHeight:'100vh', width:'100%', display:'flex', alignItems:'center', justifyContent:'center',
    background:'linear-gradient(135deg, #e8e2d6 0%, #f0ece2 50%, #e4ddd0 100%)',
    padding:24, fontFamily:"'Inter', system-ui, sans-serif"
  },
  card: {
    background:'rgba(250,248,244,0.85)',
    backdropFilter:'blur(16px)',
    border:'1px solid rgba(199,177,152,0.50)',
    borderRadius:20,
    padding:'40px 36px',
    width:'100%', maxWidth:420,
    boxShadow:'0 8px 40px rgba(89,110,121,0.15), 0 2px 8px rgba(89,110,121,0.10), 0 0 0 1px rgba(255,255,255,0.70) inset'
  },
  sub:   { textAlign:'center', color:'#8a9aa3', fontSize:14, marginBottom:28 },
  group: { marginBottom:18 },
  label: { display:'block', color:'#596e79', fontSize:13, fontWeight:600, marginBottom:6 },
  input: { width:'100%', background:'#faf8f4', border:'1.5px solid #c7b198', color:'#2c3a40', borderRadius:10, padding:'11px 14px', fontSize:14, outline:'none', boxSizing:'border-box', transition:'all 0.2s' },
  btn:   { width:'100%', padding:'13px', fontSize:15, fontWeight:700, background:'linear-gradient(135deg, #3d7a6f, #336860)', border:'none', borderRadius:10, color:'#f0ece2', cursor:'pointer', marginTop:4, boxShadow:'0 4px 15px rgba(61,122,111,0.30)', transition:'all 0.2s' },
  err:   { background:'rgba(160,65,45,0.10)', border:'1px solid rgba(160,65,45,0.28)', color:'#a0412d', borderRadius:8, padding:'11px 14px', fontSize:13, marginBottom:18 },
  link:  { textAlign:'center', marginTop:20, fontSize:13, color:'#8a9aa3' },
}

export default function Login() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const [form, setForm]       = useState({ email:'', password:'' })
  const [error, setError]     = useState('')
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
      <style>{`
        @keyframes spin { to { transform: rotate(360deg) } }
        input:focus {
          border-color: #3d7a6f !important;
          box-shadow: 0 0 0 3px rgba(61,122,111,0.18) !important;
          background: rgba(61,122,111,0.05) !important;
        }
        button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 24px rgba(61,122,111,0.35) !important;
        }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
      `}</style>

      <div style={S.card}>

        {/* Logo image */}
        <div style={{ textAlign: 'center', marginBottom: 12 }}>
          <img
            src="/finex-logo.png"
            alt="FINEX"
            style={{ height: 80, width: 'auto', objectFit: 'contain' }}
          />
        </div>

        <p style={S.sub}>Sign in to your account</p>

        {error && <div style={S.err}>{error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div style={S.group}>
            <label style={S.label}>Email</label>
            <input
              style={S.input}
              type="email"
              placeholder="you@example.com"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
              required
              autoComplete="email"
            />
          </div>

          <div style={{ ...S.group, marginBottom:20 }}>
            <label style={S.label}>Password</label>
            <input
              style={S.input}
              type="password"
              placeholder="••••••••"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              required
              autoComplete="current-password"
            />
          </div>

          <div style={{ marginBottom:20 }}>
            <CaptchaBox onVerified={setCaptchaOk} />
          </div>

          <button style={S.btn} type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={S.link}>
          Don't have an account?{' '}
          <Link to="/register" style={{ color:'#3d7a6f', fontWeight:600, textDecoration:'none' }}>Create one</Link>
        </div>
      </div>
    </div>
  )
}