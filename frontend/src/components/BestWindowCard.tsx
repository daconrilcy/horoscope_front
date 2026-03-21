import React from 'react';
import { Sparkles } from 'lucide-react';
import type { DailyPredictionBestWindow } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';
import './BestWindowCard.css';

interface Props {
  bestWindow: DailyPredictionBestWindow | null;
  lang: Lang;
}

export const BestWindowCard: React.FC<Props> = ({ bestWindow, lang }) => {
  if (!bestWindow) return null;

  return (
    <section className="best-window-card">
      <header className="best-window-card__header">
        <span className="best-window-card__time">
          <Sparkles size={14} className="best-window-card__time-icon" />
          {bestWindow.time_range}
        </span>
        {bestWindow.is_pivot && (
          <span className="best-window-card__pivot">
            {lang === 'fr' ? 'Point charnière' : 'Turning point'}
          </span>
        )}
      </header>

      <h2 className="best-window-card__title">
        {bestWindow.label}
      </h2>

      <p className="best-window-card__why">
        {bestWindow.why}
      </p>

      <div className="best-window-card__actions">
        <h3 className="best-window-card__actions-title">
          {lang === 'fr' ? 'Actions recommandées' : 'Recommended actions'}
        </h3>
        <ul className="best-window-card__actions-list">
          {bestWindow.recommended_actions.map((action) => (
            <li key={action} className="best-window-card__actions-item">
              {action}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};
