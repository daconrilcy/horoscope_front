import { useState } from "react";
import { 
  useNatalInterpretation, 
  type NatalInterpretationResult, 
  type AstroSection 
} from "../api/natalChart";
import { useAstrologers } from "../api/astrologers";
import { natalChartTranslations } from "../i18n/natalChart";
import { type AstrologyLang } from "../i18n/astrology";
import { ChevronDown, ChevronUp, Lock, RefreshCw, Star, User, AlertCircle } from "lucide-react";

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

  const { data, isLoading, error, refetch } = useNatalInterpretation({
    enabled: chartLoaded,
    useCaseLevel,
    personaId: selectedPersonaId,
    locale: lang === "fr" ? "fr-FR" : lang === "en" ? "en-US" : "es-ES",
  });

  const handleUpgrade = (personaId: string) => {
    setSelectedPersonaId(personaId);
    setUseCaseLevel("complete");
    setIsUpsellOpen(false);
  };

  if (!chartLoaded) return null;

  return (
    <section className="mt-8 border-t pt-8 border-gray-200 dark:border-gray-800">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">
          {t.title}
        </h2>
        {data?.meta.level === "complete" && (
          <span className="bg-purple-100 text-purple-800 text-xs font-medium px-2.5 py-0.5 rounded dark:bg-purple-900 dark:text-purple-300 border border-purple-400">
            {t.completeBadge}
          </span>
        )}
      </div>

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

      <EvidenceTags evidence={interpretation.evidence} title={t.evidenceTitle} />
    </div>
  );
}

function HighlightsChips({ highlights }: { highlights: string[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {highlights.map((h, i) => (
        <span key={i} className="px-3 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm text-gray-700 dark:text-gray-300 shadow-sm">
          {h}
        </span>
      ))}
    </div>
  );
}

function SectionAccordion({ sections, sectionsMap }: { sections: AstroSection[], sectionsMap: Record<string, string> }) {
  const [openKey, setOpenKey] = useState<string | null>(sections[0]?.key || null);

  return (
    <div className="space-y-2">
      {sections.map((section) => (
        <div key={section.key} className="border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden shadow-sm">
          <button
            onClick={() => setOpenKey(openKey === section.key ? null : section.key)}
            className="w-full flex items-center justify-between p-4 text-left bg-gray-50/50 dark:bg-gray-800/50 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <span className="font-semibold text-gray-800 dark:text-gray-200">
              {sectionsMap[section.key] || section.heading}
            </span>
            {openKey === section.key ? <ChevronUp className="w-5 h-4" /> : <ChevronDown className="w-5 h-4" />}
          </button>
          {openKey === section.key && (
            <div className="p-4 bg-white dark:bg-gray-900 border-t border-gray-100 dark:border-gray-800">
              <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                {section.content}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function AdviceList({ advice }: { advice: string[] }) {
  return (
    <ol className="space-y-3">
      {advice.map((item, i) => (
        <li key={i} className="flex items-start text-gray-700 dark:text-gray-300 leading-snug">
          <span className="flex-shrink-0 w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-xs font-bold mr-3 mt-0.5">
            {i + 1}
          </span>
          {item}
        </li>
      ))}
    </ol>
  );
}

function EvidenceTags({ evidence, title }: { evidence: string[], title: string }) {
  return (
    <div className="pt-4 border-t border-gray-100 dark:border-gray-800">
      <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 dark:text-gray-600 mb-2">
        {title}
      </p>
      <div className="flex flex-wrap gap-1.5 opacity-50 grayscale hover:opacity-100 hover:grayscale-0 transition-all duration-300">
        {evidence.map((e, i) => (
          <span key={i} className="text-[9px] px-1.5 py-0.5 bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 font-mono rounded border border-gray-200 dark:border-gray-700">
            {e}
          </span>
        ))}
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
  const [selectedId, setSelectedId] = useState<string | null>(null);

  return (
    <div className="mt-8 p-6 bg-white dark:bg-gray-800 border border-purple-200 dark:border-purple-900 rounded-3xl shadow-lg animate-in fade-in slide-in-from-bottom-4 duration-500">
      <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-6 text-center" id="persona-selector-title">
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
        <div 
          className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8"
          role="radiogroup"
          aria-labelledby="persona-selector-title"
        >
          {astrologers?.map((astrologer) => (
            <button 
              key={astrologer.id}
              onClick={() => setSelectedId(astrologer.id)}
              disabled={isSubmitting}
              aria-checked={selectedId === astrologer.id}
              role="radio"
              className={`p-4 rounded-2xl border-2 transition-all cursor-pointer flex items-start text-left gap-4 ${
                selectedId === astrologer.id 
                  ? "border-purple-600 bg-purple-50 dark:bg-purple-900/20" 
                  : "border-gray-100 dark:border-gray-700 hover:border-purple-200"
              } ${isSubmitting ? "opacity-50 cursor-not-allowed" : ""}`}
            >
              <div className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center flex-shrink-0">
                <User className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="font-bold text-gray-900 dark:text-white">{astrologer.name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                  {astrologer.bio_short}
                </p>
                <div className="mt-2 flex flex-wrap gap-1">
                  {astrologer.specialties.slice(0, 2).map(s => (
                    <span key={s} className="text-[10px] px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-3">
        <button
          disabled={!selectedId || isSubmitting}
          onClick={() => selectedId && onConfirm(selectedId)}
          className="flex-1 px-6 py-3 bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-xl hover:bg-purple-700 transition-colors shadow-md flex items-center justify-center"
        >
          {isSubmitting && <RefreshCw className="w-4 h-4 mr-2 animate-spin" />}
          {t.personaSelectorConfirm}
        </button>
        <button
          onClick={onCancel}
          disabled={isSubmitting}
          className="px-6 py-3 bg-gray-100 dark:bg-gray-700 disabled:opacity-50 text-gray-600 dark:text-gray-300 font-bold rounded-xl hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
        >
          {t.cancel}
        </button>
      </div>
    </div>
  );
}
