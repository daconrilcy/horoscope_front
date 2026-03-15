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
