import { ApiError, useLatestNatalChart } from "../api/natalChart"
import { useAstrologyLabels } from "../i18n/astrology"

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  })
}

export function NatalChartPage() {
  const latestChart = useLatestNatalChart()
  const { lang, translatePlanet, translateSign, translateHouse, translateAspect } = useAstrologyLabels()

  if (latestChart.isLoading) {
    return (
      <section className="panel" aria-busy="true">
        <h1>Thème natal</h1>
        <p>Chargement de votre dernier thème natal...</p>
      </section>
    )
  }

  if (latestChart.isError) {
    const error = latestChart.error
    if (error instanceof ApiError && error.code === "natal_chart_not_found") {
      return (
        <section className="panel">
          <h1>Thème natal</h1>
          <p>Aucun thème natal disponible pour le moment.</p>
          <p>Générez d'abord votre thème initial pour afficher cette page.</p>
        </section>
      )
    }

    return (
      <section className="panel">
        <h1>Thème natal</h1>
        <p>Une erreur est survenue: {error instanceof Error ? error.message : "Erreur inconnue"}</p>
        {error instanceof ApiError && error.requestId ? (
          <p className="state-line" style={{ fontSize: "0.8rem", opacity: 0.7 }}>
            <span aria-hidden="true">ID de requête: </span>
            <span aria-label={`Identifiant de support technique: ${error.requestId}`}>{error.requestId}</span>
          </p>
        ) : null}
        <button type="button" onClick={() => void latestChart.refetch()}>
          Réessayer
        </button>
      </section>
    )
  }

  const chart = latestChart.data
  if (!chart) {
    return (
      <section className="panel">
        <h1>Thème natal</h1>
        <p>Aucune donnée de thème disponible pour le moment.</p>
      </section>
    )
  }

  return (
    <section className="panel">
      <h1>Thème natal</h1>
      <p>
        Généré le {formatDateTime(chart.created_at)} · Version référentiel {chart.metadata.reference_version}
        · Ruleset {chart.metadata.ruleset_version}
      </p>

      {(chart.metadata.degraded_mode === "no_location" ||
        chart.metadata.degraded_mode === "no_location_no_time") && (
        <div className="chat-error degraded-warning" role="alert">
          ⚠ Thème calculé en maisons égales — lieu de naissance non renseigné ou non trouvé.{" "}
          Pour un calcul précis, renseignez votre ville et pays dans votre profil.
        </div>
      )}
      {(chart.metadata.degraded_mode === "no_time" ||
        chart.metadata.degraded_mode === "no_location_no_time") && (
        <div className="chat-error degraded-warning" role="alert">
          ⚠ Thème calculé en thème solaire — heure de naissance non renseignée.{" "}
          Les positions des maisons et de la Lune peuvent être inexactes.
        </div>
      )}

      <div className="grid">
        <article className="card">
          <h2>Planètes</h2>
          <ul>
            {(chart.result.planet_positions ?? []).map((item) => (
              <li key={item.planet_code}>
                {translatePlanet(item.planet_code, lang)}: {translateSign(item.sign_code, lang)} ({item.longitude.toFixed(2)}°), {translateHouse(item.house_number, lang)}
              </li>
            ))}
          </ul>
        </article>

        <article className="card">
          <h2>Maisons</h2>
          <ul>
            {(chart.result.houses ?? []).map((item) => (
              <li key={item.number}>
                {translateHouse(item.number, lang)}: cuspide {item.cusp_longitude.toFixed(2)}°
              </li>
            ))}
          </ul>
        </article>
      </div>

      <article className="card">
        <h2>Aspects majeurs</h2>
        {(() => {
          const aspects = chart.result.aspects ?? []
          return aspects.length === 0 ? (
            <p>Aucun aspect majeur détecté pour ce calcul.</p>
          ) : (
            <ul>
              {aspects.map((item) => (
                <li key={`${item.aspect_code}-${item.planet_a}-${item.planet_b}`}>
                  {translateAspect(item.aspect_code, lang)}: {translatePlanet(item.planet_a, lang)} - {translatePlanet(item.planet_b, lang)} (angle {item.angle.toFixed(2)}°, orbe{" "}
                  {item.orb.toFixed(2)}°)
                </li>
              ))}
            </ul>
          )
        })()}
      </article>
    </section>
  )
}
