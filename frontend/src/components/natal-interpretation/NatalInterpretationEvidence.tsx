// Helpers et rendu des preuves astrologiques d'une interpretation natale.
import { useEffect, useState } from "react"
import { ChevronDown, ChevronUp } from "lucide-react"

export type EvidenceCategoryKey =
  | "angles"
  | "personal_planets"
  | "slow_planets"
  | "dominant_houses"
  | "major_aspects"
  | "other"

type EvidenceTranslations = {
  evidenceIntro: string
  evidenceEmpty: string
  showEvidence: string
  hideEvidence: string
  dedupedCount: (count: number) => string
  evidenceCategories: {
    angles: string
    personalPlanets: string
    slowPlanets: string
    dominantHouses: string
    majorAspects: string
    other: string
  }
}

const EVIDENCE_LABELS: Record<string, string> = {
  SUN: "Soleil",
  MOON: "Lune",
  MERCURY: "Mercure",
  VENUS: "Vénus",
  MARS: "Mars",
  JUPITER: "Jupiter",
  SATURN: "Saturne",
  URANUS: "Uranus",
  NEPTUNE: "Neptune",
  PLUTO: "Pluton",
  CHIRON: "Chiron",
  LILITH: "Lune Noire",
  NODE: "Nœud Nord",
  ASC: "Ascendant",
  MC: "Milieu du Ciel",
  DSC: "Descendant",
  IC: "Fond du Ciel",
  ARIES: "Bélier",
  TAURUS: "Taureau",
  GEMINI: "Gémeaux",
  CANCER: "Cancer",
  LEO: "Lion",
  VIRGO: "Vierge",
  LIBRA: "Balance",
  SCORPIO: "Scorpion",
  SAGITTARIUS: "Sagittaire",
  CAPRICORN: "Capricorne",
  AQUARIUS: "Verseau",
  PISCES: "Poissons",
  CONJUNCTION: "conjonction",
  SEXTILE: "sextile",
  SQUARE: "carré",
  TRINE: "trigone",
  OPPOSITION: "opposition",
  RETROGRADE: "rétrograde",
}

function evidenceLabel(token: string): string {
  return EVIDENCE_LABELS[token] ?? token
}

/** Convertit un identifiant de preuve technique en libelle lisible. */
export function formatEvidenceId(evidenceId: string): string {
  const planetSignHouse = evidenceId.match(/^([A-Z]+)_([A-Z]+)_H(\d{1,2})$/)
  if (planetSignHouse) {
    const [, planet, sign, house] = planetSignHouse
    return `${evidenceLabel(planet)} ${evidenceLabel(sign)} (M${house})`
  }

  const planetSign = evidenceId.match(/^([A-Z]+)_([A-Z]+)$/)
  if (planetSign) {
    const [, planet, sign] = planetSign
    if (["ASC", "MC", "DSC", "IC"].includes(planet)) {
      return `${evidenceLabel(planet)} ${evidenceLabel(sign)}`
    }
    if (EVIDENCE_LABELS[planet] && EVIDENCE_LABELS[sign]) {
      return `${evidenceLabel(planet)} ${evidenceLabel(sign)}`
    }
  }

  const houseInSign = evidenceId.match(/^HOUSE_(\d{1,2})_IN_([A-Z]+)$/)
  if (houseInSign) {
    const [, house, sign] = houseInSign
    return `Maison ${house} en ${evidenceLabel(sign)}`
  }

  const aspectPrefixed = evidenceId.match(/^ASPECT_([A-Z]+)_([A-Z]+)_([A-Z]+)$/)
  if (aspectPrefixed) {
    const [, firstBody, secondBody, kind] = aspectPrefixed
    return `Aspect ${evidenceLabel(firstBody)} - ${evidenceLabel(secondBody)} (${evidenceLabel(kind)})`
  }

  return evidenceId
    .split("_")
    .map((part) => {
      if (part.startsWith("H") && part.length <= 3) return `(M${part.substring(1)})`
      if (part.startsWith("ORB")) return ""
      return evidenceLabel(part)
    })
    .filter(Boolean)
    .join(" ")
}

/** Classe une preuve pour l'affichage groupe des tags d'interpretation. */
export function categorizeEvidence(evidenceId: string): EvidenceCategoryKey {
  if (evidenceId.startsWith("ASPECT_")) {
    return "major_aspects"
  }
  if (/(^|_)(ASC|MC|DSC|IC)(_|$)/.test(evidenceId)) {
    return "angles"
  }
  if (/^HOUSE_\d{1,2}_IN_/.test(evidenceId) || /_H\d{1,2}$/.test(evidenceId)) {
    return "dominant_houses"
  }
  if (/^(SUN|MOON|MERCURY|VENUS|MARS)(_|$)/.test(evidenceId)) {
    return "personal_planets"
  }
  if (/^(JUPITER|SATURN|URANUS|NEPTUNE|PLUTO)(_|$)/.test(evidenceId)) {
    return "slow_planets"
  }
  return "other"
}

export function EvidenceTags({
  evidence,
  title,
  t,
}: {
  evidence: string[]
  title: string
  t: EvidenceTranslations
}) {
  const [open, setOpen] = useState(evidence.length > 0)
  useEffect(() => {
    if (evidence.length > 0) {
      setOpen(true)
    }
  }, [evidence.length])

  const categoryLabels: Record<EvidenceCategoryKey, string> = {
    angles: t.evidenceCategories.angles,
    personal_planets: t.evidenceCategories.personalPlanets,
    slow_planets: t.evidenceCategories.slowPlanets,
    dominant_houses: t.evidenceCategories.dominantHouses,
    major_aspects: t.evidenceCategories.majorAspects,
    other: t.evidenceCategories.other,
  }

  const deduped = Array.from(
    new Map(
      evidence.map((evidenceId) => {
        const humanText = formatEvidenceId(evidenceId)
        return [humanText.toLowerCase(), { evidenceId, humanText }]
      }),
    ).values(),
  )

  const grouped = deduped.reduce<Record<EvidenceCategoryKey, Array<{ evidenceId: string; humanText: string }>>>(
    (accumulator, item) => {
      accumulator[categorizeEvidence(item.evidenceId)].push(item)
      return accumulator
    },
    {
      angles: [],
      personal_planets: [],
      slow_planets: [],
      dominant_houses: [],
      major_aspects: [],
      other: [],
    },
  )
  const orderedKeys: EvidenceCategoryKey[] = [
    "angles",
    "personal_planets",
    "slow_planets",
    "dominant_houses",
    "major_aspects",
    "other",
  ]
  const totalCount = deduped.length

  return (
    <div className="ni-evidence-tags">
      <button
        type="button"
        onClick={() => setOpen((previous) => !previous)}
        className="ni-evidence-toggle-btn"
      >
        <div>
          <p className="ni-evidence-tags-title">{title}</p>
          <p className="ni-evidence-intro">{t.evidenceIntro}</p>
          <p className="ni-evidence-count">{t.dedupedCount(totalCount)}</p>
        </div>
        <span className="ni-evidence-toggle-icon">
          {open ? t.hideEvidence : t.showEvidence}
          {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </span>
      </button>

      {open && (
        <div className="ni-evidence-content">
          {totalCount === 0 ? <p className="ni-evidence-empty">{t.evidenceEmpty}</p> : null}
          {orderedKeys.map((key) => {
            const items = grouped[key]
            if (items.length === 0) return null
            return (
              <div key={key}>
                <p className="ni-evidence-category-label">{categoryLabels[key]}</p>
                <div className="evidence-tags__list">
                  {items.map((item, index) => {
                    const isAspect = item.evidenceId.startsWith("ASPECT_")
                    const isAngle = ["ASC", "MC", "DSC", "IC"].some((angle) => item.evidenceId.includes(angle))
                    const modifier = isAspect ? "aspect" : isAngle ? "angle" : "planet"
                    return (
                      <span
                        key={`${item.evidenceId}-${index}`}
                        title={item.evidenceId}
                        className={`evidence-pill evidence-pill--${modifier}`}
                      >
                        <span className="evidence-pill__dot" />
                        {item.humanText}
                      </span>
                    )
                  })}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
