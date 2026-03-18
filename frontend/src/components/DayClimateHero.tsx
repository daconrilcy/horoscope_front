import React from 'react';
import type { DailyPredictionDayClimate } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';
import { getCategoryLabel, getCategoryIcon } from '../utils/predictionI18n';

interface Props {
  climate: DailyPredictionDayClimate;
  lang: Lang;
}

export const DayClimateHero: React.FC<Props> = ({ climate, lang }) => {
  const getToneColor = (tone: string) => {
    switch (tone) {
      case 'positive': return 'var(--success)';
      case 'negative': return 'var(--danger)';
      case 'mixed': return 'var(--primary)';
      case 'neutral': return 'var(--text-2)';
      default: return 'var(--text-1)';
    }
  };

  return (
    <div className="day-climate-hero" style={{
      background: 'var(--glass)',
      border: '1px solid var(--glass-border)',
      borderRadius: '16px',
      padding: '24px',
      marginBottom: '24px',
      backdropFilter: 'blur(10px)'
    }}>
      <h1 style={{
        fontSize: '24px',
        fontWeight: 'bold',
        color: getToneColor(climate.tone),
        marginBottom: '8px',
        marginTop: 0
      }}>
        {climate.label}
      </h1>
      
      <p style={{
        fontSize: '16px',
        color: 'var(--text-1)',
        lineHeight: '1.5',
        marginBottom: '20px'
      }}>
        {climate.summary}
      </p>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center' }}>
        {climate.top_domains.map(key => (
          <span key={key} style={{
            background: 'var(--glass-2)',
            padding: '6px 12px',
            borderRadius: '20px',
            fontSize: '14px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            border: '1px solid var(--glass-border)'
          }}>
            <span>{getCategoryIcon(key)}</span>
            <span>{getCategoryLabel(key, lang)}</span>
          </span>
        ))}

        {climate.best_window_ref && (
          <span style={{
            fontSize: '14px',
            color: 'var(--text-2)',
            marginLeft: 'auto'
          }}>
            🕒 {climate.best_window_ref}
          </span>
        )}
      </div>

      {climate.watchout && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          background: 'rgba(255, 107, 107, 0.1)',
          borderRadius: '8px',
          borderLeft: '4px solid var(--danger)',
          display: 'flex',
          gap: '10px',
          alignItems: 'center',
          fontSize: '14px'
        }}>
          <span>⚠️</span>
          <span>
            {lang === 'fr' ? 'Vigilance sur ' : 'Watchout on '} 
            <strong>{getCategoryLabel(climate.watchout, lang).toLowerCase()}</strong>
          </span>
        </div>
      )}
    </div>
  );
};
