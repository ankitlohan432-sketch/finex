import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Pause, Zap, Brain } from 'lucide-react'

const API_BASE = import.meta.env.VITE_API_URL || ''

export default function PredictionCard({ symbol, market }) {
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchPrediction()
    const interval = setInterval(fetchPrediction, 60000)
    return () => clearInterval(interval)
  }, [symbol, market])

  const fetchPrediction = async () => {
    try {
      setLoading(true)
      // Fixed: was /predict/ensemble/... which doesn't exist — now uses correct route
      const url = `${API_BASE}/predict/${market.toLowerCase()}/${symbol}`
      const res = await fetch(url)
      const data = await res.json()

      if (data.error) {
        setError('Insufficient market data')
        setPrediction(null)
      } else {
        // Normalize response to match what the card expects
        setPrediction({
          final_prediction: {
            signal: data.signal || 'HOLD',
            confidence: (data.confidence || 0) / 100,
            combined_score: (data.confidence || 0) / 100,
          },
          ml_prediction: { ml_score: (data.confidence || 0) / 100 },
          dl_prediction: { dl_ensemble_score: (data.confidence || 0) / 100 },
          ...data
        })
        setError(null)
      }
    } catch (e) {
      setError('Failed to load prediction')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div style={{ padding: 20, textAlign: 'center', color: 'var(--text-muted)' }}>🤖 Loading prediction...</div>
  if (error) return <div style={{ padding: 20, textAlign: 'center', color: 'var(--danger)' }}>⚠️ {error}</div>
  if (!prediction) return null

  const signal = prediction.final_prediction?.signal || 'HOLD'
  const confidence = prediction.final_prediction?.confidence || 0
  const mlScore = prediction.ml_prediction?.ml_score || 0.5
  const dlScore = prediction.dl_prediction?.dl_ensemble_score || 0.5

  const signalColor = signal.includes('BUY') ? 'var(--success)' : signal.includes('SELL') ? 'var(--danger)' : 'var(--text-secondary)'
  const signalIcon = signal.includes('BUY') ? <TrendingUp size={24} /> : signal.includes('SELL') ? <TrendingDown size={24} /> : <Pause size={24} />

  const confidencePercent = Math.round(confidence * 100)

  return (
    <div className="card" style={{ background: 'rgba(0,229,255,0.05)', borderLeft: `4px solid ${signalColor}` }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <Brain size={20} style={{ color: 'var(--accent)' }} />
        <h3 style={{ margin: 0, fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>AI Prediction</h3>
        <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--text-muted)' }}>Updated now</span>
      </div>

      <div style={{ textAlign: 'center', marginBottom: 16, paddingBottom: 16, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <div style={{ color: signalColor, fontSize: 28, display: 'flex' }}>{signalIcon}</div>
          <div style={{ color: signalColor, fontSize: 24, fontWeight: 800 }}>{signal}</div>
        </div>
        <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--text-primary)' }}>{confidencePercent}%</div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>Confidence Score</div>
      </div>

      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8, letterSpacing: 0.5 }}>Model Scores</div>
        {[['ML Analysis', mlScore, 'linear-gradient(90deg, #00e5a0, #00e5ff)'], ['DL Analysis', dlScore, 'linear-gradient(90deg, #6366f1, #a855f7)']].map(([label, score, gradient]) => (
          <div key={label} style={{ marginBottom: 10 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
              <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>{label}</span>
              <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent)' }}>{(score * 100).toFixed(0)}%</span>
            </div>
            <div style={{ width: '100%', height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{ width: `${score * 100}%`, height: '100%', background: gradient, transition: 'width 0.3s' }} />
            </div>
          </div>
        ))}
      </div>

      {prediction.reasons && prediction.reasons.length > 0 && (
        <div style={{ fontSize: 11, color: 'var(--text-muted)', background: 'rgba(0,0,0,0.2)', padding: 8, borderRadius: 6, lineHeight: '1.6', marginBottom: 8 }}>
          {prediction.reasons.map((r, i) => <div key={i}>• {r}</div>)}
        </div>
      )}

      <button onClick={fetchPrediction}
        style={{ width: '100%', marginTop: 8, padding: 8, borderRadius: 6, background: 'rgba(0,229,255,0.1)', border: '1px solid rgba(0,229,255,0.2)', color: 'var(--accent)', cursor: 'pointer', fontSize: 11, fontWeight: 600 }}>
        <Zap size={12} style={{ display: 'inline', marginRight: 4 }} /> Refresh Prediction
      </button>
    </div>
  )
}
