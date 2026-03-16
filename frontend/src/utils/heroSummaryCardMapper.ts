import type { DailyPredictionResponse } from '../types/dailyPrediction'
import type { Lang } from '../i18n/predictions'
import type { ZodiacSign } from '../components/astro/zodiacPatterns'
import { getToneLabel, getPredictionMessage, getCategoryLabel, getCategoryMeta } from './predictionI18n'
import { getLocale } from './locale'

export type HeroTitlePart = { text: string; highlight?: boolean }
export type HeroTag = { id: string; label: string; icon?: string }

export interface HeroInsight {
  label: string
  time: string
  categoryLabel: string | null
}

export interface HeroSummaryCardModel {
  titleParts: HeroTitlePart[]
  subtitle: string | null
  astroTheme: string | null
  calibrationNote: string | null
  insight: HeroInsight | null
  tags: HeroTag[]
  tone: string | null
  astroProps: {
    sign: ZodiacSign
    userId: string
    dateKey: string
    dayScore: number
  }
}

function buildAstroThemeText(
  prediction: DailyPredictionResponse,
  lang: Lang,
): string | null {
  const topCats = prediction.summary.top_categories.slice(0, 2)
  if (topCats.length === 0) return null
  const catLabels = topCats.map(c => getCategoryLabel(c, lang))
  const toneLabel = getToneLabel(prediction.summary.overall_tone, lang).toLowerCase()
  return lang === 'fr'
    ? `Journée ${toneLabel}, principalement orientée sur ${catLabels.join(' et ')}.`
    : `A ${toneLabel} day, primarily oriented toward ${catLabels.join(' and ')}.`
}

export function buildHeroSummaryCardModel(
  prediction: DailyPredictionResponse,
  sign: ZodiacSign,
  userId: string,
  dayScore: number,
  lang: Lang
): HeroSummaryCardModel {
  const locale = getLocale(lang)
  const toneLabel = getToneLabel(prediction.summary.overall_tone, lang)

  // Title: "Une journée [toneLabel]" ou "A [toneLabel] day" en EN
  const titlePrefix = lang === 'fr' ? 'Une journée ' : 'A '
  const titleParts: HeroTitlePart[] = [
    { text: titlePrefix },
    { text: toneLabel, highlight: true },
  ]

  // Subtitle = overall_summary (texte narratif IA principal)
  const subtitle = prediction.summary.overall_summary || null

  // Thème astro du jour (zone dédiée, pas la calibration)
  const astroTheme = buildAstroThemeText(prediction, lang)

  // Calibration note
  const calibrationNote = prediction.meta.is_provisional_calibration
    ? (prediction.summary.calibration_note || getPredictionMessage('provisional_calibration', lang))
    : null

  // Insight = best_window formatée
  let insight: HeroInsight | null = null
  if (prediction.summary.best_window) {
    const { start_local, end_local, dominant_category } = prediction.summary.best_window
    const start = new Date(start_local).toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' })
    const end = new Date(end_local).toLocaleTimeString(locale, { hour: '2-digit', minute: '2-digit' })
    insight = {
      label: getPredictionMessage('best_window', lang),
      time: `${start} – ${end}`,
      categoryLabel: dominant_category
        ? `${getPredictionMessage('dominant', lang)} : ${getCategoryLabel(dominant_category, lang)}`
        : null,
    }
  }

  // Tags: top 3–4 catégories avec icônes
  const tags: HeroTag[] = prediction.summary.top_categories.slice(0, 4).map(code => {
    const meta = getCategoryMeta(code, lang)
    return { id: code, label: meta.label, icon: meta.icon }
  })

  return {
    titleParts,
    subtitle,
    astroTheme,
    calibrationNote,
    insight,
    tags,
    tone: prediction.summary.overall_tone,
    astroProps: {
      sign,
      userId,
      dateKey: prediction.meta.date_local,
      dayScore,
    },
  }
}
