// Container React orchestrant les donnees d'interpretation de theme natal.
import { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { RefreshCw } from "lucide-react"

import type { FeatureEntitlementResponse } from "../../api/billing"
import {
  deleteNatalInterpretation,
  downloadNatalInterpretationPdf,
  previewNatalInterpretationPdf,
  useNatalInterpretation,
  useNatalInterpretationById,
  useNatalInterpretationsList,
  useNatalPdfTemplates,
  type NatalInterpretationListItem,
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
import { PersonaSelector } from "./NatalInterpretationPersonaSelector"
import "./NatalInterpretation.css"

interface Props {
  chartLoaded: boolean
  chartId?: string
  lang: AstrologyLang
  fallbackEvidence?: string[]
  initialPersonaId?: string | null
  initialInterpretationId?: number | null
  isLockedFree?: boolean
  onActiveInterpretationChange?: (payload: {
    level: "short" | "complete"
    personaName: string | null
    canSwitchPersona: boolean
  }) => void
  actionRequest?: {
    kind: "upgrade" | "switch_persona"
    nonce: number
  } | null
  longFeatureAccess?: FeatureEntitlementResponse
}

function isFreeShortInterpretation(item: NatalInterpretationListItem): boolean {
  return item.use_case === "natal_long_free"
}

function isRealCompleteInterpretation(item: NatalInterpretationListItem): boolean {
  return item.level === "complete" && item.use_case === "natal_interpretation"
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

export function NatalInterpretationSection({
  chartLoaded,
  chartId,
  lang,
  fallbackEvidence,
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

  const [useCaseLevel, setUseCaseLevel] = useState<"short" | "complete">(
    initialPersonaId || isLockedFree ? "complete" : "short",
  )
  const [selectedPersonaId, setSelectedPersonaId] = useState<string | null>(initialPersonaId)
  const [isUpsellOpen, setIsUpsellOpen] = useState(false)
  const [forceRefresh, setForceRefresh] = useState(false)
  const [refreshKey, setRefreshKey] = useState(0)
  const [selectedInterpretationId, setSelectedInterpretationId] = useState<number | null>(initialInterpretationId)
  const [selectedTemplateKey, setSelectedTemplateKey] = useState("")
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<number | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  const historyQuery = useNatalInterpretationsList({
    enabled: chartLoaded && !!chartId,
    chartId,
  })
  const pdfTemplatesQuery = useNatalPdfTemplates({
    enabled: chartLoaded,
    locale: pdfLocaleFromLang(lang),
  })
  const mainQuery = useNatalInterpretation({
    enabled: chartLoaded && !selectedInterpretationId,
    useCaseLevel,
    personaId: selectedPersonaId,
    allowCompleteWithoutPersona: isLockedFree,
    locale: localeFromLang(lang),
    forceRefresh,
    refreshKey,
  })
  const idQuery = useNatalInterpretationById({
    enabled: !!selectedInterpretationId,
    interpretationId: selectedInterpretationId ?? undefined,
    locale: localeFromLang(lang),
  })

  const activeQuery = selectedInterpretationId ? idQuery : mainQuery
  const { data, isLoading, error, refetch } = activeQuery
  const historyItems = historyQuery.data?.items ?? []
  const latestCompleteInterpretation = findLatestCompleteInterpretation(historyItems)
  const latestShortInterpretation = findLatestShortInterpretation(historyItems)
  const hasCompleteInterpretation = latestCompleteInterpretation !== null
  const hasPersistedFreeShortInterpretation = historyItems.some(isFreeShortInterpretation)
  const isQuotaUsageExhausted = Boolean(
    longFeatureAccess?.reason_code === "quota_exhausted" ||
      longFeatureAccess?.usage_states?.some((state) => state.exhausted || state.remaining <= 0),
  )
  const isSingleAstrologerPlan = longFeatureAccess?.variant_code === "single_astrologer"
  const isPremiumPlan = longFeatureAccess?.variant_code === "multi_astrologer"
  const canSwitchPersona = isPremiumPlan && hasCompleteInterpretation
  const shouldPreferLatestCompleteByDefault = isLockedFree || isPremiumPlan
  const shouldRefreshShortAfterBasicUpgrade =
    isSingleAstrologerPlan &&
    !isLockedFree &&
    hasPersistedFreeShortInterpretation &&
    latestShortInterpretation === null
  const isCompleteGenerationBlocked = !isLockedFree && isQuotaUsageExhausted
  const primaryActionLabel = hasCompleteInterpretation
    ? isLockedFree
      ? t.upgradeToBasicCta
      : isCompleteGenerationBlocked
        ? t.quotaExhaustedCta
        : canSwitchPersona
          ? pageT.requestAnotherAstrologer
          : pageT.unlockCompleteInterpretation
    : isLockedFree
      ? t.upgradeToBasicCta
      : pageT.unlockCompleteInterpretation

  useEffect(() => {
    onActiveInterpretationChange?.({
      level: isLockedFree ? "short" : (data?.meta.level ?? "short"),
      personaName: data?.meta.persona_name ?? null,
      canSwitchPersona,
    })
  }, [canSwitchPersona, data?.meta.level, data?.meta.persona_name, isLockedFree, onActiveInterpretationChange])

  useEffect(() => {
    if (!actionRequest) return
    if (actionRequest.kind === "upgrade" && isLockedFree) {
      navigate(basicUpgradePath)
      return
    }
    if (actionRequest.kind === "switch_persona" && isCompleteGenerationBlocked) {
      navigate(premiumUpgradePath)
      return
    }
    setSelectedInterpretationId(null)
    setSelectedPersonaId(null)
    setForceRefresh(false)
    setIsUpsellOpen(true)
  }, [actionRequest, basicUpgradePath, isCompleteGenerationBlocked, isLockedFree, navigate, premiumUpgradePath])

  useEffect(() => {
    if (typeof initialInterpretationId === "number" && Number.isFinite(initialInterpretationId)) {
      setSelectedInterpretationId(initialInterpretationId)
      setSelectedPersonaId(null)
      setUseCaseLevel("complete")
      return
    }
    if (initialPersonaId) {
      setSelectedInterpretationId(null)
      setSelectedPersonaId(initialPersonaId)
      setUseCaseLevel("complete")
      return
    }
    if (isLockedFree) {
      setSelectedInterpretationId(null)
      setSelectedPersonaId(null)
      setUseCaseLevel("complete")
    }
  }, [initialInterpretationId, initialPersonaId, isLockedFree])

  useEffect(() => {
    if (typeof initialInterpretationId === "number" && Number.isFinite(initialInterpretationId)) return
    if (initialPersonaId) return
    if (historyItems.length === 0) return

    if (shouldPreferLatestCompleteByDefault && latestCompleteInterpretation) {
      setSelectedInterpretationId((current) =>
        current === latestCompleteInterpretation.id ? current : latestCompleteInterpretation.id,
      )
      setSelectedPersonaId(null)
      setUseCaseLevel("complete")
      return
    }

    if (isSingleAstrologerPlan) {
      setSelectedInterpretationId(null)
      setSelectedPersonaId(null)
      setUseCaseLevel("short")
    }
  }, [
    historyItems,
    initialInterpretationId,
    initialPersonaId,
    isSingleAstrologerPlan,
    latestCompleteInterpretation,
    shouldPreferLatestCompleteByDefault,
  ])

  useEffect(() => {
    if (!shouldRefreshShortAfterBasicUpgrade) return
    if (selectedInterpretationId !== null) return

    setSelectedPersonaId(null)
    setUseCaseLevel("short")
    setForceRefresh(true)
    setRefreshKey((previous) => previous + 1)
  }, [selectedInterpretationId, shouldRefreshShortAfterBasicUpgrade])

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
    setSelectedPersonaId(personaId)
    setUseCaseLevel("complete")
    setIsUpsellOpen(false)
    setSelectedInterpretationId(null)
    setForceRefresh(true)
    setRefreshKey((previous) => previous + 1)
  }

  const handleRegenerate = () => {
    if (isLockedFree) {
      navigate(basicUpgradePath)
      return
    }
    if (isCompleteGenerationBlocked) {
      navigate(premiumUpgradePath)
      return
    }
    setSelectedInterpretationId(null)
    setSelectedPersonaId(null)
    setForceRefresh(false)
    setIsUpsellOpen(true)
  }

  const handleSelectVersion = (id: number | null) => {
    setSelectedInterpretationId(id)
    if (id === null) {
      setUseCaseLevel("short")
      setSelectedPersonaId(null)
      setForceRefresh(false)
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
          setUseCaseLevel("short")
        }
      }
      setShowDeleteConfirm(null)
    } catch (err) {
      console.error("Failed to delete interpretation", err)
    } finally {
      setIsDeleting(false)
    }
  }

  const currentInterpretationId =
    selectedInterpretationId ??
    data?.meta.id ??
    historyQuery.data?.items.find((item) => item.created_at === data?.meta.persisted_at)?.id ??
    latestShortInterpretation?.id ??
    historyQuery.data?.items[0]?.id
  const usedPersonaIds = new Set(
    historyItems
      .filter((item) => isRealCompleteInterpretation(item) && Boolean(item.persona_id))
      .map((item) => item.persona_id as string),
  )

  const handlePreviewPdf = async () => {
    if (!accessToken || !currentInterpretationId) return
    try {
      await previewNatalInterpretationPdf(
        accessToken,
        currentInterpretationId,
        selectedTemplateKey || undefined,
        pdfLocaleFromLang(lang),
      )
    } catch (err) {
      console.error("Failed to preview PDF", err)
    }
  }

  const handleDownloadPdf = async () => {
    if (!accessToken || !currentInterpretationId) return
    try {
      await downloadNatalInterpretationPdf(
        accessToken,
        currentInterpretationId,
        selectedTemplateKey || undefined,
        pdfLocaleFromLang(lang),
      )
    } catch (err) {
      console.error("Failed to download PDF", err)
    }
  }

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

        <div className="ni-actions">
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
        {isLoading ? (
          <InterpretationSkeleton t={t} isComplete={useCaseLevel === "complete"} />
        ) : error ? (
          <InterpretationError t={t} onRetry={() => refetch()} />
        ) : data ? (
          <>
            <InterpretationContent
              data={data}
              lang={lang}
              fallbackEvidence={fallbackEvidence}
              isLockedFree={isLockedFree}
            />
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
  )
}
