import { Navigate, Outlet } from 'react-router-dom'
import { LoaderCircle } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

export function PublicRoute() {
  const { hasSession, isAuthenticated, isLoading } = useAuth()

  if (hasSession && isLoading) {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-50 px-5" aria-live="polite">
        <div className="flex items-center gap-3 text-slate-600">
          <LoaderCircle className="animate-spin text-indigo-600" aria-hidden="true" size={20} />
          <span>Restaurando tu sesión…</span>
        </div>
      </main>
    )
  }

  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <Outlet />
}
