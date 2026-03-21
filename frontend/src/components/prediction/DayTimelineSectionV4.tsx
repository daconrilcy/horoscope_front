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
import { getDomainLabel, getRegimeLabel, DOMAIN_LABELS } from '../../i18n/horoscope_copy';
import { PERIOD_LABELS } from '../../i18n/predictions';
import './SectionTitle.css';
import './DayTimelineSectionV4.css';

interface Props {
  timeWindows: DailyPredictionTimeWindow[];
  lang: Lang;
}

interface RegimeVisual {
  cardBackground: string;
  borderColor: string;
  badgeBackground: string;
  badgeColor: string;
}

const PERIOD_ICONS: Record<string, React.ElementType> = {
  nuit: Moon,
  matin: Sunrise,
  apres_midi: Sun,
  soiree: Sunset,
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

const DEFAULT_REGIME_VISUAL: RegimeVisual = {
  cardBackground: 'var(--horoscope-panel-bg, linear-gradient(180deg, rgba(255, 255, 255, 0.56) 0%, rgba(255, 255, 255, 0.34) 100%))',
  borderColor: 'var(--horoscope-panel-border-soft, rgba(220, 210, 246, 0.65))',
  badgeBackground: 'var(--horoscope-inner-bg, rgba(255, 255, 255, 0.34))',
  badgeColor: 'var(--color-text-secondary, var(--text-2))',
};

const REGIME_VISUALS: Record<string, RegimeVisual> = {
  progression: {
    cardBackground: DEFAULT_REGIME_VISUAL.cardBackground,
    borderColor: 'var(--horoscope-phase-progression, #5d946d)',
    badgeBackground: DEFAULT_REGIME_VISUAL.badgeBackground,
    badgeColor: 'var(--horoscope-phase-progression, #5d946d)',
  },
  fluidité: {
    cardBackground: DEFAULT_REGIME_VISUAL.cardBackground,
    borderColor: 'var(--horoscope-phase-fluidite, #6f67cf)',
    badgeBackground: DEFAULT_REGIME_VISUAL.badgeBackground,
    badgeColor: 'var(--horoscope-phase-fluidite, #6f67cf)',
  },
  prudence: {
    cardBackground: DEFAULT_REGIME_VISUAL.cardBackground,
    borderColor: 'var(--horoscope-phase-prudence, #d39a3e)',
    badgeBackground: DEFAULT_REGIME_VISUAL.badgeBackground,
    badgeColor: 'var(--horoscope-phase-prudence, #d39a3e)',
  },
  pivot: {
    cardBackground: DEFAULT_REGIME_VISUAL.cardBackground,
    borderColor: 'var(--horoscope-phase-pivot, #8b5cf6)',
    badgeBackground: DEFAULT_REGIME_VISUAL.badgeBackground,
    badgeColor: 'var(--horoscope-phase-pivot, #8b5cf6)',
  },
  récupération: {
    cardBackground: DEFAULT_REGIME_VISUAL.cardBackground,
    borderColor: 'var(--horoscope-phase-recuperation, #8a7cb2)',
    badgeBackground: DEFAULT_REGIME_VISUAL.badgeBackground,
    badgeColor: 'var(--horoscope-phase-recuperation, #8a7cb2)',
  },
  retombée: {
    cardBackground: DEFAULT_REGIME_VISUAL.cardBackground,
    borderColor: 'var(--horoscope-phase-retombee, #9a8ebc)',
    badgeBackground: DEFAULT_REGIME_VISUAL.badgeBackground,
    badgeColor: 'var(--horoscope-phase-retombee, #9a8ebc)',
  },
  mise_en_route: {
    cardBackground: DEFAULT_REGIME_VISUAL.cardBackground,
    borderColor: 'var(--horoscope-phase-mise-en-route, #f0b83d)',
    badgeBackground: DEFAULT_REGIME_VISUAL.badgeBackground,
    badgeColor: 'var(--horoscope-phase-mise-en-route, #f0b83d)',
  },
  recentrage: {
    cardBackground: DEFAULT_REGIME_VISUAL.cardBackground,
    borderColor: 'var(--horoscope-phase-recentrage, #7355c7)',
    badgeBackground: DEFAULT_REGIME_VISUAL.badgeBackground,
    badgeColor: 'var(--horoscope-phase-recentrage, #7355c7)',
  },
};

export const DayTimelineSectionV4: React.FC<Props> = ({ timeWindows, lang }) => {
  const getRegimeVisual = (regime: string): RegimeVisual =>
    REGIME_VISUALS[regime] ?? DEFAULT_REGIME_VISUAL;

  return (
    <section className="day-timeline-v4">
      <div className="section-title">
        <div className="section-title__dot" />
        <h2 className="section-title__text">
          {lang === 'fr' ? 'Déroulé de votre journée' : 'Your day timeline'}
        </h2>
        <hr className="section-title__line" />
      </div>

      <div className="day-timeline-v4__list">
        {timeWindows.map((window) => {
          const Icon = PERIOD_ICONS[window.period_key] || Sparkles;
          const periodLabel = PERIOD_LABELS[window.period_key as keyof typeof PERIOD_LABELS]?.[lang] || '';
          const regimeMeta = REGIME_META[window.regime] || {
            icon: Sparkles,
            description: {
              fr: "Ce créneau possède une tonalité astrologique particulière.",
              en: 'This slot has a distinct astrological tone.',
            },
          };
          const RegimeIcon = regimeMeta.icon;
          const regimeDescription = regimeMeta.description[lang];
          const regimeVisual = getRegimeVisual(window.regime);

          return (
            <article
              key={window.period_key || window.time_range}
              className="day-timeline-v4__card"
              style={{
                background: regimeVisual.cardBackground,
                border: `1.5px solid ${regimeVisual.borderColor}`,
                boxShadow: 'var(--horoscope-panel-shadow, 0 18px 44px rgba(72, 56, 118, 0.11), 0 2px 0 rgba(255, 255, 255, 0.28) inset)',
              }}
            >
              <div className="day-timeline-v4__top">
                <Icon size={16} color="var(--text-2)" />
                <span className="day-timeline-v4__period-label">
                  {periodLabel}
                </span>
                <span className="day-timeline-v4__time-range">
                  {window.time_range}
                </span>
                <span
                  title={regimeDescription}
                  aria-label={`${getRegimeLabel(window.regime, lang)}. ${regimeDescription}`}
                  className="day-timeline-v4__regime-badge"
                  style={{
                    color: regimeVisual.badgeColor,
                    background: regimeVisual.badgeBackground,
                    border: `1px solid ${regimeVisual.borderColor}`,
                  }}
                >
                  <RegimeIcon size={12} strokeWidth={2} />
                  <span>
                    {getRegimeLabel(window.regime, lang)}
                  </span>
                </span>
              </div>

              <h3 className="day-timeline-v4__label">
                {window.label}
              </h3>

              <p className="day-timeline-v4__narrative">
                {window.narrative || window.action_hint}
              </p>

              {window.astro_events && window.astro_events.length > 0 && (
                <ul className="day-timeline-v4__events">
                  {window.astro_events.map((evt, i) => (
                    <li key={i} className="day-timeline-v4__event">· {evt}</li>
                  ))}
                </ul>
              )}

              <div className="day-timeline-v4__domains">
                {window.top_domains.map(key => (
                  <span key={key} title={getDomainLabel(key, lang)} className="day-timeline-v4__domain-icon">
                    {DOMAIN_LABELS[key]?.icon || '✨'}
                  </span>
                ))}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
};
