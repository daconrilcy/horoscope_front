import type { DailyPredictionResponse } from '../types/dailyPrediction'
import type { Lang } from '../i18n/predictions'
import { getPredictionMessage } from './predictionI18n'
import { getDomainLabel } from '../i18n/horoscope_copy'

export interface DailyAdviceCardModel {
  title: string;
  advice: string;
  emphasis: string;
}

export function buildDailyAdviceCardModel(
  prediction: DailyPredictionResponse,
  lang: Lang
): DailyAdviceCardModel {
  const llmAdvice = prediction.daily_advice
  if (llmAdvice?.advice || llmAdvice?.emphasis) {
    return {
      title: getPredictionMessage('daily_advice_title', lang),
      advice: llmAdvice?.advice || buildFallbackAdvice(prediction, lang),
      emphasis: llmAdvice?.emphasis || buildFallbackEmphasis(prediction, lang),
    }
  }

  return {
    title: getPredictionMessage('daily_advice_title', lang),
    advice: buildFallbackAdvice(prediction, lang),
    emphasis: buildFallbackEmphasis(prediction, lang),
  }
}

function buildFallbackAdvice(prediction: DailyPredictionResponse, lang: Lang): string {
  const bestWindow = prediction.best_window?.time_range
  const focus = getPrimaryDomainLabel(prediction, lang)
  const watchout = getWatchoutLabel(prediction, lang)

  if (lang === 'en') {
    if (bestWindow && watchout) {
      return `Use the ${bestWindow} window to move forward on ${focus}, and avoid forcing decisions when tension rises around ${watchout}.`
    }
    if (bestWindow) {
      return `Use the ${bestWindow} window to make progress on ${focus}; the rest of the day is better for adjustment than pushing.`
    }
    if (watchout) {
      return `Keep your attention on ${focus}, but stay flexible if the day becomes more sensitive around ${watchout}.`
    }
    return `Follow the day's strongest momentum around ${focus}, and prefer well-timed actions over rushed reactions.`
  }

  if (bestWindow && watchout) {
    return `Appuyez-vous sur le créneau ${bestWindow} pour avancer sur ${focus}, puis évitez de forcer quand la tension remonte autour de ${watchout}.`
  }
  if (bestWindow) {
    return `Servez-vous du créneau ${bestWindow} pour faire avancer ${focus} ; le reste de la journée demande surtout du dosage et du bon timing.`
  }
  if (watchout) {
    return `Gardez le cap sur ${focus}, tout en restant souple si la journée devient plus sensible autour de ${watchout}.`
  }
  return `Misez sur la dynamique du jour autour de ${focus}, et privilégiez les gestes bien placés aux réactions trop rapides.`
}

function buildFallbackEmphasis(prediction: DailyPredictionResponse, lang: Lang): string {
  const bestWindow = prediction.best_window?.time_range
  const watchout = getWatchoutLabel(prediction, lang)

  if (lang === 'en') {
    if (bestWindow) {
      return `Your timing matters most around ${bestWindow}.`
    }
    if (watchout) {
      return `Stay measured around ${watchout}.`
    }
    return 'Move with timing, not pressure.'
  }

  if (bestWindow) {
    return `Votre timing compte surtout vers ${bestWindow}.`
  }
  if (watchout) {
    return `Restez mesuré autour de ${watchout}.`
  }
  return 'Le bon rythme vaut mieux que la précipitation.'
}

function getPrimaryDomainLabel(prediction: DailyPredictionResponse, lang: Lang): string {
  const key =
    prediction.day_climate?.top_domains?.[0] ||
    prediction.domain_ranking?.[0]?.key ||
    prediction.turning_point?.affected_domains?.[0]

  return key ? getDomainLabel(key, lang).toLowerCase() : lang === 'en' ? 'your priorities' : 'vos priorités'
}

function getWatchoutLabel(prediction: DailyPredictionResponse, lang: Lang): string | null {
  const key = prediction.day_climate?.watchout
  return key ? getDomainLabel(key, lang).toLowerCase() : null
}
