﻿import { useEffect, useState, useRef, useCallback } from 'react'
import { bseAPI } from '../services/api'
import PredictionCard from '../components/PredictionCard'
import { Building2, RefreshCw, ChevronDown, TrendingUp, TrendingDown } from 'lucide-react'

const INTERVALS = ['1h', '1d', '1wk']
const PAGE_SIZE  = 10

function CandleChart({ candles }) {
  const ref = useRef(null)
  const chartRef = useRef(null)

  useEffect(() => {
    if (!ref.current || !candles || candles.length === 0) return
    if (!window.LightweightCharts) return
    if (chartRef.current) { chartRef.current.remove(); chartRef.current = null }
    const chart = window.LightweightCharts.createChart(ref.current, {
      width:  ref.current.clientWidth,
      height: 300,
      layout: { background: { color: '#1e2020' }, textColor: '#849396' },
      grid:   { vertLines: { color: '#282a2b' }, horzLines: { color: '#282a2b' } },
      crosshair: { mode: 1 },
      rightPriceScale: { borderColor: '#3b494c' },
      timeScale: { borderColor: '#3b494c', timeVisible: true },
    })
    const series = chart.addCandlestickSeries({
      upColor:'#00e5a0', downColor:'#ff6b6b',
      borderUpColor:'#00e5a0', borderDownColor:'#ff6b6b',
      wickUpColor:'#00e5a0', wickDownColor:'#ff6b6b',
    })
    series.setData(candles.map(c => ({ time:c.time, open:c.open, high:c.high, low:c.low, close:c.close })))
    chart.timeScale().fitContent()
    chartRef.current = chart
    const ro = new ResizeObserver(() => {
      if (ref.current && chartRef.current) chartRef.current.resize(ref.current.clientWidth, 300)
    })
    ro.observe(ref.current)
    return () => { if (chartRef.current) { chartRef.current.remove(); chartRef.current = null } }
  }, [candles])

  return <div ref={ref} style={{ width:'100%', height:300, borderRadius:8, overflow:'hidden' }} />
}

export default function BSEMarket() {
  const [tickers,  setTickers]  = useState([])
  const [page,     setPage]     = useState(0)
  const [hasMore,  setHasMore]  = useState(true)
  const [loading,  setLoading]  = useState(false)
  const [loadingMore, setLoadingMore] = useState(false)
  const [selected, setSelected] = useState(null)
  const [candles,  setCandles]  = useState([])
  const [interval, setInterval] = useState('1d')
  const [candleLoading, setCandleLoading] = useState(false)
  const [scriptLoaded,  setScriptLoaded]  = useState(false)

  useEffect(() => {
    if (window.LightweightCharts) { setScriptLoaded(true); return }
    const s = document.createElement('script')
    s.src = 'https://unpkg.com/lightweight-charts@4.1.1/dist/lightweight-charts.standalone.production.js'
    s.onload = () => setScriptLoaded(true)
    document.head.appendChild(s)
  }, [])

  const loadData = async (reset = false) => {
    const nextPage = reset ? 0 : page
    if (reset) setLoading(true); else setLoadingMore(true)
    try {
      const tickRes = await bseAPI.tickers(nextPage, PAGE_SIZE)
      const data = tickRes.data || []
      if (reset) { setTickers(data); setPage(1) }
      else { setTickers(prev => [...prev, ...data]); setPage(p => p + 1) }
      setHasMore(data.length === PAGE_SIZE)
    } finally { setLoading(false); setLoadingMore(false) }
  }

  useEffect(() => { loadData(true) }, [])

  const loadCandles = async (symbol, intv) => {
    setCandleLoading(true)
    try {
      const res = await bseAPI.klines(symbol, intv)
      setCandles(res.data || [])
    } finally { setCandleLoading(false) }
  }

  const selectTicker = (t) => { setSelected(t); loadCandles(t.symbol, interval) }
  const changeInterval = (intv) => { setInterval(intv); if (selected) loadCandles(selected.symbol, intv) }

  const inr = (n) => n && n > 0 ? `â‚¹${Number(n).toLocaleString('en-IN', {minimumFractionDigits:2,maximumFractionDigits:2})}` : 'N/A'
  const pctColor = (v) => v >= 0 ? 'var(--success)' : 'var(--danger)'

  return (
    <div>
      {/* Header */}
      <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:16 }}>
        <Building2 size={22} style={{ color:'var(--accent)' }} />
        <h1 style={{ margin:0, fontSize:24, fontWeight:700, color:'var(--text-primary)' }}>BSE Live Market</h1>
        <button onClick={() => loadData(true)} style={{ marginLeft:'auto', background:'none', border:'none', cursor:'pointer', color:'var(--accent)', transition:'opacity 0.2s' }} disabled={loading}>
          <RefreshCw size={16} style={{ opacity:loading ? 0.5 : 1 }} />
        </button>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:20, marginTop:20 }}>
        {/* Tickers List */}
        <div className="card" style={{ maxHeight:'70vh', overflow:'auto' }}>
          <h3 style={{ margin:'0 0 12px 0', fontSize:14, fontWeight:600, color:'var(--text-primary)' }}>Stocks</h3>
          {loading ? (
            <div style={{ textAlign:'center', color:'var(--text-muted)', padding:20 }}>Loading...</div>
          ) : tickers.length === 0 ? (
            <div style={{ textAlign:'center', color:'var(--text-muted)', padding:20 }}>No data</div>
          ) : (
            <>
              {tickers.map(t => (
                <div
                  key={t.symbol}
                  onClick={() => selectTicker(t)}
                  style={{
                    padding:12,
                    borderRadius:8,
                    cursor:'pointer',
                    marginBottom:8,
                    background:selected?.symbol === t.symbol ? 'rgba(0,229,255,0.1)' : 'rgba(255,255,255,0.02)',
                    border:`1px solid ${selected?.symbol === t.symbol ? 'rgba(0,229,255,0.3)' : 'rgba(255,255,255,0.05)'}`,
                    transition:'all 0.15s'
                  }}
                  onMouseEnter={(e) => { if (selected?.symbol !== t.symbol) e.currentTarget.style.background = 'rgba(255,255,255,0.05)' }}
                  onMouseLeave={(e) => { if (selected?.symbol !== t.symbol) e.currentTarget.style.background = 'rgba(255,255,255,0.02)' }}
                >
                  <div style={{ display:'flex', justifyContent:'space-between', alignItems:'start' }}>
                    <div>
                      <div style={{ fontSize:13, fontWeight:600, color:'var(--text-primary)' }}>{t.symbol}</div>
                      <div style={{ fontSize:11, color:'var(--text-muted)', marginTop:2 }}>{t.name}</div>
                    </div>
                    <div style={{ textAlign:'right' }}>
                      <div style={{ fontSize:13, fontWeight:700, color:'var(--text-primary)' }}>{inr(t.price)}</div>
                      <div style={{ fontSize:11, fontWeight:600, color:pctColor(t.change_percent), marginTop:2, display:'flex', alignItems:'center', justifyContent:'flex-end', gap:3 }}>
                        {t.change_percent >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                        {Math.abs(t.change_percent).toFixed(2)}%
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {hasMore && (
                <button
                  onClick={() => loadData(false)}
                  disabled={loadingMore}
                  style={{
                    width:'100%',
                    padding:10,
                    marginTop:12,
                    borderRadius:8,
                    background:'rgba(0,229,255,0.1)',
                    border:'1px solid rgba(0,229,255,0.2)',
                    color:'var(--accent)',
                    cursor:'pointer',
                    fontWeight:600,
                    fontSize:12,
                    opacity:loadingMore ? 0.5 : 1
                  }}
                >
                  {loadingMore ? 'Loading...' : 'Load More'}
                </button>
              )}
            </>
          )}
        </div>

        {/* Detail Panel */}
        <div style={{ display:'flex', flexDirection:'column', gap:16 }}>
          {selected ? (
            <>
              {/* Prediction Card */}
              <PredictionCard symbol={selected.symbol} market="bse" />

              {/* Ticker Info */}
              <div className="card">
                <div style={{ marginBottom:16 }}>
                  <h2 style={{ margin:'0 0 4px 0', fontSize:20, fontWeight:700, color:'var(--text-primary)' }}>{selected.name}</h2>
                  <p style={{ margin:0, fontSize:13, color:'var(--text-muted)' }}>{selected.symbol}</p>
                </div>
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:12 }}>
                  <div>
                    <div style={{ fontSize:11, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:0.5 }}>Price</div>
                    <div style={{ fontSize:18, fontWeight:700, color:'var(--text-primary)', marginTop:4 }}>{inr(selected.price)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize:11, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:0.5 }}>24h Change</div>
                    <div style={{ fontSize:18, fontWeight:700, color:pctColor(selected.change_percent), marginTop:4 }}>
                      {selected.change_percent >= 0 ? '🤖' : '❌'} {Math.abs(selected.change_percent).toFixed(2)}%
                    </div>
                  </div>
                </div>
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:12, marginTop:16, paddingTop:16, borderTop:'1px solid rgba(255,255,255,0.05)' }}>
                  <div>
                    <div style={{ fontSize:10, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:0.5 }}>High</div>
                    <div style={{ fontSize:12, fontWeight:600, color:'var(--text-primary)', marginTop:4 }}>{inr(selected.high)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize:10, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:0.5 }}>Low</div>
                    <div style={{ fontSize:12, fontWeight:600, color:'var(--text-primary)', marginTop:4 }}>{inr(selected.low)}</div>
                  </div>
                  <div>
                    <div style={{ fontSize:10, color:'var(--text-muted)', textTransform:'uppercase', letterSpacing:0.5 }}>Volume</div>
                    <div style={{ fontSize:12, fontWeight:600, color:'var(--text-primary)', marginTop:4 }}>{(selected.volume / 1e6).toFixed(2)}M</div>
                  </div>
                </div>
              </div>

              {/* Chart */}
              {scriptLoaded && (
                <>
                  <div className="card">
                    <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12 }}>
                      <h3 style={{ margin:0, fontSize:14, fontWeight:600, color:'var(--text-primary)' }}>Chart</h3>
                      <div style={{ display:'flex', gap:6 }}>
                        {INTERVALS.map(iv => (
                          <button
                            key={iv}
                            onClick={() => changeInterval(iv)}
                            style={{
                              padding:'4px 10px',
                              borderRadius:6,
                              fontSize:11,
                              fontWeight:600,
                              cursor:'pointer',
                              background:interval === iv ? 'var(--accent)' : 'rgba(255,255,255,0.05)',
                              color:interval === iv ? '#001f24' : 'var(--text-secondary)',
                              border:'none',
                              transition:'all 0.15s'
                            }}
                          >
                            {iv}
                          </button>
                        ))}
                      </div>
                    </div>
                    {candleLoading ? (
                      <div style={{ height:300, display:'flex', alignItems:'center', justifyContent:'center', color:'var(--text-muted)' }}>
                        Loading chart...
                      </div>
                    ) : candles.length > 0 ? (
                      <CandleChart candles={candles} />
                    ) : (
                      <div style={{ height:300, display:'flex', alignItems:'center', justifyContent:'center', color:'var(--text-muted)' }}>
                        No data available
                      </div>
                    )}
                  </div>
                </>
              )}
            </>
          ) : (
            <div className="card" style={{ display:'flex', alignItems:'center', justifyContent:'center', height:300, color:'var(--text-muted)', textAlign:'center' }}>
              <p>Select a stock to view details and chart</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

