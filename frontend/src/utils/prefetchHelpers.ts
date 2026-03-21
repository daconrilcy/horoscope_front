import { QueryClient } from '@tanstack/react-query';
import { getDailyPrediction } from '../api/dailyPrediction';
import { getBirthData } from '../api/birthProfile';
import { getSubjectFromAccessToken } from '../utils/authToken';
import { ANONYMOUS_SUBJECT } from '../utils/constants';

/**
 * Prefetch essential data for the daily horoscope page.
 * This should be called on click of navigation links to provide an instant feel.
 */
export async function prefetchDailyHoroscope(queryClient: QueryClient, token: string | null) {
  if (!token) return;

  const tokenSubject = getSubjectFromAccessToken(token) ?? ANONYMOUS_SUBJECT;

  // 1. Prefetch Daily Prediction
  // We use 'today' as the default date, consistent with useDailyPrediction hook
  await queryClient.prefetchQuery({
    queryKey: ['daily-prediction', tokenSubject, 'today'],
    queryFn: async () => {
      try {
        return await getDailyPrediction(token);
      } catch (error) {
        // We let the prefetch fail silently or be handled by the subsequent hook
        return null;
      }
    },
    staleTime: 5 * 60 * 1000,
  });

  // 2. Prefetch Birth Data
  await queryClient.prefetchQuery({
    queryKey: ['birth-data', tokenSubject],
    queryFn: () => getBirthData(token),
    staleTime: 30 * 60 * 1000,
  });
}
