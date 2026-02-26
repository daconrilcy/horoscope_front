import type { ComponentType, SVGProps } from 'react'
import {
  AriesIcon,
  TaurusIcon,
  GeminiIcon,
  CancerIcon,
  LeoIcon,
  VirgoIcon,
  LibraIcon,
  ScorpioIcon,
  SagittariusIcon,
  CapricornIcon,
  AquariusIcon,
  PiscesIcon,
} from './icons/zodiac'

export type ZodiacIconComponent = ComponentType<SVGProps<SVGSVGElement>>

/**
 * Mapping sign_code (lowercase) → SVG icon component.
 * sign_code values match those returned by the backend astro_profile API.
 */
export const zodiacSignIconMap: Record<string, ZodiacIconComponent> = {
  aries: AriesIcon,
  taurus: TaurusIcon,
  gemini: GeminiIcon,
  cancer: CancerIcon,
  leo: LeoIcon,
  virgo: VirgoIcon,
  libra: LibraIcon,
  scorpio: ScorpioIcon,
  sagittarius: SagittariusIcon,
  capricorn: CapricornIcon,
  aquarius: AquariusIcon,
  pisces: PiscesIcon,
}

/**
 * Returns the SVG icon component for a given sign code, or null if not found.
 * sign_code lookup is case-insensitive.
 */
export function getZodiacIcon(signCode: string | null | undefined): ZodiacIconComponent | null {
  if (!signCode) return null
  return zodiacSignIconMap[signCode.toLowerCase()] ?? null
}
