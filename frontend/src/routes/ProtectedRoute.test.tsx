import { fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useAuth } from '../hooks/useAuth'
import type { AuthContextValue } from '../hooks/auth-context'
import { ProtectedRoute } from './ProtectedRoute'

vi.mock('../hooks/useAuth', () => ({ useAuth: vi.fn() }))

const defaultAuth: AuthContextValue = {
  user: undefined,
  hasSession: false,
  isAuthenticated: false,
  isLoading: false,
  hasSessionError: false,
  login: vi.fn(),
  logout: vi.fn(),
  retrySession: vi.fn(),
}

function renderRoute(auth: Partial<AuthContextValue>) {
  vi.mocked(useAuth).mockReturnValue({ ...defaultAuth, ...auth })
  return render(
    <MemoryRouter initialEntries={['/privado']}>
      <Routes>
        <Route path="/login" element={<p>Página de acceso</p>} />
        <Route element={<ProtectedRoute />}>
          <Route path="/privado" element={<p>Contenido privado</p>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  )
}

describe('ProtectedRoute', () => {
  beforeEach(() => vi.clearAllMocks())

  it('redirige al login cuando no existe una sesión', () => {
    renderRoute({ hasSession: false })
    expect(screen.getByText('Página de acceso')).toBeInTheDocument()
  })

  it('muestra el estado de restauración mientras valida el token', () => {
    renderRoute({ hasSession: true, isLoading: true })
    expect(screen.getByText('Restaurando tu sesión…')).toBeInTheDocument()
  })

  it('permite reintentar un error recuperable de sesión', () => {
    const retrySession = vi.fn()
    renderRoute({ hasSession: true, hasSessionError: true, retrySession })
    fireEvent.click(screen.getByRole('button', { name: 'Reintentar' }))
    expect(retrySession).toHaveBeenCalledOnce()
  })

  it('renderiza la ruta privada para un usuario autenticado', () => {
    renderRoute({
      user: { id: 1, email: 'ana@example.com' },
      hasSession: true,
      isAuthenticated: true,
    })
    expect(screen.getByText('Contenido privado')).toBeInTheDocument()
  })
})
