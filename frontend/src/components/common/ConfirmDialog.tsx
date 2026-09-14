import { LoaderCircle, TriangleAlert } from 'lucide-react'
import { useRef } from 'react'
import { useDialogFocus } from '../../hooks/useDialogFocus'

interface ConfirmDialogProps {
  title: string
  description: string
  confirmLabel?: string
  isPending?: boolean
  onCancel: () => void
  onConfirm: () => void
}

export function ConfirmDialog({
  title,
  description,
  confirmLabel = 'Eliminar',
  isPending = false,
  onCancel,
  onConfirm,
}: ConfirmDialogProps) {
  const dialogRef = useRef<HTMLElement>(null)
  useDialogFocus(dialogRef, onCancel, isPending)

  return (
    <div
      className="fixed inset-0 z-[60] grid place-items-end bg-slate-950/45 p-0 sm:place-items-center sm:p-5"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget && !isPending) onCancel()
      }}
      role="presentation"
    >
      <section
        ref={dialogRef}
        className="w-full rounded-t-2xl bg-white p-5 shadow-xl sm:max-w-md sm:rounded-2xl sm:p-6"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-dialog-title"
        aria-describedby="confirm-dialog-description"
      >
        <span className="flex size-10 items-center justify-center rounded-xl bg-red-50 text-red-700">
          <TriangleAlert aria-hidden="true" size={20} />
        </span>
        <h2 id="confirm-dialog-title" className="mt-4 text-xl font-semibold text-slate-900">{title}</h2>
        <p id="confirm-dialog-description" className="mt-2 text-sm leading-6 text-slate-600">{description}</p>
        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onCancel}
            disabled={isPending}
            data-autofocus
            className="rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isPending}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isPending && <LoaderCircle className="animate-spin" aria-hidden="true" size={16} />}
            {isPending ? 'Eliminando…' : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  )
}
