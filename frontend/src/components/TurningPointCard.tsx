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

function getBadgeToneClass(type: string): string {
  switch (type) {
    case 'emergence': return 'emergence';
    case 'recomposition': return 'recomposition';
    case 'attenuation': return 'attenuation';
    default: return 'default';
  }
}

export const TurningPointCard: React.FC<Props> = ({ turningPoint, lang }) => {
  if (!turningPoint) return null;

  const badgeToneClass = getBadgeToneClass(turningPoint.change_type);

  return (
    <section className="turning-point-card">
      <div className={`turning-point-card__rail turning-point-card__rail--${badgeToneClass}`} />
      <header className="turning-point-card__header">
        <div className="turning-point-card__meta">
          <span className="turning-point-card__time">{turningPoint.time}</span>
          <span className={`turning-point-card__type turning-point-card__type--${badgeToneClass}`}>
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
