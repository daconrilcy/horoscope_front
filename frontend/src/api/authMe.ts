import { useQuery } from "@tanstack/react-query"

import { API_BASE_URL, apiFetch } from "./client"
import { getSubjectFromAccessToken } from "../utils/authToken"

type AuthMeData = {
  id: number
  role: string
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
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? "anonymous"
  return useQuery({
    queryKey: ["auth-me", tokenSubject],
    queryFn: async () => {
      if (!accessToken) {
        throw new Error("missing access token")
      }
      return fetchAuthMe(accessToken)
    },
    enabled: Boolean(accessToken),
    retry: false,
  })
}
