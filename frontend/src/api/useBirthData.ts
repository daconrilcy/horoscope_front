import { useQuery } from '@tanstack/react-query';
import { getBirthData } from './birthProfile';
import { getSubjectFromAccessToken } from '../utils/authToken';
import { ANONYMOUS_SUBJECT } from '../utils/constants';

export function useBirthData(token: string | null) {
  const tokenSubject = getSubjectFromAccessToken(token) ?? ANONYMOUS_SUBJECT;
  return useQuery({
    queryKey: ['birth-data', tokenSubject],
    queryFn: async () => {
      if (!token) throw new Error('No access token');
      return getBirthData(token);
    },
    enabled: Boolean(token),
    staleTime: 1000 * 60 * 60, // 1 hour - birth data is stable
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnReconnect: false,
  });
}
