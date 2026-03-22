import React from 'react';
import type { DailyPredictionPublicDomainScore } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';
import { getDomainLabel, getLevelLabel } from '../i18n/horoscope_copy';
import { DomainIcon } from './prediction/DomainIcon';
import './DomainRankingCard.css';

interface Props {
  domains: DailyPredictionPublicDomainScore[];
  lang: Lang;
  hideTitle?: boolean;
}

export const DomainRankingCard: React.FC<Props> = ({ domains, lang, hideTitle = false }) => {
  return (
    <section className="domain-ranking-card">
      {!hideTitle ? (
        <h3 className="domain-ranking-card__title">
          {lang === 'fr' ? 'Vos domaines clés' : 'Your key domains'}
        </h3>
      ) : null}

      <div className="domain-ranking-card__list">
        {domains.map(domain => (
          <article key={domain.key} className="domain-ranking-card__item">
            <div className="domain-ranking-card__row">
              <div className="domain-ranking-card__info">
                <div className="domain-ranking-card__icon-circle">
                  <DomainIcon code={domain.key} size={16} />
                </div>
                <span className="domain-ranking-card__label">{getDomainLabel(domain.key, lang)}</span>
              </div>
              
              <div className="domain-ranking-card__metrics">
                <span className="domain-ranking-card__score-pill">
                  {domain.score_10}/10
                </span>
                <span className={`domain-ranking-card__status-pill domain-ranking-card__status-pill--${domain.level}`}>
                  {getLevelLabel(domain.level, lang)}
                </span>
              </div>
            </div>
            
            <div className="domain-ranking-card__progress-container">
              <div className="domain-ranking-card__track">
                <div
                  className={`domain-ranking-card__fill domain-ranking-card__fill--${domain.level}`}
                  style={{ width: `${Math.min(domain.score_10 * 10, 100)}%` }}
                />
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
};
