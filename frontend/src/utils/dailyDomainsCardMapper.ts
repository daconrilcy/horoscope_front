import type { DailyPredictionCategory } from '../types/dailyPrediction'
import type { DailyDomainsCardModel, DailyDomainScore } from '../types/detailScores'
import type { Lang } from '../i18n/predictions'
import { getCategoryMeta, getPredictionMessage } from './predictionI18n'

/**
 * Construit le modèle de données pour DailyDomainsCard.
 * AC 6: Se base sur les scores de la journée complète (categories).
 */
export function buildDailyDomainsCardModel(
  categories: DailyPredictionCategory[],
  lang: Lang
): DailyDomainsCardModel {
  // On trie par rank (si disponible) ou par note décroissante
  const sorted = [...categories].sort((a, b) => {
    if (a.rank && b.rank) return a.rank - b.rank
    return b.note_20 - a.note_20
  })
  
  const allDomains: DailyDomainScore[] = sorted.map(c => ({
    code: c.code,
    label: getCategoryMeta(c.code, lang).label,
    score: c.note_20,
    percentage: (c.note_20 / 20) * 100
  }))

  return {
    title: getPredictionMessage('domains_title', lang),
    primaryDomains: allDomains.slice(0, 3),
    secondaryDomains: allDomains.slice(3)
  }
}
