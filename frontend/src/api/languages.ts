// Client des langues publiques servant de source de vérité au sélecteur d'interface.
import { useQuery } from "@tanstack/react-query"

import { apiFetch, type ApiResponseEnvelope } from "./client"

export interface LanguageOption {
  code: string
  name: string
}

async function fetchLanguages(): Promise<LanguageOption[]> {
  const response = await apiFetch("/v1/reference-data/languages")
  if (!response.ok) {
    throw new Error("Failed to fetch languages")
  }
  const payload = (await response.json()) as ApiResponseEnvelope<LanguageOption[]>
  return payload.data
}

export function useLanguages() {
  return useQuery({
    queryKey: ["reference-data", "languages"],
    queryFn: fetchLanguages,
    staleTime: 1000 * 60 * 10,
  })
}
