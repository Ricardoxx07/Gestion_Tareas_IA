import axios from 'axios'

const apiUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8001'
const SESSION_TOKEN_KEY = 'gestor_tareas_token'

let onUnauthorized: () => void = () => undefined

export function getSessionToken(): string | null {
  return sessionStorage.getItem(SESSION_TOKEN_KEY)
}

export function saveSessionToken(token: string): void {
  sessionStorage.setItem(SESSION_TOKEN_KEY, token)
}

export function clearSessionToken(): void {
  sessionStorage.removeItem(SESSION_TOKEN_KEY)
}

export function registerUnauthorizedHandler(handler: () => void): () => void {
  onUnauthorized = handler

  return () => {
    onUnauthorized = () => undefined
  }
}

export const apiClient = axios.create({
  baseURL: apiUrl,
  headers: {
    Accept: 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const token = getSessionToken()

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      const url = error.config?.url ?? ''
      const isAuthenticationAttempt = url === '/auth/login' || url === '/auth/registro'

      if (!isAuthenticationAttempt && getSessionToken()) {
        clearSessionToken()
        onUnauthorized()
      }
    }

    return Promise.reject(error)
  },
)
