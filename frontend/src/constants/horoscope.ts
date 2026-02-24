/**
 * Static horoscope data per Epic 17 specifications (§13).
 * Shared between TodayPage and integration tests to avoid brittle assertions.
 */
export const STATIC_HOROSCOPE = {
  sign: '♒',
  signName: 'Verseau',
  headline: "Ta journée s'éclaircit après 14h.",
} as const

export const TODAY_DATE_FORMATTER = new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'short' })
