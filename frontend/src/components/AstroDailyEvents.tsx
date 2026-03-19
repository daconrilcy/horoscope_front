import React from 'react';
import { Star, Zap, MapPin } from 'lucide-react';
import type { AstroDailyEventsViewData } from '../utils/astroDailyEventsMapper';
import './AstroDailyEvents.css';

interface AstroDailyEventsProps {
  data: AstroDailyEventsViewData;
}

export const AstroDailyEvents: React.FC<AstroDailyEventsProps> = ({ data }) => {
  const { ingresses, aspects, planetPositions } = data;

  return (
    <section className="astro-daily-events" aria-labelledby="astro-events-title">
      <h3 id="astro-events-title" className="astro-daily-events__title">
        Astrologie du Jour
      </h3>

      <div className="astro-daily-events__grid">
        {/* Ingresses */}
        {ingresses.length > 0 && (
          <div className="astro-daily-events__group">
            <header className="astro-daily-events__group-header">
              <Star size={16} className="astro-daily-events__group-icon" />
              <h4 className="astro-daily-events__group-title">Mouvements</h4>
            </header>
            <ul className="astro-daily-events__list">
              {ingresses.map((ing: { text: string; time: string | null }, idx: number) => (
                <li key={idx} className="astro-daily-events__item">
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
              <h4 className="astro-daily-events__group-title">Aspects exacts</h4>
            </header>
            <ul className="astro-daily-events__list">
              {aspects.map((asp: string, idx: number) => (
                <li key={idx} className="astro-daily-events__item">
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
              <h4 className="astro-daily-events__group-title">Positions</h4>
            </header>
            <ul className="astro-daily-events__list astro-daily-events__list--positions">
              {planetPositions.map((pos: string, idx: number) => (
                <li key={idx} className="astro-daily-events__item astro-daily-events__item--pill">
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
