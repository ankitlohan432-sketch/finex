import { useState } from 'react'
import { DollarSign, CreditCard, Building, Smartphone, Check } from 'lucide-react'

const METHODS = [
  { id: 'card', label: 'Credit/Debit Card', icon: CreditCard, desc: 'Instant deposit' },
  { id: 'bank', label: 'Bank Transfer', icon: Building, desc: '1-3 business days' },
  { id: 'upi', label: 'UPI / Net Banking', icon: Smartphone, desc: 'Instant for India' },
]

const AMOUNTS = [500, 1000, 5000, 10000, 25000]

export default function AddFunds() {
  const [method, setMethod] = useState('card')
  const [amount, setAmount] = useState('')
  const [done, setDone] = useState(false)
  const [loading, setLoading] = useState(false)

  const submit = () => {
    if (!amount || isNaN(amount) || Number(amount) <= 0) return
    setLoading(true)
    setTimeout(() => { setLoading(false); setDone(true) }, 1500)
  }

  if (done) return (
    <div style={{ maxWidth: 480, margin: '60px auto', textAlign: 'center' }}>
      <div className="card">
        <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'var(--success-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px' }}>
          <Check size={28} style={{ color: 'var(--success)' }} />
        </div>
        <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>Funds Added!</h2>
        <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 20 }}>${Number(amount).toLocaleString()} has been added to your account.</p>
        <button className="btn btn-primary" style={{ width: '100%' }} onClick={() => { setDone(false); setAmount('') }}>Add More Funds</button>
      </div>
    </div>
  )

  return (
    <div style={{ maxWidth: 480, margin: '0 auto' }}>
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-header"><span className="card-title">Select Amount</span></div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
          {AMOUNTS.map(a => (
            <button key={a} className={`btn ${amount == a ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setAmount(String(a))}>
              ${a.toLocaleString()}
            </button>
          ))}
        </div>
        <div className="form-group" style={{ margin: 0 }}>
          <label className="form-label">Custom Amount</label>
          <div style={{ position: 'relative' }}>
            <DollarSign size={14} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input className="form-input" type="number" placeholder="Enter amount" value={amount} onChange={e => setAmount(e.target.value)} style={{ paddingLeft: 32 }} />
          </div>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <div className="card-header"><span className="card-title">Payment Method</span></div>
        {METHODS.map(({ id, label, icon: Icon, desc }) => (
          <div key={id} onClick={() => setMethod(id)} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '14px', borderRadius: 10, border: `1px solid ${method === id ? 'var(--accent)' : 'var(--border-light)'}`, background: method === id ? 'var(--accent-light)' : 'transparent', cursor: 'pointer', marginBottom: 8, transition: 'all 0.2s' }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: method === id ? 'var(--accent-light)' : 'var(--bg-card)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Icon size={16} style={{ color: method === id ? 'var(--accent)' : 'var(--text-muted)' }} />
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-primary)' }}>{label}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{desc}</div>
            </div>
            <div style={{ marginLeft: 'auto', width: 18, height: 18, borderRadius: '50%', border: `2px solid ${method === id ? 'var(--accent)' : 'var(--border)'}`, background: method === id ? 'var(--accent)' : 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {method === id && <Check size={10} style={{ color: '#001f24' }} />}
            </div>
          </div>
        ))}
      </div>

      <button className="btn btn-primary" style={{ width: '100%' }} onClick={submit} disabled={!amount || loading}>
        {loading ? 'Processing...' : `Add $${amount ? Number(amount).toLocaleString() : '0'}`}
      </button>
    </div>
  )
}
