/**
 * Extracts a display name from user data.
 * Fallback logic: email prefix (e.g. "john.doe" from "john.doe@example.com").
 * Future: Will prioritize 'username' field once added to the backend schema.
 */
export function getUserDisplayName(user?: { email?: string; username?: string } | null): string {
  if (user?.username) return user.username
  if (!user?.email) return 'Utilisateur'
  
  // Handle email prefix (e.g. "john.doe@example.com" -> "john.doe")
  const prefix = user.email.split('@')[0]
  if (!prefix) return 'Utilisateur'
  
  // Clean up prefix if it's just dots or underscores
  const cleanPrefix = prefix.replace(/[._]+$/, '').trim()
  return cleanPrefix || 'Utilisateur'
}

/**
 * Generates initials from a display name.
 * Handles spaces, dots, and underscores.
 */
export function getInitials(name: string): string {
  const safeName = (name || "U").trim()
  if (!safeName) return "U"
  
  // Split by space, dot, or underscore, filtering out empty parts
  const parts = safeName.split(/[\s._]+/).filter(Boolean)
  if (parts.length >= 2) {
    const first = parts[0]?.[0] || ""
    const last = parts[parts.length - 1]?.[0] || ""
    if (first && last) return (first + last).toUpperCase()
  }
  
  const firstChar = safeName[0]
  if (firstChar === "." || !firstChar) return "U"
  
  return firstChar.toUpperCase()
}
