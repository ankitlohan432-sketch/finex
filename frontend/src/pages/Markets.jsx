import { useEffect, useState } from 'react'
import { stockAPI, transactionAPI } from '../services/api'
import { Search, TrendingUp, TrendingDown, RefreshCw, Star } from 'lucide-react'
import { LineChart, Line, ResponsiveContainer, Tooltip, XAxis } from 'recharts'

const SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']

export default function Markets() {
  const [indices, setIndices] = useState([])
  const [movers, setMovers] = useState([])
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState(null)
  const [history, setHistory] = useState([])
  const [tradeForm, setTradeForm] = useState({ type: 'BUY', quantity: 1 })
  const [tradeMsg, setTradeMsg] = useState({ text: '', type: '' })
  const [loading, setLoading] = useState(true)
  const [tradeLoading, setTradeLoading] = useState(false)
  const [loadingSymbol, setLoadingSymbol] = useState('')

  const load = async () => {
    setLoading(true)
    try {
      const [idx, mv] = await Promise.allSettled([stockAPI.getIndices(), stockAPI.getTopMovers()])
      if (idx.status === 'fulfilled') setIndices(Array.isArray(idx.value.data) ? idx.value.data : [])
      if (mv.status === 'fulfilled') setMovers(Array.isArray(mv.value.data) ? mv.value.data : [])
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  const loadStock = async (symbol) => {
    setLoadingSymbol(symbol)
    try {
      const [p, h] = await Promise.allSettled([stockAPI.getPrice(symbol), stockAPI.getHistory(symbol)])
      if (p.status === 'fulfilled') setSelected(p.value.data)
      if (h.status === 'fulfilled') {
        const data = Array.isArray(h.value.data) ? h.value.data : []
        setHistory(data.reverse().map(d => ({ date: d.date?.slice(0, 10), close: d.close })))
      }
    } finally { setLoadingSymbol('') }
  }

  const handleTrade = async () => {
    if (!selected || selected.price <= 0) return
    setTradeLoading(true)
    setTradeMsg({ text: '', type: '' })
    try {
      await transactionAPI.create({
        type: tradeForm.type,
        symbol: selected.symbol,
        quantity: Number(tradeForm.quantity),
        price_per_unit: selected.price,
        total_amount: tradeForm.quantity * selected.price,
        description: `${tradeForm.type} ${tradeForm.quantity} ${selected.symbol} @ $${selected.price.toFixed(2)}`
      })
      setTradeMsg({ text: `${tradeForm.type} order placed for ${tradeForm.quantity} ${selected.symbol}!`, type: 'success' })
    } catch (e) {
      setTradeMsg({ text: e.response?.data?.detail || 'Order failed. Please try again.', type: 'error' })
    } finally { setTradeLoading(false) }
  }

  const fmt = (n) => n != null && n > 0 ? `$${Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '—'
  const filtered = SYMBOLS.filter(s => s.includes(search.toUpperCase()))

  return (
    <div>
      {/* Indices */}
      <div className="grid-4" style={{ marginBottom: 20 }}>
        {indices.length > 0 ? indices.slice(0, 4).map((idx, i) => (
          <div className="stat-card" key={i}>
            <div className="stat-label">{idx.name}</div>
            <div className="stat-value mono">{idx.value?.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
            <div className={`stat-change ${(idx.change_percent ?? idx.change ?? 0) >= 0 ? '' : 'down'}`}>
              {(idx.change_percent ?? 0) >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
              {(idx.change_percent ?? idx.change ?? 0) >= 0 ? '+' : ''}{(idx.change_percent ?? idx.change ?? 0).toFixed(2)}%
            </div>
          </div>
        )) : ['NIFTY 50', 'SENSEX', 'BANK NIFTY', 'NASDAQ'].map(name => (
          <div className="stat-card" key={name}>
            <div className="stat-label">{name}</div>
            <div className="stat-value" style={{ color: 'var(--text-muted)' }}>{loading ? '...' : '—'}</div>
          </div>
        ))}
      </div>

      <div className="grid-2-1">
        {/* Stock list */}
        <div className="card">
          <div className="card-header">
            <span className="card-title">Live Stocks</span>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <div style={{ position: 'relative' }}>
                <Search size={13} style={{ position: 'absolute', left: 9, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input className="form-input" placeholder="Search..." value={search}
                  onChange={e => setSearch(e.target.value.toUpperCase())}
                  style={{ paddingLeft: 28, width: 120, padding: '6px 10px 6px 26px', fontSize: 12 }} />
              </div>
              <button className="btn btn-ghost btn-sm" onClick={load}><RefreshCw size={12} /></button>
            </div>
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 16 }}>
            {filtered.map(sym => (
              <button key={sym} onClick={() => loadStock(sym)}
                className="btn btn-ghost btn-sm mono"
                style={{
                  borderColor: selected?.symbol === sym ? 'var(--accent)' : undefined,
                  color: selected?.symbol === sym ? 'var(--accent)' : undefined,
                  opacity: loadingSymbol === sym ? 0.5 : 1
                }}>
                {sym}
              </button>
            ))}
          </div>

          <div className="table-container">
            <table>
              <thead><tr><th>Symbol</th><th>Price</th><th>Change</th><th>52W High</th><th>52W Low</th><th>Volume</th></tr></thead>
              <tbody>
                {movers.length > 0 ? movers.map((m, i) => (
                  <tr key={i} style={{ cursor: 'pointer' }} onClick={() => loadStock(m.symbol)}>
                    <td>
                      <div className="mono" style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{m.symbol}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{m.name}</div>
                    </td>
                    <td className="mono">{fmt(m.price)}</td>
                    <td>
                      <span style={{ color: (m.change_percent ?? m.change ?? 0) >= 0 ? 'var(--success)' : 'var(--danger)', fontFamily: 'monospace', fontSize: 12 }}>
                        {(m.change_percent ?? 0) >= 0 ? '+' : ''}{(m.change_percent ?? 0).toFixed(2)}%
                      </span>
                    </td>
                    <td className="mono" style={{ color: 'var(--success)', fontSize: 12 }}>{m.fifty_two_week_high > 0 ? fmt(m.fifty_two_week_high) : '—'}</td>
                    <td className="mono" style={{ color: 'var(--danger)', fontSize: 12 }}>{m.fifty_two_week_low > 0 ? fmt(m.fifty_two_week_low) : '—'}</td>
                    <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{m.volume > 0 ? `${(m.volume / 1e6).toFixed(1)}M` : '—'}</td>
                  </tr>
                )) : (
                  <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: 24 }}>
                    {loading ? 'Loading market data...' : 'Click a symbol above to load stock data'}
                  </td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Trade panel */}
        <div>
          {selected && selected.price > 0 ? (
            <div className="card">
              <div style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--text-primary)' }}>{selected.symbol}</div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{selected.name}</div>
                  </div>
                  <Star size={16} style={{ color: 'var(--text-muted)', cursor: 'pointer' }} />
                </div>
                <div style={{ fontFamily: 'monospace', fontSize: 28, fontWeight: 700, color: 'var(--accent)', marginTop: 8 }}>
                  {fmt(selected.price)}
                </div>
                <div style={{ display: 'flex', gap: 16, marginTop: 4, fontSize: 12 }}>
                  <span style={{ color: (selected.change_percent ?? 0) >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                    {(selected.change_percent ?? 0) >= 0 ? '▲' : '▼'} {Math.abs(selected.change_percent ?? 0).toFixed(2)}%
                  </span>
                  {selected.high > 0 && <span style={{ color: 'var(--text-muted)' }}>H: {fmt(selected.high)}</span>}
                  {selected.low > 0 && <span style={{ color: 'var(--text-muted)' }}>L: {fmt(selected.low)}</span>}
                </div>
              </div>

              {history.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <ResponsiveContainer width="100%" height={80}>
                    <LineChart data={history}>
                      <XAxis dataKey="date" hide />
                      <Tooltip contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 6, fontSize: 11 }}
                        formatter={(v) => [`$${v?.toFixed(2)}`, 'Price']} labelFormatter={(l) => l} />
                      <Line type="monotone" dataKey="close" stroke="var(--accent)" strokeWidth={1.5} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              <div style={{ height: 1, background: 'var(--border-light)', margin: '12px 0' }} />

              <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                {['BUY', 'SELL'].map(t => (
                  <button key={t} onClick={() => setTradeForm({ ...tradeForm, type: t })}
                    className={`btn ${tradeForm.type === t ? (t === 'BUY' ? 'btn-success' : 'btn-danger') : 'btn-ghost'}`}
                    style={{ flex: 1 }}>{t}</button>
                ))}
              </div>

              <div className="form-group">
                <label className="form-label">Quantity</label>
                <input className="form-input" type="number" min="1" value={tradeForm.quantity}
                  onChange={e => setTradeForm({ ...tradeForm, quantity: Math.max(1, Number(e.target.value)) })} />
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderTop: '1px solid var(--border-light)', marginBottom: 12, fontSize: 13 }}>
                <span style={{ color: 'var(--text-muted)' }}>Estimated Total</span>
                <span className="mono" style={{ fontWeight: 600 }}>{fmt((tradeForm.quantity || 0) * (selected.price || 0))}</span>
              </div>

              {tradeMsg.text && (
                <div className={`msg ${tradeMsg.type === 'success' ? 'msg-success' : 'msg-error'}`} style={{ marginBottom: 12 }}>
                  {tradeMsg.text}
                </div>
              )}

              <button className={`btn ${tradeForm.type === 'BUY' ? 'btn-success' : 'btn-danger'}`}
                style={{ width: '100%' }} onClick={handleTrade} disabled={tradeLoading}>
                {tradeLoading ? 'Processing...' : `Place ${tradeForm.type} Order`}
              </button>
            </div>
          ) : (
            <div className="card" style={{ textAlign: 'center', padding: '40px 20px' }}>
              <TrendingUp size={40} style={{ color: 'var(--accent)', opacity: 0.4, marginBottom: 12 }} />
              <p style={{ color: 'var(--text-muted)', fontSize: 13 }}>Select a stock above to view details and trade</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
