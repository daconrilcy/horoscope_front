import { useAccessTokenSnapshot } from '../utils/authToken';
import { useDailyPrediction } from '../api/useDailyPrediction';

/**
 * Wrapper hook for daily prediction fetching (Story 55.2).
 */
export function useDayPrediction(date?: string) {
  const token = useAccessTokenSnapshot();
  const query = useDailyPrediction(token, date);

  return {
    prediction: query.data ?? null,
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
  };
}
