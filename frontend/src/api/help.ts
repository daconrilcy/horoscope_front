import { useMutation, useQuery } from "@tanstack/react-query"
import { apiFetch, parseApiErrorDetails } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"

export type HelpCategory = {
  code: string
  label: string
  description: string | null
}

export type HelpTicket = {
  ticket_id: number
  category_code: string
  subject: string
  description: string
  support_response: string | null
  status: string
  created_at: string
  updated_at: string
  resolved_at: string | null
}

export type HelpTicketsList = {
  tickets: HelpTicket[]
  total: number
  limit: number
  offset: number
}

export type CreateHelpTicketPayload = {
  category_code: string
  subject: string
  description: string
}

export class HelpApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: Record<string, unknown>
  readonly requestId: string | null

  constructor(
    code: string,
    message: string,
    status: number,
    details: Record<string, unknown> = {},
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
  const error = await parseApiErrorDetails<Record<string, unknown>>(response, {})
  throw new HelpApiError(error.code, error.message, response.status, error.details, error.requestId)
}

export async function getHelpCategories(lang: string = "fr"): Promise<HelpCategory[]> {
  const response = await apiFetch(`/v1/help/categories?lang=${lang}`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = await response.json()
  return body.data.categories
}

export async function createHelpTicket(payload: CreateHelpTicketPayload): Promise<HelpTicket> {
  const response = await apiFetch("/v1/help/tickets", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...getAccessTokenAuthHeader(),
    },
    body: JSON.stringify(payload),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = await response.json()
  return body.data
}

export async function listHelpTickets(limit: number = 20, offset: number = 0): Promise<HelpTicketsList> {
  const response = await apiFetch(`/v1/help/tickets?limit=${limit}&offset=${offset}`, {
    method: "GET",
    headers: getAccessTokenAuthHeader(),
  })
  if (!response.ok) {
    return parseError(response)
  }
  const body = await response.json()
  return body.data
}

export function useHelpCategories(lang: string = "fr") {
  return useQuery({
    queryKey: ["help-categories", lang],
    queryFn: () => getHelpCategories(lang),
  })
}

export function useCreateHelpTicket() {
  return useMutation({
    mutationFn: createHelpTicket,
  })
}

export function useHelpTickets(limit: number = 20, offset: number = 0) {
  return useQuery({
    queryKey: ["help-tickets", limit, offset],
    queryFn: () => listHelpTickets(limit, offset),
  })
}
