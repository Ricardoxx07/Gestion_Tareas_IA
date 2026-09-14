import { apiClient } from './client'

export interface ApiStatus {
  mensaje: string
}

export async function getApiStatus(): Promise<ApiStatus> {
  const { data } = await apiClient.get<ApiStatus>('/')
  return data
}
