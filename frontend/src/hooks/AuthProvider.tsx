import { useCallback, useEffect, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { iniciarSesion, obtenerMiUsuario } from '../api/auth.api'
import {
  clearSessionToken,
  getSessionToken,
  registerUnauthorizedHandler,
  saveSessionToken,
} from '../api/client'
import type { Credenciales, Usuario } from '../types/auth'
import { AuthContext } from './auth-context'

const AUTH_QUERY_KEY = ['auth', 'me'] as const

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [hasSession, setHasSession] = useState(() => Boolean(getSessionToken()))
  const userQuery = useQuery({
    queryKey: AUTH_QUERY_KEY,
    queryFn: obtenerMiUsuario,
    enabled: hasSession,
  })
  const { data: user, isError, isPending, refetch } = userQuery

  useEffect(() => {
    return registerUnauthorizedHandler(() => {
      setHasSession(false)
      queryClient.removeQueries({ queryKey: AUTH_QUERY_KEY })
      navigate('/login', { replace: true, state: { sessionExpired: true } })
    })
  }, [navigate, queryClient])

  const logout = useCallback(() => {
    clearSessionToken()
    setHasSession(false)
    queryClient.removeQueries({ queryKey: AUTH_QUERY_KEY })
    navigate('/login', { replace: true })
  }, [navigate, queryClient])

  const login = useCallback(async (credentials: Credenciales): Promise<Usuario> => {
    const { access_token: accessToken } = await iniciarSesion(credentials)
    saveSessionToken(accessToken)
    setHasSession(true)

    return queryClient.fetchQuery({
      queryKey: AUTH_QUERY_KEY,
      queryFn: obtenerMiUsuario,
    })
  }, [queryClient])

  const retrySession = useCallback(() => {
    void refetch()
  }, [refetch])

  const value = useMemo(
    () => ({
      user,
      hasSession,
      isAuthenticated: Boolean(user),
      isLoading: hasSession && isPending,
      hasSessionError: hasSession && isError,
      login,
      logout,
      retrySession,
    }),
    [hasSession, isError, isPending, login, logout, retrySession, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
