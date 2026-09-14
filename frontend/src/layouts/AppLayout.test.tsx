import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '../hooks/auth-context'
import { AppLayout } from './AppLayout'

const authValue: AuthContextValue = {
  user: { id: 1, email: 'ana@example.com' },
  hasSession: true,
  isAuthenticated: true,
  isLoading: false,
  hasSessionError: false,
  login: vi.fn(),
  logout: vi.fn(),
  retrySession: vi.fn(),
}

describe('AppLayout', () => {
  it('abre el drawer móvil y permite cerrarlo con Escape', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <AuthContext.Provider value={authValue}>
          <Routes>
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<p>Dashboard</p>} />
            </Route>
          </Routes>
        </AuthContext.Provider>
      </MemoryRouter>,
    )

    await user.click(screen.getByRole('button', { name: 'Abrir navegación' }))
    expect(screen.getByRole('dialog', { name: 'Navegación principal' })).toBeInTheDocument()
    expect(await screen.findByRole('button', { name: 'Cerrar menú' })).toHaveFocus()

    await user.keyboard('{Escape}')
    expect(screen.queryByRole('dialog', { name: 'Navegación principal' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Abrir navegación' })).toHaveFocus()
  })
})
