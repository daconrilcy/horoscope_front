// Composant public d'affichage de l'interprétation natale Astral normalisée.
import { useEffect, useId, useMemo, useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import {
  ArrowRight,
  BadgeCheck,
  BookOpen,
  CalendarDays,
  ChevronDown,
  ChevronRight,
  ChevronUp,
  CircleDot,
  Clock,
  Compass,
  Home,
  Info,
  Lightbulb,
  MapPin,
  Moon,
  Settings,
  Sparkles,
  Sun,
  Triangle,
  UserRound,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"

import type {
  NatalCalculationFactItemViewModel,
  NatalCalculationFactsViewModel,
  NatalHighlightFactViewModel,
  NatalInterpretationViewModel,
  NatalReadingChapterViewModel,
} from "./natalAstralReadingViewModel"
import natalLogoSrc from "../../assets/Natal_Logo02.png"
import { getZodiacIcon } from "../../components/zodiacSignIconMap"
import { normalizeSignCode } from "../../i18n/astrology"
import "./NatalReading.css"
import "./NatalReadingFacts.css"

type NatalAstralReadingProps = {
  guide?: ReactNode
  reading: NatalInterpretationViewModel
  showSummary?: boolean
}

const PUBLIC_READING_ERROR_MESSAGE =
  "La lecture Astral n'a pas pu être générée pour le moment. Veuillez réessayer plus tard."
const EXCERPT_MAX_LENGTH = 140
const PROSE_CHUNK_TARGET_LENGTH = 230
const CALCULATION_FACTS_SECTION_ID = "natal-reading-calculation-facts"
const CALCULATION_EXPLANATIONS_SECTION_ID = "natal-reading-calculation-explanations"
const READING_GUIDE_SECTION_ID = "natal-chart-guide"

const GROUP_MARKERS: Record<string, LucideIcon> = {
  "Repères principaux": Sun,
  Maisons: Home,
  "Positions sensibles": CircleDot,
  "Aspects majeurs": Triangle,
}
const GROUP_MODIFIERS: Record<string, string> = {
  "Repères principaux": "primary",
  Maisons: "houses",
  "Positions sensibles": "sensitive",
  "Aspects majeurs": "aspects",
}
const METHOD_MODIFIERS: Record<string, string> = {
  Coordonnées: "coordinates",
  "Fuseau horaire": "timezone",
  Précision: "precision",
  Référence: "reference",
  Système: "system",
}
const SECONDARY_FACTS_VISIBLE_COUNT = 3
const OPEN_MAIN_CHAPTER_COUNT = 2
const MAIN_CHAPTER_ROOT_ID = "natal-reading-chapter"
const SHORT_PROGRESS_LABELS = ["Identité", "Émotions", "Relations", "Carrière", "Talents", "Croissance"]
const WORDS_PER_MINUTE = 190
const METRIC_LABELS = ["Soleil", "Lune", "Ascendant"] as const
const CHAPTER_THEME_COUNT = 6

type MainChapterEntry = {
  anchorId: string
  chapter: NatalReadingChapterViewModel
  excerpt: string | null
  indexLabel: string
  itemKey: string
  progressKey: string
  readTimeLabel: string
  shortTitle: string
  themeClassName: string
  title: string
}

type ReadingMetric = NatalHighlightFactViewModel & {
  icon: LucideIcon
}

type SummaryExtraEntry = {
  anchorId: string
  indexLabel: string
  key: string
  subtitle: string
  title: string
}

type SummaryTrackedEntry = {
  anchorId: string
  itemKey: string
}

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
  const visualModifier = GROUP_MODIFIERS[title]
  const primaryModifier = title === "Repères principaux" ? " natal-reading-facts__group--primary" : ""
  const toneModifier = visualModifier ? ` natal-reading-facts__group--${visualModifier}` : ""
  return `natal-reading-facts__group${primaryModifier}${toneModifier}`
}

function primaryFactBadgeClassName(title: string): string {
  if (title === "Maisons") return "natal-badge natal-badge--astro-data natal-badge--astro-house"
  if (title === "Aspects majeurs") return "natal-badge natal-badge--astro-data natal-badge--astro-aspect"
  return "natal-badge natal-badge--astro-data natal-badge--astro-sign"
}

function detailFactBadgeClassName(title: string): string {
  const modifier = title === "Maisons" || title === "Aspects majeurs" ? " natal-badge--astro-intensity" : ""
  return `natal-badge natal-badge--fact-detail${modifier}`
}

function iconForPrimaryFact(label: string): LucideIcon {
  if (label === "Soleil") return Sun
  if (label === "Lune") return Moon
  if (label === "Ascendant") return Compass
  if (label === "Lieu") return MapPin
  if (label === "Date") return CalendarDays
  if (label === "Heure de naissance") return Clock
  return Sparkles
}

function zodiacIconForFact(item: NatalCalculationFactItemViewModel) {
  return getZodiacIcon(normalizeSignCode(item.value))
}

function primaryFactItemClassName(label: string): string {
  const modifier = safeDomId(label)
  return `natal-reading-facts__item natal-reading-facts__item--primary natal-reading-facts__item--${modifier}`
}

function iconForMethod(label: string): LucideIcon {
  if (label === "Système") return Settings
  if (label === "Fuseau horaire") return Clock
  if (label === "Coordonnées") return MapPin
  if (label === "Précision") return CircleDot
  return Sparkles
}

function methodClassName(label: string): string {
  const modifier = METHOD_MODIFIERS[label]
  return modifier ? `natal-reading-facts__method natal-reading-facts__method--${modifier}` : "natal-reading-facts__method"
}

function expandLabelForGroup(title: string, isExpanded: boolean): string {
  if (title === "Maisons") return isExpanded ? "Réduire les maisons" : "Voir toutes les maisons"
  if (title === "Aspects majeurs") return isExpanded ? "Réduire les aspects" : "Voir tous les aspects"
  if (title === "Positions sensibles") return isExpanded ? "Réduire les positions" : "Voir toutes les positions"
  return isExpanded ? "Réduire" : "Voir tout"
}

function chapterExcerpt(chapter: NatalReadingChapterViewModel): string | null {
  const firstParagraph = chapter.paragraphs[0]?.trim()
  if (!firstParagraph) return null

  const firstSentence = firstParagraph.match(/^(.+?[.!?])(?:\s|$)/)?.[1]
  const excerpt = firstSentence && firstSentence.length <= EXCERPT_MAX_LENGTH ? firstSentence : compactExcerpt(firstParagraph)
  return excerpt.endsWith(".") || excerpt.endsWith("!") || excerpt.endsWith("?") ? excerpt : `${excerpt}...`
}

function chapterBodyParagraphs(chapter: NatalReadingChapterViewModel, excerpt: string | null): string[] {
  const splitParagraphs = (paragraphs: string[]) => paragraphs.flatMap(splitProseParagraph)
  if (!excerpt) return splitParagraphs(chapter.paragraphs)

  const [firstParagraph, ...remainingParagraphs] = chapter.paragraphs
  const normalizedFirstParagraph = firstParagraph?.trim()
  if (!normalizedFirstParagraph) return splitParagraphs(remainingParagraphs)

  if (normalizedFirstParagraph === excerpt) {
    return splitParagraphs(remainingParagraphs)
  }

  const excerptPrefix = excerpt.replace(/\.\.\.$/, "").trim()
  if (excerptPrefix && normalizedFirstParagraph.startsWith(excerptPrefix)) {
    const remainder = normalizedFirstParagraph.slice(excerptPrefix.length).trim()
    return splitParagraphs(remainder ? [remainder, ...remainingParagraphs] : remainingParagraphs)
  }

  return splitParagraphs(chapter.paragraphs)
}

function chapterThemeTitle(chapter: NatalReadingChapterViewModel): string {
  return chapter.title.replace(/^\d+\.\s*/, "")
}

function chapterThemeClassName(index: number): string {
  return `natal-reading__theme-${(index % CHAPTER_THEME_COUNT) + 1}`
}

function estimatedReadTime(chapter: NatalReadingChapterViewModel): string {
  const words = chapter.paragraphs.join(" ").trim().split(/\s+/).filter(Boolean).length
  const minutes = Math.max(1, Math.ceil(words / WORDS_PER_MINUTE))
  return `${minutes} min de lecture`
}

function progressPercent(activeIndex: number, total: number): number {
  if (total <= 0) return 0
  if (total === 1) return 0
  return Math.round((activeIndex / (total - 1)) * 100)
}

function metricIcon(label: string): LucideIcon {
  if (label === "Soleil") return Sun
  if (label === "Lune") return Moon
  if (label === "Ascendant") return Compass
  return BadgeCheck
}

function metricToneClassName(label: string): string {
  if (label === "Soleil") return "natal-reading-metrics__item--sun"
  if (label === "Lune") return "natal-reading-metrics__item--moon"
  if (label === "Ascendant") return "natal-reading-metrics__item--ascendant"
  return "natal-reading-metrics__item--status"
}

function buildReadingMetrics(reading: NatalInterpretationViewModel): ReadingMetric[] {
  const metrics = METRIC_LABELS.flatMap((label) => {
    const fact = reading.highlightFacts.find((item) => item.label === label)
    return fact ? [{ ...fact, icon: metricIcon(label) }] : []
  })

  return [
    ...metrics,
    {
      detail: reading.completeness === "partial" ? "Lecture partielle" : "Lecture complète",
      icon: BadgeCheck,
      label: "Statut",
      value: reading.label,
    },
  ]
}

function splitProseParagraph(paragraph: string): string[] {
  const normalizedParagraph = paragraph.trim()
  if (normalizedParagraph.length <= PROSE_CHUNK_TARGET_LENGTH) return normalizedParagraph ? [normalizedParagraph] : []

  const sentences = normalizedParagraph.match(/[^.!?]+[.!?]+(?:["'»”])?|[^.!?]+$/g)
  if (!sentences || sentences.length < 2) return splitLongProseChunk(normalizedParagraph)

  const chunks: string[] = []
  let currentChunk = ""
  for (const sentence of sentences) {
    const normalizedSentence = sentence.trim()
    if (!normalizedSentence) continue
    const nextChunk = currentChunk ? `${currentChunk} ${normalizedSentence}` : normalizedSentence
    if (currentChunk && nextChunk.length > PROSE_CHUNK_TARGET_LENGTH) {
      chunks.push(...splitLongProseChunk(currentChunk))
      currentChunk = normalizedSentence
    } else {
      currentChunk = nextChunk
    }
  }
  if (currentChunk) chunks.push(...splitLongProseChunk(currentChunk))
  return chunks
}

function splitLongProseChunk(chunk: string): string[] {
  if (chunk.length <= PROSE_CHUNK_TARGET_LENGTH) return chunk ? [chunk] : []

  const parts = chunk.split(/([,;:]\s+)/)
  const chunks: string[] = []
  let currentChunk = ""
  for (let index = 0; index < parts.length; index += 2) {
    const part = `${parts[index] ?? ""}${parts[index + 1] ?? ""}`.trim()
    if (!part) continue
    if (part.length > PROSE_CHUNK_TARGET_LENGTH) {
      if (currentChunk) {
        chunks.push(currentChunk)
        currentChunk = ""
      }
      chunks.push(...splitOverlongProsePart(part))
      continue
    }
    const nextChunk = currentChunk ? `${currentChunk} ${part}` : part
    if (currentChunk && nextChunk.length > PROSE_CHUNK_TARGET_LENGTH) {
      chunks.push(currentChunk)
      currentChunk = part
    } else {
      currentChunk = nextChunk
    }
  }
  if (currentChunk) chunks.push(currentChunk)
  return chunks.length > 0 ? chunks : [chunk]
}

function splitOverlongProsePart(part: string): string[] {
  const words = part.split(/\s+/).filter(Boolean)
  if (words.length < 2) return [part]

  const chunks: string[] = []
  let currentChunk = ""
  for (const word of words) {
    const nextChunk = currentChunk ? `${currentChunk} ${word}` : word
    if (currentChunk && nextChunk.length > PROSE_CHUNK_TARGET_LENGTH) {
      chunks.push(currentChunk)
      currentChunk = word
    } else {
      currentChunk = nextChunk
    }
  }
  if (currentChunk) chunks.push(currentChunk)
  return chunks
}

function shortProgressTitle(title: string, index: number): string {
  const normalizedTitle = title
    .replace(/^\d+\.\s*/, "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()

  if (normalizedTitle.includes("ident")) return "Identité"
  if (normalizedTitle.includes("emotion") || normalizedTitle.includes("lune")) return "Émotions"
  if (normalizedTitle.includes("relation") || normalizedTitle.includes("amour")) return "Relations"
  if (normalizedTitle.includes("carriere") || normalizedTitle.includes("travail")) return "Carrière"
  if (normalizedTitle.includes("talent") || normalizedTitle.includes("ressource")) return "Talents"
  if (normalizedTitle.includes("croissance") || normalizedTitle.includes("evolution")) return "Croissance"
  return SHORT_PROGRESS_LABELS[index] ?? title.replace(/^\d+\.\s*/, "")
}

function safeDomId(value: string): string {
  return value
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9_-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .toLowerCase()
}

function chapterAnchorId(itemKey: string): string {
  return `${MAIN_CHAPTER_ROOT_ID}-${safeDomId(itemKey)}`
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

function NatalCalculationFactsHeader({ sourceLabel }: { sourceLabel: string }) {
  return (
    <div className="natal-reading-facts__header">
      <div className="natal-reading-facts__header-copy">
        <span className="natal-section-eyebrow">{sourceLabel}</span>
        <h2 id="natal-reading-facts-title">Base du calcul natal</h2>
        <p>Paramètres astronomiques et astrologiques utilisés pour établir votre thème.</p>
      </div>
      <Link to="/profile" className="natal-reading-facts__profile-link">
        <UserRound size={17} aria-hidden="true" />
        Mon profil de base
      </Link>
    </div>
  )
}

function NatalPrimaryFactsPanel({ group }: { group: NatalCalculationFactsViewModel["groups"][number] }) {
  return (
    <section className={groupClassName(group.title)} aria-label={group.title}>
      <div className="natal-reading-facts__group-head">
        <span className="natal-reading-facts__marker" aria-hidden="true">
          <Sparkles size={22} strokeWidth={1.8} />
        </span>
        <h3>{group.title}</h3>
      </div>
      <dl className="natal-reading-facts__list natal-reading-facts__list--primary">
        {group.items.map((item) => {
          const Icon = zodiacIconForFact(item) ?? iconForPrimaryFact(item.label)
          return (
            <div className={primaryFactItemClassName(item.label)} key={`${group.title}-${item.label}-${item.value}`}>
              <span className="natal-reading-facts__item-icon" aria-hidden="true">
                <Icon width={21} height={21} strokeWidth={1.8} />
              </span>
              <dt>{item.label}</dt>
              <dd>
                <span className={primaryFactBadgeClassName(group.title)}>
                  <strong>{item.value}</strong>
                </span>
                {item.detail ? <span className={detailFactBadgeClassName(group.title)}>{item.detail}</span> : null}
              </dd>
            </div>
          )
        })}
      </dl>
    </section>
  )
}

function NatalCalculationGroupPanel({ group }: { group: NatalCalculationFactsViewModel["groups"][number] }) {
  const panelId = useId()
  const [isExpanded, setIsExpanded] = useState(false)
  const Marker = markerForGroup(group.title)
  const visibleItems = isExpanded ? group.items : group.items.slice(0, SECONDARY_FACTS_VISIBLE_COUNT)
  const canExpand = group.items.length > SECONDARY_FACTS_VISIBLE_COUNT

  return (
    <section className={groupClassName(group.title)} aria-label={group.title}>
      <div className="natal-reading-facts__group-head">
        <span className="natal-reading-facts__marker" aria-hidden="true">
          <Marker size={22} strokeWidth={1.8} />
        </span>
        <h3>{group.title}</h3>
      </div>
      <dl className="natal-reading-facts__list" id={panelId}>
        {visibleItems.map((item) => (
          <div className="natal-reading-facts__item" key={`${group.title}-${item.label}-${item.value}`}>
            <dt>{item.label}</dt>
            <dd>
              <span className={primaryFactBadgeClassName(group.title)}>
                <strong>{item.value}</strong>
              </span>
              {item.detail ? <span className={detailFactBadgeClassName(group.title)}>{item.detail}</span> : null}
            </dd>
          </div>
        ))}
      </dl>
      {canExpand ? (
        <button
          aria-controls={panelId}
          aria-expanded={isExpanded}
          className="natal-reading-facts__more"
          type="button"
          onClick={() => setIsExpanded((current) => !current)}
        >
          {expandLabelForGroup(group.title, isExpanded)}
          <ArrowRight size={16} aria-hidden="true" />
        </button>
      ) : null}
    </section>
  )
}

function NatalCalculationMethodsPanel({ facts }: { facts: NatalCalculationFactsViewModel }) {
  if (facts.methods.length === 0) return null

  return (
    <section className="natal-reading-facts__methods" aria-label="Système et méthodes de calcul">
      <div className="natal-reading-facts__methods-head">
        <span className="natal-reading-facts__marker" aria-hidden="true">
          <Settings size={22} strokeWidth={1.8} />
        </span>
        <h3>Système & méthodes de calcul</h3>
      </div>
      <dl className="natal-reading-facts__methods-list">
        {facts.methods.map((method) => {
          const Icon = iconForMethod(method.label)
          return (
            <div className={methodClassName(method.label)} key={`${method.label}-${method.value}`}>
              <span className="natal-reading-facts__method-icon" aria-hidden="true">
                <Icon size={22} strokeWidth={1.8} />
              </span>
              <dt>{method.label}</dt>
              <dd>
                <strong>{method.value}</strong>
                {method.detail ? <span>{method.detail}</span> : null}
              </dd>
            </div>
          )
        })}
      </dl>
    </section>
  )
}

function NatalCalculationNotice() {
  return (
    <p className="natal-reading-facts__notice">
      <Info size={16} aria-hidden="true" />
      Ces calculs sont effectués selon les normes astrologiques traditionnelles. Les interprétations peuvent varier selon l'approche.
    </p>
  )
}

function NatalReadingFactsDetails({ facts }: { facts: NatalCalculationFactsViewModel }) {
  const primaryGroup = facts.groups.find((group) => group.title === "Repères principaux")
  const secondaryGroups = facts.groups.filter((group) => group.title !== "Repères principaux")
  const hasGroups = Boolean(primaryGroup) || secondaryGroups.length > 0
  const gridClassName =
    primaryGroup && secondaryGroups.length === 0
      ? "natal-reading-facts__grid natal-reading-facts__grid--single"
      : "natal-reading-facts__grid"

  return (
    <section className="natal-reading-facts" aria-labelledby="natal-reading-facts-title" id={CALCULATION_FACTS_SECTION_ID}>
      <NatalCalculationFactsHeader sourceLabel={facts.sourceLabel} />
      <div className="natal-reading-facts__content">
        {hasGroups ? (
          <div className={gridClassName}>
            {primaryGroup ? <NatalPrimaryFactsPanel group={primaryGroup} /> : null}
            {secondaryGroups.length > 0 ? (
              <div className="natal-reading-facts__secondary-grid">
                {secondaryGroups.map((group) => (
                  <NatalCalculationGroupPanel group={group} key={group.title} />
                ))}
              </div>
            ) : null}
          </div>
        ) : null}
        <NatalCalculationMethodsPanel facts={facts} />
        <NatalCalculationNotice />
      </div>
    </section>
  )
}

function NatalReadingHero({ reading, showSummary }: { reading: NatalInterpretationViewModel; showSummary: boolean }) {
  return (
    <header className="natal-reading-hero">
      <div className="natal-reading-hero__symbol" aria-hidden="true">
        <img className="natal-reading-hero__logo" src={natalLogoSrc} alt="" />
      </div>
      <div className="natal-reading-hero__content">
        <nav className="natal-reading-hero__breadcrumb" aria-label="Fil d'Ariane">
          <span>Accueil</span>
          <span>Mon thème natal</span>
          <span>Lecture</span>
        </nav>
        <span className="natal-section-eyebrow">Interprétation de votre thème natal</span>
        <div className="natal-reading__summary">
          <h1>Thème natal</h1>
          <span className="natal-badge natal-badge--report-status">{reading.label}</span>
        </div>
        {showSummary && reading.shortText ? <p>{reading.shortText}</p> : null}
      </div>
    </header>
  )
}

function NatalReadingMetricsBar({ reading }: { reading: NatalInterpretationViewModel }) {
  const metrics = buildReadingMetrics(reading)

  if (metrics.length === 0) return null

  return (
    <section className="natal-reading-metrics" aria-label="Marqueurs clés du portrait astral">
      {metrics.map((metric) => {
        const Icon = metric.icon
        return (
          <div
            className={`natal-reading-metrics__item ${metricToneClassName(metric.label)}`}
            key={`${metric.label}-${metric.value}-${metric.detail ?? ""}`}
          >
            <span className="natal-reading-metrics__icon" aria-hidden="true">
              <Icon size={24} strokeWidth={1.8} />
            </span>
            <span className="natal-reading-metrics__label">{metric.label}</span>
            <strong>{metric.value}</strong>
            {metric.detail ? <span className="natal-reading-metrics__detail">{metric.detail}</span> : null}
          </div>
        )
      })}
    </section>
  )
}

function NatalReadingSummaryNav({
  activeChapterKey,
  entries,
  extraEntries,
  onNavigate,
}: {
  activeChapterKey: string | null
  entries: MainChapterEntry[]
  extraEntries: SummaryExtraEntry[]
  onNavigate: (anchorId: string, itemKey: string) => void
}) {
  const activeIndex = activeChapterKey?.startsWith("extra-")
    ? entries.length - 1
    : Math.max(0, entries.findIndex((entry) => entry.itemKey === activeChapterKey))
  const completion = progressPercent(activeIndex, entries.length)

  if (entries.length === 0) return null

  return (
    <aside className="natal-reading-summary" aria-label="Sommaire de lecture">
      <div className="natal-reading-summary__header">
        <h2>Sommaire</h2>
        <span>{completion}% complété</span>
        <progress className="natal-reading-summary__bar" max={100} value={completion}>
          {completion}%
        </progress>
      </div>
      <ol className="natal-reading-summary__list">
        {entries.map((entry) => (
          <li className="natal-reading-summary__item" key={entry.progressKey}>
            <button
              aria-label={entry.title.replace(/^\d+\.\s*/, "")}
              aria-current={activeChapterKey === entry.itemKey ? "step" : undefined}
              className={[
                "natal-reading-summary__button",
                entry.themeClassName,
                activeChapterKey === entry.itemKey ? "is-active" : "",
              ].filter(Boolean).join(" ")}
              type="button"
              onClick={() => onNavigate(entry.anchorId, entry.itemKey)}
            >
              <span className="natal-reading-summary__index" aria-hidden="true">{entry.indexLabel}</span>
              <span className="natal-reading-summary__copy">
                <span className="natal-reading-summary__title">{entry.shortTitle}</span>
                {entry.excerpt ? <span className="natal-reading-summary__excerpt">{entry.excerpt}</span> : null}
              </span>
            </button>
          </li>
        ))}
        {extraEntries.map((entry) => (
          <li className="natal-reading-summary__item natal-reading-summary__item--extra" key={entry.key}>
            <a
              aria-current={activeChapterKey === `extra-${entry.key}` ? "step" : undefined}
              className={[
                "natal-reading-summary__extra-link",
                activeChapterKey === `extra-${entry.key}` ? "is-active" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              href={`#${entry.anchorId}`}
              onClick={() => onNavigate(entry.anchorId, `extra-${entry.key}`)}
            >
              <span className="natal-reading-summary__index natal-reading-summary__index--extra" aria-hidden="true">
                {entry.indexLabel}
              </span>
              <span className="natal-reading-summary__copy">
                <span className="natal-reading-summary__title">{entry.title}</span>
                <span className="natal-reading-summary__excerpt">{entry.subtitle}</span>
              </span>
            </a>
          </li>
        ))}
      </ol>
      <a href={`#${READING_GUIDE_SECTION_ID}`} className="natal-reading-summary__guide">
        <span className="natal-reading-summary__guide-label">
          <BookOpen size={18} aria-hidden="true" />
          Guide de lecture
        </span>
        <ChevronRight size={16} aria-hidden="true" />
      </a>
    </aside>
  )
}

function NatalChapterCard({
  chapter,
  anchorId,
  defaultExpanded = true,
  entry,
  itemKey: explicitItemKey,
  themeTitle: explicitThemeTitle,
  compact = false,
}: {
  chapter: NatalReadingChapterViewModel
  anchorId?: string
  defaultExpanded?: boolean
  entry?: MainChapterEntry
  itemKey?: string
  themeTitle?: string
  compact?: boolean
}) {
  const baseId = useId()
  const itemKey = entry?.itemKey ?? explicitItemKey ?? "chapter"
  const themeTitle = entry?.title ?? explicitThemeTitle ?? chapter.title
  const excerpt = entry?.excerpt ?? chapterExcerpt(chapter)
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)
  const [isMetaExpanded, setIsMetaExpanded] = useState(false)
  const resetKey = chapterStateKey(chapter, itemKey)
  const bodyParagraphs = chapterBodyParagraphs(chapter, excerpt)
  const hasMeta = Boolean(chapter.confidenceLabel) || chapter.astroBasis.length > 0 || chapter.safetyFlags.length > 0
  const panelId = chapterPanelId(baseId, itemKey)
  const metaPanelId = `${panelId}-meta`
  const canToggle = bodyParagraphs.length > 0
  const chapterClassName = [
    "natal-reading__chapter",
    hasMeta ? "" : "natal-reading__chapter--no-meta",
    isExpanded ? "natal-reading__chapter--expanded" : "natal-reading__chapter--collapsed",
    compact ? "natal-reading__chapter--compact" : "",
    entry?.themeClassName ?? "",
    hasMeta && isMetaExpanded ? "natal-reading__chapter--meta-expanded" : "",
  ]
    .filter(Boolean)
    .join(" ")

  useEffect(() => {
    setIsExpanded(defaultExpanded)
    setIsMetaExpanded(false)
  }, [defaultExpanded, resetKey])

  return (
    <section className={chapterClassName} id={anchorId}>
      <div className="natal-reading__chapter-main">
        <div className="natal-reading__chapter-head">
          {entry ? <span className="natal-reading__chapter-index" aria-hidden="true">{entry.indexLabel}</span> : null}
          <div className="natal-reading__chapter-title">
            <h3>{themeTitle}</h3>
            <span className="natal-section-eyebrow">Lecture guidée</span>
          </div>
          {entry ? (
            <span className="natal-reading__chapter-time">
              <Clock size={14} aria-hidden="true" />
              {entry.readTimeLabel}
            </span>
          ) : null}
          {canToggle ? (
            <button
              aria-controls={panelId}
              aria-expanded={isExpanded}
              aria-label={`${isExpanded ? "Réduire" : "Ouvrir"} ${chapter.title}`}
              className="natal-reading__chapter-collapse"
              type="button"
              onClick={() => setIsExpanded((current) => !current)}
            >
              {isExpanded ? <ChevronUp size={18} aria-hidden="true" /> : <ChevronDown size={18} aria-hidden="true" />}
            </button>
          ) : null}
        </div>
        {excerpt ? (
          <p className="natal-reading__chapter-excerpt">
            <span className="natal-reading__chapter-excerpt-icon" aria-hidden="true">
              <Lightbulb size={20} strokeWidth={1.8} />
            </span>
            <span className="natal-reading__chapter-excerpt-copy">
              <span className="natal-reading__chapter-excerpt-label">À retenir</span>
              <span className="natal-reading__chapter-excerpt-text">{excerpt}</span>
            </span>
          </p>
        ) : null}
        {bodyParagraphs.length > 0 ? (
          <div
            aria-hidden={!isExpanded}
            className={[
              "natal-reading__chapter-body",
              isExpanded ? "natal-reading__chapter-body--expanded" : "natal-reading__chapter-body--collapsed",
            ].join(" ")}
            hidden={!isExpanded}
            id={panelId}
          >
            {bodyParagraphs.map((paragraph, paragraphIndex) => (
              <p className="natal-reading__prose-paragraph" key={`${itemKey}-paragraph-${paragraphIndex}`}>
                {paragraph}
              </p>
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
        {hasMeta ? (
          <button
            aria-controls={metaPanelId}
            aria-expanded={isMetaExpanded}
            className="natal-reading__meta-toggle"
            type="button"
            onClick={() => setIsMetaExpanded((current) => !current)}
          >
            {isMetaExpanded ? "Masquer les repères" : "Afficher les repères"}
          </button>
        ) : null}
      </div>
      {hasMeta ? (
        <aside className="natal-reading__chapter-meta" aria-label={`Repères et évidences pour ${chapter.title}`} id={metaPanelId}>
          {chapter.confidenceLabel ? (
            <span className="natal-badge natal-badge--confidence">{chapter.confidenceLabel}</span>
          ) : null}
          {chapter.astroBasis.length > 0 ? (
            <div className="natal-reading__basis" aria-label={`Repères utilisés pour ${chapter.title}`}>
              <span>Repères & évidences</span>
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
export function NatalAstralReading({ guide, reading, showSummary = true }: NatalAstralReadingProps) {
  const mainChapterEntries = useMemo(
    () =>
      reading.chapters.map((chapter, index) => {
        const itemKey = `chapter-${chapter.code ?? chapter.title}-${index}`
        const title = chapterThemeTitle(chapter)
        return {
          anchorId: chapterAnchorId(itemKey),
          chapter,
          excerpt: chapterExcerpt(chapter),
          indexLabel: String(index + 1),
          itemKey,
          progressKey: `progress-${chapter.code ?? chapter.title}-${index}`,
          readTimeLabel: estimatedReadTime(chapter),
          shortTitle: shortProgressTitle(title, index),
          themeClassName: chapterThemeClassName(index),
          title,
        }
      }),
    [reading.chapters],
  )
  const summaryExtraEntries = useMemo(() => {
    const startIndex = mainChapterEntries.length
    const entries: SummaryExtraEntry[] = []

    if (reading.calculationFacts) {
      entries.push({
        anchorId: CALCULATION_FACTS_SECTION_ID,
        indexLabel: String(startIndex + entries.length + 1),
        key: "calculation-facts",
        subtitle: "Positions, maisons et aspects retenus",
        title: "Éléments du calcul",
      })
    }

    if (reading.explanations.length > 0) {
      entries.push({
        anchorId: CALCULATION_EXPLANATIONS_SECTION_ID,
        indexLabel: String(startIndex + entries.length + 1),
        key: "calculation-explanations",
        subtitle: "Logique utilisée par le moteur",
        title: "Explications du calcul",
      })
    }

    return entries
  }, [mainChapterEntries.length, reading.calculationFacts, reading.explanations.length])

  const summaryTrackedEntries = useMemo<SummaryTrackedEntry[]>(
    () => [
      ...mainChapterEntries.map((entry) => ({ anchorId: entry.anchorId, itemKey: entry.itemKey })),
      ...summaryExtraEntries.map((entry) => ({ anchorId: entry.anchorId, itemKey: `extra-${entry.key}` })),
    ],
    [mainChapterEntries, summaryExtraEntries],
  )
  const [activeSummaryKey, setActiveSummaryKey] = useState<string | null>(summaryTrackedEntries[0]?.itemKey ?? null)

  useEffect(() => {
    setActiveSummaryKey((currentKey) =>
      currentKey && summaryTrackedEntries.some((entry) => entry.itemKey === currentKey)
        ? currentKey
        : summaryTrackedEntries[0]?.itemKey ?? null,
    )
  }, [summaryTrackedEntries])

  useEffect(() => {
    if (!summaryTrackedEntries.length || typeof window === "undefined") return undefined

    let frameId = 0

    const updateActiveChapterFromViewport = () => {
      const viewportAnchor = Math.min(180, window.innerHeight * 0.28)
      const measuredChapters = summaryTrackedEntries.flatMap((entry) => {
        const element = document.getElementById(entry.anchorId)
        if (!element) return []
        const rect = element.getBoundingClientRect()
        return [{ entry, rect }]
      })
      if (measuredChapters.length === 0) return

      const orderedChapters = [...measuredChapters].sort((left, right) => left.rect.top - right.rect.top)
      const visibleChapter = orderedChapters
        .filter(({ rect }) => rect.bottom > viewportAnchor && rect.top < window.innerHeight)
        .sort((left, right) => Math.abs(left.rect.top - viewportAnchor) - Math.abs(right.rect.top - viewportAnchor))[0]
      const nextKey =
        visibleChapter?.entry.itemKey ??
        (viewportAnchor < orderedChapters[0].rect.top
          ? orderedChapters[0].entry.itemKey
          : orderedChapters[orderedChapters.length - 1]?.entry.itemKey)
      if (nextKey) setActiveSummaryKey(nextKey)
    }

    const scheduleUpdate = () => {
      window.cancelAnimationFrame(frameId)
      frameId = window.requestAnimationFrame(updateActiveChapterFromViewport)
    }

    scheduleUpdate()
    window.addEventListener("scroll", scheduleUpdate, { passive: true })
    window.addEventListener("resize", scheduleUpdate)

    return () => {
      window.cancelAnimationFrame(frameId)
      window.removeEventListener("scroll", scheduleUpdate)
      window.removeEventListener("resize", scheduleUpdate)
    }
  }, [summaryTrackedEntries])

  function scrollToChapter(anchorId: string, itemKey: string) {
    setActiveSummaryKey(itemKey)
    document.getElementById(anchorId)?.scrollIntoView({ behavior: "smooth", block: "start" })
  }

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
      <div className="natal-reading__layout">
        <NatalReadingSummaryNav
          activeChapterKey={activeSummaryKey}
          entries={mainChapterEntries}
          extraEntries={summaryExtraEntries}
          onNavigate={scrollToChapter}
        />
        <div className="natal-reading__main">
          <NatalReadingHero reading={reading} showSummary={showSummary} />
          <NatalReadingMetricsBar reading={reading} />

          {reading.isPartial ? (
            <p className="natal-reading__precision-note natal-reading__partial-alert" role="alert">
              Thème partiel : certaines données de naissance manquent ou ne sont pas assez fiables. L'ascendant, les
              maisons et certains angles peuvent être absents ou limités.
            </p>
          ) : null}

          {mainChapterEntries.length > 0 ? (
            <div className="natal-reading__chapters">
              {mainChapterEntries.map((entry, index) => (
                <NatalChapterCard
                  anchorId={entry.anchorId}
                  chapter={entry.chapter}
                  defaultExpanded={index < OPEN_MAIN_CHAPTER_COUNT}
                  entry={entry}
                  key={entry.itemKey}
                />
              ))}
            </div>
          ) : reading.explanations.length === 0 ? (
            <p className="natal-card__lead">La lecture est disponible mais ne contient pas encore de chapitres publics.</p>
          ) : null}

          {reading.calculationFacts ? <NatalReadingFactsDetails facts={reading.calculationFacts} /> : null}

          {reading.explanations.length > 0 ? (
            <section
              className="natal-reading-explanations"
              aria-labelledby="natal-reading-explanations-title"
              id={CALCULATION_EXPLANATIONS_SECTION_ID}
            >
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
          {guide}
        </div>
      </div>
    </article>
  )
}
