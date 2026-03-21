import React from 'react';
import type { DailyPredictionDayClimate } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';
import { getDomainLabel } from '../i18n/horoscope_copy';
import { DomainIcon } from './prediction/DomainIcon';
import { AstroMoodBackground } from './astro/AstroMoodBackground';
import type { ZodiacSign } from './astro/zodiacPatterns';
import './DayClimateHero.css';

interface Props {
  climate: DailyPredictionDayClimate;
  dailySynthesis?: string | null;
  lang: Lang;
  astroBackgroundProps?: {
    sign: ZodiacSign;
    userId: string;
    dateKey: string;
    dayScore: number;
  };
}

export const DayClimateHero: React.FC<Props> = ({
  climate,
  dailySynthesis,
  lang,
  astroBackgroundProps,
}) => {
  const getToneColor = (tone: string) => {
    switch (tone) {
      case 'positive': return '#4caf50';
      case 'negative': return '#f44336';
      default: return 'var(--accent-purple)';
    }
  };

  const content = (
    <div className="day-climate-hero__inner">
      <div className="day-climate-hero__content-zone">
        <header className="day-climate-hero__header">
          <h2 className="day-climate-hero__title" style={{ color: getToneColor(climate.tone) }}>
            {climate.label}
          </h2>
          {climate.best_window_ref && (
            <div className="day-climate-hero__best-window">
              {lang === 'fr' ? 'Meilleur créneau' : 'Best window'} · {climate.best_window_ref}
            </div>
          )}
        </header>

        <p className="day-climate-hero__summary">
          {dailySynthesis || climate.summary}
        </p>

        <div className="day-climate-hero__pills">
          <div className="day-climate-hero__domains">
            {climate.top_domains.map(key => (
              <span key={key} className="day-climate-hero__pill">
                <span className="day-climate-hero__pill-icon">
                  <DomainIcon code={key} size={14} />
                </span>
                <span>{getDomainLabel(key, lang)}</span>
              </span>
            ))}
          </div>

          {climate.watchout && (
            <div className="day-climate-hero__pill day-climate-hero__pill--watchout">
              <span className="day-climate-hero__pill-icon">⚠️</span>
              <span>
                {lang === 'fr' ? 'Vigilance sur ' : 'Watchout on '} 
                <strong>{getDomainLabel(climate.watchout!, lang).toLowerCase()}</strong>
              </span>
            </div>
          )}
        </div>
      </div>
      
      <div className="day-climate-hero__decor-zone">
        {/* The AstroMoodBackground will render its decorative elements here via CSS positioning */}
      </div>
    </div>
  );

  if (astroBackgroundProps) {
    return (
      <div className="day-climate-hero-container">
        <AstroMoodBackground
          sign={astroBackgroundProps.sign}
          userId={astroBackgroundProps.userId}
          dateKey={astroBackgroundProps.dateKey}
          dayScore={astroBackgroundProps.dayScore}
          className="day-climate-hero"
        >
          {content}
        </AstroMoodBackground>
      </div>
    );
  }

  return (
    <section className="day-climate-hero">
      {content}
    </section>
  );
};
