// Composant public d'affichage de l'interprétation natale Astral normalisée.
import { useEffect, useId, useState } from "react"
import { Link } from "react-router-dom"
import { Home, Sparkles, Sun, Triangle } from "lucide-react"
import type { LucideIcon } from "lucide-react"

import type {
  NatalCalculationFactsViewModel,
  NatalInterpretationViewModel,
  NatalReadingChapterViewModel,
} from "./natalAstralReadingViewModel"

type NatalAstralReadingProps = {
  reading: NatalInterpretationViewModel
  showSummary?: boolean
}

const PUBLIC_READING_ERROR_MESSAGE =
  "La lecture Astral n'a pas pu être générée pour le moment. Veuillez réessayer plus tard."
const EXCERPT_MAX_LENGTH = 140

const GROUP_MARKERS: Record<string, LucideIcon> = {
  "Repères principaux": Sun,
  Maisons: Home,
  "Planètes notables": Sparkles,
  "Aspects notables": Triangle,
}
const OPEN_MAIN_CHAPTER_COUNT = 2

function compactExcerpt(text: string): string {
  if (text.length <= EXCERPT_MAX_LENGTH) return text

  const rawExcerpt = text.slice(0, EXCERPT_MAX_LENGTH - 3).trimEnd()
  const lastWordBoundary = rawExcerpt.lastIndexOf(" ")
  return lastWordBoundary > 80 ? rawExcerpt.slice(0, lastWordBoundary) : rawExcerpt
}

function markerForGroup(title: string): LucideIcon {
  return GROUP_MARKERS[title] ?? Sparkles
}

function groupClassName(title: string): string {
  const modifier = title === "Repères principaux" ? " natal-reading-facts__group--primary" : ""
  return `natal-reading-facts__group${modifier}`
}

function chapterExcerpt(chapter: NatalReadingChapterViewModel): string | null {
  const firstParagraph = chapter.paragraphs[0]?.trim()
  if (!firstParagraph) return null

  const firstSentence = firstParagraph.match(/^(.+?[.!?])(?:\s|$)/)?.[1]
  const excerpt = firstSentence && firstSentence.length <= EXCERPT_MAX_LENGTH ? firstSentence : compactExcerpt(firstParagraph)
  return excerpt.endsWith(".") || excerpt.endsWith("!") || excerpt.endsWith("?") ? excerpt : `${excerpt}...`
}

function chapterBodyParagraphs(chapter: NatalReadingChapterViewModel, excerpt: string | null): string[] {
  if (!excerpt) return chapter.paragraphs

  const [firstParagraph, ...remainingParagraphs] = chapter.paragraphs
  const normalizedFirstParagraph = firstParagraph?.trim()
  if (!normalizedFirstParagraph) return remainingParagraphs

  if (normalizedFirstParagraph === excerpt) {
    return remainingParagraphs
  }

  const excerptPrefix = excerpt.replace(/\.\.\.$/, "").trim()
  if (excerptPrefix && normalizedFirstParagraph.startsWith(excerptPrefix)) {
    const remainder = normalizedFirstParagraph.slice(excerptPrefix.length).trim()
    return remainder ? [remainder, ...remainingParagraphs] : remainingParagraphs
  }

  return chapter.paragraphs
}

function chapterThemeTitle(chapter: NatalReadingChapterViewModel, index: number): string {
  return `${index + 1}. ${chapter.title}`
}

function chapterPanelId(baseId: string, itemKey: string): string {
  const safeKey = itemKey.replace(/[^a-zA-Z0-9_-]/g, "-")
  return `${baseId}-${safeKey}-body`
}

function chapterStateKey(chapter: NatalReadingChapterViewModel, itemKey: string): string {
  return [itemKey, chapter.paragraphs.join("\u0000"), chapter.astroBasis.join("\u0000"), chapter.safetyFlags.join("\u0000")].join(
    "\u0001",
  )
}

function NatalCalculationFacts({ facts }: { facts: NatalCalculationFactsViewModel }) {
  return (
    <section className="natal-reading-facts" aria-labelledby="natal-reading-facts-title">
      <div className="natal-reading-facts__header">
        <span className="natal-section-eyebrow">{facts.sourceLabel}</span>
        <h2 id="natal-reading-facts-title">Base du calcul natal</h2>
      </div>
      <div className="natal-reading-facts__grid">
        {facts.groups.map((group) => {
          const Marker = markerForGroup(group.title)
          return (
            <section className={groupClassName(group.title)} key={group.title} aria-label={group.title}>
              <div className="natal-reading-facts__group-head">
                <span className="natal-reading-facts__marker" aria-hidden="true">
                  <Marker size={16} strokeWidth={1.8} />
                </span>
                <h3>{group.title}</h3>
              </div>
              <dl className="natal-reading-facts__list">
                {group.items.map((item) => (
                  <div className="natal-reading-facts__item" key={`${group.title}-${item.label}-${item.value}`}>
                    <dt>{item.label}</dt>
                    <dd>
                      <span className="natal-badge natal-badge--astro-data">
                        <strong>{item.value}</strong>
                      </span>
                      {item.detail ? <span className="natal-badge natal-badge--fact-detail">{item.detail}</span> : null}
                    </dd>
                  </div>
                ))}
              </dl>
            </section>
          )
        })}
      </div>
    </section>
  )
}

function NatalChapterCard({
  chapter,
  itemKey,
  themeTitle,
  defaultExpanded = true,
  compact = false,
}: {
  chapter: NatalReadingChapterViewModel
  itemKey: string
  themeTitle: string
  defaultExpanded?: boolean
  compact?: boolean
}) {
  const baseId = useId()
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)
  const resetKey = chapterStateKey(chapter, itemKey)
  const excerpt = chapterExcerpt(chapter)
  const bodyParagraphs = chapterBodyParagraphs(chapter, excerpt)
  const hasMeta = Boolean(chapter.confidenceLabel) || chapter.astroBasis.length > 0 || chapter.safetyFlags.length > 0
  const panelId = chapterPanelId(baseId, itemKey)
  const canToggle = bodyParagraphs.length > 0
  const chapterClassName = [
    "natal-reading__chapter",
    hasMeta ? "" : "natal-reading__chapter--no-meta",
    isExpanded ? "natal-reading__chapter--expanded" : "natal-reading__chapter--collapsed",
    compact ? "natal-reading__chapter--compact" : "",
  ]
    .filter(Boolean)
    .join(" ")

  useEffect(() => {
    setIsExpanded(defaultExpanded)
  }, [defaultExpanded, resetKey])

  return (
    <section className={chapterClassName}>
      <div className="natal-reading__chapter-main">
        <div className="natal-reading__chapter-head">
          <div className="natal-reading__chapter-title">
            <h3>{themeTitle}</h3>
            <span className="natal-section-eyebrow">Lecture guidée</span>
          </div>
        </div>
        {excerpt ? (
          <p className="natal-reading__chapter-excerpt">
            <span className="natal-reading__chapter-excerpt-label">À retenir</span>
            <span className="natal-reading__chapter-excerpt-text">{excerpt}</span>
          </p>
        ) : null}
        {bodyParagraphs.length > 0 ? (
          <div className="natal-reading__chapter-body" id={panelId} hidden={!isExpanded}>
            {bodyParagraphs.map((paragraph, paragraphIndex) => (
              <p key={`${itemKey}-paragraph-${paragraphIndex}`}>{paragraph}</p>
            ))}
          </div>
        ) : null}
        {canToggle ? (
          <button
            aria-controls={panelId}
            aria-expanded={isExpanded}
            className="natal-reading__chapter-toggle"
            type="button"
            onClick={() => setIsExpanded((current) => !current)}
          >
            {isExpanded ? "Réduire" : "Lire la suite"}
          </button>
        ) : null}
      </div>
      {hasMeta ? (
        <aside className="natal-reading__chapter-meta" aria-label={`Qualité et repères pour ${chapter.title}`}>
          {chapter.confidenceLabel ? (
            <span className="natal-badge natal-badge--confidence">{chapter.confidenceLabel}</span>
          ) : null}
          {chapter.astroBasis.length > 0 ? (
            <div className="natal-reading__basis" aria-label={`Repères utilisés pour ${chapter.title}`}>
              <span>Repères utilisés</span>
              <ul>
                {chapter.astroBasis.map((basis, basisIndex) => (
                  <li className="natal-badge natal-badge--basis" key={`${itemKey}-basis-${basisIndex}`}>
                    {basis}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
          {chapter.safetyFlags.length > 0 ? (
            <p className="natal-reading__safety">Note de prudence : {chapter.safetyFlags.join(", ")}</p>
          ) : null}
        </aside>
      ) : null}
    </section>
  )
}

/** Affiche la lecture Astral sans exposer les champs techniques du moteur externe. */
export function NatalAstralReading({ reading, showSummary = true }: NatalAstralReadingProps) {
  if (reading.status === "failed" || reading.status === "safety_rejected") {
    return (
      <article className="natal-reading natal-reading--error" aria-label="Erreur de lecture Astral">
        <header className="natal-reading__header">
          <span className="natal-section-eyebrow">{reading.label}</span>
          <h2>{reading.title}</h2>
        </header>
        <div className="chat-error natal-card__error" role="alert">
          <p>{PUBLIC_READING_ERROR_MESSAGE}</p>
          <Link to="/profile" className="btn-link natal-card__secondary-link">
            Vérifier mon profil de naissance
          </Link>
        </div>
      </article>
    )
  }

  return (
    <article className="natal-reading" aria-label="Interprétation de votre thème natal">
      {reading.calculationFacts ? <NatalCalculationFacts facts={reading.calculationFacts} /> : null}

      <header className="natal-reading__header">
        <span className="natal-section-eyebrow">Interprétation de votre thème natal</span>
        <div className="natal-reading__summary">
          <h2>{reading.title}</h2>
          <span className="natal-badge natal-badge--report-status">{reading.label}</span>
        </div>
        {showSummary && reading.shortText ? <p>{reading.shortText}</p> : null}
      </header>

      {reading.isPartial ? (
        <p className="natal-reading__precision-note natal-reading__partial-alert" role="alert">
          Thème partiel : certaines données de naissance manquent ou ne sont pas assez fiables. L'ascendant, les
          maisons et certains angles peuvent être absents ou limités.
        </p>
      ) : null}

      {reading.chapters.length > 0 ? (
        <div className="natal-reading__progress" aria-label="Progression des lectures">
          <span className="natal-section-eyebrow">Parcours de lecture</span>
          <ol>
            {reading.chapters.map((chapter, index) => (
              <li key={`progress-${chapter.code ?? chapter.title}-${index}`}>{chapterThemeTitle(chapter, index)}</li>
            ))}
          </ol>
        </div>
      ) : null}

      {reading.chapters.length > 0 ? (
        <div className="natal-reading__chapters">
          {reading.chapters.map((chapter, index) => (
            <NatalChapterCard
              chapter={chapter}
              defaultExpanded={index < OPEN_MAIN_CHAPTER_COUNT}
              itemKey={`chapter-${chapter.code ?? chapter.title}-${index}`}
              key={`${chapter.code ?? chapter.title}-${index}`}
              themeTitle={chapterThemeTitle(chapter, index)}
            />
          ))}
        </div>
      ) : reading.explanations.length === 0 ? (
        <p className="natal-card__lead">La lecture est disponible mais ne contient pas encore de chapitres publics.</p>
      ) : null}

      {reading.explanations.length > 0 ? (
        <section className="natal-reading-explanations" aria-labelledby="natal-reading-explanations-title">
          <div className="natal-reading-explanations__header">
            <span className="natal-section-eyebrow">Repères calculés</span>
            <h2 id="natal-reading-explanations-title">Explications du moteur Astral</h2>
          </div>
          <div className="natal-reading-explanations__list">
            {reading.explanations.map((chapter, index) => (
              <NatalChapterCard
                compact
                chapter={chapter}
                defaultExpanded={false}
                itemKey={`explanation-${chapter.code ?? chapter.title}-${index}`}
                key={`explanation-${chapter.code ?? chapter.title}-${index}`}
                themeTitle={chapter.title}
              />
            ))}
          </div>
        </section>
      ) : null}

      {reading.disclaimer ? <p className="natal-reading__disclaimer">{reading.disclaimer}</p> : null}
    </article>
  )
}
