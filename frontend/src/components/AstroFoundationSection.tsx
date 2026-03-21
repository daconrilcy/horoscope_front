import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import type { DailyPredictionAstroFoundation } from '../types/dailyPrediction';
import type { Lang } from '../i18n/predictions';
import './AstroFoundationSection.css';

interface Props {
  foundation: DailyPredictionAstroFoundation | null;
  lang: Lang;
}

export const AstroFoundationSection: React.FC<Props> = ({ foundation, lang }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!foundation) return null;

  return (
    <section className="astro-foundation-section">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="astro-foundation-section__toggle"
      >
        <span className="astro-foundation-section__title">
          {lang === 'fr' ? 'Fondements astrologiques' : 'Astrological foundations'}
        </span>
        <span className={`astro-foundation-section__chevron ${isOpen ? 'astro-foundation-section__chevron--open' : ''}`}>
          <ChevronDown size={20} />
        </span>
      </button>

      {isOpen && (
        <div className="astro-foundation-section__content">
          <p className="astro-foundation-section__headline">
            {foundation.headline}
          </p>

          <div className="astro-foundation-section__groups">
            <section>
              <h3 className="astro-foundation-section__section-title">
                {lang === 'fr' ? 'Mouvements clés' : 'Key movements'}
              </h3>
              <div className="astro-foundation-section__items">
                {foundation.key_movements.map((m, i) => (
                  <div key={i} className="astro-foundation-section__row">
                    <span><strong>{m.planet}</strong> {m.target ? `sur ${m.target}` : ''}</span>
                    <span className="astro-foundation-section__hint">{m.effect_label}</span>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 className="astro-foundation-section__section-title">
                {lang === 'fr' ? 'Maisons activées' : 'Activated houses'}
              </h3>
              <div className="astro-foundation-section__items">
                {foundation.activated_houses.map((h, i) => (
                  <div key={i} className="astro-foundation-section__row astro-foundation-section__row--stack">
                    <strong>{h.house_label}</strong> : {h.domain_label}
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 className="astro-foundation-section__section-title">
                {lang === 'fr' ? 'Aspects dominants' : 'Dominant aspects'}
              </h3>
              <div className="astro-foundation-section__items">
                {foundation.dominant_aspects.map((a, i) => (
                  <div key={i} className="astro-foundation-section__row">
                    <span>{a.planet_a} {a.aspect_type.toLowerCase()}{a.planet_b ? ` ${a.planet_b}` : ''}</span>
                    <span className="astro-foundation-section__tonality" data-tonality={a.tonality}>
                      {a.tonality}
                    </span>
                  </div>
                ))}
              </div>
            </section>

            <p className="astro-foundation-section__bridge">
              {foundation.interpretation_bridge}
            </p>
          </div>
        </div>
      )}
    </section>
  );
};
