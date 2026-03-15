import {
  PrivacyApiError,
  useDeleteStatus,
  useExportStatus,
  useRequestDelete,
  useRequestExport,
} from "@api"
import { useTranslation } from "../i18n"

export function PrivacyPanel() {
  const t = useTranslation("admin").b2b.privacy
  const exportStatus = useExportStatus()
  const deleteStatus = useDeleteStatus()
  const requestExport = useRequestExport()
  const requestDelete = useRequestDelete()

  const exportError = requestExport.error as PrivacyApiError | null
  const deleteError = requestDelete.error as PrivacyApiError | null

  return (
    <section className="panel">
      <h2>{t.title}</h2>
      <p>{t.description}</p>

      <div className="action-row">
        <button
          type="button"
          disabled={requestExport.isPending}
          onClick={() => requestExport.mutate()}
        >
          {t.requestExport}
        </button>
        <button
          type="button"
          className="button-danger"
          disabled={requestDelete.isPending}
          onClick={() => requestDelete.mutate()}
        >
          {t.requestDelete}
        </button>
      </div>

      <div className="status-section mt-6">
        <h3>Export Status</h3>
        {exportStatus.data ? <p className="state-line">{t.statusExport(exportStatus.data.status)}</p> : null}
        {!exportStatus.data && !exportStatus.isPending && (
          <p className="state-line state-empty">{t.emptyExport}</p>
        )}
        {exportStatus.isError ? (
          <p className="chat-error">{t.errorExportStatus((exportStatus.error as PrivacyApiError).message)}</p>
        ) : null}
      </div>

      <div className="status-section mt-6">
        <h3>Deletion Status</h3>
        {deleteStatus.data ? <p className="state-line">{t.statusDelete(deleteStatus.data.status)}</p> : null}
        {!deleteStatus.data && !deleteStatus.isPending && (
          <p className="state-line state-empty">{t.emptyDelete}</p>
        )}
        {deleteStatus.isError ? (
          <p className="chat-error">{t.errorDeleteStatus((deleteStatus.error as PrivacyApiError).message)}</p>
        ) : null}
      </div>

      {exportError ? <p className="chat-error">{t.errorExportRequest(exportError.message)}</p> : null}
      {deleteError ? <p className="chat-error">{t.errorDeleteRequest(deleteError.message)}</p> : null}
    </section>
  )
}
