import { zodResolver } from '@hookform/resolvers/zod'
import { CalendarDays, ClipboardList, LoaderCircle, Sparkles } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { usePlanDia } from '../hooks/useIA'
import { useTareas } from '../hooks/useTareas'
import { useToast } from '../hooks/useToast'
import { planDiaSchema, type PlanDiaValues } from '../schemas/ia.schema'
import { getApiErrorMessage } from '../utils/api-error'
import { todayIso } from '../utils/date'
import { formatTaskDate, priorityLabel, priorityStyles } from '../utils/tarea'

export function DayPlanPage() {
  const planMutation = usePlanDia()
  const tareasQuery = useTareas()
  const { showToast } = useToast()
  const { register, handleSubmit, formState: { errors } } = useForm<PlanDiaValues>({
    resolver: zodResolver(planDiaSchema),
    defaultValues: { fecha: todayIso() },
  })
  const tareasPorId = new Map((tareasQuery.data ?? []).map((tarea) => [tarea.id, tarea]))

  const generarPlan = (values: PlanDiaValues) => {
    planMutation.reset()
    planMutation.mutate(
      { fecha: values.fecha },
      { onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error') },
    )
  }

  return (
    <main className="p-5 sm:p-8">
      <section className="mx-auto max-w-4xl">
        <header>
          <p className="text-sm font-medium text-cyan-700">Asistencia con IA</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">Plan del día</h1>
          <p className="mt-2 max-w-2xl text-slate-600">Obtén una propuesta ordenada a partir de tus tareas pendientes. Es una recomendación y no modifica ningún dato.</p>
        </header>

        <section className="mt-8 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <form onSubmit={handleSubmit(generarPlan)} className="flex flex-col gap-4 sm:flex-row sm:items-end" noValidate aria-busy={planMutation.isPending}>
            <div className="flex-1">
              <label htmlFor="fecha-plan" className="text-sm font-medium text-slate-800">Fecha que quieres planificar</label>
              <input id="fecha-plan" type="date" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100" aria-invalid={Boolean(errors.fecha)} aria-describedby={errors.fecha ? 'fecha-plan-error' : undefined} {...register('fecha')} />
              {errors.fecha && <p id="fecha-plan-error" className="mt-2 text-sm text-red-700" role="alert">{errors.fecha.message}</p>}
            </div>
            <button type="submit" disabled={planMutation.isPending || tareasQuery.isPending || tareasQuery.isError} className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">
              {planMutation.isPending ? <LoaderCircle className="animate-spin" aria-hidden="true" size={17} /> : <Sparkles aria-hidden="true" size={17} />}
              {planMutation.isPending ? 'Preparando plan…' : 'Planificar mi día'}
            </button>
          </form>
          {tareasQuery.isPending && <p className="mt-4 flex items-center gap-2 text-sm text-slate-600" role="status"><LoaderCircle className="animate-spin text-indigo-600" aria-hidden="true" size={16} />Cargando tareas disponibles…</p>}
          {tareasQuery.isError && <p className="mt-4 text-sm text-red-700" role="alert">Necesitamos cargar tus tareas para mostrar sus nombres y prioridades. Intenta recargar la página.</p>}
          {planMutation.isError && <p className="mt-4 text-sm text-red-700" role="alert">{getApiErrorMessage(planMutation.error)}</p>}
        </section>

        {planMutation.data && !planMutation.isPending && (
          <section className="mt-6 overflow-hidden rounded-xl border border-cyan-200 bg-white shadow-sm" aria-live="polite">
            <div className="border-b border-cyan-100 bg-cyan-50/60 px-5 py-4 sm:px-6">
              <div className="flex flex-wrap items-center gap-2">
                <CalendarDays className="text-cyan-700" aria-hidden="true" size={19} />
                <h2 className="font-semibold text-slate-900">Plan para {formatTaskDate(planMutation.data.fecha)}</h2>
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-600">{planMutation.data.resumen}</p>
              <p className="mt-1 text-xs font-medium text-cyan-800">Mostrado en el orden enviado por el backend.</p>
            </div>

            {planMutation.data.plan.length === 0 ? (
              <div className="px-6 py-12 text-center">
                <span className="mx-auto flex size-11 items-center justify-center rounded-xl bg-slate-100 text-slate-500"><ClipboardList aria-hidden="true" size={22} /></span>
                <h3 className="mt-4 font-semibold text-slate-900">No hay tareas para este plan</h3>
                <p className="mt-1 text-sm text-slate-600">Cuando tengas pendientes relevantes, aparecerán aquí ordenados.</p>
              </div>
            ) : (
              <ol className="divide-y divide-slate-100">
                {planMutation.data.plan.map((recomendacion) => {
                  const tarea = tareasPorId.get(recomendacion.tarea_id)
                  return (
                    <li key={recomendacion.tarea_id} className="flex gap-4 px-5 py-5 sm:px-6">
                      <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-sm font-semibold text-white" aria-label={`Orden ${recomendacion.orden}`}>{recomendacion.orden}</span>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <h3 className="font-semibold text-slate-900">{tarea?.nombre ?? `Tarea #${recomendacion.tarea_id}`}</h3>
                          {tarea ? <span className={`rounded-full border px-2.5 py-1 text-xs font-medium ${priorityStyles[tarea.prioridad]}`}>Prioridad {priorityLabel[tarea.prioridad].toLowerCase()}</span> : <span className="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600">Prioridad no disponible</span>}
                        </div>
                        <p className="mt-2 text-sm leading-6 text-slate-600">{recomendacion.motivo}</p>
                      </div>
                    </li>
                  )
                })}
              </ol>
            )}
          </section>
        )}
      </section>
    </main>
  )
}
