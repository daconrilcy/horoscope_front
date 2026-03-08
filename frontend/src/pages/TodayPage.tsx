import { useNavigate } from 'react-router-dom'

import { TodayHeader } from '../components/TodayHeader'
import { ShortcutsSection } from '../components/ShortcutsSection'
import { DayPredictionCard } from '../components/prediction/DayPredictionCard'
import { CategoryGrid } from '../components/prediction/CategoryGrid'
import { DayTimeline } from '../components/prediction/DayTimeline'
import { TurningPointsList } from '../components/prediction/TurningPointsList'

import { useAccessTokenSnapshot } from '../utils/authToken'
import { useAuthMe } from '../api/authMe'
import { useDailyPrediction } from '../api/useDailyPrediction'
import { getUserDisplayName } from '../utils/user'

export function TodayPage() {
  const navigate = useNavigate()
  const accessToken = useAccessTokenSnapshot()

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
          <p>Chargement de votre ciel du jour...</p>
        </div>
      ) : isError ? (
        <div className="panel state-error-centered" style={{ marginTop: '2rem' }}>
          <p>Impossible de charger votre horoscope du jour.</p>
          <button type="button" onClick={handleRetry}>Réessayer</button>
        </div>
      ) : prediction ? (
        <>
          <DayPredictionCard prediction={prediction} />
          
          <CategoryGrid categories={prediction.categories} />
          
          <TurningPointsList turningPoints={prediction.turning_points} />
          
          <DayTimeline timeline={prediction.timeline} />

          <ShortcutsSection />
        </>
      ) : (
        <div className="panel state-empty" style={{ marginTop: '2rem', textAlign: 'center' }}>
          <p>Aucune prédiction disponible pour le moment.</p>
          <button type="button" onClick={() => navigate('/natal')}>Configurer mon profil</button>
        </div>
      )}
    </div>
  )
}
