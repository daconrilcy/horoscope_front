import { useEffect, useRef, useState } from "react";
import { 
  useNatalInterpretation, 
  useNatalInterpretationsList,
  useNatalPdfTemplates,
  useNatalInterpretationById,
  deleteNatalInterpretation,
  downloadNatalInterpretationPdf,
  previewNatalInterpretationPdf,
  type NatalInterpretationResult, 
  type AstroSection,
  type NatalInterpretationListItem
} from "../api/natalChart";
import { useAstrologers, type Astrologer } from "../api/astrologers";
import { AstrologerGrid } from "../features/astrologers";
import { natalChartTranslations } from "../i18n/natalChart";
import { type AstrologyLang } from "../i18n/astrology";
import { 
  ChevronDown, 
  ChevronUp, 
  Lock, 
  RefreshCw, 
  Star, 
  AlertCircle, 
  Trash2, 
  History,
  Download,
  Eye
} from "lucide-react";
import { ErrorBoundary } from "@components/ErrorBoundary";
import { useAccessTokenSnapshot } from "../utils/authToken";
import "./NatalInterpretation.css";

interface Props {
  chartLoaded: boolean;
  chartId?: string;
  lang: AstrologyLang;
}

type InterpretationTranslations = typeof natalChartTranslations['fr']['interpretation'];

export function NatalInterpretationSection({ chartLoaded, chartId, lang }: Props) {
  const t = natalChartTranslations[lang].interpretation;
  const accessToken = useAccessTokenSnapshot();
  
  const [useCaseLevel, setUseCaseLevel] = useState<"short" | "complete">("short");
  const [selectedPersonaId, setSelectedPersonaId] = useState<string | null>(null);
  const [isUpsellOpen, setIsUpsellOpen] = useState(false);
  const [forceRefresh, setForceRefresh] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);
  
  // New state for history
  const [selectedInterpretationId, setSelectedInterpretationId] = useState<number | null>(null);
  const [selectedTemplateKey, setSelectedTemplateKey] = useState<string>("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // 1. Fetch versions list
  const historyQuery = useNatalInterpretationsList({
    enabled: chartLoaded && !!chartId,
    chartId,
  });
  const pdfTemplatesQuery = useNatalPdfTemplates({
    enabled: chartLoaded,
    locale: lang === "fr" ? "fr" : lang,
  });

  // 2. Main interpretation query (POST) - used for auto-load/generate
  const mainQuery = useNatalInterpretation({
    enabled: chartLoaded && !selectedInterpretationId,
    useCaseLevel,
    personaId: selectedPersonaId,
    locale: lang === "fr" ? "fr-FR" : lang === "en" ? "en-US" : "es-ES",
    forceRefresh,
    refreshKey,
  });

  // 3. Specific interpretation query (GET by ID) - used when selecting from history
  const idQuery = useNatalInterpretationById({
    enabled: !!selectedInterpretationId,
    interpretationId: selectedInterpretationId ?? undefined,
    locale: lang === "fr" ? "fr-FR" : lang === "en" ? "en-US" : "es-ES",
  });

  // Determine which data to show
  const activeQuery = selectedInterpretationId ? idQuery : mainQuery;
  const { data, isLoading, error, refetch } = activeQuery;

  useEffect(() => {
    if (selectedTemplateKey) return;
    const defaultTemplate = pdfTemplatesQuery.data?.items.find((item) => item.is_default);
    if (defaultTemplate) {
      setSelectedTemplateKey(defaultTemplate.key);
    }
  }, [pdfTemplatesQuery.data, selectedTemplateKey]);

  const handleUpgrade = (personaId: string) => {
    setSelectedPersonaId(personaId);
    setUseCaseLevel("complete");
    setIsUpsellOpen(false);
    setSelectedInterpretationId(null); // Clear selected ID to trigger new generation
    setForceRefresh(true);
    setRefreshKey((previous) => previous + 1);
  };

  const handleRegenerate = () => {
    const historyItems = historyQuery.data?.items ?? [];
    const hasShortInterpretation = historyItems.some((item) => item.level === "short");
    const hasCompleteInterpretation = historyItems.some((item) => item.level === "complete");
    if (hasShortInterpretation && hasCompleteInterpretation) {
      setSelectedInterpretationId(null);
      setForceRefresh(false);
      setIsUpsellOpen(true);
      return;
    }
    setSelectedInterpretationId(null);
    setForceRefresh(true);
    setRefreshKey((previous) => previous + 1);
  };

  const handleSelectVersion = (id: number | null) => {
    setSelectedInterpretationId(id);
    if (id === null) {
      // Reset to default latest behavior
      setUseCaseLevel("short");
      setSelectedPersonaId(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!accessToken) return;
    setIsDeleting(true);
    try {
      await deleteNatalInterpretation(accessToken, id);
      const updatedHistory = await historyQuery.refetch();
      
      if (selectedInterpretationId === id) {
        // Find next available version if any
        const remaining = updatedHistory.data?.items || [];
        if (remaining.length > 0) {
          setSelectedInterpretationId(remaining[0].id);
        } else {
          setSelectedInterpretationId(null);
        }
      }
      setShowDeleteConfirm(null);
    } catch (err) {
      console.error("Failed to delete interpretation", err);
    } finally {
      setIsDeleting(false);
    }
  };

  const currentInterpretationId =
    selectedInterpretationId ??
    data?.meta.id ??
    historyQuery.data?.items.find((i) => i.created_at === data?.meta.persisted_at)?.id ??
    historyQuery.data?.items[0]?.id;
  const usedPersonaIds = new Set(
    (historyQuery.data?.items ?? [])
      .filter((item) => item.level === "complete" && Boolean(item.persona_id))
      .map((item) => item.persona_id as string),
  );

  const handlePreviewPdf = async () => {
    if (!accessToken || !currentInterpretationId) return;
    try {
      await previewNatalInterpretationPdf(
        accessToken,
        currentInterpretationId,
        selectedTemplateKey || undefined,
        lang === "fr" ? "fr" : lang,
      );
    } catch (err) {
      console.error("Failed to preview PDF", err);
    }
  };

  const handleDownloadPdf = async () => {
    
    if (!accessToken || !currentInterpretationId) return;
    try {
      await downloadNatalInterpretationPdf(
        accessToken,
        currentInterpretationId,
        selectedTemplateKey || undefined,
        lang === "fr" ? "fr" : lang,
      );
    } catch (err) {
      console.error("Failed to download PDF", err);
    }
  };

  if (!chartLoaded) return null;

  return (
    <section className="mt-8 border-t pt-8 border-gray-200 dark:border-gray-800">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
        <div className="flex flex-col">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white uppercase tracking-wide">
            {t.title}
          </h2>
          {data?.meta.persisted_at && (
            <span className="text-[10px] text-gray-400 dark:text-gray-500 mt-1">
              Généré le {new Date(data.meta.persisted_at).toLocaleDateString(lang, { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>
        
        <div className="flex flex-wrap items-center gap-2">
          {/* History Selector */}
          {historyQuery.data && historyQuery.data.items.length > 0 && (
            <VersionSelector 
              items={historyQuery.data.items} 
              selectedId={selectedInterpretationId || (historyQuery.data.items.find(i => i.created_at === data?.meta.persisted_at)?.id ?? null)}
              onSelect={handleSelectVersion}
              onDeleteRequest={(id) => setShowDeleteConfirm(id)}
              t={t}
              lang={lang}
            />
          )}

          {data && !isLoading && (
            <>
              <label className="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-full dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700">
                <span>{t.templateLabel}</span>
                <select
                  className="bg-transparent border-none focus:outline-none text-xs"
                  value={selectedTemplateKey}
                  onChange={(event) => setSelectedTemplateKey(event.target.value)}
                  aria-label={t.templateLabel}
                >
                  {pdfTemplatesQuery.data?.items.map((template) => (
                    <option key={template.key} value={template.key}>
                      {template.name}
                    </option>
                  ))}
                  {!pdfTemplatesQuery.data?.items.length && (
                    <option value="default_natal">default_natal</option>
                  )}
                </select>
              </label>

              <button 
                onClick={handlePreviewPdf}
                title={t.previewPdf}
                className="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-slate-700 bg-slate-50 border border-slate-200 rounded-full hover:bg-slate-100 transition-colors dark:bg-slate-900/20 dark:text-slate-300 dark:border-slate-700"
              >
                <Eye className="w-4 h-4" />
                <span className="hidden sm:inline">{t.previewPdf}</span>
              </button>

              <button 
                onClick={handleDownloadPdf}
                title={t.downloadPdf}
                className="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-full hover:bg-blue-100 transition-colors dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-800"
              >
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline">{t.downloadPdf}</span>
              </button>

              <button 
                onClick={handleRegenerate}
                title={t.regenerate}
                className="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-purple-700 bg-purple-50 border border-purple-200 rounded-full hover:bg-purple-100 transition-colors dark:bg-purple-900/20 dark:text-purple-300 dark:border-purple-800"
              >
                <RefreshCw className="w-4 h-4" />
                <span className="hidden sm:inline">{t.regenerate}</span>
              </button>
            </>
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
            
            {useCaseLevel === "short" && !isUpsellOpen && !selectedInterpretationId && (
              <UpsellBlock t={t} onOpenSelector={() => setIsUpsellOpen(true)} />
            )}

            {isUpsellOpen && (
              <PersonaSelector 
                t={t} 
                onConfirm={handleUpgrade} 
                onCancel={() => setIsUpsellOpen(false)} 
                isSubmitting={isLoading && useCaseLevel === "complete"}
                excludedPersonaIds={usedPersonaIds}
              />
            )}
          </>
        ) : null}
      </ErrorBoundary>

      {showDeleteConfirm && (
        <ConfirmDeleteModal 
          t={t} 
          onConfirm={() => handleDelete(showDeleteConfirm)} 
          onCancel={() => setShowDeleteConfirm(null)}
          isDeleting={isDeleting}
        />
      )}
    </section>
  );
}

function VersionSelector({ 
  items, 
  selectedId, 
  onSelect, 
  onDeleteRequest,
  t,
  lang 
}: { 
  items: NatalInterpretationListItem[], 
  selectedId: number | null, 
  onSelect: (id: number | null) => void,
  onDeleteRequest: (id: number) => void,
  t: InterpretationTranslations,
  lang: string
}) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const selectedItem = items.find(i => i.id === selectedId);

  useEffect(() => {
    if (!isOpen) return;
    const handleOutsideClick = (event: MouseEvent | TouchEvent) => {
      const target = event.target as Node | null;
      if (!target) return;
      if (containerRef.current && !containerRef.current.contains(target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    document.addEventListener("touchstart", handleOutsideClick);
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
      document.removeEventListener("touchstart", handleOutsideClick);
    };
  }, [isOpen]);

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-gray-700 bg-white border border-gray-300 rounded-full hover:bg-gray-50 transition-colors dark:bg-gray-800 dark:text-gray-200 dark:border-gray-700 shadow-sm"
      >
        <History className="w-4 h-4 text-purple-500" />
        <span>
          {selectedItem 
            ? `${new Date(selectedItem.created_at).toLocaleDateString(lang)} - ${selectedItem.persona_name || 'Standard'}` 
            : t.historyTitle}
        </span>
        <ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
          <div className="absolute right-0 mt-2 w-72 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl z-40 overflow-hidden animate-in fade-in zoom-in-95 duration-100">
            <div className="p-3 border-b border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/50">
              <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500 dark:text-gray-400">
                {t.historyTitle}
              </span>
            </div>
            <div className="max-h-64 overflow-y-auto">
              {items.map((item) => (
                <div
                  key={item.id}
                  className={`group flex items-center justify-between p-3 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors ${selectedId === item.id ? 'bg-purple-50/50 dark:bg-purple-900/10' : ''}`}
                >
                  <button
                    type="button"
                    className="flex flex-col min-w-0 text-left flex-1"
                    onClick={() => {
                      onSelect(item.id);
                      setIsOpen(false);
                    }}
                  >
                    <span className={`text-xs font-medium truncate ${selectedId === item.id ? 'text-purple-700 dark:text-purple-400' : 'text-gray-700 dark:text-gray-300'}`}>
                      {item.persona_name || 'Standard'}
                    </span>
                    <span className="text-[10px] text-gray-500 dark:text-gray-500">
                      {new Date(item.created_at).toLocaleString(lang, { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })} · {item.level === 'complete' ? t.completeBadge : 'Short'}
                    </span>
                  </button>
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); onDeleteRequest(item.id); }}
                    className="opacity-70 sm:opacity-0 sm:group-hover:opacity-100 p-1.5 text-gray-400 hover:text-red-500 transition-all rounded-md hover:bg-red-50 dark:hover:bg-red-900/30"
                    title={t.deleteCta}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
      )}
    </div>
  );
}

function ConfirmDeleteModal({ t, onConfirm, onCancel, isDeleting }: { t: InterpretationTranslations, onConfirm: () => void, onCancel: () => void, isDeleting: boolean }) {
  return (
    <div 
      className="modal-overlay" 
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-confirm-title"
    >
      <div className="modal-content natal-interpretation__modal" onClick={e => e.stopPropagation()}>
        <div className="flex items-center gap-3 text-red-600 mb-4">
          <div className="p-2 bg-red-100 dark:bg-red-900/30 rounded-full">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h4 className="text-lg font-bold m-0" id="delete-confirm-title">{t.deleteConfirm}</h4>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-6 text-sm">
          {t.deleteConfirmSub}
        </p>
        <div className="flex justify-end gap-3">
          <button 
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            disabled={isDeleting}
          >
            {t.cancel}
          </button>
          <button 
            onClick={onConfirm}
            className="px-4 py-2 text-sm font-bold text-white bg-red-600 hover:bg-red-700 rounded-lg transition-colors flex items-center gap-2"
            disabled={isDeleting}
          >
            {isDeleting && <RefreshCw className="w-3 h-3 animate-spin" />}
            {t.deleteCta}
          </button>
        </div>
      </div>
    </div>
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
  const highlights = Array.isArray(interpretation.highlights) ? interpretation.highlights : [];
  const sections = Array.isArray(interpretation.sections) ? interpretation.sections : [];
  const advice = Array.isArray(interpretation.advice) ? interpretation.advice : [];
  const evidence = Array.isArray(interpretation.evidence) ? interpretation.evidence : [];
  const disclaimers = Array.isArray(data.disclaimers)
    ? data.disclaimers
    : Array.isArray(interpretation.disclaimers)
      ? interpretation.disclaimers
      : [];

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
        <HighlightsChips highlights={highlights} />
      </div>

      <SectionAccordion sections={sections} sectionsMap={t.sectionsMap} />

      <div className="bg-blue-50 dark:bg-blue-900/10 p-6 rounded-2xl">
        <h4 className="text-lg font-bold text-blue-900 dark:text-blue-300 mb-4">
          {t.adviceTitle}
        </h4>
        <AdviceList advice={advice} />
      </div>

      <EvidenceTags evidence={evidence} title={t.evidenceTitle} t={t} />

      {disclaimers.length > 0 && (
        <footer className="mt-2 border-t border-gray-200 dark:border-gray-800 pt-4">
          <div className="rounded-xl bg-amber-50/70 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 p-4">
            <p className="font-bold uppercase tracking-tight text-[11px] text-amber-900 dark:text-amber-300 mb-2 flex items-center gap-2">
              <AlertCircle className="w-3.5 h-3.5" />
              {t.disclaimerTitle}
            </p>
            <div className="space-y-2 text-xs text-amber-900/90 dark:text-amber-200/90">
              {disclaimers.map((d, i) => (
                <p key={i}>{d}</p>
              ))}
            </div>
          </div>
        </footer>
      )}
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
  const [openIds, setOpenIds] = useState<string[]>(sections[0] ? [`${sections[0].key}-0`] : []);

  const toggleSection = (sectionId: string) => {
    setOpenIds(prev =>
      prev.includes(sectionId)
        ? prev.filter(id => id !== sectionId)
        : [...prev, sectionId]
    );
  };

  return (
    <div className="space-y-3">
      {sections.map((section, index) => {
        const sectionId = `${section.key}-${index}`;
        const isOpen = openIds.includes(sectionId);
        return (
          <div key={sectionId} className="border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden shadow-sm bg-white dark:bg-gray-900">
            <button
              onClick={() => toggleSection(sectionId)}
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

  const label = (token: string): string => map[token] || token;
  const planetSignHouse = eid.match(/^([A-Z]+)_([A-Z]+)_H(\d{1,2})$/);
  if (planetSignHouse) {
    const [, planet, sign, house] = planetSignHouse;
    return `${label(planet)} ${label(sign)} (M${house})`;
  }

  const planetSign = eid.match(/^([A-Z]+)_([A-Z]+)$/);
  if (planetSign) {
    const [, planet, sign] = planetSign;
    if (["ASC", "MC", "DSC", "IC"].includes(planet)) {
      return `${label(planet)} ${label(sign)}`;
    }
    if (map[planet] && map[sign]) {
      return `${label(planet)} ${label(sign)}`;
    }
  }

  const houseInSign = eid.match(/^HOUSE_(\d{1,2})_IN_([A-Z]+)$/);
  if (houseInSign) {
    const [, house, sign] = houseInSign;
    return `Maison ${house} en ${label(sign)}`;
  }

  const aspectPrefixed = eid.match(/^ASPECT_([A-Z]+)_([A-Z]+)_([A-Z]+)$/);
  if (aspectPrefixed) {
    const [, a, b, kind] = aspectPrefixed;
    return `Aspect ${label(a)} - ${label(b)} (${label(kind)})`;
  }

  const aspectLegacy = eid.match(/^(CONJUNCTION|SEXTILE|SQUARE|TRINE|OPPOSITION)_([A-Z]+)_([A-Z]+)$/);
  if (aspectLegacy) {
    const [, kind, a, b] = aspectLegacy;
    return `Aspect ${label(a)} - ${label(b)} (${label(kind)})`;
  }

  const parts = eid.split("_");
  return parts
    .map((p) => {
      if (p.startsWith("H") && p.length <= 3) return `(M${p.substring(1)})`;
      if (p.startsWith("ORB")) return "";
      return label(p);
    })
    .filter(Boolean)
    .join(" ");
}

type EvidenceCategoryKey =
  | "angles"
  | "personal_planets"
  | "slow_planets"
  | "dominant_houses"
  | "major_aspects"
  | "other"

function _categorizeEvidence(eid: string): EvidenceCategoryKey {
  if (
    eid.startsWith("ASPECT_") ||
    /^(CONJUNCTION|SEXTILE|SQUARE|TRINE|OPPOSITION)_/.test(eid)
  ) {
    return "major_aspects";
  }
  if (/^(ASC|MC|DSC|IC)_/.test(eid) || /(ASC|MC|DSC|IC)/.test(eid)) {
    return "angles";
  }
  if (/^HOUSE_\d{1,2}_IN_/.test(eid) || /_H\d{1,2}$/.test(eid)) {
    return "dominant_houses";
  }
  if (/^(SUN|MOON|MERCURY|VENUS|MARS)(_|$)/.test(eid)) {
    return "personal_planets";
  }
  if (/^(JUPITER|SATURN|URANUS|NEPTUNE|PLUTO)(_|$)/.test(eid)) {
    return "slow_planets";
  }
  return "other";
}

function EvidenceTags({
  evidence,
  title,
  t,
}: {
  evidence: string[]
  title: string
  t: InterpretationTranslations
}) {
  const [open, setOpen] = useState(false);
  const categoryLabels: Record<EvidenceCategoryKey, string> = {
    angles: t.evidenceCategories.angles,
    personal_planets: t.evidenceCategories.personalPlanets,
    slow_planets: t.evidenceCategories.slowPlanets,
    dominant_houses: t.evidenceCategories.dominantHouses,
    major_aspects: t.evidenceCategories.majorAspects,
    other: t.evidenceCategories.other,
  };

  const deduped = Array.from(
    new Map(
      evidence.map((eid) => {
        const humanText = formatEvidenceId(eid);
        return [humanText.toLowerCase(), { eid, humanText }];
      }),
    ).values(),
  );

  const grouped = deduped.reduce(
    (acc, item) => {
      const key = _categorizeEvidence(item.eid);
      acc[key].push(item);
      return acc;
    },
    {
      angles: [] as Array<{ eid: string; humanText: string }>,
      personal_planets: [] as Array<{ eid: string; humanText: string }>,
      slow_planets: [] as Array<{ eid: string; humanText: string }>,
      dominant_houses: [] as Array<{ eid: string; humanText: string }>,
      major_aspects: [] as Array<{ eid: string; humanText: string }>,
      other: [] as Array<{ eid: string; humanText: string }>,
    },
  );

  const orderedKeys: EvidenceCategoryKey[] = [
    "angles",
    "personal_planets",
    "slow_planets",
    "dominant_houses",
    "major_aspects",
    "other",
  ];

  const totalCount = deduped.length;

  return (
    <div className="evidence-tags border border-gray-200 dark:border-gray-800 rounded-2xl p-4 bg-gray-50/50 dark:bg-gray-900/30">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="w-full flex items-center justify-between gap-3 text-left"
      >
        <div>
          <p className="evidence-tags__title font-semibold text-sm text-gray-700 dark:text-gray-200">
            {title}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{t.evidenceIntro}</p>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            {totalCount} élément{totalCount > 1 ? "s" : ""} dédupliqué{totalCount > 1 ? "s" : ""}
          </p>
        </div>
        <span className="inline-flex items-center gap-2 text-xs font-medium text-purple-700 dark:text-purple-300">
          {open ? t.hideEvidence : t.showEvidence}
          {open ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </span>
      </button>

      {open && (
        <div className="mt-4 space-y-4">
          {orderedKeys.map((key) => {
            const items = grouped[key];
            if (items.length === 0) return null;
            return (
              <div key={key}>
                <p className="text-[11px] uppercase tracking-wide font-semibold text-gray-500 dark:text-gray-400 mb-2">
                  {categoryLabels[key]}
                </p>
                <div className="evidence-tags__list">
                  {items.map((item, i) => {
                    const isAspect = item.eid.startsWith("ASPECT_");
                    const isAngle = ["ASC", "MC", "DSC", "IC"].some((a) =>
                      item.eid.includes(a),
                    );
                    const modifier = isAspect ? "aspect" : isAngle ? "angle" : "planet";
                    return (
                      <span
                        key={`${item.eid}-${i}`}
                        title={item.eid}
                        className={`evidence-pill evidence-pill--${modifier}`}
                      >
                        <span className="evidence-pill__dot" />
                        {item.humanText}
                      </span>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      )}
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
  isSubmitting,
  excludedPersonaIds,
}: { 
  t: InterpretationTranslations, 
  onConfirm: (id: string) => void, 
  onCancel: () => void,
  isSubmitting?: boolean,
  excludedPersonaIds?: Set<string>,
}) {
  const { data: astrologers, isLoading, isError, refetch } = useAstrologers();
  const availableAstrologers = (astrologers ?? []).filter(
    (astrologer) => !excludedPersonaIds?.has(astrologer.id),
  );

  return (
    <div
      className="modal-overlay"
      onClick={onCancel}
      role="dialog"
      aria-modal="true"
      aria-labelledby="persona-selector-title"
    >
      <div
        className="modal-content natal-interpretation__fullscreen-modal"
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
        ) : availableAstrologers.length > 0 ? (
          <AstrologerGrid
            astrologers={availableAstrologers}
            onSelectAstrologer={(astrologer: Astrologer) => {
              if (isSubmitting) return;
              onConfirm(astrologer.id);
            }}
          />
        ) : (
          <div className="py-8 text-center text-sm text-gray-600 dark:text-gray-400">
            Tous les astrologues disponibles ont deja une interpretation.
          </div>
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
