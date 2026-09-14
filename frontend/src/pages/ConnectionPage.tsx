import { useQuery } from '@tanstack/react-query'
import { CircleCheck, LoaderCircle, RefreshCw, Sparkles, TriangleAlert } from 'lucide-react'
import { getApiStatus } from '../api/health.api'
import { getApiErrorMessage } from '../utils/api-error'

export function ConnectionPage() {
  const statusQuery = useQuery({
    queryKey: ['api-status'],
    queryFn: getApiStatus,
  })

  return (
    <main className="min-h-screen bg-slate-50 px-5 py-12 sm:px-8">
      <section className="mx-auto max-w-3xl">
        <div className="mb-10 flex items-center gap-3">
          <span className="flex size-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
            <Sparkles aria-hidden="true" size={20} />
          </span>
          <div>
            <p className="text-sm font-semibold text-slate-900">Gestor de tareas</p>
            <p className="text-sm text-slate-500">Planificación asistida por IA</p>
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm sm:p-8">
          <p className="mb-2 text-sm font-medium text-cyan-700">Configuración inicial</p>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900">Frontend preparado</h1>
          <p className="mt-3 max-w-xl text-slate-600">
            React, Router, TanStack Query y Axios están configurados. Esta consulta valida la conexión real con FastAPI.
          </p>

          <div className="mt-8 rounded-lg border border-slate-200 bg-slate-50 p-4" aria-live="polite">
            {statusQuery.isPending && (
              <div className="flex items-center gap-3 text-slate-600">
                <LoaderCircle className="animate-spin text-indigo-600" aria-hidden="true" size={20} />
                <span>Comprobando conexión con la API…</span>
              </div>
            )}

            {statusQuery.isSuccess && (
              <div className="flex items-start gap-3 text-emerald-700">
                <CircleCheck className="mt-0.5 shrink-0" aria-hidden="true" size={20} />
                <div>
                  <p className="font-medium">Conexión con FastAPI establecida</p>
                  <p className="mt-1 text-sm text-slate-600">{statusQuery.data.mensaje}</p>
                </div>
              </div>
            )}

            {statusQuery.isError && (
              <div className="flex items-start gap-3 text-red-700">
                <TriangleAlert className="mt-0.5 shrink-0" aria-hidden="true" size={20} />
                <div>
                  <p className="font-medium">No fue posible conectar con la API</p>
                  <p className="mt-1 text-sm text-slate-600">{getApiErrorMessage(statusQuery.error)}</p>
                  <button
                    type="button"
                    onClick={() => void statusQuery.refetch()}
                    className="mt-4 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3 py-2 text-sm font-medium text-white hover:bg-indigo-700"
                  >
                    <RefreshCw aria-hidden="true" size={16} />
                    Reintentar
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </main>
  )
}
