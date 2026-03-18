import type { DailyPredictionResponse } from '../types/dailyPrediction'
import type { DailyAgendaSlot } from './dailyAstrology'
import type { Lang } from '../i18n/predictions'
import type { DayPeriodKey } from '../types/dayTimeline'
import type { FocusMomentCardModel, FocusMomentTag } from '../types/detailScores'
import { getCategoryMeta, getPredictionMessage, humanizeTurningPointSemantic } from './predictionI18n'

const PERIOD_SLOT_RANGES: Record<DayPeriodKey, [number, number]> = {
  nuit: [0, 3],
  matin: [3, 6],
  apres_midi: [6, 9],
  soiree: [9, 12]
}

/**
 * Construit le modèle de données pour FocusMomentCard.
 * AC 4: affiche le slot 2h le plus significatif de la période sélectionnée (ou de la journée).
 */
export function buildFocusMomentCardModel(
  selectedPeriodKey: DayPeriodKey | null,
  agendaSlots: DailyAgendaSlot[],
  prediction: DailyPredictionResponse,
  lang: Lang
): FocusMomentCardModel {
  // 1. Déterminer les slots à considérer
  let startIdx = 0
  let endIdx = agendaSlots.length
  
  if (selectedPeriodKey) {
    const [s, e] = PERIOD_SLOT_RANGES[selectedPeriodKey]
    startIdx = s
    endIdx = e
  }

  const candidateSlots = agendaSlots.slice(startIdx, endIdx)

  // 2. Trouver le "meilleur" slot (turning point prioritaire, sinon premier avec catégories)
  let bestCandidateIdx = candidateSlots.findIndex(s => s.hasTurningPoint)
  if (bestCandidateIdx === -1) {
    bestCandidateIdx = candidateSlots.findIndex(s => s.topCategories.length > 0)
  }
  
  // Si rien trouvé dans la période (ou si pas de période et rien dans la journée)
  if (bestCandidateIdx === -1) {
    if (selectedPeriodKey) {
        // On retombe sur le meilleur de la journée complète si la période est vide
        return buildFocusMomentCardModel(null, agendaSlots, prediction, lang)
    }
    bestCandidateIdx = 0
  }

  const finalIdxInCandidates = bestCandidateIdx
  const globalSlotIdx = startIdx + finalIdxInCandidates
  const bestSlot = agendaSlots[globalSlotIdx]
  
  // 3. Formater le timeRange (ex: "14:00 – 16:00")
  const startHour = globalSlotIdx * 2
  const endHour = (globalSlotIdx + 1) * 2
  const timeRange = `${String(startHour).padStart(2, '0')}:00 – ${String(endHour).padStart(2, '0')}:00`

  // 4. Tags
  const tags: FocusMomentTag[] = bestSlot.topCategories.slice(0, 3).map(code => ({
    code,
    label: getCategoryMeta(code, lang).label
  }))

  // 5. Description et Titre
  // On cherche le bloc de timeline correspondant à ce slot pour avoir le summary
  const slotStartIso = `${prediction.meta.date_local}T${String(startHour).padStart(2, '0')}:00:00`
  const matchingBlock = prediction.timeline.find(b => b.start_local <= slotStartIso && b.end_local > slotStartIso)

  // TP pertinent : cherche dans la période sélectionnée, sinon prend le premier du jour
  // (même logique que keyPointsSectionMapper — non contraint au slot de 2h)
  let relevantTP = prediction.turning_points[0] as typeof prediction.turning_points[number] | undefined
  if (selectedPeriodKey) {
    const [pStart, pEnd] = PERIOD_SLOT_RANGES[selectedPeriodKey]
    const pStartIso = `${prediction.meta.date_local}T${String(pStart * 2).padStart(2, '0')}:00:00`
    const pEndIso   = `${prediction.meta.date_local}T${String(pEnd   * 2).padStart(2, '0')}:00:00`
    const periodTP = prediction.turning_points.find(
      tp => tp.occurred_at_local >= pStartIso && tp.occurred_at_local < pEndIso
    )
    relevantTP = periodTP ?? prediction.turning_points[0]
  }

  // Titre : même source que key-point-card__label (semantic.cause || semantic.title)
  // Description : explication sémantique de la transition, ou summary en fallback
  let title = getPredictionMessage('focus_moment_default_title', lang)
  let description = getPredictionMessage('no_detail_available', lang)

  if (relevantTP) {
    const semantic = humanizeTurningPointSemantic(relevantTP, lang)
    title = semantic.cause || semantic.title || title
    description = semantic.transition || semantic.implication || matchingBlock?.summary || getPredictionMessage('no_detail_available', lang)
  } else if (matchingBlock?.summary) {
    description = matchingBlock.summary
  }

  return {
    timeRange,
    title,
    tags,
    description,
    ctaLabel: getPredictionMessage('see_details_cta', lang)
  }
}
