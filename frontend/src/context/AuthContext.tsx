import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import api from '../lib/api'

interface AuthContextValue {
  isLoggedIn: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(() => !!localStorage.getItem('eg_token'))

  const login = useCallback(async (username: string, password: string) => {
    const { data } = await api.post('/auth/login', { username, password })
    localStorage.setItem('eg_token', data.access_token)
    setIsLoggedIn(true)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('eg_token')
    setIsLoggedIn(false)
  }, [])

  const value = useMemo(() => ({ isLoggedIn, login, logout }), [isLoggedIn, login, logout])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
