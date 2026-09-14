import { apiClient } from './client'
import type {
  AnalisisCargaRequest,
  AnalisisSobrecargaResponse,
  DescomposicionTareaResponse,
  PlanDiaRequest,
  PlanDiaResponse,
  PlanificarTextoRequest,
  PropuestasConfirmadasResponse,
  PropuestasReprogramacionResponse,
  ReprogramacionConfirmarItem,
  ReprogramacionesConfirmadasResponse,
  PropuestasTareasResponse,
  TareaParaConfirmar,
} from '../types/ia'

export async function planificarTexto(datos: PlanificarTextoRequest): Promise<PropuestasTareasResponse> {
  const { data } = await apiClient.post<PropuestasTareasResponse>('/ia/planificar', datos)
  return data
}

export async function descomponerTarea(datos: PlanificarTextoRequest): Promise<DescomposicionTareaResponse> {
  const { data } = await apiClient.post<DescomposicionTareaResponse>('/ia/descomponer', datos)
  return data
}

export async function confirmarPropuestas(tareas: TareaParaConfirmar[]): Promise<PropuestasConfirmadasResponse> {
  const { data } = await apiClient.post<PropuestasConfirmadasResponse>('/ia/propuestas/confirmar', { tareas })
  return data
}

export async function planificarDia(datos: PlanDiaRequest): Promise<PlanDiaResponse> {
  const { data } = await apiClient.post<PlanDiaResponse>('/ia/plan-dia', datos)
  return data
}

export async function detectarSobrecarga(datos: AnalisisCargaRequest): Promise<AnalisisSobrecargaResponse> {
  const { data } = await apiClient.post<AnalisisSobrecargaResponse>('/ia/detectar-sobrecarga', datos)
  return data
}

export async function proponerReprogramacion(datos: AnalisisCargaRequest): Promise<PropuestasReprogramacionResponse> {
  const { data } = await apiClient.post<PropuestasReprogramacionResponse>('/ia/proponer-reprogramacion', datos)
  return data
}

export async function confirmarReprogramaciones(reprogramaciones: ReprogramacionConfirmarItem[]): Promise<ReprogramacionesConfirmadasResponse> {
  const { data } = await apiClient.post<ReprogramacionesConfirmadasResponse>('/ia/reprogramaciones/confirmar', { reprogramaciones })
  return data
}
