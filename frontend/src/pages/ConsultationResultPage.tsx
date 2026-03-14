import { useEffect, useState, useCallback, useRef, useMemo } from "react"
import { useNavigate, useSearchParams, Link } from "react-router-dom"

import { useConsultation, CHAT_PREFILL_KEY } from "../state/consultationStore"
import { useConsultationGenerate, type ConsultationPrecheckData } from "../api/consultations"
import { useAstrologer } from "../api/astrologers"
import { detectLang } from "../i18n/astrology"
import { t } from "../i18n/consultations"
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
    blocks.push({
      kind: "paragraph",
      text: paragraphLines.join(" ").trim(),
    })
    paragraphLines = []
  }

  const flushBullets = () => {
    if (bulletItems.length === 0) return
    blocks.push({
      kind: "bullet_list",
      items: [...bulletItems],
    })
    bulletItems = []
  }

  for (const rawLine of content.split("\n")) {
    const line = rawLine.trim()
    if (!line) {
      flushParagraph()
      flushBullets()
      continue
    }

    if (/^#{1,6}\s+/u.test(line)) {
      flushParagraph()
      flushBullets()
      blocks.push({
        kind: line.startsWith("##") ? "subtitle" : "title",
        text: cleanStructuredText(line),
      })
      continue
    }

    if (/^\s*[-*•]\s+/u.test(line)) {
      flushParagraph()
      bulletItems.push(cleanStructuredText(line))
      continue
    }

    if (/^\s*\d+[\).\s]+/u.test(line)) {
      flushParagraph()
      flushBullets()
      blocks.push({
        kind: "subtitle",
        text: cleanStructuredText(line),
      })
      continue
    }

    paragraphLines.push(cleanStructuredText(line))
  }

  flushParagraph()
  flushBullets()
  return blocks
}

function getRenderableBlocks(section: ConsultationSection): ConsultationBlock[] {
  if (section.blocks && section.blocks.length > 0) {
    return section.blocks
  }
  return buildLegacyBlocks(section.content)
}

function renderSectionBlock(block: ConsultationBlock, index: number) {
  if (block.kind === "title" && block.text) {
    return <h4 key={index}>{block.text}</h4>
  }
  if (block.kind === "subtitle" && block.text) {
    return <h5 key={index}>{block.text}</h5>
  }
  if (block.kind === "bullet_list" && block.items && block.items.length > 0) {
    return (
      <ul key={index}>
        {block.items.map((item, itemIndex) => (
          <li key={`${index}-${itemIndex}`}>{item}</li>
        ))}
      </ul>
    )
  }
  if (block.text) {
    return <p key={index}>{block.text}</p>
  }
  return null
}

export function ConsultationResultPage() {
  const navigate = useNavigate()
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
    currentResult?.astrologerId === AUTO_ASTROLOGER_ID
      ? undefined
      : currentResult?.astrologerId
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
    () =>
      currentResult
        ? resolveObjectiveText(currentResult.objective, currentResult.type, lang)
        : "",
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
      blocking_reasons: []
    }
  }, [currentResult])

  const generateInterpretation = useCallback(async () => {
    if (draftType === null) {
      navigate("/consultations/new")
      return
    }

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
        other_person: draftOtherPerson ? {
          birth_date: draftOtherPerson.birthDate,
          birth_time: draftOtherPerson.birthTime ?? undefined,
          birth_time_known: draftOtherPerson.birthTimeKnown,
          birth_place: draftOtherPerson.birthPlace,
          birth_city: draftOtherPerson.birthCity,
          birth_country: draftOtherPerson.birthCountry,
          ...(draftOtherPerson.placeResolvedId
            ? { place_resolved_id: draftOtherPerson.placeResolvedId }
            : {}),
          ...(draftOtherPerson.birthLat !== null && draftOtherPerson.birthLat !== undefined
            ? { birth_lat: draftOtherPerson.birthLat }
            : {}),
          ...(draftOtherPerson.birthLon !== null && draftOtherPerson.birthLon !== undefined
            ? { birth_lon: draftOtherPerson.birthLon }
            : {}),
        } : undefined
      }

      const response = await consultationGenerate.mutateAsync(payload)
      const data = response.data

      trackEvent(EVENTS.CONSULTATION_GENERATED, { 
        type: data.consultation_type,
        status: data.status,
        route: data.route_key
      })

      const result: ConsultationResult = {
        id: data.consultation_id,
        type: data.consultation_type as any,
        astrologerId: draftAstrologerId,
        context: draftContext,
        objective,
        timeHorizon,
        summary: data.summary,
        keyPoints: data.sections.find(s => s.id === "key_points")?.content.split("\n") || [],
        actionableAdvice: data.sections.find(s => s.id === "advice")?.content.split("\n") || [],
        createdAt: new Date().toISOString(),
        fallbackMode: data.fallback_mode,
        precisionLevel: data.precision_level,
        sections: data.sections,
        routeKey: data.route_key
      }

      setResult(result)
      saveToHistory(result)
      setIsSaved(true)
    } catch (err: any) {
      setError(
        err?.code === "request_timeout" || err?.name === "AbortError"
          ? t("generation_timeout", lang)
          : err.message || t("error_generation", lang)
      )
      trackEvent(EVENTS.CONSULTATION_ERROR, { 
        type: draftType,
        error: err.message || "unknown"
      })
    } finally {
      setIsGenerating(false)
    }
  }, [
    draftType,
    draftAstrologerId,
    draftContext,
    draftObjective,
    draftTimeHorizon,
    draftOtherPerson,
    state.draft.saveThirdParty,
    state.draft.thirdPartyNickname,
    consultationGenerate,
    setResult,
    saveToHistory,
    navigate,
    lang,
  ])

  useEffect(() => {
    if (!historyId && !state.result && draftType !== null && !generationStarted.current) {
      generationStarted.current = true
      void generateInterpretation()
    }
  }, [historyId, state.result, draftType, generateInterpretation])

  const handleSave = useCallback(() => {
    if (currentResult) {
      saveToHistory(currentResult)
      setIsSaved(true)
    }
  }, [currentResult, saveToHistory])

  const handleOpenInChat = useCallback(() => {
    if (currentResult) {
      trackEvent(EVENTS.CONSULTATION_CHAT_OPENED, { 
        type: currentResult.type,
        precision: currentResult.precisionLevel 
      })
      const interpretation = currentResult.summary || ""
      const timeHorizonBlock = currentResult.timeHorizon
        ? `\n${t("time_horizon_summary_label", lang)}: ${currentResult.timeHorizon}`
        : ""
      const message =
        `[Consultation ${t(typeConfig?.labelKey ?? "", lang)}]\n\n` +
        `${t("objective_summary_label", lang)}: ${resolveObjectiveText(currentResult.objective, currentResult.type, lang)}${timeHorizonBlock}\n\n` +
        `${currentResult.context}\n\n${t("interpretation_label", lang)}:\n${interpretation}`
      sessionStorage.setItem(CHAT_PREFILL_KEY, message)
      reset()
      const astrologerParam = currentResult.astrologerId !== AUTO_ASTROLOGER_ID
        ? `?astrologerId=${currentResult.astrologerId}`
        : ""
      navigate(`/chat${astrologerParam}`)
    }
  }, [currentResult, typeConfig, reset, navigate, lang])

  if (isGenerating && !currentResult && !error) {
    return (
      <div className="panel consultation-result-page">
        <div className="consultation-result-loading" aria-live="polite" aria-busy="true">
          <span className="loading-spinner" />
          <p>{t("generating", lang)}</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="panel consultation-result-page">
        <div className="consultation-result-error" role="alert">
          <p>{error}</p>
          <Link to="/consultations/new" className="btn">
            {t("back_to_consultations", lang)}
          </Link>
        </div>
      </div>
    )
  }

  if (!currentResult) {
    return (
      <div className="panel consultation-result-page">
        <div className="consultation-result-empty" aria-live="polite">
          <p>{t("no_history", lang)}</p>
          <Link to="/consultations" className="btn">
            {t("back_to_consultations", lang)}
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="panel consultation-result-page">
      <header className="consultation-result-header">
        <h1>{t("result_title", lang)}</h1>
      </header>

      {resultPrecheck && (
        <ConsultationFallbackBanner precheck={resultPrecheck} />
      )}

      <div className="consultation-result-summary-section">
        <div className="consultation-result-type">
          <span className="consultation-result-type-icon" aria-hidden="true">
            {typeConfig?.icon}
          </span>
          <span className="consultation-result-type-label">
            {t(typeConfig?.labelKey ?? "", lang)}
          </span>
        </div>

        <div className="consultation-result-meta">
          <span className="consultation-result-astrologer">
            {t("step_astrologer", lang)}: {astrologerName}
          </span>
        </div>

        <div className="consultation-result-context">
          <strong>{t("objective_label", lang)}:</strong>
          <p>{currentObjective}</p>
        </div>

        {currentResult.timeHorizon && (
          <div className="consultation-result-context">
            <strong>{t("time_horizon_label", lang)}:</strong>
            <p>{currentResult.timeHorizon}</p>
          </div>
        )}

        <div className="consultation-result-context">
          <strong>{t("enter_context", lang)}:</strong>
          <p>{currentResult.context}</p>
        </div>
      </div>

      <section className="consultation-result-guidance">
        <div className="consultation-result-interpretation">
          <h2>{t("summary_label", lang)}</h2>
          <p className="consultation-result-interpretation-text">
            {currentResult.summary}
          </p>
        </div>

        {currentResult.sections && currentResult.sections.length > 0 ? (
          currentResult.sections.map((section) => (
            <div key={section.id} className={`consultation-result-section consultation-result-section--${section.id}`}>
              <h3>{section.title}</h3>
              <div className="section-content">
                {getRenderableBlocks(section).map((block, index) =>
                  renderSectionBlock(block, index)
                )}
              </div>
            </div>
          ))
        ) : (
          <>
            {currentResult.keyPoints && currentResult.keyPoints.length > 0 && (
              <div className="consultation-result-key-points">
                <h3>{t("key_points_label", lang)}</h3>
                <ul>
                  {currentResult.keyPoints.map((point, idx) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
              </div>
            )}

            {currentResult.actionableAdvice && currentResult.actionableAdvice.length > 0 && (
              <div className="consultation-result-advice">
                <h3>{t("actionable_advice_label", lang)}</h3>
                <ul>
                  {currentResult.actionableAdvice.map((advice, idx) => (
                    <li key={idx}>{advice}</li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}

        {currentResult.disclaimer && (
          <p className="consultation-result-disclaimer">
            <em>{currentResult.disclaimer}</em>
          </p>
        )}
      </section>

      <div className="consultation-result-actions">
        <button
          type="button"
          className="btn btn-primary"
          onClick={handleOpenInChat}
        >
          {t("open_in_chat", lang)}
        </button>
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
  )
}
