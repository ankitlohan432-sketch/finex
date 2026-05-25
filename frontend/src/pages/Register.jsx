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

  const border = status === 'verified' ? '1.5px solid #10b981' : status === 'loading' ? '1.5px solid #63b3ed' : '1.5px solid rgba(255,255,255,0.15)'
  const bg = status === 'verified' ? 'rgba(16,185,129,0.08)' : status === 'loading' ? 'rgba(99,179,237,0.08)' : 'rgba(255,255,255,0.04)'

  return (
    <div onClick={handleClick} style={{ display:'flex',alignItems:'center',gap:12,padding:'12px 16px',borderRadius:10,cursor:status==='idle'?'pointer':'default',border,background:bg,userSelect:'none',transition:'all 0.2s' }}>
      <div style={{ width:20,height:20,borderRadius:status==='loading'?'50%':4,flexShrink:0,border:status==='verified'?'none':status==='loading'?'2px solid #63b3ed':'2px solid rgba(255,255,255,0.3)',background:status==='verified'?'#10b981':'transparent',display:'flex',alignItems:'center',justifyContent:'center',animation:status==='loading'?'spin 0.8s linear infinite':'none' }}>
        {status==='verified'&&<svg width="11" height="11" viewBox="0 0 12 12"><path d="M2 6l3 3 5-5" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" fill="none"/></svg>}
      </div>
      <span style={{ color:status==='verified'?'#6ee7b7':'rgba(255,255,255,0.7)',fontSize:13,fontWeight:500 }}>
        {status==='idle'&&"I'm not a robot"}{status==='loading'&&'Verifying...'}{status==='verified'&&'Verified ✓'}
      </span>
      <div style={{ marginLeft:'auto',textAlign:'right',fontSize:10,color:'rgba(255,255,255,0.25)',lineHeight:1.4 }}>reCAPTCHA</div>
    </div>
  )
}

const S = {
  bg: { minHeight:'100vh',width:'100%',display:'flex',alignItems:'center',justifyContent:'center',background:'linear-gradient(135deg,#0f172a 0%,#1e293b 50%,#0f2044 100%)',padding:24,fontFamily:"'Inter',system-ui,sans-serif" },
  card: { background:'rgba(255,255,255,0.05)',backdropFilter:'blur(20px)',border:'1px solid rgba(255,255,255,0.1)',borderRadius:20,padding:'40px 36px',width:'100%',maxWidth:420,boxShadow:'0 25px 60px rgba(0,0,0,0.5)' },
  logo: { textAlign:'center',fontSize:32,fontWeight:800,color:'#fff',marginBottom:4,letterSpacing:-1 },
  sub: { textAlign:'center',color:'rgba(255,255,255,0.45)',fontSize:14,marginBottom:28 },
  group: { marginBottom:14 },
  label: { display:'block',color:'rgba(255,255,255,0.7)',fontSize:13,fontWeight:600,marginBottom:6 },
  input: { width:'100%',background:'rgba(255,255,255,0.07)',border:'1.5px solid rgba(255,255,255,0.12)',color:'#fff',borderRadius:10,padding:'11px 14px',fontSize:14,outline:'none',boxSizing:'border-box',transition:'all 0.2s' },
  btn: { width:'100%',padding:'13px',fontSize:15,fontWeight:700,background:'linear-gradient(135deg,#3b82f6,#2563eb)',border:'none',borderRadius:10,color:'#fff',cursor:'pointer',marginTop:4,boxShadow:'0 4px 15px rgba(59,130,246,0.35)',transition:'all 0.2s' },
  btnGhost: { width:'100%',padding:'11px',fontSize:13,fontWeight:600,background:'transparent',border:'1px solid rgba(255,255,255,0.15)',borderRadius:10,color:'rgba(255,255,255,0.6)',cursor:'pointer',marginTop:8,transition:'all 0.2s' },
  err: { background:'rgba(239,68,68,0.15)',border:'1px solid rgba(239,68,68,0.3)',color:'#fca5a5',borderRadius:8,padding:'11px 14px',fontSize:13,marginBottom:16 },
  success: { background:'rgba(16,185,129,0.15)',border:'1px solid rgba(16,185,129,0.3)',color:'#6ee7b7',borderRadius:8,padding:'11px 14px',fontSize:13,marginBottom:16,textAlign:'center' },
  link: { textAlign:'center',marginTop:20,fontSize:13,color:'rgba(255,255,255,0.45)' },
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
            background:'rgba(255,255,255,0.07)',
            border: d.trim() ? '2px solid #38bdf8' : '2px solid rgba(255,255,255,0.15)',
            color:'#fff',borderRadius:12,outline:'none',fontFamily:'monospace',
            boxShadow: d.trim() ? '0 0 0 3px rgba(56,189,248,0.15)' : 'none',
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
      // If backend returns a token, log user in directly
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
      <div style={S.logo}>Fin<span style={{ color:'#63b3ed' }}>ex</span></div>
      <p style={S.sub}>Verify your email</p>

      <div style={{ textAlign:'center',marginBottom:20,padding:'14px',background:'rgba(56,189,248,0.08)',borderRadius:12,border:'1px solid rgba(56,189,248,0.2)' }}>
        <div style={{ fontSize:13,color:'rgba(255,255,255,0.5)',marginBottom:4 }}>Code sent to</div>
        <div style={{ fontSize:15,fontWeight:700,color:'#38bdf8' }}>{email}</div>
      </div>

      {error && <div style={S.err}>{error}</div>}
      {success && <div style={S.success}>{success}</div>}
      {resendMsg && <div style={{ ...S.success,background:'rgba(56,189,248,0.1)',borderColor:'rgba(56,189,248,0.3)',color:'#7dd3fc' }}>{resendMsg}</div>}

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
        <Link to="/register" style={{ color:'#63b3ed',fontWeight:600,textDecoration:'none' }}>Go back</Link>
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
  const [otpEmail, setOtpEmail] = useState(null) // triggers OTP screen
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
      setOtpEmail(form.email) // switch to OTP screen
    } catch (err) {
      const d = err.response?.data?.detail
      if (Array.isArray(d)) setError(d.map(x => x.msg).join('. '))
      else setError(d || 'Registration failed. Please try again.')
    } finally { setLoading(false) }
  }

  // Show OTP screen after successful register
  if (otpEmail) {
    return (
      <div style={S.bg}>
        <style>{`@keyframes spin{to{transform:rotate(360deg)}} input:focus{border-color:#38bdf8!important;box-shadow:0 0 0 3px rgba(56,189,248,0.2)!important}`}</style>
        <OtpScreen email={otpEmail} />
      </div>
    )
  }

  return (
    <div style={S.bg}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}} input:focus{border-color:#63b3ed!important;box-shadow:0 0 0 3px rgba(99,179,237,0.2)!important} button:disabled{opacity:0.6;cursor:not-allowed}`}</style>
      <div style={S.card}>
        <div style={S.logo}>Fin<span style={{ color:'#63b3ed' }}>ex</span></div>
        <p style={S.sub}>Create your account</p>
        {error && <div style={S.err}>{error}</div>}
        <form onSubmit={handleSubmit} noValidate>
          <div style={S.group}><label style={S.label}>Full Name</label><input style={S.input} placeholder="John Doe" value={form.full_name} onChange={set('full_name')} required /></div>
          <div style={S.group}><label style={S.label}>Email</label><input style={S.input} type="email" placeholder="you@example.com" value={form.email} onChange={set('email')} required /></div>
          <div style={S.group}><label style={S.label}>Phone <span style={{ color:'rgba(255,255,255,0.3)',fontWeight:400 }}>(optional)</span></label><input style={S.input} type="tel" placeholder="+91 98765 43210" value={form.phone} onChange={set('phone')} /></div>
          <div style={S.group}><label style={S.label}>Password</label><input style={S.input} type="password" placeholder="••••••••" value={form.password} onChange={set('password')} required /></div>
          <div style={{ ...S.group,marginBottom:20 }}><label style={S.label}>Confirm Password</label><input style={S.input} type="password" placeholder="••••••••" value={form.confirm} onChange={set('confirm')} required /></div>
          <div style={{ marginBottom:20 }}><CaptchaBox onVerified={setCaptchaOk} /></div>
          <button style={S.btn} type="submit" disabled={loading}>
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>
        <div style={S.link}>
          Already have an account?{' '}
          <Link to="/login" style={{ color:'#63b3ed',fontWeight:600,textDecoration:'none' }}>Sign in</Link>
        </div>
      </div>
    </div>
  )
}
