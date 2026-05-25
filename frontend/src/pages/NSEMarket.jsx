import { useEffect, useState, useRef, useCallback } from 'react'
import { nseAPI } from '../services/api'
import PredictionCard from '../components/PredictionCard'
import { IndianRupee, RefreshCw, ChevronDown, TrendingUp, TrendingDown } from 'lucide-react'

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

export default function NSEMarket() {
  const [indices,  setIndices]  = useState([])
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
      const [idxRes, tickRes] = await Promise.allSettled([
        reset ? nseAPI.indices() : Promise.resolve(null),
        nseAPI.tickers(nextPage, PAGE_SIZE),
      ])
      if (idxRes.status === 'fulfilled' && idxRes.value) setIndices(idxRes.value.data || [])
      const data = tickRes.status === 'fulfilled' ? (tickRes.value.data || []) : []
      if (reset) { setTickers(data); setPage(1) }
      else { setTickers(prev => [...prev, ...data]); setPage(p => p + 1) }
      setHasMore(data.length === PAGE_SIZE)
    } finally { setLoading(false); setLoadingMore(false) }
  }

  useEffect(() => { loadData(true) }, [])

  const loadCandles = async (symbol, intv) => {
    setCandleLoading(true)
    try {
      const res = await nseAPI.klines(symbol, intv)
      setCandles(res.data || [])
    } finally { setCandleLoading(false) }
  }

  const selectTicker = (t) => { setSelected(t); loadCandles(t.symbol, interval) }
  const changeInterval = (intv) => { setInterval(intv); if (selected) loadCandles(selected.symbol, intv) }

  const inr = (n) => n && n > 0 ? `₹${Number(n).toLocaleString('en-IN', {minimumFractionDigits:2,maximumFractionDigits:2})}` : '—'
  const pctColor = (v) => v >= 0 ? 'var(--success)' : 'var(--danger)'

  return (
    <div>
      {/* Header */}
      <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:16 }}>
        <IndianRupee size={22} style={{ color:'var(--accent)' }} />
        <h2 style={{ fontSize:20, fontWeight:700 }}>NSE — National Stock Exchange</h2>
        <span style={{ fontSize:12, color:'var(--text-muted)', background:'var(--bg-card-high)', padding:'2px 8px', borderRadius:20 }}>via Yahoo Finance</span>
        <button className="btn btn-ghost btn-sm" style={{ marginLeft:'auto' }} onClick={() => loadData(true)}><RefreshCw size={12} /></button>
      </div>

      {/* Indices row */}
      {indices.length > 0 && (
        <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(180px,1fr))', gap:10, marginBottom:16 }}>
          {indices.map((idx, i) => (
            <div key={i} className="stat-card">
              <div className="stat-label">{idx.name}</div>
              <div className="stat-value mono">{idx.price?.toLocaleString('en-IN', {minimumFractionDigits:2}) || '—'}</div>
              <div className={`stat-change ${(idx.change_percent||0) >= 0 ? '' : 'down'}`}>
                {(idx.change_percent||0) >= 0 ? <TrendingUp size={12}/> : <TrendingDown size={12}/>}
                {(idx.change_percent||0) >= 0 ? '+' : ''}{(idx.change_percent||0).toFixed(2)}%
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="grid-2-1">
        {/* Stock list */}
        <div className="card" style={{ padding:0 }}>
          <div style={{ overflowX:'auto' }}>
            <table style={{ width:'100%' }}>
              <thead>
                <tr>
                  <th style={{ padding:'12px 16px', textAlign:'left' }}>Stock</th>
                  <th style={{ padding:'12px 16px', textAlign:'right' }}>Price (₹)</th>
                  <th style={{ padding:'12px 16px', textAlign:'right' }}>Change %</th>
                  <th style={{ padding:'12px 16px', textAlign:'right' }}>High</th>
                  <th style={{ padding:'12px 16px', textAlign:'right' }}>Low</th>
                  <th style={{ padding:'12px 16px', textAlign:'right' }}>Volume</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr><td colSpan={6} style={{ textAlign:'center', padding:40, color:'var(--text-muted)' }}>Fetching NSE data...</td></tr>
                ) : tickers.map((t, i) => (
                  <tr key={t.symbol||i} onClick={() => selectTicker(t)}
                    style={{ cursor:'pointer', background: selected?.symbol === t.symbol ? 'var(--accent-light)' : 'transparent' }}>
                    <td style={{ padding:'10px 16px' }}>
                      <div style={{ fontWeight:600, fontFamily:'monospace', color:'var(--text-primary)' }}>{t.symbol}</div>
                      <div style={{ fontSize:11, color:'var(--text-muted)' }}>{t.name}</div>
                      {t.sector && <div style={{ fontSize:10, color:'var(--accent)', opacity:0.7 }}>{t.sector}</div>}
                    </td>
                    <td style={{ padding:'10px 16px', textAlign:'right', fontFamily:'monospace', fontWeight:500 }}>{inr(t.price)}</td>
                    <td style={{ padding:'10px 16px', textAlign:'right' }}>
                      <span style={{ color:pctColor(t.change_percent||0), fontFamily:'monospace', fontSize:13 }}>
                        {(t.change_percent||0) >= 0 ? '▲' : '▼'} {Math.abs(t.change_percent||0).toFixed(2)}%
                      </span>
                    </td>
                    <td style={{ padding:'10px 16px', textAlign:'right', fontFamily:'monospace', fontSize:12, color:'var(--success)' }}>{inr(t.high)}</td>
                    <td style={{ padding:'10px 16px', textAlign:'right', fontFamily:'monospace', fontSize:12, color:'var(--danger)' }}>{inr(t.low)}</td>
                    <td style={{ padding:'10px 16px', textAlign:'right', fontSize:12, color:'var(--text-muted)' }}>
                      {t.volume > 0 ? `${(t.volume/1e5).toFixed(1)}L` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {hasMore && !loading && (
            <div style={{ padding:'12px 16px', textAlign:'center', borderTop:'1px solid var(--border-light)' }}>
              <button className="btn btn-ghost btn-sm" onClick={() => loadData(false)} disabled={loadingMore} style={{ gap:6 }}>
                <ChevronDown size={14} />
                {loadingMore ? 'Loading...' : 'Load More Stocks'}
              </button>
            </div>
          )}
        </div>

        {/* Chart panel */}
        <div>
          {selected ? (
            <>
              {/* Prediction Card */}
              <PredictionCard symbol={selected.symbol} market="nse" />

              {/* Ticker Info */}
              <div className="card">
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:12 }}>
                <div>
                  <div style={{ fontSize:18, fontWeight:700, fontFamily:'monospace' }}>{selected.symbol}</div>
                  <div style={{ fontSize:12, color:'var(--text-muted)' }}>{selected.name}</div>
                  {selected.sector && <div style={{ fontSize:11, color:'var(--accent)', marginTop:2 }}>{selected.sector}</div>}
                </div>
                <div style={{ textAlign:'right' }}>
                  <div style={{ fontSize:22, fontWeight:700, color:'var(--accent)', fontFamily:'monospace' }}>{inr(selected.price)}</div>
                  <div style={{ fontSize:13, color:pctColor(selected.change_percent||0), fontFamily:'monospace' }}>
                    {(selected.change_percent||0) >= 0 ? '▲' : '▼'} {Math.abs(selected.change_percent||0).toFixed(2)}%
                  </div>
                </div>
              </div>

              <div style={{ display:'flex', gap:4, marginBottom:10, flexWrap:'wrap' }}>
                {INTERVALS.map(intv => (
                  <button key={intv} className="btn btn-ghost btn-sm mono"
                    style={{ padding:'3px 10px', fontSize:11, background:interval===intv?'var(--accent-light)':undefined, color:interval===intv?'var(--accent)':undefined, borderColor:interval===intv?'var(--accent)':undefined }}
                    onClick={() => changeInterval(intv)}>{intv}</button>
                ))}
              </div>

              <div style={{ position:'relative', minHeight:300 }}>
                {candleLoading && (
                  <div style={{ position:'absolute', inset:0, display:'flex', alignItems:'center', justifyContent:'center', background:'rgba(30,32,32,0.8)', zIndex:2, borderRadius:8 }}>
                    <span style={{ color:'var(--text-muted)', fontSize:13 }}>Loading chart...</span>
                  </div>
                )}
                {scriptLoaded && candles.length > 0 && <CandleChart candles={candles} />}
                {!scriptLoaded && <div style={{ height:300, display:'flex', alignItems:'center', justifyContent:'center', color:'var(--text-muted)' }}>Loading chart library...</div>}
                {scriptLoaded && candles.length === 0 && !candleLoading && (
                  <div style={{ height:300, display:'flex', alignItems:'center', justifyContent:'center', color:'var(--text-muted)', fontSize:13 }}>No candle data available</div>
                )}
              </div>

              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginTop:12 }}>
                {[
                  ['Day High',  inr(selected.high),   'var(--success)'],
                  ['Day Low',   inr(selected.low),    'var(--danger)'],
                  ['Open',      inr(selected.open),   'var(--text-secondary)'],
                  ['Volume',    selected.volume > 0 ? `${(selected.volume/1e5).toFixed(2)}L` : '—', 'var(--info)'],
                ].map(([label, val, color]) => (
                  <div key={label} style={{ background:'var(--bg-card-high)', borderRadius:8, padding:'10px 12px' }}>
                    <div style={{ fontSize:11, color:'var(--text-muted)', marginBottom:2 }}>{label}</div>
                    <div style={{ fontFamily:'monospace', fontWeight:600, color }}>{val}</div>
                  </div>
                ))}
              </div>
            </div>
            </>
          ) : (
            <div className="card" style={{ textAlign:'center', padding:'60px 20px' }}>
              <IndianRupee size={40} style={{ color:'var(--accent)', opacity:0.3, marginBottom:12 }} />
              <p style={{ color:'var(--text-muted)', fontSize:13 }}>Select a stock to view candlestick chart</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}