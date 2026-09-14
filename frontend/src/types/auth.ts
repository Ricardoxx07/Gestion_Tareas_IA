export interface Usuario {
  id: number
  email: string
}

export interface Credenciales {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}
