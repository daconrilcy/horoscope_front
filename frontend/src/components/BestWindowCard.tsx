import React from 'react';
import type { DailyPredictionBestWindow } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';

interface Props {
  bestWindow: DailyPredictionBestWindow | null;
  lang: Lang;
}

export const BestWindowCard: React.FC<Props> = ({ bestWindow, lang }) => {
  if (!bestWindow) return null;

  return (
    <div className="best-window-card" style={{
      background: 'linear-gradient(135deg, var(--glass) 0%, rgba(76, 175, 80, 0.05) 100%)',
      border: '1px solid var(--success)',
      borderRadius: '16px',
      padding: '24px',
      marginBottom: '24px',
      boxShadow: '0 4px 20px rgba(76, 175, 80, 0.1)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <span style={{ 
          fontSize: '12px', 
          fontWeight: 'bold', 
          color: 'var(--success)', 
          background: 'rgba(76, 175, 80, 0.1)',
          padding: '4px 12px',
          borderRadius: '20px',
          border: '1px solid var(--success)'
        }}>
          ✨ {bestWindow.time_range}
        </span>
        {bestWindow.is_pivot && (
          <span style={{ fontSize: '11px', color: 'var(--primary)', fontWeight: 'bold', textTransform: 'uppercase' }}>
            {lang === 'fr' ? 'Point charnière' : 'Turning point'}
          </span>
        )}
      </div>

      <h2 style={{ fontSize: '22px', fontWeight: 'bold', marginBottom: '8px', color: 'var(--text-1)' }}>
        {bestWindow.label}
      </h2>

      <p style={{ fontSize: '16px', color: 'var(--text-1)', marginBottom: '20px', lineHeight: '1.5' }}>
        {bestWindow.why}
      </p>

      <div style={{ background: 'var(--glass-2)', borderRadius: '12px', padding: '16px' }}>
        <h3 style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--text-2)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          {lang === 'fr' ? 'Actions recommandées' : 'Recommended actions'}
        </h3>
        <ul style={{ margin: 0, paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {bestWindow.recommended_actions.map((action) => (
            <li key={action} style={{ fontSize: '14px', color: 'var(--text-1)' }}>
              {action}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
