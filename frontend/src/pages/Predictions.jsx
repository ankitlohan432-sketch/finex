import { useEffect, useState } from 'react'
import { TrendingUp, TrendingDown, Zap, AlertCircle } from 'lucide-react'

const signalColors = {
  "BUY": { bg: "rgba(0, 229, 160, 0.1)", border: "rgba(0, 229, 160, 0.3)", text: "#00e5a0", icon: TrendingUp },
  "SELL": { bg: "rgba(255, 107, 107, 0.1)", border: "rgba(255, 107, 107, 0.3)", text: "#ff6b6b", icon: TrendingDown },
  "HOLD": { bg: "rgba(251, 191, 36, 0.1)", border: "rgba(251, 191, 36, 0.3)", text: "#fbbf24", icon: AlertCircle }
}

function PredictionBox({ prediction }) {
  const config = signalColors[prediction.signal] || signalColors["HOLD"]
  const Icon = config.icon
  
  return (
    <div
      style={{
        background: config.bg,
        border: `2px solid ${config.border}`,
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        cursor: 'pointer',
        transition: 'all 0.2s',
        position: 'relative',
        overflow: 'hidden'
      }}
      onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
      onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
    >
      {/* Gradient background */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `linear-gradient(135deg, ${config.bg} 0%, transparent 100%)`,
        pointerEvents: 'none'
      }} />
      
      <div style={{ position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 12 }}>
          <div>
            <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 4 }}>
              {prediction.name || prediction.symbol}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
              {prediction.market.toUpperCase()} • ${prediction.price?.toFixed(2) || '—'}
            </div>
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            background: config.bg,
            padding: '6px 12px',
            borderRadius: 8,
            border: `1px solid ${config.border}`
          }}>
            <Icon size={16} style={{ color: config.text }} />
            <div style={{ fontSize: 14, fontWeight: 700, color: config.text }}>
              {prediction.signal}
            </div>
          </div>
        </div>
        
        {/* Confidence bar */}
        <div style={{ marginBottom: 12 }}>
          <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4, display: 'flex', justifyContent: 'space-between' }}>
            <span>Confidence</span>
            <span>{(prediction.confidence * 100).toFixed(0)}%</span>
          </div>
          <div style={{
            height: 6,
            background: 'rgba(255,255,255,0.05)',
            borderRadius: 3,
            overflow: 'hidden'
          }}>
            <div style={{
              height: '100%',
              width: `${(prediction.confidence * 100)}%`,
              background: config.text,
              transition: 'width 0.3s'
            }} />
          </div>
        </div>
        
        {/* Reason/Strategy */}
        <div style={{
          fontSize: 12,
          color: 'var(--text-secondary)',
          lineHeight: 1.5,
          padding: 10,
          background: 'rgba(0,0,0,0.2)',
          borderRadius: 8,
          marginBottom: 10
        }}>
          {prediction.reason || 'Analyzing market...'}
        </div>
        
        {/* Change indicator */}
        {prediction.change_percent !== undefined && (
          <div style={{
            fontSize: 13,
            fontWeight: 600,
            color: prediction.change_percent >= 0 ? '#00e5a0' : '#ff6b6b'
          }}>
            {prediction.change_percent >= 0 ? '+' : ''}{prediction.change_percent?.toFixed(2) || '—'}%
          </div>
        )}
      </div>
    </div>
  )
}

export default function Predictions() {
  const [cryptoPreds, setCryptoPreds] = useState([])
  const [nsePreds, setNsePreds] = useState([])
  const [bsePreds, setBsePreds] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('all')

  useEffect(() => {
    loadPredictions()
  }, [])

  const loadPredictions = async () => {
    setLoading(true)
    try {
      const [cryptoRes, nseRes, bseRes, summaryRes] = await Promise.allSettled([
        fetch('http://localhost:8000/predict/predictions/crypto').then(r => r.json()),
        fetch('http://localhost:8000/predict/predictions/nse').then(r => r.json()),
        fetch('http://localhost:8000/predict/predictions/bse').then(r => r.json()),
        fetch('http://localhost:8000/predict/predictions/summary').then(r => r.json())
      ])
      
      setCryptoPreds(cryptoRes.status === 'fulfilled' ? (cryptoRes.value || []) : [])
      setNsePreds(nseRes.status === 'fulfilled' ? (nseRes.value || []) : [])
      setBsePreds(bseRes.status === 'fulfilled' ? (bseRes.value || []) : [])
      setSummary(summaryRes.status === 'fulfilled' ? summaryRes.value : null)
    } catch (e) {
      console.error('Prediction load error:', e)
    } finally {
      setLoading(false)
    }
  }

  const SummaryCard = ({ label, value, color }) => (
    <div className="card" style={{ textAlign: 'center', padding: 20 }}>
      <div style={{ fontSize: 32, fontWeight: 700, color, marginBottom: 8 }}>{value}</div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: 0.5 }}>
        {label}
      </div>
    </div>
  )

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ margin: '0 0 8px 0', fontSize: 24, fontWeight: 700, color: 'var(--text-primary)' }}>
          🤖 Market Predictions
        </h1>
        <p style={{ margin: 0, fontSize: 14, color: 'var(--text-muted)' }}>
          ML/DL buy/sell signals for all markets • Updated every 10 minutes
        </p>
      </div>

      {/* Summary Stats */}
      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 16, marginBottom: 24 }}>
          <SummaryCard label="Buy Signals" value={summary.buy_count} color="#00e5a0" />
          <SummaryCard label="Sell Signals" value={summary.sell_count} color="#ff6b6b" />
          <SummaryCard label="Hold/Wait" value={summary.hold_count} color="#fbbf24" />
          <SummaryCard label="Total Analyzed" value={summary.total} color="var(--accent)" />
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 20, borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: 12 }}>
        {['all', 'crypto', 'nse', 'bse'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '8px 16px',
              borderRadius: 8,
              border: 'none',
              background: activeTab === tab ? 'var(--accent)' : 'rgba(255,255,255,0.05)',
              color: activeTab === tab ? '#001f24' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: 13,
              textTransform: 'uppercase',
              transition: 'all 0.2s'
            }}
          >
            {tab === 'all' ? '📊 All Markets' : tab === 'crypto' ? '₿ Crypto' : tab === 'nse' ? '🇮🇳 NSE' : '📈 BSE'}
          </button>
        ))}
      </div>

      {/* Predictions Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 20 }}>
        {loading ? (
          <div style={{ gridColumn: '1/-1', textAlign: 'center', color: 'var(--text-muted)', padding: 40 }}>
            Loading predictions...
          </div>
        ) : (
          <>
            {/* All Markets */}
            {activeTab === 'all' && (
              <>
                {/* Crypto Section */}
                {cryptoPreds.length > 0 && (
                  <div style={{ gridColumn: '1/-1' }}>
                    <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 12 }}>
                      💰 Cryptocurrency Predictions ({cryptoPreds.length})
                    </h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 16 }}>
                      {cryptoPreds.map(p => <PredictionBox key={p.symbol} prediction={p} />)}
                    </div>
                  </div>
                )}
                
                {/* NSE Section */}
                {nsePreds.length > 0 && (
                  <div style={{ gridColumn: '1/-1' }}>
                    <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 12, marginTop: 24 }}>
                      🇮🇳 NSE Stock Predictions ({nsePreds.length})
                    </h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 16 }}>
                      {nsePreds.map(p => <PredictionBox key={p.symbol} prediction={p} />)}
                    </div>
                  </div>
                )}
                
                {/* BSE Section */}
                {bsePreds.length > 0 && (
                  <div style={{ gridColumn: '1/-1' }}>
                    <h2 style={{ fontSize: 18, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 12, marginTop: 24 }}>
                      📊 BSE Stock Predictions ({bsePreds.length})
                    </h2>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 16 }}>
                      {bsePreds.map(p => <PredictionBox key={p.symbol} prediction={p} />)}
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Crypto Only */}
            {activeTab === 'crypto' && cryptoPreds.map(p => <PredictionBox key={p.symbol} prediction={p} />)}

            {/* NSE Only */}
            {activeTab === 'nse' && nsePreds.map(p => <PredictionBox key={p.symbol} prediction={p} />)}

            {/* BSE Only */}
            {activeTab === 'bse' && bsePreds.map(p => <PredictionBox key={p.symbol} prediction={p} />)}
          </>
        )}
      </div>

      {/* Refresh Button */}
      <button
        onClick={loadPredictions}
        style={{
          position: 'fixed',
          bottom: 30,
          right: 30,
          padding: '12px 24px',
          background: 'var(--accent)',
          color: '#001f24',
          border: 'none',
          borderRadius: 10,
          cursor: 'pointer',
          fontWeight: 600,
          fontSize: 13,
          boxShadow: '0 4px 16px rgba(0, 229, 255, 0.2)'
        }}
      >
        🔄 Refresh Predictions
      </button>
    </div>
  )
}
