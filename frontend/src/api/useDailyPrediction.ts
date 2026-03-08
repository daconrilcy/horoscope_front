import { useQuery } from "@tanstack/react-query";
import { ApiError, getDailyPrediction, getDailyHistory } from "./dailyPrediction";
import { getSubjectFromAccessToken } from "../utils/authToken";
import { ANONYMOUS_SUBJECT } from "../utils/constants";

function isPredictionSetupError(error: unknown): boolean {
  if (!(error instanceof ApiError)) {
    return false;
  }

  return (
    error.status === 404 ||
    (error.status === 422 &&
      [
        "natal_missing",
        "profile_missing",
        "timezone_missing",
        "timezone_invalid",
        "location_missing",
      ].includes(error.code))
  );
}

export function useDailyPrediction(token: string | null, date?: string) {
  const tokenSubject = getSubjectFromAccessToken(token) ?? ANONYMOUS_SUBJECT;
  return useQuery({
    queryKey: ["daily-prediction", tokenSubject, date ?? "today"],
    queryFn: async () => {
      try {
        return await getDailyPrediction(token!, date);
      } catch (error) {
        if (isPredictionSetupError(error)) {
          return null;
        }
        throw error;
      }
    },
    enabled: Boolean(token),
    staleTime: 1000 * 60 * 5, // 5 minutes
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });
}

export function useDailyHistory(token: string | null, from: string, to: string) {
  const tokenSubject = getSubjectFromAccessToken(token) ?? ANONYMOUS_SUBJECT;
  return useQuery({
    queryKey: ["daily-history", tokenSubject, from, to],
    queryFn: () => getDailyHistory(token!, from, to),
    enabled: Boolean(token) && Boolean(from) && Boolean(to),
    staleTime: 1000 * 60 * 15, // 15 minutes
  });
}
