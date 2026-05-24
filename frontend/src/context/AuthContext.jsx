import { createContext, useContext, useState, useEffect } from "react"
import { authAPI, userAPI } from "../services/api"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem("token")
    if (token) {
      userAPI.getMe()
        .then(res => setUser(res.data))
        .catch(() => { localStorage.removeItem("token") })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    const res = await authAPI.login({ email, password })
    const { access_token, user: userData } = res.data
    localStorage.setItem("token", access_token)
    if (userData) { setUser(userData); return userData }
    const userRes = await userAPI.getMe()
    setUser(userRes.data)
    return userRes.data
  }

  // Register: create account but DO NOT log them in
  // They must go to login page after registration
  const register = async (data) => {
    const res = await authAPI.register(data)
    // Don't store token or set user — force login flow
    return res.data
  }

  const logout = () => {
    authAPI.logout().catch(() => {})
    localStorage.removeItem("token")
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
