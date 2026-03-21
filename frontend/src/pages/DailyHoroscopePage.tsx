import { useNavigate } from 'react-router-dom'
import { PageLayout } from '../layouts'
import { useEffect, useRef } from 'react'

import { DailyPageHeader } from '../components/prediction/DailyPageHeader'
import { DayClimateHero } from '../components/DayClimateHero'
import { AstroDailyEvents } from '../components/AstroDailyEvents'
import { DomainRankingCard } from '../components/DomainRankingCard'
import { DayTimelineSectionV4 } from '../components/prediction/DayTimelineSectionV4'
import { TurningPointCard } from '../components/TurningPointCard'
import { BestWindowCard } from '../components/BestWindowCard'
import { DailyAdviceCard } from '../components/prediction/DailyAdviceCard'
import { AstroFoundationSection } from '../components/AstroFoundationSection'

import { detectLang } from '../i18n/astrology'
import { normalizeSignCode } from '../i18n/astrology'
import type { Lang } from '../i18n/predictions'
import { getPredictionMessage } from '../utils/predictionI18n'
import { getSubjectFromAccessToken, useAccessTokenSnapshot } from '../utils/authToken'
import { useDailyPrediction } from '../api/useDailyPrediction'
import { useBirthData } from '../api/useBirthData'
import { trackEvent, EVENTS } from '../utils/analytics'
import { SectionErrorBoundary } from '../components/ErrorBoundary'

import { mapDayClimate } from '../utils/dayClimateHeroMapper'
import { mapAstroDailyEvents } from '../utils/astroDailyEventsMapper'
import { mapDomainRanking } from '../utils/domainRankingCardMapper'

import { mapTurningPoint } from '../utils/turningPointCardMapper'
import { mapBestWindow } from '../utils/bestWindowCardMapper'
import { mapAstroFoundation } from '../utils/astroFoundationSectionMapper'
import { buildDailyAdviceCardModel } from '../utils/dailyAdviceCardMapper'
import { clamp } from '../components/astro/astroMoodBackgroundUtils'
import type { ZodiacSign } from '../components/astro/zodiacPatterns'

import './DailyHoroscopePage.css'

export default function DailyHoroscopePage() {
  const navigate = useNavigate()
  const lang = detectLang()
  const token = useAccessTokenSnapshot()
  const userId = getSubjectFromAccessToken(token)
  const { data: prediction, isLoading, isError, refetch } = useDailyPrediction(token)
  const { data: birthData } = useBirthData(token)
  const bootstrapPredictionRefetchDoneForToken = useRef<string | null>(null)

  // Track page view
  const hasTracked = useRef(false)
  useEffect(() => {
    if (prediction && !hasTracked.current) {
      trackEvent(EVENTS.PREDICTION_VIEWED, { date: prediction.meta.date_local })
      hasTracked.current = true
    }
  }, [prediction])

  useEffect(() => {
    if (!token) {
      bootstrapPredictionRefetchDoneForToken.current = null
      return
    }

    if (isLoading || isError || prediction !== null) {
      return
    }

    if (bootstrapPredictionRefetchDoneForToken.current === token) {
      return
    }

    bootstrapPredictionRefetchDoneForToken.current = token
    void refetch()
  }, [isError, isLoading, prediction, refetch, token])

  const handleRefresh = async () => {
    await refetch()
  }

  const handleRetry = () => {
    void refetch()
  }

  // Pre-calculate astro background data
  const astroBackgroundProps = prediction
    ? {
        sign: ((birthData?.astro_profile?.sun_sign_code
          ? normalizeSignCode(birthData.astro_profile.sun_sign_code)
          : 'neutral') as ZodiacSign),
        userId: userId || 'anonymous',
        dateKey: prediction.meta.date_local,
        dayScore: clamp(
          Math.round(
            prediction.categories.length > 0
              ? prediction.categories
                  .map((category) => category.note_20)
                  .filter((note) => typeof note === 'number' && !Number.isNaN(note))
                  .reduce((sum, note, _, notes) => sum + note / notes.length, 0)
              : 12,
          ),
          1,
          20,
        ),
      }
    : undefined

  const pLang = lang as Lang

  return (
    <PageLayout>
      {isLoading ? (
        <div className="daily-page-state">
          <div className="state-line state-loading">{getPredictionMessage('loading', pLang)}</div>
        </div>
      ) : isError ? (
        <div className="daily-page-state">
          <p>{getPredictionMessage('error', pLang)}</p>
          <button type="button" onClick={handleRetry}>{getPredictionMessage('retry', pLang)}</button>
        </div>
      ) : prediction ? (
        <div className="daily-layout">
          {/* Decorative Background Elements (Story 60.17) */}
          <div className="daily-layout__bg-halo-3" />
          <div className="daily-layout__noise" />

          {/* Zone 1 : DailyPageHeader éditorial */}
          <DailyPageHeader
            date={prediction.meta.date_local}
            tone={prediction.day_climate?.tone || prediction.summary.overall_tone}
            lang={pLang}
            onRefresh={handleRefresh}
            refreshLabel={getPredictionMessage('refresh', pLang)}
          />

          {/* Zone 2 : DayClimateHero (V4) — Focus Masterpiece */}
          <SectionErrorBoundary onRetry={handleRefresh}>
            {(() => {
              const climate = mapDayClimate(prediction);
              return climate ? (
                <DayClimateHero 
                  climate={climate} 
                  dailySynthesis={prediction.daily_synthesis} 
                  astroBackgroundProps={astroBackgroundProps}
                  lang={pLang} 
                />
              ) : null;
            })()}
          </SectionErrorBoundary>

          {/* Zone 3 : DomainRankingCard (V4) — Premium Metrics */}
          {(() => {
            const domains = mapDomainRanking(prediction);
            return domains.length > 0 ? (
              <div className="daily-layout__section">
                <DomainRankingCard domains={domains} lang={pLang} />
              </div>
            ) : null;
          })()}

          {/* Zone 4 : DayTimelineSectionV4 (V4) — Connected Story */}
          <SectionErrorBoundary onRetry={handleRefresh}>
            {prediction.time_windows && (
              <div className="daily-layout__section">
                <DayTimelineSectionV4 
                  timeWindows={prediction.time_windows} 
                  lang={pLang} 
                />
              </div>
            )}
          </SectionErrorBoundary>

          {/* Zone 5 : TurningPointCard (V4) */}
          {(() => {
            const tp = mapTurningPoint(prediction);
            return tp ? (
              <div className="daily-layout__section">
                <h3 className="daily-layout__section-title">
                  {pLang === 'fr' ? 'Moment clé' : 'Key moment'}
                </h3>
                <TurningPointCard turningPoint={tp} lang={pLang} />
              </div>
            ) : null;
          })()}

          {/* Zone 6 : BestWindowCard (V4) */}
          {(() => {
            const bw = mapBestWindow(prediction);
            return bw ? (
              <div className="daily-layout__section">
                <h3 className="daily-layout__section-title">
                  {pLang === 'fr' ? 'Opportunité' : 'Opportunity'}
                </h3>
                <BestWindowCard bestWindow={bw} lang={pLang} />
              </div>
            ) : null;
          })()}

          {/* Zone 7 : AstroDailyEvents (Story 60.13) — Analytical Card */}
          {(() => {
            const astroEvents = mapAstroDailyEvents(prediction);
            return astroEvents ? (
              <div className="daily-layout__section">
                <AstroDailyEvents 
                  data={astroEvents} 
                  intro={prediction.astro_events_intro} 
                  lang={pLang} 
                />
              </div>
            ) : null;
          })()}

          {/* Zone 8 : DailyAdviceCard — Conclusive Masterpiece */}
          <div className="daily-layout__section">
            <DailyAdviceCard model={buildDailyAdviceCardModel(prediction, pLang)} />
          </div>

          {/* Zone 9 : AstroFoundationSection (V4) */}
          <div className="daily-layout__section">
            <AstroFoundationSection 
              foundation={mapAstroFoundation(prediction)} 
              lang={pLang} 
            />
          </div>

          {/* BottomSpacer */}
          <div className="daily-layout__bottom-spacer" />
        </div>
      ) : (
        <div className="panel state-empty daily-page-state">
          <p>{getPredictionMessage('empty', pLang)}</p>
          <button type="button" onClick={() => navigate('/natal')}>{getPredictionMessage('setup_profile', pLang)}</button>
        </div>
      )}
    </PageLayout>
  )
}
