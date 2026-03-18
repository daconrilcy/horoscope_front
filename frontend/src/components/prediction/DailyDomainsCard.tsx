import React from 'react'
import type { DailyDomainsCardModel, DailyDomainScore } from '../../types/detailScores'
import type { Lang } from '../../i18n/predictions'
import { getCategoryMeta } from '../../utils/predictionI18n'
import './DailyDomainsCard.css'

interface DailyDomainsCardProps {
  model: DailyDomainsCardModel
  lang: Lang
}

const DomainItem: React.FC<{ domain: DailyDomainScore; isPrimary: boolean; lang: Lang }> = ({ domain, isPrimary, lang }) => {
  const { icon } = getCategoryMeta(domain.code, lang)
  
  return (
    <div className={`daily-domains-card__item ${isPrimary ? 'daily-domains-card__item--primary' : 'daily-domains-card__item--secondary'}`}>
      <div className="daily-domains-card__item-header">
        <span className="daily-domains-card__item-icon" aria-hidden="true">{icon}</span>
        <span className="daily-domains-card__item-label">{domain.label}</span>
        <span className="daily-domains-card__item-score">{domain.score.toFixed(1)}</span>
      </div>
      <div className="daily-domains-card__progress-bg" aria-hidden="true">
        <div 
          className="daily-domains-card__progress-bar" 
          style={{ width: `${domain.percentage}%` }}
        />
      </div>
    </div>
  )
}

export const DailyDomainsCard: React.FC<DailyDomainsCardProps> = ({ model, lang }) => {
  return (
    <aside className="daily-domains-card" aria-labelledby="daily-domains-title">
      <h3 id="daily-domains-title" className="daily-domains-card__title">
        {model.title}
      </h3>

      <div className="daily-domains-card__primary-list">
        {model.primaryDomains.map(domain => (
          <DomainItem key={domain.code} domain={domain} isPrimary={true} lang={lang} />
        ))}
      </div>

      {model.secondaryDomains.length > 0 && (
        <div className="daily-domains-card__secondary-list">
          {model.secondaryDomains.map(domain => (
            <DomainItem key={domain.code} domain={domain} isPrimary={false} lang={lang} />
          ))}
        </div>
      )}

      <footer className="daily-domains-card__footer">
        <button type="button" className="daily-domains-card__cta">
          {model.ctaLabel}
        </button>
      </footer>
    </aside>
  )
}
