import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'

import { TodayHeader } from '../components/TodayHeader'
import { HeroHoroscopeCard } from '../components/HeroHoroscopeCard'
import { ShortcutsSection } from '../components/ShortcutsSection'
import { DailyInsightsSection } from '../components/DailyInsightsSection'
import { useAccessTokenSnapshot, getSubjectFromAccessToken } from '../utils/authToken'
import { useAuthMe } from '../api/authMe'
import { getBirthData } from '../api/birthProfile'
import { getUserDisplayName } from '../utils/user'
import { STATIC_HOROSCOPE, TODAY_DATE_FORMATTER } from '../constants/horoscope'
import { ANONYMOUS_SUBJECT } from '../utils/constants'
import { translateSign, detectLang, isKnownSignCode } from '../i18n/astrology'

export function TodayPage() {
  const navigate = useNavigate()
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT
  const lang = detectLang()

  const { data: user, isLoading: isUserLoading, isError, refetch } = useAuthMe(accessToken)

  const { data: birthData } = useQuery({
    queryKey: ['birth-profile', tokenSubject],
    queryFn: () => getBirthData(accessToken!),
    enabled: Boolean(accessToken),
    staleTime: 1000 * 60 * 5,
  })

  // Current date formatted for the hero card (e.g. "24 fév.")
  const todayDate = TODAY_DATE_FORMATTER.format(new Date())
    .replace(/\.$/, '') // Remove trailing dot if any (standardizing for French abbreviations)
    .trim()

  const userName = isUserLoading ? 'loading' : (isError ? 'Utilisateur' : getUserDisplayName(user))

  // Derive sign info from API astro_profile, fallback to static data
  const rawSunSignCode = birthData?.astro_profile?.sun_sign_code ?? null
  const sunSignCode = rawSunSignCode && isKnownSignCode(rawSunSignCode) ? rawSunSignCode : null
  const signName = sunSignCode ? translateSign(sunSignCode, lang) : STATIC_HOROSCOPE.signName

  return (
    <div className="today-page">
      <TodayHeader userName={userName} />

      {isError && !user ? (
        <div className="panel state-error-centered" style={{ marginTop: '2rem' }}>
          <p>Impossible de charger votre profil.</p>
          <button type="button" onClick={() => refetch()}>Réessayer</button>
        </div>
      ) : (
        <>
          <HeroHoroscopeCard
            signCode={sunSignCode}
            sign={STATIC_HOROSCOPE.sign}
            signName={signName}
            date={todayDate}
            headline={STATIC_HOROSCOPE.headline}
            onReadFull={() => navigate('/natal')}
            onReadDetailed={() => navigate('/natal')}
          />
          <ShortcutsSection />
          {/* DailyInsightsSection implements the 'Section Amour/Travail/Énergie' from spec §10.3 */}
          <DailyInsightsSection onSectionClick={() => navigate('/natal')} />
        </>
      )}
    </div>
  )
}
