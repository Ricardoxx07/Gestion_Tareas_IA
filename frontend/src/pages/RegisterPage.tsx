import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { ArrowLeft, LoaderCircle, Sparkles, UserRoundPlus } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { registrarUsuario } from '../api/auth.api'
import { registroSchema } from '../schemas/auth.schema'
import type { RegistroFormValues } from '../schemas/auth.schema'
import { getApiErrorMessage } from '../utils/api-error'

export function RegisterPage() {
  const navigate = useNavigate()
  const form = useForm<RegistroFormValues>({
    resolver: zodResolver(registroSchema),
    defaultValues: { email: '', password: '', confirmPassword: '' },
  })
  const registerMutation = useMutation({
    mutationFn: registrarUsuario,
    onSuccess: (_, values) => {
      navigate('/login', { replace: true, state: { email: values.email, registered: true } })
    },
  })

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-8">
      <section className="mx-auto flex min-h-[calc(100vh-2rem)] max-w-lg items-center rounded-2xl border border-slate-200 bg-white p-6 shadow-sm sm:min-h-[calc(100vh-4rem)] sm:p-10">
        <div className="mx-auto w-full max-w-sm">
          <div className="flex items-center gap-3 text-slate-900">
            <span className="flex size-10 items-center justify-center rounded-xl bg-indigo-600 text-white"><Sparkles aria-hidden="true" size={20} /></span>
            <span className="font-semibold">Gestor de tareas</span>
          </div>
          <p className="mt-8 text-sm font-medium text-cyan-700">Empieza a planificar</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">Crea tu cuenta</h1>
          <p className="mt-2 text-sm text-slate-600">Solo necesitaremos tu email y una contraseña segura.</p>

          {registerMutation.isError && <p className="mt-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700" role="alert">{getApiErrorMessage(registerMutation.error)}</p>}

          <form className="mt-7 space-y-5" onSubmit={form.handleSubmit((values) => registerMutation.mutate({ email: values.email, password: values.password }))} noValidate aria-busy={registerMutation.isPending}>
            <div>
              <label htmlFor="register-email" className="block text-sm font-medium text-slate-700">Email</label>
              <input id="register-email" type="email" autoComplete="email" aria-invalid={Boolean(form.formState.errors.email)} aria-describedby={form.formState.errors.email ? 'register-email-error' : undefined} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 shadow-sm outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100" {...form.register('email')} />
              {form.formState.errors.email && <span id="register-email-error" className="mt-1 block text-sm text-red-600" role="alert">{form.formState.errors.email.message}</span>}
            </div>
            <div>
              <label htmlFor="register-password" className="block text-sm font-medium text-slate-700">Contraseña</label>
              <input id="register-password" type="password" autoComplete="new-password" aria-invalid={Boolean(form.formState.errors.password)} aria-describedby={form.formState.errors.password ? 'register-password-error' : undefined} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 shadow-sm outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100" {...form.register('password')} />
              {form.formState.errors.password && <span id="register-password-error" className="mt-1 block text-sm text-red-600" role="alert">{form.formState.errors.password.message}</span>}
            </div>
            <div>
              <label htmlFor="register-confirm-password" className="block text-sm font-medium text-slate-700">Confirmar contraseña</label>
              <input id="register-confirm-password" type="password" autoComplete="new-password" aria-invalid={Boolean(form.formState.errors.confirmPassword)} aria-describedby={form.formState.errors.confirmPassword ? 'register-confirm-password-error' : undefined} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 shadow-sm outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100" {...form.register('confirmPassword')} />
              {form.formState.errors.confirmPassword && <span id="register-confirm-password-error" className="mt-1 block text-sm text-red-600" role="alert">{form.formState.errors.confirmPassword.message}</span>}
            </div>
            <button type="submit" disabled={registerMutation.isPending} className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">
              {registerMutation.isPending ? <LoaderCircle className="animate-spin" aria-hidden="true" size={18} /> : <UserRoundPlus aria-hidden="true" size={18} />}
              {registerMutation.isPending ? 'Creando cuenta…' : 'Crear cuenta'}
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-slate-600"><Link to="/login" className="font-medium text-indigo-600 hover:text-indigo-700"><ArrowLeft className="mr-1 inline" aria-hidden="true" size={14} />Volver a iniciar sesión</Link></p>
        </div>
      </section>
    </main>
  )
}
