import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { confirmarPropuestas, planificarTexto } from '../api/ia.api'
import { ToastProvider } from '../components/common/ToastProvider'
import { PlannerPage } from './PlannerPage'

vi.mock('../api/ia.api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../api/ia.api')>()
  return {
    ...actual,
    planificarTexto: vi.fn(),
    confirmarPropuestas: vi.fn(),
  }
})

function renderPlanner() {
  const queryClient = new QueryClient({ defaultOptions: { mutations: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider><PlannerPage /></ToastProvider>
    </QueryClientProvider>,
  )
}

describe('PlannerPage', () => {
  beforeEach(() => vi.clearAllMocks())

  it('separa la propuesta de IA de la confirmación persistente', async () => {
    vi.mocked(planificarTexto).mockResolvedValue({
      tareas_propuestas: [{
        nombre: 'Preparar presentación',
        fecha_sugerida: '2026-09-14',
        prioridad_sugerida: 'alta',
        motivo: 'Tiene una fecha cercana.',
      }],
    })
    vi.mocked(confirmarPropuestas).mockResolvedValue({
      tareas_confirmadas: [{
        id: 12,
        nombre: 'Preparar presentación',
        completada: false,
        fecha_limite: '2026-09-14',
        prioridad: 'alta',
        created_at: '2026-09-12T10:00:00',
        tarea_padre_id: null,
      }],
    })
    const user = userEvent.setup()
    renderPlanner()

    await user.type(screen.getByLabelText('¿Qué necesitas organizar?'), 'Preparar la presentación del lunes')
    await user.click(screen.getByRole('button', { name: 'Generar propuestas' }))

    expect(await screen.findByText('Preparar presentación')).toBeInTheDocument()
    expect(screen.getByText(/aún no han sido guardadas/i)).toBeInTheDocument()
    expect(confirmarPropuestas).not.toHaveBeenCalled()

    await user.click(screen.getByRole('button', { name: 'Confirmar seleccionadas' }))
    expect(confirmarPropuestas).toHaveBeenCalledWith([{
      nombre: 'Preparar presentación',
      fecha_limite: '2026-09-14',
      prioridad: 'alta',
    }], expect.any(Object))
    expect(await screen.findByText('1 tarea guardada correctamente.')).toBeInTheDocument()
  })

  it('muestra un estado vacío cuando la IA no devuelve propuestas', async () => {
    vi.mocked(planificarTexto).mockResolvedValue({ tareas_propuestas: [] })
    const user = userEvent.setup()
    renderPlanner()

    await user.type(screen.getByLabelText('¿Qué necesitas organizar?'), 'Revisar pendientes')
    await user.click(screen.getByRole('button', { name: 'Generar propuestas' }))
    expect(await screen.findByText('No se generaron propuestas')).toBeInTheDocument()
  })
})
