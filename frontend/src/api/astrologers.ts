import { useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "./client"
import { getAccessTokenAuthHeader } from "../utils/authToken"
import type { Astrologer, AstrologerProfile } from "../types/astrologer"

export type { Astrologer, AstrologerProfile }

type ErrorEnvelope = {
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}

const MOCK_ASTROLOGERS: Astrologer[] = [
  {
    id: "c0a80101-8edb-4e1a-8f1a-8f1a8f1a8f1a",
    name: "Guide Psychologique",
    first_name: "Étienne",
    last_name: "Garnier",
    avatar_url: "/assets/astrologers/etienne.png",
    specialties: ["Débutants", "Bases", "Onboarding"],
    style: "Pédagogique",
    bio_short: "Astrologue généraliste pédagogique, spécialisé dans l’accompagnement des débutants.",
  },
]

const MOCK_ASTROLOGER_PROFILES: Record<string, AstrologerProfile> = {
  "c0a80101-8edb-4e1a-8f1a-8f1a8f1a8f1a": {
    ...MOCK_ASTROLOGERS[0],
    bio_full:
      "Ancien professeur de philosophie, Étienne Garnier accompagne les débutants avec une approche simple, claire et progressive.",
    gender: "male",
    age: 55,
    professional_background: [
      "20 ans professeur (philosophie / pédagogie)",
      "12 ans astrologue généraliste",
      "Création de programmes d’initiation à l’astrologie",
    ],
    key_skills: [
      "Vulgarisation astrologique",
      "Explication des bases",
      "Rassurance et pédagogie",
    ],
    behavioral_style: ["Calme", "Posé", "Progressif (step-by-step)"],
  },
}

export class AstrologersApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: Record<string, unknown>

  constructor(code: string, message: string, status: number, details: Record<string, unknown> = {}) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
  }
}

const USE_MOCK_FALLBACK = import.meta.env.DEV
const ASTROLOGERS_LOCAL_CACHE_KEY = "astrologers_last_successful_list"

function loadCachedAstrologers(): Astrologer[] {
  if (typeof window === "undefined") {
    return []
  }
  try {
    const raw = window.localStorage.getItem(ASTROLOGERS_LOCAL_CACHE_KEY)
    if (!raw) {
      return []
    }
    const parsed = JSON.parse(raw) as unknown
    if (!Array.isArray(parsed)) {
      return []
    }
    return parsed.filter(
      (item): item is Astrologer =>
        typeof item === "object" &&
        item !== null &&
        typeof (item as Astrologer).id === "string" &&
        typeof (item as Astrologer).name === "string" &&
        typeof (item as Astrologer).first_name === "string" &&
        typeof (item as Astrologer).last_name === "string" &&
        Array.isArray((item as Astrologer).specialties) &&
        typeof (item as Astrologer).style === "string" &&
        typeof (item as Astrologer).bio_short === "string"
    )
  } catch {
    return []
  }
}

function storeCachedAstrologers(astrologers: Astrologer[]): void {
  if (typeof window === "undefined" || astrologers.length === 0) {
    return
  }
  window.localStorage.setItem(
    ASTROLOGERS_LOCAL_CACHE_KEY,
    JSON.stringify(astrologers)
  )
}

async function getAstrologers(): Promise<Astrologer[]> {
  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/astrologers`, {
      method: "GET",
      headers: {
        ...getAccessTokenAuthHeader(),
      },
    })

    if (!response.ok) {
      if (response.status === 404 && USE_MOCK_FALLBACK) {
        return MOCK_ASTROLOGERS
      }
      let payload: ErrorEnvelope | null = null
      try {
        payload = (await response.json()) as ErrorEnvelope
      } catch {
        payload = null
      }
      throw new AstrologersApiError(
        payload?.error?.code ?? "unknown_error",
        payload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        payload?.error?.details ?? {},
      )
    }

    const payload = (await response.json()) as { data: Astrologer[] }
    const astrologers = Array.isArray(payload.data) ? payload.data : []
    if (astrologers.length > 0) {
      storeCachedAstrologers(astrologers)
      return astrologers
    }

    const cachedAstrologers = loadCachedAstrologers()
    if (cachedAstrologers.length > 0) {
      return cachedAstrologers
    }

    if (USE_MOCK_FALLBACK) {
      return MOCK_ASTROLOGERS
    }

    return []
  } catch (error) {
    if (error instanceof AstrologersApiError) {
      const cachedAstrologers = loadCachedAstrologers()
      if (cachedAstrologers.length > 0) {
        return cachedAstrologers
      }
      throw error
    }
    if (error instanceof TypeError && USE_MOCK_FALLBACK) {
      return MOCK_ASTROLOGERS
    }
    const cachedAstrologers = loadCachedAstrologers()
    if (cachedAstrologers.length > 0) {
      return cachedAstrologers
    }
    throw error
  }
}

/**
 * Validates an astrologer ID.
 * Valid IDs: alphanumeric characters, underscores, hyphens; 1-64 chars.
 */
function isValidAstrologerId(id: string): boolean {
  return /^[a-zA-Z0-9_-]+$/.test(id) && id.length > 0 && id.length <= 64
}

async function getAstrologer(id: string): Promise<AstrologerProfile | null> {
  if (!isValidAstrologerId(id)) {
    return null
  }

  try {
    const response = await apiFetch(`${API_BASE_URL}/v1/astrologers/${encodeURIComponent(id)}`, {
      method: "GET",
      headers: {
        ...getAccessTokenAuthHeader(),
      },
    })

    if (!response.ok) {
      if (response.status === 404 && USE_MOCK_FALLBACK) {
        return MOCK_ASTROLOGER_PROFILES[id] ?? null
      }
      let payload: ErrorEnvelope | null = null
      try {
        payload = (await response.json()) as ErrorEnvelope
      } catch {
        payload = null
      }
      throw new AstrologersApiError(
        payload?.error?.code ?? "unknown_error",
        payload?.error?.message ?? `Request failed with status ${response.status}`,
        response.status,
        payload?.error?.details ?? {},
      )
    }

    const payload = (await response.json()) as { data: AstrologerProfile }
    return payload.data
  } catch (error) {
    if (error instanceof AstrologersApiError) {
      throw error
    }
    if (error instanceof TypeError && USE_MOCK_FALLBACK) {
      return MOCK_ASTROLOGER_PROFILES[id] ?? null
    }
    throw error
  }
}

export const ASTROLOGERS_CACHE_CONFIG = {
  list: {
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  },
  detail: {
    staleTime: 10 * 60 * 1000,
    gcTime: 20 * 60 * 1000,
  },
} as const

export function useAstrologers() {
  return useQuery({
    queryKey: ["astrologers"],
    queryFn: getAstrologers,
    staleTime: ASTROLOGERS_CACHE_CONFIG.list.staleTime,
    gcTime: ASTROLOGERS_CACHE_CONFIG.list.gcTime,
  })
}

export function useAstrologer(id: string | undefined) {
  const isValidId = !!id && isValidAstrologerId(id)

  return useQuery({
    queryKey: ["astrologer", id],
    queryFn: () => getAstrologer(id!),
    enabled: isValidId,
    staleTime: ASTROLOGERS_CACHE_CONFIG.detail.staleTime,
    gcTime: ASTROLOGERS_CACHE_CONFIG.detail.gcTime,
  })
}

export { MOCK_ASTROLOGERS, MOCK_ASTROLOGER_PROFILES, isValidAstrologerId }
