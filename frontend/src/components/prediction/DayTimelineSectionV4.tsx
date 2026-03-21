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
  cardBackground: 'linear-gradient(135deg, rgba(255, 255, 255, 0.16), rgba(208, 188, 255, 0.12))',
  borderColor: 'rgba(255, 255, 255, 0.22)',
  badgeBackground: 'rgba(255, 255, 255, 0.54)',
  badgeColor: 'var(--text-2)',
};

const REGIME_VISUALS: Record<string, RegimeVisual> = {
  progression: {
    cardBackground: 'linear-gradient(135deg, rgba(223, 247, 229, 0.42), rgba(168, 230, 186, 0.18))',
    borderColor: 'rgba(54, 141, 79, 0.9)',
    badgeBackground: 'rgba(222, 245, 229, 0.92)',
    badgeColor: '#225c37',
  },
  fluidité: {
    cardBackground: 'linear-gradient(135deg, rgba(226, 246, 240, 0.4), rgba(156, 214, 198, 0.18))',
    borderColor: 'rgba(47, 134, 116, 0.78)',
    badgeBackground: 'rgba(227, 246, 241, 0.9)',
    badgeColor: '#1d6255',
  },
  prudence: {
    cardBackground: 'linear-gradient(135deg, rgba(255, 241, 223, 0.45), rgba(255, 194, 122, 0.16))',
    borderColor: 'rgba(214, 131, 26, 0.92)',
    badgeBackground: 'rgba(255, 242, 226, 0.92)',
    badgeColor: '#8d5408',
  },
  pivot: {
    cardBackground: 'linear-gradient(135deg, rgba(223, 239, 255, 0.42), rgba(146, 189, 255, 0.18))',
    borderColor: 'rgba(58, 111, 196, 0.88)',
    badgeBackground: 'rgba(225, 239, 255, 0.9)',
    badgeColor: '#214f96',
  },
  récupération: {
    cardBackground: 'linear-gradient(135deg, rgba(245, 241, 252, 0.42), rgba(216, 208, 237, 0.16))',
    borderColor: 'rgba(180, 172, 205, 0.74)',
    badgeBackground: 'rgba(246, 243, 252, 0.9)',
    badgeColor: '#615a76',
  },
  retombée: {
    cardBackground: 'linear-gradient(135deg, rgba(241, 238, 248, 0.42), rgba(202, 193, 226, 0.16))',
    borderColor: 'rgba(161, 151, 189, 0.74)',
    badgeBackground: 'rgba(243, 239, 250, 0.9)',
    badgeColor: '#5f5774',
  },
  mise_en_route: {
    cardBackground: 'linear-gradient(135deg, rgba(240, 251, 229, 0.46), rgba(213, 234, 146, 0.18))',
    borderColor: 'rgba(109, 146, 26, 0.92)',
    badgeBackground: 'rgba(242, 250, 231, 0.94)',
    badgeColor: '#587115',
  },
  recentrage: {
    cardBackground: 'linear-gradient(135deg, rgba(250, 243, 236, 0.4), rgba(231, 204, 188, 0.16))',
    borderColor: 'rgba(177, 136, 110, 0.72)',
    badgeBackground: 'rgba(251, 244, 238, 0.9)',
    badgeColor: '#7b5a46',
  },
};

export const DayTimelineSectionV4: React.FC<Props> = ({ timeWindows, lang }) => {
  const getRegimeVisual = (regime: string): RegimeVisual =>
    REGIME_VISUALS[regime] ?? DEFAULT_REGIME_VISUAL;

  return (
    <section className="day-timeline-v4" style={{ marginBottom: '32px' }}>
      <h2 style={{ fontSize: '18px', marginBottom: '16px', color: 'var(--text-1)' }}>
        {lang === 'fr' ? 'Déroulé de votre journée' : 'Your day timeline'}
      </h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
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
            <div key={window.period_key || window.time_range} style={{
              background: regimeVisual.cardBackground,
              border: `1px solid ${regimeVisual.borderColor}`,
              boxShadow: `inset 0 1px 0 rgba(255,255,255,0.12), 0 8px 24px ${regimeVisual.borderColor.replace(/0\.\d+\)$/, '0.12)')}`,
              borderRadius: '12px',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Icon size={16} color="var(--text-2)" />
                <span style={{ fontWeight: 'bold', color: 'var(--text-1)', fontSize: '15px' }}>
                  {periodLabel}
                </span>
                <span style={{ marginLeft: 'auto', fontSize: '12px', color: 'var(--text-2)' }}>
                  {window.time_range}
                </span>
                <span
                  title={regimeDescription}
                  aria-label={`${getRegimeLabel(window.regime, lang)}. ${regimeDescription}`}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontSize: '10px',
                    textTransform: 'uppercase',
                    fontWeight: 'bold',
                    letterSpacing: '0.04em',
                    color: regimeVisual.badgeColor,
                    background: regimeVisual.badgeBackground,
                    border: `1px solid ${regimeVisual.borderColor}`,
                    padding: '4px 8px',
                    borderRadius: '999px',
                    marginLeft: '8px',
                    cursor: 'help',
                  }}
                >
                  <RegimeIcon size={12} strokeWidth={2} />
                  <span>
                    {getRegimeLabel(window.regime, lang)}
                  </span>
                </span>
              </div>

              <h3 style={{ fontSize: '16px', fontWeight: 'bold', margin: 0, color: 'var(--text-1)' }}>
                {window.label}
              </h3>

              <p style={{ fontSize: '14px', color: 'var(--text-1)', fontStyle: 'italic', margin: 0 }}>
                {window.narrative || window.action_hint}
              </p>

              {window.astro_events && window.astro_events.length > 0 && (
                <ul style={{ margin: 0, padding: 0, listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                  {window.astro_events.map((evt, i) => (
                    <li key={i} style={{ fontSize: '12px', color: 'var(--text-2)' }}>· {evt}</li>
                  ))}
                </ul>
              )}

              <div style={{ display: 'flex', gap: '4px' }}>
                {window.top_domains.map(key => (
                  <span key={key} title={getDomainLabel(key, lang)} style={{ fontSize: '14px' }}>
                    {DOMAIN_LABELS[key]?.icon || '✨'}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
};
