import type { PrioridadTarea, Tarea } from './tarea'

export interface PlanificarTextoRequest {
  texto: string
}

export interface TareaPropuesta {
  nombre: string
  fecha_sugerida: string | null
  prioridad_sugerida: PrioridadTarea
  motivo: string
}

export interface PropuestasTareasResponse {
  tareas_propuestas: TareaPropuesta[]
}

export interface SubtareaPropuesta {
  orden: number
  nombre: string
  motivo: string
}

export interface DescomposicionTareaResponse {
  tarea_original: string
  subtareas: SubtareaPropuesta[]
}

export interface TareaParaConfirmar {
  nombre: string
  fecha_limite: string | null
  prioridad: PrioridadTarea
  tarea_padre_id?: number
}

export interface PropuestasConfirmadasResponse {
  tareas_confirmadas: Tarea[]
}

export interface PlanDiaRequest {
  fecha?: string | null
}

export interface RecomendacionPlanDia {
  tarea_id: number
  orden: number
  motivo: string
}

export interface PlanDiaResponse {
  fecha: string
  plan: RecomendacionPlanDia[]
  resumen: string
}

export interface AnalisisCargaRequest {
  fecha_inicio?: string | null
  dias: number
  max_tareas_por_dia: number
}

export interface AlertaSobrecarga {
  fecha: string
  mensaje: string
  sugerencia: string
  cantidad_tareas: number
  tarea_ids: number[]
}

export interface AnalisisSobrecargaResponse {
  fecha_inicio: string
  fecha_fin: string
  max_tareas_por_dia: number
  alertas: AlertaSobrecarga[]
}

export interface PropuestaReprogramacion {
  tarea_id: number
  fecha_actual: string
  fecha_sugerida: string
  motivo: string
}

export interface PropuestasReprogramacionResponse {
  fecha_inicio: string
  fecha_fin: string
  max_tareas_por_dia: number
  propuestas: PropuestaReprogramacion[]
}

export interface ReprogramacionConfirmarItem {
  tarea_id: number
  fecha_actual: string
  fecha_sugerida: string
}

export interface ReprogramacionesConfirmadasResponse {
  tareas_actualizadas: Tarea[]
}
