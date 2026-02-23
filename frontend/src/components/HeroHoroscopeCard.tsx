import { memo, useId } from 'react'
import { ChevronRight } from 'lucide-react'
import { ConstellationSVG } from './ConstellationSVG'
import { ZodiacSign } from '../types/astrology'

/**
 * Props for the HeroHoroscopeCard component
 */
export interface HeroHoroscopeCardProps {
  /** Zodiac sign symbol (e.g., "♒") */
  sign: ZodiacSign
  /** Translated name of the sign */
  signName: string
  /** Date string to display in the chip */
  date: string
  /** Main message of the day */
  headline: string
  /** Callback for the main CTA button */
  onReadFull?: () => void
  /** Callback for the "Version détaillée" button */
  onReadDetailed?: () => void
  /** Accessible label for the main CTA */
  ariaLabelReadFull?: string
  /** Accessible label for the detailed link */
  ariaLabelReadDetailed?: string
}

/**
 * HeroHoroscopeCard is the primary visual element of the 'Today' page,
 * featuring glassmorphism effects and a constellation backdrop.
 */
export const HeroHoroscopeCard = memo(function HeroHoroscopeCard({
  sign,
  signName,
  date,
  headline,
  onReadFull,
  onReadDetailed,
  // Default values kept for now but marked for i18n review
  ariaLabelReadFull = "Lire l'horoscope complet en 2 minutes",
  ariaLabelReadDetailed = "Voir la version détaillée de l'horoscope",
}: HeroHoroscopeCardProps) {
  const headlineId = useId()

  return (
    <div className="hero-card" role="article" aria-labelledby={headlineId}>
      {/* Top row */}
      <div className="hero-card__top-row">
        <div className="hero-card__chip">
          <span>{sign}</span>
          <span>{signName} • {date}</span>
        </div>
        <ChevronRight size={18} strokeWidth={1.75} className="hero-card__top-chevron" aria-hidden="true" />
      </div>

      {/* Headline */}
      <h2 className="hero-card__headline" id={headlineId}>{headline}</h2>

      {/* Constellation overlay */}
      <div className="hero-card__constellation" aria-hidden="true">
        <ConstellationSVG className="hero-card__constellation-svg" />
      </div>

      {/* CTA Button */}
      {onReadFull && (
        <button
          type="button"
          className="hero-card__cta"
          onClick={onReadFull}
          aria-label={ariaLabelReadFull}
        >
          Lire en 2 min <ChevronRight size={18} strokeWidth={1.75} aria-hidden="true" />
        </button>
      )}

      {/* Secondary Action (Link style) */}
      {onReadDetailed && (
        <button
          type="button"
          className="hero-card__link"
          onClick={onReadDetailed}
          aria-label={ariaLabelReadDetailed}
        >
          Version détaillée
        </button>
      )}
    </div>
  )
})
