import { zodResolver } from '@hookform/resolvers/zod'
import { Inbox, LoaderCircle, Sparkles } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useConfirmarPropuestas, usePlanificarTexto } from '../hooks/useIA'
import { useToast } from '../hooks/useToast'
import { textoIaSchema, type TextoIaValues } from '../schemas/ia.schema'
import type { TareaPropuesta } from '../types/ia'
import { getApiErrorMessage } from '../utils/api-error'
import { formatTaskDate, priorityLabel, priorityStyles } from '../utils/tarea'

type PropuestaPendiente = TareaPropuesta & { id: string }

export function PlannerPage() {
  const planificarMutation = usePlanificarTexto()
  const confirmarMutation = useConfirmarPropuestas()
  const [propuestas, setPropuestas] = useState<PropuestaPendiente[]>([])
  const [seleccionadas, setSeleccionadas] = useState<Set<string>>(new Set())
  const { showToast } = useToast()
  const { register, handleSubmit, formState: { errors } } = useForm<TextoIaValues>({
    resolver: zodResolver(textoIaSchema),
  })

  const generarPropuestas = (values: TextoIaValues) => {
    setPropuestas([])
    setSeleccionadas(new Set())
    confirmarMutation.reset()
    planificarMutation.mutate(values, {
      onSuccess: ({ tareas_propuestas }) => {
        const pendientes = tareas_propuestas.map((propuesta, index) => ({
          ...propuesta,
          id: `${Date.now()}-${index}`,
        }))
        setPropuestas(pendientes)
        setSeleccionadas(new Set(pendientes.map((propuesta) => propuesta.id)))
      },
      onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
    })
  }

  const alternarSeleccion = (id: string) => {
    setSeleccionadas((actuales) => {
      const siguiente = new Set(actuales)
      if (siguiente.has(id)) siguiente.delete(id)
      else siguiente.add(id)
      return siguiente
    })
  }

  const confirmarSeleccionadas = () => {
    const paraConfirmar = propuestas.filter((propuesta) => seleccionadas.has(propuesta.id))
    if (paraConfirmar.length === 0) return

    confirmarMutation.mutate(
      paraConfirmar.map(({ nombre, fecha_sugerida, prioridad_sugerida }) => ({
        nombre,
        fecha_limite: fecha_sugerida,
        prioridad: prioridad_sugerida,
      })),
      {
        onSuccess: ({ tareas_confirmadas }) => {
          const idsConfirmados = new Set(paraConfirmar.map((propuesta) => propuesta.id))
          setPropuestas((actuales) => actuales.filter((propuesta) => !idsConfirmados.has(propuesta.id)))
          setSeleccionadas(new Set())
          planificarMutation.reset()
          showToast(`${tareas_confirmadas.length} tarea${tareas_confirmadas.length === 1 ? '' : 's'} guardada${tareas_confirmadas.length === 1 ? '' : 's'} correctamente.`)
        },
        onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
      },
    )
  }

  const seleccionadasCantidad = propuestas.filter((propuesta) => seleccionadas.has(propuesta.id)).length

  return (
    <main className="p-5 sm:p-8">
      <section className="mx-auto max-w-4xl">
        <header>
          <p className="text-sm font-medium text-cyan-700">Asistencia con IA</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">Planificar con IA</h1>
          <p className="mt-2 max-w-2xl text-slate-600">Describe tus pendientes en lenguaje natural. La IA propondrá tareas para que las revises antes de guardarlas.</p>
        </header>

        <section className="mt-8 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <form onSubmit={handleSubmit(generarPropuestas)} noValidate aria-busy={planificarMutation.isPending}>
            <label htmlFor="texto-planificacion" className="text-sm font-medium text-slate-800">¿Qué necesitas organizar?</label>
            <textarea id="texto-planificacion" rows={5} maxLength={2000} placeholder="El viernes debo preparar la presentación y enviar el informe a Ana." className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100" aria-invalid={Boolean(errors.texto)} aria-describedby={errors.texto ? 'texto-planificacion-error' : undefined} {...register('texto')} />
            {errors.texto && <p id="texto-planificacion-error" className="mt-2 text-sm text-red-700" role="alert">{errors.texto.message}</p>}
            {planificarMutation.isError && <p className="mt-3 text-sm text-red-700" role="alert">{getApiErrorMessage(planificarMutation.error)}</p>}
            <button type="submit" disabled={planificarMutation.isPending || confirmarMutation.isPending} className="mt-4 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">
              {planificarMutation.isPending ? <LoaderCircle className="animate-spin" aria-hidden="true" size={17} /> : <Sparkles aria-hidden="true" size={17} />}
              {planificarMutation.isPending ? 'Generando propuestas…' : 'Generar propuestas'}
            </button>
          </form>
        </section>

        {planificarMutation.isSuccess && propuestas.length === 0 && (
          <section className="mt-6 rounded-xl border border-slate-200 bg-white px-6 py-10 text-center shadow-sm" aria-live="polite">
            <span className="mx-auto flex size-11 items-center justify-center rounded-xl bg-slate-100 text-slate-500"><Inbox aria-hidden="true" size={22} /></span>
            <h2 className="mt-4 font-semibold text-slate-900">No se generaron propuestas</h2>
            <p className="mt-1 text-sm text-slate-600">Prueba describiendo tareas más concretas o indicando fechas y prioridades.</p>
          </section>
        )}

        {propuestas.length > 0 && <section className="mt-6 rounded-xl border border-cyan-200 bg-cyan-50/50 shadow-sm">
          <div className="border-b border-cyan-100 px-5 py-4 sm:px-6"><div className="flex items-center gap-2"><Sparkles className="text-cyan-700" aria-hidden="true" size={19} /><h2 className="font-semibold text-slate-900">Propuestas de IA</h2></div><p className="mt-1 text-sm text-slate-700">Estas propuestas aún no han sido guardadas. Selecciona únicamente las que quieras confirmar.</p></div>
          <div className="divide-y divide-cyan-100">
            {propuestas.map((propuesta) => <label key={propuesta.id} className="flex cursor-pointer gap-3 px-5 py-4 hover:bg-cyan-50 sm:px-6">
              <input type="checkbox" checked={seleccionadas.has(propuesta.id)} onChange={() => alternarSeleccion(propuesta.id)} disabled={confirmarMutation.isPending} className="mt-1 size-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 disabled:cursor-not-allowed" />
              <span className="min-w-0 flex-1"><span className="flex flex-wrap items-center gap-2"><span className="font-medium text-slate-900">{propuesta.nombre}</span><span className={`rounded-full border px-2 py-0.5 text-xs font-medium ${priorityStyles[propuesta.prioridad_sugerida]}`}>{priorityLabel[propuesta.prioridad_sugerida]}</span></span><span className="mt-2 block text-sm text-slate-600">{propuesta.motivo}</span><span className="mt-2 block text-xs text-slate-500">Fecha sugerida: {formatTaskDate(propuesta.fecha_sugerida)}</span></span>
            </label>)}
          </div>
          <div className="flex flex-col gap-3 border-t border-cyan-100 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6"><p className="text-sm text-slate-600">{seleccionadasCantidad} seleccionada{seleccionadasCantidad === 1 ? '' : 's'}</p><div><button type="button" onClick={confirmarSeleccionadas} disabled={seleccionadasCantidad === 0 || confirmarMutation.isPending} className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">{confirmarMutation.isPending && <LoaderCircle className="animate-spin" aria-hidden="true" size={17} />}{confirmarMutation.isPending ? 'Guardando…' : 'Confirmar seleccionadas'}</button>{confirmarMutation.isError && <p className="mt-2 text-sm text-red-700" role="alert">{getApiErrorMessage(confirmarMutation.error)}</p>}</div></div>
        </section>}
      </section>
    </main>
  )
}
