import { useEffect } from "react"
import { Link } from "react-router-dom"
import { ApiError, useLatestNatalChart } from "../api/natalChart"
import { useAstrologyLabels, DEGRADED_MODE_MESSAGES } from "../i18n/astrology"
import { natalChartTranslations } from "../i18n/natalChart"
import { logSupportRequestId } from "../utils/constants"
import { formatDateTime } from "../utils/formatDate"

export function NatalChartPage() {
  const latestChart = useLatestNatalChart()
  const { lang, translatePlanet, translateSign, translateHouse, translateAspect } = useAstrologyLabels()
  const t = natalChartTranslations[lang]

  const error = latestChart.error
  const apiError = error instanceof ApiError ? error : null

  useEffect(() => {
    if (latestChart.isError && apiError) {
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

  return (
    <section className="panel">
      <h1>{t.title}</h1>
      <p>
        {t.generatedOn} {formatDateTime(chart.created_at)} · {t.referenceVersion} {chart.metadata.reference_version}
        · {t.rulesetVersion} {chart.metadata.ruleset_version}
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

      <div className="grid">
        <article className="card">
          <h2>{t.sections.planets}</h2>
          <ul>
            {planetPositions.map((item) => (
              <li key={item.planet_code}>
                {translatePlanet(item.planet_code)}: {translateSign(item.sign_code)} ({item.longitude.toFixed(2)}°), {translateHouse(item.house_number)}
              </li>
            ))}
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
    </section>
  )
}
