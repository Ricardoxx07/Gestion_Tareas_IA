import { zodResolver } from '@hookform/resolvers/zod'
import { LoaderCircle, X } from 'lucide-react'
import { useEffect, useId, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { useDialogFocus } from '../../hooks/useDialogFocus'
import { tareaFormSchema } from '../../schemas/tarea.schema'
import type { TareaFormValues } from '../../schemas/tarea.schema'
import type { Tarea, TareaRequest } from '../../types/tarea'
import { getApiErrorMessage } from '../../utils/api-error'

interface TaskFormProps {
  title: string
  submitLabel: string
  task?: Tarea
  error?: unknown
  isPending: boolean
  onClose: () => void
  onSubmit: (values: TareaRequest) => void
}

function getDefaultValues(task?: Tarea): TareaFormValues {
  return {
    nombre: task?.nombre ?? '',
    fecha_limite: task?.fecha_limite ?? '',
    prioridad: task?.prioridad ?? 'media',
  }
}

export function TaskForm({ title, submitLabel, task, error, isPending, onClose, onSubmit }: TaskFormProps) {
  const dialogRef = useRef<HTMLElement>(null)
  const formId = useId()
  const form = useForm<TareaFormValues>({
    resolver: zodResolver(tareaFormSchema),
    defaultValues: getDefaultValues(task),
  })

  useEffect(() => {
    form.reset(getDefaultValues(task))
  }, [form, task])

  useDialogFocus(dialogRef, onClose, isPending)

  const nameErrorId = form.formState.errors.nombre ? `${formId}-nombre-error` : undefined
  const submitForm = (values: TareaFormValues) => {
    onSubmit({
      ...values,
      fecha_limite: values.fecha_limite || null,
    })
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end bg-slate-950/45 p-0 sm:items-center sm:justify-center sm:p-5"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !isPending) onClose()
      }}
      role="presentation"
    >
      <section ref={dialogRef} className="max-h-[95dvh] w-full overflow-y-auto rounded-t-2xl bg-white p-5 shadow-xl sm:max-w-lg sm:rounded-2xl sm:p-6" role="dialog" aria-modal="true" aria-labelledby={`${formId}-title`}>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 id={`${formId}-title`} className="text-xl font-semibold text-slate-900">{title}</h2>
            <p className="mt-1 text-sm text-slate-600">Define los datos que se guardarán en tu lista.</p>
          </div>
          <button type="button" onClick={onClose} disabled={isPending} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-700 disabled:opacity-50" aria-label="Cerrar formulario">
            <X aria-hidden="true" size={20} />
          </button>
        </div>

        {Boolean(error) && <p className="mt-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700" role="alert">{getApiErrorMessage(error)}</p>}

        <form className="mt-6 space-y-5" onSubmit={form.handleSubmit(submitForm)} noValidate aria-busy={isPending}>
          <div>
            <label htmlFor={`${formId}-nombre`} className="block text-sm font-medium text-slate-700">Nombre</label>
            <input id={`${formId}-nombre`} data-autofocus maxLength={255} aria-invalid={Boolean(nameErrorId)} aria-describedby={nameErrorId} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 shadow-sm outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100" {...form.register('nombre')} />
            {form.formState.errors.nombre && <span id={nameErrorId} className="mt-1 block text-sm text-red-600" role="alert">{form.formState.errors.nombre.message}</span>}
          </div>
          <div className="grid gap-5 sm:grid-cols-2">
            <div>
              <label htmlFor={`${formId}-fecha`} className="block text-sm font-medium text-slate-700">Fecha límite</label>
              <input id={`${formId}-fecha`} type="date" className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 shadow-sm outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100" {...form.register('fecha_limite')} />
            </div>
            <div>
              <label htmlFor={`${formId}-prioridad`} className="block text-sm font-medium text-slate-700">Prioridad</label>
              <select id={`${formId}-prioridad`} className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-slate-900 shadow-sm outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100" {...form.register('prioridad')}>
                <option value="baja">Baja</option>
                <option value="media">Media</option>
                <option value="alta">Alta</option>
              </select>
            </div>
          </div>
          <div className="flex flex-col-reverse gap-3 pt-1 sm:flex-row sm:justify-end">
            <button type="button" onClick={onClose} disabled={isPending} className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60">Cancelar</button>
            <button type="submit" disabled={isPending} className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">
              {isPending && <LoaderCircle className="animate-spin" aria-hidden="true" size={16} />}
              {submitLabel}
            </button>
          </div>
        </form>
      </section>
    </div>
  )
}
