import { useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "./client"
import { getSubjectFromAccessToken, hasUsableAccessToken } from "../utils/authToken"
import { ANONYMOUS_SUBJECT } from "../utils/constants"

type AuthMeData = {
  id: number
  role: string
  email: string
  created_at: string
}

async function fetchAuthMe(accessToken: string): Promise<AuthMeData> {
  const response = await apiFetch(`${API_BASE_URL}/v1/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
  })
  if (!response.ok) {
    throw new Error(`auth me failed with status ${response.status}`)
  }
  const payload = (await response.json()) as { data: AuthMeData }
  return payload.data
}

export function useAuthMe(accessToken: string | null) {
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT
  const hasValidTokenShape = hasUsableAccessToken(accessToken)
  return useQuery({
    queryKey: ["auth-me", tokenSubject],
    queryFn: async () => {
      if (!hasUsableAccessToken(accessToken)) {
        throw new Error("missing access token")
      }
      return fetchAuthMe(accessToken)
    },
    enabled: hasValidTokenShape,
    retry: false,
  })
}
