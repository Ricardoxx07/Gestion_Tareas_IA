import { apiClient } from './client'
import type { Credenciales, TokenResponse, Usuario } from '../types/auth'

export async function registrarUsuario(datos: Credenciales): Promise<Usuario> {
  const { data } = await apiClient.post<Usuario>('/auth/registro', datos)
  return data
}

export async function iniciarSesion(datos: Credenciales): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', datos)
  return data
}

export async function obtenerMiUsuario(): Promise<Usuario> {
  const { data } = await apiClient.get<Usuario>('/auth/me')
  return data
}
