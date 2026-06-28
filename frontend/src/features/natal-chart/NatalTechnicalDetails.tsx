// Details techniques du theme natal: rendu brut reserve au mode astrologue.
import type { AspectResult, HouseResult, PlanetPosition } from "../../api/natalChart"
import "./NatalTechnicalDetails.css"
import "./NatalAspects.css"

type NatalTechnicalDetailsProps = {
  planetPositions: PlanetPosition[]
  houses: HouseResult[]
  aspects: AspectResult[]
  translatePlanet: (code: string) => string
  translateSign: (code: string) => string
  translateHouse: (house: number) => string
  translateAspect: (code: string) => string
  getHouseIntervalLabel: (houseNumber: number) => string | null
  formatDegreeMinuteFromSignLongitude: (value: number) => string
  getSignCodeFromLongitude: (value: number) => string
  t: {
    sections: { planets: string; houses: string; aspects: string }
    planetsLead: string
    housesLead: string
    aspectsLead: string
    positionLabel: string
    longitudeLabel: string
    houseLabel: string
    cuspLongitudeLabel: string
    houseSignLabel: string
    aspectExactAngleLabel: string
    aspectMeaningMap: Record<string, string>
    orb: string
    orbUsed: string
    noAspects: string
  }
}

/** Regroupe les anciennes listes techniques sans les rendre dans la vue publique par defaut. */
export function NatalTechnicalDetails({
  planetPositions,
  houses,
  aspects,
  translatePlanet,
  translateSign,
  translateHouse,
  translateAspect,
  getHouseIntervalLabel,
  formatDegreeMinuteFromSignLongitude,
  getSignCodeFromLongitude,
  t,
}: NatalTechnicalDetailsProps) {
  const sortedHouses = [...houses].sort((a, b) => a.number - b.number)

  return (
    <>
      <div className="natal-grid">
        <article className="natal-card">
          <h2 className="natal-technical-card__title">{t.sections.planets}</h2>
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
          <h2 className="natal-technical-card__title">{t.sections.houses}</h2>
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
        <h2 className="natal-technical-card__title">{t.sections.aspects}</h2>
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
                    {translatePlanet(item.planet_a)} - {translatePlanet(item.planet_b)}
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
    </>
  )
}
