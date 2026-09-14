import type { PrioridadTarea } from '../types/tarea'

export function formatTaskDate(fecha: string | null): string {
  if (!fecha) return 'Sin fecha límite'

  return new Intl.DateTimeFormat('es-PE', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(`${fecha}T00:00:00`))
}

export const priorityStyles: Record<PrioridadTarea, string> = {
  alta: 'border-red-200 bg-red-50 text-red-700',
  media: 'border-amber-200 bg-amber-50 text-amber-700',
  baja: 'border-emerald-200 bg-emerald-50 text-emerald-700',
}

export const priorityLabel: Record<PrioridadTarea, string> = {
  alta: 'Alta',
  media: 'Media',
  baja: 'Baja',
}
