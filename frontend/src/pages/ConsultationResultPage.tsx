import { useEffect, useState, useCallback, useRef, useMemo } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { useNavigate, useSearchParams, Link } from "react-router-dom"
import { ChevronLeft, MessageSquare } from "lucide-react"

import { useConsultation, CHAT_PREFILL_KEY } from "../state/consultationStore"
import { useConsultationGenerate, type ConsultationPrecheckData } from "../api/consultations"
import { useAstrologer } from "../api/astrologers"
import { detectLang } from "../i18n/astrology"
import { tConsultations as t } from "@i18n/consultations"
import {
  AUTO_ASTROLOGER_ID,
  getConsultationTypeConfig,
  getObjectiveForType,
  type ConsultationResult,
  type ConsultationSection,
  type ConsultationBlock,
} from "../types/consultation"
import { ConsultationFallbackBanner } from "../features/consultations"
import { classNames } from "../utils/classNames"
import { trackEvent, EVENTS } from "../utils/analytics"
import { PageLayout } from "../layouts"
import "./ConsultationResultPage.css"

function resolveObjectiveText(
  objective: string | undefined,
  type: ConsultationResult["type"],
  lang: ReturnType<typeof detectLang>
): string {
  if (objective && !objective.startsWith("objective_")) {
    return objective
  }
  return t(getObjectiveForType(type), lang)
}

function cleanStructuredText(text: string): string {
  return text
    .replace(/^#{1,6}\s*/u, "")
    .replace(/^\s*[-*•]\s+/u, "")
    .replace(/^\s*\d+[\).\s]+/u, "")
    .replace(/\*\*([^*]+)\*\*/gu, "$1")
    .trim()
}

function buildLegacyBlocks(content: string): ConsultationBlock[] {
  const blocks: ConsultationBlock[] = []
  let paragraphLines: string[] = []
  let bulletItems: string[] = []

  const flushParagraph = () => {
    if (paragraphLines.length === 0) return
    blocks.push({ kind: "paragraph", text: paragraphLines.join(" ").trim() })
    paragraphLines = []
  }

  const flushBullets = () => {
    if (bulletItems.length === 0) return
    blocks.push({ kind: "bullet_list", items: [...bulletItems] })
    bulletItems = []
  }

  for (const rawLine of content.split("\n")) {
    const line = rawLine.trim()
    if (!line) { flushParagraph(); flushBullets(); continue }
    if (/^#{1,6}\s+/u.test(line)) {
      flushParagraph(); flushBullets()
      blocks.push({ kind: line.startsWith("##") ? "subtitle" : "title", text: cleanStructuredText(line) })
      continue
    }
    if (/^\s*[-*•]\s+/u.test(line)) {
      flushParagraph()
      bulletItems.push(cleanStructuredText(line))
      continue
    }
    if (/^\s*\d+[\).\s]+/u.test(line)) {
      flushParagraph(); flushBullets()
      blocks.push({ kind: "subtitle", text: cleanStructuredText(line) })
      continue
    }
    paragraphLines.push(cleanStructuredText(line))
  }
  flushParagraph(); flushBullets()
  return blocks
}

function getRenderableBlocks(section: ConsultationSection): ConsultationBlock[] {
  if (section.blocks && section.blocks.length > 0) return section.blocks
  return buildLegacyBlocks(section.content)
}

function renderSectionBlock(block: ConsultationBlock, index: number) {
  if (block.kind === "title" && block.text) return <h4 key={index}>{block.text}</h4>
  if (block.kind === "subtitle" && block.text) return <h5 key={index}>{block.text}</h5>
  if (block.kind === "bullet_list" && block.items && block.items.length > 0) {
    return (
      <ul key={index}>
        {block.items.map((item, i) => <li key={`${index}-${i}`}>{item}</li>)}
      </ul>
    )
  }
  if (block.text) return <p key={index}>{block.text}</p>
  return null
}

export function ConsultationResultPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [searchParams] = useSearchParams()
  const lang = detectLang()

  const { state, setResult, saveToHistory, reset } = useConsultation()
  const consultationGenerate = useConsultationGenerate()

  const [error, setError] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  const historyId = searchParams.get("id")
  const currentResult: ConsultationResult | undefined = historyId
    ? state.history.find((h) => h.id === historyId)
    : state.result ?? undefined

  const isAlreadyInHistory = historyId !== null && currentResult !== undefined
  const [isSaved, setIsSaved] = useState(isAlreadyInHistory)

  const astrologerId =
    currentResult?.astrologerId === AUTO_ASTROLOGER_ID ? undefined : currentResult?.astrologerId
  const { data: astrologer } = useAstrologer(astrologerId)
  const astrologerName =
    currentResult?.astrologerId === AUTO_ASTROLOGER_ID
      ? t("auto_astrologer", lang)
      : astrologer?.name ?? t("loading_name", lang)

  const draftType = state.draft.type
  const draftAstrologerId = state.draft.astrologerId ?? AUTO_ASTROLOGER_ID
  const draftContext = state.draft.context
  const draftObjective = state.draft.objective
  const draftTimeHorizon = state.draft.timeHorizon
  const draftOtherPerson = state.draft.otherPerson
  const generationStarted = useRef(false)

  const typeConfig = useMemo(
    () => (currentResult ? getConsultationTypeConfig(currentResult.type) : undefined),
    [currentResult]
  )

  const currentObjective = useMemo(
    () => currentResult ? resolveObjectiveText(currentResult.objective, currentResult.type, lang) : "",
    [currentResult, lang]
  )

  const resultPrecheck = useMemo<ConsultationPrecheckData | null>(() => {
    if (!currentResult?.fallbackMode && !currentResult?.precisionLevel) return null
    return {
      consultation_type: currentResult.type,
      status:
        currentResult.precisionLevel === "blocked"
          ? "blocked"
          : currentResult.fallbackMode
            ? "degraded"
            : "nominal",
      precision_level: (currentResult.precisionLevel as any) || "high",
      fallback_mode: currentResult.fallbackMode as any,
      safeguard_issue: null,
      user_profile_quality: "complete",
      missing_fields: [],
      available_modes: [],
      blocking_reasons: [],
    }
  }, [currentResult])

  const generateInterpretation = useCallback(async () => {
    if (draftType === null) { navigate("/consultations/new"); return }
    setError(null)
    setIsGenerating(true)
    try {
      const objective = resolveObjectiveText(draftObjective, draftType, lang)
      const timeHorizon = draftTimeHorizon?.trim() ? draftTimeHorizon.trim() : null
      const payload = {
        consultation_type: draftType,
        question: draftContext,
        objective,
        horizon: timeHorizon ?? undefined,
        astrologer_id: draftAstrologerId,
        save_third_party: state.draft.saveThirdParty,
        third_party_nickname: state.draft.thirdPartyNickname,
        third_party_external_id: state.draft.selectedThirdPartyExternalId ?? undefined,
        other_person: draftOtherPerson ? {
          birth_date: draftOtherPerson.birthDate,
          birth_time: draftOtherPerson.birthTime ?? undefined,
          birth_time_known: draftOtherPerson.birthTimeKnown,
          birth_place: draftOtherPerson.birthPlace,
          birth_city: draftOtherPerson.birthCity,
          birth_country: draftOtherPerson.birthCountry,
          ...(draftOtherPerson.placeResolvedId ? { place_resolved_id: draftOtherPerson.placeResolvedId } : {}),
          ...(draftOtherPerson.birthLat != null ? { birth_lat: draftOtherPerson.birthLat } : {}),
          ...(draftOtherPerson.birthLon != null ? { birth_lon: draftOtherPerson.birthLon } : {}),
        } : undefined,
      }
      const response = await consultationGenerate.mutateAsync(payload)
      const data = response.data
      trackEvent(EVENTS.CONSULTATION_GENERATED, { type: data.consultation_type, status: data.status, route: data.route_key })
      const result: ConsultationResult = {
        id: data.consultation_id,
        type: data.consultation_type as any,
        astrologerId: draftAstrologerId,
        context: draftContext,
        objective,
        timeHorizon,
        summary: data.summary,
        keyPoints: data.sections.find((s) => s.id === "key_points")?.content.split("\n") || [],
        actionableAdvice: data.sections.find((s) => s.id === "advice")?.content.split("\n") || [],
        createdAt: new Date().toISOString(),
        fallbackMode: data.fallback_mode,
        precisionLevel: data.precision_level,
        sections: data.sections,
        routeKey: data.route_key,
      }
      setResult(result)
      saveToHistory(result)
      setIsSaved(true)
      if (state.draft.saveThirdParty) {
        void queryClient.invalidateQueries({ queryKey: ["consultation-third-parties"] })
      }
    } catch (err: any) {
      setError(
        err?.code === "request_timeout" || err?.name === "AbortError"
          ? t("generation_timeout", lang)
          : err.message || t("error_generation", lang)
      )
      trackEvent(EVENTS.CONSULTATION_ERROR, { type: draftType, error: err.message || "unknown" })
    } finally {
      setIsGenerating(false)
    }
  }, [
    draftType, draftAstrologerId, draftContext, draftObjective, draftTimeHorizon, draftOtherPerson,
    state.draft.saveThirdParty, state.draft.thirdPartyNickname, state.draft.selectedThirdPartyExternalId,
    consultationGenerate, setResult, saveToHistory, queryClient, navigate, lang,
  ])

  useEffect(() => {
    if (!historyId && !state.result && draftType !== null && !generationStarted.current) {
      generationStarted.current = true
      void generateInterpretation()
    }
  }, [historyId, state.result, draftType, generateInterpretation])

  const handleSave = useCallback(() => {
    if (currentResult) { saveToHistory(currentResult); setIsSaved(true) }
  }, [currentResult, saveToHistory])

  const handleOpenInChat = useCallback(() => {
    if (!currentResult) return
    trackEvent(EVENTS.CONSULTATION_CHAT_OPENED, { type: currentResult.type, precision: currentResult.precisionLevel })
    const interpretation = currentResult.summary || ""
    const timeHorizonBlock = currentResult.timeHorizon ? `\n${t("time_horizon_summary_label", lang)}: ${currentResult.timeHorizon}` : ""
    const message =
      `[Consultation ${t(typeConfig?.labelKey ?? "", lang)}]\n\n` +
      `${t("objective_summary_label", lang)}: ${resolveObjectiveText(currentResult.objective, currentResult.type, lang)}${timeHorizonBlock}\n\n` +
      `${currentResult.context}\n\n${t("interpretation_label", lang)}:\n${interpretation}`
    sessionStorage.setItem(CHAT_PREFILL_KEY, message)
    reset()
    const astrologerParam = currentResult.astrologerId !== AUTO_ASTROLOGER_ID
      ? `?astrologerId=${currentResult.astrologerId}` : ""
    navigate(`/chat${astrologerParam}`)
  }, [currentResult, typeConfig, reset, navigate, lang])

  // — Loading state —
  if (isGenerating && !currentResult && !error) {
    return (
      <PageLayout className="is-consultation-result-page">
        <div className="result-bg-halo" />
        <div className="result-noise" />
        <div className="result-container">
          <div className="result-state-wrap">
            <span className="loading-spinner" />
            <p>{t("generating", lang)}</p>
          </div>
        </div>
      </PageLayout>
    )
  }

  // — Error state —
  if (error) {
    return (
      <PageLayout className="is-consultation-result-page">
        <div className="result-bg-halo" />
        <div className="result-noise" />
        <div className="result-container">
          <div className="result-state-wrap" role="alert">
            <p>{error}</p>
            <Link to="/consultations/new" className="btn btn-primary">
              {t("back_to_consultations", lang)}
            </Link>
          </div>
        </div>
      </PageLayout>
    )
  }

  // — Empty state —
  if (!currentResult) {
    return (
      <PageLayout className="is-consultation-result-page">
        <div className="result-bg-halo" />
        <div className="result-noise" />
        <div className="result-container">
          <div className="result-state-wrap">
            <p>{t("no_history", lang)}</p>
            <Link to="/consultations" className="btn btn-primary">
              {t("back_to_consultations", lang)}
            </Link>
          </div>
        </div>
      </PageLayout>
    )
  }

  // Sections à afficher : on exclut consultation_basis
  const visibleSections = currentResult.sections?.filter((s) => s.id !== "consultation_basis") ?? []

  return (
    <PageLayout className="is-consultation-result-page">
      <div className="result-bg-halo" />
      <div className="result-noise" />

      <div className="result-container">
        {/* Navigation */}
        <nav className="result-nav">
          <Link to="/consultations" className="result-back-btn">
            <ChevronLeft size={18} />
            <span>{t("back_to_consultations", lang)}</span>
          </Link>
        </nav>

        {/* Hero */}
        <section className="result-hero">
          <div className="result-hero__icon-wrap">
            <div className="result-hero__icon-glow" />
            <span className="result-hero__icon" aria-hidden="true">
              {typeConfig?.icon}
            </span>
          </div>
          <div className="result-hero__content">
            <span className="result-type-label">
              {t(typeConfig?.labelKey ?? "", lang)}
            </span>
            <h1 className="result-hero__title">{currentObjective}</h1>
            <div className="result-astrologer-pill">
              <span aria-hidden="true">✨</span>
              <span>{astrologerName}</span>
            </div>
          </div>
        </section>

        {/* Banner dégradé/bloqué uniquement */}
        {resultPrecheck && resultPrecheck.status !== "nominal" && (
          <ConsultationFallbackBanner precheck={resultPrecheck} />
        )}

        {/* Résumé du contexte */}
        <div className="result-context-card">
          <div className="result-context-card__row">
            <span className="result-context-card__label">{t("enter_context", lang)}</span>
            <p className="result-context-card__value">{currentResult.context}</p>
          </div>
          {currentResult.timeHorizon && (
            <div className="result-context-card__row">
              <span className="result-context-card__label">{t("time_horizon_label", lang)}</span>
              <p className="result-context-card__value">{currentResult.timeHorizon}</p>
            </div>
          )}
        </div>

        {/* Contenu de la consultation */}
        <section className="result-guidance">
          {currentResult.summary && (
            <div className="result-section-card">
              <h2 className="result-section-title">{t("summary_label", lang)}</h2>
              <p className="result-summary-text">{currentResult.summary}</p>
            </div>
          )}

          {visibleSections.length > 0 ? (
            visibleSections.map((section) => (
              <div key={section.id} className="result-section-card">
                <h3 className="result-section-title result-section-title--sub">{section.title}</h3>
                <div className="result-section-content">
                  {getRenderableBlocks(section).map((block, index) =>
                    renderSectionBlock(block, index)
                  )}
                </div>
              </div>
            ))
          ) : (
            <>
              {currentResult.keyPoints && currentResult.keyPoints.length > 0 && (
                <div className="result-section-card">
                  <h3 className="result-section-title result-section-title--sub">
                    {t("key_points_label", lang)}
                  </h3>
                  <div className="result-section-content">
                    <ul>
                      {currentResult.keyPoints.map((point, idx) => (
                        <li key={idx}>{point}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
              {currentResult.actionableAdvice && currentResult.actionableAdvice.length > 0 && (
                <div className="result-section-card">
                  <h3 className="result-section-title result-section-title--sub">
                    {t("actionable_advice_label", lang)}
                  </h3>
                  <div className="result-section-content">
                    <ul>
                      {currentResult.actionableAdvice.map((advice, idx) => (
                        <li key={idx}>{advice}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </>
          )}

          {currentResult.disclaimer && (
            <p className="result-disclaimer">
              <em>{currentResult.disclaimer}</em>
            </p>
          )}
        </section>

        {/* Actions */}
        <div className="result-actions">
          <button
            type="button"
            className="btn btn-primary result-chat-btn"
            onClick={handleOpenInChat}
          >
            <MessageSquare size={18} />
            {t("open_in_chat", lang)}
          </button>
          <div className="result-actions__secondary">
            <button
              type="button"
              className={classNames("btn", "btn-secondary", isSaved && "btn-success")}
              onClick={handleSave}
              disabled={isSaved}
            >
              {isSaved ? t("saved", lang) : t("save", lang)}
            </button>
            <Link to="/consultations" className="btn btn-secondary">
              {t("back_to_consultations", lang)}
            </Link>
          </div>
        </div>
      </div>
    </PageLayout>
  )
}
