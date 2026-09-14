import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ConfirmDialog } from './ConfirmDialog'

describe('ConfirmDialog', () => {
  it('requiere una acción explícita antes de ejecutar una eliminación', async () => {
    const onCancel = vi.fn()
    const onConfirm = vi.fn()
    const user = userEvent.setup()
    render(
      <ConfirmDialog
        title="Eliminar tarea"
        description="Esta acción no se puede deshacer."
        onCancel={onCancel}
        onConfirm={onConfirm}
      />,
    )

    expect(onConfirm).not.toHaveBeenCalled()
    expect(await screen.findByRole('button', { name: 'Cancelar' })).toHaveFocus()
    await user.click(screen.getByRole('button', { name: 'Eliminar' }))
    expect(onConfirm).toHaveBeenCalledOnce()
  })

  it('permite cancelar con Escape', async () => {
    const onCancel = vi.fn()
    const user = userEvent.setup()
    render(
      <ConfirmDialog
        title="Eliminar tarea"
        description="Esta acción no se puede deshacer."
        onCancel={onCancel}
        onConfirm={vi.fn()}
      />,
    )

    await user.keyboard('{Escape}')
    expect(onCancel).toHaveBeenCalledOnce()
  })
})
