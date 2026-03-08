import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'
import { RefreshCw } from 'lucide-react'

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
import { trackEvent, EVENTS } from '../utils/analytics'

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

  useEffect(() => {
    if (prediction) {
      trackEvent(EVENTS.PREDICTION_VIEWED, {
        date: prediction.meta.date_local,
        was_reused: prediction.meta.was_reused,
      })
    }
  }, [prediction])

  const userName = isUserLoading ? 'loading' : (isUserError ? 'Utilisateur' : getUserDisplayName(user))

  const isLoading = isUserLoading || isPredictionLoading
  const isError = isUserError || isPredictionError

  const handleRetry = () => {
    refetchUser()
    refetchPrediction()
  }

  const handleRefresh = () => {
    trackEvent(EVENTS.PREDICTION_REFRESHED)
    refetchPrediction()
  }

  const handleCategoryClick = (categoryCode: string) => {
    trackEvent(EVENTS.CATEGORY_CLICKED, { category_code: categoryCode })
  }

  const handleTimelineClick = () => {
    trackEvent(EVENTS.TIMELINE_OPENED)
  }

  const handleTurningPointClick = (severity: number) => {
    const severityCode = severity > 0.75 ? 'critical' : severity > 0.5 ? 'high' : severity > 0.25 ? 'medium' : 'low'
    trackEvent(EVENTS.TURNING_POINT_OPENED, { severity: severityCode })
  }

  const handleHistoryClick = () => {
    trackEvent(EVENTS.HISTORY_VIEWED, { range_days: 7 })
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
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1rem' }}>
            <button 
              type="button" 
              className="button-ghost" 
              onClick={handleRefresh}
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}
            >
              <RefreshCw size={16} />
              Actualiser
            </button>
          </div>

          <DayPredictionCard prediction={prediction} lang={lang} />
          
          <CategoryGrid 
            categories={prediction.categories} 
            lang={lang} 
            onCategoryClick={handleCategoryClick}
          />
          
          <TurningPointsList 
            turningPoints={prediction.turning_points} 
            lang={lang} 
            onTurningPointClick={handleTurningPointClick}
          />
          
          <DayTimeline 
            timeline={prediction.timeline} 
            lang={lang} 
            onTimelineClick={handleTimelineClick}
          />

          <ShortcutsSection onHistoryClick={handleHistoryClick} />
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
