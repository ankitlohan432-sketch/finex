import { useState, useRef, useEffect } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import Sidebar from './Sidebar'
import { Menu, Bell, User, Settings, PlusCircle, LogOut, ChevronDown } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

const pageTitles = {
  '/dashboard':'Dashboard','/markets':'Markets','/transactions':'Transactions',
  '/portfolio':'Portfolio','/cards':'My Account','/analytics':'Analytics',
  '/chat':'AI Assistant','/admin':'Admin Panel','/profile':'Profile',
  '/settings':'Settings','/add-funds':'Add Funds','/loan-advisor':'Loan Advisor',
  '/fraud-detection':'Fraud Detection','/risk-analysis':'Risk Analysis',
  '/help':'Help Centre','/report':'Report Issue',
}

function ProfileDropdown() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const ref = useRef(null)

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const initials = user?.full_name?.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2) || 'FX'

  const items = [
    { icon: User, label: 'Profile', to: '/profile' },
    { icon: Settings, label: 'Settings', to: '/settings' },
    { icon: PlusCircle, label: 'Add Funds', to: '/add-funds' },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
    setOpen(false)
  }

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <div onClick={() => setOpen(!open)} style={{ display:'flex',alignItems:'center',gap:8,cursor:'pointer',padding:'6px 10px',borderRadius:10,background:open?'var(--bg-card)':'transparent',border:'1px solid',borderColor:open?'var(--border)':'transparent',transition:'all 0.15s' }}>
        <div style={{ width:30,height:30,borderRadius:'50%',background:'var(--accent)',color:'#001f24',display:'flex',alignItems:'center',justifyContent:'center',fontSize:12,fontWeight:700,flexShrink:0 }}>
          {initials}
        </div>
        <div style={{ display:'flex',flexDirection:'column',minWidth:0 }}>
          <span style={{ fontSize:12,fontWeight:600,color:'var(--text-primary)',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis',maxWidth:80 }}>
            {user?.full_name?.split(' ')[0] || 'User'}
          </span>
          <span style={{ fontSize:10,color:'var(--text-muted)' }}>{user?.is_admin ? 'Admin' : 'Investor'}</span>
        </div>
        <ChevronDown size={12} style={{ color:'var(--text-muted)',transform:open?'rotate(180deg)':'rotate(0)',transition:'transform 0.2s',flexShrink:0 }} />
      </div>

      {open && (
        <div style={{ position:'absolute',top:'calc(100% + 8px)',right:0,width:220,background:'var(--bg-card)',border:'1px solid var(--border)',borderRadius:12,boxShadow:'0 16px 48px rgba(0,0,0,0.5)',zIndex:200,overflow:'hidden' }}>
          {/* User info header */}
          <div style={{ padding:'14px 16px',borderBottom:'1px solid var(--border-light)',background:'var(--bg-secondary)' }}>
            <div style={{ fontSize:13,fontWeight:600,color:'var(--text-primary)',marginBottom:2 }}>{user?.full_name}</div>
            <div style={{ fontSize:11,color:'var(--text-muted)',overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap' }}>{user?.email}</div>
          </div>
          {/* Menu items */}
          <div style={{ padding:'6px 0' }}>
            {items.map(({ icon: Icon, label, to }) => (
              <div key={to} onClick={() => { navigate(to); setOpen(false) }} style={{ display:'flex',alignItems:'center',gap:10,padding:'10px 16px',cursor:'pointer',transition:'background 0.15s',color:'var(--text-secondary)',fontSize:13 }}
                onMouseEnter={e => e.currentTarget.style.background='var(--bg-secondary)'}
                onMouseLeave={e => e.currentTarget.style.background='transparent'}>
                <Icon size={14} style={{ color:'var(--text-muted)' }} />
                {label}
              </div>
            ))}
          </div>
          {/* Logout */}
          <div style={{ borderTop:'1px solid var(--border-light)',padding:'6px 0' }}>
            <div onClick={handleLogout} style={{ display:'flex',alignItems:'center',gap:10,padding:'10px 16px',cursor:'pointer',color:'var(--danger)',fontSize:13,transition:'background 0.15s' }}
              onMouseEnter={e => e.currentTarget.style.background='var(--danger-bg)'}
              onMouseLeave={e => e.currentTarget.style.background='transparent'}>
              <LogOut size={14} />
              Sign Out
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()
  const title = pageTitles[location.pathname] || 'Finex'

  return (
    <div className="app-layout">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      {sidebarOpen && (
        <div onClick={() => setSidebarOpen(false)} style={{ position:'fixed',inset:0,background:'rgba(0,0,0,0.5)',zIndex:99 }} />
      )}
      <div className="main-content">
        <header className="topbar">
          <div style={{ display:'flex',alignItems:'center',gap:12 }}>
            <button onClick={() => setSidebarOpen(true)} className="mobile-menu-btn" style={{ background:'none',border:'none',color:'var(--text-muted)',cursor:'pointer',display:'none' }}>
              <Menu size={18} />
            </button>
            <h1 className="topbar-title">{title}</h1>
          </div>
          <div style={{ display:'flex',alignItems:'center',gap:10 }}>
            <div style={{ fontSize:11,color:'var(--text-muted)',fontFamily:'monospace' }}>
              {new Date().toLocaleDateString('en-US',{weekday:'short',month:'short',day:'numeric'})}
            </div>
            <div style={{ position:'relative',width:32,height:32,borderRadius:8,background:'var(--bg-card)',border:'1px solid var(--border-light)',display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer' }}>
              <Bell size={15} style={{ color:'var(--text-muted)' }} />
              <div style={{ width:6,height:6,borderRadius:'50%',background:'var(--danger)',position:'absolute',top:6,right:6 }} />
            </div>
            <ProfileDropdown />
          </div>
        </header>
        <div className="page-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
