import React from 'react';
import type { DailyPredictionDayClimate } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';
import { getDomainLabel, DOMAIN_LABELS } from '../i18n/horoscope_copy';
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
      case 'positive': return 'var(--color-success)';
      case 'negative': return 'var(--color-danger)';
      case 'mixed': return 'var(--color-primary)';
      case 'neutral': return 'var(--color-text-secondary)';
      default: return 'var(--color-text-primary)';
    }
  };

  const content = (
    <>
      <div className="day-climate-hero__aura" aria-hidden="true" />
      <header className="day-climate-hero__header">
        <h1 className="day-climate-hero__title" style={{ color: getToneColor(climate.tone) }}>
          {climate.label}
        </h1>
        {climate.best_window_ref && (
          <span className="day-climate-hero__best-window">
            {lang === 'fr' ? 'Meilleur créneau' : 'Best window'} · {climate.best_window_ref}
          </span>
        )}
      </header>

      <p className="day-climate-hero__summary">
        {dailySynthesis || climate.summary}
      </p>

      <div className="day-climate-hero__domains">
        {climate.top_domains.map(key => (
          <span key={key} className="day-climate-hero__chip">
            <span>{DOMAIN_LABELS[key]?.icon || '✨'}</span>
            <span>{getDomainLabel(key, lang)}</span>
          </span>
        ))}
      </div>

      {climate.watchout && (
        <div className="day-climate-hero__watchout">
          <span className="day-climate-hero__watchout-icon">⚠️</span>
          <span className="day-climate-hero__watchout-text">
            {lang === 'fr' ? 'Vigilance sur ' : 'Watchout on '} 
            <strong>{getDomainLabel(climate.watchout!, lang).toLowerCase()}</strong>
          </span>
        </div>
      )}
    </>
  );

  if (astroBackgroundProps) {
    return (
      <div className="day-climate-hero-wrapper">
        <AstroMoodBackground
          sign={astroBackgroundProps.sign}
          userId={astroBackgroundProps.userId}
          dateKey={astroBackgroundProps.dateKey}
          dayScore={astroBackgroundProps.dayScore}
          className="day-climate-hero day-climate-hero--astro"
        >
          <div className="day-climate-hero__content">{content}</div>
        </AstroMoodBackground>
      </div>
    );
  }

  return (
    <section className="day-climate-hero glass-card glass-card--hero">
      {content}
    </section>
  );
};
