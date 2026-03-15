/**
 * Canonical application locale type.
 * All other language types should be aliases of this.
 */
export type AppLocale = "fr" | "en" | "es"

/**
 * Default locale for the application.
 */
export const DEFAULT_LOCALE: AppLocale = "fr"

/**
 * List of all supported locales.
 */
export const SUPPORTED_LOCALES: AppLocale[] = ["fr", "en", "es"]
