import { PageLayout } from "../layouts"
import { ErrorState } from "@ui"
import { useEffect, useState } from "react"
import { useNavigate, Link, useSearchParams } from "react-router-dom"
import { RefreshCw, ChevronLeft } from "lucide-react"
import { ApiError, useLatestNatalChart } from "@api"
import { generateNatalChart } from "../api/natalChart"
import { useAstrologyLabels, DEGRADED_MODE_MESSAGES } from "../i18n/astrology"
import { natalChartTranslations } from "../i18n/natalChart"
import { shouldLogSupportForApiError } from "../utils/apiErrorSupport"
import { logSupportRequestId } from "../utils/constants"
import { formatDateTime } from "../utils/formatDate"
import { useAccessTokenSnapshot } from "../utils/authToken"
import { useFeatureAccess } from "../hooks/useEntitlementSnapshot"
import { NatalChartGuide } from "../components/NatalChartGuide"
import { NatalExpertPanel } from "../features/natal-chart/NatalExpertPanel"
import { NatalProfileHero } from "../features/natal-chart/NatalProfileHero"
import { NatalThemeSynthesis } from "../features/natal-chart/NatalThemeSynthesis"
import { NatalAstrologerMode } from "../features/natal-chart/NatalAstrologerMode"
import { NatalTechnicalDetails } from "../features/natal-chart/NatalTechnicalDetails"
import "./NatalChartPage.css"
import "../components/prediction/DailyPageHeader.css"

function normalize360(value: number): number {
  const normalized = value % 360
  return normalized >= 0 ? normalized : normalized + 360
}

function formatDegreeMinuteFromSignLongitude(value: number): string {
  const signLongitude = normalize360(value) % 30
  const degrees = Math.floor(signLongitude)
  const minutes = Math.round((signLongitude - degrees) * 60)
  const normalizedMinutes = minutes === 60 ? 59 : minutes
  const normalizedDegrees = degrees
  return `${normalizedDegrees}°${String(normalizedMinutes).padStart(2, "0")}′`
}

const SIGN_CODES = [
  "ARIES",
  "TAURUS",
  "GEMINI",
  "CANCER",
  "LEO",
  "VIRGO",
  "LIBRA",
  "SCORPIO",
  "SAGITTARIUS",
  "CAPRICORN",
  "AQUARIUS",
  "PISCES",
] as const

function getSignCodeFromLongitude(value: number): string {
  const normalized = normalize360(value)
  return SIGN_CODES[Math.floor(normalized / 30)] ?? "ARIES"
}

export function NatalChartPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const accessToken = useAccessTokenSnapshot()
  const latestChart = useLatestNatalChart()
  const { lang, translatePlanet, translateSign, translateHouse, translateAspect } = useAstrologyLabels()
  const t = natalChartTranslations[lang]
  const placementIn = lang === "en" || lang === "de" ? " in " : " en "
  const publicLabels = { translatePlanet, translateSign, translateHouse, placementIn }
  const [generateError, setGenerateError] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [activeInterpretation, setActiveInterpretation] = useState<{
    level: "short" | "complete";
    personaName: string | null;
    canSwitchPersona: boolean;
    isBasicCompleteLimitReached: boolean;
  }>({ level: "short", personaName: null, canSwitchPersona: false, isBasicCompleteLimitReached: false })
  const [headerActionRequest, setHeaderActionRequest] = useState<{
    kind: "upgrade" | "switch_persona";
    nonce: number;
  } | null>(null)

  const error = latestChart.error
  const apiError = error instanceof ApiError ? error : null
  const natalAccess = useFeatureAccess("natal_chart_long")
  const isLockedFree = natalAccess?.variant_code === "free_short"
  const hasSingleAstrologerQuota = natalAccess?.variant_code === "single_astrologer"
  const isLongQuotaExhausted = Boolean(
    !isLockedFree &&
      (
        activeInterpretation.isBasicCompleteLimitReached ||
        natalAccess?.reason_code === "quota_exhausted" ||
        natalAccess?.usage_states?.some((state) => state.exhausted || state.remaining <= 0)
      ),
  )

  async function handleGenerateChart() {
    if (!accessToken || isGenerating) return
    setIsGenerating(true)
    setGenerateError(null)
    try {
      await generateNatalChart(accessToken, true)
      await latestChart.refetch?.()
    } catch (err) {
      if (err instanceof ApiError && shouldLogSupportForApiError(err)) {
        logSupportRequestId(err)
      }
      setGenerateError(t.generateError)
    } finally {
      setIsGenerating(false)
    }
  }

  useEffect(() => {
    if (latestChart.isError && apiError && shouldLogSupportForApiError(apiError)) {
      logSupportRequestId(apiError)
    }
  }, [latestChart.isError, apiError])

  if (latestChart.isLoading) {
    return (
      <PageLayout className="natal-page-container is-natal-page" aria-busy="true">
        <div className="natal-page-container__bg-halo" />
        <div className="natal-page-container__noise" />
        <header className="natal-page-header">
          <span className="natal-page-header__meta">{t.title}</span>
          <h1 className="natal-page-header__title">{t.loading}</h1>
        </header>
        <div className="natal-card">
          <div className="ni-loader-container">
            <RefreshCw size={32} className="ni-loader-spin" />
          </div>
        </div>
      </PageLayout>
    )
  }

  if (latestChart.isError) {
    if (apiError?.code === "natal_chart_not_found") {
      return (
        <PageLayout className="natal-page-container is-natal-page">
          <div className="natal-page-container__bg-halo" />
          <div className="natal-page-container__noise" />
          <header className="natal-page-header">
            <span className="natal-page-header__meta">{t.title}</span>
            <h1 className="natal-page-header__title">{t.notFound}</h1>
          </header>
          <div className="natal-card">
            <p className="natal-card__lead">{t.notFoundSub}</p>
            {generateError ? (
              <div className="chat-error natal-card__error" role="alert">
                <p>{generateError}</p>
              </div>
            ) : null}
            <div className="natal-card__actions">
              <button
                type="button"
                onClick={() => void handleGenerateChart()}
                disabled={isGenerating}
                aria-busy={isGenerating}
                className="ni-action-btn ni-action-btn--regenerate"
              >
                {isGenerating ? t.generating : t.generateNow}
              </button>
              <Link to="/profile" className="btn-link natal-card__secondary-link">
                {t.completeProfile}
              </Link>
            </div>
          </div>
        </PageLayout>
      )
    }

    if (
      apiError?.code === "birth_profile_not_found" ||
      apiError?.code === "unprocessable_entity" ||
      apiError?.status === 422
    ) {
      return (
        <PageLayout className="natal-page-container is-natal-page">
          <div className="natal-page-container__bg-halo" />
          <div className="natal-page-container__noise" />
          <header className="natal-page-header">
            <span className="natal-page-header__meta">{t.title}</span>
            <h1 className="natal-page-header__title">{t.incompleteData}</h1>
          </header>
          <div className="natal-card">
            <div className="chat-error degraded-warning natal-page__inline-alert" role="alert">
              <p>{t.incompleteDataSub}</p>
            </div>
            <Link to="/profile" className="btn-link complete-profile-link natal-card__complete-link">
              {t.completeProfile}
            </Link>
          </div>
        </PageLayout>
      )
    }

    return (
      <PageLayout className="natal-page-container is-natal-page">
        <div className="natal-page-container__bg-halo" />
        <div className="natal-page-container__noise" />
        <ErrorState 
          title={t.title}
          message={t.genericError}
          onRetry={() => void latestChart.refetch()}
        />
      </PageLayout>
    )
  }

  const chart = latestChart.data
  if (!chart) {
    return (
      <PageLayout className="natal-page-container is-natal-page">
        <div className="natal-page-container__bg-halo" />
        <div className="natal-page-container__noise" />
        <header className="natal-page-header">
          <h1 className="natal-page-header__title">{t.title}</h1>
        </header>
        <div className="natal-card">
          <p>{t.noData}</p>
        </div>
      </PageLayout>
    )
  }

  const planetPositions = chart.result.planet_positions ?? []
  const houses = chart.result.houses ?? []
  const aspects = chart.result.aspects ?? []
  const housesByNumber = new Map(houses.map((house) => [house.number, house]))

  function getHouseIntervalLabel(houseNumber: number): string | null {
    const current = housesByNumber.get(houseNumber)
    const next = housesByNumber.get(houseNumber === 12 ? 1 : houseNumber + 1)
    if (!current || !next) return null
    const start = current.cusp_longitude
    const end = next.cusp_longitude
    if (end < start) {
      return `${start.toFixed(2)}° -> 360° ${t.wrapConnector} -> ${end.toFixed(2)}°`
    }
    return `${start.toFixed(2)}° -> ${end.toFixed(2)}°`
  }

  const astroProfile = chart.astro_profile
  const houseSystemKey = chart.metadata.house_system
  const houseSystemLabel =
    houseSystemKey === "equal"
      ? t.equalHouseSystem
      : houseSystemKey === "placidus"
        ? t.placidusHouseSystem
        : houseSystemKey === "koch"
          ? t.kochHouseSystem
          : houseSystemKey === "regiomontanus"
            ? t.regiomontanusHouseSystem
          : houseSystemKey
  const missingBirthTime = astroProfile?.missing_birth_time ?? false
  const pageTitle =
    !isLockedFree && activeInterpretation.level === "complete" ? t.completeTitle : t.astroProfile.title
  const headerActionLabel =
    isLockedFree
      ? t.interpretation.upgradeToBasicCta
      : isLongQuotaExhausted
      ? t.interpretation.quotaExhaustedCta
      : activeInterpretation.canSwitchPersona
      ? t.requestAnotherAstrologer
      : t.unlockCompleteInterpretation
  const interpretationIdParam = searchParams.get("interpretationId")
  const parsedInterpretationId = interpretationIdParam
    ? Number.parseInt(interpretationIdParam, 10)
    : null
  const initialInterpretationId =
    parsedInterpretationId !== null && !Number.isNaN(parsedInterpretationId)
      ? parsedInterpretationId
      : null
  const initialPersonaId = searchParams.get("personaId")

  return (
    <PageLayout className="natal-page-container is-natal-page">
      {/* Decorative Halos and Noise (Story 60.20) */}
      <div className="natal-page-container__bg-halo" />
      <div className="natal-page-container__noise" />

      <header className="natal-page-header">
        <div className="natal-page-header__top">
          <button 
            className="daily-page-header__back" 
            onClick={() => navigate('/dashboard')}
            aria-label={t.backToDashboard}
          >
            <ChevronLeft size={18} strokeWidth={2.4} />
          </button>
          <div className="natal-page-header__main">
            <span className="natal-page-header__meta">{t.title}</span>
            <h1 className="natal-page-header__title">
              {pageTitle}
            </h1>
            <div className="natal-page-header__actions">
              {activeInterpretation.level === "complete" && activeInterpretation.personaName ? (
                <p className="natal-page-header__persona">
                  {t.interpretedByLabel} <strong>{activeInterpretation.personaName}</strong>
                </p>
              ) : null}
              <button
                type="button"
                className="natal-page-header__cta"
                onClick={() => {
                  if (isLockedFree) {
                    navigate("/settings/subscription")
                    return
                  }
                  setHeaderActionRequest({
                    kind:
                      !isLockedFree && activeInterpretation.canSwitchPersona
                        ? "switch_persona"
                        : "upgrade",
                    nonce: Date.now(),
                  })
                }}
              >
                {headerActionLabel}
              </button>
            </div>
          </div>
        </div>
        <div className="natal-page-header__info">
          <span>{t.generatedOn} {formatDateTime(chart.created_at)}</span>
          <span>·</span>
          <span>{chart.metadata.reference_version}</span>
          {houseSystemLabel && (
            <>
              <span>·</span>
              <span>{t.houseSystem} {houseSystemLabel}</span>
            </>
          )}
        </div>
      </header>

        {(chart.metadata.degraded_mode === "no_location" ||
          chart.metadata.degraded_mode === "no_location_no_time") && (
        <div className="chat-error degraded-warning natal-page__degraded-warning" role="alert">
          ⚠ {DEGRADED_MODE_MESSAGES.no_location[lang]}
        </div>
      )}
      {(chart.metadata.degraded_mode === "no_time" ||
        chart.metadata.degraded_mode === "no_location_no_time") && (
        <div className="chat-error degraded-warning natal-page__degraded-warning" role="alert">
          ⚠ {DEGRADED_MODE_MESSAGES.no_time[lang]}
        </div>
      )}

      <NatalProfileHero chart={chart} labels={publicLabels} lang={lang} />
      <NatalThemeSynthesis
        chartId={chart.chart_id}
        lang={lang}
        initialPersonaId={initialPersonaId}
        initialInterpretationId={initialInterpretationId}
        isLockedFree={isLockedFree}
        longFeatureAccess={natalAccess}
        onActiveInterpretationChange={setActiveInterpretation}
        actionRequest={headerActionRequest}
      />
      <NatalAstrologerMode access={natalAccess} lang={lang}>
        <NatalTechnicalDetails
          planetPositions={planetPositions}
          houses={houses}
          aspects={aspects}
          translatePlanet={translatePlanet}
          translateSign={translateSign}
          translateHouse={translateHouse}
          translateAspect={translateAspect}
          getHouseIntervalLabel={getHouseIntervalLabel}
          formatDegreeMinuteFromSignLongitude={formatDegreeMinuteFromSignLongitude}
          getSignCodeFromLongitude={getSignCodeFromLongitude}
          t={t}
        />
        <NatalExpertPanel chart={chart} />
      </NatalAstrologerMode>
      <NatalChartGuide lang={lang} missingBirthTime={missingBirthTime} />
    </PageLayout>
  )
}

