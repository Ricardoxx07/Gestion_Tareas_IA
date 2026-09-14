import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { LoaderCircle, RefreshCw } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

export function ProtectedRoute() {
  const location = useLocation()
  const { hasSession, hasSessionError, isAuthenticated, isLoading, retrySession } = useAuth()

  if (!hasSession) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  if (isLoading) {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-50 px-5" aria-live="polite">
        <div className="flex items-center gap-3 text-slate-600">
          <LoaderCircle className="animate-spin text-indigo-600" aria-hidden="true" size={20} />
          <span>Restaurando tu sesión…</span>
        </div>
      </main>
    )
  }

  if (hasSessionError) {
    return (
      <main className="grid min-h-screen place-items-center bg-slate-50 px-5">
        <section className="max-w-md rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm">
          <h1 className="text-lg font-semibold text-slate-900">No pudimos restaurar tu sesión</h1>
          <p className="mt-2 text-sm text-slate-600">Comprueba la conexión con la API e inténtalo de nuevo.</p>
          <button type="button" onClick={retrySession} className="mt-5 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
            <RefreshCw aria-hidden="true" size={16} />
            Reintentar
          </button>
        </section>
      </main>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
