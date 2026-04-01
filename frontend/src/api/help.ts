import { useMutation, useQuery } from "@tanstack/react-query"
import { API_BASE_URL } from "./client"
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
  status: string
  created_at: string
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
  readonly details: Record<string, any>

  constructor(code: string, message: string, status: number, details: Record<string, any> = {}) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
  }
}

async function parseError(response: Response): Promise<never> {
  let payload: any = null
  try {
    payload = await response.json()
  } catch {
    payload = null
  }
  throw new HelpApiError(
    payload?.error?.code ?? "unknown_error",
    payload?.error?.message ?? `Request failed with status ${response.status}`,
    response.status,
    payload?.error?.details ?? {},
  )
}

export async function getHelpCategories(lang: string = "fr"): Promise<HelpCategory[]> {
  const response = await fetch(`${API_BASE_URL}/v1/help/categories?lang=${lang}`, {
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
  const response = await fetch(`${API_BASE_URL}/v1/help/tickets`, {
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
  const response = await fetch(`${API_BASE_URL}/v1/help/tickets?limit=${limit}&offset=${offset}`, {
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
