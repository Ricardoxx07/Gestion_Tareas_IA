import { createContext } from 'react'
import type { Credenciales, Usuario } from '../types/auth'

export interface AuthContextValue {
  user: Usuario | undefined
  hasSession: boolean
  isAuthenticated: boolean
  isLoading: boolean
  hasSessionError: boolean
  login: (credentials: Credenciales) => Promise<Usuario>
  logout: () => void
  retrySession: () => void
}

export const AuthContext = createContext<AuthContextValue | null>(null)
