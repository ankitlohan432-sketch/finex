import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Pause, Zap, Brain } from 'lucide-react'

export default function PredictionCard({ symbol, market }) {
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchPrediction()
    const interval = setInterval(fetchPrediction, 60000) // Update every 1 min
    return () => clearInterval(interval)
  }, [symbol, market])

  const fetchPrediction = async () => {
    try {
      setLoading(true)
      const url = `/predict/ensemble/${market.toLowerCase()}/${symbol}`
      const res = await fetch(url)
      const data = await res.json()
      setPrediction(data)
      setError(null)
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

  const signalColor = signal === 'BUY' ? 'var(--success)' : signal === 'SELL' ? 'var(--danger)' : 'var(--text-secondary)'
  const signalIcon = signal === 'BUY' ? <TrendingUp size={24} /> : signal === 'SELL' ? <TrendingDown size={24} /> : <Pause size={24} />

  const confidencePercent = Math.round(confidence * 100)

  return (
    <div className="card" style={{ background: 'rgba(0,229,255,0.05)', borderLeft: `4px solid ${signalColor}` }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
        <Brain size={20} style={{ color: 'var(--accent)' }} />
        <h3 style={{ margin: 0, fontSize: 14, fontWeight: 700, color: 'var(--text-primary)' }}>AI Prediction</h3>
        <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--text-muted)' }}>Updated now</span>
      </div>

      {/* Main Signal */}
      <div style={{ textAlign: 'center', marginBottom: 16, paddingBottom: 16, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <div style={{ color: signalColor, fontSize: 28, display: 'flex' }}>
            {signalIcon}
          </div>
          <div style={{ color: signalColor, fontSize: 24, fontWeight: 800 }}>
            {signal}
          </div>
        </div>
        <div style={{ fontSize: 28, fontWeight: 700, color: 'var(--text-primary)' }}>
          {confidencePercent}%
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
          Confidence Score
        </div>
      </div>

      {/* Model Scores */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 8, letterSpacing: 0.5 }}>
          Model Scores
        </div>

        {/* ML Score */}
        <div style={{ marginBottom: 10 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>ML (RF + XGBoost)</span>
            <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent)' }}>{(mlScore * 100).toFixed(0)}%</span>
          </div>
          <div style={{ 
            width: '100%', 
            height: 6, 
            background: 'rgba(255,255,255,0.1)', 
            borderRadius: 3,
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${mlScore * 100}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #00e5a0, #00e5ff)',
              transition: 'width 0.3s'
            }} />
          </div>
        </div>

        {/* DL Score */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>DL (LSTM + GRU)</span>
            <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--accent)' }}>{(dlScore * 100).toFixed(0)}%</span>
          </div>
          <div style={{ 
            width: '100%', 
            height: 6, 
            background: 'rgba(255,255,255,0.1)', 
            borderRadius: 3,
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${dlScore * 100}%`,
              height: '100%',
              background: 'linear-gradient(90deg, #6366f1, #a855f7)',
              transition: 'width 0.3s'
            }} />
          </div>
        </div>
      </div>

      {/* Details */}
      <div style={{ fontSize: 11, color: 'var(--text-muted)', background: 'rgba(0,0,0,0.2)', padding: 8, borderRadius: 6, lineHeight: '1.6' }}>
        <div style={{ marginBottom: 4 }}>
          <strong style={{ color: 'var(--text-secondary)' }}>Combined Score:</strong> {(prediction.final_prediction?.combined_score * 100).toFixed(0)}%
        </div>
        <div>
          <strong style={{ color: 'var(--text-secondary)' }}>Model Type:</strong> Ensemble (ML + DL)
        </div>
      </div>

      {/* Refresh Button */}
      <button
        onClick={fetchPrediction}
        style={{
          width: '100%',
          marginTop: 12,
          padding: 8,
          borderRadius: 6,
          background: 'rgba(0,229,255,0.1)',
          border: '1px solid rgba(0,229,255,0.2)',
          color: 'var(--accent)',
          cursor: 'pointer',
          fontSize: 11,
          fontWeight: 600,
          transition: 'all 0.2s'
        }}
        onMouseEnter={(e) => e.target.style.background = 'rgba(0,229,255,0.2)'}
        onMouseLeave={(e) => e.target.style.background = 'rgba(0,229,255,0.1)'}
      >
        <Zap size={12} style={{ display: 'inline', marginRight: 4 }} /> Refresh Prediction
      </button>
    </div>
  )
}
