import { useState } from 'react'
import { HelpCircle, ChevronDown, ChevronUp, Search, MessageSquare, Mail, Phone } from 'lucide-react'

const FAQS = [
  { q: 'How do I buy stocks?', a: 'Go to Markets → Search for the stock symbol → Click on it → Enter quantity → Click "Buy". Your order will be placed instantly.' },
  { q: 'How do I add funds to my account?', a: 'Click "Add Funds" in the sidebar → Choose an amount → Select payment method → Confirm. Funds are added instantly for card payments.' },
  { q: 'What is my credit score and how is it calculated?', a: 'Your credit score is based on your transaction history, repayment record, and account activity. Check the Risk Analysis section for your current score.' },
  { q: 'How do I apply for a loan?', a: 'Go to "Loan Advisor" in the AI Tools section → Fill in your income and loan details → Click "Check Eligibility" → If approved, click Apply.' },
  { q: 'Is my money safe on Finex?', a: 'Yes! Finex uses bank-grade 256-bit encryption, real-time fraud detection, and provides 100% fraud protection guarantee on all transactions.' },
  { q: 'How do I report a suspicious transaction?', a: 'Go to Fraud Detection → Click "Report" next to the suspicious transaction → Our team investigates within 24 hours.' },
  { q: 'Can I withdraw my funds anytime?', a: 'Yes, you can withdraw funds at any time. Bank transfers take 1-3 business days. Card refunds appear within 3-5 business days.' },
  { q: 'How does the AI assistant work?', a: 'The AI Assistant (Loan Advisor) uses your portfolio data and market trends to give personalized financial advice. It is available 24/7.' },
]

export default function Help() {
  const [open, setOpen] = useState(null)
  const [search, setSearch] = useState('')

  const filtered = FAQS.filter(f => f.q.toLowerCase().includes(search.toLowerCase()) || f.a.toLowerCase().includes(search.toLowerCase()))

  return (
    <div style={{ maxWidth: 700, margin: '0 auto' }}>
      <div className="card" style={{ marginBottom: 20, textAlign: 'center', padding: '32px 24px' }}>
        <HelpCircle size={40} style={{ color: 'var(--accent)', marginBottom: 12 }} />
        <h2 style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 8 }}>How can we help?</h2>
        <div style={{ position: 'relative', maxWidth: 400, margin: '0 auto' }}>
          <Search size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input className="form-input" placeholder="Search help articles..." value={search} onChange={e => setSearch(e.target.value)} style={{ paddingLeft: 42 }} />
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="card-header"><span className="card-title">Frequently Asked Questions</span></div>
        {filtered.map((faq, i) => (
          <div key={i} style={{ borderBottom: '1px solid var(--border-light)' }}>
            <div onClick={() => setOpen(open === i ? null : i)} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 0', cursor: 'pointer' }}>
              <span style={{ fontSize: 14, fontWeight: 500, color: 'var(--text-primary)' }}>{faq.q}</span>
              {open === i ? <ChevronUp size={16} style={{ color: 'var(--text-muted)', flexShrink: 0 }} /> : <ChevronDown size={16} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />}
            </div>
            {open === i && <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.7, paddingBottom: 14 }}>{faq.a}</div>}
          </div>
        ))}
        {filtered.length === 0 && <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)', fontSize: 14 }}>No results found for "{search}"</div>}
      </div>

      <div className="grid-3">
        {[
          { icon: MessageSquare, label: 'Live Chat', desc: 'Chat with support', action: 'Start Chat' },
          { icon: Mail, label: 'Email Us', desc: 'support@finex.com', action: 'Send Email' },
          { icon: Phone, label: 'Call Us', desc: '+1 800-FINEX-00', action: 'Call Now' },
        ].map(({ icon: Icon, label, desc, action }) => (
          <div className="card" key={label} style={{ textAlign: 'center', cursor: 'pointer' }}>
            <Icon size={28} style={{ color: 'var(--accent)', marginBottom: 10 }} />
            <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 12 }}>{desc}</div>
            <button className="btn btn-ghost btn-sm" style={{ width: '100%' }}>{action}</button>
          </div>
        ))}
      </div>
    </div>
  )
}
