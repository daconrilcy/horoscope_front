// Porte le champ d'etoiles SVG canonique du theme dark global.
import { useThemeSafe } from "../state/ThemeProvider"

/** Constantes du generateur pseudo-aleatoire deterministe LCG. */
export const LCG_MULTIPLIER = 1103515245
export const LCG_INCREMENT = 12345
export const LCG_MODULUS = 0x7fffffff

/** Rayon minimal d'une etoile en unites de viewBox. */
export const STAR_RADIUS_MIN = 0.16

/** Amplitude maximale ajoutee au rayon minimal. */
export const STAR_RADIUS_RANGE = 0.24

/** Opacite minimale d'une etoile. */
export const STAR_OPACITY_MIN = 0.24

/** Amplitude maximale ajoutee a l'opacite minimale. */
export const STAR_OPACITY_RANGE = 0.58

/** Taille du viewBox SVG pour placer les couches astrales. */
export const VIEWBOX_SIZE = 100

/**
 * Cree un generateur pseudo-aleatoire stable pour produire le meme ciel a chaque rendu.
 */
export function seededRandom(seed: number): () => number {
  let state = seed
  return () => {
    state = (state * LCG_MULTIPLIER + LCG_INCREMENT) & LCG_MODULUS
    return state / LCG_MODULUS
  }
}

/** Etoile affichee dans le fond astral. */
export interface Star {
  id: string
  cx: number
  cy: number
  r: number
  opacity: number
  className: string
}

/** Etoile filante rare et decorrellee du champ d'etoiles principal. */
export interface ShootingStar {
  id: string
  x1: number
  y1: number
  x2: number
  y2: number
  opacity: number
  className: string
}

/**
 * Genere un champ d'etoiles plus dense en haut et sur les bords pour liberer le centre de lecture.
 */
export function generateStars(count: number, seed: number): Star[] {
  const random = seededRandom(seed)
  const stars: Star[] = []
  for (let i = 0; i < count; i++) {
    const upperBias = Math.pow(random(), 1.72) * VIEWBOX_SIZE
    const edgeBias = random() < 0.46 ? random() * 18 : VIEWBOX_SIZE - random() * 18
    const usesEdgeLane = random() < 0.34
    const cy = Math.min(VIEWBOX_SIZE - 1, upperBias)
    const cx = usesEdgeLane ? edgeBias : random() * VIEWBOX_SIZE
    const depth = cy < 42 ? "near" : cy < 70 ? "mid" : "far"

    stars.push({
      id: `star-${seed}-${i}`,
      cx,
      cy,
      r: STAR_RADIUS_MIN + random() * STAR_RADIUS_RANGE,
      opacity: STAR_OPACITY_MIN + random() * STAR_OPACITY_RANGE,
      className: `starfield-bg__star starfield-bg__star--${depth}`,
    })
  }
  return stars
}

/** Genere des etoiles filantes rares et fines, sans ajouter de logique d'animation JS. */
export function generateShootingStars(count: number, seed: number): ShootingStar[] {
  const random = seededRandom(seed)
  const shootingStars: ShootingStar[] = []
  for (let i = 0; i < count; i++) {
    const x1 = 8 + random() * 70
    const y1 = 6 + random() * 42
    const length = 11 + random() * 13
    shootingStars.push({
      id: `shooting-${seed}-${i}`,
      x1,
      y1,
      x2: Math.min(VIEWBOX_SIZE, x1 + length),
      y2: Math.max(0, y1 - length * 0.28),
      opacity: 0.28 + random() * 0.24,
      className: `starfield-bg__shooting starfield-bg__shooting--${i + 1}`,
    })
  }
  return shootingStars
}

/** Nombre d'etoiles rendu dans le fond astral. */
export const STAR_COUNT = 118

/** Graine deterministe du champ d'etoiles. */
export const STAR_SEED = 12345

/** Nombre d'etoiles filantes rares. */
export const SHOOTING_STAR_COUNT = 3

/** Graine deterministe des etoiles filantes. */
export const SHOOTING_STAR_SEED = 98765

/** Champ d'etoiles pregenere pour limiter le travail au rendu. */
export const STARS = generateStars(STAR_COUNT, STAR_SEED)

/** Etoiles filantes pregenerees pour conserver un DOM leger et stable. */
export const SHOOTING_STARS = generateShootingStars(SHOOTING_STAR_COUNT, SHOOTING_STAR_SEED)

/**
 * Rend le fond astral SVG uniquement quand le theme dark est actif.
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
        <defs>
          <linearGradient id="starfield-milky-dawn" x1="5%" y1="68%" x2="92%" y2="12%">
            <stop offset="0%" stopColor="var(--starfield-milky-start)" stopOpacity="0" />
            <stop offset="42%" stopColor="var(--starfield-milky-core)" stopOpacity="0.22" />
            <stop offset="100%" stopColor="var(--starfield-milky-end)" stopOpacity="0" />
          </linearGradient>
          <linearGradient id="starfield-shooting-tail" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="var(--starfield-shooting-tail)" stopOpacity="0" />
            <stop offset="62%" stopColor="var(--starfield-shooting-tail)" stopOpacity="0.36" />
            <stop offset="100%" stopColor="var(--starfield-shooting-core)" stopOpacity="0.82" />
          </linearGradient>
        </defs>
        <path
          className="starfield-bg__milky-way"
          d="M -8 72 C 14 56, 34 49, 52 39 C 70 29, 82 17, 108 10"
          fill="none"
          stroke="url(#starfield-milky-dawn)"
          strokeWidth="18"
          strokeLinecap="round"
        />
        {STARS.map((star) => (
          <circle
            key={star.id}
            className={star.className}
            cx={star.cx}
            cy={star.cy}
            r={star.r}
            fill="var(--star-fill)"
            opacity={star.opacity}
          />
        ))}
        {SHOOTING_STARS.map((shootingStar) => (
          <line
            key={shootingStar.id}
            className={shootingStar.className}
            x1={shootingStar.x1}
            y1={shootingStar.y1}
            x2={shootingStar.x2}
            y2={shootingStar.y2}
            stroke="url(#starfield-shooting-tail)"
            strokeWidth="0.34"
            strokeLinecap="round"
            opacity={shootingStar.opacity}
          />
        ))}
      </svg>
    </div>
  )
}
