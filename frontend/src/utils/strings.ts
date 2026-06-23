/**
 * Normalise les textes destines a l'affichage public.
 */
export function normalizeDisplayText(str: string): string {
  return str.replace(/\u2014/g, "-")
}

/**
 * Normalise recursivement les chaines d'un payload JSON avant affichage.
 */
export function normalizeDisplayValue<T>(value: T): T {
  if (typeof value === "string") {
    return normalizeDisplayText(value) as T
  }
  if (Array.isArray(value)) {
    return value.map((item) => normalizeDisplayValue(item)) as T
  }
  if (value !== null && typeof value === "object") {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, normalizeDisplayValue(item)]),
    ) as T
  }
  return value
}

/**
 * Removes leading digits, dashes, dots, and whitespace from a string.
 * Used to clean numbered or bulleted highlight items from the API.
 * Example: "1. Some highlight" → "Some highlight"
 * Example: "1 - Some highlight" → "Some highlight"
 */
export function stripLeadingNumbering(str: string): string {
  return str.replace(/^[\d\-\.\s]+/, "")
}

/**
 * Removes a leading integer followed by optional dot/spaces from a string.
 * Used to clean numbered list items from the API.
 * Example: "1. Some advice" → "Some advice"
 * Example: "3  Some advice" → "Some advice"
 */
export function stripLeadingNumber(str: string): string {
  return str.replace(/^\d+[\.\s]*/, "")
}
