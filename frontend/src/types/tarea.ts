export type PrioridadTarea = 'baja' | 'media' | 'alta'

export interface Tarea {
  id: number
  nombre: string
  completada: boolean
  fecha_limite: string | null
  prioridad: PrioridadTarea
  created_at: string | null
  tarea_padre_id: number | null
}

export interface TareaRequest {
  nombre: string
  fecha_limite: string | null
  prioridad: PrioridadTarea
}

export type TareaPatch = Partial<TareaRequest> & {
  completada?: boolean
}
