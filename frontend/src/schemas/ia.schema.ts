import { z } from 'zod'

export const textoIaSchema = z.object({
  texto: z.string().trim().min(1, 'Describe el trabajo que quieres planificar.').max(2000, 'El texto no puede superar los 2000 caracteres.'),
})

export type TextoIaValues = z.infer<typeof textoIaSchema>

export const planDiaSchema = z.object({
  fecha: z.string().date('Selecciona una fecha válida.'),
})

export type PlanDiaValues = z.infer<typeof planDiaSchema>

export const analisisCargaSchema = z.object({
  fecha_inicio: z.string().date('Selecciona una fecha válida.'),
  dias: z.number().int().min(1, 'El período mínimo es de 1 día.').max(31, 'El período máximo es de 31 días.'),
  max_tareas_por_dia: z.number().int().min(1, 'El umbral mínimo es 1.').max(20, 'El umbral máximo es 20.'),
})

export type AnalisisCargaValues = z.infer<typeof analisisCargaSchema>
