import type { AstrologyLang } from "../i18n/astrology"

const localeMap: Record<AstrologyLang, string> = {
  fr: "fr-FR",
  en: "en-US",
  es: "es-ES",
}

export function getLocale(lang: AstrologyLang): string {
  return localeMap[lang]
}
