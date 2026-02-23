import type { AstrologyLang } from "../i18n/astrology"
import { CONTEXT_TRUNCATE_LENGTH } from "../types/consultation"

export function generateSimpleInterpretation(context: string, lang: AstrologyLang): string {
  const truncatedContext = context.length > CONTEXT_TRUNCATE_LENGTH
    ? `${context.slice(0, CONTEXT_TRUNCATE_LENGTH)}...`
    : context
  const interpretations: Record<AstrologyLang, string> = {
    fr: `Votre question "${truncatedContext}" mérite une réflexion approfondie. Les astres vous invitent à faire confiance à votre intuition tout en restant ancré(e) dans la réalité. Prenez le temps de peser le pour et le contre avant de prendre une décision importante.`,
    en: `Your question "${truncatedContext}" deserves deep reflection. The stars invite you to trust your intuition while staying grounded in reality. Take time to weigh the pros and cons before making an important decision.`,
    es: `Su pregunta "${truncatedContext}" merece una reflexión profunda. Las estrellas le invitan a confiar en su intuición mientras permanece anclado en la realidad. Tómese el tiempo para sopesar los pros y los contras antes de tomar una decisión importante.`,
  }
  return interpretations[lang] ?? interpretations.fr
}
