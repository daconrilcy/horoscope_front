import { useThemeSafe } from "../state/ThemeProvider"

/**
 * LCG (Linear Congruential Generator) constants.
 * These are the constants used by glibc's rand() function.
 * @see https://en.wikipedia.org/wiki/Linear_congruential_generator
 */
export const LCG_MULTIPLIER = 1103515245
export const LCG_INCREMENT = 12345
export const LCG_MODULUS = 0x7fffffff

/** Minimum star radius in viewBox units */
export const STAR_RADIUS_MIN = 0.3

/** Maximum additional radius (total max = MIN + RANGE = 1.1) */
export const STAR_RADIUS_RANGE = 0.8

/** Minimum star opacity */
export const STAR_OPACITY_MIN = 0.3

/** Maximum additional opacity (total max = MIN + RANGE = 0.8) */
export const STAR_OPACITY_RANGE = 0.5

/** SVG viewBox size (stars are positioned within 0-VIEWBOX_SIZE range) */
export const VIEWBOX_SIZE = 100

/**
 * Creates a seeded pseudo-random number generator using LCG algorithm.
 * @param seed - Initial seed value
 * @returns Function that returns next random number in [0, 1)
 */
export function seededRandom(seed: number): () => number {
  let state = seed
  return () => {
    state = (state * LCG_MULTIPLIER + LCG_INCREMENT) & LCG_MODULUS
    return state / LCG_MODULUS
  }
}

/** Represents a star in the starfield background */
export interface Star {
  id: string
  cx: number
  cy: number
  r: number
  opacity: number
}

/**
 * Generates an array of stars with deterministic positions based on seed.
 * @param count - Number of stars to generate
 * @param seed - Seed for the random number generator
 * @returns Array of Star objects with random positions, sizes, and opacities
 */
export function generateStars(count: number, seed: number): Star[] {
  const random = seededRandom(seed)
  const stars: Star[] = []
  for (let i = 0; i < count; i++) {
    stars.push({
      id: `star-${seed}-${i}`,
      cx: random() * VIEWBOX_SIZE,
      cy: random() * VIEWBOX_SIZE,
      r: STAR_RADIUS_MIN + random() * STAR_RADIUS_RANGE,
      opacity: STAR_OPACITY_MIN + random() * STAR_OPACITY_RANGE,
    })
  }
  return stars
}

/** Number of stars rendered in the starfield background */
export const STAR_COUNT = 80

/** Seed for deterministic star generation (ensures consistent positions) */
export const STAR_SEED = 12345

/** Pre-generated array of stars using STAR_COUNT and STAR_SEED */
export const STARS = generateStars(STAR_COUNT, STAR_SEED)

/**
 * Renders a starfield background for dark theme.
 * Only visible when theme is "dark", returns null otherwise.
 * Uses pre-generated deterministic star positions for consistent rendering.
 */
export function StarfieldBackground() {
  const themeContext = useThemeSafe()
  const theme = themeContext?.theme ?? "light"

  if (theme !== "dark") {
    return null
  }

  return (
    <div
      aria-hidden="true"
      className="starfield-bg"
    >
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${VIEWBOX_SIZE} ${VIEWBOX_SIZE}`}
        preserveAspectRatio="xMidYMid slice"
        xmlns="http://www.w3.org/2000/svg"
      >
        {STARS.map((star) => (
          <circle
            key={star.id}
            cx={star.cx}
            cy={star.cy}
            r={star.r}
            fill="var(--star-fill)"
            opacity={star.opacity}
          />
        ))}
      </svg>
    </div>
  )
}
