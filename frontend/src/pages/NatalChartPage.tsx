import { PageLayout } from "../layouts"
import { ErrorState } from "@ui"
import { useEffect, useState } from "react"
import { useNavigate, Link, useSearchParams } from "react-router-dom"
import { RefreshCw, ChevronLeft } from "lucide-react"
import { ApiError, useLatestNatalChart } from "@api"
import { generateNatalChart } from "../api/natalChart"
import { useAstrologyLabels, DEGRADED_MODE_MESSAGES } from "../i18n/astrology"
import { natalChartTranslations } from "../i18n/natalChart"
import { logSupportRequestId } from "../utils/constants"
import { formatDateTime } from "../utils/formatDate"
import { useAccessTokenSnapshot } from "../utils/authToken"
import { useFeatureAccess } from "../hooks/useEntitlementSnapshot"
import { NatalChartGuide } from "../components/NatalChartGuide"
import { NatalInterpretationSection } from "../components/NatalInterpretation"
import { getZodiacIcon } from "../components/zodiacSignIconMap"
import "./NatalChartPage.css"
import "../components/prediction/DailyPageHeader.css"

function shouldLogSupportForApiError(error: ApiError): boolean {
  return error.status >= 500
}

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
  const [generateError, setGenerateError] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [activeInterpretation, setActiveInterpretation] = useState<{
    level: "short" | "complete";
    personaName: string | null;
  }>({ level: "short", personaName: null })
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
  const sunSignName = astroProfile?.sun_sign_code ? translateSign(astroProfile.sun_sign_code.toUpperCase()) : null
  const ascendantSignName = astroProfile?.ascendant_sign_code ? translateSign(astroProfile.ascendant_sign_code.toUpperCase()) : null
  const missingBirthTime = astroProfile?.missing_birth_time ?? false
  const SunSignIcon = getZodiacIcon(astroProfile?.sun_sign_code)
  const AscendantSignIcon = getZodiacIcon(astroProfile?.ascendant_sign_code)
  const pageTitle =
    !isLockedFree && activeInterpretation.level === "complete" ? t.completeTitle : t.basicTitle
  const headerActionLabel =
    isLockedFree
      ? t.interpretation.upgradeToBasicCta
      : isLongQuotaExhausted
      ? t.interpretation.quotaExhaustedCta
      : activeInterpretation.level === "complete"
      ? t.requestAnotherAstrologer
      : t.unlockCompleteInterpretation
  const sortedHouses = [...houses].sort((a, b) => a.number - b.number)
  const fallbackEvidence = Array.from(
    new Set([
      astroProfile?.sun_sign_code ? `SUN_${astroProfile.sun_sign_code.toUpperCase()}` : null,
      astroProfile?.ascendant_sign_code ? `ASC_${astroProfile.ascendant_sign_code.toUpperCase()}` : null,
      ...planetPositions
        .slice(0, 6)
        .map((item) => `${item.planet_code.toUpperCase()}_${item.sign_code.toUpperCase()}_H${item.house_number}`),
      ...aspects
        .slice(0, 4)
        .map((item) => `ASPECT_${item.planet_a.toUpperCase()}_${item.planet_b.toUpperCase()}_${item.aspect_code.toUpperCase()}`),
    ].filter(Boolean) as string[]),
  )
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
                  if (isLongQuotaExhausted) {
                    navigate("/settings/subscription")
                    return
                  }
                  setHeaderActionRequest({
                    kind:
                      !isLockedFree && activeInterpretation.level === "complete"
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

      {astroProfile && (
        <article className="natal-card natal-astro-summary">
          <h2>{t.astroProfile.title}</h2>
          <dl className="natal-astro-summary__list">
            <div className="natal-astro-summary__item">
              <dt>{t.astroProfile.sunSign}</dt>
              <dd>
                {SunSignIcon ? <SunSignIcon className="natal-astro-summary__icon" aria-hidden="true" /> : null}
                <span>{sunSignName ?? "—"}</span>
              </dd>
            </div>
            <div className="natal-astro-summary__item">
              <dt>{t.astroProfile.ascendant}</dt>
              <dd>
                {AscendantSignIcon ? <AscendantSignIcon className="natal-astro-summary__icon" aria-hidden="true" /> : null}
                <span>
                  {ascendantSignName ?? (
                    missingBirthTime
                      ? `— (${t.astroProfile.missingTime})`
                      : "—"
                  )}
                </span>
              </dd>
            </div>
          </dl>
        </article>
      )}

      <div className="natal-grid">
        <article className="natal-card">
          <h2>{t.sections.planets}</h2>
          <p className="natal-card__intro">{t.planetsLead}</p>
          <ul className="natal-data-list">
            {planetPositions.map((item) => {
              const houseInterval = getHouseIntervalLabel(item.house_number)
              const planetLabel = `${translatePlanet(item.planet_code)}${item.is_retrograde === true ? " ℞" : ""}:`
              return (
                <li key={item.planet_code} className="natal-data-card">
                  <div className="natal-data-card__head">
                    <strong className="natal-data-card__title">{planetLabel}</strong>
                    <span className="natal-data-card__value">
                      {formatDegreeMinuteFromSignLongitude(item.longitude)}
                    </span>
                  </div>
                  <p className="natal-data-card__reading">
                    {translateSign(item.sign_code)} {formatDegreeMinuteFromSignLongitude(item.longitude)} ({item.longitude.toFixed(2)}°)
                  </p>
                  <div className="natal-data-card__meta">
                    <span className="natal-data-pill">{t.positionLabel} {item.longitude.toFixed(2)}°</span>
                    <span className="natal-data-pill">{t.houseLabel} {translateHouse(item.house_number)}</span>
                    <span className="natal-data-pill">{t.longitudeLabel} {item.longitude.toFixed(2)}°</span>
                  </div>
                  {houseInterval ? (
                    <p className="natal-data-card__support">
                      {translateHouse(item.house_number)} {houseInterval}
                    </p>
                  ) : null}
                </li>
              )
            })}
          </ul>
        </article>

        <article className="natal-card">
          <h2>{t.sections.houses}</h2>
          <p className="natal-card__intro">{t.housesLead}</p>
          <ul className="natal-data-list">
            {sortedHouses.map((item) => (
              <li key={item.number} className="natal-data-card natal-data-card--house">
                <div className="natal-data-card__head">
                  <strong className="natal-data-card__title">{translateHouse(item.number)}</strong>
                  <span className="natal-data-card__value">
                    {translateSign(getSignCodeFromLongitude(item.cusp_longitude))} {formatDegreeMinuteFromSignLongitude(item.cusp_longitude)}
                  </span>
                </div>
                <div className="natal-data-card__meta">
                  <span className="natal-data-pill">{t.cuspLongitudeLabel} {item.cusp_longitude.toFixed(2)}°</span>
                  <span className="natal-data-pill">{t.houseSignLabel} {translateSign(getSignCodeFromLongitude(item.cusp_longitude))}</span>
                </div>
              </li>
            ))}
          </ul>
        </article>
      </div>

      <article className="natal-card natal-aspects-card">
        <h2>{t.sections.aspects}</h2>
        <p className="natal-card__intro">{t.aspectsLead}</p>
        {aspects.length === 0 ? (
          <p>{t.noAspects}</p>
        ) : (
          <ul className="natal-aspects-list">
            {aspects.map((item, index) => (
              <li key={`${item.aspect_code}-${item.planet_a}-${item.planet_b}-${index}`} className="natal-aspect-item">
                <div className="natal-aspect-item__head">
                  <span className="natal-aspect-badge">{translateAspect(item.aspect_code)}</span>
                  <h3 className="natal-aspect-title">
                    {translatePlanet(item.planet_a)} — {translatePlanet(item.planet_b)}
                  </h3>
                </div>
                <p className="natal-aspect-meaning">
                  {t.aspectMeaningMap[item.aspect_code] ?? t.aspectMeaningMap.CONJUNCTION}
                </p>
                <dl className="natal-aspect-meta">
                  <div className="natal-aspect-meta__item">
                    <dt>{t.aspectExactAngleLabel}</dt>
                    <dd>{item.angle.toFixed(2)}°</dd>
                </div>
                <div className="natal-aspect-meta__item">
                  <dt>{t.orb}</dt>
                  <dd>{t.orb} {item.orb.toFixed(2)}°</dd>
                </div>
                {typeof item.orb_used === "number" ? (
                  <div className="natal-aspect-meta__item">
                    <dt>{t.orbUsed}</dt>
                    <dd>{t.orbUsed} {item.orb_used.toFixed(2)}°</dd>
                  </div>
                ) : null}
              </dl>
              </li>
            ))}
          </ul>
        )}
      </article>

      <NatalChartGuide lang={lang} missingBirthTime={missingBirthTime} />
      
      <div className="natal-interpretation-container">
        <NatalInterpretationSection
          chartLoaded={Boolean(chart)}
          chartId={chart.chart_id}
          lang={lang}
          fallbackEvidence={fallbackEvidence}
          initialPersonaId={initialPersonaId}
          initialInterpretationId={initialInterpretationId}
          isLockedFree={isLockedFree}
          longFeatureAccess={natalAccess}
          onActiveInterpretationChange={setActiveInterpretation}
          actionRequest={headerActionRequest}
        />
      </div>
    </PageLayout>
  )
}

