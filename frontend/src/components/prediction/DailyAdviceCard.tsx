import React from 'react'
import { Lightbulb } from 'lucide-react'
import type { DailyAdviceCardModel } from '../../utils/dailyAdviceCardMapper'
import './DailyAdviceCard.css'

interface DailyAdviceCardProps {
  model: DailyAdviceCardModel
  hideTitle?: boolean
}

export const DailyAdviceCard: React.FC<DailyAdviceCardProps> = ({ model, hideTitle = false }) => (
  <section
    className="daily-advice-card"
    aria-labelledby={hideTitle ? undefined : "daily-advice-title"}
    aria-label={hideTitle ? model.title : undefined}
  >
    {!hideTitle ? (
      <header className="daily-advice-card__header">
        <span className="daily-advice-card__icon-badge" aria-hidden="true">
          <Lightbulb size={16} strokeWidth={2} />
        </span>
        <h3 id="daily-advice-title" className="daily-advice-card__title">
          {model.title}
        </h3>
      </header>
    ) : null}
    <div className="daily-advice-card__content">
      <p className="daily-advice-card__body">{model.advice}</p>
      {model.emphasis ? (
        <p className="daily-advice-card__emphasis">{model.emphasis}</p>
      ) : null}
    </div>
  </section>
)
