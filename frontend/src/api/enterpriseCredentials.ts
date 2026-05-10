import { useMutation, useQuery } from "@tanstack/react-query"

import { apiFetch, type ApiResponseEnvelope, parseApiErrorDetails } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

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

async function parseError(response: Response): Promise<never> {
  const error = await parseApiErrorDetails<Record<string, string>>(response, {})
  throw new EnterpriseCredentialsApiError(
    error.code,
    error.message,
    response.status,
    error.details,
    error.requestId,
  )
}

async function listEnterpriseCredentials(): Promise<EnterpriseCredentialsList> {
  const response = await apiFetch("/v1/b2b/credentials", {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ApiResponseEnvelope<EnterpriseCredentialsList>
  return body.data
}

async function generateCredential(): Promise<EnterpriseCredentialSecret> {
  const response = await apiFetch("/v1/b2b/credentials/generate", {
    method: "POST",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ApiResponseEnvelope<EnterpriseCredentialSecret>
  return body.data
}

async function rotateCredential(): Promise<EnterpriseCredentialSecret> {
  const response = await apiFetch("/v1/b2b/credentials/rotate", {
    method: "POST",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = (await response.json()) as ApiResponseEnvelope<EnterpriseCredentialSecret>
  return body.data
}

export function useB2BCredentials(enabled = true) {
  return useQuery({
    queryKey: ["enterprise-credentials"],
    queryFn: listEnterpriseCredentials,
    enabled,
  })
}

export function useGenerateB2BCredential() {
  return useMutation({
    mutationFn: generateCredential,
  })
}

export function useRotateB2BCredential() {
  return useMutation({
    mutationFn: rotateCredential,
  })
}
