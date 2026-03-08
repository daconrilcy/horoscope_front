import { useNavigate } from 'react-router-dom'

import { TodayHeader } from '../components/TodayHeader'
import { ShortcutsSection } from '../components/ShortcutsSection'
import { DayPredictionCard } from '../components/prediction/DayPredictionCard'
import { CategoryGrid } from '../components/prediction/CategoryGrid'
import { DayTimeline } from '../components/prediction/DayTimeline'
import { TurningPointsList } from '../components/prediction/TurningPointsList'

import { detectLang } from '../i18n/astrology'
import { getPredictionMessage } from '../utils/predictionI18n'
import { useAccessTokenSnapshot } from '../utils/authToken'
import { useAuthMe } from '../api/authMe'
import { useDailyPrediction } from '../api/useDailyPrediction'
import { getUserDisplayName } from '../utils/user'

export function TodayPage() {
  const navigate = useNavigate()
  const accessToken = useAccessTokenSnapshot()
  const lang = detectLang() === 'en' ? 'en' : 'fr'

  const { data: user, isLoading: isUserLoading, isError: isUserError, refetch: refetchUser } = useAuthMe(accessToken)

  const { 
    data: prediction, 
    isLoading: isPredictionLoading, 
    isError: isPredictionError,
    refetch: refetchPrediction
  } = useDailyPrediction(accessToken)

  const userName = isUserLoading ? 'loading' : (isUserError ? 'Utilisateur' : getUserDisplayName(user))

  const isLoading = isUserLoading || isPredictionLoading
  const isError = isUserError || isPredictionError

  const handleRetry = () => {
    refetchUser()
    refetchPrediction()
  }

  return (
    <div className="today-page">
      <TodayHeader userName={userName} />

      {isLoading ? (
        <div className="panel state-loading" style={{ marginTop: '2rem', textAlign: 'center' }}>
          <p>{getPredictionMessage('loading', lang)}</p>
        </div>
      ) : isError ? (
        <div className="panel state-error-centered" style={{ marginTop: '2rem' }}>
          <p>{getPredictionMessage('error', lang)}</p>
          <button type="button" onClick={handleRetry}>{getPredictionMessage('retry', lang)}</button>
        </div>
      ) : prediction ? (
        <>
          <DayPredictionCard prediction={prediction} lang={lang} />
          
          <CategoryGrid categories={prediction.categories} lang={lang} />
          
          <TurningPointsList turningPoints={prediction.turning_points} lang={lang} />
          
          <DayTimeline timeline={prediction.timeline} lang={lang} />

          <ShortcutsSection />
        </>
      ) : (
        <div className="panel state-empty" style={{ marginTop: '2rem', textAlign: 'center' }}>
          <p>{getPredictionMessage('empty', lang)}</p>
          <button type="button" onClick={() => navigate('/natal')}>{getPredictionMessage('setup_profile', lang)}</button>
        </div>
      )}
    </div>
  )
}
