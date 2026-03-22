import { queryOptions, useQuery } from '@tanstack/react-query';
import { getBirthData } from './birthProfile';
import { getSubjectFromAccessToken } from '../utils/authToken';
import { ANONYMOUS_SUBJECT } from '../utils/constants';

export function getBirthDataQueryOptions(token: string | null) {
  const tokenSubject = getSubjectFromAccessToken(token) ?? ANONYMOUS_SUBJECT;

  return queryOptions({
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

export function useBirthData(token: string | null) {
  return useQuery(getBirthDataQueryOptions(token));
}
