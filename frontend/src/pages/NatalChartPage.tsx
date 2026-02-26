import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { ApiError, useLatestNatalChart } from "../api/natalChart"
import { generateNatalChart } from "../api/natalChart"
import { useAstrologyLabels, DEGRADED_MODE_MESSAGES } from "../i18n/astrology"
import { natalChartTranslations } from "../i18n/natalChart"
import { logSupportRequestId } from "../utils/constants"
import { formatDateTime } from "../utils/formatDate"
import { useAccessTokenSnapshot } from "../utils/authToken"
import { NatalChartGuide } from "../components/NatalChartGuide"

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
      await generateNatalChart(accessToken)
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
      <section className="panel" aria-busy="true">
        <h1>{t.title}</h1>
        <p>{t.loading}</p>
      </section>
    )
  }

  if (latestChart.isError) {
    if (apiError?.code === "natal_chart_not_found") {
      return (
        <section className="panel">
          <h1>{t.title}</h1>
          <p>{t.notFound}</p>
          <p>{t.notFoundSub}</p>
          {generateError ? (
            <div className="chat-error" role="alert">
              <p>{generateError}</p>
            </div>
          ) : null}
          <button
            type="button"
            onClick={() => void handleGenerateChart()}
            disabled={isGenerating}
            aria-busy={isGenerating}
          >
            {isGenerating ? t.generating : t.generateNow}
          </button>
          <Link to="/profile" className="btn-link">
            {t.completeProfile}
          </Link>
        </section>
      )
    }

    if (
      apiError?.code === "birth_profile_not_found" ||
      apiError?.code === "unprocessable_entity" ||
      apiError?.status === 422
    ) {
      return (
        <section className="panel">
          <h1>{t.title}</h1>
          <div className="chat-error degraded-warning" role="alert">
            <p>
              <strong>{t.incompleteData}</strong>
            </p>
            <p>{t.incompleteDataSub}</p>
          </div>
          <Link to="/profile" className="btn-link complete-profile-link">
            {t.completeProfile}
          </Link>
        </section>
      )
    }

    return (
      <section className="panel">
        <h1>{t.title}</h1>
        <p>{t.genericError}</p>
        <button type="button" onClick={() => void latestChart.refetch()} className="retry-button">
          {t.retry}
        </button>
      </section>
    )
  }

  const chart = latestChart.data
  if (!chart) {
    return (
      <section className="panel">
        <h1>{t.title}</h1>
        <p>{t.noData}</p>
      </section>
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
  const houseSystemLabel =
    chart.metadata.house_system === "equal" ? t.equalHouseSystem : chart.metadata.house_system ?? null
  const sunSignName = astroProfile?.sun_sign_code ? translateSign(astroProfile.sun_sign_code) : null
  const ascendantSignName = astroProfile?.ascendant_sign_code ? translateSign(astroProfile.ascendant_sign_code) : null
  const missingBirthTime = astroProfile?.missing_birth_time ?? false

  return (
    <section className="panel">
      <h1>{t.title}</h1>
      <p>
        {t.generatedOn} {formatDateTime(chart.created_at)} · {t.referenceVersion} {chart.metadata.reference_version}
        · {t.rulesetVersion} {chart.metadata.ruleset_version}
        {houseSystemLabel ? ` · ${t.houseSystem} ${houseSystemLabel}` : ""}
      </p>

      {(chart.metadata.degraded_mode === "no_location" ||
        chart.metadata.degraded_mode === "no_location_no_time") && (
        <div className="chat-error degraded-warning" role="alert">
          ⚠ {DEGRADED_MODE_MESSAGES.no_location[lang]}
        </div>
      )}
      {(chart.metadata.degraded_mode === "no_time" ||
        chart.metadata.degraded_mode === "no_location_no_time") && (
        <div className="chat-error degraded-warning" role="alert">
          ⚠ {DEGRADED_MODE_MESSAGES.no_time[lang]}
        </div>
      )}

      {astroProfile && (
        <article className="card natal-astro-summary">
          <h2>{lang === "fr" ? "Profil astrologique" : lang === "es" ? "Perfil astrológico" : "Astro Profile"}</h2>
          <dl className="natal-astro-summary__list">
            <div className="natal-astro-summary__item">
              <dt>{lang === "fr" ? "Signe solaire" : lang === "es" ? "Signo solar" : "Sun sign"}</dt>
              <dd>{sunSignName ?? "—"}</dd>
            </div>
            <div className="natal-astro-summary__item">
              <dt>{lang === "fr" ? "Ascendant" : lang === "es" ? "Ascendente" : "Ascendant"}</dt>
              <dd>
                {ascendantSignName ?? (
                  missingBirthTime
                    ? (lang === "fr"
                        ? "— (heure de naissance manquante)"
                        : lang === "es"
                          ? "— (hora de nacimiento no disponible)"
                          : "— (birth time missing)")
                    : "—"
                )}
              </dd>
            </div>
          </dl>
        </article>
      )}

      <div className="grid">
        <article className="card">
          <h2>{t.sections.planets}</h2>
          <ul>
            {planetPositions.map((item) => {
              const houseInterval = getHouseIntervalLabel(item.house_number)
              return (
                <li key={item.planet_code}>
                  {translatePlanet(item.planet_code)}: {translateSign(item.sign_code)}{" "}
                  {formatDegreeMinuteFromSignLongitude(item.longitude)} ({item.longitude.toFixed(2)}°),{" "}
                  {translateHouse(item.house_number)}
                  {houseInterval ? ` (${houseInterval})` : ""}
                </li>
              )
            })}
          </ul>
        </article>

        <article className="card">
          <h2>{t.sections.houses}</h2>
          <ul>
            {houses.map((item) => (
              <li key={item.number}>
                {translateHouse(item.number)}: {t.cuspide} {item.cusp_longitude.toFixed(2)}°
              </li>
            ))}
          </ul>
        </article>
      </div>

      <article className="card">
        <h2>{t.sections.aspects}</h2>
        {aspects.length === 0 ? (
          <p>{t.noAspects}</p>
        ) : (
          <ul>
            {aspects.map((item, index) => (
              <li key={`${item.aspect_code}-${item.planet_a}-${item.planet_b}-${index}`}>
                {translateAspect(item.aspect_code)}: {translatePlanet(item.planet_a)} - {translatePlanet(item.planet_b)} ({t.angle} {item.angle.toFixed(2)}°, {t.orb}{" "}
                {item.orb.toFixed(2)}°)
              </li>
            ))}
          </ul>
        )}
      </article>

      <NatalChartGuide lang={lang} missingBirthTime={missingBirthTime} />
    </section>
  )
}
