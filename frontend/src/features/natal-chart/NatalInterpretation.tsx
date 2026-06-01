// Container React orchestrant les donnees d'interpretation de theme natal.
import { useEffect, useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { RefreshCw } from "lucide-react"

import type { FeatureEntitlementResponse } from "../../api/billing"
import { ApiError } from "../../api/client"
import {
  deleteNatalInterpretation,
  requestThemeNatalReadingAction,
  useNatalInterpretation,
  useNatalInterpretationById,
  useNatalInterpretationsList,
  useNatalPdfTemplates,
  type NatalInterpretationListItem,
  type ThemeNatalReadingAction,
  type ThemeNatalReadingSlotState,
} from "../../api/natalChart"
import { natalChartTranslations } from "../../i18n/natalChart"
import { type AstrologyLang } from "../../i18n/astrology"
import { ErrorBoundary } from "@components/ErrorBoundary"
import { useAccessTokenSnapshot } from "../../utils/authToken"
import { InterpretationContent } from "../../components/natal-interpretation/NatalInterpretationContent"
import {
  ConfirmDeleteModal,
  InterpretationError,
  InterpretationSkeleton,
  PdfActionsMenu,
  VersionSelector,
} from "../../components/natal-interpretation/NatalInterpretationMenus"
import { NatalNarrativeReading } from "./NatalNarrativeReading"
import { NatalReadingSources } from "./NatalReadingSources"
import { PersonaSelector } from "./NatalInterpretationPersonaSelector"
import "./NatalInterpretation.css"

interface Props {
  chartLoaded: boolean
  chartId?: string
  lang: AstrologyLang
  initialPersonaId?: string | null
  initialInterpretationId?: number | null
  isLockedFree?: boolean
  onActiveInterpretationChange?: (payload: {
    level: "short" | "complete"
    personaName: string | null
    canSwitchPersona: boolean
    isBasicCompleteLimitReached: boolean
  }) => void
  actionRequest?: {
    kind: "upgrade" | "switch_persona"
    nonce: number
  } | null
  longFeatureAccess?: FeatureEntitlementResponse
}

function isRealCompleteInterpretation(item: NatalInterpretationListItem): boolean {
  return item.level === "complete" && (Boolean(item.persona_id) || Boolean(item.prompt_version_id))
}

function findLatestCompleteInterpretation(
  items: NatalInterpretationListItem[],
): NatalInterpretationListItem | null {
  return items.find(isRealCompleteInterpretation) ?? null
}

function findLatestShortInterpretation(
  items: NatalInterpretationListItem[],
): NatalInterpretationListItem | null {
  return items.find((item) => item.level === "short") ?? null
}

function findPreferredFreeInterpretation(
  items: NatalInterpretationListItem[],
): NatalInterpretationListItem | null {
  return findLatestShortInterpretation(items)
}

function localeFromLang(lang: AstrologyLang): "fr-FR" | "en-US" | "es-ES" | "de-DE" {
  if (lang === "en") return "en-US"
  if (lang === "es") return "es-ES"
  if (lang === "de") return "de-DE"
  return "fr-FR"
}

function pdfLocaleFromLang(lang: AstrologyLang): "fr" | "en" | "es" {
  if (lang === "fr" || lang === "en" || lang === "es") return lang
  return "en"
}

function createClientRequestId(chartId: string, action: ThemeNatalReadingAction): string {
  return `${chartId}:${action}:${Date.now()}`
}

function isBlockingSlotState(state: ThemeNatalReadingSlotState | null): boolean {
  return state === "failed_retriable" || state === "locked" || state === "paywall" || state === "rejected"
}

function maxRemainingCompleteReadings(access: FeatureEntitlementResponse | undefined): number | null {
  const remainingValues = access?.usage_states?.map((state) => state.remaining) ?? []
  if (remainingValues.length === 0) return null
  return Math.max(...remainingValues)
}

function hasSingleCompleteReadingAccess(access: FeatureEntitlementResponse | undefined): boolean {
  if (!access?.granted) return false
  const remaining = maxRemainingCompleteReadings(access)
  return access.access_mode === "quota" && (remaining === null || remaining <= 1)
}

function hasMultiCompleteReadingAccess(access: FeatureEntitlementResponse | undefined): boolean {
  if (!access?.granted) return false
  const remaining = maxRemainingCompleteReadings(access)
  return access.access_mode === "quota" && remaining !== null && remaining > 1
}

export function NatalInterpretationSection({
  chartLoaded,
  chartId,
  lang,
  initialPersonaId = null,
  initialInterpretationId = null,
  isLockedFree = false,
  onActiveInterpretationChange,
  actionRequest,
  longFeatureAccess,
}: Props) {
  const pageT = natalChartTranslations[lang]
  const t = pageT.interpretation
  const accessToken = useAccessTokenSnapshot()
  const navigate = useNavigate()
  const basicUpgradePath = "/settings/subscription"
  const premiumUpgradePath = "/settings/subscription"

  const [readingAction, setReadingAction] = useState<ThemeNatalReadingAction>(
    initialPersonaId ? "generate_full" : "preview",
  )
  const [nextFullAction, setNextFullAction] = useState<ThemeNatalReadingAction>("generate_full")
  const [selectedPersonaId, setSelectedPersonaId] = useState<string | null>(initialPersonaId)
  const [isUpsellOpen, setIsUpsellOpen] = useState(false)
  const [actionNonce, setActionNonce] = useState(0)
  const [selectedInterpretationId, setSelectedInterpretationId] = useState<number | null>(initialInterpretationId)
  const [selectedTemplateKey, setSelectedTemplateKey] = useState("")
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const [showBasicLimitNotice, setShowBasicLimitNotice] = useState(false)

  const historyQuery = useNatalInterpretationsList({
    enabled: chartLoaded && !!chartId,
    chartId,
  })
  const historyItems = historyQuery.data?.items ?? []
  const latestCompleteInterpretation = findLatestCompleteInterpretation(historyItems)
  const latestShortInterpretation = findLatestShortInterpretation(historyItems)
  const preferredFreeInterpretation = findPreferredFreeInterpretation(historyItems)
  const isQuotaUsageExhausted = Boolean(
    longFeatureAccess?.reason_code === "quota_exhausted" ||
      longFeatureAccess?.usage_states?.some((state) => state.exhausted || state.remaining <= 0),
  )
  const isSingleAstrologerPlan = hasSingleCompleteReadingAccess(longFeatureAccess)
  const isPremiumPlan = hasMultiCompleteReadingAccess(longFeatureAccess)
  const shouldPreferLatestCompleteByDefault = isSingleAstrologerPlan || isPremiumPlan
  const hasPersistedShortInterpretation = latestShortInterpretation !== null
  const shouldResolveInterpretationFromHistory =
    shouldPreferLatestCompleteByDefault || isSingleAstrologerPlan
  const hasPersistedInterpretationCandidate =
    (shouldPreferLatestCompleteByDefault && latestCompleteInterpretation !== null) ||
    (isLockedFree && preferredFreeInterpretation !== null) ||
    (isSingleAstrologerPlan &&
      hasPersistedShortInterpretation)
  const isResolvingPersistedInterpretation =
    !selectedInterpretationId &&
    shouldResolveInterpretationFromHistory &&
    (historyQuery.isLoading || historyQuery.isFetching)
  const isBasicCompleteLimitReached =
    isSingleAstrologerPlan && latestCompleteInterpretation !== null
  const isExplicitProductActionRequest =
    readingAction !== "preview" &&
    !selectedInterpretationId &&
    !isBasicCompleteLimitReached &&
    Boolean(selectedPersonaId)
  const clientRequestId = chartId ? `${chartId}:${readingAction}:${actionNonce}` : undefined
  const pdfTemplatesQuery = useNatalPdfTemplates({
    enabled: chartLoaded,
    locale: pdfLocaleFromLang(lang),
  })
  const mainQuery = useNatalInterpretation({
    enabled:
      chartLoaded &&
      !selectedInterpretationId &&
      !isResolvingPersistedInterpretation &&
      (!hasPersistedInterpretationCandidate || isExplicitProductActionRequest),
    chartId,
    action: readingAction,
    personaProfileId: selectedPersonaId,
    locale: localeFromLang(lang),
    clientRequestId,
  })
  const idQuery = useNatalInterpretationById({
    enabled: !!selectedInterpretationId,
    interpretationId: selectedInterpretationId ?? undefined,
    locale: localeFromLang(lang),
  })

  const activeQuery = selectedInterpretationId ? idQuery : mainQuery
  const { data, isLoading, error, refetch } = activeQuery
  const hasCompleteInterpretation = latestCompleteInterpretation !== null
  const canSwitchPersona = isPremiumPlan && hasCompleteInterpretation
  const isCompleteGenerationBlocked = !isLockedFree && isQuotaUsageExhausted
  const shouldShowBasicLimitNotice =
    showBasicLimitNotice ||
    (
      error instanceof ApiError &&
      (error.code === "natal_chart_long_quota_exceeded" || error.status === 429)
    )
  const primaryActionLabel = hasCompleteInterpretation
    ? isLockedFree
      ? t.upgradeToBasicCta
      : isBasicCompleteLimitReached || isCompleteGenerationBlocked
        ? t.quotaExhaustedCta
        : canSwitchPersona
          ? pageT.requestAnotherAstrologer
          : pageT.unlockCompleteInterpretation
    : isLockedFree
      ? t.upgradeToBasicCta
      : pageT.unlockCompleteInterpretation

  const revealBasicCompleteLimitNotice = () => {
    setShowBasicLimitNotice(true)
    setIsUpsellOpen(false)
  }

  useEffect(() => {
    onActiveInterpretationChange?.({
      level: isLockedFree ? "short" : (data?.meta.level ?? "short"),
      personaName: data?.meta.persona_name ?? null,
      canSwitchPersona,
      isBasicCompleteLimitReached,
    })
  }, [
    canSwitchPersona,
    data?.meta.level,
    data?.meta.persona_name,
    isBasicCompleteLimitReached,
    isLockedFree,
    onActiveInterpretationChange,
  ])

  useEffect(() => {
    if (!actionRequest) return
    if (actionRequest.kind === "upgrade" && isLockedFree) {
      navigate(basicUpgradePath)
      return
    }
    if (
      actionRequest.kind === "upgrade" &&
      (isBasicCompleteLimitReached || isCompleteGenerationBlocked)
    ) {
      if (isBasicCompleteLimitReached || isSingleAstrologerPlan) {
        revealBasicCompleteLimitNotice()
        return
      }
      navigate(premiumUpgradePath)
      return
    }
    if (actionRequest.kind === "switch_persona" && isCompleteGenerationBlocked) {
      navigate(premiumUpgradePath)
      return
    }
    setSelectedInterpretationId(null)
    setSelectedPersonaId(null)
    setNextFullAction(actionRequest.kind === "switch_persona" ? "regenerate" : "generate_full")
    setIsUpsellOpen(true)
  }, [
    actionRequest,
    basicUpgradePath,
    isBasicCompleteLimitReached,
    isCompleteGenerationBlocked,
    isLockedFree,
    isSingleAstrologerPlan,
    navigate,
    premiumUpgradePath,
  ])

  useEffect(() => {
    if (typeof initialInterpretationId === "number" && Number.isFinite(initialInterpretationId)) {
      setSelectedInterpretationId(initialInterpretationId)
      setSelectedPersonaId(null)
      setReadingAction("generate_full")
      return
    }
    if (initialPersonaId) {
      setSelectedInterpretationId(null)
      setSelectedPersonaId(initialPersonaId)
      setReadingAction("generate_full")
      return
    }
    if (isLockedFree) {
      setSelectedInterpretationId(null)
      setSelectedPersonaId(null)
      setReadingAction("preview")
    }
  }, [initialInterpretationId, initialPersonaId, isLockedFree, preferredFreeInterpretation?.level])

  useEffect(() => {
    if (typeof initialInterpretationId === "number" && Number.isFinite(initialInterpretationId)) return
    if (initialPersonaId) return
    if (historyItems.length === 0) return

    if (shouldPreferLatestCompleteByDefault && latestCompleteInterpretation) {
      setSelectedInterpretationId((current) =>
        current === latestCompleteInterpretation.id ? current : latestCompleteInterpretation.id,
      )
      setSelectedPersonaId(null)
      return
    }

    if (isLockedFree && preferredFreeInterpretation) {
      setSelectedInterpretationId((current) =>
        current === preferredFreeInterpretation.id ? current : preferredFreeInterpretation.id,
      )
      setSelectedPersonaId(null)
      return
    }

    if (isSingleAstrologerPlan) {
      if (readingAction !== "preview" && selectedPersonaId) {
        return
      }
      if (latestShortInterpretation) {
        setSelectedInterpretationId((current) =>
          current === latestShortInterpretation.id ? current : latestShortInterpretation.id,
        )
      } else {
        setSelectedInterpretationId(null)
      }
      setSelectedPersonaId(null)
      setReadingAction("preview")
    }
  }, [
    historyItems,
    initialInterpretationId,
    initialPersonaId,
    isLockedFree,
    isSingleAstrologerPlan,
    latestCompleteInterpretation,
    latestShortInterpretation,
    preferredFreeInterpretation,
    readingAction,
    selectedPersonaId,
    shouldPreferLatestCompleteByDefault,
  ])

  useEffect(() => {
    if (selectedTemplateKey) return
    const defaultTemplate = pdfTemplatesQuery.data?.items.find((item) => item.is_default)
    if (defaultTemplate) {
      setSelectedTemplateKey(defaultTemplate.key)
    }
  }, [pdfTemplatesQuery.data, selectedTemplateKey])

  useEffect(() => {
    if (selectedInterpretationId) return
    const persistedAt = data?.meta.persisted_at
    const interpretationId = data?.meta.id
    if (!persistedAt && !interpretationId) return

    const isPresentInHistory = historyItems.some(
      (item) => item.id === interpretationId || item.created_at === persistedAt,
    )
    if (!isPresentInHistory) {
      void historyQuery.refetch()
    }
  }, [
    data?.meta.id,
    data?.meta.persisted_at,
    historyItems,
    historyQuery,
    selectedInterpretationId,
  ])

  const handleUpgrade = (personaId: string) => {
    if (isBasicCompleteLimitReached) {
      revealBasicCompleteLimitNotice()
      return
    }
    setSelectedPersonaId(personaId)
    setReadingAction(nextFullAction)
    setIsUpsellOpen(false)
    setSelectedInterpretationId(null)
    setActionNonce((previous) => previous + 1)
  }

  const handleRegenerate = () => {
    if (isLockedFree) {
      navigate(basicUpgradePath)
      return
    }
    if (isBasicCompleteLimitReached) {
      revealBasicCompleteLimitNotice()
      return
    }
    if (isCompleteGenerationBlocked) {
      if (isSingleAstrologerPlan) {
        revealBasicCompleteLimitNotice()
        return
      }
      navigate(premiumUpgradePath)
      return
    }
    setSelectedInterpretationId(null)
    setSelectedPersonaId(null)
    setNextFullAction(hasCompleteInterpretation ? "regenerate" : "generate_full")
    setIsUpsellOpen(true)
  }

  const handleSelectVersion = (id: number | null) => {
    setSelectedInterpretationId(id)
    if (id === null) {
      setSelectedPersonaId(null)
      setReadingAction("preview")
      return
    }
    const selectedItem = historyItems.find((item) => item.id === id)
    if (selectedItem) {
      setSelectedPersonaId(null)
      setReadingAction("preview")
    }
  }

  const handleDelete = async (id: number) => {
    if (!accessToken) return
    setIsDeleting(true)
    try {
      await deleteNatalInterpretation(accessToken, id)
      const updatedHistory = await historyQuery.refetch()
      if (selectedInterpretationId === id) {
        const remaining = updatedHistory.data?.items ?? []
        if (remaining.length > 0) {
          setSelectedInterpretationId(remaining[0].id)
        } else {
          setSelectedInterpretationId(null)
          setReadingAction("preview")
        }
      }
      setShowDeleteConfirm(null)
    } catch (err) {
      console.error("Failed to delete interpretation", err)
    } finally {
      setIsDeleting(false)
    }
  }

  const usedPersonaIds = new Set(
    historyItems
      .filter((item) => isRealCompleteInterpretation(item) && Boolean(item.persona_id))
      .map((item) => item.persona_id as string),
  )

  const handlePreviewPdf = async () => {
    if (!accessToken || !chartId) return
    try {
      await requestThemeNatalReadingAction(accessToken, {
        chart_id: chartId,
        action: "preview",
        persona_profile_id: selectedPersonaId,
        locale: localeFromLang(lang),
        client_request_id: createClientRequestId(chartId, "preview"),
      })
    } catch (err) {
      console.error("Failed to preview PDF", err)
    }
  }

  const handleDownloadPdf = async () => {
    if (!accessToken || !chartId) return
    try {
      await requestThemeNatalReadingAction(accessToken, {
        chart_id: chartId,
        action: "download",
        persona_profile_id: selectedPersonaId,
        locale: localeFromLang(lang),
        client_request_id: createClientRequestId(chartId, "download"),
      })
    } catch (err) {
      console.error("Failed to download PDF", err)
    }
  }

  const productActionState = selectedInterpretationId ? null : mainQuery.state

  if (!chartLoaded) return null

  return (
    <section className="ni-section">
      <div className="ni-header">
        <div className="ni-header__title">
          <h2 className="ni-title">{t.title}</h2>
          {data?.meta.persisted_at && (
            <span className="ni-date">
              {t.generatedOnLabel}{" "}
              {new Date(data.meta.persisted_at).toLocaleDateString(lang, {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              })}
            </span>
          )}
        </div>

        <div className="ni-actions ni-actions--compact">
          {data && !isLoading && (
            <button
              type="button"
              onClick={handleRegenerate}
              title={primaryActionLabel}
              className="ni-action-btn ni-action-btn--regenerate ni-action-btn--primary"
            >
              <RefreshCw size={16} />
              <span className="ni-action-btn__label">{primaryActionLabel}</span>
            </button>
          )}

          {historyItems.length > 1 && (
            <div className="ni-actions__group">
              <span className="ni-actions__group-label">{t.historyGroupLabel}</span>
              <div className="ni-actions__group-content">
                <VersionSelector
                  items={historyItems}
                  selectedId={
                    selectedInterpretationId ||
                    (historyItems.find((item) => item.created_at === data?.meta.persisted_at)?.id ?? null)
                  }
                  onSelect={handleSelectVersion}
                  onDeleteRequest={(id) => setShowDeleteConfirm(id)}
                  t={t}
                  lang={lang}
                />
              </div>
            </div>
          )}

          {data && !isLoading && (
            <div className="ni-actions__group ni-actions__group--pdf">
              <span className="ni-actions__group-label">{t.pdfGroupLabel}</span>
              <div className="ni-actions__group-content">
                <label className="ni-control-trigger ni-template-label">
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

                <PdfActionsMenu t={t} onPreview={handlePreviewPdf} onDownload={handleDownloadPdf} />
              </div>
            </div>
          )}

          {data?.meta.level === "complete" && (
            <span className="ni-level-badge">{isLockedFree ? t.summaryBadge : t.completeBadge}</span>
          )}
        </div>
      </div>

      <ErrorBoundary onReset={() => refetch()}>
        {shouldShowBasicLimitNotice ? (
          <div className="ni-quota-notice" role="note">
            <p className="ni-quota-notice__message">{t.basicCompleteLimitMessage}</p>
            <Link to={premiumUpgradePath} className="btn-link ni-quota-notice__cta">
              {t.quotaExhaustedCta}
            </Link>
          </div>
        ) : null}
        {isLoading || productActionState === "generating" || isResolvingPersistedInterpretation ? (
          <InterpretationSkeleton t={t} isComplete={readingAction !== "preview"} />
        ) : error && !shouldShowBasicLimitNotice ? (
          <InterpretationError t={t} onRetry={() => refetch()} />
        ) : isBlockingSlotState(productActionState) ? (
          <InterpretationError t={t} onRetry={() => refetch()} />
        ) : data ? (
          <>
            <InterpretationContent
              data={data}
              lang={lang}
              renderNarrativeReading={(reading, readingLang) => (
                <NatalNarrativeReading reading={reading} lang={readingLang} />
              )}
              renderReadingSources={(elements, sourcesLang) => (
                <NatalReadingSources elements={elements} lang={sourcesLang} />
              )}
            />
            {isUpsellOpen && (
              <PersonaSelector
                t={t}
                onConfirm={handleUpgrade}
                onCancel={() => setIsUpsellOpen(false)}
                isSubmitting={isLoading && readingAction !== "preview"}
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
  )
}
