import { useNavigate } from 'react-router-dom'
import { useEffect, useRef } from 'react'
import { RefreshCw } from 'lucide-react'

import { TodayHeader } from '../components/TodayHeader'
import { ShortcutsSection } from '../components/ShortcutsSection'
import { DayPredictionCard } from '../components/prediction/DayPredictionCard'
import { CategoryGrid } from '../components/prediction/CategoryGrid'
import { TurningPointsList } from '../components/prediction/TurningPointsList'
import { DayAgenda } from '../components/prediction/DayAgenda'
import type { DailyPredictionTurningPoint } from '../types/dailyPrediction'

import { detectLang } from '../i18n/astrology'
import { buildDailyAgendaSlots, buildDailyKeyMoments } from '../utils/dailyAstrology'
import { getPredictionMessage } from '../utils/predictionI18n'
import { useAccessTokenSnapshot } from '../utils/authToken'
import { useAuthMe } from '../api/authMe'
import { useDailyPrediction } from '../api/useDailyPrediction'
import { getUserDisplayName } from '../utils/user'
import { trackEvent, EVENTS } from '../utils/analytics'

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

export function TodayPage() {
  const navigate = useNavigate()
  const accessToken = useAccessTokenSnapshot()
  const detected = detectLang()
  const lang = (detected === 'en' ? 'en' : 'fr') as any
  const manualRefreshPending = useRef(false)

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
      if (manualRefreshPending.current) {
        trackEvent(EVENTS.PREDICTION_REFRESHED, { was_reused: prediction.meta.was_reused })
        manualRefreshPending.current = false
      }
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

  const handleHistoryClick = () => {
    trackEvent(EVENTS.HISTORY_VIEWED)
  }

  const agendaSlots = prediction
    ? buildDailyAgendaSlots(
        prediction.meta.date_local,
        prediction.decision_windows,
        prediction.timeline,
        prediction.categories,
      )
    : []

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

        const changeType =
          moment.change_type ||
          (
            previousCategories.length === 0 && nextCategories.length > 0
              ? 'emergence'
              : previousCategories.length > 0 && nextCategories.length === 0
                ? 'attenuation'
                : !categoriesEqual(previousCategories, nextCategories)
                  ? 'recomposition'
                  : undefined
          )

        return {
          ...moment,
          impacted_categories: impactedCategories,
          previous_categories: previousCategories,
          next_categories: nextCategories,
          change_type: changeType,
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
        change_type:
          moment.previousCategories.length === 0 && moment.nextCategories.length > 0
            ? 'emergence'
            : moment.previousCategories.length > 0 && moment.nextCategories.length === 0
              ? 'attenuation'
              : 'recomposition',
        primary_driver: null,
      }))
    : []

  const keyMoments = prediction
    ? (prediction.turning_points?.length > 0 
        ? normalizedApiMoments 
        : normalizedFallbackMoments)
    : []

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
              {getPredictionMessage('refresh', lang)}
            </button>
          </div>

          <DayPredictionCard prediction={prediction} lang={lang} />

          <TurningPointsList
            moments={keyMoments}
            lang={lang}
            onTurningPointClick={handleTurningPointClick}
          />

          <DayAgenda
            slots={agendaSlots}
            lang={lang}
          />

          <CategoryGrid
            categories={prediction.categories}
            lang={lang}
            onCategoryClick={handleCategoryClick}
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
