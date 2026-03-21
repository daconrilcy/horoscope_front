import React from 'react';
import { Star, Zap, MapPin, Cake, TrendingUp, Anchor, Cloud } from 'lucide-react';
import type { AstroDailyEventsViewData } from '../utils/astroDailyEventsMapper';
import type { Lang } from '../i18n/predictions';
import './AstroDailyEvents.css';

const LABELS = {
  title:       { fr: 'Astrologie du jour', en: 'Astrology of the Day' },
  mouvements:  { fr: 'Mouvements',       en: 'Transits' },
  aspects:     { fr: 'Transits actifs',    en: 'Active Transits' },
  positions:   { fr: 'Positions',          en: 'Positions' },
  returns:     { fr: 'Cycles & Retours',   en: 'Cycles & Returns' },
  progressions:{ fr: 'Évolution longue',   en: 'Long-term Evolution' },
  nodes:       { fr: 'Nœuds Lunaires',     en: 'Lunar Nodes' },
  skyAspects:  { fr: 'Ambiance du Ciel',   en: 'Sky Climate' },
  fixedStars:  { fr: 'Étoiles Fixes',      en: 'Fixed Stars' },
};

interface AstroDailyEventsProps {
  data: AstroDailyEventsViewData;
  intro?: string | null;
  lang: Lang;
}

export const AstroDailyEvents: React.FC<AstroDailyEventsProps> = ({ data, intro, lang }) => {
  const { 
    ingresses, aspects, planetPositions, 
    returns, progressions, nodes, skyAspects, fixedStars 
  } = data;
  
  const l = (key: keyof typeof LABELS) => LABELS[key][lang] ?? LABELS[key].fr;

  const renderGroup = (titleKey: keyof typeof LABELS, items: string[] | undefined, Icon: React.ElementType, isPill = false) => {
    if (!items || items.length === 0) return null;
    return (
      <div className="astro-daily-events__group">
        <header className="astro-daily-events__group-header">
          <Icon size={16} className="astro-daily-events__group-icon" />
          <h4 className="astro-daily-events__group-title">{l(titleKey)}</h4>
        </header>
        <ul className={`astro-daily-events__list ${isPill ? 'astro-daily-events__list--positions' : ''}`}>
          {items.map((item) => (
            <li key={item} className={`astro-daily-events__item ${isPill ? 'astro-daily-events__item--pill' : ''}`}>
              <span className="astro-daily-events__item-text">{item}</span>
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <section className="astro-daily-events" aria-labelledby="astro-events-title">
      <h3 id="astro-events-title" className="astro-daily-events__title">
        {l('title')}
      </h3>

      {intro && (
        <p className="astro-daily-events__intro">
          {intro}
        </p>
      )}

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

        {renderGroup('skyAspects', skyAspects, Cloud)}
        {renderGroup('aspects', aspects, Zap)}
        {renderGroup('returns', returns, Cake)}
        {renderGroup('progressions', progressions, TrendingUp)}
        {renderGroup('nodes', nodes, Anchor)}
        {renderGroup('fixedStars', fixedStars, Star)}
        {renderGroup('positions', planetPositions, MapPin, true)}
      </div>
    </section>
  );
};
