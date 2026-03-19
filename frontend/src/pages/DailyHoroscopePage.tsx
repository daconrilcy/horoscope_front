import { useNavigate } from 'react-router-dom'
import { PageLayout } from '../layouts'
import { useEffect, useRef } from 'react'
import { RefreshCw } from 'lucide-react'

import { TodayHeader } from '../components/TodayHeader'
import { DayClimateHero } from '../components/DayClimateHero'
import { DomainRankingCard } from '../components/DomainRankingCard'
import { DayTimelineSectionV4 } from '../components/prediction/DayTimelineSectionV4'
import { TurningPointCard } from '../components/TurningPointCard'
import { BestWindowCard } from '../components/BestWindowCard'
import { DailyAdviceCard } from '../components/prediction/DailyAdviceCard'
import { AstroFoundationSection } from '../components/AstroFoundationSection'
import { DailyPageHeader } from '../components/prediction/DailyPageHeader'

import { detectLang } from '../i18n/astrology'
import { getPredictionMessage } from '../utils/predictionI18n'
import { useAccessTokenSnapshot } from '../utils/authToken'
import { useAuthMe } from '../api/authMe'
import { useDailyPrediction } from '../api/useDailyPrediction'
import { trackEvent, EVENTS } from '../utils/analytics'
import { SectionErrorBoundary } from '../components/ErrorBoundary'

import { mapDayClimate } from '../utils/dayClimateHeroMapper'
import { mapDomainRanking } from '../utils/domainRankingCardMapper'
import { mapTurningPoint } from '../utils/turningPointCardMapper'
import { mapBestWindow } from '../utils/bestWindowCardMapper'
import { mapAstroFoundation } from '../utils/astroFoundationSectionMapper'
import { buildDailyAdviceCardModel } from '../utils/dailyAdviceCardMapper'

import './DailyHoroscopePage.css'

export function DailyHoroscopePage() {
  const navigate = useNavigate()
  const accessToken = useAccessTokenSnapshot()
  const detected = detectLang()
  const lang = (detected === 'en' ? 'en' : 'fr') as any
  const manualRefreshPending = useRef(false)
  const bootstrapPredictionRefetchDoneForToken = useRef<string | null>(null)

  const { isLoading: isUserLoading, isError: isUserError, refetch: refetchUser } = useAuthMe(accessToken)

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
      if (manualRefreshPending.current) {
        trackEvent(EVENTS.PREDICTION_REFRESHED, { was_reused: prediction.meta.was_reused })
        manualRefreshPending.current = false
      }
    }
  }, [prediction])

  useEffect(() => {
    if (!accessToken) {
      bootstrapPredictionRefetchDoneForToken.current = null
      return
    }

    if (isPredictionLoading || isPredictionError || prediction !== null) {
      return
    }

    if (bootstrapPredictionRefetchDoneForToken.current === accessToken) {
      return
    }

    bootstrapPredictionRefetchDoneForToken.current = accessToken
    refetchPrediction()
  }, [accessToken, isPredictionError, isPredictionLoading, prediction, refetchPrediction])

  const isLoading = isUserLoading || isPredictionLoading
  const isError = isUserError || isPredictionError

  const handleRetry = () => {
    refetchUser()
    refetchPrediction()
  }

  const handleRefresh = () => {
    manualRefreshPending.current = true
    refetchPrediction()
  }

  return (
    <PageLayout
      header={
        <TodayHeader 
          showAvatar={false}
          onBackClick={() => navigate("/dashboard")} 
        />
      }
      className="today-page"
    >
      {isLoading ? (
        <div className="panel state-loading daily-page-state">
          <p>{getPredictionMessage('loading', lang)}</p>
        </div>
      ) : isError ? (
        <div className="panel state-error-centered daily-page-state">
          <p>{getPredictionMessage('error', lang)}</p>
          <button type="button" onClick={handleRetry}>{getPredictionMessage('retry', lang)}</button>
        </div>
      ) : prediction ? (
        <div className="daily-layout">
          {/* Zone 1 : DailyPageHeader éditorial */}
          <DailyPageHeader
            date={prediction.meta.date_local}
            tone={prediction.day_climate?.tone || prediction.summary.overall_tone}
            lang={lang}
          />

          {/* Bouton refresh — séparé du header éditorial */}
          <div className="daily-layout__refresh-row">
            <button
              type="button"
              className="daily-page-refresh-button"
              onClick={handleRefresh}
              aria-label={getPredictionMessage('refresh', lang)}
            >
              <RefreshCw size={15} aria-hidden="true" />
            </button>
          </div>

          {/* Zone 2 : DayClimateHero (V4) or HeroSummaryCard (V3) */}
          <SectionErrorBoundary onRetry={handleRefresh}>
            {(() => {
              const isV4 = prediction.meta.payload_version === 'v4';
              const climate = mapDayClimate(prediction);
              
              if (isV4 && climate) {
                return <DayClimateHero climate={climate} lang={lang} />;
              }
              
              // Fallback V3 (using data directly or via old mapper if available)
              // Since I replaced the whole page content, I need to make sure I don't break fallback.
              // Actually, mapDayClimate handles fallback internally.
              return climate ? <DayClimateHero climate={climate} lang={lang} /> : null;
            })()}
          </SectionErrorBoundary>

          {/* Zone 3 : DomainRankingCard (V4) */}
          <DomainRankingCard 
            domains={mapDomainRanking(prediction)} 
            lang={lang} 
          />

          {/* Zone 4 : DayTimelineSectionV4 (V4) */}
          {prediction.time_windows && (
            <DayTimelineSectionV4 
              timeWindows={prediction.time_windows} 
              lang={lang} 
            />
          )}

          {/* Zone 5 : TurningPointCard (V4) */}
          <TurningPointCard 
            turningPoint={mapTurningPoint(prediction)} 
            lang={lang} 
          />

          {/* Zone 6 : BestWindowCard (V4) */}
          <BestWindowCard 
            bestWindow={mapBestWindow(prediction)} 
            lang={lang} 
          />

          {/* Zone 7 : DailyAdviceCard — Conseil du jour */}
          <DailyAdviceCard model={buildDailyAdviceCardModel(prediction, lang)} />

          {/* Zone 8 : AstroFoundationSection (V4) */}
          <AstroFoundationSection 
            foundation={mapAstroFoundation(prediction)} 
            lang={lang} 
          />

          {/* BottomSpacer */}
          <div className="daily-layout__bottom-spacer" />
        </div>
      ) : (
        <div className="panel state-empty daily-page-state">
          <p>{getPredictionMessage('empty', lang)}</p>
          <button type="button" onClick={() => navigate('/natal')}>{getPredictionMessage('setup_profile', lang)}</button>
        </div>
      )}
    </PageLayout>
  )
}
