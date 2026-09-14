import { CircleCheck, CircleX, Info, X } from 'lucide-react'
import { useCallback, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { ToastContext, type ToastTone } from './toast-context'

interface ToastMessage {
  id: number
  message: string
  tone: ToastTone
}

const toneStyles: Record<ToastTone, string> = {
  success: 'border-emerald-200 bg-white text-emerald-700',
  error: 'border-red-200 bg-white text-red-700',
  info: 'border-slate-200 bg-white text-indigo-700',
}

const toneIcons = {
  success: CircleCheck,
  error: CircleX,
  info: Info,
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const nextId = useRef(0)
  const [toasts, setToasts] = useState<ToastMessage[]>([])

  const dismissToast = useCallback((id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
  }, [])

  const showToast = useCallback((message: string, tone: ToastTone = 'success') => {
    nextId.current += 1
    const id = nextId.current
    setToasts((current) => [...current, { id, message, tone }])
    window.setTimeout(() => dismissToast(id), 4500)
  }, [dismissToast])

  const value = useMemo(() => ({ showToast }), [showToast])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed inset-x-4 bottom-4 z-[70] flex flex-col items-stretch gap-3 sm:left-auto sm:right-5 sm:max-w-sm" aria-label="Notificaciones">
        {toasts.map((toast) => {
          const Icon = toneIcons[toast.tone]
          return (
            <div
              key={toast.id}
              className={`pointer-events-auto flex items-start gap-3 rounded-xl border p-4 shadow-lg ${toneStyles[toast.tone]}`}
              role={toast.tone === 'error' ? 'alert' : 'status'}
            >
              <Icon className="mt-0.5 shrink-0" aria-hidden="true" size={19} />
              <p className="min-w-0 flex-1 text-sm leading-5 text-slate-700">{toast.message}</p>
              <button
                type="button"
                onClick={() => dismissToast(toast.id)}
                className="-m-1 shrink-0 rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700"
                aria-label="Cerrar notificación"
              >
                <X aria-hidden="true" size={17} />
              </button>
            </div>
          )
        })}
      </div>
    </ToastContext.Provider>
  )
}
