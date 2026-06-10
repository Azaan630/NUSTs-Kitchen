import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react'
import type { User, AccountType } from '@/types'
import { verifyUser } from '@/lib/api'
import toast from 'react-hot-toast'

interface AuthContextType {
  user: User | null
  email: string
  isAuthenticated: boolean
  role: AccountType | null
  login: (email: string) => Promise<User>
  logout: () => void
  isLoading: boolean
  error: string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const savedEmail = localStorage.getItem('auth_email')
    if (savedEmail) {
      setIsLoading(true)
      verifyUser(savedEmail)
        .then((verifiedUser) => {
          setUser(verifiedUser)
          setEmail(savedEmail)
        })
        .catch(() => {
          localStorage.removeItem('auth_email')
        })
        .finally(() => setIsLoading(false))
    }
  }, [])

  const login = useCallback(async (emailInput: string): Promise<User> => {
    setIsLoading(true)
    setError(null)
    try {
      const verifiedUser = await verifyUser(emailInput)
      setUser(verifiedUser)
      setEmail(emailInput)
      localStorage.setItem('auth_email', emailInput)
      return verifiedUser
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed'
      setError(message)
      toast.error(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    setUser(null)
    setEmail('')
    setError(null)
    localStorage.removeItem('auth_email')
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        email,
        isAuthenticated: !!user,
        role: user?.Account_Type ?? null,
        login,
        logout,
        isLoading,
        error,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
