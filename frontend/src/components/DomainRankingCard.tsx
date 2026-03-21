import React from 'react';
import type { DailyPredictionPublicDomainScore } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';
import { getDomainLabel, getLevelLabel, LEVEL_LABELS, DOMAIN_LABELS } from '../i18n/horoscope_copy';
import './prediction/SectionTitle.css';
import './DomainRankingCard.css';

interface Props {
  domains: DailyPredictionPublicDomainScore[];
  lang: Lang;
}

export const DomainRankingCard: React.FC<Props> = ({ domains, lang }) => {
  const getLevelColor = (level: string) => {
    const hint = LEVEL_LABELS[level]?.color_hint;
    switch (hint) {
      case 'success': return 'var(--success)';
      case 'success-light': return '#a8e6cf';
      case 'neutral': return 'var(--text-2)';
      case 'warning': return '#ffd3b6';
      case 'danger': return 'var(--danger)';
      default: return 'var(--text-2)';
    }
  };

  return (
    <section className="domain-ranking-card glass-card glass-card--hero">
      <div className="section-title">
        <div className="section-title__dot" />
        <h2 className="section-title__text">
          {lang === 'fr' ? 'Vos domaines clés' : 'Your key domains'}
        </h2>
        <hr className="section-title__line" />
      </div>

      <div className="domain-ranking-card__list">
        {domains.map(domain => (
          <article key={domain.key} className="domain-ranking-card__item">
            <div className="domain-ranking-card__item-top">
              <div className="domain-ranking-card__label-wrap">
                <span className="domain-ranking-card__icon">{DOMAIN_LABELS[domain.key]?.icon || '✨'}</span>
                <span className="domain-ranking-card__label">{getDomainLabel(domain.key, lang)}</span>
              </div>
              <div className="domain-ranking-card__meta">
                <span className="domain-ranking-card__score" style={{ color: getLevelColor(domain.level) }}>
                  {domain.score_10}/10
                </span>
                <span className="domain-ranking-card__badge" style={{ borderColor: getLevelColor(domain.level) }}>
                  {getLevelLabel(domain.level, lang)}
                </span>
              </div>
            </div>
            
            <div className="domain-ranking-card__track">
              <div
                className="domain-ranking-card__fill"
                style={{
                  width: `${Math.min(domain.score_10 * 10, 100)}%`,
                  background: getLevelColor(domain.level),
                }}
              />
            </div>
          </article>
        ))}
      </div>
    </section>
  );
};
