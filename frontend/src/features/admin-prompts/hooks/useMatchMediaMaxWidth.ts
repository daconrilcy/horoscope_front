// Isole le hook responsive du domaine admin-prompts pour reduire la page route monolithique.
import { useEffect, useState } from "react"

/** Observe une media query max-width uniquement quand le comportement responsive est actif. */
export function useMatchMediaMaxWidth(maxPx: number, enabled: boolean): boolean {
  const [matches, setMatches] = useState(() => {
    if (!enabled || typeof window === "undefined" || typeof window.matchMedia !== "function") {
      return false
    }
    return window.matchMedia(`(max-width: ${maxPx}px)`).matches
  })
  useEffect(() => {
    if (!enabled || typeof window.matchMedia !== "function") {
      setMatches(false)
      return
    }
    const mq = window.matchMedia(`(max-width: ${maxPx}px)`)
    const apply = () => setMatches(mq.matches)
    apply()
    mq.addEventListener("change", apply)
    return () => mq.removeEventListener("change", apply)
  }, [enabled, maxPx])
  return matches
}
