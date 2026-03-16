import React from 'react'
import type { Lang } from '../../i18n/predictions'
import type { HeroSummaryCardModel } from '../../utils/heroSummaryCardMapper'
import { getPredictionMessage } from '../../utils/predictionI18n'
import { AstroMoodBackground } from '../astro/AstroMoodBackground'
import './HeroSummaryCard.css'

interface Props {
  model: HeroSummaryCardModel
  lang: Lang
}

export const HeroSummaryCard: React.FC<Props> = ({ model, lang }) => {
  return (
    <AstroMoodBackground
      className="hero-summary-card"
      sign={model.astroProps.sign}
      userId={model.astroProps.userId}
      dateKey={model.astroProps.dateKey}
      dayScore={model.astroProps.dayScore}
    >
      <div className="hero-summary-card__inner">
        {/* Colonne gauche : contenu textuel */}
        <section
          className="hero-summary-card__content"
          aria-labelledby="hero-summary-title"
        >
          <h2 id="hero-summary-title" className="hero-summary-card__title">
            {model.titleParts.map((part, i) =>
              part.highlight ? (
                <span key={i} className="hero-summary-card__title-highlight">
                  {part.text}
                </span>
              ) : (
                <span key={i}>{part.text}</span>
              )
            )}
          </h2>

          {model.subtitle && (
            <p className="hero-summary-card__subtitle">{model.subtitle}</p>
          )}

          {model.calibrationNote && (
            <p className="hero-summary-card__calibration">{model.calibrationNote}</p>
          )}

          <div className="hero-summary-card__divider" aria-hidden="true" />

          {model.insight && (
            <div className="hero-summary-card__insight-row">
              <span className="hero-summary-card__insight-icon" aria-hidden="true">✦</span>
              <div className="hero-summary-card__insight-text">
                <span className="hero-summary-card__insight-label">
                  {model.insight.label}
                </span>
                <span className="hero-summary-card__insight-time">
                  {model.insight.time}
                </span>
                {model.insight.categoryLabel && (
                  <span className="hero-summary-card__insight-category">
                    {model.insight.categoryLabel}
                  </span>
                )}
              </div>
            </div>
          )}

          {model.tags.length > 0 && (
            <div
              className="hero-summary-card__tags-row"
              aria-label={getPredictionMessage('domains_title', lang)}
            >
              {model.tags.map(tag => (
                <span key={tag.id} className="hero-tag-chip">
                  {tag.icon && (
                    <span className="hero-tag-chip__icon" aria-hidden="true">
                      {tag.icon}
                    </span>
                  )}
                  <span className="hero-tag-chip__label">{tag.label}</span>
                </span>
              ))}
            </div>
          )}
        </section>

        {/* Colonne droite : décor visuel CSS, masqué pour les lecteurs d'écran */}
        <div className="hero-summary-card__visual" aria-hidden="true">
          <div className="hero-summary-card__visual-glow" />
          <div className="hero-summary-card__visual-orb" />
        </div>
      </div>
    </AstroMoodBackground>
  )
}
