import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  confirmarPropuestas,
  confirmarReprogramaciones,
  descomponerTarea,
  detectarSobrecarga,
  planificarDia,
  planificarTexto,
  proponerReprogramacion,
} from '../api/ia.api'
import { tareasQueryKey } from './useTareas'
import type { Tarea } from '../types/tarea'

export function usePlanificarTexto() {
  return useMutation({ mutationFn: planificarTexto })
}

export function useDescomponerTarea() {
  return useMutation({ mutationFn: descomponerTarea })
}

export function useConfirmarPropuestas() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: confirmarPropuestas,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: tareasQueryKey }),
  })
}

export function usePlanDia() {
  return useMutation({ mutationFn: planificarDia })
}

export function useDetectarSobrecarga() {
  return useMutation({ mutationFn: detectarSobrecarga })
}

export function useProponerReprogramacion() {
  return useMutation({ mutationFn: proponerReprogramacion })
}

export function useConfirmarReprogramaciones() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: confirmarReprogramaciones,
    onSuccess: ({ tareas_actualizadas }) => {
      const actualizadasPorId = new Map(tareas_actualizadas.map((tarea) => [tarea.id, tarea]))
      queryClient.setQueryData<Tarea[]>(tareasQueryKey, (actuales) =>
        actuales?.map((tarea) => actualizadasPorId.get(tarea.id) ?? tarea),
      )
      void queryClient.invalidateQueries({ queryKey: tareasQueryKey })
    },
  })
}
