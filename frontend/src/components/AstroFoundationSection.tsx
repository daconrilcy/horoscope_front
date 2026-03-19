import React, { useState } from 'react';
import type { DailyPredictionAstroFoundation } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';

interface Props {
  foundation: DailyPredictionAstroFoundation | null;
  lang: Lang;
}

export const AstroFoundationSection: React.FC<Props> = ({ foundation, lang }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!foundation) return null;

  return (
    <div className="astro-foundation-section" style={{
      background: 'var(--glass-2)',
      borderRadius: '16px',
      padding: '16px',
      marginBottom: '24px',
      border: '1px solid var(--glass-border)'
    }}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          background: 'none',
          border: 'none',
          padding: 0,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: 'pointer',
          color: 'var(--text-1)'
        }}
      >
        <span style={{ fontWeight: 'bold', fontSize: '16px' }}>
          {lang === 'fr' ? 'Fondements astrologiques' : 'Astrological foundations'}
        </span>
        <span style={{ 
          transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
          transition: 'transform 0.3s ease'
        }}>
          ▼
        </span>
      </button>

      {isOpen && (
        <div style={{ marginTop: '20px' }}>
          <p style={{ fontSize: '15px', color: 'var(--text-1)', marginBottom: '20px', fontStyle: 'italic' }}>
            {foundation.headline}
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <section>
              <h3 style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--text-2)', marginBottom: '10px', textTransform: 'uppercase' }}>
                {lang === 'fr' ? 'Mouvements clés' : 'Key movements'}
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {foundation.key_movements.map((m, i) => (
                  <div key={i} style={{ fontSize: '14px', color: 'var(--text-1)', display: 'flex', justifyContent: 'space-between' }}>
                    <span><strong>{m.planet}</strong> {m.target ? `sur ${m.target}` : ''}</span>
                    <span style={{ color: 'var(--text-2)', fontSize: '13px' }}>{m.effect_label}</span>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--text-2)', marginBottom: '10px', textTransform: 'uppercase' }}>
                {lang === 'fr' ? 'Maisons activées' : 'Activated houses'}
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {foundation.activated_houses.map((h, i) => (
                  <div key={i} style={{ fontSize: '14px', color: 'var(--text-1)' }}>
                    <strong>{h.house_label}</strong> : {h.domain_label}
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 style={{ fontSize: '13px', fontWeight: 'bold', color: 'var(--text-2)', marginBottom: '10px', textTransform: 'uppercase' }}>
                {lang === 'fr' ? 'Aspects dominants' : 'Dominant aspects'}
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {foundation.dominant_aspects.map((a, i) => (
                  <div key={i} style={{ fontSize: '14px', color: 'var(--text-1)', display: 'flex', justifyContent: 'space-between' }}>
                    <span>{a.planet_a} {a.aspect_type.toLowerCase()}{a.planet_b ? ` ${a.planet_b}` : ''}</span>
                    <span style={{
                      fontSize: '12px',
                      color: a.tonality === 'fluidité' ? 'var(--success)'
                        : a.tonality === 'ajustement' ? '#ff9800'
                        : a.tonality === 'intensification' ? 'var(--primary)'
                        : 'var(--text-2)',
                      fontWeight: '500'
                    }}>
                      {a.tonality}
                    </span>
                  </div>
                ))}
              </div>
            </section>

            <p style={{ 
              fontSize: '14px', 
              color: 'var(--text-2)', 
              padding: '12px', 
              background: 'var(--glass-2)', 
              borderRadius: '8px',
              borderLeft: '2px solid var(--primary)'
            }}>
              {foundation.interpretation_bridge}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
