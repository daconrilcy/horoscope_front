// Porte le champ d'etoiles SVG canonique du theme dark global.
import { useThemeSafe } from "../state/ThemeProvider"

/** Constantes du generateur pseudo-aleatoire deterministe LCG. */
export const LCG_MULTIPLIER = 1103515245
export const LCG_INCREMENT = 12345
export const LCG_MODULUS = 0x7fffffff

/** Rayon minimal d'une etoile en unites de viewBox. */
export const STAR_RADIUS_MIN = 0.035

/** Amplitude maximale ajoutee au rayon minimal. */
export const STAR_RADIUS_RANGE = 0.15

/** Opacite minimale d'une etoile. */
export const STAR_OPACITY_MIN = 0.28

/** Amplitude maximale ajoutee a l'opacite minimale. */
export const STAR_OPACITY_RANGE = 0.66

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
  fill: string
}

/** Micro-etoile concentree dans la bande de Voie lactee. */
export type MilkyWayStar = Star

/** Nuage diffus qui porte la matiere vaporeuse de la Voie lactee. */
export interface MilkyWayCloud {
  id: string
  cx: number
  cy: number
  rx: number
  ry: number
  opacity: number
  rotation: number
  className: string
}

/** Etoile rare et nette qui donne un accent cristallin au ciel. */
export type JewelStar = Star

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

function centeredRandom(random: () => number): number {
  return (random() + random() + random() + random()) / 4 - 0.5
}

/**
 * Genere un champ d'etoiles plus dense en haut et sur les bords pour liberer le centre de lecture.
 */
export function generateStars(count: number, seed: number): Star[] {
  const random = seededRandom(seed)
  const stars: Star[] = []
  for (let i = 0; i < count; i++) {
    const layerRoll = random()
    const layer = layerRoll < 0.8 ? "micro" : layerRoll < 0.965 ? "soft" : "accent"
    const usesEdgeLane = random() < 0.36
    const usesMilkyDust = random() < 0.34
    const edgeBias = random() < 0.5 ? random() * 18 : VIEWBOX_SIZE - random() * 18
    let cx = usesEdgeLane ? edgeBias : random() * VIEWBOX_SIZE
    let cy = Math.pow(random(), 2.35) * VIEWBOX_SIZE

    if (usesMilkyDust) {
      const t = random()
      cx = Math.max(0, Math.min(VIEWBOX_SIZE, -12 + t * 64 + (random() - 0.5) * 16))
      cy = Math.max(0, Math.min(VIEWBOX_SIZE, 10 + t * 26 + (random() - 0.5) * 10))
    }

    const isInReadingCorridor = cx > 24 && cx < 76 && cy > 18 && cy < 74
    if (isInReadingCorridor && !usesMilkyDust && random() < 0.84) {
      cx = random() < 0.5 ? random() * 20 : 80 + random() * 20
      cy = Math.pow(random(), 1.7) * 78
    }

    const radiusByLayer = {
      micro: STAR_RADIUS_MIN + random() * 0.04,
      soft: 0.07 + random() * 0.055,
      accent: 0.14 + random() * (STAR_RADIUS_MIN + STAR_RADIUS_RANGE - 0.14),
    }
    const opacityByLayer = {
      micro: 0.34 + random() * 0.34,
      soft: 0.46 + random() * 0.36,
      accent: 0.68 + random() * 0.26,
    }
    const fillByLayer = {
      micro: random() < 0.5 ? "var(--starfield-star-blue)" : random() < 0.78 ? "var(--starfield-star-lavender)" : "var(--starfield-star-violet)",
      soft: random() < 0.48 ? "var(--starfield-star-ice)" : random() < 0.76 ? "var(--starfield-star-lavender)" : "var(--starfield-star-gold)",
      accent: cy > 68 ? "var(--starfield-star-dawn)" : random() < 0.58 ? "var(--starfield-star-ice)" : "var(--starfield-star-blue)",
    }

    stars.push({
      id: `star-${seed}-${i}`,
      cx,
      cy: Math.min(VIEWBOX_SIZE - 1, cy),
      r: radiusByLayer[layer],
      opacity: opacityByLayer[layer],
      className: `starfield-bg__star starfield-bg__star--${layer}`,
      fill: fillByLayer[layer],
    })
  }
  return stars
}

/**
 * Genere la Voie lactee comme une concentration diagonale de micro-etoiles.
 */
export function generateMilkyWayStars(count: number, seed: number): MilkyWayStar[] {
  const random = seededRandom(seed)
  const stars: MilkyWayStar[] = []
  for (let i = 0; i < count; i++) {
    const clusterRoll = random()
    const clusterAnchor = clusterRoll < 0.36 ? 0.2 : clusterRoll < 0.73 ? 0.44 : clusterRoll < 0.91 ? 0.6 : 0.77
    const t = Math.max(0, Math.min(1, clusterAnchor + centeredRandom(random) * 0.48))
    const lowerRightFade = t > 0.64 ? Math.max(0.24, 1 - (t - 0.64) / 0.42) : 1
    const upperFade = t < 0.16 ? 0.42 + t * 3.1 : 1
    const quietGap =
      t > 0.29 && t < 0.37 ? 0.42 :
        t > 0.53 && t < 0.59 ? 0.62 :
          t > 0.69 && t < 0.86 ? 0.34 : 1
    const bandWidth = 6.2 + Math.sin(t * Math.PI) * 13.8 + Math.sin(t * Math.PI * 6.1) * 3.4
    const wave = Math.sin(t * Math.PI * 2.12 + 0.55) * 5.9 + Math.sin(t * Math.PI * 6.9) * 2.8
    const brokenBend = Math.sin(t * Math.PI * 13.5 + 0.8) * 1.9
    const perpendicular = centeredRandom(random) * bandWidth
    const longitudinal = centeredRandom(random) * 10.6
    const cx = Math.max(0, Math.min(VIEWBOX_SIZE, -9 + t * 118 + longitudinal + perpendicular * 1.08 + brokenBend))
    const cy = Math.max(0, Math.min(VIEWBOX_SIZE, 5 + t * 74 + wave + perpendicular * 0.72))
    const layerRoll = random()
    const layer = layerRoll < 0.905 ? "micro" : layerRoll < 0.984 ? "soft" : "accent"
    const fillRoll = random()
    const naturalFade = (0.5 + lowerRightFade * 0.5) * quietGap * upperFade

    stars.push({
      id: `milky-star-${seed}-${i}`,
      cx,
      cy,
      r: layer === "micro"
        ? STAR_RADIUS_MIN + random() * 0.024
        : layer === "soft"
          ? 0.062 + random() * 0.046
          : 0.12 + random() * 0.052,
      opacity: layer === "micro"
        ? Math.max(STAR_OPACITY_MIN, (STAR_OPACITY_MIN + random() * 0.34) * naturalFade)
        : layer === "soft"
          ? Math.max(STAR_OPACITY_MIN, (0.42 + random() * 0.34) * naturalFade)
          : Math.max(STAR_OPACITY_MIN, (0.68 + random() * 0.2) * naturalFade),
      className: `starfield-bg__milky-star starfield-bg__milky-star--${layer}`,
      fill: fillRoll < 0.34
        ? "var(--starfield-star-ice)"
        : fillRoll < 0.62
          ? "var(--starfield-star-blue)"
          : fillRoll < 0.9
            ? "var(--starfield-star-lavender)"
            : "var(--starfield-star-violet)",
    })
  }
  return stars
}

/** Genere des masses brumeuses non continues autour de la Voie lactee. */
export function generateMilkyWayClouds(seed: number): MilkyWayCloud[] {
  const random = seededRandom(seed)
  const anchors = [0.12, 0.2, 0.31, 0.43, 0.54, 0.64, 0.76]

  return anchors.map((anchor, index) => {
    const t = Math.max(0, Math.min(1, anchor + centeredRandom(random) * 0.12))
    const wave = Math.sin(t * Math.PI * 2.12 + 0.55) * 5.9 + Math.sin(t * Math.PI * 6.9) * 2.8
    const cx = Math.max(-8, Math.min(108, -9 + t * 116 + centeredRandom(random) * 8))
    const cy = Math.max(-2, Math.min(94, 6 + t * 74 + wave + centeredRandom(random) * 6.5))
    const isCoreMass = t > 0.2 && t < 0.6
    const isLowerFragment = t > 0.66

    return {
      id: `milky-cloud-${seed}-${index}`,
      cx,
      cy,
      rx: isCoreMass ? 21 + random() * 11 : 13 + random() * 8,
      ry: isCoreMass ? 7.4 + random() * 4.8 : 4.5 + random() * 3.4,
      opacity: isCoreMass ? 0.3 + random() * 0.09 : isLowerFragment ? 0.12 + random() * 0.04 : 0.18 + random() * 0.05,
      rotation: 28 + centeredRandom(random) * 24,
      className: `starfield-bg__milky-cloud starfield-bg__milky-cloud--${index + 1}`,
    }
  })
}

/** Genere quelques etoiles bijoux fixes, froides et peu nombreuses. */
export function generateJewelStars(seed: number): JewelStar[] {
  const random = seededRandom(seed)
  const anchors = [
    { cx: 16, cy: 14 },
    { cx: 72, cy: 12 },
    { cx: 88, cy: 34 },
    { cx: 32, cy: 63 },
  ]

  return anchors.map((anchor, index) => ({
    id: `jewel-star-${seed}-${index}`,
    cx: anchor.cx + centeredRandom(random) * 2.2,
    cy: anchor.cy + centeredRandom(random) * 2,
    r: 0.13 + random() * 0.035,
    opacity: 0.7 + random() * 0.11,
    className: "starfield-bg__jewel-star",
    fill: "var(--starfield-star-ice)",
  }))
}

/** Genere des etoiles filantes rares et fines, sans ajouter de logique d'animation JS. */
export function generateShootingStars(count: number, seed: number): ShootingStar[] {
  const random = seededRandom(seed)
  const shootingStars: ShootingStar[] = []
  for (let i = 0; i < count; i++) {
    const x1 = 66 + random() * 22
    const y1 = 8 + random() * 18
    const length = 22 + random() * 10
    shootingStars.push({
      id: `shooting-${seed}-${i}`,
      x1,
      y1,
      x2: Math.max(0, x1 - length),
      y2: Math.min(VIEWBOX_SIZE, y1 + length * 0.34),
      opacity: 0.14 + random() * 0.12,
      className: `starfield-bg__shooting starfield-bg__shooting--${i + 1}`,
    })
  }
  return shootingStars
}

/** Nombre d'etoiles rendu dans le fond astral. */
export const STAR_COUNT = 420

/** Nombre de micro-etoiles concentrees dans la Voie lactee. */
export const MILKY_WAY_STAR_COUNT = 920

/** Graine deterministe du champ d'etoiles. */
export const STAR_SEED = 12345

/** Graine deterministe de la bande dense de Voie lactee. */
export const MILKY_WAY_STAR_SEED = 24680

/** Graine deterministe des masses brumeuses de Voie lactee. */
export const MILKY_WAY_CLOUD_SEED = 13579

/** Graine deterministe des etoiles bijoux. */
export const JEWEL_STAR_SEED = 54321

/** Nombre d'etoiles filantes rares. */
export const SHOOTING_STAR_COUNT = 1

/** Graine deterministe des etoiles filantes. */
export const SHOOTING_STAR_SEED = 98765

/** Champ d'etoiles pregenere pour limiter le travail au rendu. */
export const STARS = generateStars(STAR_COUNT, STAR_SEED)

/** Bande de Voie lactee pregeneree comme concentration de micro-etoiles. */
export const MILKY_WAY_STARS = generateMilkyWayStars(MILKY_WAY_STAR_COUNT, MILKY_WAY_STAR_SEED)

/** Masses brumeuses pregenerees pour adoucir la lecture de la Voie lactee. */
export const MILKY_WAY_CLOUDS = generateMilkyWayClouds(MILKY_WAY_CLOUD_SEED)

/** Etoiles bijoux pregenerees pour ponctuer rarement le ciel. */
export const JEWEL_STARS = generateJewelStars(JEWEL_STAR_SEED)

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
          <linearGradient id="starfield-milky-dawn" x1="0%" y1="0%" x2="100%" y2="76%">
            <stop offset="0%" stopColor="var(--starfield-milky-start)" stopOpacity="0" />
            <stop offset="31%" stopColor="var(--starfield-milky-violet)" stopOpacity="0.15" />
            <stop offset="47%" stopColor="var(--starfield-milky-mid)" stopOpacity="0.22" />
            <stop offset="56%" stopColor="var(--starfield-milky-core)" stopOpacity="0.19" />
            <stop offset="72%" stopColor="var(--starfield-milky-lavender)" stopOpacity="0.1" />
            <stop offset="100%" stopColor="var(--starfield-milky-end)" stopOpacity="0" />
          </linearGradient>
          <radialGradient id="starfield-milky-cloud" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="var(--starfield-milky-core)" stopOpacity="0.43" />
            <stop offset="42%" stopColor="var(--starfield-milky-lavender)" stopOpacity="0.29" />
            <stop offset="72%" stopColor="var(--starfield-milky-violet)" stopOpacity="0.13" />
            <stop offset="100%" stopColor="var(--starfield-milky-start)" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="starfield-shooting-tail" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="var(--starfield-shooting-tail)" stopOpacity="0" />
            <stop offset="46%" stopColor="var(--starfield-shooting-tail)" stopOpacity="0.16" />
            <stop offset="78%" stopColor="var(--starfield-shooting-tail)" stopOpacity="0.58" />
            <stop offset="100%" stopColor="var(--starfield-shooting-core)" stopOpacity="0.98" />
          </linearGradient>
          <radialGradient id="starfield-shooting-head" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="var(--starfield-shooting-core)" stopOpacity="1" />
            <stop offset="46%" stopColor="var(--starfield-star-blue)" stopOpacity="0.86" />
            <stop offset="100%" stopColor="var(--starfield-shooting-tail)" stopOpacity="0" />
          </radialGradient>
          <filter id="starfield-shooting-glow" x="-260%" y="-260%" width="620%" height="620%">
            <feGaussianBlur stdDeviation="0.42" result="shootingGlow" />
            <feMerge>
              <feMergeNode in="shootingGlow" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <filter id="starfield-milky-smoke" x="-18%" y="-18%" width="136%" height="136%">
            <feTurbulence
              type="fractalNoise"
              baseFrequency="0.05 0.076"
              numOctaves="3"
              seed="11"
              result="milkyNoise"
            />
            <feDisplacementMap
              in="SourceGraphic"
              in2="milkyNoise"
              scale="7.2"
              xChannelSelector="R"
              yChannelSelector="G"
            />
            <feGaussianBlur stdDeviation="2.6" />
          </filter>
        </defs>
        <path
          className="starfield-bg__milky-way starfield-bg__milky-way--smoke"
          d="M -22 12 C -2 8, 12 26, 32 29 C 47 31, 58 49, 74 56 C 89 63, 104 65, 122 74"
          fill="none"
          stroke="url(#starfield-milky-dawn)"
          strokeWidth="42"
          strokeLinecap="round"
          filter="url(#starfield-milky-smoke)"
        />
        <path
          className="starfield-bg__milky-way starfield-bg__milky-way--veil"
          d="M -18 11 C 4 15, 17 26, 34 32 C 51 38, 61 50, 76 59 C 91 67, 104 71, 120 75"
          fill="none"
          stroke="url(#starfield-milky-dawn)"
          strokeWidth="34"
          strokeLinecap="round"
          filter="url(#starfield-milky-smoke)"
        />
        <path
          className="starfield-bg__milky-way starfield-bg__milky-way--haze"
          d="M -16 8 C 5 13, 17 27, 35 32 C 50 37, 60 52, 76 59 C 92 67, 105 70, 118 76"
          fill="none"
          stroke="url(#starfield-milky-dawn)"
          strokeWidth="20"
          strokeLinecap="round"
          filter="url(#starfield-milky-smoke)"
        />
        <path
          className="starfield-bg__milky-way starfield-bg__milky-way--dust"
          d="M -13 10 C 8 22, 26 19, 40 35 C 53 50, 71 51, 87 65 C 98 74, 108 71, 116 77"
          fill="none"
          stroke="url(#starfield-milky-dawn)"
          strokeWidth="9.5"
          strokeLinecap="round"
          filter="url(#starfield-milky-smoke)"
        />
        <path
          className="starfield-bg__milky-way starfield-bg__milky-way--core"
          d="M -7 12 C 12 16, 25 29, 43 37 C 58 44, 71 59, 92 67 C 100 70, 105 75, 111 76"
          fill="none"
          stroke="url(#starfield-milky-dawn)"
          strokeWidth="3.2"
          strokeLinecap="round"
        />
        {MILKY_WAY_CLOUDS.map((cloud) => (
          <ellipse
            key={cloud.id}
            className={cloud.className}
            cx={cloud.cx}
            cy={cloud.cy}
            rx={cloud.rx}
            ry={cloud.ry}
            fill="url(#starfield-milky-cloud)"
            opacity={cloud.opacity}
            transform={`rotate(${cloud.rotation} ${cloud.cx} ${cloud.cy})`}
            filter="url(#starfield-milky-smoke)"
          />
        ))}
        {MILKY_WAY_STARS.map((star) => (
          <circle
            key={star.id}
            className={star.className}
            cx={star.cx}
            cy={star.cy}
            r={star.r}
            fill={star.fill}
            opacity={star.opacity}
          />
        ))}
        {STARS.map((star) => (
          <circle
            key={star.id}
            className={star.className}
            cx={star.cx}
            cy={star.cy}
            r={star.r}
            fill={star.fill}
            opacity={star.opacity}
          />
        ))}
        {JEWEL_STARS.map((star) => (
          <circle
            key={star.id}
            className={star.className}
            cx={star.cx}
            cy={star.cy}
            r={star.r}
            fill={star.fill}
            opacity={star.opacity}
          />
        ))}
        {SHOOTING_STARS.map((shootingStar) => (
          <g
            key={shootingStar.id}
            className={shootingStar.className}
            opacity={shootingStar.opacity}
          >
            <line
              className="starfield-bg__shooting-tail"
              x1={shootingStar.x1}
              y1={shootingStar.y1}
              x2={shootingStar.x2}
              y2={shootingStar.y2}
              stroke="url(#starfield-shooting-tail)"
              strokeWidth="0.42"
              strokeLinecap="round"
            />
            <circle
              className="starfield-bg__shooting-head"
              cx={shootingStar.x2}
              cy={shootingStar.y2}
              r="0.62"
              fill="url(#starfield-shooting-head)"
              filter="url(#starfield-shooting-glow)"
            />
          </g>
        ))}
      </svg>
    </div>
  )
}
