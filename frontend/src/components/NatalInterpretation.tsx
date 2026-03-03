import { useState } from "react";
import { 
  useNatalInterpretation, 
  type NatalInterpretationResult, 
  type AstroSection 
} from "../api/natalChart";
import { useAstrologers, type Astrologer } from "../api/astrologers";
import { AstrologerGrid } from "../features/astrologers";
import { natalChartTranslations } from "../i18n/natalChart";
import { type AstrologyLang } from "../i18n/astrology";
import { ChevronDown, ChevronUp, Lock, RefreshCw, Star, AlertCircle } from "lucide-react";
import { ErrorBoundary } from "./ErrorBoundary";

interface Props {
  chartLoaded: boolean;
  lang: AstrologyLang;
}

type InterpretationTranslations = typeof natalChartTranslations['fr']['interpretation'];

export function NatalInterpretationSection({ chartLoaded, lang }: Props) {
  const t = natalChartTranslations[lang].interpretation;
  const [useCaseLevel, setUseCaseLevel] = useState<"short" | "complete">("short");
  const [selectedPersonaId, setSelectedPersonaId] = useState<string | null>(null);
  const [isUpsellOpen, setIsUpsellOpen] = useState(false);
  const [forceRefresh, setForceRefresh] = useState(false);

  const { data, isLoading, error, refetch } = useNatalInterpretation({
    enabled: chartLoaded,
    useCaseLevel,
    personaId: selectedPersonaId,
    locale: lang === "fr" ? "fr-FR" : lang === "en" ? "en-US" : "es-ES",
    forceRefresh,
  });

  const handleUpgrade = (personaId: string) => {
    setSelectedPersonaId(personaId);
    setUseCaseLevel("complete");
    setIsUpsellOpen(false);
    setForceRefresh(false); // Reset force refresh when upgrading
  };

  const handleRegenerate = () => {
    setForceRefresh(true);
    // refetch is handled by queryKey change due to forceRefresh in queryKey
  };

  if (!chartLoaded) return null;

  return (
    <section className="mt-8 border-t pt-8 border-gray-200 dark:border-gray-800">
      <div className="flex items-center justify-between mb-6">
        <div className="flex flex-col">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">
            {t.title}
          </h2>
          {data?.meta.persisted_at && (
            <span className="text-[10px] text-gray-400 dark:text-gray-500 mt-1">
              Généré le {new Date(data.meta.persisted_at).toLocaleDateString(lang)}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {useCaseLevel === "short" && data && !isLoading && (
            <button 
              onClick={handleRegenerate}
              title={t.regenerate}
              className="p-2 text-gray-400 hover:text-purple-500 transition-colors rounded-full hover:bg-purple-50 dark:hover:bg-purple-900/20"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
          {data?.meta.level === "complete" && (
            <span className="bg-purple-100 text-purple-800 text-xs font-medium px-2.5 py-0.5 rounded dark:bg-purple-900 dark:text-purple-300 border border-purple-400">
              {t.completeBadge}
            </span>
          )}
        </div>
      </div>

      <ErrorBoundary onReset={() => refetch()}>
        {isLoading ? (
          <InterpretationSkeleton t={t} isComplete={useCaseLevel === "complete"} />
        ) : error ? (
          <InterpretationError t={t} onRetry={() => refetch()} />
        ) : data ? (
          <>
            <InterpretationContent data={data} lang={lang} />
            
            {useCaseLevel === "short" && !isUpsellOpen && (
              <UpsellBlock t={t} onOpenSelector={() => setIsUpsellOpen(true)} />
            )}

            {isUpsellOpen && (
              <PersonaSelector 
                t={t} 
                onConfirm={handleUpgrade} 
                onCancel={() => setIsUpsellOpen(false)} 
                isSubmitting={isLoading && useCaseLevel === "complete"}
              />
            )}
          </>
        ) : null}
      </ErrorBoundary>
    </section>
  );
}

function InterpretationSkeleton({ t, isComplete }: { t: InterpretationTranslations, isComplete?: boolean }) {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
      <div className="space-y-2">
        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
        <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
      </div>
      <div className="flex gap-2 py-4">
        {[1, 2, 3].map(i => (
          <div key={i} className="h-8 bg-gray-200 dark:bg-gray-700 rounded-full w-20"></div>
        ))}
      </div>
      <div className="h-40 bg-gray-200 dark:bg-gray-700 rounded w-full"></div>
      <p className="text-sm text-gray-500 italic text-center py-4">
        {isComplete ? t.requestingComplete : t.loading}
      </p>
    </div>
  );
}

function InterpretationError({ t, onRetry }: { t: InterpretationTranslations, onRetry: () => void }) {
  return (
    <div className="p-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-center">
      <p className="text-red-800 dark:text-red-400 mb-4">{t.error}</p>
      <button 
        onClick={onRetry}
        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
      >
        <RefreshCw className="w-4 h-4 mr-2" />
        {t.retry}
      </button>
    </div>
  );
}

function InterpretationContent({ data, lang }: { data: NatalInterpretationResult, lang: AstrologyLang }) {
  const t = natalChartTranslations[lang].interpretation;
  const { interpretation, meta, degraded_mode } = data;

  return (
    <div className="space-y-8">
      {degraded_mode && (
        <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg text-sm text-amber-800 dark:text-amber-400 flex items-center">
          <Star className="w-4 h-4 mr-2 fill-current" />
          {t.degradedNotice}
        </div>
      )}

      <div>
        <h3 className="text-xl font-semibold mb-3 text-gray-800 dark:text-gray-200">
          {interpretation.title}
        </h3>
        {meta.persona_name && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4 italic">
            {t.completeBy} <span className="font-medium text-purple-600 dark:text-purple-400">{meta.persona_name}</span>
          </p>
        )}
        <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
          {interpretation.summary}
        </p>
      </div>

      <div>
        <h4 className="text-sm font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-4">
          {t.highlightsTitle}
        </h4>
        <HighlightsChips highlights={interpretation.highlights} />
      </div>

      <SectionAccordion sections={interpretation.sections} sectionsMap={t.sectionsMap} />

      <div className="bg-blue-50 dark:bg-blue-900/10 p-6 rounded-2xl">
        <h4 className="text-lg font-bold text-blue-900 dark:text-blue-300 mb-4">
          {t.adviceTitle}
        </h4>
        <AdviceList advice={interpretation.advice} />
      </div>

      {interpretation.disclaimers.length > 0 && (
        <div className="text-xs text-gray-400 dark:text-gray-500 italic space-y-1">
          <p className="font-bold uppercase tracking-tight">{t.disclaimerTitle}</p>
          {interpretation.disclaimers.map((d, i) => <p key={i}>{d}</p>)}
        </div>
      )}

      <EvidenceTags evidence={interpretation.evidence} title={t.evidenceTitle} t={t} />
    </div>
  );
}

function HighlightsChips({ highlights }: { highlights: string[] }) {
  return (
    <div className="grid grid-cols-1 gap-3">
      {highlights.map((h, i) => (
        <div 
          key={i} 
          className="flex items-center p-3 bg-purple-50/30 dark:bg-purple-900/10 border border-purple-100 dark:border-purple-900/30 rounded-xl shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex-shrink-0 w-8 h-8 bg-white dark:bg-gray-800 rounded-lg flex items-center justify-center mr-3 shadow-sm border border-purple-100 dark:border-purple-800">
            <Star className="w-4 h-4 text-purple-500 fill-current" />
          </div>
          <p className="text-gray-700 dark:text-gray-300 text-sm leading-snug font-medium">
            {h.replace(/^[\d\-\.\s]+/, "")}
          </p>
        </div>
      ))}
    </div>
  );
}

function SectionAccordion({ sections, sectionsMap }: { sections: AstroSection[], sectionsMap: Record<string, string> }) {
  const [openKeys, setOpenKeys] = useState<string[]>(sections[0] ? [sections[0].key] : []);

  const toggleSection = (key: string) => {
    setOpenKeys(prev => 
      prev.includes(key) 
        ? prev.filter(k => k !== key) 
        : [...prev, key]
    );
  };

  return (
    <div className="space-y-3">
      {sections.map((section) => {
        const isOpen = openKeys.includes(section.key);
        return (
          <div key={section.key} className="border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden shadow-sm bg-white dark:bg-gray-900">
            <button
              onClick={() => toggleSection(section.key)}
              className="w-full flex items-center justify-between p-4 text-left bg-gray-50/30 dark:bg-gray-800/30 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <span className="font-bold text-gray-800 dark:text-gray-200">
                {sectionsMap[section.key] || section.heading}
              </span>
              {isOpen ? <ChevronUp className="w-5 h-4 text-purple-500" /> : <ChevronDown className="w-5 h-4 text-gray-400" />}
            </button>
            {isOpen && (
              <div className="p-4 border-t border-gray-100 dark:border-gray-800 animate-in fade-in duration-300">
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed text-sm">
                  {section.content}
                </p>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function AdviceList({ advice }: { advice: string[] }) {
  return (
    <div className="space-y-4">
      {advice.map((item, i) => (
        <div key={i} className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-0.5">
            <div className="w-5 h-5 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center">
              <Star className="w-3 h-3 text-blue-600 dark:text-blue-400 fill-current" />
            </div>
          </div>
          <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed m-0">
            {item.replace(/^\d+[\.\s]*/, "")}
          </p>
        </div>
      ))}
    </div>
  );
}

function formatEvidenceId(eid: string): string {
  const parts = eid.split("_");
  const map: Record<string, string> = {
    SUN: "Soleil", MOON: "Lune", MERCURY: "Mercure", VENUS: "Vénus", MARS: "Mars",
    JUPITER: "Jupiter", SATURN: "Saturne", URANUS: "Uranus", NEPTUNE: "Neptune",
    PLUTO: "Pluton", CHIRON: "Chiron", LILITH: "Lune Noire", NODE: "Nœud Nord",
    ASC: "Ascendant", MC: "Milieu du Ciel", DSC: "Descendant", IC: "Fond du Ciel",
    ARIES: "Bélier", TAURUS: "Taureau", GEMINI: "Gémeaux", CANCER: "Cancer",
    LEO: "Lion", VIRGO: "Vierge", LIBRA: "Balance", SCORPIO: "Scorpion",
    SAGITTARIUS: "Sagittaire", CAPRICORN: "Capricorne", AQUARIUS: "Verseau", PISCES: "Poissons",
    CONJUNCTION: "conjonction", SEXTILE: "sextile", SQUARE: "carré", TRINE: "trigone", OPPOSITION: "opposition",
    RETROGRADE: "rétrograde"
  };

  return parts.map(p => {
    if (p.startsWith("H") && p.length <= 3) return `(M${p.substring(1)})`;
    if (p.startsWith("ORB")) return "";
    return map[p] || p;
  }).filter(Boolean).join(" ");
}

function EvidenceTags({ evidence, title }: { evidence: string[], title: string, t: InterpretationTranslations }) {
  return (
    <div className="evidence-tags">
      <p className="evidence-tags__title">{title}</p>
      <div className="evidence-tags__list">
        {evidence.map((e, i) => {
          const humanText = formatEvidenceId(e);
          const isAspect = e.startsWith("ASPECT_");
          const isAngle = ["ASC", "MC", "DSC", "IC"].some(a => e.includes(a));
          const modifier = isAspect ? "aspect" : isAngle ? "angle" : "planet";

          return (
            <span key={i} title={e} className={`evidence-pill evidence-pill--${modifier}`}>
              <span className="evidence-pill__dot" />
              {humanText}
            </span>
          );
        })}
      </div>
    </div>
  );
}

function UpsellBlock({ t, onOpenSelector }: { t: InterpretationTranslations, onOpenSelector: () => void }) {
  return (
    <div className="mt-12 p-8 bg-gradient-to-br from-purple-600 to-indigo-700 rounded-3xl text-white text-center shadow-xl shadow-purple-500/20 relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-10">
        <Lock className="w-32 h-32 -rotate-12 translate-x-12" />
      </div>
      <div className="relative z-10">
        <h4 className="text-2xl font-bold mb-3">{t.upsellTitle}</h4>
        <p className="text-purple-100 mb-6 max-w-md mx-auto">
          {t.upsellDescription}
        </p>
        <button
          onClick={onOpenSelector}
          className="px-8 py-3 bg-white text-purple-700 font-bold rounded-full hover:bg-purple-50 transition-colors shadow-lg"
        >
          {t.upsellCta}
        </button>
      </div>
    </div>
  );
}

function PersonaSelector({ 
  t, 
  onConfirm, 
  onCancel,
  isSubmitting
}: { 
  t: InterpretationTranslations, 
  onConfirm: (id: string) => void, 
  onCancel: () => void,
  isSubmitting?: boolean
}) {
  const { data: astrologers, isLoading, isError, refetch } = useAstrologers();

  return (
    <div
      className="modal-overlay"
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
      aria-labelledby="persona-selector-title"
    >
      <div
        className="modal-content"
        style={{ width: "min(980px, 92vw)", maxHeight: "88vh", overflowY: "auto" }}
        onClick={(event) => event.stopPropagation()}
      >
        <h4 className="modal-title" id="persona-selector-title">
          {t.personaSelectorTitle}
        </h4>

        {isLoading ? (
          <div className="flex justify-center py-8">
            <RefreshCw className="w-8 h-8 animate-spin text-purple-600" />
          </div>
        ) : isError ? (
          <div className="py-8 text-center">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 mb-4">
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-4">{t.error}</p>
            <button 
              onClick={() => refetch()}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
            >
              {t.retry}
            </button>
          </div>
        ) : (
          <AstrologerGrid
            astrologers={astrologers ?? []}
            onSelectAstrologer={(astrologer: Astrologer) => {
              if (isSubmitting) return;
              onConfirm(astrologer.id);
            }}
          />
        )}

        <div className="modal-actions">
          <button
            onClick={onCancel}
            disabled={isSubmitting}
          >
            {t.cancel}
          </button>
        </div>
      </div>
    </div>
  );
}
