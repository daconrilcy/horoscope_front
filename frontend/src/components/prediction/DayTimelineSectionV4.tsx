import React from 'react';
import {
  ArrowUpRight,
  Compass,
  Moon,
  PauseCircle,
  RotateCcw,
  Sparkles,
  Sunrise,
  Sun,
  Sunset,
  TriangleAlert,
  Waves,
} from 'lucide-react';
import type { DailyPredictionTimeWindow } from '../../types/dailyPrediction';
import type { Lang } from '../../i18n/predictions';
import { getDomainLabel, getRegimeLabel } from '../../i18n/horoscope_copy';
import { DomainIcon } from './DomainIcon';
import { PERIOD_LABELS } from '../../i18n/predictions';
import './DayTimelineSectionV4.css';

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

const PERIOD_ACCENTS: Record<string, string> = {
  nuit: '#a5b4fc', // Light indigo
  matin: '#fde68a', // Light amber
  apres_midi: '#ddd6fe', // Light violet
  soiree: '#fca5a5', // Light rose/plum
};

const REGIME_META: Record<
  string,
  {
    icon: React.ElementType;
    description: { fr: string; en: string };
  }
> = {
  progression: {
    icon: ArrowUpRight,
    description: {
      fr: "L'énergie monte. C'est un créneau pour avancer, lancer ou prendre l'initiative.",
      en: 'Energy is rising. This is a good slot to move forward, initiate, or push ahead.',
    },
  },
  fluidité: {
    icon: Waves,
    description: {
      fr: "Le climat est fluide. Les choses circulent plus naturellement si vous restez simple.",
      en: 'The climate is flowing. Things move more naturally if you keep it simple.',
    },
  },
  prudence: {
    icon: TriangleAlert,
    description: {
      fr: "Le ciel demande du discernement. Mieux vaut ajuster, vérifier et éviter les réactions hâtives.",
      en: 'The sky calls for caution. Better to adjust, verify, and avoid rushed reactions.',
    },
  },
  pivot: {
    icon: Sparkles,
    description: {
      fr: "Un basculement est possible. Le ton ou les priorités peuvent changer nettement dans ce créneau.",
      en: 'A turning point is possible. Tone or priorities may shift clearly during this slot.',
    },
  },
  récupération: {
    icon: PauseCircle,
    description: {
      fr: "Créneau de récupération. Le rythme est plus favorable au repos, à l'intégration et au recul.",
      en: 'Recovery slot. The rhythm is better suited to rest, integration, and stepping back.',
    },
  },
  retombée: {
    icon: RotateCcw,
    description: {
      fr: "L'intensité redescend. C'est le moment de relâcher la pression et de laisser décanter.",
      en: 'Intensity is easing down. This is a time to release pressure and let things settle.',
    },
  },
  mise_en_route: {
    icon: Compass,
    description: {
      fr: "Le moteur se met en route. Bon moment pour préparer, cadrer et prendre votre élan.",
      en: 'The engine is warming up. Good time to prepare, frame things, and build momentum.',
    },
  },
  recentrage: {
    icon: Compass,
    description: {
      fr: "Le ciel invite au recentrage. Priorisez l'essentiel et revenez à votre axe.",
      en: 'The sky invites refocusing. Prioritize what matters and return to your center.',
    },
  },
};

export const DayTimelineSectionV4: React.FC<Props> = ({ timeWindows, lang }) => {
  return (
    <section className="day-timeline-v4">
      <h3 className="day-timeline-v4__title">
        {lang === 'fr' ? 'Déroulé de votre journée' : 'Your day timeline'}
      </h3>

      <div className="day-timeline-v4__container">
        {/* Vertical Timeline Line (AC8.34) */}
        <div className="day-timeline-v4__line" aria-hidden="true" />

        <div className="day-timeline-v4__list">
          {timeWindows.map((window) => {
            const Icon = PERIOD_ICONS[window.period_key] || Sparkles;
            const periodLabel = PERIOD_LABELS[window.period_key as keyof typeof PERIOD_LABELS]?.[lang] || '';
            const accentColor = PERIOD_ACCENTS[window.period_key] || 'var(--accent-purple)';
            const regimeMeta = REGIME_META[window.regime] || {
              icon: Sparkles,
              description: {
                fr: "Ce créneau possède une tonalité astrologique particulière.",
                en: 'This slot has a distinct astrological tone.',
              },
            };
            const RegimeIcon = regimeMeta.icon;
            const regimeDescription = regimeMeta.description[lang];

            return (
              <article
                key={window.period_key || window.time_range}
                className="day-timeline-v4__card"
                style={{ ['--period-accent' as string]: accentColor }}
              >
                {/* Timeline Connector Dot */}
                <div className="day-timeline-v4__dot" style={{ backgroundColor: accentColor }} />

                {/* Line 1: Header */}
                <div className="day-timeline-v4__row-1">
                  <div className="day-timeline-v4__period-info">
                    <Icon size={16} color={accentColor} />
                    <span className="day-timeline-v4__period-name">{periodLabel}</span>
                    <span className="day-timeline-v4__time-range">{window.time_range}</span>
                  </div>
                  <span
                    title={regimeDescription}
                    className="day-timeline-v4__regime-badge"
                  >
                    <RegimeIcon size={12} />
                    {getRegimeLabel(window.regime, lang)}
                  </span>
                </div>

                {/* Line 2: Strong Title */}
                <h4 className="day-timeline-v4__card-title">
                  {window.label}
                </h4>

                {/* Line 3: Text */}
                <p className="day-timeline-v4__narrative">
                  {window.narrative || window.action_hint}
                </p>

                {/* Line 4: Secondary Markers */}
                <div className="day-timeline-v4__footer">
                  <div className="day-timeline-v4__domains">
                    {window.top_domains.map(key => (
                      <span key={key} title={getDomainLabel(key, lang)} className="day-timeline-v4__domain-icon">
                        <DomainIcon code={key} size={14} />
                      </span>
                    ))}
                  </div>
                  
                  {window.astro_events && window.astro_events.length > 0 && (
                    <div className="day-timeline-v4__mini-events">
                      {window.astro_events.slice(0, 2).map((evt, i) => (
                        <span key={i} className="day-timeline-v4__mini-event">{evt}</span>
                      ))}
                    </div>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
};
