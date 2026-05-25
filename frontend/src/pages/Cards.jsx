import { useEffect, useState } from 'react'
import { cardsAPI } from '../services/api'
import { CreditCard, Plus, Trash2 } from 'lucide-react'

function CardVisual({ card }) {
  const colors = {
    VISA: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
    MASTERCARD: 'linear-gradient(135deg, #2d1b69 0%, #11998e 100%)',
    AMEX: 'linear-gradient(135deg, #134e5e 0%, #71b280 100%)',
    DEFAULT: 'linear-gradient(135deg, #0d0d14 0%, #1a1a2e 100%)',
  }
  const bg = colors[card.card_type?.toUpperCase()] || colors.DEFAULT

  return (
    <div style={{
      background: bg,
      border: '1px solid var(--border)',
      borderRadius: 16,
      padding: '24px',
      position: 'relative',
      overflow: 'hidden',
      minHeight: 180,
    }}>
      <div style={{ position: 'absolute', top: -20, right: -20, width: 120, height: 120, borderRadius: '50%', background: 'rgba(255,255,255,0.03)' }} />
      <div style={{ position: 'absolute', bottom: -30, right: 30, width: 160, height: 160, borderRadius: '50%', background: 'rgba(255,255,255,0.02)' }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 40 }}>
        <CreditCard size={28} style={{ color: 'rgba(255,255,255,0.6)' }} />
        <span style={{ fontFamily: 'Syne', fontSize: 14, fontWeight: 700, color: 'rgba(255,255,255,0.8)', letterSpacing: 2 }}>
          {card.card_type?.toUpperCase()}
        </span>
      </div>

      <div style={{ fontFamily: 'DM Mono', fontSize: 18, letterSpacing: 4, color: 'rgba(255,255,255,0.9)', marginBottom: 20 }}>
        •••• •••• •••• {card.last_four}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 2 }}>Card Holder</div>
          <div style={{ fontFamily: 'Syne', fontSize: 13, color: 'rgba(255,255,255,0.8)' }}>{card.card_holder}</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 10, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 2 }}>Expires</div>
          <div style={{ fontFamily: 'DM Mono', fontSize: 13, color: 'rgba(255,255,255,0.8)' }}>
            {String(card.expiry_month).padStart(2, '0')}/{String(card.expiry_year).slice(-2)}
          </div>
        </div>
      </div>

      {card.is_primary && (
        <div style={{ position: 'absolute', top: 12, right: 12 }}>
          <span className="badge badge-success" style={{ fontSize: 10 }}>PRIMARY</span>
        </div>
      )}
    </div>
  )
}

export default function Cards() {
  const [cards, setCards] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ card_number: '', card_holder: '', expiry_month: '', expiry_year: '', card_type: 'VISA', is_primary: false })
  const [msg, setMsg] = useState('')
  const [loading, setLoading] = useState(true)

  const load = () => {
    cardsAPI.getAll()
      .then(r => setCards(r.data || []))
      .catch(() => setCards([]))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleAdd = async (e) => {
    e.preventDefault()
    try {
      await cardsAPI.add({ ...form, expiry_month: Number(form.expiry_month), expiry_year: Number(form.expiry_year) })
      setMsg('Card added!')
      setShowForm(false)
      setForm({ card_number: '', card_holder: '', expiry_month: '', expiry_year: '', card_type: 'VISA', is_primary: false })
      load()
    } catch (e) {
      setMsg(e.response?.data?.detail || 'Failed to add card')
    }
    setTimeout(() => setMsg(''), 3000)
  }

  const handleRemove = async (id) => {
    if (!confirm('Remove this card?')) return
    await cardsAPI.remove(id)
    load()
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value })

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h2 style={{ fontFamily: 'Syne', fontSize: 18, fontWeight: 700 }}>Payment Cards</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 4 }}>{cards.length} card{cards.length !== 1 ? 's' : ''} on file</p>
        </div>
        <button className="btn btn-primary" style={{ width: 'auto' }} onClick={() => setShowForm(!showForm)}>
          <Plus size={14} /> Add Card
        </button>
      </div>

      {msg && <div className={`msg ${msg.includes('added') ? 'msg-success' : 'msg-error'}`}>{msg}</div>}

      {/* Add card form */}
      {showForm && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-header"><span className="card-title">New Card</span></div>
          <form onSubmit={handleAdd}>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Card Number</label>
                <input className="form-input mono" placeholder="1234 5678 9012 3456" maxLength={16} value={form.card_number} onChange={set('card_number')} required />
              </div>
              <div className="form-group">
                <label className="form-label">Card Holder</label>
                <input className="form-input" placeholder="John Doe" value={form.card_holder} onChange={set('card_holder')} required />
              </div>
              <div className="form-group">
                <label className="form-label">Expiry Month</label>
                <input className="form-input mono" placeholder="MM" maxLength={2} value={form.expiry_month} onChange={set('expiry_month')} required />
              </div>
              <div className="form-group">
                <label className="form-label">Expiry Year</label>
                <input className="form-input mono" placeholder="YYYY" maxLength={4} value={form.expiry_year} onChange={set('expiry_year')} required />
              </div>
              <div className="form-group">
                <label className="form-label">Card Type</label>
                <select className="form-input" value={form.card_type} onChange={set('card_type')}>
                  <option>VISA</option>
                  <option>MASTERCARD</option>
                  <option>AMEX</option>
                </select>
              </div>
              <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: 10, paddingTop: 24 }}>
                <input type="checkbox" id="primary" checked={form.is_primary} onChange={set('is_primary')} />
                <label htmlFor="primary" style={{ fontSize: 13, color: 'var(--text-secondary)', cursor: 'pointer' }}>Set as primary</label>
              </div>
            </div>
            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <button type="submit" className="btn btn-primary" style={{ width: 'auto' }}>Add Card</button>
              <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Cards grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: 60 }}><div className="spinner" style={{ margin: 'auto' }} /></div>
      ) : cards.length > 0 ? (
        <div className="grid-3">
          {cards.map(card => (
            <div key={card.id}>
              <CardVisual card={card} />
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 8 }}>
                <button className="btn btn-danger btn-sm" onClick={() => handleRemove(card.id)}>
                  <Trash2 size={12} /> Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text-muted)' }}>
          <CreditCard size={40} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
          <p>No cards added yet</p>
          <button className="btn btn-ghost" style={{ marginTop: 16 }} onClick={() => setShowForm(true)}>
            <Plus size={14} /> Add your first card
          </button>
        </div>
      )}
    </div>
  )
}
