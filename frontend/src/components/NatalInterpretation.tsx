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
import { Button } from "@ui/Button";
import { useAccessTokenSnapshot } from "../utils/authToken";
import { stripLeadingNumbering, stripLeadingNumber } from "@utils/strings";
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

  const [selectedInterpretationId, setSelectedInterpretationId] = useState<number | null>(null);
  const [selectedTemplateKey, setSelectedTemplateKey] = useState<string>("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const historyQuery = useNatalInterpretationsList({
    enabled: chartLoaded && !!chartId,
    chartId,
  });
  const pdfTemplatesQuery = useNatalPdfTemplates({
    enabled: chartLoaded,
    locale: lang === "fr" ? "fr" : lang,
  });

  const mainQuery = useNatalInterpretation({
    enabled: chartLoaded && !selectedInterpretationId,
    useCaseLevel,
    personaId: selectedPersonaId,
    locale: lang === "fr" ? "fr-FR" : lang === "en" ? "en-US" : "es-ES",
    forceRefresh,
    refreshKey,
  });

  const idQuery = useNatalInterpretationById({
    enabled: !!selectedInterpretationId,
    interpretationId: selectedInterpretationId ?? undefined,
    locale: lang === "fr" ? "fr-FR" : lang === "en" ? "en-US" : "es-ES",
  });

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
    setSelectedInterpretationId(null);
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
    <section className="ni-section">
      <div className="ni-header">
        <div className="ni-header__title">
          <h2 className="ni-title">{t.title}</h2>
          {data?.meta.persisted_at && (
            <span className="ni-date">
              Généré le {new Date(data.meta.persisted_at).toLocaleDateString(lang, { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>

        <div className="ni-actions">
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
              <label className="ni-template-label">
                <span>{t.templateLabel}</span>
                <select
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
                className="ni-action-btn ni-action-btn--preview"
              >
                <Eye size={16} />
                <span className="ni-action-btn__label">{t.previewPdf}</span>
              </button>

              <button
                onClick={handleDownloadPdf}
                title={t.downloadPdf}
                className="ni-action-btn ni-action-btn--download"
              >
                <Download size={16} />
                <span className="ni-action-btn__label">{t.downloadPdf}</span>
              </button>

              <button
                onClick={handleRegenerate}
                title={t.regenerate}
                className="ni-action-btn ni-action-btn--regenerate"
              >
                <RefreshCw size={16} />
                <span className="ni-action-btn__label">{t.regenerate}</span>
              </button>
            </>
          )}

          {data?.meta.level === "complete" && (
            <span className="ni-level-badge">{t.completeBadge}</span>
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
    <div className="ni-version-selector" ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="ni-version-btn"
      >
        <History size={16} style={{ color: 'var(--color-primary-strong)' }} />
        <span>
          {selectedItem
            ? `${new Date(selectedItem.created_at).toLocaleDateString(lang)} - ${selectedItem.persona_name || 'Standard'}`
            : t.historyTitle}
        </span>
        <ChevronDown
          size={12}
          className={`ni-version-btn__chevron${isOpen ? ' ni-version-btn__chevron--open' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="ni-version-dropdown">
          <div className="ni-version-dropdown__header">
            <span className="ni-version-dropdown__label">{t.historyTitle}</span>
          </div>
          <div className="ni-version-dropdown__list">
            {items.map((item) => (
              <div
                key={item.id}
                className={`ni-version-item${selectedId === item.id ? ' ni-version-item--selected' : ''}`}
              >
                <button
                  type="button"
                  className="ni-version-item__btn"
                  onClick={() => {
                    onSelect(item.id);
                    setIsOpen(false);
                  }}
                >
                  <span className={`ni-version-item__name${selectedId === item.id ? ' ni-version-item__name--selected' : ''}`}>
                    {item.persona_name || 'Standard'}
                  </span>
                  <span className="ni-version-item__date">
                    {new Date(item.created_at).toLocaleString(lang, { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })} · {item.level === 'complete' ? t.completeBadge : 'Short'}
                  </span>
                </button>
                <button
                  type="button"
                  onClick={(e) => { e.stopPropagation(); onDeleteRequest(item.id); }}
                  className="ni-version-item__delete"
                  title={t.deleteCta}
                >
                  <Trash2 size={14} />
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
        <div className="ni-modal-header">
          <div className="ni-modal-icon">
            <AlertCircle size={24} />
          </div>
          <h4 className="ni-modal-heading" id="delete-confirm-title">{t.deleteConfirm}</h4>
        </div>
        <p className="ni-modal-body">{t.deleteConfirmSub}</p>
        <div className="ni-modal-footer">
          <Button variant="ghost" onClick={onCancel} disabled={isDeleting}>
            {t.cancel}
          </Button>
          <Button variant="danger" onClick={onConfirm} loading={isDeleting} leftIcon={<RefreshCw size={12} />}>
            {t.deleteCta}
          </Button>
        </div>
      </div>
    </div>
  );
}

function InterpretationSkeleton({ t, isComplete }: { t: InterpretationTranslations, isComplete?: boolean }) {
  return (
    <div className="ni-skeleton">
      <div className="ni-skeleton__line ni-skeleton__line--75" />
      <div className="ni-skeleton__line" />
      <div className="ni-skeleton__line ni-skeleton__line--83" />
      <div className="ni-skeleton__tabs">
        {[1, 2, 3].map(i => <div key={i} className="ni-skeleton__tab" />)}
      </div>
      <div className="ni-skeleton__block" />
      <p className="ni-skeleton__caption">
        {isComplete ? t.requestingComplete : t.loading}
      </p>
    </div>
  );
}

function InterpretationError({ t, onRetry }: { t: InterpretationTranslations, onRetry: () => void }) {
  return (
    <div className="ni-error">
      <div className="ni-error__icon">
        <AlertCircle size={32} />
      </div>
      <p className="ni-error__message">{t.error}</p>
      <Button variant="danger" onClick={onRetry} leftIcon={<RefreshCw size={16} />}>
        {t.retry}
      </Button>
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
    <div className="ni-content">
      {degraded_mode && (
        <div className="ni-degraded-notice">
          <Star size={16} style={{ fill: 'currentColor', flexShrink: 0 }} />
          {t.degradedNotice}
        </div>
      )}

      <div>
        <h3 className="ni-interpretation-title">{interpretation.title}</h3>
        {meta.persona_name && (
          <p className="ni-persona-text">
            {t.completeBy} <strong>{meta.persona_name}</strong>
          </p>
        )}
        <p className="ni-summary">{interpretation.summary}</p>
      </div>

      <div>
        <p className="ni-section-label">{t.highlightsTitle}</p>
        <HighlightsChips highlights={highlights} />
      </div>

      <SectionAccordion sections={sections} sectionsMap={t.sectionsMap} />

      <div className="ni-advice-block">
        <h4 className="ni-advice-title">{t.adviceTitle}</h4>
        <AdviceList advice={advice} />
      </div>

      <EvidenceTags evidence={evidence} title={t.evidenceTitle} t={t} />

      {disclaimers.length > 0 && (
        <footer className="ni-disclaimer-footer">
          <div className="ni-degraded-notice ni-degraded-notice--disclaimer">
            <p className="ni-disclaimer-title">
              <AlertCircle size={14} />
              {t.disclaimerTitle}
            </p>
            <div className="ni-disclaimer-list">
              {disclaimers.map((d, i) => (
                <p key={i} className="ni-disclaimer-item">{d}</p>
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
    <div className="ni-highlights">
      {highlights.map((h, i) => (
        <div key={i} className="ni-highlight-chip">
          <div className="ni-highlight-icon">
            <Star size={16} className="ni-highlight-star" />
          </div>
          <p className="ni-highlight-text">{stripLeadingNumbering(h)}</p>
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
    <div className="ni-accordion">
      {sections.map((section, index) => {
        const sectionId = `${section.key}-${index}`;
        const isOpen = openIds.includes(sectionId);
        return (
          <div key={sectionId} className="ni-accordion-item">
            <button onClick={() => toggleSection(sectionId)} className="ni-accordion-header">
              <span className="ni-accordion-title">
                {sectionsMap[section.key] || section.heading}
              </span>
              {isOpen
                ? <ChevronUp size={20} className="ni-accordion-icon ni-accordion-icon--open" />
                : <ChevronDown size={20} className="ni-accordion-icon ni-accordion-icon--closed" />
              }
            </button>
            {isOpen && (
              <div className="ni-accordion-body">
                <p className="ni-accordion-text">{section.content}</p>
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
    <div className="ni-advice-list">
      {advice.map((item, i) => (
        <div key={i} className="ni-advice-item">
          <div className="ni-advice-icon">
            <Star size={12} className="ni-advice-star" />
          </div>
          <p className="ni-advice-text">{stripLeadingNumber(item)}</p>
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
    <div className="ni-evidence-tags">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="ni-evidence-toggle-btn"
      >
        <div>
          <p className="ni-evidence-tags-title">
            {title}
          </p>
          <p className="ni-evidence-intro">{t.evidenceIntro}</p>
          <p className="ni-evidence-count">
            {totalCount} élément{totalCount > 1 ? "s" : ""} dédupliqué{totalCount > 1 ? "s" : ""}
          </p>
        </div>
        <span className="ni-evidence-toggle-icon">
          {open ? t.hideEvidence : t.showEvidence}
          {open ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </span>
      </button>

      {open && (
        <div className="ni-evidence-content">
          {orderedKeys.map((key) => {
            const items = grouped[key];
            if (items.length === 0) return null;
            return (
              <div key={key}>
                <p className="ni-evidence-category-label">{categoryLabels[key]}</p>
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
    <div className="ni-upsell">
      <div className="ni-upsell__icon-bg">
        <Lock size={128} className="ni-upsell__lock-icon" />
      </div>
      <div className="ni-upsell__content">
        <h4 className="ni-upsell__title">{t.upsellTitle}</h4>
        <p className="ni-upsell__desc">{t.upsellDescription}</p>
        <button onClick={onOpenSelector} className="ni-upsell__cta">
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
          <div className="ni-loader-container">
            <RefreshCw size={32} className="ni-loader-spin" />
          </div>
        ) : isError ? (
          <div className="ni-modal-error">
            <div className="ni-modal-error-icon">
              <AlertCircle size={24} />
            </div>
            <p className="ni-modal-error-text">{t.error}</p>
            <Button variant="secondary" onClick={() => refetch()}>{t.retry}</Button>
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
          <p className="ni-modal-empty-text">
            Tous les astrologues disponibles ont déjà une interprétation.
          </p>
        )}

        <div className="modal-actions">
          <button onClick={onCancel} disabled={isSubmitting} className="ni-modal-cancel-btn">
            {t.cancel}
          </button>
        </div>
      </div>
    </div>
  );
}
