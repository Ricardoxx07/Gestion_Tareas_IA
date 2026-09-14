import { ArrowLeft, CalendarDays, Check, CirclePlus, ClipboardList, LoaderCircle, Pencil, Plus, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'
import { ConfirmDialog } from '../components/common/ConfirmDialog'
import { TaskForm } from '../components/tareas/TaskForm'
import { TaskDecompositionPanel } from '../components/ia/TaskDecompositionPanel'
import { useActualizarSubtarea, useActualizarTarea, useCrearSubtarea, useEliminarSubtarea, useEliminarTarea, useSubtareas, useTarea } from '../hooks/useTareas'
import { useToast } from '../hooks/useToast'
import type { Tarea, TareaRequest } from '../types/tarea'
import { getApiErrorMessage } from '../utils/api-error'
import { formatTaskDate, priorityLabel, priorityStyles } from '../utils/tarea'

export function TaskDetailPage() {
  const { tareaId } = useParams()
  const taskId = tareaId && /^\d+$/.test(tareaId) ? Number(tareaId) : null
  const navigate = useNavigate()
  const [isSubtaskFormOpen, setSubtaskFormOpen] = useState(false)
  const [subtaskToEdit, setSubtaskToEdit] = useState<Tarea | null>(null)
  const [isTaskFormOpen, setTaskFormOpen] = useState(false)
  const [taskToDelete, setTaskToDelete] = useState<Tarea | null>(null)
  const { showToast } = useToast()
  const taskQuery = useTarea(taskId)
  const subtaskQuery = useSubtareas(taskId)
  const updateTask = useActualizarTarea()
  const deleteTask = useEliminarTarea()
  const createSubtask = useCrearSubtarea()
  const updateSubtask = useActualizarSubtarea()
  const deleteSubtask = useEliminarSubtarea()

  if (taskId === null) return <Navigate to="/tareas" replace />
  if (taskQuery.isPending) return <main className="grid min-h-[60vh] place-items-center"><div className="flex items-center gap-3 text-slate-600"><LoaderCircle className="animate-spin text-indigo-600" aria-hidden="true" size={20} />Cargando tarea…</div></main>
  if (taskQuery.isError || !taskQuery.data) return <main className="p-5 sm:p-8"><section className="mx-auto max-w-3xl rounded-xl border border-red-200 bg-red-50 p-6"><h1 className="font-semibold text-red-900">No pudimos abrir esta tarea</h1><p className="mt-1 text-sm text-red-700">{getApiErrorMessage(taskQuery.error)}</p><Link to="/tareas" className="mt-4 inline-block text-sm font-medium text-red-800 underline">Volver a tareas</Link></section></main>

  const task = taskQuery.data
  const subtasks = subtaskQuery.data ?? []
  const completedSubtasks = subtasks.filter((subtask) => subtask.completada).length
  const updateParent = (values: TareaRequest) => updateTask.mutate({ id: task.id, cambios: values }, {
    onSuccess: () => {
      setTaskFormOpen(false)
      showToast('Cambios guardados correctamente.')
    },
    onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
  })
  const toggleSubtask = (subtask: Tarea) => updateSubtask.mutate(
    { tareaId: task.id, subtareaId: subtask.id, cambios: { completada: !subtask.completada } },
    {
      onSuccess: () => showToast(subtask.completada ? 'Subtarea marcada como pendiente.' : 'Subtarea completada.'),
      onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
    },
  )
  const editSubtask = (values: TareaRequest) => {
    if (!subtaskToEdit) return
    updateSubtask.mutate({ tareaId: task.id, subtareaId: subtaskToEdit.id, cambios: values }, {
      onSuccess: () => {
        setSubtaskToEdit(null)
        showToast('Subtarea actualizada correctamente.')
      },
      onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
    })
  }
  const confirmDelete = () => {
    if (!taskToDelete) return

    if (taskToDelete.id === task.id) {
      deleteTask.mutate(task.id, {
        onSuccess: () => {
          setTaskToDelete(null)
          showToast('Tarea eliminada correctamente.')
          navigate('/tareas', { replace: true })
        },
        onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
      })
      return
    }

    deleteSubtask.mutate(
      { tareaId: task.id, subtareaId: taskToDelete.id },
      {
        onSuccess: () => {
          setTaskToDelete(null)
          showToast('Subtarea eliminada correctamente.')
        },
        onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error'),
      },
    )
  }

  return (
    <main className="p-5 sm:p-8">
      <section className="mx-auto max-w-4xl">
        <Link to="/tareas" className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-indigo-700"><ArrowLeft aria-hidden="true" size={16} />Volver a tareas</Link>
        <article className="mt-5 rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-7">
          <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-start"><div className="min-w-0"><div className="flex flex-wrap items-center gap-2"><span className={`rounded-full border px-2.5 py-1 text-xs font-medium ${priorityStyles[task.prioridad]}`}>{priorityLabel[task.prioridad]}</span><span className={`rounded-full px-2.5 py-1 text-xs font-medium ${task.completada ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>{task.completada ? 'Completada' : 'Pendiente'}</span></div><h1 className={`mt-4 break-words text-2xl font-semibold tracking-tight sm:text-3xl ${task.completada ? 'text-slate-400 line-through' : 'text-slate-900'}`}>{task.nombre}</h1><p className="mt-3 flex items-center gap-2 text-sm text-slate-600"><CalendarDays aria-hidden="true" size={17} />{formatTaskDate(task.fecha_limite)}</p></div><div className="flex gap-2"><button type="button" onClick={() => { updateTask.reset(); setTaskFormOpen(true) }} className="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"><Pencil aria-hidden="true" size={16} />Editar</button><button type="button" onClick={() => { deleteTask.reset(); setTaskToDelete(task) }} disabled={deleteTask.isPending} className="rounded-lg border border-red-200 p-2 text-red-700 hover:bg-red-50 disabled:opacity-60" aria-label="Eliminar tarea"><Trash2 aria-hidden="true" size={18} /></button></div></div>
          <div className="mt-7 border-t border-slate-100 pt-5"><button type="button" onClick={() => updateTask.mutate({ id: task.id, cambios: { completada: !task.completada } }, { onSuccess: () => showToast(task.completada ? 'Tarea marcada como pendiente.' : 'Tarea completada.'), onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error') })} disabled={updateTask.isPending} className={`inline-flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium disabled:opacity-60 ${task.completada ? 'border border-slate-300 text-slate-700 hover:bg-slate-50' : 'bg-emerald-600 text-white hover:bg-emerald-700'}`}><Check aria-hidden="true" size={17} />{task.completada ? 'Marcar como pendiente' : 'Marcar como completada'}</button>{(updateTask.isError || deleteTask.isError) && <p className="mt-3 text-sm text-red-700" role="alert">{getApiErrorMessage(updateTask.error ?? deleteTask.error)}</p>}</div>
        </article>

        <section className="mt-8 rounded-xl border border-slate-200 bg-white shadow-sm"><div className="flex flex-col justify-between gap-4 border-b border-slate-200 p-5 sm:flex-row sm:items-center sm:px-6"><div><div className="flex items-center gap-2"><ClipboardList className="text-cyan-600" aria-hidden="true" size={20} /><h2 className="text-lg font-semibold text-slate-900">Subtareas guardadas</h2></div><p className="mt-1 text-sm text-slate-500">{subtasks.length ? `${completedSubtasks} de ${subtasks.length} completadas` : 'Divide esta tarea en pasos concretos.'}</p></div><button type="button" onClick={() => { createSubtask.reset(); setSubtaskFormOpen(true) }} className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-3.5 py-2 text-sm font-medium text-white hover:bg-indigo-700"><Plus aria-hidden="true" size={16} />Añadir subtarea</button></div>
          {subtaskQuery.isPending ? <div className="divide-y divide-slate-100" aria-label="Cargando subtareas" aria-busy="true">{Array.from({ length: 2 }).map((_, index) => <div key={index} className="h-20 animate-pulse bg-slate-50" />)}</div> : subtaskQuery.isError ? <div className="p-6"><p className="text-sm text-red-700" role="alert">{getApiErrorMessage(subtaskQuery.error)}</p><button type="button" onClick={() => void subtaskQuery.refetch()} className="mt-3 text-sm font-medium text-red-800 underline">Reintentar</button></div> : subtasks.length === 0 ? <div className="px-6 py-12 text-center"><CirclePlus className="mx-auto text-slate-400" aria-hidden="true" size={30} /><p className="mt-3 font-medium text-slate-900">Aún no hay subtareas</p><p className="mt-1 text-sm text-slate-600">Convierte esta tarea en pasos pequeños y fáciles de seguir.</p></div> : <div className="divide-y divide-slate-100">{subtasks.map((subtask) => <article key={subtask.id} className="flex gap-3 px-5 py-4 sm:items-center sm:px-6"><button type="button" onClick={() => toggleSubtask(subtask)} disabled={updateSubtask.isPending} className={`mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full border transition sm:mt-0 ${subtask.completada ? 'border-emerald-600 bg-emerald-600 text-white' : 'border-slate-300 text-transparent hover:border-indigo-500'} disabled:opacity-60`} aria-label={subtask.completada ? `Marcar ${subtask.nombre} como pendiente` : `Marcar ${subtask.nombre} como completada`}><Check aria-hidden="true" size={15} /></button><div className="min-w-0 flex-1"><h3 className={`truncate font-medium ${subtask.completada ? 'text-slate-400 line-through' : 'text-slate-900'}`}>{subtask.nombre}</h3><div className="mt-2 flex flex-wrap gap-2"><span className="inline-flex items-center gap-1 text-xs text-slate-500"><CalendarDays aria-hidden="true" size={14} />{formatTaskDate(subtask.fecha_limite)}</span><span className={`rounded-full border px-2 py-0.5 text-xs font-medium ${priorityStyles[subtask.prioridad]}`}>{priorityLabel[subtask.prioridad]}</span></div></div><div className="flex shrink-0"><button type="button" onClick={() => { updateSubtask.reset(); setSubtaskToEdit(subtask) }} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-800" aria-label={`Editar ${subtask.nombre}`}><Pencil aria-hidden="true" size={16} /></button><button type="button" onClick={() => { deleteSubtask.reset(); setTaskToDelete(subtask) }} disabled={deleteSubtask.isPending} className="rounded-lg p-2 text-slate-500 hover:bg-red-50 hover:text-red-700 disabled:opacity-60" aria-label={`Eliminar ${subtask.nombre}`}><Trash2 aria-hidden="true" size={16} /></button></div></article>)}</div>}
          {(createSubtask.isError || updateSubtask.isError || deleteSubtask.isError) && <p className="border-t border-red-100 bg-red-50 px-5 py-3 text-sm text-red-700" role="alert">{getApiErrorMessage(createSubtask.error ?? updateSubtask.error ?? deleteSubtask.error)}</p>}
          <div className="border-t border-slate-200 px-5 py-5 sm:px-6"><TaskDecompositionPanel tareaId={task.id} tareaNombre={task.nombre} /></div>
        </section>
      </section>
      {isTaskFormOpen && <TaskForm title="Editar tarea" submitLabel="Guardar cambios" task={task} isPending={updateTask.isPending} error={updateTask.error} onClose={() => !updateTask.isPending && setTaskFormOpen(false)} onSubmit={updateParent} />}
      {isSubtaskFormOpen && <TaskForm title="Nueva subtarea" submitLabel="Crear subtarea" isPending={createSubtask.isPending} error={createSubtask.error} onClose={() => !createSubtask.isPending && setSubtaskFormOpen(false)} onSubmit={(values) => createSubtask.mutate({ tareaId: task.id, datos: values }, { onSuccess: () => { setSubtaskFormOpen(false); showToast('Subtarea creada correctamente.') }, onError: (mutationError) => showToast(getApiErrorMessage(mutationError), 'error') })} />}
      {subtaskToEdit && <TaskForm title="Editar subtarea" submitLabel="Guardar cambios" task={subtaskToEdit} isPending={updateSubtask.isPending} error={updateSubtask.error} onClose={() => !updateSubtask.isPending && setSubtaskToEdit(null)} onSubmit={editSubtask} />}
      {taskToDelete && (
        <ConfirmDialog
          title={taskToDelete.id === task.id ? 'Eliminar tarea' : 'Eliminar subtarea'}
          description={`Vas a eliminar “${taskToDelete.nombre}”. Esta acción no se puede deshacer${taskToDelete.id === task.id ? ' y también puede afectar a sus subtareas.' : '.'}`}
          isPending={deleteTask.isPending || deleteSubtask.isPending}
          onCancel={() => !(deleteTask.isPending || deleteSubtask.isPending) && setTaskToDelete(null)}
          onConfirm={confirmDelete}
        />
      )}
    </main>
  )
}
