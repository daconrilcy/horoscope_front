import { ApiError, useLatestNatalChart } from "../api/natalChart"

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString("fr-FR", {
    dateStyle: "medium",
    timeStyle: "short",
  })
}

export function NatalChartPage() {
  const latestChart = useLatestNatalChart()

  if (latestChart.isLoading) {
    return (
      <section className="panel" aria-busy="true">
        <h1>Theme natal</h1>
        <p>Chargement de votre dernier theme natal...</p>
      </section>
    )
  }

  if (latestChart.isError) {
    const error = latestChart.error as ApiError
    if (error.code === "natal_chart_not_found") {
      return (
        <section className="panel">
          <h1>Theme natal</h1>
          <p>Aucun theme natal disponible pour le moment.</p>
          <p>Generez d abord votre theme initial pour afficher cette page.</p>
        </section>
      )
    }

    return (
      <section className="panel">
        <h1>Theme natal</h1>
        <p>Une erreur est survenue: {error.message}</p>
        <button type="button" onClick={() => latestChart.refetch()}>
          Reessayer
        </button>
      </section>
    )
  }

  const chart = latestChart.data
  if (!chart) {
    return (
      <section className="panel">
        <h1>Theme natal</h1>
        <p>Aucune donnee de theme disponible pour le moment.</p>
      </section>
    )
  }

  return (
    <section className="panel">
      <h1>Theme natal</h1>
      <p>
        Genere le {formatDateTime(chart.created_at)} · Version referentiel {chart.metadata.reference_version}
        · Ruleset {chart.metadata.ruleset_version}
      </p>

      <div className="grid">
        <article className="card">
          <h2>Planetes</h2>
          <ul>
            {chart.result.planet_positions.map((item) => (
              <li key={item.planet_code}>
                {item.planet_code}: {item.sign_code} ({item.longitude.toFixed(2)}°), maison {item.house_number}
              </li>
            ))}
          </ul>
        </article>

        <article className="card">
          <h2>Maisons</h2>
          <ul>
            {chart.result.houses.map((item) => (
              <li key={item.number}>
                Maison {item.number}: cuspide {item.cusp_longitude.toFixed(2)}°
              </li>
            ))}
          </ul>
        </article>
      </div>

      <article className="card">
        <h2>Aspects majeurs</h2>
        {chart.result.aspects.length === 0 ? (
          <p>Aucun aspect majeur detecte pour ce calcul.</p>
        ) : (
          <ul>
            {chart.result.aspects.map((item) => (
              <li key={`${item.aspect_code}-${item.planet_a}-${item.planet_b}`}>
                {item.aspect_code}: {item.planet_a} - {item.planet_b} (angle {item.angle.toFixed(2)}°, orbe{" "}
                {item.orb.toFixed(2)}°)
              </li>
            ))}
          </ul>
        )}
      </article>
    </section>
  )
}
