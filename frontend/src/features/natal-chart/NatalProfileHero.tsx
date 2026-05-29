// Hero public du theme natal: il expose les trois reperes lisibles sans details techniques.
import type { LatestNatalChart } from "../../api/natalChart"
import type { AstrologyLabelers, PublicCopyLang } from "./natalPublicFacts"
import { firstAvailable, formatPlacement, getPlanetPosition } from "./natalPublicFacts"

type NatalProfileHeroProps = {
  chart: LatestNatalChart
  labels: AstrologyLabelers
  lang: PublicCopyLang
}

const COPY = {
  fr: {
    title: "Votre profil astrologique",
    lead: "Les trois portes d'entree de votre theme: elan vital, monde emotionnel et facon d'entrer en relation avec le monde.",
    sun: "Soleil",
    moon: "Lune",
    ascendant: "Ascendant",
    missing: "Donnee indisponible",
    traits: "Traits dominants",
  },
  en: {
    title: "Your astrological profile",
    lead: "The three entry points of your chart: vitality, emotional world, and the way you meet life.",
    sun: "Sun",
    moon: "Moon",
    ascendant: "Ascendant",
    missing: "Unavailable data",
    traits: "Dominant traits",
  },
  es: {
    title: "Tu perfil astrologico",
    lead: "Las tres puertas de entrada de tu carta: impulso vital, mundo emocional y forma de entrar en relacion.",
    sun: "Sol",
    moon: "Luna",
    ascendant: "Ascendente",
    missing: "Dato no disponible",
    traits: "Rasgos dominantes",
  },
  de: {
    title: "Your astrological profile",
    lead: "The three entry points of your chart: vitality, emotional world, and the way you meet life.",
    sun: "Sun",
    moon: "Moon",
    ascendant: "Ascendant",
    missing: "Unavailable data",
    traits: "Dominant traits",
  },
} as const

/** Affiche Soleil, Lune et Ascendant depuis le payload public existant. */
export function NatalProfileHero({ chart, labels, lang }: NatalProfileHeroProps) {
  const copy = COPY[lang] ?? COPY.fr
  const sun = getPlanetPosition(chart.result.planet_positions, "SUN")
  const moon = getPlanetPosition(chart.result.planet_positions, "MOON")
  const sunProfileCode = chart.astro_profile?.sun_sign_code
  const ascendantCode = chart.astro_profile?.ascendant_sign_code
  const adapter = chart.result.interpretation_adapter
  const traits = [
    ...(adapter?.dominant_topics ?? []),
    ...(adapter?.dominant_axes ?? []),
    ...(adapter?.narrative_priorities ?? []),
  ].slice(0, 4)

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
      <p className="natal-hero__traits">
        <strong>{copy.traits}</strong>
        {firstAvailable([traits.join(" · ")], copy.missing)}
      </p>
    </section>
  )
}
