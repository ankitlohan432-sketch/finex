import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import {
  LayoutDashboard, CreditCard, ArrowLeftRight, TrendingUp,
  Brain, ShieldAlert, BarChart3, LineChart, HelpCircle, Bug, X,
  Bitcoin, IndianRupee, Building2
} from 'lucide-react'

const sections = [
  {
    label: 'Platform',
    items: [
      { label: 'Overview', icon: LayoutDashboard, to: '/dashboard' },
      { label: 'My Account', icon: CreditCard, to: '/cards' },
      { label: 'Transactions', icon: ArrowLeftRight, to: '/transactions' },
      { label: 'Market', icon: TrendingUp, to: '/markets' },
    ]
  },
  {
    label: 'Live Markets',
    items: [
      { label: 'Crypto', icon: Bitcoin, to: '/crypto' },
      { label: 'NSE', icon: IndianRupee, to: '/nse' },
      { label: 'BSE', icon: Building2, to: '/bse' },
    ]
  },
  {
    label: 'AI Tools',
    items: [
      { label: 'Loan Advisor', icon: Brain, to: '/loan-advisor' },
      { label: 'Fraud Detection', icon: ShieldAlert, to: '/fraud-detection' },
      { label: 'Risk Analysis', icon: BarChart3, to: '/risk-analysis' },
      { label: 'Investments', icon: LineChart, to: '/portfolio' },
    ]
  },
  {
    label: 'Support',
    items: [
      { label: 'Help Centre', icon: HelpCircle, to: '/help' },
      { label: 'Report Issue', icon: Bug, to: '/report' },
    ]
  },
]

export default function Sidebar({ open, onClose }) {
  return (
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <div className="sidebar-logo" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <img
          src="/finex-logo.png"
          alt="FINEX"
          style={{ height: 36, width: 'auto', objectFit: 'contain' }}
        />
        <button onClick={onClose} style={{ background:'none',border:'none',color:'var(--text-muted)',cursor:'pointer',display:'none' }} className="mobile-close">
          <X size={16} />
        </button>
      </div>
      <nav className="sidebar-nav">
        {sections.map(section => (
          <div key={section.label}>
            <div className="nav-section-label">{section.label}</div>
            {section.items.map(({ label, icon: Icon, to }) => (
              <NavLink key={to+label} to={to} end={to==='/dashboard'} className={({ isActive }) => `nav-item ${isActive?'active':''}`} onClick={onClose}>
                <Icon size={15} />
                <span style={{ flex:1 }}>{label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>
    </aside>
  )
}