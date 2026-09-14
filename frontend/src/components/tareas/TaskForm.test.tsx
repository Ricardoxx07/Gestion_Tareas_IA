import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { TaskForm } from './TaskForm'

describe('TaskForm', () => {
  it('muestra validación accesible y normaliza una fecha vacía antes de guardar', async () => {
    const onSubmit = vi.fn()
    const user = userEvent.setup()
    render(
      <TaskForm
        title="Nueva tarea"
        submitLabel="Crear tarea"
        isPending={false}
        onClose={vi.fn()}
        onSubmit={onSubmit}
      />,
    )

    await user.click(screen.getByRole('button', { name: 'Crear tarea' }))
    expect(await screen.findByText('Ingresa un nombre para la tarea.')).toHaveAttribute('role', 'alert')
    expect(screen.getByLabelText('Nombre')).toHaveAttribute('aria-invalid', 'true')
    expect(onSubmit).not.toHaveBeenCalled()

    await user.type(screen.getByLabelText('Nombre'), 'Preparar informe')
    await user.selectOptions(screen.getByLabelText('Prioridad'), 'alta')
    await user.click(screen.getByRole('button', { name: 'Crear tarea' }))

    expect(onSubmit).toHaveBeenCalledWith({
      nombre: 'Preparar informe',
      fecha_limite: null,
      prioridad: 'alta',
    })
  })

  it('deshabilita las acciones mientras se envía', () => {
    render(
      <TaskForm
        title="Editar tarea"
        submitLabel="Guardar cambios"
        isPending
        onClose={vi.fn()}
        onSubmit={vi.fn()}
      />,
    )

    expect(screen.getByRole('button', { name: 'Guardar cambios' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Cancelar' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Cerrar formulario' })).toBeDisabled()
  })
})
