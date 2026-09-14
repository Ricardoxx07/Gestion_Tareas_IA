import { useEffect, useRef } from 'react'
import type { RefObject } from 'react'

const focusableSelector = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(',')

export function useDialogFocus(
  dialogRef: RefObject<HTMLElement | null>,
  onClose: () => void,
  preventClose = false,
) {
  const onCloseRef = useRef(onClose)
  const preventCloseRef = useRef(preventClose)

  useEffect(() => {
    onCloseRef.current = onClose
  }, [onClose])

  useEffect(() => {
    preventCloseRef.current = preventClose
  }, [preventClose])

  useEffect(() => {
    const previousFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    const focusInitialElement = () => {
      const initial = dialogRef.current?.querySelector<HTMLElement>('[data-autofocus]')
        ?? dialogRef.current?.querySelector<HTMLElement>(focusableSelector)
      initial?.focus()
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !preventCloseRef.current) {
        event.preventDefault()
        onCloseRef.current()
        return
      }

      if (event.key !== 'Tab') return
      const focusable = Array.from(dialogRef.current?.querySelectorAll<HTMLElement>(focusableSelector) ?? [])
      if (focusable.length === 0) return
      const first = focusable[0]
      const last = focusable.at(-1)

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last?.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }

    queueMicrotask(focusInitialElement)
    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = previousOverflow
      previousFocus?.focus()
    }
  }, [dialogRef])
}
