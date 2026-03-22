import { PageLayout } from "../layouts"
import { ErrorState } from "@ui"
import { useEffect, useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { RefreshCw, ChevronLeft } from "lucide-react"
import { ApiError, useLatestNatalChart } from "@api"
import { generateNatalChart } from "../api/natalChart"
import { useAstrologyLabels, DEGRADED_MODE_MESSAGES } from "../i18n/astrology"
import { natalChartTranslations } from "../i18n/natalChart"
import { logSupportRequestId } from "../utils/constants"
import { formatDateTime } from "../utils/formatDate"
import { useAccessTokenSnapshot } from "../utils/authToken"
import { NatalChartGuide } from "../components/NatalChartGuide"
import { NatalInterpretationSection } from "../components/NatalInterpretation"
import "./NatalChartPage.css"

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

export function NatalChartPage() {
  const navigate = useNavigate()
  const accessToken = useAccessTokenSnapshot()
  const latestChart = useLatestNatalChart()
  const { lang, translatePlanet, translateSign, translateHouse, translateAspect } = useAstrologyLabels()
  const t = natalChartTranslations[lang]
  const [generateError, setGenerateError] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const error = latestChart.error
  const apiError = error instanceof ApiError ? error : null

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
            <p style={{ marginBottom: '24px', opacity: 0.8 }}>{t.notFoundSub}</p>
            {generateError ? (
              <div className="chat-error" role="alert" style={{ marginBottom: '24px' }}>
                <p>{generateError}</p>
              </div>
            ) : null}
            <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
              <button
                type="button"
                onClick={() => void handleGenerateChart()}
                disabled={isGenerating}
                aria-busy={isGenerating}
                className="ni-action-btn ni-action-btn--regenerate"
                style={{ height: '44px', padding: '0 24px' }}
              >
                {isGenerating ? t.generating : t.generateNow}
              </button>
              <Link to="/profile" className="btn-link" style={{ fontSize: '14px', fontWeight: 600 }}>
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
            <div className="chat-error degraded-warning" role="alert" style={{ border: 'none', background: 'none', padding: 0 }}>
              <p>{t.incompleteDataSub}</p>
            </div>
            <Link to="/profile" className="btn-link complete-profile-link" style={{ marginTop: '24px', display: 'inline-block' }}>
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
  const sunSignName = astroProfile?.sun_sign_code ? translateSign(astroProfile.sun_sign_code) : null
  const ascendantSignName = astroProfile?.ascendant_sign_code ? translateSign(astroProfile.ascendant_sign_code) : null
  const missingBirthTime = astroProfile?.missing_birth_time ?? false

  return (
    <PageLayout className="natal-page-container is-natal-page">
      {/* Decorative Halos and Noise (Story 60.20) */}
      <div className="natal-page-container__bg-halo" />
      <div className="natal-page-container__noise" />

      <header className="natal-page-header">
        <div className="natal-page-header__top" style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '8px' }}>
          <button 
            className="daily-page-header__back" 
            onClick={() => navigate('/dashboard')}
            aria-label="Retour au dashboard"
          >
            <ChevronLeft size={18} strokeWidth={2.4} />
          </button>
          <div className="natal-page-header__main">
            <span className="natal-page-header__meta">{t.title}</span>
            <h1 className="natal-page-header__title">
              {astroProfile?.sun_sign_code ? translateSign(astroProfile.sun_sign_code) : t.title}
            </h1>
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
        <div className="chat-error degraded-warning" role="alert" style={{ marginBottom: '24px' }}>
          ⚠ {DEGRADED_MODE_MESSAGES.no_location[lang]}
        </div>
      )}
      {(chart.metadata.degraded_mode === "no_time" ||
        chart.metadata.degraded_mode === "no_location_no_time") && (
        <div className="chat-error degraded-warning" role="alert" style={{ marginBottom: '24px' }}>
          ⚠ {DEGRADED_MODE_MESSAGES.no_time[lang]}
        </div>
      )}

      {astroProfile && (
        <article className="natal-card natal-astro-summary">
          <h2>{t.astroProfile.title}</h2>
          <dl className="natal-astro-summary__list">
            <div className="natal-astro-summary__item">
              <dt>{t.astroProfile.sunSign}</dt>
              <dd>{sunSignName ?? "—"}</dd>
            </div>
            <div className="natal-astro-summary__item">
              <dt>{t.astroProfile.ascendant}</dt>
              <dd>
                {ascendantSignName ?? (
                  missingBirthTime
                    ? `— (${t.astroProfile.missingTime})`
                    : "—"
                )}
              </dd>
            </div>
          </dl>
        </article>
      )}

      <div className="natal-grid">
        <article className="natal-card">
          <h2>{t.sections.planets}</h2>
          <ul>
            {planetPositions.map((item) => {
              const houseInterval = getHouseIntervalLabel(item.house_number)
              return (
                <li key={item.planet_code}>
                  <strong>{translatePlanet(item.planet_code)}</strong>
                  {item.is_retrograde === true ? " ℞" : ""}: {translateSign(item.sign_code)}{" "}
                  {formatDegreeMinuteFromSignLongitude(item.longitude)} ({item.longitude.toFixed(2)}°),{" "}
                  {translateHouse(item.house_number)}
                  {houseInterval ? <div className="natal-house-interval">{houseInterval}</div> : ""}
                </li>
              )
            })}
          </ul>
        </article>

        <article className="natal-card">
          <h2>{t.sections.houses}</h2>
          <ul>
            {houses.map((item) => (
              <li key={item.number}>
                <strong>{translateHouse(item.number)}</strong>: {t.cuspide} {item.cusp_longitude.toFixed(2)}°
              </li>
            ))}
          </ul>
        </article>
      </div>

      <article className="natal-card natal-aspects-card">
        <h2>{t.sections.aspects}</h2>
        {aspects.length === 0 ? (
          <p>{t.noAspects}</p>
        ) : (
          <ul className="natal-aspects-list">
            {aspects.map((item, index) => (
              <li key={`${item.aspect_code}-${item.planet_a}-${item.planet_b}-${index}`} className="natal-aspect-item">
                <div className="natal-aspect-header">
                  <strong>{translateAspect(item.aspect_code)}</strong>
                  <span className="natal-aspect-orb">{item.orb.toFixed(1)}°</span>
                </div>
                <div className="natal-aspect-planets">
                  {translatePlanet(item.planet_a)} — {translatePlanet(item.planet_b)}
                </div>
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
        />
      </div>
    </PageLayout>
  )
}

