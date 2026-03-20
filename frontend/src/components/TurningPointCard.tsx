import React from 'react';
import type { DailyPredictionTurningPointPublic } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';
import { getDomainLabel, getChangeTypeLabel, DOMAIN_LABELS } from '../i18n/horoscope_copy';

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
    <div className="turning-point-card" style={{
      background: 'var(--glass)',
      border: '1px solid var(--glass-border)',
      borderRadius: '16px',
      padding: '24px',
      marginBottom: '24px',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '4px',
        height: '100%',
        background: badge.color
      }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
        <div>
          <span style={{ 
            fontSize: '12px', 
            fontWeight: 'bold', 
            color: 'var(--text-2)', 
            background: 'var(--glass-2)',
            padding: '4px 8px',
            borderRadius: '4px',
            marginRight: '8px'
          }}>
            {turningPoint.time}
          </span>
          <span style={{ 
            fontSize: '12px', 
            fontWeight: '500', 
            color: badge.color,
            background: badge.bg,
            padding: '4px 8px',
            borderRadius: '4px'
          }}>
            {getChangeTypeLabel(turningPoint.change_type, lang)}
          </span>
        </div>
      </div>

      <h2 style={{ fontSize: '20px', fontWeight: 'bold', marginBottom: '12px', color: 'var(--text-1)' }}>
        {turningPoint.title}
      </h2>

      <p style={{ fontSize: '15px', color: 'var(--text-1)', marginBottom: '16px', lineHeight: '1.4' }}>
        {turningPoint.narrative || turningPoint.what_changes}
      </p>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '20px' }}>
        {turningPoint.affected_domains.map(key => (
          <span key={key} style={{ 
            fontSize: '12px', 
            color: 'var(--text-2)', 
            padding: '2px 8px', 
            borderRadius: '12px', 
            background: 'var(--glass-2)',
            border: '1px solid var(--glass-border)'
          }}>
            {DOMAIN_LABELS[key]?.icon || '✨'} {getDomainLabel(key, lang)}
          </span>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div style={{ padding: '12px', background: 'rgba(76, 175, 80, 0.05)', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--success)', marginBottom: '4px', textTransform: 'uppercase' }}>
            {lang === 'fr' ? 'À privilégier' : 'To do'}
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text-1)' }}>{turningPoint.do}</div>
        </div>
        <div style={{ padding: '12px', background: 'rgba(244, 67, 54, 0.05)', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', fontWeight: 'bold', color: 'var(--danger)', marginBottom: '4px', textTransform: 'uppercase' }}>
            {lang === 'fr' ? 'À éviter' : 'Avoid'}
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text-1)' }}>{turningPoint.avoid}</div>
        </div>
      </div>
    </div>
  );
};
