import { useEffect, useState, useRef, useCallback } from 'react'
import { cryptoAPI } from '../services/api'
import { TrendingUp, TrendingDown, RefreshCw, ChevronDown, Bitcoin, Brain } from 'lucide-react'

const INTERVALS = ['1m','5m','15m','1h','4h','1d','1w']
const PAGE_SIZE  = 10
const API_BASE   = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const predictionCache = {}

function CandleChart({ candles }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !candles || candles.length === 0) return
    
    const loadChart = async () => {
      await new Promise(r => setTimeout(r, 150))
      
      if (!window.LightweightCharts) {
        console.warn('LightweightCharts not loaded')
        return
      }
      
      if (chartRef.current) { 
        try {
          chartRef.current.remove()
        } catch (e) {}
        chartRef.current = null 
      }
      
      try {
        const chart = window.LightweightCharts.createChart(ref.current, {
          width:  ref.current.clientWidth,
          height: 320,
          layout: { background: { color: '#1a1a1a' }, textColor: '#d1d5db' },
          grid:   { vertLines: { color: '#2d3748' }, horzLines: { color: '#2d3748' } },
          crosshair: { mode: 1 },
          rightPriceScale: { borderColor: '#4b5563' },
          timeScale: { borderColor: '#4b5563', timeVisible: true },
        })

        const series = chart.addCandlestickSeries({
          upColor: '#10b981', 
          downColor: '#ef4444',
          borderUpColor: '#10b981', 
          borderDownColor: '#ef4444',
          wickUpColor: '#10b981', 
          wickDownColor: '#ef4444',
        })

        const candleData = candles
          .map(c => {
            const timeMs = typeof c.time === 'number' ? c.time : parseInt(c.time || 0)
            const timeSec = timeMs > 10000000000 ? Math.floor(timeMs / 1000) : timeMs
            
            return {
              time: timeSec,
              open: parseFloat(c.open || 0),
              high: parseFloat(c.high || 0),
              low: parseFloat(c.low || 0),
              close: parseFloat(c.close || 0),
            }
          })
          .filter(c => !isNaN(c.open) && !isNaN(c.high) && !isNaN(c.low) && !isNaN(c.close) && c.time && c.open > 0)
          .sort((a, b) => a.time - b.time)
          .slice(-100)

        if (candleData.length > 1) {
          series.setData(candleData)
          chart.timeScale().fitContent()
          chartRef.current = chart
          
          const ro = new ResizeObserver(() => {
            try {
              if (ref.current && chartRef.current) {
                chartRef.current.resize(ref.current.clientWidth, 320)
              }
            } catch (e) {}
          })
          ro.observe(ref.current)
          
          return () => {
            try { ro.disconnect() } catch (e) {}
          }
        } else {
          console.warn('Insufficient candle data:', candleData.length)
        }
      } catch (e) {
        console.error('Chart render error:', e)
      }
    }
    
    loadChart()
    
    return () => { 
      if (chartRef.current) { 
        try {
          chartRef.current.remove()
        } catch (e) {}
        chartRef.current = null 
      } 
    }
  }, [candles])

  return <div ref={ref} style={{ width:'100%', height:320, borderRadius:8, overflow:'hidden', background:'#0f0f0f' }} />
}

function PredictionBadge({ symbol }) {
  const [pred, setPred] = useState(predictionCache[symbol] || null)
  const [loading, setLoading] = useState(!predictionCache[symbol])

  useEffect(() => {
    if (!symbol) return
    
    if (predictionCache[symbol]) {
      setPred(predictionCache[symbol])
      setLoading(false)
      return
    }
    
    setLoading(true)
    
    const fetchPred = async (attempt = 0) => {
      try {
        const response = await fetch(`${API_BASE}/predict/crypto/${symbol}?interval=1h`, {
          headers: { 'Accept': 'application/json' }
        })
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        
        const data = await response.json()
        
        if (data && data.signal && data.confidence) {
          predictionCache[symbol] = data
          setPred(data)
          setLoading(false)
        } else if (attempt < 3) {
          setTimeout(() => fetchPred(attempt + 1), 800)
        } else {
          setPred(null)
          setLoading(false)
        }
      } catch (e) {
        console.log(`Prediction failed for ${symbol} (attempt ${attempt}):`, e.message)
        if (attempt < 3) {
          setTimeout(() => fetchPred(attempt + 1), 800)
        } else {
          setPred(null)
          setLoading(false)
        }
      }
    }
    
    fetchPred(0)
  }, [symbol])

  if (loading) return <span style={{ fontSize:11, color:'#9ca3af' }}>...</span>
  if (!pred) return <span style={{ fontSize:11, color:'#9ca3af' }}>—</span>

  return (
    <span style={{
      fontSize:11, 
      fontWeight:700, 
      padding:'4px 10px', 
      borderRadius:20,
      background: (pred.color || '#3b82f6') + '22', 
      color: pred.color || '#3b82f6', 
      border:`1px solid ${(pred.color || '#3b82f6') + '55}`
    }}>
      {pred.signal || '?'} {pred.confidence || '0'}%
    </span>
  )
}

function PredictionPanel({ symbol }) {
  const [pred, setPred] = useState(predictionCache[symbol] || null)
  const [loading, setLoading] = useState(!predictionCache[symbol])
  const [interval, setInterval] = useState('1h')

  const loadPred = useCallback(async (intv, attempt = 0) => {
    if (!symbol) return
    
    try {
      const cacheKey = `${symbol}_${intv}`
      if (predictionCache[cacheKey]) {
        setPred(predictionCache[cacheKey])
        setLoading(false)
        return
      }
      
      const response = await fetch(`${API_BASE}/predict/crypto/${symbol}?interval=${intv}`, {
        headers: { 'Accept': 'application/json' }
      })
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      const data = await response.json()
      
      if (data && data.signal && data.confidence) {
        predictionCache[cacheKey] = data
        setPred(data)
        setLoading(false)
      } else if (attempt < 3) {
        setTimeout(() => loadPred(intv, attempt + 1), 800)
      } else {
        setPred(null)
        setLoading(false)
      }
    } catch (e) {
      console.log(`Panel prediction failed for ${symbol} (attempt ${attempt}):`, e.message)
      if (attempt < 3) {
        setTimeout(() => loadPred(intv, attempt + 1), 800)
      } else {
        setPred(null)
        setLoading(false)
      }
    }
  }, [symbol])

  useEffect(() => {
    setLoading(true)
    loadPred(interval, 0)
  }, [symbol, interval, loadPred])

  if (loading) return (
    <div className="card" style={{ marginBottom:12, textAlign:'center', padding:20 }}>
      <span style={{ color:'#9ca3af', fontSize:13 }}>🤖 Loading...</span>
    </div>
  )

  if (!pred) return null

  return (
    <div className="card" style={{ marginBottom:12 }}>
      <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:12 }}>
        <Brain size:16 style={{ color:'var(--accent)' }} />
        <span style={{ fontWeight:700, fontSize:14 }}>AI Prediction</span>
        <div style={{ marginLeft:'auto', display:'flex', gap:4 }}>
          {['5m','15m','1h','4h','1d'].map(i => (
            <button key={i} onClick={() => { setInterval(i); loadPred(i, 0) }}
              style={{ fontSize:10, padding:'4px 8px', borderRadius:4, border:'1px solid var(--border-light)',
                background: interval===i ? 'var(--accent)' : 'transparent',
                color: interval===i ? '#fff' : 'var(--text-muted)', cursor:'pointer', transition:'all 0.2s' }}>
              {i}
            </button>
          ))}
        </div>
      </div>

      <div style={{ textAlign:'center', marginBottom:16 }}>
        <div style={{ fontSize:28, fontWeight:900, color:pred.color || '#3b82f6' }}>{pred.signal || '?'}</div>
        <div style={{ fontSize:12, color:'var(--text-muted)' }}>Confidence: {pred.confidence || 0}%</div>
        <div style={{ background:'var(--bg-card-high)', borderRadius:8, height:6, marginTop:8, overflow:'hidden' }}>
          <div style={{ width:`${Math.min(pred.confidence || 0, 100)}%`, height:6, borderRadius:8, background:pred.color || '#3b82f6', transition:'width 0.5s' }} />
        </div>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:12 }}>
        {[
          ['Predicted Price', `$${(pred.predicted_price || 0).toLocaleString()}`, pred.color || '#3b82f6'],
          ['Expected Change', `${(pred.change_pct || 0) >= 0 ? '+' : ''}${pred.change_pct || 0}%`, pred.color || '#3b82f6'],
          ['RSI', pred.rsi || 'N/A', (pred.rsi || 0) > 70 ? '#ef4444' : (pred.rsi || 0) < 30 ? '#10b981' : '#f59e0b'],
          ['Momentum', `${(pred.momentum || 0) >= 0 ? '+' : ''}${pred.momentum || 0}%`, (pred.momentum || 0) >= 0 ? '#10b981' : '#ef4444'],
        ].map(([label, val, color]) => (
          <div key={label} style={{ background:'var(--bg-card-high)', borderRadius:8, padding:'10px 12px' }}>
            <div style={{ fontSize:11, color:'var(--text-muted)', marginBottom:3 }}>{label}</div>
            <div style={{ fontFamily:'monospace', fontWeight:600, color, fontSize:13 }}>{val}</div>
          </div>
        ))}
      </div>

      {pred.reasons && Array.isArray(pred.reasons) && pred.reasons.length > 0 && (
        <div style={{ fontSize:11, color:'var(--text-muted)', borderTop:'1px solid var(--border-light)', paddingTop:10 }}>
          {pred.reasons.slice(0, 3).map((r, i) => (
            <div key={i} style={{ padding:'4px 0' }}>📊 {r}</div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function CryptoMarket() {
  const [tickers,   setTickers]   = useState([])
  const [page,      setPage]      = useState(0)
  const [hasMore,   setHasMore]   = useState(true)
  const [loading,   setLoading]   = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)
  const [selected,  setSelected]  = useState(null)
  const [candles,   setCandles]   = useState([])
  const [interval,  setInterval]  = useState('1d')
  const [candleLoading, setCandleLoading] = useState(false)
  const [scriptLoaded, setScriptLoaded]   = useState(false)

  useEffect(() => {
    if (window.LightweightCharts) { 
      setScriptLoaded(true)
      return 
    }
    const s = document.createElement('script')
    s.src = 'https://cdn.jsdelivr.net/npm/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js'
    s.onload = () => {
      console.log('Chart library loaded')
      setScriptLoaded(true)
    }
    s.onerror = () => {
      console.error('Chart library failed to load')
      setScriptLoaded(false)
    }
    document.head.appendChild(s)
  }, [])

  const loadTickers = useCallback(async (reset = false) => {
    const nextPage = reset ? 0 : page
    if (reset) setLoading(true); else setLoadingMore(true)
    
    try {
      const res = await cryptoAPI.tickers(nextPage, PAGE_SIZE)
      const data = res.data || []
      
      if (reset) { 
        setTickers(data)
        setPage(1)
      } else { 
        setTickers(prev => [...prev, ...data])
        setPage(p => p + 1)
      }
      setHasMore(data.length === PAGE_SIZE)
    } catch(e) {
      console.error('Ticker load error:', e)
      setHasMore(false)
    } finally { 
      setLoading(false)
      setLoadingMore(false) 
    }
  }, [page])

  useEffect(() => { 
    loadTickers(true) 
  }, [])

  const loadCandles = async (sym, intv) => {
    setCandleLoading(true)
    try {
      const symbolId = sym.cg_id || sym.symbol || sym.binance_symbol
      console.log('Loading candles for:', symbolId, 'interval:', intv)
      
      const res = await cryptoAPI.klines(symbolId, intv, 200)
      const data = res.data || []
      
      console.log('Received candle data:', data.length, 'candles')
      setCandles(data)
    } catch(e) {
      console.error('Candle load error:', e)
      setCandles([])
    } finally { 
      setCandleLoading(false) 
    }
  }

  const selectTicker = (t) => { 
    console.log('Selected ticker:', t.symbol)
    setSelected(t)
    loadCandles(t, interval) 
  }

  const changeInterval = (intv) => { 
    setInterval(intv)
    if (selected) loadCandles(selected, intv) 
  }

  const fmt = (n) => {
    if (!n || n === 0) return 'N/A'
    if (n >= 1e9) return `$${(n/1e9).toFixed(2)}B`
    if (n >= 1e6) return `$${(n/1e6).toFixed(2)}M`
    if (n >= 1e3) return `$${n.toLocaleString('en-US', {minimumFractionDigits:2,maximumFractionDigits:2})}`
    return `$${Number(n).toFixed(n < 0.01 ? 6 : 2)}`
  }

  const pctColor = (v) => v >= 0 ? 'var(--success)' : 'var(--danger)'

  return (
    <div>
      <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:20 }}>
        <Bitcoin size={22} style={{ color:'var(--warning)' }} />
        <h2 style={{ fontSize:20, fontWeight:700, color:'var(--text-primary)' }}>Crypto Markets</h2>
        <span style={{ fontSize:12, color:'var(--text-muted)', background:'var(--bg-card-high)', padding:'4px 12px', borderRadius:20 }}>Live + AI Predictions</span>
        <button className="btn btn-ghost btn-sm" style={{ marginLeft:'auto' }} onClick={() => loadTickers(true)}>
          <RefreshCw size={12} />
        </button>
      </div>

      <div className="grid-2-1">
        {/* Ticker list */}
        <div className="card" style={{ padding:0 }}>
          <div style={{ overflowX:'auto' }}>
            <table style={{ width:'100%' }}>
              <thead>
                <tr>
                  <th style={{ padding:'12px 16px', textAlign:'left' }}>Coin</th>
                  <th style={{ padding:'12px 16px', textAlign:'right' }}>Price</th>
                  <th style={{ padding:'12px 16px', textAlign:'right' }}>24h %</th>
                  <th style={{ padding:'12px 16px', textAlign:'right' }}>High</th>
                  <th style={{ padding:'12px 16px', textAlign:'right' }}>Low</th>
                  <th style={{ padding:'12px 16px', textAlign:'right' }}>Volume</th>
                  <th style={{ padding:'12px 16px', textAlign:'right' }}> AI Signal</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={7} style={{ textAlign:'center', padding:40, color:'var(--text-muted)' }}>Loading crypto data...</td></tr>
                ) : tickers.length === 0 ? (
                  <tr><td colSpan={7} style={{ textAlign:'center', padding:40, color:'var(--text-muted)' }}>No data. Click refresh →</td></tr>
                ) : tickers.map((t, i) => (
                  <tr key={t.binance_symbol || i}
                    onClick={() => selectTicker(t)}
                    style={{ cursor:'pointer', background: selected?.binance_symbol === t.binance_symbol ? 'var(--accent-light)' : 'transparent', transition:'background 0.15s' }}>
                    <td style={{ padding:'10px 16px' }}>
                      {t.image && <img src={t.image} alt={t.symbol} style={{ width:20, height:20, borderRadius:'50%', marginRight:8, verticalAlign:'middle' }} />}
                      <span style={{ fontWeight:600, color:'var(--text-primary)', fontFamily:'monospace' }}>{t.symbol}</span>
                      <div style={{ fontSize:11, color:'var(--text-muted)' }}>{t.name}</div>
                    </td>
                    <td style={{ padding:'10px 16px', textAlign:'right', fontFamily:'monospace', fontWeight:500 }}>{fmt(t.price)}</td>
                    <td style={{ padding:'10px 16px', textAlign:'right' }}>
                      <span style={{ color:pctColor(t.change_percent), fontFamily:'monospace', fontSize:13 }}>
                        {t.change_percent >= 0 ? '+' : ''}{(t.change_percent || 0).toFixed(2)}%
                      </span>
                    </td>
                    <td style={{ padding:'10px 16px', textAlign:'right', fontFamily:'monospace', fontSize:12, color:'var(--success)' }}>{fmt(t.high)}</td>
                    <td style={{ padding:'10px 16px', textAlign:'right', fontFamily:'monospace', fontSize:12, color:'var(--danger)' }}>{fmt(t.low)}</td>
                    <td style={{ padding:'10px 16px', textAlign:'right', fontSize:12, color:'var(--text-muted)' }}>{fmt(t.quote_volume)}</td>
                    <td style={{ padding:'10px 16px', textAlign:'right' }}>
                      <PredictionBadge symbol={t.binance_symbol} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {hasMore && !loading && (
            <div style={{ padding:'12px 16px', textAlign:'center', borderTop:'1px solid var(--border-light)' }}>
              <button className="btn btn-ghost btn-sm" onClick={() => {
                const nextPage = tickers.length / PAGE_SIZE
                setLoadingMore(true)
                cryptoAPI.tickers(nextPage, PAGE_SIZE)
                  .then(res => { 
                    const data = res.data || []
                    setTickers(prev => [...prev, ...data])
                    setHasMore(data.length === PAGE_SIZE) 
                  })
                  .catch(e => {
                    console.error('Load more error:', e)
                    setHasMore(false)
                  })
                  .finally(() => setLoadingMore(false))
              }} disabled={loadingMore} style={{ gap:6 }}>
                <ChevronDown size={14} />
                {loadingMore ? 'Loading...' : 'Load More Coins'}
              </button>
            </div>
          )}
        </div>

        {/* Right panel */}
        <div>
          {selected ? (
            <>
              <PredictionPanel symbol={selected.binance_symbol} />

              <div className="card">
                <div style={{ marginBottom:12 }}>
                  <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start' }}>
                    <div>
                      {selected.image && <img src={selected.image} alt="" style={{ width:32, height:32, borderRadius:'50%', marginBottom:4 }} />}
                      <div style={{ fontSize:18, fontWeight:700, color:'var(--text-primary)', fontFamily:'monospace' }}>{selected.symbol}/USDT</div>
                      <div style={{ fontSize:12, color:'var(--text-muted)' }}>{selected.name}</div>
                    </div>
                    <div style={{ textAlign:'right' }}>
                      <div style={{ fontSize:22, fontWeight:700, color:'var(--accent)', fontFamily:'monospace' }}>{fmt(selected.price)}</div>
                      <div style={{ fontSize:13, color:pctColor(selected.change_percent), fontFamily:'monospace' }}>
                        {selected.change_percent >= 0 ? '+' : ''}{(selected.change_percent || 0).toFixed(2)}%
                      </div>
                    </div>
                  </div>
                </div>

                <div style={{ display:'flex', gap:4, marginBottom:12, flexWrap:'wrap' }}>
                  {INTERVALS.map(intv => (
                    <button key={intv} className="btn btn-ghost btn-sm mono"
                      style={{ padding:'4px 10px', fontSize:11,
                        background: interval===intv ? 'var(--accent-light)' : undefined,
                        color: interval===intv ? 'var(--accent)' : undefined,
                        borderColor: interval===intv ? 'var(--accent)' : undefined }}
                      onClick={() => changeInterval(intv)}>{intv}</button>
                  ))}
                </div>

                <div style={{ position:'relative', minHeight:320, borderRadius:8 }}>
                  {candleLoading && (
                    <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center', background:'rgba(15,15,15,0.85)', zIndex:2, borderRadius:8 }}>
                      <span style={{ color:'var(--text-muted)', fontSize:13 }}>⏳ Loading chart...</span>
                    </div>
                  )}
                  {scriptLoaded && candles.length > 1 && <CandleChart candles={candles} />}
                  {scriptLoaded && candles.length <= 1 && !candleLoading && <div style={{ height:320, display:'flex', alignItems:'center', justifyContent:'center', color:'var(--text-muted)', background:'#0f0f0f', borderRadius:8, fontSize:13 }}>No chart data - API might not have candles yet</div>}
                  {!scriptLoaded && <div style={{ height:320, display:'flex', alignItems:'center', justifyContent:'center', color:'var(--text-muted)', background:'#0f0f0f', borderRadius:8 }}>⏳ Loading chart library...</div>}
                </div>

                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginTop:12 }}>
                  {[
                    ['24h High', fmt(selected.high), 'var(--success)'],
                    ['24h Low',  fmt(selected.low),  'var(--danger)'],
                    ['Volume',   fmt(selected.volume), 'var(--text-secondary)'],
                    ['24h Change', `${selected.change >= 0 ? '+' : ''}${fmt(selected.change)}`, pctColor(selected.change_percent)],
                  ].map(([label, val, color]) => (
                    <div key={label} style={{ background:'var(--bg-card-high)', borderRadius:8, padding:'10px 12px' }}>
                      <div style={{ fontSize:11, color:'var(--text-muted)', marginBottom:3 }}>{label}</div>
                      <div style={{ fontFamily:'monospace', fontWeight:600, color }}>{val}</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="card" style={{ textAlign:'center', padding:'60px 20px' }}>
              <Bitcoin size={40} style={{ color:'var(--warning)', opacity:0.3, marginBottom:12 }} />
              <p style={{ color:'var(--text-muted)', fontSize:13 }}>Select a coin to view chart and AI prediction</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}