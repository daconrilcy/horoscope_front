import React from 'react';
import { Moon, Sunrise, Sun, Sunset, Sparkles } from 'lucide-react';
import type { DailyPredictionTimeWindow } from '../../types/dailyPrediction';
import type { Lang } from '../../i18n/predictions';
import { getDomainLabel, getRegimeLabel, DOMAIN_LABELS } from '../../i18n/horoscope_copy';
import { PERIOD_LABELS } from '../../i18n/predictions';

interface Props {
  timeWindows: DailyPredictionTimeWindow[];
  lang: Lang;
}

const PERIOD_ICONS: Record<string, React.ElementType> = {
  nuit: Moon,
  matin: Sunrise,
  apres_midi: Sun,
  soiree: Sunset,
};

export const DayTimelineSectionV4: React.FC<Props> = ({ timeWindows, lang }) => {
  const getRegimeColor = (regime: string) => {
    switch (regime) {
      case 'progression':
      case 'fluidité':
      case 'mise_en_route':
        return 'rgba(76, 175, 80, 0.1)';
      case 'prudence':
        return 'rgba(255, 152, 0, 0.1)';
      case 'pivot':
        return 'rgba(33, 150, 243, 0.1)';
      case 'récupération':
      case 'recentrage':
      case 'retombée':
        return 'var(--glass-2)';
      default:
        return 'var(--glass-2)';
    }
  };

  const getRegimeBorder = (regime: string) => {
    switch (regime) {
      case 'progression':
      case 'fluidité':
      case 'mise_en_route':
        return '1px solid var(--success)';
      case 'prudence':
        return '1px solid #ff9800';
      case 'pivot':
        return '1px solid var(--primary)';
      default:
        return '1px solid var(--glass-border)';
    }
  };

  return (
    <section className="day-timeline-v4" style={{ marginBottom: '32px' }}>
      <h2 style={{ fontSize: '18px', marginBottom: '16px', color: 'var(--text-1)' }}>
        {lang === 'fr' ? 'Déroulé de votre journée' : 'Your day timeline'}
      </h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {timeWindows.map((window) => {
          const Icon = PERIOD_ICONS[window.period_key] || Sparkles;
          const periodLabel = PERIOD_LABELS[window.period_key as keyof typeof PERIOD_LABELS]?.[lang] || '';

          return (
            <div key={window.period_key || window.time_range} style={{
              background: getRegimeColor(window.regime),
              border: getRegimeBorder(window.regime),
              borderRadius: '12px',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Icon size={16} color="var(--text-2)" />
                <span style={{ fontWeight: 'bold', color: 'var(--text-1)', fontSize: '15px' }}>
                  {periodLabel}
                </span>
                <span style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text-2)' }}>
                  {window.time_range}
                </span>
                <span style={{ 
                  fontSize: '10px', 
                  textTransform: 'uppercase', 
                  fontWeight: 'bold', 
                  color: 'var(--text-2)',
                  background: 'var(--glass-2)',
                  padding: '2px 6px',
                  borderRadius: '4px',
                  marginLeft: '8px'
                }}>
                  {getRegimeLabel(window.regime, lang)}
                </span>
              </div>

              <h3 style={{ fontSize: '16px', fontWeight: 'bold', margin: 0, color: 'var(--text-1)' }}>
                {window.label}
              </h3>

              <p style={{ fontSize: '14px', color: 'var(--text-1)', fontStyle: 'italic', margin: 0 }}>
                {window.action_hint}
              </p>

              <div style={{ display: 'flex', gap: '4px' }}>
                {window.top_domains.map(key => (
                  <span key={key} title={getDomainLabel(key, lang)} style={{ fontSize: '14px' }}>
                    {DOMAIN_LABELS[key]?.icon || '✨'}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
