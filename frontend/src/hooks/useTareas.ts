import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  actualizarSubtarea,
  actualizarTarea,
  crearSubtarea,
  crearTarea,
  eliminarSubtarea,
  eliminarTarea,
  listarSubtareas,
  listarTareas,
  obtenerTarea,
} from '../api/tareas.api'
import type { TareaPatch, TareaRequest } from '../types/tarea'

export const tareasQueryKey = ['tareas'] as const

export function useTareas() {
  return useQuery({ queryKey: tareasQueryKey, queryFn: listarTareas })
}

export function useTarea(tareaId: number | null) {
  return useQuery({
    queryKey: [...tareasQueryKey, tareaId],
    queryFn: () => obtenerTarea(tareaId as number),
    enabled: tareaId !== null,
  })
}

export function useSubtareas(tareaId: number | null) {
  return useQuery({
    queryKey: [...tareasQueryKey, tareaId, 'subtareas'],
    queryFn: () => listarSubtareas(tareaId as number),
    enabled: tareaId !== null,
  })
}

function useInvalidarTareas() {
  const queryClient = useQueryClient()
  return () => queryClient.invalidateQueries({ queryKey: tareasQueryKey })
}

export function useCrearTarea() {
  const invalidarTareas = useInvalidarTareas()
  return useMutation({ mutationFn: crearTarea, onSuccess: invalidarTareas })
}

export function useActualizarTarea() {
  const invalidarTareas = useInvalidarTareas()
  return useMutation({
    mutationFn: ({ id, cambios }: { id: number; cambios: TareaPatch }) => actualizarTarea(id, cambios),
    onSuccess: invalidarTareas,
  })
}

export function useEliminarTarea() {
  const invalidarTareas = useInvalidarTareas()
  return useMutation({ mutationFn: eliminarTarea, onSuccess: invalidarTareas })
}

export function useCrearSubtarea() {
  const invalidarTareas = useInvalidarTareas()
  return useMutation({
    mutationFn: ({ tareaId, datos }: { tareaId: number; datos: TareaRequest }) => crearSubtarea(tareaId, datos),
    onSuccess: invalidarTareas,
  })
}

export function useActualizarSubtarea() {
  const invalidarTareas = useInvalidarTareas()
  return useMutation({
    mutationFn: ({ tareaId, subtareaId, cambios }: { tareaId: number; subtareaId: number; cambios: TareaPatch }) => actualizarSubtarea(tareaId, subtareaId, cambios),
    onSuccess: invalidarTareas,
  })
}

export function useEliminarSubtarea() {
  const invalidarTareas = useInvalidarTareas()
  return useMutation({
    mutationFn: ({ tareaId, subtareaId }: { tareaId: number; subtareaId: number }) => eliminarSubtarea(tareaId, subtareaId),
    onSuccess: invalidarTareas,
  })
}
