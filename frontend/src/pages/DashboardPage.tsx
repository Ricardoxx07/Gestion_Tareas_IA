import { ArrowRight, CalendarCheck2, CalendarDays, CheckCircle2, Circle, ListTodo, Sparkles } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useTareas } from '../hooks/useTareas'
import { getApiErrorMessage } from '../utils/api-error'
import { formatTaskDate, priorityLabel, priorityStyles } from '../utils/tarea'

export function DashboardPage() {
  const { user } = useAuth()
  const { data: allTasks = [], error, isError, isPending, refetch } = useTareas()
  const tasks = allTasks.filter((task) => task.tarea_padre_id === null)
  const pending = tasks.filter((task) => !task.completada)
  const now = new Date()
  const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
  const metrics = [
    { label: 'Pendientes', value: pending.length, icon: Circle, color: 'text-indigo-600' },
    { label: 'Para hoy', value: pending.filter((task) => task.fecha_limite === today).length, icon: CalendarDays, color: 'text-amber-600' },
    { label: 'Alta prioridad', value: pending.filter((task) => task.prioridad === 'alta').length, icon: ListTodo, color: 'text-red-600' },
    { label: 'Completadas', value: tasks.filter((task) => task.completada).length, icon: CheckCircle2, color: 'text-emerald-600' },
  ]

  return (
    <main className="p-5 sm:p-8">
      <section className="mx-auto max-w-6xl">
        <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div>
            <p className="text-sm font-medium text-cyan-700">Tu espacio de trabajo</p>
            <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">Hola, {user?.email?.split('@')[0]}</h1>
            <p className="mt-2 text-slate-600">Revisa lo importante y mantén tus pendientes en movimiento.</p>
          </div>
          <div className="flex flex-wrap gap-3"><Link to="/plan-dia" className="inline-flex items-center justify-center gap-2 rounded-lg border border-cyan-200 bg-cyan-50 px-4 py-2.5 text-sm font-medium text-cyan-800 hover:bg-cyan-100"><CalendarCheck2 aria-hidden="true" size={16} />Planificar mi día</Link><Link to="/planificar" className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100"><Sparkles aria-hidden="true" size={16} />Planificar con IA</Link><Link to="/tareas" className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700">Ver todas las tareas<ArrowRight aria-hidden="true" size={16} /></Link></div>
        </header>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {metrics.map(({ label, value, icon: Icon, color }) => <article key={label} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><Icon className={color} aria-hidden="true" size={20} /><p className="mt-5 text-3xl font-semibold text-slate-900">{isPending ? '—' : value}</p><p className="mt-1 text-sm text-slate-600">{label}</p></article>)}
        </div>

        <section className="mt-8 rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between gap-4 border-b border-slate-200 px-5 py-4 sm:px-6"><div><h2 className="font-semibold text-slate-900">Próximas tareas</h2><p className="mt-1 text-sm text-slate-500">Tus pendientes con fecha más cercana.</p></div><Link to="/tareas" className="text-sm font-medium text-indigo-600 hover:text-indigo-700">Gestionar</Link></div>
          {isError ? <div className="p-6" role="alert"><p className="text-sm text-red-700">{getApiErrorMessage(error)}</p><button type="button" onClick={() => void refetch()} className="mt-3 text-sm font-medium text-red-800 underline">Reintentar</button></div> : pending.length === 0 && !isPending ? <div className="p-8 text-center"><p className="font-medium text-slate-900">No tienes tareas pendientes.</p><Link to="/tareas" className="mt-2 inline-block text-sm font-medium text-indigo-600 hover:text-indigo-700">Crear mi primera tarea</Link></div> : <div className="divide-y divide-slate-100" aria-label={isPending ? 'Cargando próximas tareas' : undefined} aria-busy={isPending}>{isPending ? Array.from({ length: 3 }).map((_, index) => <div key={index} className="h-16 animate-pulse bg-slate-50" />) : [...pending].sort((a, b) => (a.fecha_limite ?? '9999').localeCompare(b.fecha_limite ?? '9999')).slice(0, 4).map((task) => <Link to={`/tareas/${task.id}`} key={task.id} className="flex items-center justify-between gap-4 px-5 py-4 hover:bg-slate-50 sm:px-6"><span className="min-w-0"><span className="block truncate font-medium text-slate-800">{task.nombre}</span><span className="mt-1 block text-sm text-slate-500">{formatTaskDate(task.fecha_limite)}</span></span><span className={`shrink-0 rounded-full border px-2.5 py-1 text-xs font-medium ${priorityStyles[task.prioridad]}`}>{priorityLabel[task.prioridad]}</span></Link>)}</div>}
        </section>
      </section>
    </main>
  )
}
