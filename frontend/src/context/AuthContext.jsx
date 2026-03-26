import { createContext, useContext, useState } from 'react'
import { login as apiLogin, register as apiRegister } from '../api/auth'

const AuthContext = createContext(null)

function parseUser(raw) {
  try { return typeof raw === 'string' ? JSON.parse(raw) : raw } catch { return null }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [user, setUser]   = useState(() => parseUser(localStorage.getItem('user')))
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState(null)

  /** Persist user + token to localStorage and state */
  const persist = (tokenStr, userObj) => {
    localStorage.setItem('token', tokenStr)
    localStorage.setItem('user', JSON.stringify(userObj))
    setToken(tokenStr)
    setUser(userObj)
  }

  const login = async (email, password) => {
    setLoading(true); setError(null)
    try {
      const data = await apiLogin(email, password)
      // data.user comes from the Token schema: {id, email, full_name, role, username, ...}
      const userObj = {
        id:        data.user?.id,
        email:     data.user?.email ?? email,
        full_name: data.user?.full_name,
        username:  data.user?.username,
        role:      data.user?.role ?? data.role ?? 'student',
      }
      persist(data.access_token, userObj)
      return true
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Login failed')
      return false
    } finally {
      setLoading(false)
    }
  }

  const register = async ({ fullName, email, password }) => {
    setLoading(true); setError(null)
    try {
      await apiRegister({ fullName, email, password })
      // auto-login after successful registration
      return await login(email, password)
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(Array.isArray(detail) ? detail[0]?.msg : (detail ?? 'Registration failed'))
      return false
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{
      token, user, loading, error,
      login, register, logout,
      isAuthenticated: !!token,
      isAdmin:   user?.role === 'admin',
      isStudent: user?.role === 'student',
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
