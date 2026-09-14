import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@tanstack/react-query'
import { ArrowRight, KeyRound, LoaderCircle, Sparkles } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { loginSchema } from '../schemas/auth.schema'
import type { LoginFormValues } from '../schemas/auth.schema'
import { useAuth } from '../hooks/useAuth'
import { getApiErrorMessage } from '../utils/api-error'

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: typeof location.state?.email === 'string' ? location.state.email : '',
      password: '',
    },
  })
  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      const from = location.state?.from?.pathname
      navigate(typeof from === 'string' ? from : '/dashboard', { replace: true })
    },
  })

  const registered = location.state?.registered === true
  const sessionExpired = location.state?.sessionExpired === true

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-8">
      <section className="mx-auto grid min-h-[calc(100vh-2rem)] max-w-5xl overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm lg:grid-cols-2 sm:min-h-[calc(100vh-4rem)]">
        <div className="hidden flex-col justify-between bg-slate-900 p-10 text-white lg:flex">
          <div className="flex items-center gap-3">
            <span className="flex size-10 items-center justify-center rounded-xl bg-indigo-500">
              <Sparkles aria-hidden="true" size={20} />
            </span>
            <span className="font-semibold">Gestor de tareas</span>
          </div>
          <div>
            <p className="text-sm font-medium text-cyan-300">Planificación asistida por IA</p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight">Organiza tu trabajo con claridad.</h1>
            <p className="mt-4 max-w-md leading-7 text-slate-300">Gestiona tus tareas y revisa cada propuesta antes de que se guarde.</p>
          </div>
          <p className="text-sm text-slate-400">Tu información está separada y protegida por sesión.</p>
        </div>

        <div className="flex items-center p-6 sm:p-10">
          <div className="mx-auto w-full max-w-sm">
            <div className="mb-8 lg:hidden">
              <div className="flex items-center gap-3 text-slate-900">
                <span className="flex size-10 items-center justify-center rounded-xl bg-indigo-600 text-white"><Sparkles aria-hidden="true" size={20} /></span>
                <span className="font-semibold">Gestor de tareas</span>
              </div>
            </div>
            <p className="text-sm font-medium text-cyan-700">Bienvenido de nuevo</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">Inicia sesión</h1>
            <p className="mt-2 text-sm text-slate-600">Accede a tu espacio de planificación.</p>

            {registered && <p className="mt-5 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-800" role="status">Tu cuenta fue creada. Ya puedes iniciar sesión.</p>}
            {sessionExpired && <p className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800" role="status">Tu sesión expiró o ya no es válida. Inicia sesión nuevamente.</p>}
            {loginMutation.isError && <p className="mt-5 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700" role="alert">{getApiErrorMessage(loginMutation.error)}</p>}

            <form className="mt-7 space-y-5" onSubmit={form.handleSubmit((values) => loginMutation.mutate(values))} noValidate aria-busy={loginMutation.isPending}>
              <div>
                <label htmlFor="login-email" className="block text-sm font-medium text-slate-700">Email</label>
                <input id="login-email" type="email" autoComplete="email" aria-invalid={Boolean(form.formState.errors.email)} aria-describedby={form.formState.errors.email ? 'login-email-error' : undefined} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 shadow-sm outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100" {...form.register('email')} />
                {form.formState.errors.email && <span id="login-email-error" className="mt-1 block text-sm text-red-600" role="alert">{form.formState.errors.email.message}</span>}
              </div>
              <div>
                <label htmlFor="login-password" className="block text-sm font-medium text-slate-700">Contraseña</label>
                <input id="login-password" type="password" autoComplete="current-password" aria-invalid={Boolean(form.formState.errors.password)} aria-describedby={form.formState.errors.password ? 'login-password-error' : undefined} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-slate-900 shadow-sm outline-none transition focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100" {...form.register('password')} />
                {form.formState.errors.password && <span id="login-password-error" className="mt-1 block text-sm text-red-600" role="alert">{form.formState.errors.password.message}</span>}
              </div>
              <button type="submit" disabled={loginMutation.isPending} className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60">
                {loginMutation.isPending ? <LoaderCircle className="animate-spin" aria-hidden="true" size={18} /> : <KeyRound aria-hidden="true" size={18} />}
                {loginMutation.isPending ? 'Iniciando sesión…' : 'Iniciar sesión'}
              </button>
            </form>
            <p className="mt-6 text-center text-sm text-slate-600">¿Aún no tienes una cuenta? <Link to="/registro" className="font-medium text-indigo-600 hover:text-indigo-700">Crear cuenta <ArrowRight className="inline" aria-hidden="true" size={14} /></Link></p>
          </div>
        </div>
      </section>
    </main>
  )
}
