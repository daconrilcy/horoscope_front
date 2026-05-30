// Hero public du theme natal: il expose les trois reperes lisibles sans details techniques.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers, PublicCopyLang } from "./natalPublicFacts"
import { formatPlacement, getPlanetPosition } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"

type NatalProfileHeroProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
  lang: PublicCopyLang
}

/** Affiche Soleil, Lune et Ascendant depuis le payload public existant. */
export function NatalProfileHero({ chart, labels, lang }: NatalProfileHeroProps) {
  const copy = getNatalPublicCopy(lang).hero
  const sun = getPlanetPosition(chart.result.planet_positions, "SUN")
  const moon = getPlanetPosition(chart.result.planet_positions, "MOON")
  const sunProfileCode = chart.astro_profile?.sun_sign_code
  const ascendantCode = chart.astro_profile?.ascendant_sign_code
  const ascendantLabel = ascendantCode ? labels.translateSign(ascendantCode.toUpperCase()) : copy.missing

  return (
    <section className="natal-hero" aria-labelledby="natal-profile-hero-title">
      <div className="natal-hero__copy">
        <span className="natal-section-eyebrow">{copy.title}</span>
        <h2 id="natal-profile-hero-title">{copy.title}</h2>
        <p>{copy.lead}</p>
      </div>
      <div className="natal-hero__triptych" aria-label={copy.title}>
        <article className="natal-hero-pill">
          <span className="natal-hero-pill__symbol" aria-hidden="true">☉</span>
          <h3>{copy.sun}</h3>
          <p>{sun ? formatPlacement(sun, labels, copy.missing) : sunProfileCode ? labels.translateSign(sunProfileCode.toUpperCase()) : copy.missing}</p>
        </article>
        <article className="natal-hero-pill">
          <span className="natal-hero-pill__symbol" aria-hidden="true">☽</span>
          <h3>{copy.moon}</h3>
          <p>{formatPlacement(moon, labels, copy.missing)}</p>
        </article>
        <article className="natal-hero-pill">
          <span className="natal-hero-pill__symbol" aria-hidden="true">↑</span>
          <h3>{copy.ascendant}</h3>
          <p>{ascendantLabel}</p>
        </article>
      </div>
    </section>
  )
}
