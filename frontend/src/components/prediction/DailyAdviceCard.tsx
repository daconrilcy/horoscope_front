import React from 'react'
import { Lightbulb } from 'lucide-react'
import type { DailyAdviceCardModel } from '../../utils/dailyAdviceCardMapper'
import './DailyAdviceCard.css'

interface DailyAdviceCardProps {
  model: DailyAdviceCardModel
}

export const DailyAdviceCard: React.FC<DailyAdviceCardProps> = ({ model }) => (
  <section className="daily-advice-card" aria-labelledby="daily-advice-title">
    <header className="daily-advice-card__header">
      <span className="daily-advice-card__icon-badge" aria-hidden="true">
        <Lightbulb size={16} strokeWidth={2} />
      </span>
      <h3 id="daily-advice-title" className="daily-advice-card__title">
        {model.title}
      </h3>
    </header>
    <div className="daily-advice-card__content">
      <p className="daily-advice-card__body">{model.advice}</p>
      {model.emphasis ? (
        <p className="daily-advice-card__emphasis">{model.emphasis}</p>
      ) : null}
    </div>
  </section>
)
