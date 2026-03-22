import { QueryClient } from '@tanstack/react-query';
import { getDailyPredictionQueryOptions } from '../api/useDailyPrediction';
import { getBirthDataQueryOptions } from '../api/useBirthData';

/**
 * Prefetch essential data for the daily horoscope page.
 * This should be called on click of navigation links to provide an instant feel.
 */
export async function prefetchDailyHoroscope(queryClient: QueryClient, token: string | null) {
  if (!token) return;

  await Promise.allSettled([
    queryClient.prefetchQuery(getDailyPredictionQueryOptions(token)),
    queryClient.prefetchQuery(getBirthDataQueryOptions(token)),
  ]);
}
