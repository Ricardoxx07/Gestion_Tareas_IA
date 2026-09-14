import { z } from 'zod'

export const tareaFormSchema = z.object({
  nombre: z.string().trim().min(1, 'Ingresa un nombre para la tarea.').max(255, 'El nombre no puede superar los 255 caracteres.'),
  fecha_limite: z.string(),
  prioridad: z.enum(['baja', 'media', 'alta']),
})

export type TareaFormValues = z.infer<typeof tareaFormSchema>
