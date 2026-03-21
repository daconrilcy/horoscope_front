import React from 'react';
import type { DailyPredictionTurningPointPublic } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';
import { getDomainLabel, getChangeTypeLabel } from '../i18n/horoscope_copy';
import { DomainIcon } from './prediction/DomainIcon';
import './TurningPointCard.css';

interface Props {
  turningPoint: DailyPredictionTurningPointPublic | null;
  lang: Lang;
}

export const TurningPointCard: React.FC<Props> = ({ turningPoint, lang }) => {
  if (!turningPoint) return null;

  const getBadgeStyle = (type: string) => {
    switch (type) {
      case 'emergence': return { bg: 'rgba(76, 175, 80, 0.1)', color: 'var(--success)' };
      case 'recomposition': return { bg: 'rgba(33, 150, 243, 0.1)', color: 'var(--primary)' };
      case 'attenuation': return { bg: 'rgba(158, 158, 158, 0.1)', color: 'var(--text-2)' };
      default: return { bg: 'var(--glass-2)', color: 'var(--text-2)' };
    }
  };

  const badge = getBadgeStyle(turningPoint.change_type);

  return (
    <section className="turning-point-card">
      <div className="turning-point-card__rail" style={{ background: badge.color }} />
      <header className="turning-point-card__header">
        <div className="turning-point-card__meta">
          <span className="turning-point-card__time">{turningPoint.time}</span>
          <span className="turning-point-card__type" style={{ color: badge.color, background: badge.bg }}>
            {getChangeTypeLabel(turningPoint.change_type, lang)}
          </span>
        </div>
      </header>

      <h2 className="turning-point-card__title">{turningPoint.title}</h2>

      <p className="turning-point-card__body">
        {turningPoint.narrative || turningPoint.what_changes}
      </p>

      <div className="turning-point-card__domains">
        {turningPoint.affected_domains.map(key => (
          <span key={key} className="turning-point-card__domain-pill">
            <DomainIcon code={key} size={14} />
            {getDomainLabel(key, lang)}
          </span>
        ))}
      </div>

      <div className="turning-point-card__actions">
        <div className="turning-point-card__action turning-point-card__action--do">
          <div className="turning-point-card__action-label">
            {lang === 'fr' ? 'À privilégier' : 'To do'}
          </div>
          <div className="turning-point-card__action-text">{turningPoint.do}</div>
        </div>
        <div className="turning-point-card__action turning-point-card__action--avoid">
          <div className="turning-point-card__action-label">
            {lang === 'fr' ? 'À éviter' : 'Avoid'}
          </div>
          <div className="turning-point-card__action-text">{turningPoint.avoid}</div>
        </div>
      </div>
    </section>
  );
};
