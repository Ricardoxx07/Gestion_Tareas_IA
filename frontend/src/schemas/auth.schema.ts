import { z } from 'zod'

const email = z.string().trim().email('Ingresa un email válido.')
const password = z.string().min(8, 'La contraseña debe tener al menos 8 caracteres.').max(128, 'La contraseña no puede superar los 128 caracteres.')

export const loginSchema = z.object({ email, password })

export const registroSchema = z
  .object({
    email,
    password,
    confirmPassword: z.string(),
  })
  .refine((datos) => datos.password === datos.confirmPassword, {
    message: 'Las contraseñas no coinciden.',
    path: ['confirmPassword'],
  })

export type LoginFormValues = z.infer<typeof loginSchema>
export type RegistroFormValues = z.infer<typeof registroSchema>
