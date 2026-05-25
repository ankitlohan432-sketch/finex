import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Pause, Zap, Brain } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function PredictionCard({ symbol, market }) {
  const [pred, setPred]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const [interval, setInterval] = useState(market === 'crypto' ? '1h' : '1d')

  useEffect(() => { fetchPrediction(interval) }, [symbol, market])

  const fetchPrediction = async (intv) => {
    try {
      setLoading(true)
      setError(null)
      const res  = await fetch(`${API_BASE}/predict/${market.toLowerCase()}/${symbol}?interval=${intv}`)
      const data = await res.json()
      if (data.error) { setError(data.error); setPred(null) }
      else setPred(data)
    } catch (e) {
      setError('Failed to load prediction')
    } finally {
      setLoading(false)
    }
  }

  const intervals = market === 'crypto' ? ['5m','15m','1h','4h','1d'] : ['1d','1wk']

  const signalColor = pred
    ? pred.signal?.includes('BUY')  ? '#00e5a0'
    : pred.signal?.includes('SELL') ? '#ff4444'
    : '#fbbf24'
    : '#fbbf24'

  return (
    <div className="card" style={{ borderLeft: `4px solid ${signalColor}` }}>
      <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:12 }}>
        <Brain size={16} style={{ color:'var(--accent)' }} />
        <span style={{ fontWeight:700, fontSize:14 }}>AI Prediction</span>
        <div style={{ marginLeft:'auto', display:'flex', gap:4 }}>
          {intervals.map(i => (
            <button key={i} onClick={() => { setInterval(i); fetchPrediction(i) }}
              style={{ fontSize:10, padding:'2px 6px', borderRadius:4,
                border:'1px solid var(--border-light)',
                background: interval===i ? 'var(--accent)' : 'transparent',
                color: interval===i ? '#fff' : 'var(--text-muted)',
                cursor:'pointer' }}>
              {i}
            </button>
          ))}
        </div>
      </div>

      {loading && (
        <div style={{ textAlign:'center', padding:20, color:'var(--text-muted)' }}>
          🤖 Running AI analysis...
        </div>
      )}

      {error && !loading && (
        <div style={{ textAlign:'center', padding:20, color:'var(--danger)', fontSize:13 }}>
          ⚠️ {error}
        </div>
      )}

      {pred && !loading && (
        <>
          {/* Signal */}
          <div style={{ textAlign:'center', marginBottom:16 }}>
            <div style={{ fontSize:28, fontWeight:900, color:signalColor }}>{pred.signal}</div>
            <div style={{ fontSize:12, color:'var(--text-muted)' }}>Confidence: {pred.confidence}%</div>
            <div style={{ background:'var(--bg-card-high)', borderRadius:8, height:6, marginTop:8 }}>
              <div style={{ width:`${pred.confidence}%`, height:6, borderRadius:8, background:signalColor, transition:'width 0.5s' }} />
            </div>
          </div>

          {/* Stats */}
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:12 }}>
            {[
              ['Predicted',   `$${Number(pred.predicted_price)?.toLocaleString()}`, signalColor],
              ['Change',      `${pred.change_pct >= 0 ? '+' : ''}${pred.change_pct}%`, signalColor],
              ['RSI',         pred.rsi, pred.rsi > 70 ? '#ff6b6b' : pred.rsi < 30 ? '#00e5a0' : '#fbbf24'],
              ['Momentum',    `${pred.momentum >= 0 ? '+' : ''}${pred.momentum}%`, pred.momentum >= 0 ? '#00e5a0' : '#ff6b6b'],
            ].map(([label, val, color]) => (
              <div key={label} style={{ background:'var(--bg-card-high)', borderRadius:8, padding:'8px 12px' }}>
                <div style={{ fontSize:11, color:'var(--text-muted)', marginBottom:2 }}>{label}</div>
                <div style={{ fontFamily:'monospace', fontWeight:600, color, fontSize:13 }}>{val}</div>
              </div>
            ))}
          </div>

          {/* Reasons */}
          {pred.reasons?.length > 0 && (
            <div style={{ fontSize:11, color:'var(--text-muted)' }}>
              {pred.reasons.map((r, i) => (
                <div key={i} style={{ padding:'3px 0', borderBottom:'1px solid var(--border-light)' }}>• {r}</div>
              ))}
            </div>
          )}

          <button onClick={() => fetchPrediction(interval)}
            style={{ width:'100%', marginTop:10, padding:8, borderRadius:6,
              background:'rgba(0,229,255,0.1)', border:'1px solid rgba(0,229,255,0.2)',
              color:'var(--accent)', cursor:'pointer', fontSize:11, fontWeight:600 }}>
            <Zap size={12} style={{ display:'inline', marginRight:4 }} /> Refresh
          </button>
        </>
      )}
    </div>
  )
}
