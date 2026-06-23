// Hook dashboard qui consolide le resume astrologique depuis les donnees utilisateur.
import { useMemo } from 'react';
import { useBirthData } from '../../../api/useBirthData';
import { getSubjectFromAccessToken } from '../../../utils/authToken';
import { normalizeSignCode } from '../../../i18n/astrology';
import type { ZodiacSign } from '../../../components/astro/zodiacPatterns';
import { clamp } from '../../../components/astro/astroMoodBackgroundUtils';

export interface DashboardAstroSummary {
  sign: ZodiacSign;
  userId: string;
  dateKey: string;
  dayScore: number;
  isLoading: boolean;
  isError: boolean;
  prediction: null;
  refetch: () => void;
}

export function useDashboardAstroSummary(token: string | null): DashboardAstroSummary {
  const { data: birthData, isLoading, isError, refetch } = useBirthData(token);

  const userId = useMemo(() => getSubjectFromAccessToken(token) || 'anonymous', [token]);

  const dateKey = useMemo(() => {
    return new Date().toISOString().split('T')[0];
  }, []);

  const sign = useMemo((): ZodiacSign => {
    const code = birthData?.astro_profile?.sun_sign_code;
    if (code) {
      return normalizeSignCode(code) as ZodiacSign;
    }
    return 'neutral';
  }, [birthData]);

  const dayScore = useMemo(() => {
    return clamp(12, 1, 20);
  }, []);

  return {
    sign,
    userId,
    dateKey,
    dayScore,
    isLoading,
    isError,
    prediction: null,
    refetch,
  };
}
