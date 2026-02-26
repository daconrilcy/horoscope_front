import { memo, useId } from 'react'
import { ChevronRight } from 'lucide-react'
import { ConstellationSVG } from './ConstellationSVG'
import type { ZodiacSign } from '../types/astrology'
import { getZodiacIcon } from './zodiacSignIconMap'
import './HeroHoroscopeCard.css'

/**
 * Props for the HeroHoroscopeCard component
 */
export interface HeroHoroscopeCardProps {
  /** Zodiac sign symbol (e.g., "♒") — used as fallback when signCode is absent */
  sign?: ZodiacSign
  /** Sign code from the API (e.g., "aquarius") — used to display the SVG icon */
  signCode?: string | null
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
  signCode,
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
  const SignIcon = getZodiacIcon(signCode)

  return (
    <div className="hero-card" role="article" aria-labelledby={headlineId}>
      {/* Top row */}
      <div className="hero-card__top-row">
        <div className="hero-card__chip">
          {SignIcon
            ? <SignIcon className="hero-card__chip-icon" aria-hidden="true" />
            : sign
              ? <span>{sign}</span>
              : null
          }
          <span className="hero-card__chip-text-sign">{signName}</span><span className="hero-card__chip-text-date"> • {date}</span>
        </div>
        <ChevronRight size={20} strokeWidth={2.25} className="hero-card__top-chevron" aria-hidden="true" />
      </div>

      {/* Headline */}
      <h2 className="hero-card__headline" id={headlineId}>{headline}</h2>

      {/* Constellation overlay */}
      <div className="hero-card__constellation" aria-hidden="true">
        <ConstellationSVG className="hero-card__constellation-svg" />
      </div>

      {/* CTA Panel — second niveau glass (profondeur premium) */}
      {(onReadFull || onReadDetailed) && (
        <div className="hero-card__cta-panel">
          {onReadFull && (
            <button
              type="button"
              className="hero-card__cta"
              onClick={onReadFull}
              aria-label={ariaLabelReadFull}
            >
              Lire en 2 min <ChevronRight size={22} strokeWidth={2.25} aria-hidden="true" />
            </button>
          )}
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
      )}
    </div>
  )
})
