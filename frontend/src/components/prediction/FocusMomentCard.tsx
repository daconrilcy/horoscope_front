import React from 'react'
import { Sparkles, ArrowRight } from 'lucide-react'
import type { FocusMomentCardModel } from '../../types/detailScores'
import { CategoryIcon } from './CategoryIcon'
import './FocusMomentCard.css'

interface FocusMomentCardProps {
  model: FocusMomentCardModel
}

export const FocusMomentCard: React.FC<FocusMomentCardProps> = ({ model }) => {
  return (
    <article className="focus-moment-card" aria-labelledby="focus-moment-title">
      <div className="focus-moment-card__background-glow" aria-hidden="true" />
      
      <header className="focus-moment-card__header">
        <div className="focus-moment-card__time-badge">
          <Sparkles size={14} className="focus-moment-card__sparkle" />
          <span className="focus-moment-card__time">{model.timeRange}</span>
        </div>
        <h3 id="focus-moment-title" className="focus-moment-card__title">
          {model.title}
        </h3>
      </header>

      <div className="focus-moment-card__tags">
        {model.tags.map(tag => (
          <span key={tag.code} className="focus-moment-card__tag">
            <CategoryIcon code={tag.code} className="focus-moment-card__tag-icon" />
            {tag.label}
          </span>
        ))}
      </div>

      <p className="focus-moment-card__description">
        {model.description}
      </p>

      <footer className="focus-moment-card__footer">
        <button type="button" className="focus-moment-card__cta">
          {model.ctaLabel}
          <ArrowRight size={15} strokeWidth={3} className="focus-moment-card__cta-arrow" aria-hidden="true" />
        </button>
      </footer>
    </article>
  )
}
