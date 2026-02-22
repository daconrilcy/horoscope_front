import { API_BASE_URL, apiFetch } from "./client"

export type LoginResult = {
  access_token: string
  user: { id: number; role: string }
}

export class AuthApiError extends Error {
  code: string
  constructor(code: string, message: string) {
    super(message)
    this.name = "AuthApiError"
    this.code = code
  }
}

async function postAuth(endpoint: string, email: string, password: string): Promise<LoginResult> {
  const response = await apiFetch(`${API_BASE_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  })

  if (!response.ok) {
    try {
      const payload = (await response.json()) as { error: { code: string; message: string } }
      throw new AuthApiError(payload.error.code, payload.error.message)
    } catch (parseError) {
      if (parseError instanceof AuthApiError) throw parseError
      throw new Error(`HTTP ${response.status}`)
    }
  }

  const payload = (await response.json()) as {
    data: { tokens: { access_token: string }; user: { id: number; role: string } }
    meta: { request_id: string }
  }
  return {
    access_token: payload.data.tokens.access_token,
    user: payload.data.user,
  }
}

export function loginApi(email: string, password: string): Promise<LoginResult> {
  return postAuth("/v1/auth/login", email, password)
}

export function registerApi(email: string, password: string): Promise<LoginResult> {
  return postAuth("/v1/auth/register", email, password)
}
