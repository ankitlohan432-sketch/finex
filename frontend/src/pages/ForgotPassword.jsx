import { useState } from "react"
import { useNavigate } from "react-router-dom"
const API_BASE = import.meta.env.VITE_API_URL || ""

export default function ForgotPassword() {
  const [step, setStep]         = useState(1)
  const [email, setEmail]       = useState("")
  const [otp, setOtp]           = useState("")
  const [newPass, setNewPass]   = useState("")
  const [loading, setLoading]   = useState(false)
  const [error, setError]       = useState("")
  const [success, setSuccess]   = useState("")
  const navigate = useNavigate()

  const sendOtp = async () => {
    setLoading(true); setError("")
    try {
      const res  = await fetch(`${API_BASE}/auth/forgot-password`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({email})
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || "Error"); return }
      setSuccess("Reset code sent to your email!"); setStep(2)
    } catch { setError("Network error") }
    finally { setLoading(false) }
  }

  const resetPass = async () => {
    setLoading(true); setError("")
    try {
      const res  = await fetch(`${API_BASE}/auth/reset-password`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({email, otp, new_password: newPass})
      })
      const data = await res.json()
      if (!res.ok) { setError(data.detail || "Error"); return }
      setSuccess("Password reset! Redirecting to login...")
      setTimeout(() => navigate("/login"), 2000)
    } catch { setError("Network error") }
    finally { setLoading(false) }
  }

  return (
    <div style={{minHeight:"100vh",display:"flex",alignItems:"center",justifyContent:"center",background:"var(--bg-primary)"}}>
      <div className="card" style={{width:"100%",maxWidth:400,padding:32}}>
        <h2 style={{marginBottom:8,color:"var(--text-primary)"}}>Reset Password</h2>
        <p style={{color:"var(--text-muted)",fontSize:13,marginBottom:24}}>
          {step===1 ? "Enter your email to receive a reset code." : "Enter the code from your email."}
        </p>

        {error   && <div style={{color:"var(--danger)",  marginBottom:12,fontSize:13}}>{error}</div>}
        {success && <div style={{color:"var(--success)", marginBottom:12,fontSize:13}}>{success}</div>}

        {step===1 && <>
          <input className="input" placeholder="Email address" type="email"
            value={email} onChange={e=>setEmail(e.target.value)}
            style={{width:"100%",marginBottom:16}} />
          <button className="btn btn-primary" style={{width:"100%"}}
            onClick={sendOtp} disabled={loading||!email}>
            {loading ? "Sending..." : "Send Reset Code"}
          </button>
        </>}

        {step===2 && <>
          <input className="input" placeholder="6-digit code" maxLength={6}
            value={otp} onChange={e=>setOtp(e.target.value)}
            style={{width:"100%",marginBottom:12}} />
          <input className="input" placeholder="New password" type="password"
            value={newPass} onChange={e=>setNewPass(e.target.value)}
            style={{width:"100%",marginBottom:16}} />
          <button className="btn btn-primary" style={{width:"100%"}}
            onClick={resetPass} disabled={loading||!otp||!newPass}>
            {loading ? "Resetting..." : "Reset Password"}
          </button>
        </>}

        <div style={{textAlign:"center",marginTop:16}}>
          <span onClick={()=>navigate("/login")}
            style={{fontSize:13,color:"var(--accent)",cursor:"pointer"}}>
            Back to Login
          </span>
        </div>
      </div>
    </div>
  )
}
