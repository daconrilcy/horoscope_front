import React from 'react';
import { Star, Zap, MapPin } from 'lucide-react';
import type { AstroDailyEventsViewData } from '../utils/astroDailyEventsMapper';
import type { Lang } from '../i18n/predictions';
import './AstroDailyEvents.css';

const LABELS = {
  title:    { fr: 'Astrologie du jour', en: 'Astrology of the Day' },
  mouvements: { fr: 'Mouvements',       en: 'Transits' },
  aspects:  { fr: 'Transits actifs',    en: 'Active Transits' },
  positions:{ fr: 'Positions',          en: 'Positions' },
};

interface AstroDailyEventsProps {
  data: AstroDailyEventsViewData;
  lang: Lang;
}

export const AstroDailyEvents: React.FC<AstroDailyEventsProps> = ({ data, lang }) => {
  const { ingresses, aspects, planetPositions } = data;
  const l = (key: keyof typeof LABELS) => LABELS[key][lang] ?? LABELS[key].fr;

  return (
    <section className="astro-daily-events" aria-labelledby="astro-events-title">
      <h3 id="astro-events-title" className="astro-daily-events__title">
        {l('title')}
      </h3>

      <div className="astro-daily-events__grid">
        {/* Ingresses */}
        {ingresses.length > 0 && (
          <div className="astro-daily-events__group">
            <header className="astro-daily-events__group-header">
              <Star size={16} className="astro-daily-events__group-icon" />
              <h4 className="astro-daily-events__group-title">{l('mouvements')}</h4>
            </header>
            <ul className="astro-daily-events__list">
              {ingresses.map((ing) => (
                <li key={ing.text} className="astro-daily-events__item">
                  <span className="astro-daily-events__item-text">{ing.text}</span>
                  {ing.time && (
                    <span className="astro-daily-events__item-time">{ing.time}</span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Aspects */}
        {aspects.length > 0 && (
          <div className="astro-daily-events__group">
            <header className="astro-daily-events__group-header">
              <Zap size={16} className="astro-daily-events__group-icon" />
              <h4 className="astro-daily-events__group-title">{l('aspects')}</h4>
            </header>
            <ul className="astro-daily-events__list">
              {aspects.map((asp) => (
                <li key={asp} className="astro-daily-events__item">
                  <span className="astro-daily-events__item-text">{asp}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Positions */}
        {planetPositions.length > 0 && (
          <div className="astro-daily-events__group">
            <header className="astro-daily-events__group-header">
              <MapPin size={16} className="astro-daily-events__group-icon" />
              <h4 className="astro-daily-events__group-title">{l('positions')}</h4>
            </header>
            <ul className="astro-daily-events__list astro-daily-events__list--positions">
              {planetPositions.map((pos) => (
                <li key={pos} className="astro-daily-events__item astro-daily-events__item--pill">
                  {pos}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
};
