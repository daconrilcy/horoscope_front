// Regroupe les fragments UI et helpers partages de la page admin prompts hors du conteneur de route.
import type { ReactNode } from "react"

import {
  AdminPromptsApiError,
  type AdminConsumptionRow,
  type AdminLlmCatalogEntry,
  type AdminPromptVersion,
  type AdminResolvedPlaceholder,
} from "@api"
import {
  archivePromptStatusLabel,
  formatArchivePromptTimestamp,
  interpolateArchiveTemplate,
  type AdminPromptsArchiveStrings,
} from "@i18n/adminPromptsArchive"
import type { AdminPromptsCatalogStrings } from "@i18n/adminPromptsCatalog"
import type { AppLocale } from "@i18n/types"

export type DiffRow = {
  leftText: string
  rightText: string
  leftType: "unchanged" | "removed"
  rightType: "unchanged" | "added"
}

export function consumptionRowKey(row: AdminConsumptionRow): string {
  return `${row.period_start_utc}::${row.user_id ?? "none"}::${row.subscription_plan ?? "none"}::${row.feature ?? "none"}::${row.subfeature ?? "none"}`
}

export function formatReleaseSnapshotIdShort(id: string): string {
  return id.length > 10 ? `${id.slice(0, 8)}…` : id
}

/** Segments complets du manifest pour distinguer les variantes canoniques. */
export function formatManifestEntryCatalogHint(manifestEntryId: string): string {
  const parts = manifestEntryId
    .split(":")
    .map((segment) => segment.trim())
    .filter((segment) => segment.length > 0)
  if (parts.length === 0) {
    return manifestEntryId.trim() || "—"
  }
  return parts.join(" · ")
}

export function pickPreferredCatalogEntry(entries: AdminLlmCatalogEntry[]): AdminLlmCatalogEntry | null {
  if (entries.length === 0) {
    return null
  }
  return [...entries].sort((left, right) => {
    const leftScore =
      (left.execution_path_kind === "nominal" ? 4 : 0) +
      (left.source_of_truth_status === "active_snapshot" ? 2 : 0) +
      (left.catalog_visibility_status === "visible" ? 1 : 0)
    const rightScore =
      (right.execution_path_kind === "nominal" ? 4 : 0) +
      (right.source_of_truth_status === "active_snapshot" ? 2 : 0) +
      (right.catalog_visibility_status === "visible" ? 1 : 0)
    if (leftScore !== rightScore) {
      return rightScore - leftScore
    }
    return (left.subfeature ?? "").localeCompare(right.subfeature ?? "")
  })[0] ?? null
}

export function formatCatalogFeatureLabel(feature: string): string {
  const normalized = feature.trim().toLowerCase()
  const labels: Record<string, string> = {
    chat: "Chat",
    guidance: "Consultations thematiques",
    natal: "Natal",
    horoscope_daily: "Horoscope quotidien",
  }
  return labels[normalized] ?? feature
}

export function releaseDiffAxisBadgeClass(changed: boolean): string {
  return changed ? "badge badge--warning" : "badge badge--info"
}

type ManualLlmExecuteConfirmModalProps = {
  isPending: boolean
  manifestEntryId: string
  samplePayloadId: string
  inspectionModeLabel: string
  catalog: AdminPromptsCatalogStrings
  onCancel: () => void
  onConfirm: () => void
}

export function ManualLlmExecuteConfirmModal({
  isPending,
  manifestEntryId,
  samplePayloadId,
  inspectionModeLabel,
  catalog: c,
  onCancel,
  onConfirm,
}: ManualLlmExecuteConfirmModalProps) {
  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content admin-prompts-modal admin-prompts-modal--manual-llm"
        aria-labelledby="manual-llm-exec-title"
        role="dialog"
        aria-modal="true"
      >
        <h3 id="manual-llm-exec-title">{c.manualLlmModalTitle}</h3>
        <p className="admin-prompts-modal__copy">
          {c.manualLlmModalIntroBeforeSample}
          <code>{samplePayloadId}</code>
          {c.manualLlmModalBetweenSampleAndManifest}
          <code>{manifestEntryId}</code>
          {c.manualLlmModalAfterManifest}
        </p>
        <p className="admin-prompts-modal__copy admin-prompts-modal__copy--emphasis">
          {c.manualLlmModalModePrefix}
          <strong>{inspectionModeLabel}</strong>
          {c.manualLlmModalModeTraced}
        </p>
        <div className="modal-actions">
          <button className="text-button" type="button" onClick={onCancel}>
            {c.manualLlmModalCancel}
          </button>
          <button
            className="action-button action-button--primary"
            type="button"
            disabled={isPending}
            onClick={onConfirm}
          >
            {isPending ? c.manualLlmModalExecuting : c.manualLlmModalConfirm}
          </button>
        </div>
      </div>
    </div>
  )
}

type ArchiveVersionMetaStripProps = {
  version: AdminPromptVersion
  headingId: string
  variant: "reference" | "active" | "peer"
  archive: AdminPromptsArchiveStrings
  lang: AppLocale
}

export function ArchiveVersionMetaStrip({ version, headingId, variant, archive, lang }: ArchiveVersionMetaStripProps) {
  const variantLabel =
    variant === "reference"
      ? archive.metaVariantReference
      : variant === "active"
        ? archive.metaVariantProduction
        : archive.metaVariantPeer
  return (
    <div className="admin-prompts-archive__meta-strip-wrap" aria-labelledby={headingId}>
      <div className="admin-prompts-archive__meta-strip-kicker">
        <span className="admin-prompts-archive__pill">{variantLabel}</span>
      </div>
      <dl className="admin-prompts-archive__meta-strip">
        <div>
          <dt>{archive.metaStatus}</dt>
          <dd>
            <span className={`badge ${version.status === "published" ? "badge--info" : "badge--warning"}`}>
              {archivePromptStatusLabel(version.status, archive)}
            </span>
          </dd>
        </div>
        <div>
          <dt>{archive.metaModel}</dt>
          <dd>{version.model}</dd>
        </div>
        <div>
          <dt>{archive.metaAuthor}</dt>
          <dd>{version.created_by}</dd>
        </div>
        <div>
          <dt>{archive.metaCreated}</dt>
          <dd>{formatArchivePromptTimestamp(version.created_at, lang)}</dd>
        </div>
        <div>
          <dt>{archive.metaId}</dt>
          <dd>
            <code>{version.id}</code>
          </dd>
        </div>
        {version.published_at ? (
          <div>
            <dt>{archive.metaPublished}</dt>
            <dd>{formatArchivePromptTimestamp(version.published_at, lang)}</dd>
          </div>
        ) : null}
      </dl>
    </div>
  )
}

type ArchiveRollbackModalProps = {
  isPending: boolean
  useCaseKey: string
  useCaseDisplayName: string
  activeVersion: AdminPromptVersion | null
  targetVersion: AdminPromptVersion
  archive: AdminPromptsArchiveStrings
  onCancel: () => void
  onConfirm: () => void
}

export function ArchiveRollbackModal({
  isPending,
  useCaseKey,
  useCaseDisplayName,
  activeVersion,
  targetVersion,
  archive,
  onCancel,
  onConfirm,
}: ArchiveRollbackModalProps) {
  const activeShort = activeVersion ? `${activeVersion.id.slice(0, 8)}…` : "—"
  const targetShort = `${targetVersion.id.slice(0, 8)}…`
  const statusTarget = archivePromptStatusLabel(targetVersion.status, archive)
  const statusActive = activeVersion ? archivePromptStatusLabel(activeVersion.status, archive) : ""
  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal-content admin-prompts-modal admin-prompts-modal--rollback"
        aria-labelledby="archive-rollback-title"
        role="dialog"
        aria-modal="true"
      >
        <h3 id="archive-rollback-title">{archive.modalTitle}</h3>
        <p className="admin-prompts-modal__copy">
          {interpolateArchiveTemplate(archive.modalPublishTarget, {
            code: targetShort,
            status: statusTarget,
            name: useCaseDisplayName,
            key: useCaseKey,
          })}
        </p>
        {activeVersion ? (
          <p className="admin-prompts-modal__copy">
            {interpolateArchiveTemplate(archive.modalReplaceActive, {
              code: activeShort,
              status: statusActive,
            })}
          </p>
        ) : (
          <p className="admin-prompts-modal__copy text-muted">{archive.modalNoActiveResolved}</p>
        )}
        <p className="admin-prompts-modal__copy admin-prompts-modal__copy--emphasis">{archive.modalEmphasis}</p>
        <div className="modal-actions">
          <button className="text-button" type="button" onClick={onCancel}>
            {archive.modalCancel}
          </button>
          <button className="action-button action-button--primary" type="button" disabled={isPending} onClick={onConfirm}>
            {isPending ? archive.modalConfirming : archive.modalConfirm}
          </button>
        </div>
      </div>
    </div>
  )
}

export function PromptDisclosure({ summary, children }: { summary: string; children: ReactNode }) {
  return (
    <details className="admin-prompts-detail__disclosure">
      <summary className="admin-prompts-detail__disclosure-summary">{summary}</summary>
      <div className="admin-prompts-detail__disclosure-body">{children}</div>
    </details>
  )
}

export function resolvedAssemblyErrorPresentation(
  error: unknown,
  tCat: AdminPromptsCatalogStrings,
): { primary: string; secondary: string | null } {
  if (!(error instanceof AdminPromptsApiError)) {
    return { primary: tCat.resolvedErrorLoadDetailGeneric, secondary: null }
  }
  const mapped = tCat.resolvedAssemblyErrorMessage(error.code)
  const primary = mapped ?? error.message
  const secondary =
    mapped && mapped !== error.message
      ? error.message
      : !mapped
        ? tCat.resolvedErrorSecondaryCodeHttp(error.code, error.status)
        : null
  return { primary, secondary }
}

export function AdminPromptsResolvedAssemblyError({
  error,
  catalog,
}: {
  error: unknown
  catalog: AdminPromptsCatalogStrings
}) {
  const { primary, secondary } = resolvedAssemblyErrorPresentation(error, catalog)
  return (
    <div className="admin-prompts-resolved__error" role="alert">
      <p className="admin-prompts-resolved__error-primary">{primary}</p>
      {secondary ? (
        <p className="admin-prompts-resolved__error-secondary text-muted">{secondary}</p>
      ) : null}
    </div>
  )
}

export function placeholderStatusClassName(status: AdminResolvedPlaceholder["status"]): string {
  switch (status) {
    case "blocking_missing":
      return "admin-prompts-resolved__placeholder-status--blocking"
    case "expected_missing_in_preview":
      return "admin-prompts-resolved__placeholder-status--expected-preview"
    default:
      return "admin-prompts-resolved__placeholder-status--neutral"
  }
}

export function manualExecutionFailureLead(error: unknown, tCat: AdminPromptsCatalogStrings): string | null {
  if (!(error instanceof AdminPromptsApiError)) {
    return null
  }
  const kind = error.details.failure_kind
  if (typeof kind !== "string") {
    return null
  }
  return tCat.manualExecutionFailureLeadMessage(kind) ?? null
}

export function formatPromptSaveError(error: unknown): string {
  if (error instanceof AdminPromptsApiError) {
    const detailLines = Object.entries(error.details)
      .filter(([, value]) => value !== null && value !== undefined && value !== "")
      .map(([key, value]) => {
        if (Array.isArray(value)) {
          return `${key}: ${value.join(", ")}`
        }
        if (typeof value === "object") {
          return `${key}: ${JSON.stringify(value)}`
        }
        return `${key}: ${String(value)}`
      })
    return detailLines.length > 0 ? `${error.message} (${detailLines.join(" · ")})` : error.message
  }
  if (error instanceof Error) {
    return error.message
  }
  return "Erreur inconnue."
}

export function buildDiffRows(basePrompt: string, nextPrompt: string): DiffRow[] {
  const leftLines = basePrompt.split("\n")
  const rightLines = nextPrompt.split("\n")
  const rowCount = Math.max(leftLines.length, rightLines.length)
  const rows: DiffRow[] = []

  for (let index = 0; index < rowCount; index += 1) {
    const leftText = leftLines[index] ?? ""
    const rightText = rightLines[index] ?? ""
    rows.push({
      leftText,
      rightText,
      leftType: leftText === rightText ? "unchanged" : "removed",
      rightType: leftText === rightText ? "unchanged" : "added",
    })
  }

  return rows
}
