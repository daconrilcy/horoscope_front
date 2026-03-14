import { useMemo } from 'react';
import { useDailyPrediction } from '../../api/useDailyPrediction';
import { useBirthData } from '../../api/useBirthData';
import { getSubjectFromAccessToken } from '../../utils/authToken';
import { normalizeSignCode } from '../../i18n/astrology';
import type { ZodiacSign } from '../astro/zodiacPatterns';
import { clamp } from '../astro/astroMoodBackgroundUtils';
import type { DailyPredictionResponse } from '../../types/dailyPrediction';

export interface DashboardAstroSummary {
  sign: ZodiacSign;
  userId: string;
  dateKey: string;
  dayScore: number;
  isLoading: boolean;
  isError: boolean;
  prediction: DailyPredictionResponse | null;
  refetch: () => void;
}

export function useDashboardAstroSummary(token: string | null): DashboardAstroSummary {
  const { 
    data: prediction, 
    isLoading: isLoadingPrediction, 
    isError: isPredictionError,
    refetch,
  } = useDailyPrediction(token);
  
  const { data: birthData } = useBirthData(token);

  const userId = useMemo(() => getSubjectFromAccessToken(token) || 'anonymous', [token]);

  const dateKey = useMemo(() => {
    if (prediction?.meta?.date_local) {
      return prediction.meta.date_local;
    }
    return new Date().toISOString().split('T')[0];
  }, [prediction]);

  const sign = useMemo((): ZodiacSign => {
    const code = birthData?.astro_profile?.sun_sign_code;
    if (code) {
      return normalizeSignCode(code) as ZodiacSign;
    }
    return 'neutral';
  }, [birthData]);

  const dayScore = useMemo(() => {
    if (!prediction?.categories || prediction.categories.length === 0) {
      return 12; // Fallback value
    }

    const validNotes = prediction.categories
      .map((c) => c.note_20)
      .filter((n) => typeof n === 'number' && !isNaN(n));

    if (validNotes.length === 0) {
      return 12;
    }

    const mean = validNotes.reduce((acc, val) => acc + val, 0) / validNotes.length;
    return clamp(Math.round(mean), 1, 20);
  }, [prediction]);

  return {
    sign,
    userId,
    dateKey,
    dayScore,
    isLoading: isLoadingPrediction,
    isError: isPredictionError,
    prediction: prediction ?? null,
    refetch,
  };
}
