import { useContext } from 'react'
import { ToastContext } from '../components/common/toast-context'
import type { ToastContextValue } from '../components/common/toast-context'

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext)

  if (!context) {
    throw new Error('useToast debe utilizarse dentro de ToastProvider.')
  }

  return context
}
