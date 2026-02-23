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
    id: "1",
    name: "Luna Céleste",
    avatar_url: "/avatars/luna.jpg",
    specialties: ["Thème natal", "Transits", "Relations"],
    style: "Bienveillant et direct",
    bio_short: "Astrologue depuis 15 ans, spécialisée en astrologie relationnelle.",
  },
  {
    id: "2",
    name: "Orion Mystique",
    avatar_url: "/avatars/orion.jpg",
    specialties: ["Carrière", "Événements", "Tarot"],
    style: "Analytique et précis",
    bio_short: "Expert en astrologie prévisionnelle et choix de carrière.",
  },
  {
    id: "3",
    name: "Stella Nova",
    avatar_url: "/avatars/stella.jpg",
    specialties: ["Développement personnel", "Spiritualité", "Méditation"],
    style: "Doux et intuitif",
    bio_short: "Guide spirituel utilisant l'astrologie comme outil d'éveil.",
  },
  {
    id: "4",
    name: "Atlas Cosmos",
    avatar_url: "/avatars/atlas.jpg",
    specialties: ["Finance", "Investissements", "Cycles économiques"],
    style: "Pragmatique et factuel",
    bio_short: "Spécialiste de l'astrologie financière et des cycles planétaires.",
  },
]

const MOCK_ASTROLOGER_PROFILES: Record<string, AstrologerProfile> = {
  "1": {
    ...MOCK_ASTROLOGERS[0],
    bio_full:
      "Passionnée par les étoiles depuis mon enfance, j'ai consacré 15 années à l'étude approfondie de l'astrologie. Ma spécialité est l'astrologie relationnelle : comprendre les dynamiques de couple, les compatibilités et les défis à surmonter ensemble. Mon approche est bienveillante mais directe - je crois qu'une guidance claire est plus utile qu'un discours flou.",
    languages: ["Français", "Anglais", "Espagnol"],
    experience_years: 15,
  },
  "2": {
    ...MOCK_ASTROLOGERS[1],
    bio_full:
      "Formé à l'astrologie traditionnelle et moderne, je combine analyse rigoureuse et intuition. Mon domaine de prédilection : les questions de carrière et les moments clés de la vie. Je travaille avec le tarot en complément de l'astrologie pour offrir des lectures enrichies. Mon style est analytique et précis - chaque conseil est fondé sur une étude minutieuse de votre thème.",
    languages: ["Français", "Anglais"],
    experience_years: 12,
  },
  "3": {
    ...MOCK_ASTROLOGERS[2],
    bio_full:
      "L'astrologie est pour moi un chemin vers la connaissance de soi. Je guide mes consultants vers une compréhension profonde de leur être intérieur, utilisant le thème natal comme miroir de l'âme. Mes séances intègrent méditation et visualisation pour une expérience transformatrice. Mon approche est douce et intuitive, respectant le rythme de chacun.",
    languages: ["Français"],
    experience_years: 8,
  },
  "4": {
    ...MOCK_ASTROLOGERS[3],
    bio_full:
      "Ancien analyste financier reconverti à l'astrologie, j'applique une approche pragmatique et factuelle. Je me spécialise dans les cycles économiques, les moments propices aux investissements et les questions financières. Pas de mysticisme excessif : des conseils concrets basés sur des observations astrologiques solides.",
    languages: ["Français", "Anglais", "Allemand"],
    experience_years: 10,
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
    return payload.data
  } catch (error) {
    if (error instanceof AstrologersApiError) {
      throw error
    }
    if (error instanceof TypeError && USE_MOCK_FALLBACK) {
      return MOCK_ASTROLOGERS
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
