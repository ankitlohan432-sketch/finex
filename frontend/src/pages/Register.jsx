import { useState, useCallback, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authAPI } from '../services/api'
import { useAuth } from '../context/AuthContext'

function CaptchaBox({ onVerified }) {
  const [status, setStatus] = useState('idle')
  const handleClick = useCallback(() => {
    if (status !== 'idle') return
    setStatus('loading')
    setTimeout(() => { setStatus('verified'); onVerified(true) }, 800 + Math.random() * 500)
  }, [status, onVerified])

  const border = status === 'verified' ? '1.5px solid #4a7c59' : status === 'loading' ? '1.5px solid #3d7a6f' : '1.5px solid #c7b198'
  const bg     = status === 'verified' ? 'rgba(74,124,89,0.10)' : status === 'loading' ? 'rgba(61,122,111,0.08)' : 'rgba(199,177,152,0.12)'

  return (
    <div onClick={handleClick} style={{ display:'flex',alignItems:'center',gap:12,padding:'12px 16px',borderRadius:10,cursor:status==='idle'?'pointer':'default',border,background:bg,userSelect:'none',transition:'all 0.2s' }}>
      <div style={{ width:20,height:20,borderRadius:status==='loading'?'50%':4,flexShrink:0,border:status==='verified'?'none':status==='loading'?'2px solid #3d7a6f':'2px solid #c7b198',background:status==='verified'?'#4a7c59':'transparent',display:'flex',alignItems:'center',justifyContent:'center',animation:status==='loading'?'spin 0.8s linear infinite':'none' }}>
        {status==='verified'&&<svg width="11" height="11" viewBox="0 0 12 12"><path d="M2 6l3 3 5-5" stroke="#f0ece2" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" fill="none"/></svg>}
      </div>
      <span style={{ color:status==='verified'?'#4a7c59':status==='loading'?'#3d7a6f':'#596e79',fontSize:13,fontWeight:500 }}>
        {status==='idle'&&"I'm not a robot"}{status==='loading'&&'Verifying...'}{status==='verified'&&'Verified ✓'}
      </span>
      <div style={{ marginLeft:'auto',textAlign:'right',fontSize:10,color:'#8a9aa3',lineHeight:1.4 }}>reCAPTCHA</div>
    </div>
  )
}

const S = {
  bg: {
    minHeight:'100vh',width:'100%',display:'flex',alignItems:'center',justifyContent:'center',
    background:'linear-gradient(135deg,#e8e2d6 0%,#f0ece2 50%,#e4ddd0 100%)',
    padding:24,fontFamily:"'Inter',system-ui,sans-serif"
  },
  card: {
    background:'rgba(250,248,244,0.85)',
    backdropFilter:'blur(16px)',
    border:'1px solid rgba(199,177,152,0.50)',
    borderRadius:20,
    padding:'40px 36px',
    width:'100%',maxWidth:420,
    boxShadow:'0 8px 40px rgba(89,110,121,0.15), 0 2px 8px rgba(89,110,121,0.10), 0 0 0 1px rgba(255,255,255,0.70) inset'
  },
  sub:  { textAlign:'center',color:'#8a9aa3',fontSize:14,marginBottom:28 },
  group:{ marginBottom:14 },
  label:{ display:'block',color:'#596e79',fontSize:13,fontWeight:600,marginBottom:6 },
  input:{ width:'100%',background:'#faf8f4',border:'1.5px solid #c7b198',color:'#2c3a40',borderRadius:10,padding:'11px 14px',fontSize:14,outline:'none',boxSizing:'border-box',transition:'all 0.2s' },
  btn:  { width:'100%',padding:'13px',fontSize:15,fontWeight:700,background:'linear-gradient(135deg,#3d7a6f,#336860)',border:'none',borderRadius:10,color:'#f0ece2',cursor:'pointer',marginTop:4,boxShadow:'0 4px 15px rgba(61,122,111,0.30)',transition:'all 0.2s' },
  btnGhost: { width:'100%',padding:'11px',fontSize:13,fontWeight:600,background:'transparent',border:'1px solid #c7b198',borderRadius:10,color:'#596e79',cursor:'pointer',marginTop:8,transition:'all 0.2s' },
  err:  { background:'rgba(160,65,45,0.10)',border:'1px solid rgba(160,65,45,0.28)',color:'#a0412d',borderRadius:8,padding:'11px 14px',fontSize:13,marginBottom:16 },
  success:{ background:'rgba(74,124,89,0.10)',border:'1px solid rgba(74,124,89,0.28)',color:'#4a7c59',borderRadius:8,padding:'11px 14px',fontSize:13,marginBottom:16,textAlign:'center' },
  link: { textAlign:'center',marginTop:20,fontSize:13,color:'#8a9aa3' },
}

// ── Logo component — reused in all screens ────────────────────────────────────
function FinexLogo() {
  return (
    <div style={{ textAlign: 'center', marginBottom: 12 }}>
      <img
        src="/finex-logo.png"
        alt="FINEX"
        style={{ height: 80, width: 'auto', objectFit: 'contain' }}
      />
    </div>
  )
}

// ── OTP Input: 6 individual boxes ─────────────────────────────────────────────
function OtpInput({ value, onChange }) {
  const inputs = useRef([])
  const digits = (value + '      ').slice(0, 6).split('')

  const handleKey = (i, e) => {
    if (e.key === 'Backspace') {
      const next = value.slice(0, i) + value.slice(i + 1)
      onChange(next)
      if (i > 0) inputs.current[i - 1]?.focus()
      return
    }
    if (!/^\d$/.test(e.key)) return
    const next = value.slice(0, i) + e.key + value.slice(i + 1)
    onChange(next.slice(0, 6))
    if (i < 5) inputs.current[i + 1]?.focus()
  }

  const handlePaste = (e) => {
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    onChange(pasted)
    inputs.current[Math.min(pasted.length, 5)]?.focus()
    e.preventDefault()
  }

  return (
    <div style={{ display:'flex',gap:10,justifyContent:'center',marginBottom:24 }}>
      {digits.map((d, i) => (
        <input
          key={i}
          ref={el => inputs.current[i] = el}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={d.trim()}
          onChange={() => {}}
          onKeyDown={e => handleKey(i, e)}
          onPaste={handlePaste}
          style={{
            width:48,height:56,textAlign:'center',fontSize:22,fontWeight:700,
            background:'#faf8f4',
            border: d.trim() ? '2px solid #3d7a6f' : '2px solid #c7b198',
            color:'#2c3a40',borderRadius:12,outline:'none',fontFamily:'monospace',
            boxShadow: d.trim() ? '0 0 0 3px rgba(61,122,111,0.15)' : 'none',
            transition:'all 0.15s'
          }}
        />
      ))}
    </div>
  )
}

// ── OTP Screen ────────────────────────────────────────────────────────────────
function OtpScreen({ email, onSuccess }) {
  const [otp, setOtp] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const [resendLoading, setResendLoading] = useState(false)
  const [resendMsg, setResendMsg] = useState('')
  const { login: ctxLogin } = useAuth()
  const navigate = useNavigate()

  const handleVerify = async () => {
    if (otp.length < 6) { setError('Please enter the full 6-digit code.'); return }
    setError('')
    setLoading(true)
    try {
      const res = await authAPI.verifyOtp({ email, otp })
      if (res.data?.access_token) {
        localStorage.setItem('token', res.data.access_token)
        setSuccess('✅ Email verified! Taking you to your dashboard...')
        setTimeout(() => navigate('/dashboard'), 1500)
      } else {
        setSuccess('✅ Verified! Redirecting to login...')
        setTimeout(() => navigate('/login', { state: { justRegistered: true, email } }), 1500)
      }
    } catch (err) {
      const d = err.response?.data?.detail
      setError(d || 'Verification failed. Please try again.')
    } finally { setLoading(false) }
  }

  const handleResend = async () => {
    setResendMsg(''); setError('')
    setResendLoading(true)
    try {
      await authAPI.resendOtp({ email })
      setResendMsg('✉️ New OTP sent! Check your inbox.')
      setOtp('')
    } catch (err) {
      const d = err.response?.data?.detail
      setError(d || 'Could not resend OTP. Please wait a moment.')
    } finally { setResendLoading(false) }
  }

  return (
    <div style={S.card}>
      {/* Logo */}
      <FinexLogo />
      <p style={S.sub}>Verify your email</p>

      <div style={{ textAlign:'center',marginBottom:20,padding:'14px',background:'rgba(61,122,111,0.08)',borderRadius:12,border:'1px solid rgba(61,122,111,0.22)' }}>
        <div style={{ fontSize:13,color:'#8a9aa3',marginBottom:4 }}>Code sent to</div>
        <div style={{ fontSize:15,fontWeight:700,color:'#3d7a6f' }}>{email}</div>
      </div>

      {error   && <div style={S.err}>{error}</div>}
      {success && <div style={S.success}>{success}</div>}
      {resendMsg && <div style={{ ...S.success,background:'rgba(61,122,111,0.08)',borderColor:'rgba(61,122,111,0.22)',color:'#3d7a6f' }}>{resendMsg}</div>}

      <div style={{ marginBottom:8 }}>
        <label style={{ ...S.label,textAlign:'center',display:'block',marginBottom:14 }}>Enter 6-digit code</label>
        <OtpInput value={otp} onChange={setOtp} />
      </div>

      <button style={S.btn} onClick={handleVerify} disabled={loading || otp.length < 6 || !!success}>
        {loading ? 'Verifying...' : 'Verify Email →'}
      </button>

      <button style={S.btnGhost} onClick={handleResend} disabled={resendLoading}>
        {resendLoading ? 'Sending...' : "Didn't get it? Resend OTP"}
      </button>

      <div style={{ ...S.link,marginTop:16 }}>
        Wrong email?{' '}
        <Link to="/register" style={{ color:'#3d7a6f',fontWeight:600,textDecoration:'none' }}>Go back</Link>
      </div>
    </div>
  )
}

// ── Register Screen ───────────────────────────────────────────────────────────
export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ full_name:'',email:'',phone:'',password:'',confirm:'' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [captchaOk, setCaptchaOk] = useState(false)
  const [otpEmail, setOtpEmail] = useState(null)
  const set = k => e => setForm({ ...form, [k]: e.target.value })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) { setError('Passwords do not match.'); return }
    if (form.password.length < 6) { setError('Password must be at least 6 characters.'); return }
    if (!captchaOk) { setError('Please complete the CAPTCHA first.'); return }
    setLoading(true)
    try {
      await authAPI.register({
        full_name: form.full_name,
        email: form.email,
        phone: form.phone || undefined,
        password: form.password
      })
      localStorage.removeItem('token')
      setOtpEmail(form.email)
    } catch (err) {
      const d = err.response?.data?.detail
      if (Array.isArray(d)) setError(d.map(x => x.msg).join('. '))
      else setError(d || 'Registration failed. Please try again.')
    } finally { setLoading(false) }
  }

  if (otpEmail) {
    return (
      <div style={S.bg}>
        <style>{`
          @keyframes spin { to { transform: rotate(360deg) } }
          input:focus { border-color: #3d7a6f !important; box-shadow: 0 0 0 3px rgba(61,122,111,0.18) !important; }
        `}</style>
        <OtpScreen email={otpEmail} />
      </div>
    )
  }

  return (
    <div style={S.bg}>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg) } }
        input:focus { border-color: #3d7a6f !important; box-shadow: 0 0 0 3px rgba(61,122,111,0.18) !important; }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        button:hover:not(:disabled) { opacity: 0.92; transform: translateY(-1px); }
      `}</style>
      <div style={S.card}>

        {/* Logo */}
        <FinexLogo />
        <p style={S.sub}>Create your account</p>

        {error && <div style={S.err}>{error}</div>}

        <form onSubmit={handleSubmit} noValidate>
          <div style={S.group}>
            <label style={S.label}>Full Name</label>
            <input style={S.input} placeholder="John Doe" value={form.full_name} onChange={set('full_name')} required />
          </div>
          <div style={S.group}>
            <label style={S.label}>Email</label>
            <input style={S.input} type="email" placeholder="you@example.com" value={form.email} onChange={set('email')} required />
          </div>
          <div style={S.group}>
            <label style={S.label}>Phone <span style={{ color:'#8a9aa3',fontWeight:400 }}>(optional)</span></label>
            <input style={S.input} type="tel" placeholder="+91 98765 43210" value={form.phone} onChange={set('phone')} />
          </div>
          <div style={S.group}>
            <label style={S.label}>Password</label>
            <input style={S.input} type="password" placeholder="••••••••" value={form.password} onChange={set('password')} required />
          </div>
          <div style={{ ...S.group,marginBottom:20 }}>
            <label style={S.label}>Confirm Password</label>
            <input style={S.input} type="password" placeholder="••••••••" value={form.confirm} onChange={set('confirm')} required />
          </div>

          <div style={{ marginBottom:20 }}>
            <CaptchaBox onVerified={setCaptchaOk} />
          </div>

          <button style={S.btn} type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <div style={S.link}>
          Already have an account?{' '}
          <Link to="/login" style={{ color:'#3d7a6f',fontWeight:600,textDecoration:'none' }}>Sign in</Link>
        </div>
      </div>
    </div>
  )
}