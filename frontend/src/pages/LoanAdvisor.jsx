import { useState } from 'react'
import { Brain, DollarSign, Calendar, Percent, CheckCircle, XCircle } from 'lucide-react'

export default function LoanAdvisor() {
  const [form, setForm] = useState({ amount: '', income: '', employment: 'salaried', purpose: 'personal', credit: '700' })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const set = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const analyze = () => {
    setLoading(true)
    setTimeout(() => {
      const amt = Number(form.amount)
      const income = Number(form.income)
      const credit = Number(form.credit)
      const ratio = amt / (income * 12)
      const eligible = credit >= 650 && ratio < 0.5 && income > 0
      const rate = credit >= 750 ? 5.5 : credit >= 700 ? 7.2 : credit >= 650 ? 9.8 : 14.5
      const emi = eligible ? (amt * (rate/1200) * Math.pow(1 + rate/1200, 60)) / (Math.pow(1 + rate/1200, 60) - 1) : 0
      setResult({ eligible, rate, emi: emi.toFixed(0), credit, ratio: (ratio * 100).toFixed(0) })
      setLoading(false)
    }, 1500)
  }

  return (
    <div style={{ maxWidth: 700, margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
        <div style={{ width: 44, height: 44, borderRadius: 12, background: 'var(--accent-light)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Brain size={22} style={{ color: 'var(--accent)' }} />
        </div>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>AI Loan Advisor</h2>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>Get instant loan eligibility analysis</p>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header"><span className="card-title">Loan Details</span></div>
          <div className="form-group">
            <label className="form-label">Loan Amount ($)</label>
            <input className="form-input" type="number" placeholder="e.g. 10000" value={form.amount} onChange={set('amount')} />
          </div>
          <div className="form-group">
            <label className="form-label">Monthly Income ($)</label>
            <input className="form-input" type="number" placeholder="e.g. 5000" value={form.income} onChange={set('income')} />
          </div>
          <div className="form-group">
            <label className="form-label">Employment Type</label>
            <select value={form.employment} onChange={set('employment')}>
              <option value="salaried">Salaried</option>
              <option value="self">Self-Employed</option>
              <option value="business">Business Owner</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Loan Purpose</label>
            <select value={form.purpose} onChange={set('purpose')}>
              <option value="personal">Personal</option>
              <option value="investment">Investment</option>
              <option value="education">Education</option>
              <option value="home">Home Improvement</option>
            </select>
          </div>
          <div className="form-group">
            <label className="form-label">Credit Score (approx)</label>
            <select value={form.credit} onChange={set('credit')}>
              <option value="750">750+ (Excellent)</option>
              <option value="700">700-749 (Good)</option>
              <option value="650">650-699 (Fair)</option>
              <option value="600">Below 650 (Poor)</option>
            </select>
          </div>
          <button className="btn btn-primary" style={{ width: '100%' }} onClick={analyze} disabled={!form.amount || !form.income || loading}>
            <Brain size={14} /> {loading ? 'Analyzing...' : 'Check Eligibility'}
          </button>
        </div>

        <div>
          {result ? (
            <div className="card">
              <div className="card-header"><span className="card-title">AI Analysis Result</span></div>
              <div style={{ textAlign: 'center', padding: '20px 0', borderBottom: '1px solid var(--border-light)', marginBottom: 16 }}>
                {result.eligible ? (
                  <>
                    <CheckCircle size={48} style={{ color: 'var(--success)', marginBottom: 8 }} />
                    <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--success)' }}>Eligible!</div>
                    <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>You qualify for this loan</div>
                  </>
                ) : (
                  <>
                    <XCircle size={48} style={{ color: 'var(--danger)', marginBottom: 8 }} />
                    <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--danger)' }}>Not Eligible</div>
                    <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Improve credit score or reduce amount</div>
                  </>
                )}
              </div>
              {result.eligible && (
                <div style={{ display: 'grid', gap: 12 }}>
                  {[
                    { label: 'Interest Rate', value: `${result.rate}% p.a.`, icon: Percent },
                    { label: 'Monthly EMI', value: `$${Number(result.emi).toLocaleString()}`, icon: Calendar },
                    { label: 'Debt-to-Income', value: `${result.ratio}%`, icon: DollarSign },
                    { label: 'Loan Term', value: '60 months', icon: Calendar },
                  ].map(({ label, value, icon: Icon }) => (
                    <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid var(--border-light)' }}>
                      <span style={{ fontSize: 13, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
                        <Icon size={13} /> {label}
                      </span>
                      <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', fontFamily: 'monospace' }}>{value}</span>
                    </div>
                  ))}
                </div>
              )}
              {!result.eligible && (
                <div style={{ background: 'var(--danger-bg)', border: '1px solid rgba(255,107,107,0.2)', borderRadius: 10, padding: 14 }}>
                  <div style={{ fontSize: 13, color: 'var(--danger)', fontWeight: 600, marginBottom: 8 }}>How to improve eligibility:</div>
                  <ul style={{ fontSize: 12, color: 'var(--text-muted)', paddingLeft: 16, lineHeight: 2 }}>
                    <li>Reduce loan amount requested</li>
                    <li>Improve credit score above 650</li>
                    <li>Show additional income sources</li>
                    <li>Clear existing debts first</li>
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
              <Brain size={40} style={{ marginBottom: 12, opacity: 0.3 }} />
              <p style={{ fontSize: 14 }}>Fill the form and click<br />"Check Eligibility"</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
