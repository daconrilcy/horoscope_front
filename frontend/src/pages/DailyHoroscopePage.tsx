import { useNavigate } from 'react-router-dom'
import { PageLayout } from '../layouts'
import { useEffect, useRef } from 'react'
import { RefreshCw } from 'lucide-react'

import { TodayHeader } from '../components/TodayHeader'
import { HeroSummaryCard } from '../components/prediction/HeroSummaryCard'
import { CategoryGrid } from '../components/prediction/CategoryGrid'
import { TurningPointsList } from '../components/prediction/TurningPointsList'
import { DayAgenda } from '../components/prediction/DayAgenda'
import { KeyPointsSection } from '../components/prediction/KeyPointsSection'
import { DailyPageHeader } from '../components/prediction/DailyPageHeader'
import type { DailyPredictionTurningPoint } from '../types/dailyPrediction'

import { detectLang } from '../i18n/astrology'
import { buildDailyAgendaSlots, buildDailyKeyMoments } from '../utils/dailyAstrology'
import { getPredictionMessage, getToneLabel, getToneColor, getCategoryLabel } from '../utils/predictionI18n'
import { getLocale } from '../utils/locale'
import { useAccessTokenSnapshot } from '../utils/authToken'
import { useAuthMe } from '../api/authMe'
import { useDailyPrediction } from '../api/useDailyPrediction'
import { trackEvent, EVENTS } from '../utils/analytics'
import { useDashboardAstroSummary } from '../components/dashboard/useDashboardAstroSummary'
import { SectionErrorBoundary } from '../components/ErrorBoundary'
import { buildHeroSummaryCardModel } from '../utils/heroSummaryCardMapper'
import { buildKeyPointsSectionModel } from '../utils/keyPointsSectionMapper'
import './DailyHoroscopePage.css'

function parseLocalMinute(iso: string): number | null {
  const match = iso.match(/T(\d{2}):(\d{2})/)
  if (!match) {
    return null
  }

  return Number(match[1]) * 60 + Number(match[2])
}

function categoriesEqual(left: string[], right: string[]): boolean {
  return left.length === right.length && left.every((category, index) => category === right[index])
}

function isSubset(subset: string[], superset: string[]): boolean {
  return subset.every((category) => superset.includes(category))
}

function deriveChangeType(previousCategories: string[], nextCategories: string[]): string | undefined {
  if (previousCategories.length === 0 && nextCategories.length > 0) {
    return 'emergence'
  }

  if (previousCategories.length > 0 && nextCategories.length === 0) {
    return 'attenuation'
  }

  if (categoriesEqual(previousCategories, nextCategories)) {
    return undefined
  }

  if (
    previousCategories.length > 0 &&
    nextCategories.length > previousCategories.length &&
    isSubset(previousCategories, nextCategories)
  ) {
    return 'emergence'
  }

  if (
    nextCategories.length > 0 &&
    previousCategories.length > nextCategories.length &&
    isSubset(nextCategories, previousCategories)
  ) {
    return 'attenuation'
  }

  return 'recomposition'
}

function formatTime(iso: string, locale: string) {
  return new Date(iso).toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' })
}

export function DailyHoroscopePage() {
  const navigate = useNavigate()
  const accessToken = useAccessTokenSnapshot()
  const detected = detectLang()
  const lang = (detected === 'en' ? 'en' : 'fr') as any
  const manualRefreshPending = useRef(false)
  const bootstrapPredictionRefetchDoneForToken = useRef<string | null>(null)

  const { data: user, isLoading: isUserLoading, isError: isUserError, refetch: refetchUser } = useAuthMe(accessToken)

  const { 
    data: prediction, 
    isLoading: isPredictionLoading, 
    isError: isPredictionError,
    refetch: refetchPrediction
  } = useDailyPrediction(accessToken)

  const { sign, dayScore } = useDashboardAstroSummary(accessToken)

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

  const handleCategoryClick = (categoryCode: string) => {
    trackEvent(EVENTS.CATEGORY_CLICKED, { category_code: categoryCode })
  }

  const handleTurningPointClick = (severity: number) => {
    const severityCode = severity > 0.75 ? 'critical' : severity > 0.5 ? 'high' : severity > 0.25 ? 'medium' : 'low'
    trackEvent(EVENTS.TURNING_POINT_OPENED, { severity: severityCode })
  }

  const normalizedApiMoments: DailyPredictionTurningPoint[] = prediction
    ? prediction.turning_points.map((moment) => {
        const occurredMinute = parseLocalMinute(moment.occurred_at_local)
        const timelineBlocks = prediction.timeline
        const currentIndex = occurredMinute === null
          ? -1
          : timelineBlocks.findIndex((block) => {
              const startMinute = parseLocalMinute(block.start_local)
              const endMinute = parseLocalMinute(block.end_local)
              if (startMinute === null || endMinute === null) {
                return false
              }

              return occurredMinute >= startMinute && occurredMinute < endMinute
            })

        const previousCategories =
          moment.previous_categories && moment.previous_categories.length > 0
            ? moment.previous_categories
            : currentIndex > 0
              ? timelineBlocks[currentIndex - 1].dominant_categories
              : []

        const nextCategories =
          moment.next_categories && moment.next_categories.length > 0
            ? moment.next_categories
            : currentIndex >= 0
              ? timelineBlocks[currentIndex].dominant_categories
              : []

        const impactedCategories =
          moment.impacted_categories && moment.impacted_categories.length > 0
            ? moment.impacted_categories
            : nextCategories.length > 0
              ? nextCategories
              : previousCategories

        const inferredNextCategories =
          !moment.next_categories?.length &&
          categoriesEqual(previousCategories, nextCategories) &&
          impactedCategories.length > 0 &&
          !categoriesEqual(previousCategories, impactedCategories)
            ? impactedCategories
            : nextCategories

        const resolvedChangeType = moment.change_type || deriveChangeType(previousCategories, inferredNextCategories)
        const hasResolvedTransition = !!resolvedChangeType

        return {
          ...moment,
          impacted_categories: impactedCategories,
          previous_categories: hasResolvedTransition ? previousCategories : moment.previous_categories,
          next_categories: hasResolvedTransition ? inferredNextCategories : moment.next_categories,
          change_type: resolvedChangeType,
        }
      })
    : []

  const normalizedFallbackMoments: DailyPredictionTurningPoint[] = prediction
    ? buildDailyKeyMoments(
        prediction.meta.date_local,
        prediction.decision_windows,
        prediction.timeline,
        prediction.categories,
      ).map((moment) => ({
        occurred_at_local: moment.occurredAtLocal,
        severity: 0.5,
        summary: null,
        drivers: [],
        impacted_categories: moment.impactedCategories,
        previous_categories: moment.previousCategories,
        next_categories: moment.nextCategories,
        change_type: deriveChangeType(moment.previousCategories, moment.nextCategories) || 'recomposition',
        primary_driver: null,
      }))
    : []

  const keyMoments = prediction
    ? (prediction.turning_points?.length > 0 
        ? normalizedApiMoments 
        : normalizedFallbackMoments)
    : []

  const agendaSlots = prediction
    ? buildDailyAgendaSlots(
        prediction.meta.date_local,
        prediction.decision_windows,
        prediction.timeline,
        prediction.categories,
        keyMoments.map((moment) => ({ occurred_at_local: moment.occurred_at_local })),
      )
    : []

  const locale = getLocale(lang)

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
            tone={prediction.summary.overall_tone}
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

          {/* Zone 2 : HeroSummaryCard */}
          <SectionErrorBoundary onRetry={handleRefresh}>
            <HeroSummaryCard
              model={buildHeroSummaryCardModel(
                prediction,
                sign,
                user?.id ? String(user.id) : 'anonymous',
                dayScore,
                lang
              )}
              lang={lang}
            />
          </SectionErrorBoundary>

          {/* Zone 3 : KeyPointsSection — 3 premiers turning points */}
          <KeyPointsSection model={buildKeyPointsSectionModel(prediction, lang)} />

          {/* Zone 4 : DayTimelineSection */}
          {agendaSlots.length > 0 && (
            <section className="daily-layout__section" id="timeline">
              <h3 className="daily-layout__section-title">
                {getPredictionMessage('timeline_title', lang)}
              </h3>
              <DayAgenda slots={agendaSlots} lang={lang} />
            </section>
          )}

          {/* Zone 5 : DetailAndScoresSection (2 col sur ≥768px) */}
          <section className="daily-layout__section daily-layout__detail-scores">
            <div className="daily-layout__detail-scores-inner">
              {/* FocusMomentCard : premier turning point */}
              {keyMoments.length > 0 && (
                <div className="daily-layout__focus">
                  <h3 className="daily-layout__section-title">
                    {getPredictionMessage('focus_title', lang)}
                  </h3>
                  <TurningPointsList
                    moments={keyMoments.slice(0, 1)}
                    lang={lang}
                    onTurningPointClick={handleTurningPointClick}
                  />
                </div>
              )}
              {/* DailyDomainsCard */}
              <div className="daily-layout__domains">
                <h3 className="daily-layout__section-title">
                  {getPredictionMessage('domains_title', lang)}
                </h3>
                <CategoryGrid
                  categories={prediction.categories}
                  lang={lang}
                  onCategoryClick={handleCategoryClick}
                />
              </div>
            </div>
          </section>

          {/* Zone 6 : AdviceCard + CTA */}
          {prediction.summary.best_window && (
            <section className="daily-layout__section daily-layout__advice">
              <div className="panel daily-layout__advice-card">
                <h3 className="daily-layout__advice-title">
                  {getPredictionMessage('advice_title', lang)}
                </h3>
                <p className="daily-layout__advice-text">
                  {getPredictionMessage('best_window', lang)} ({getCategoryLabel(prediction.summary.best_window.dominant_category, lang)}) :{' '}
                  {formatTime(prediction.summary.best_window.start_local, locale)} –{' '}
                  {formatTime(prediction.summary.best_window.end_local, locale)}
                </p>
                <a
                  href="#key-points"
                  className="daily-layout__advice-cta"
                >
                  {getPredictionMessage('advice_cta', lang)}
                </a>
              </div>
            </section>
          )}

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
