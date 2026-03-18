import React from 'react';
import type { DailyPredictionPublicDomainScore } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';
import { getDomainLabel, getLevelLabel, LEVEL_LABELS, DOMAIN_LABELS } from '../i18n/horoscope_copy';

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
    <div className="domain-ranking-card" style={{
      background: 'var(--glass)',
      border: '1px solid var(--glass-border)',
      borderRadius: '16px',
      padding: '24px',
      marginBottom: '24px'
    }}>
      <h2 style={{ fontSize: '18px', marginBottom: '20px', color: 'var(--text-1)' }}>
        {lang === 'fr' ? 'Vos domaines clés' : 'Your key domains'}
      </h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {domains.map(domain => (
          <div key={domain.key} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '20px' }}>{DOMAIN_LABELS[domain.key]?.icon || '✨'}</span>
                <span style={{ fontWeight: '500', color: 'var(--text-1)' }}>{getDomainLabel(domain.key, lang)}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '14px', fontWeight: 'bold', color: getLevelColor(domain.level) }}>
                  {domain.score_10}/10
                </span>
                <span style={{ 
                  fontSize: '12px', 
                  padding: '2px 8px', 
                  borderRadius: '10px', 
                  background: 'var(--glass-2)',
                  color: 'var(--text-2)',
                  border: `1px solid ${getLevelColor(domain.level)}`
                }}>
                  {getLevelLabel(domain.level, lang)}
                </span>
              </div>
            </div>
            
            <div style={{ 
              height: '6px', 
              background: 'var(--glass-2)', 
              borderRadius: '3px', 
              overflow: 'hidden' 
            }}>
              <div style={{ 
                height: '100%', 
                width: `${domain.score_10 * 10}%`, 
                background: getLevelColor(domain.level),
                borderRadius: '3px',
                transition: 'width 0.5s ease-out'
              }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
