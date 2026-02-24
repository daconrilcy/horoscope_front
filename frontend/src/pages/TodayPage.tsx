import { useNavigate } from 'react-router-dom'

import { TodayHeader } from '../components/TodayHeader'
import { HeroHoroscopeCard } from '../components/HeroHoroscopeCard'
import { ShortcutsSection } from '../components/ShortcutsSection'
import { DailyInsightsSection } from '../components/DailyInsightsSection'
import { useAccessTokenSnapshot } from '../utils/authToken'
import { useAuthMe } from '../api/authMe'
import { getUserDisplayName } from '../utils/user'
import { STATIC_HOROSCOPE, TODAY_DATE_FORMATTER } from '../constants/horoscope'

export function TodayPage() {
  const navigate = useNavigate()
  const accessToken = useAccessTokenSnapshot()
  const { data: user, isLoading: isUserLoading, isError, refetch } = useAuthMe(accessToken)

  // Current date formatted for the hero card (e.g. "24 fév.")
  const todayDate = TODAY_DATE_FORMATTER.format(new Date())
    .replace(/\.$/, '') // Remove trailing dot if any (standardizing for French abbreviations)
    .trim()

  const userName = isUserLoading ? 'loading' : (isError ? 'Utilisateur' : getUserDisplayName(user))

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
            sign={STATIC_HOROSCOPE.sign}
            signName={STATIC_HOROSCOPE.signName}
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
