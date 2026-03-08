import { useQuery } from "@tanstack/react-query";
import { getDailyPrediction, getDailyHistory } from "./dailyPrediction";
import { getSubjectFromAccessToken } from "../utils/authToken";
import { ANONYMOUS_SUBJECT } from "../utils/constants";

export function useDailyPrediction(token: string | null, date?: string) {
  const tokenSubject = getSubjectFromAccessToken(token) ?? ANONYMOUS_SUBJECT;
  return useQuery({
    queryKey: ["daily-prediction", tokenSubject, date ?? "today"],
    queryFn: () => getDailyPrediction(token!, date),
    enabled: Boolean(token),
    staleTime: 1000 * 60 * 5, // 5 minutes
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
