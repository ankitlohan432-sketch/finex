import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider, useAuth } from "./context/AuthContext"
import AppLayout from "./components/layout/AppLayout"
import Landing from "./pages/Landing"
import ForgotPassword from './pages/ForgotPassword'
import Login from "./pages/Login"
import Register from "./pages/Register"
import Dashboard from "./pages/Dashboard"
import Markets from "./pages/Markets"
import Transactions from "./pages/Transactions"
import Portfolio from "./pages/Portfolio"
import Cards from "./pages/Cards"
import Analytics from "./pages/Analytics"
import Chat from "./pages/Chat"
import Admin from "./pages/Admin"
import Profile from "./pages/Profile"
import Settings from "./pages/Settings"
import AddFunds from "./pages/AddFunds"
import LoanAdvisor from "./pages/LoanAdvisor"
import FraudDetection from "./pages/FraudDetection"
import RiskAnalysis from "./pages/RiskAnalysis"
import Help from "./pages/Help"
import Report from "./pages/Report"
import CryptoMarket from "./pages/CryptoMarket"
import NSEMarket from "./pages/NSEMarket"
import BSEMarket from "./pages/BSEMarket"

const LoadingScreen = () => (
  <div className="loading-screen">
    <div className="loading-screen-logo">Fin<span>ex</span></div>
    <div className="loading-screen-bar"><div className="loading-screen-bar-fill" /></div>
  </div>
)

function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <LoadingScreen />
  if (!user && !localStorage.getItem("token")) return <Navigate to="/login" replace />
  if (!user && localStorage.getItem("token")) return <LoadingScreen />
  return children
}

function AdminRoute({ children }) {
  const { user } = useAuth()
  return user?.is_admin ? children : <Navigate to="/dashboard" replace />
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <LoadingScreen />
  return user ? <Navigate to="/dashboard" replace /> : children
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<PublicRoute><Landing /></PublicRoute>} />
          <Route path="/forgot-password" element={<ForgotPassword />} />`n        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
          <Route element={<PrivateRoute><AppLayout /></PrivateRoute>}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/markets" element={<Markets />} />
            <Route path="/crypto" element={<CryptoMarket />} />
            <Route path="/nse" element={<NSEMarket />} />
            <Route path="/bse" element={<BSEMarket />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/cards" element={<Cards />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/add-funds" element={<AddFunds />} />
            <Route path="/loan-advisor" element={<LoanAdvisor />} />
            <Route path="/fraud-detection" element={<FraudDetection />} />
            <Route path="/risk-analysis" element={<RiskAnalysis />} />
            <Route path="/help" element={<Help />} />
            <Route path="/report" element={<Report />} />
            <Route path="/admin" element={<AdminRoute><Admin /></AdminRoute>} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

