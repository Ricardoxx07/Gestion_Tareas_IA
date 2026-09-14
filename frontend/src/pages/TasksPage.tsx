import { CalendarDays, Check, ChevronRight, ListPlus, Pencil, Plus, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ConfirmDialog } from '../components/common/ConfirmDialog'
import { TaskForm } from '../components/tareas/TaskForm'
import { useActualizarTarea, useCrearTarea, useEliminarTarea, useTareas } from '../hooks/useTareas'
import { useToast } from '../hooks/useToast'
import type { Tarea, TareaRequest } from '../types/tarea'
import { getApiErrorMessage } from '../utils/api-error'
import { formatTaskDate, priorityLabel, priorityStyles } from '../utils/tarea'

export function TasksPage() {
  const [isCreateOpen, setCreateOpen] = useState(false)
  const [taskToEdit, setTaskToEdit] = useState<Tarea | null>(null)
  const [taskToDelete, setTaskToDelete] = useState<Tarea | null>(null)
  const { showToast } = useToast()
  const { data: allTasks = [], isError, isPending, error, refetch } = useTareas()
  const createMutation = useCrearTarea()
  const updateMutation = useActualizarTarea()
  const deleteMutation = useEliminarTarea()
  const tasks = allTasks.filter((task) => task.tarea_padre_id === null)
  const childCount = allTasks.reduce<Record<number, number>>((counts, task) => {
    if (task.tarea_padre_id !== null) counts[task.tarea_padre_id] = (counts[task.tarea_padre_id] ?? 0) + 1
    return counts
  }, {})

  const closeCreate = () => {
    if (!createMutation.isPending) setCreateOpen(false)
  }
  const closeEdit = () => {
    if (!updateMutation.isPending) setTaskToEdit(null)
  }
  const handleCreate = (values: TareaRequest) => createMutation.mutate(values, {
    onSuccess: () => {
      setCreateOpen(false)
      showToast('Tarea creada correctamente.')
    },
    onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
  })
  const handleEdit = (values: TareaRequest) => {
    if (!taskToEdit) return
    updateMutation.mutate({ id: taskToEdit.id, cambios: values }, {
      onSuccess: () => {
        setTaskToEdit(null)
        showToast('Cambios guardados correctamente.')
      },
      onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
    })
  }
  const toggleTask = (task: Tarea) => updateMutation.mutate(
    { id: task.id, cambios: { completada: !task.completada } },
    {
      onSuccess: () => showToast(task.completada ? 'Tarea marcada como pendiente.' : 'Tarea completada.'),
      onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
    },
  )
  const confirmDelete = () => {
    if (!taskToDelete) return
    deleteMutation.mutate(taskToDelete.id, {
      onSuccess: () => {
        setTaskToDelete(null)
        showToast('Tarea eliminada correctamente.')
      },
      onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
    })
  }

  return (
    <main className="p-5 sm:p-8">
      <section className="mx-auto max-w-6xl">
        <header className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
          <div><p className="text-sm font-medium text-cyan-700">Organización</p><h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">Tus tareas</h1><p className="mt-2 text-slate-600">Crea, prioriza y completa el trabajo que tienes por delante.</p></div>
          <button type="button" onClick={() => { createMutation.reset(); setCreateOpen(true) }} className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-700"><Plus aria-hidden="true" size={18} />Nueva tarea</button>
        </header>

        {isError ? <section className="mt-8 rounded-xl border border-red-200 bg-red-50 p-6"><h2 className="font-semibold text-red-900">No se pudieron cargar las tareas</h2><p className="mt-1 text-sm text-red-700">{getApiErrorMessage(error)}</p><button type="button" onClick={() => void refetch()} className="mt-4 rounded-lg border border-red-300 px-3 py-2 text-sm font-medium text-red-800 hover:bg-white">Reintentar</button></section> : <section className="mt-8 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
          {isPending ? <div className="divide-y divide-slate-100" aria-label="Cargando tareas" aria-busy="true">{Array.from({ length: 4 }).map((_, index) => <div key={index} className="h-24 animate-pulse bg-slate-50" />)}</div> : tasks.length === 0 ? <div className="px-6 py-16 text-center"><span className="mx-auto flex size-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600"><ListPlus aria-hidden="true" size={24} /></span><h2 className="mt-4 text-lg font-semibold text-slate-900">Tu lista está vacía</h2><p className="mx-auto mt-2 max-w-sm text-sm leading-6 text-slate-600">Añade una tarea para empezar a organizar tu trabajo.</p><button type="button" onClick={() => { createMutation.reset(); setCreateOpen(true) }} className="mt-5 inline-flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-700"><Plus aria-hidden="true" size={16} />Crear tarea</button></div> : <div className="divide-y divide-slate-100">{tasks.map((task) => <article key={task.id} className="flex gap-3 px-4 py-4 sm:items-center sm:px-6"><button type="button" onClick={() => toggleTask(task)} disabled={updateMutation.isPending} className={`mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full border transition sm:mt-0 ${task.completada ? 'border-emerald-600 bg-emerald-600 text-white' : 'border-slate-300 text-transparent hover:border-indigo-500'} disabled:opacity-60`} aria-label={task.completada ? `Marcar ${task.nombre} como pendiente` : `Marcar ${task.nombre} como completada`}><Check aria-hidden="true" size={15} /></button><Link to={`/tareas/${task.id}`} className="min-w-0 flex-1"><h2 className={`truncate font-medium ${task.completada ? 'text-slate-400 line-through' : 'text-slate-900'}`}>{task.nombre}</h2><div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500"><span className="inline-flex items-center gap-1"><CalendarDays aria-hidden="true" size={14} />{formatTaskDate(task.fecha_limite)}</span>{childCount[task.id] && <span className="rounded-full bg-slate-100 px-2 py-0.5">{childCount[task.id]} subtarea{childCount[task.id] === 1 ? '' : 's'}</span>}</div></Link><span className={`hidden rounded-full border px-2.5 py-1 text-xs font-medium sm:inline ${priorityStyles[task.prioridad]}`}>{priorityLabel[task.prioridad]}</span><div className="flex shrink-0 items-center"><button type="button" onClick={() => { updateMutation.reset(); setTaskToEdit(task) }} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800" aria-label={`Editar ${task.nombre}`}><Pencil aria-hidden="true" size={16} /></button><button type="button" onClick={() => { deleteMutation.reset(); setTaskToDelete(task) }} disabled={deleteMutation.isPending} className="rounded-lg p-2 text-slate-500 hover:bg-red-50 hover:text-red-700 disabled:opacity-60" aria-label={`Eliminar ${task.nombre}`}><Trash2 aria-hidden="true" size={16} /></button><Link to={`/tareas/${task.id}`} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800" aria-label={`Ver ${task.nombre}`}><ChevronRight aria-hidden="true" size={18} /></Link></div></article>)}</div>}
        </section>}
        {deleteMutation.isError && <p className="mt-4 text-sm text-red-700" role="alert">{getApiErrorMessage(deleteMutation.error)}</p>}
      </section>
      {isCreateOpen && <TaskForm title="Nueva tarea" submitLabel="Crear tarea" isPending={createMutation.isPending} error={createMutation.error} onClose={closeCreate} onSubmit={handleCreate} />}
      {taskToEdit && <TaskForm title="Editar tarea" submitLabel="Guardar cambios" task={taskToEdit} isPending={updateMutation.isPending} error={updateMutation.error} onClose={closeEdit} onSubmit={handleEdit} />}
      {taskToDelete && (
        <ConfirmDialog
          title="Eliminar tarea"
          description={`Vas a eliminar “${taskToDelete.nombre}”. Esta acción no se puede deshacer y también puede afectar a sus subtareas.`}
          isPending={deleteMutation.isPending}
          onCancel={() => !deleteMutation.isPending && setTaskToDelete(null)}
          onConfirm={confirmDelete}
        />
      )}
    </main>
  )
}
