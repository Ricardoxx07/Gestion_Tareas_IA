import axios from 'axios'

export function getApiErrorMessage(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return 'Ocurrió un error inesperado. Intenta nuevamente.'
  }

  if (!error.response) {
    return 'No se pudo conectar con la API. Verifica que FastAPI esté en ejecución e inténtalo nuevamente.'
  }

  const detail = error.response.data?.detail
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  const messages: Record<number, string> = {
    400: 'La solicitud no es válida. Revisa los datos e inténtalo nuevamente.',
    401: 'Tu sesión no es válida o ha expirado.',
    403: 'No tienes permiso para realizar esta operación.',
    404: 'No se encontró el recurso solicitado.',
    409: 'La operación entra en conflicto con el estado actual.',
    422: 'Los datos enviados no son válidos.',
    502: 'La respuesta del proveedor de IA no es válida.',
    503: 'El proveedor de IA no está disponible temporalmente.',
  }

  return messages[error.response.status] ?? 'La API no pudo procesar la solicitud. Intenta nuevamente.'
}
