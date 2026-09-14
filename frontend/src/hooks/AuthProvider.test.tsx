import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { iniciarSesion, obtenerMiUsuario } from '../api/auth.api'
import { getSessionToken } from '../api/client'
import { AuthProvider } from './AuthProvider'
import { useAuth } from './useAuth'

vi.mock('../api/auth.api', () => ({
  iniciarSesion: vi.fn(),
  obtenerMiUsuario: vi.fn(),
}))

function SessionProbe() {
  const { hasSession, login, logout, user } = useAuth()
  return (
    <div>
      <p>{hasSession ? 'Con sesión' : 'Sin sesión'}</p>
      {user && <p>{user.email}</p>}
      <button type="button" onClick={() => void login({ email: 'ana@example.com', password: 'segura123' })}>Acceder</button>
      <button type="button" onClick={logout}>Salir</button>
    </div>
  )
}

function renderProvider() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <MemoryRouter>
      <QueryClientProvider client={queryClient}>
        <AuthProvider><SessionProbe /></AuthProvider>
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

describe('AuthProvider', () => {
  beforeEach(() => vi.clearAllMocks())

  it('guarda el token solo en sessionStorage y limpia la sesión al salir', async () => {
    vi.mocked(iniciarSesion).mockResolvedValue({ access_token: 'token-de-prueba', token_type: 'bearer' })
    vi.mocked(obtenerMiUsuario).mockResolvedValue({ id: 1, email: 'ana@example.com' })
    const user = userEvent.setup()
    renderProvider()

    await user.click(screen.getByRole('button', { name: 'Acceder' }))
    expect(await screen.findByText('ana@example.com')).toBeInTheDocument()
    expect(getSessionToken()).toBe('token-de-prueba')
    expect(localStorage.length).toBe(0)

    await user.click(screen.getByRole('button', { name: 'Salir' }))
    expect(screen.getByText('Sin sesión')).toBeInTheDocument()
    expect(getSessionToken()).toBeNull()
  })
})
