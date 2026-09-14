import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { AuthContext, type AuthContextValue } from '../hooks/auth-context'
import { LoginPage } from './LoginPage'

const authValue: AuthContextValue = {
  user: undefined,
  hasSession: false,
  isAuthenticated: false,
  isLoading: false,
  hasSessionError: false,
  login: vi.fn().mockResolvedValue({ id: 1, email: 'ana@example.com' }),
  logout: vi.fn(),
  retrySession: vi.fn(),
}

describe('LoginPage', () => {
  it('valida el formulario y envía credenciales válidas', async () => {
    const queryClient = new QueryClient()
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <QueryClientProvider client={queryClient}>
          <AuthContext.Provider value={authValue}><LoginPage /></AuthContext.Provider>
        </QueryClientProvider>
      </MemoryRouter>,
    )

    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))
    expect(await screen.findByText('Ingresa un email válido.')).toBeInTheDocument()
    expect(authValue.login).not.toHaveBeenCalled()

    await user.type(screen.getByLabelText('Email'), 'ana@example.com')
    await user.type(screen.getByLabelText('Contraseña'), 'segura123')
    await user.click(screen.getByRole('button', { name: 'Iniciar sesión' }))

    expect(authValue.login).toHaveBeenCalledWith(
      { email: 'ana@example.com', password: 'segura123' },
      expect.any(Object),
    )
  })
})
