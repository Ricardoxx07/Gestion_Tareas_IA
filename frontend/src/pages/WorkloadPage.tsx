import { zodResolver } from '@hookform/resolvers/zod'
import { AlertTriangle, ArrowRight, CheckCircle2, Gauge, LoaderCircle, RefreshCw, Sparkles } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import {
  useConfirmarReprogramaciones,
  useDetectarSobrecarga,
  useProponerReprogramacion,
} from '../hooks/useIA'
import { useTareas } from '../hooks/useTareas'
import { useToast } from '../hooks/useToast'
import { analisisCargaSchema, type AnalisisCargaValues } from '../schemas/ia.schema'
import type {
  AnalisisCargaRequest,
  AnalisisSobrecargaResponse,
  PropuestaReprogramacion,
} from '../types/ia'
import type { Tarea } from '../types/tarea'
import { getApiErrorMessage } from '../utils/api-error'
import { eachIsoDate, formatDayDate, todayIso } from '../utils/date'
import { formatTaskDate } from '../utils/tarea'

interface CambioConfirmado {
  tarea: Tarea
  fechaAnterior: string
}

function obtenerCargaPorFecha(tareas: Tarea[], fechaInicio: string, fechaFin: string): Record<string, number> {
  return tareas.reduce<Record<string, number>>((carga, tarea) => {
    if (tarea.completada || !tarea.fecha_limite || tarea.fecha_limite > fechaFin) return carga
    const fechaCarga = tarea.fecha_limite < fechaInicio ? fechaInicio : tarea.fecha_limite
    carga[fechaCarga] = (carga[fechaCarga] ?? 0) + 1
    return carga
  }, {})
}

export function WorkloadPage() {
  const tareasQuery = useTareas()
  const detectarMutation = useDetectarSobrecarga()
  const proponerMutation = useProponerReprogramacion()
  const confirmarMutation = useConfirmarReprogramaciones()
  const [analisis, setAnalisis] = useState<AnalisisSobrecargaResponse | null>(null)
  const [propuestas, setPropuestas] = useState<PropuestaReprogramacion[]>([])
  const [seleccionadas, setSeleccionadas] = useState<Set<number>>(new Set())
  const [cambiosConfirmados, setCambiosConfirmados] = useState<CambioConfirmado[]>([])
  const { showToast } = useToast()
  const { register, handleSubmit, formState: { errors } } = useForm<AnalisisCargaValues>({
    resolver: zodResolver(analisisCargaSchema),
    defaultValues: { fecha_inicio: todayIso(), dias: 7, max_tareas_por_dia: 3 },
  })
  const tareas = tareasQuery.data ?? []
  const tareasPorId = new Map(tareas.map((tarea) => [tarea.id, tarea]))

  const limpiarFlujoPosterior = () => {
    proponerMutation.reset()
    confirmarMutation.reset()
    setPropuestas([])
    setSeleccionadas(new Set())
    setCambiosConfirmados([])
  }

  const detectar = (values: AnalisisCargaValues) => {
    limpiarFlujoPosterior()
    setAnalisis(null)
    detectarMutation.reset()
    detectarMutation.mutate(values, {
      onSuccess: setAnalisis,
      onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
    })
  }

  const parametrosAnalisis = (): AnalisisCargaRequest | null => analisis ? {
    fecha_inicio: analisis.fecha_inicio,
    dias: eachIsoDate(analisis.fecha_inicio, analisis.fecha_fin).length,
    max_tareas_por_dia: analisis.max_tareas_por_dia,
  } : null

  const solicitarPropuestas = () => {
    const parametros = parametrosAnalisis()
    if (!parametros) return
    setCambiosConfirmados([])
    setPropuestas([])
    setSeleccionadas(new Set())
    confirmarMutation.reset()
    proponerMutation.reset()
    proponerMutation.mutate(parametros, {
      onSuccess: (respuesta) => {
        setPropuestas(respuesta.propuestas)
        setSeleccionadas(new Set(respuesta.propuestas.map((propuesta) => propuesta.tarea_id)))
      },
      onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
    })
  }

  const alternarSeleccion = (tareaId: number) => {
    setSeleccionadas((actuales) => {
      const siguientes = new Set(actuales)
      if (siguientes.has(tareaId)) siguientes.delete(tareaId)
      else siguientes.add(tareaId)
      return siguientes
    })
  }

  const confirmarSeleccionadas = () => {
    const elegidas = propuestas.filter((propuesta) => seleccionadas.has(propuesta.tarea_id))
    if (elegidas.length === 0) return

    confirmarMutation.mutate(
      elegidas.map(({ tarea_id, fecha_actual, fecha_sugerida }) => ({ tarea_id, fecha_actual, fecha_sugerida })),
      {
        onSuccess: ({ tareas_actualizadas }) => {
          const fechaAnteriorPorId = new Map(elegidas.map((propuesta) => [propuesta.tarea_id, propuesta.fecha_actual]))
          setCambiosConfirmados(tareas_actualizadas.map((tarea) => ({
            tarea,
            fechaAnterior: fechaAnteriorPorId.get(tarea.id) ?? '',
          })))
          setPropuestas([])
          setSeleccionadas(new Set())
          showToast(`${tareas_actualizadas.length} cambio${tareas_actualizadas.length === 1 ? '' : 's'} guardado${tareas_actualizadas.length === 1 ? '' : 's'} correctamente.`)

          const parametros = parametrosAnalisis()
          if (parametros) {
            setAnalisis(null)
            detectarMutation.mutate(parametros, {
              onSuccess: setAnalisis,
              onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
            })
          }
        },
        onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
      },
    )
  }

  const fechas = analisis ? eachIsoDate(analisis.fecha_inicio, analisis.fecha_fin) : []
  const cargaPorFecha = analisis ? obtenerCargaPorFecha(tareas, analisis.fecha_inicio, analisis.fecha_fin) : {}
  const alertasPorFecha = new Map((analisis?.alertas ?? []).map((alerta) => [alerta.fecha, alerta]))
  const mayorCarga = Math.max(analisis?.max_tareas_por_dia ?? 1, ...Object.values(cargaPorFecha), 1)
  const cantidadSeleccionada = propuestas.filter((propuesta) => seleccionadas.has(propuesta.tarea_id)).length

  return (
    <main className="p-5 sm:p-8">
      <section className="mx-auto max-w-5xl">
        <header>
          <p className="text-sm font-medium text-cyan-700">Análisis y decisiones</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">Carga de trabajo</h1>
          <p className="mt-2 max-w-3xl text-slate-600">Detecta días con demasiadas tareas y, solo si lo decides, confirma propuestas para distribuirlas mejor.</p>
        </header>

        <section className="mt-8 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <form onSubmit={handleSubmit(detectar)} className="grid gap-4 sm:grid-cols-3 sm:items-end" noValidate aria-busy={detectarMutation.isPending}>
            <div>
              <label htmlFor="fecha-inicio" className="text-sm font-medium text-slate-800">Inicio del período</label>
              <input id="fecha-inicio" type="date" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100" aria-invalid={Boolean(errors.fecha_inicio)} aria-describedby={errors.fecha_inicio ? 'fecha-inicio-error' : undefined} {...register('fecha_inicio')} />
              {errors.fecha_inicio && <p id="fecha-inicio-error" className="mt-2 text-sm text-red-700" role="alert">{errors.fecha_inicio.message}</p>}
            </div>
            <div>
              <label htmlFor="dias-analisis" className="text-sm font-medium text-slate-800">Días a analizar</label>
              <input id="dias-analisis" type="number" min="1" max="31" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100" aria-invalid={Boolean(errors.dias)} aria-describedby={errors.dias ? 'dias-analisis-error' : undefined} {...register('dias', { valueAsNumber: true })} />
              {errors.dias && <p id="dias-analisis-error" className="mt-2 text-sm text-red-700" role="alert">{errors.dias.message}</p>}
            </div>
            <div>
              <label htmlFor="umbral-carga" className="text-sm font-medium text-slate-800">Máximo normal por día</label>
              <input id="umbral-carga" type="number" min="1" max="20" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm text-slate-900 shadow-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100" aria-invalid={Boolean(errors.max_tareas_por_dia)} aria-describedby={errors.max_tareas_por_dia ? 'umbral-carga-error' : undefined} {...register('max_tareas_por_dia', { valueAsNumber: true })} />
              {errors.max_tareas_por_dia && <p id="umbral-carga-error" className="mt-2 text-sm text-red-700" role="alert">{errors.max_tareas_por_dia.message}</p>}
            </div>
            <button type="submit" disabled={detectarMutation.isPending || tareasQuery.isPending || tareasQuery.isError} className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60 sm:col-span-3 sm:justify-self-start">
              {detectarMutation.isPending ? <LoaderCircle className="animate-spin" aria-hidden="true" size={17} /> : <Gauge aria-hidden="true" size={17} />}
              {detectarMutation.isPending ? 'Analizando carga…' : 'Analizar carga'}
            </button>
          </form>
          {tareasQuery.isPending && <p className="mt-4 flex items-center gap-2 text-sm text-slate-600" role="status"><LoaderCircle className="animate-spin text-indigo-600" aria-hidden="true" size={16} />Cargando tareas para el análisis…</p>}
          {tareasQuery.isError && <p className="mt-4 text-sm text-red-700" role="alert">No pudimos cargar las tareas necesarias para representar la distribución diaria.</p>}
          {detectarMutation.isError && <p className="mt-4 text-sm text-red-700" role="alert">{getApiErrorMessage(detectarMutation.error)}</p>}
        </section>

        {analisis && !detectarMutation.isPending && (
          <section className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm" aria-live="polite">
            <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
              <div>
                <h2 className="font-semibold text-slate-900">Distribución por día</h2>
                <p className="mt-1 text-sm text-slate-500">Una alerta aparece al superar {analisis.max_tareas_por_dia} tarea{analisis.max_tareas_por_dia === 1 ? '' : 's'} pendientes.</p>
              </div>
              {analisis.alertas.length > 0 && <span className="inline-flex w-fit items-center gap-1.5 rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-800"><AlertTriangle aria-hidden="true" size={14} />{analisis.alertas.length} día{analisis.alertas.length === 1 ? '' : 's'} con sobrecarga</span>}
            </div>

            <div className="space-y-3 p-5 sm:p-6">
              {fechas.map((fecha) => {
                const cantidad = cargaPorFecha[fecha] ?? 0
                const alerta = alertasPorFecha.get(fecha)
                const { weekday, label } = formatDayDate(fecha)
                return (
                  <article key={fecha} className={`rounded-lg border p-4 ${alerta ? 'border-amber-300 bg-amber-50' : 'border-slate-200 bg-slate-50/70'}`}>
                    <div className="grid items-center gap-3 sm:grid-cols-[9rem_1fr_auto]">
                      <div><p className={`font-medium capitalize ${alerta ? 'text-amber-950' : 'text-slate-800'}`}>{weekday}</p><p className="text-xs text-slate-500">{label}</p></div>
                      <div className="h-2.5 overflow-hidden rounded-full bg-white" aria-hidden="true"><div className={`h-full rounded-full ${alerta ? 'bg-amber-500' : 'bg-indigo-500'}`} style={{ width: `${cantidad === 0 ? 0 : Math.max(8, (cantidad / mayorCarga) * 100)}%` }} /></div>
                      <div className="flex items-center justify-between gap-3 sm:justify-end"><span className={`text-sm font-semibold ${alerta ? 'text-amber-900' : 'text-slate-700'}`}>{cantidad} tarea{cantidad === 1 ? '' : 's'}</span>{alerta && <span className="rounded-full bg-amber-200 px-2.5 py-1 text-xs font-semibold text-amber-900">Sobrecarga</span>}</div>
                    </div>
                    {alerta && <div className="mt-3 border-t border-amber-200 pt-3 text-sm text-amber-900"><p>{alerta.mensaje}</p><p className="mt-1 text-amber-800"><span className="font-medium">Sugerencia:</span> {alerta.sugerencia}</p></div>}
                  </article>
                )
              })}
            </div>

            {analisis.alertas.length === 0 ? (
              <div className="flex gap-3 border-t border-emerald-200 bg-emerald-50 px-5 py-4 text-sm text-emerald-800 sm:px-6"><CheckCircle2 className="mt-0.5 shrink-0" aria-hidden="true" size={18} /><div><p className="font-medium">No detectamos sobrecarga</p><p className="mt-1">Todos los días del período están dentro del máximo configurado.</p></div></div>
            ) : (
              <div className="flex flex-col gap-3 border-t border-slate-200 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
                <p className="text-sm text-slate-600">Puedes pedir alternativas. Solicitar propuestas no cambia ninguna fecha.</p>
                <button type="button" onClick={solicitarPropuestas} disabled={proponerMutation.isPending || confirmarMutation.isPending} className="inline-flex items-center justify-center gap-2 rounded-lg border border-cyan-200 bg-cyan-50 px-4 py-2.5 text-sm font-medium text-cyan-800 hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-60">
                  {proponerMutation.isPending ? <LoaderCircle className="animate-spin" aria-hidden="true" size={17} /> : <Sparkles aria-hidden="true" size={17} />}
                  {proponerMutation.isPending ? 'Buscando alternativas…' : 'Proponer reprogramación'}
                </button>
              </div>
            )}
          </section>
        )}

        {proponerMutation.isError && <section className="mt-6 rounded-xl border border-red-200 bg-red-50 p-5" role="alert"><h2 className="font-semibold text-red-900">No pudimos generar propuestas</h2><p className="mt-1 text-sm text-red-700">{getApiErrorMessage(proponerMutation.error)}</p></section>}

        {proponerMutation.isSuccess && propuestas.length === 0 && cambiosConfirmados.length === 0 && <section className="mt-6 rounded-xl border border-slate-200 bg-white p-6 text-center shadow-sm"><h2 className="font-semibold text-slate-900">No hay movimientos disponibles</h2><p className="mt-2 text-sm text-slate-600">No encontramos fechas con espacio suficiente dentro del período seleccionado.</p></section>}

        {propuestas.length > 0 && (
          <section className="mt-6 overflow-hidden rounded-xl border border-cyan-200 bg-cyan-50/40 shadow-sm">
            <div className="border-b border-cyan-100 px-5 py-4 sm:px-6">
              <div className="flex items-center gap-2"><RefreshCw className="text-cyan-700" aria-hidden="true" size={18} /><h2 className="font-semibold text-slate-900">Propuestas de reprogramación</h2></div>
              <p className="mt-2 text-sm font-medium text-cyan-900">Ningún cambio se aplicará hasta que confirmes.</p>
            </div>
            <div className="divide-y divide-cyan-100">
              {propuestas.map((propuesta) => {
                const tarea = tareasPorId.get(propuesta.tarea_id)
                return (
                  <label key={propuesta.tarea_id} className="flex cursor-pointer gap-3 px-5 py-5 hover:bg-cyan-50 sm:px-6">
                    <input type="checkbox" checked={seleccionadas.has(propuesta.tarea_id)} onChange={() => alternarSeleccion(propuesta.tarea_id)} disabled={confirmarMutation.isPending} className="mt-1 size-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 disabled:cursor-not-allowed" />
                    <span className="min-w-0 flex-1">
                      <span className="block font-semibold text-slate-900">{tarea?.nombre ?? `Tarea #${propuesta.tarea_id}`}</span>
                      <span className="mt-3 flex flex-wrap items-center gap-2 text-sm font-medium"><span className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-slate-700">{formatTaskDate(propuesta.fecha_actual)}</span><ArrowRight className="text-cyan-700" aria-hidden="true" size={18} /><span className="rounded-lg border border-cyan-200 bg-cyan-100 px-3 py-1.5 text-cyan-900">{formatTaskDate(propuesta.fecha_sugerida)}</span></span>
                      <span className="mt-3 block text-sm leading-6 text-slate-600">{propuesta.motivo}</span>
                    </span>
                  </label>
                )
              })}
            </div>
            <div className="flex flex-col gap-3 border-t border-cyan-100 px-5 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
              <p className="text-sm text-slate-600">{cantidadSeleccionada} cambio{cantidadSeleccionada === 1 ? '' : 's'} seleccionado{cantidadSeleccionada === 1 ? '' : 's'}</p>
              <button type="button" onClick={confirmarSeleccionadas} disabled={cantidadSeleccionada === 0 || confirmarMutation.isPending} className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">
                {confirmarMutation.isPending && <LoaderCircle className="animate-spin" aria-hidden="true" size={17} />}
                {confirmarMutation.isPending ? 'Guardando cambios…' : 'Confirmar cambios seleccionados'}
              </button>
            </div>
            {confirmarMutation.isError && <p className="border-t border-red-200 bg-red-50 px-5 py-4 text-sm text-red-700 sm:px-6" role="alert">{getApiErrorMessage(confirmarMutation.error)}</p>}
          </section>
        )}

        {cambiosConfirmados.length > 0 && (
          <section className="mt-6 overflow-hidden rounded-xl border border-emerald-200 bg-white shadow-sm" aria-live="polite">
            <div className="flex items-start gap-3 border-b border-emerald-200 bg-emerald-50 px-5 py-4 sm:px-6"><CheckCircle2 className="mt-0.5 shrink-0 text-emerald-700" aria-hidden="true" size={19} /><div><h2 className="font-semibold text-emerald-900">Cambios guardados</h2><p className="mt-1 text-sm text-emerald-800">El backend confirmó y persistió estas nuevas fechas.</p></div></div>
            <div className="divide-y divide-slate-100">
              {cambiosConfirmados.map(({ tarea, fechaAnterior }) => <article key={tarea.id} className="px-5 py-4 sm:px-6"><div className="flex flex-wrap items-center justify-between gap-2"><h3 className="font-medium text-slate-900">{tarea.nombre}</h3><span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-800">Cambio guardado</span></div><p className="mt-2 flex flex-wrap items-center gap-2 text-sm text-slate-600"><span>{formatTaskDate(fechaAnterior)}</span><ArrowRight aria-hidden="true" size={16} /><span className="font-medium text-emerald-700">{formatTaskDate(tarea.fecha_limite)}</span></p></article>)}
            </div>
          </section>
        )}
      </section>
    </main>
  )
}
