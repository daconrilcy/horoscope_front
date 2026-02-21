import { useMutation, useQuery } from "@tanstack/react-query"

import { API_BASE_URL } from "./client"

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, string>
    request_id?: string
  }
}

type ResponseEnvelope<TData> = {
  data: TData
}

export type EnterpriseCredentialMetadata = {
  credential_id: number
  key_prefix: string
  status: string
  created_at: string
  revoked_at: string | null
}

export type EnterpriseCredentialsList = {
  account_id: number
  company_name: string
  status: string
  has_active_credential: boolean
  credentials: EnterpriseCredentialMetadata[]
}

export type EnterpriseCredentialSecret = {
  credential_id: number
  key_prefix: string
  api_key: string
  status: string
  created_at: string
}

export class EnterpriseCredentialsApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: Record<string, string>
  readonly requestId: string | null

  constructor(
    code: string,
    message: string,
    status: number,
    details: Record<string, string> = {},
    requestId: string | null = null,
  ) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
    this.requestId = requestId
  }
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem("access_token")
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function parseError(response: Response): Promise<never> {
  let payload: ErrorEnvelope | null = null
  try {
    payload = (await response.json()) as ErrorEnvelope
  } catch {
    payload = null
  }
  throw new EnterpriseCredentialsApiError(
    payload?.error?.code ?? "unknown_error",
    payload?.error?.message ?? `Request failed with status ${response.status}`,
    response.status,
    payload?.error?.details ?? {},
    payload?.error?.request_id ?? null,
  )
}

async function listEnterpriseCredentials(): Promise<EnterpriseCredentialsList> {
  const response = await fetch(`${API_BASE_URL}/v1/b2b/credentials`, {
    method: "GET",
    headers: getAuthHeaders(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ResponseEnvelope<EnterpriseCredentialsList>
  return body.data
}

async function generateCredential(): Promise<EnterpriseCredentialSecret> {
  const response = await fetch(`${API_BASE_URL}/v1/b2b/credentials/generate`, {
    method: "POST",
    headers: getAuthHeaders(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ResponseEnvelope<EnterpriseCredentialSecret>
  return body.data
}

async function rotateCredential(): Promise<EnterpriseCredentialSecret> {
  const response = await fetch(`${API_BASE_URL}/v1/b2b/credentials/rotate`, {
    method: "POST",
    headers: getAuthHeaders(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ResponseEnvelope<EnterpriseCredentialSecret>
  return body.data
}

export function useEnterpriseCredentials(enabled = true) {
  return useQuery({
    queryKey: ["enterprise-credentials"],
    queryFn: listEnterpriseCredentials,
    enabled,
  })
}

export function useGenerateEnterpriseCredential() {
  return useMutation({
    mutationFn: generateCredential,
  })
}

export function useRotateEnterpriseCredential() {
  return useMutation({
    mutationFn: rotateCredential,
  })
}
