import { apiClient } from './client'
import type { Tarea, TareaPatch, TareaRequest } from '../types/tarea'

export async function listarTareas(): Promise<Tarea[]> {
  const { data } = await apiClient.get<Tarea[]>('/tareas')
  return data
}

export async function obtenerTarea(id: number): Promise<Tarea> {
  const { data } = await apiClient.get<Tarea>(`/tareas/${id}`)
  return data
}

export async function crearTarea(datos: TareaRequest): Promise<Tarea> {
  const { data } = await apiClient.post<Tarea>('/tareas', datos)
  return data
}

export async function actualizarTarea(id: number, cambios: TareaPatch): Promise<Tarea> {
  const { data } = await apiClient.patch<Tarea>(`/tareas/${id}`, cambios)
  return data
}

export async function eliminarTarea(id: number): Promise<void> {
  await apiClient.delete(`/tareas/${id}`)
}

export async function listarSubtareas(tareaId: number): Promise<Tarea[]> {
  const { data } = await apiClient.get<Tarea[]>(`/tareas/${tareaId}/subtareas`)
  return data
}

export async function crearSubtarea(tareaId: number, datos: TareaRequest): Promise<Tarea> {
  const { data } = await apiClient.post<Tarea>(`/tareas/${tareaId}/subtareas`, datos)
  return data
}

export async function actualizarSubtarea(tareaId: number, subtareaId: number, cambios: TareaPatch): Promise<Tarea> {
  const { data } = await apiClient.patch<Tarea>(`/tareas/${tareaId}/subtareas/${subtareaId}`, cambios)
  return data
}

export async function eliminarSubtarea(tareaId: number, subtareaId: number): Promise<void> {
  await apiClient.delete(`/tareas/${tareaId}/subtareas/${subtareaId}`)
}
