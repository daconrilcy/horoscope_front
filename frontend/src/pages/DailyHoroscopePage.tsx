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
import {
  getHoroscopeLockedBody,
  getHoroscopeLockedLead,
  getHoroscopeTeaser,
  getHoroscopeUpgradeCtaLabel,
  getHoroscopeUpgradeHeroMessage,
  type TeaserKey,
} from '../i18n/horoscope_copy'
import { getSubjectFromAccessToken, useAccessTokenSnapshot } from '../utils/authToken'
import { useDailyPrediction } from '../api/useDailyPrediction'
import { useBirthData } from '../api/useBirthData'
import { trackEvent, EVENTS } from '../utils/analytics'
import { SectionErrorBoundary } from '../components/ErrorBoundary'
import { useFeatureAccess } from '../hooks/useEntitlementSnapshot'
import { LockedSection, UpgradeCTA } from '../components/ui'

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

function SectionHeading({ title }: { title: string }) {
  return (
    <div className="daily-layout__section-header">
      <h3 className="daily-layout__section-title">{title}</h3>
    </div>
  )
}

function LockedHoroscopeTeaser({ teaserKey, lang }: { teaserKey: TeaserKey; lang: Lang }) {
  return (
    <div className="teaser-placeholder">
      <p className="teaser-placeholder__lead">{getHoroscopeLockedLead(teaserKey, lang)}</p>
      <p className="teaser-placeholder__body">{getHoroscopeLockedBody(teaserKey, lang)}</p>
    </div>
  )
}

export default function DailyHoroscopePage() {
  const navigate = useNavigate()
  const lang = detectLang()
  const token = useAccessTokenSnapshot()
  const userId = getSubjectFromAccessToken(token)
  const { data: prediction, isLoading, isError, refetch } = useDailyPrediction(token)
  const { data: birthData } = useBirthData(token)
  const featureAccess = useFeatureAccess("horoscope_daily")
  const isLocked = featureAccess?.variant_code === "summary_only"
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
  const lockedSectionCta = (
    <UpgradeCTA
      featureCode="horoscope_daily"
      variant="button"
      to="/settings/subscription"
      label={getHoroscopeUpgradeCtaLabel(pLang)}
    />
  )

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
                  upgradeMessage={isLocked ? getHoroscopeUpgradeHeroMessage(pLang) : undefined}
                  upgradeCta={isLocked ? lockedSectionCta : undefined}
                />
              ) : null;
            })()}
          </SectionErrorBoundary>

          {/* Zone 3 : DomainRankingCard (V4) — Premium Metrics */}
          {isLocked ? (
            <div className="daily-layout__section">
              <SectionHeading title={pLang === 'fr' ? 'Vos domaines clés' : 'Your key domains'} />
              <LockedSection
                cta={lockedSectionCta}
                label={getHoroscopeTeaser('domainRanking', pLang)}
              >
                <LockedHoroscopeTeaser teaserKey="domainRanking" lang={pLang} />
              </LockedSection>
            </div>
          ) : (
            (() => {
              const domains = mapDomainRanking(prediction);
              return domains.length > 0 ? (
                <div className="daily-layout__section">
                  <SectionHeading title={pLang === 'fr' ? 'Vos domaines clés' : 'Your key domains'} />
                  <DomainRankingCard domains={domains} lang={pLang} hideTitle />
                </div>
              ) : null;
            })()
          )}

          {/* Zone 4 : DayTimelineSectionV4 (V4) — Connected Story */}
          {isLocked ? (
            <div className="daily-layout__section">
              <SectionHeading title={pLang === 'fr' ? 'Déroulé de votre journée' : 'Your day timeline'} />
              <LockedSection cta={lockedSectionCta} label={getHoroscopeTeaser('dayTimeline', pLang)}>
                <LockedHoroscopeTeaser teaserKey="dayTimeline" lang={pLang} />
              </LockedSection>
            </div>
          ) : (
            <SectionErrorBoundary onRetry={handleRefresh}>
              {prediction.time_windows && (
                <div className="daily-layout__section">
                  <SectionHeading title={pLang === 'fr' ? 'Déroulé de votre journée' : 'Your day timeline'} />
                  <DayTimelineSectionV4
                    timeWindows={prediction.time_windows}
                    lang={pLang}
                    hideTitle
                  />
                </div>
              )}
            </SectionErrorBoundary>
          )}

          {/* Zone 5 : TurningPointCard (V4) */}
          {isLocked ? (
            <div className="daily-layout__section">
              <SectionHeading title={pLang === 'fr' ? 'Moment clé' : 'Key moment'} />
              <LockedSection cta={lockedSectionCta} label={getHoroscopeTeaser('turningPoint', pLang)}>
                <LockedHoroscopeTeaser teaserKey="turningPoint" lang={pLang} />
              </LockedSection>
            </div>
          ) : (
            (() => {
              const tp = mapTurningPoint(prediction);
              return tp ? (
                <div className="daily-layout__section">
                  <SectionHeading title={pLang === 'fr' ? 'Moment clé' : 'Key moment'} />
                  <TurningPointCard turningPoint={tp} lang={pLang} />
                </div>
              ) : null;
            })()
          )}

          {/* Zone 6 : BestWindowCard (V4) */}
          {isLocked ? (
            <div className="daily-layout__section">
              <SectionHeading title={pLang === 'fr' ? 'Opportunité' : 'Opportunity'} />
              <LockedSection cta={lockedSectionCta} label={getHoroscopeTeaser('bestWindow', pLang)}>
                <LockedHoroscopeTeaser teaserKey="bestWindow" lang={pLang} />
              </LockedSection>
            </div>
          ) : (
            (() => {
              const bw = mapBestWindow(prediction);
              return bw ? (
                <div className="daily-layout__section">
                  <SectionHeading title={pLang === 'fr' ? 'Opportunité' : 'Opportunity'} />
                  <BestWindowCard bestWindow={bw} lang={pLang} />
                </div>
              ) : null;
            })()
          )}

          {/* Zone 7 : AstroDailyEvents (Story 60.13) — Analytical Card */}
          {(() => {
            const astroEvents = mapAstroDailyEvents(prediction);
            return astroEvents ? (
              <div className="daily-layout__section">
                <SectionHeading title={pLang === 'fr' ? 'Astrologie du jour' : 'Astrology of the day'} />
                <AstroDailyEvents 
                  data={astroEvents} 
                  intro={prediction.astro_events_intro} 
                  lang={pLang}
                  hideTitle
                />
              </div>
            ) : null;
          })()}

          {/* Zone 8 : DailyAdviceCard — Conclusive Masterpiece */}
          {isLocked ? (
            <div className="daily-layout__section">
              <SectionHeading title={pLang === 'fr' ? 'Conseil du jour' : 'Daily advice'} />
              <LockedSection cta={lockedSectionCta} label={getHoroscopeTeaser('dailyAdvice', pLang)}>
                <LockedHoroscopeTeaser teaserKey="dailyAdvice" lang={pLang} />
              </LockedSection>
            </div>
          ) : (
            <div className="daily-layout__section">
              <SectionHeading title={pLang === 'fr' ? 'Conseil du jour' : 'Daily advice'} />
              <DailyAdviceCard model={buildDailyAdviceCardModel(prediction, pLang)} hideTitle />
            </div>
          )}

          {/* Zone 9 : AstroFoundationSection (V4) */}
          {isLocked ? (
            <div className="daily-layout__section">
              <SectionHeading title={pLang === 'fr' ? 'Fondements astrologiques' : 'Astrological foundations'} />
              <LockedSection cta={lockedSectionCta} label={getHoroscopeTeaser('astroFoundation', pLang)}>
                <LockedHoroscopeTeaser teaserKey="astroFoundation" lang={pLang} />
              </LockedSection>
            </div>
          ) : (
            (() => {
              const foundation = mapAstroFoundation(prediction)
              return foundation ? (
                <div className="daily-layout__section">
                  <SectionHeading title={pLang === 'fr' ? 'Fondements astrologiques' : 'Astrological foundations'} />
                  <AstroFoundationSection
                    foundation={foundation}
                    lang={pLang}
                    hideTitle
                  />
                </div>
              ) : null
            })()
          )}

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
