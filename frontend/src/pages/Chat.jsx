import { useState, useEffect, useRef } from 'react'
import { chatAPI } from '../services/api'
import { Send, Bot, User, Sparkles } from 'lucide-react'

const QUICK = [
  'What stocks should I buy today?',
  'Check my loan eligibility',
  'How is the market trending?',
  'Explain fraud protection',
  'Best investment strategy for beginners',
  'What is rupee cost averaging?'
]

export default function Chat() {
  const [messages, setMessages] = useState([{
    role: 'assistant',
    content: "Hello! I'm your Finex AI Financial Assistant 🤖\n\nI can help you with:\n• Stock recommendations & market analysis\n• Loan eligibility & financial planning\n• Portfolio review & optimization\n• Fraud detection & account security\n• Investment strategies\n\nWhat would you like to know today?"
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async (text) => {
    const msg = (text || input).trim()
    if (!msg || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: msg }])
    setLoading(true)
    try {
      const res = await chatAPI.ask({ message: msg })
      const reply = res.data?.response || res.data?.reply || res.data?.message || "I couldn't process that. Please try again."
      setMessages(prev => [...prev, { role: 'assistant', content: reply }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }])
    } finally { setLoading(false) }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 100px)', maxWidth: 800, margin: '0 auto' }}>
      <div style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{ width: 40, height: 40, borderRadius: 12, background: 'var(--accent-light)', border: '1px solid rgba(0,229,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Sparkles size={20} style={{ color: 'var(--accent)' }} />
        </div>
        <div>
          <div style={{ fontWeight: 600, fontSize: 15, color: 'var(--text-primary)' }}>Finex AI Assistant</div>
          <div style={{ fontSize: 11, color: 'var(--success)', display: 'flex', alignItems: 'center', gap: 4 }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--success)' }} /> Online
          </div>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', marginBottom: 12 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', gap: 10, marginBottom: 16, flexDirection: m.role === 'user' ? 'row-reverse' : 'row' }}>
            <div style={{ width: 30, height: 30, borderRadius: 8, flexShrink: 0, background: m.role === 'user' ? 'var(--accent-light)' : 'rgba(104,211,145,0.1)', border: `1px solid ${m.role === 'user' ? 'rgba(0,229,255,0.2)' : 'rgba(104,211,145,0.2)'}`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {m.role === 'user' ? <User size={13} style={{ color: 'var(--accent)' }} /> : <Bot size={13} style={{ color: 'var(--success)' }} />}
            </div>
            <div style={{ background: m.role === 'user' ? 'var(--bg-card)' : 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: m.role === 'user' ? '12px 4px 12px 12px' : '4px 12px 12px 12px', padding: '12px 16px', maxWidth: '78%', fontSize: 13, lineHeight: 1.65, color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
              {m.content}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', gap: 10, marginBottom: 16 }}>
            <div style={{ width: 30, height: 30, borderRadius: 8, background: 'rgba(104,211,145,0.1)', border: '1px solid rgba(104,211,145,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bot size={13} style={{ color: 'var(--success)' }} />
            </div>
            <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border)', borderRadius: '4px 12px 12px 12px', padding: '14px 18px', display: 'flex', gap: 5 }}>
              {[0,1,2].map(i => <div key={i} style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--text-muted)', animation: 'pulse 1.2s ease infinite', animationDelay: `${i*0.2}s` }} />)}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {messages.length <= 2 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
          {QUICK.map((q, i) => (
            <button key={i} className="btn btn-ghost btn-sm" onClick={() => send(q)} style={{ fontSize: 11 }}>{q}</button>
          ))}
        </div>
      )}

      <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 12, padding: '8px 8px 8px 16px', display: 'flex', gap: 8 }}>
        <input className="form-input" placeholder="Ask about stocks, loans, investments, fraud protection..."
          value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          disabled={loading}
          style={{ border: 'none', background: 'none', flex: 1, padding: '6px 0', fontSize: 13 }} />
        <button className="btn btn-primary" style={{ borderRadius: 8, padding: '8px 14px' }}
          onClick={() => send()} disabled={loading || !input.trim()}>
          <Send size={14} />
        </button>
      </div>
      <p style={{ fontSize: 10, color: 'var(--text-muted)', textAlign: 'center', marginTop: 6 }}>
        AI responses are for informational purposes only, not financial advice.
      </p>
      <style>{`@keyframes pulse{0%,100%{opacity:0.3;transform:scale(0.8)}50%{opacity:1;transform:scale(1)}}`}</style>
    </div>
  )
}
