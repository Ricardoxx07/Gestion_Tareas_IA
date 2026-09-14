import { zodResolver } from '@hookform/resolvers/zod'
import { Inbox, LoaderCircle, Sparkles } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useConfirmarPropuestas, useDescomponerTarea } from '../../hooks/useIA'
import { useToast } from '../../hooks/useToast'
import { textoIaSchema, type TextoIaValues } from '../../schemas/ia.schema'
import type { SubtareaPropuesta } from '../../types/ia'
import { getApiErrorMessage } from '../../utils/api-error'

type SubtareaPendiente = SubtareaPropuesta & { id: string }

interface TaskDecompositionPanelProps {
  tareaId: number
  tareaNombre: string
}

export function TaskDecompositionPanel({ tareaId, tareaNombre }: TaskDecompositionPanelProps) {
  const descomponerMutation = useDescomponerTarea()
  const confirmarMutation = useConfirmarPropuestas()
  const [propuestas, setPropuestas] = useState<SubtareaPendiente[]>([])
  const [seleccionadas, setSeleccionadas] = useState<Set<string>>(new Set())
  const { showToast } = useToast()
  const { register, handleSubmit, formState: { errors } } = useForm<TextoIaValues>({
    resolver: zodResolver(textoIaSchema),
    defaultValues: { texto: tareaNombre },
  })

  const generarPropuestas = (values: TextoIaValues) => {
    setPropuestas([])
    setSeleccionadas(new Set())
    confirmarMutation.reset()
    descomponerMutation.mutate(values, {
      onSuccess: ({ subtareas }) => {
        const pendientes = subtareas.map((subtarea) => ({ ...subtarea, id: `${Date.now()}-${subtarea.orden}` }))
        setPropuestas(pendientes)
        setSeleccionadas(new Set(pendientes.map((subtarea) => subtarea.id)))
      },
      onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
    })
  }

  const alternarSeleccion = (id: string) => setSeleccionadas((actuales) => {
    const siguiente = new Set(actuales)
    if (siguiente.has(id)) siguiente.delete(id)
    else siguiente.add(id)
    return siguiente
  })

  const confirmarSeleccionadas = () => {
    const paraConfirmar = propuestas.filter((propuesta) => seleccionadas.has(propuesta.id))
    if (paraConfirmar.length === 0) return

    confirmarMutation.mutate(
      paraConfirmar.map(({ nombre }) => ({ nombre, fecha_limite: null, prioridad: 'media' as const, tarea_padre_id: tareaId })),
      {
        onSuccess: ({ tareas_confirmadas }) => {
          const idsConfirmados = new Set(paraConfirmar.map((propuesta) => propuesta.id))
          setPropuestas((actuales) => actuales.filter((propuesta) => !idsConfirmados.has(propuesta.id)))
          setSeleccionadas(new Set())
          descomponerMutation.reset()
          showToast(`${tareas_confirmadas.length} subtarea${tareas_confirmadas.length === 1 ? '' : 's'} guardada${tareas_confirmadas.length === 1 ? '' : 's'} bajo esta tarea.`)
        },
        onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
      },
    )
  }

  const seleccionadasCantidad = propuestas.filter((propuesta) => seleccionadas.has(propuesta.id)).length

  return <section className="mt-5 rounded-lg border border-cyan-200 bg-cyan-50/50 p-4 sm:p-5">
    <div className="flex items-center gap-2"><Sparkles className="text-cyan-700" aria-hidden="true" size={18} /><h3 className="font-semibold text-slate-900">Descomponer con IA</h3></div>
    <p className="mt-1 text-sm text-slate-600">Obtén pasos sugeridos para esta tarea. Ninguna subtarea se creará sin tu confirmación.</p>
    <form className="mt-4" onSubmit={handleSubmit(generarPropuestas)} noValidate aria-busy={descomponerMutation.isPending}><label htmlFor="texto-descomposicion" className="text-sm font-medium text-slate-800">Contexto de la tarea</label><textarea id="texto-descomposicion" rows={3} maxLength={2000} className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 shadow-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100" aria-invalid={Boolean(errors.texto)} aria-describedby={errors.texto ? 'texto-descomposicion-error' : undefined} {...register('texto')} />{errors.texto && <p id="texto-descomposicion-error" className="mt-2 text-sm text-red-700" role="alert">{errors.texto.message}</p>}{descomponerMutation.isError && <p className="mt-2 text-sm text-red-700" role="alert">{getApiErrorMessage(descomponerMutation.error)}</p>}<button type="submit" disabled={descomponerMutation.isPending || confirmarMutation.isPending} className="mt-3 inline-flex items-center gap-2 rounded-lg border border-cyan-700 bg-white px-3.5 py-2 text-sm font-medium text-cyan-800 hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-60">{descomponerMutation.isPending && <LoaderCircle className="animate-spin" aria-hidden="true" size={16} />}{descomponerMutation.isPending ? 'Generando pasos…' : 'Proponer subtareas'}</button></form>
    {descomponerMutation.isSuccess && propuestas.length === 0 && <div className="mt-5 rounded-lg border border-slate-200 bg-white px-4 py-6 text-center" role="status"><Inbox className="mx-auto text-slate-400" aria-hidden="true" size={22} /><p className="mt-2 text-sm font-medium text-slate-800">No se generaron subtareas</p><p className="mt-1 text-xs text-slate-600">Añade más contexto sobre el resultado que quieres conseguir.</p></div>}
    {propuestas.length > 0 && <div className="mt-5 rounded-lg border border-cyan-200 bg-white"><div className="border-b border-cyan-100 px-4 py-3"><p className="text-sm font-semibold text-slate-900">Subtareas propuestas por IA</p><p className="mt-1 text-xs text-slate-600">Son sugerencias pendientes; las subtareas guardadas se muestran arriba.</p></div><div className="divide-y divide-slate-100">{propuestas.map((propuesta) => <label key={propuesta.id} className="flex cursor-pointer gap-3 px-4 py-3 hover:bg-cyan-50"><input type="checkbox" checked={seleccionadas.has(propuesta.id)} onChange={() => alternarSeleccion(propuesta.id)} disabled={confirmarMutation.isPending} className="mt-1 size-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" /><span><span className="font-medium text-slate-900">{propuesta.orden}. {propuesta.nombre}</span><span className="mt-1 block text-sm text-slate-600">{propuesta.motivo}</span></span></label>)}</div><div className="flex flex-col gap-3 border-t border-cyan-100 px-4 py-3 sm:flex-row sm:items-center sm:justify-between"><span className="text-sm text-slate-600">{seleccionadasCantidad} seleccionada{seleccionadasCantidad === 1 ? '' : 's'}</span><div><button type="button" onClick={confirmarSeleccionadas} disabled={seleccionadasCantidad === 0 || confirmarMutation.isPending} className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-3.5 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">{confirmarMutation.isPending && <LoaderCircle className="animate-spin" aria-hidden="true" size={16} />}{confirmarMutation.isPending ? 'Guardando…' : 'Confirmar seleccionadas'}</button>{confirmarMutation.isError && <p className="mt-2 text-sm text-red-700" role="alert">{getApiErrorMessage(confirmarMutation.error)}</p>}</div></div></div>}
  </section>
}
