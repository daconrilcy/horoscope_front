import {
  PrivacyApiError,
  useDeleteStatus,
  useExportStatus,
  useRequestDelete,
  useRequestExport,
} from "../api/privacy"

export function PrivacyPanel() {
  const exportStatus = useExportStatus()
  const deleteStatus = useDeleteStatus()
  const requestExport = useRequestExport()
  const requestDelete = useRequestDelete()

  const exportError = requestExport.error as PrivacyApiError | null
  const deleteError = requestDelete.error as PrivacyApiError | null

  return (
    <section className="panel">
      <h2>Confidentialité et données</h2>
      <p>Demandez un export de vos données ou la suppression de votre compte.</p>

      <div className="action-row">
        <button
          type="button"
          disabled={requestExport.isPending}
          onClick={async () => {
            await requestExport.mutateAsync()
            void exportStatus.refetch()
          }}
        >
          Demander un export
        </button>
      </div>
      {exportStatus.isLoading ? (
        <p aria-busy="true" className="state-line state-loading">
          Chargement statut export...
        </p>
      ) : null}
      {exportStatus.data ? <p className="state-line">Statut export: {exportStatus.data.status}</p> : null}
      {!exportStatus.isLoading && !exportStatus.error && !exportStatus.data ? (
        <p className="state-line state-empty">Aucune demande d'export pour le moment.</p>
      ) : null}
      {exportStatus.error ? (
        <p className="chat-error">Erreur statut export: {(exportStatus.error as PrivacyApiError).message}</p>
      ) : null}

      <div className="action-row">
        <button
          type="button"
          disabled={requestDelete.isPending}
          onClick={async () => {
            const confirmed = window.confirm(
              "Confirmez-vous la suppression de vos données personnelles ?",
            )
            if (!confirmed) {
              return
            }
            await requestDelete.mutateAsync()
            void deleteStatus.refetch()
          }}
        >
          Supprimer mes données
        </button>
      </div>
      {deleteStatus.isLoading ? (
        <p aria-busy="true" className="state-line state-loading">
          Chargement statut suppression...
        </p>
      ) : null}
      {deleteStatus.data ? <p className="state-line">Statut suppression: {deleteStatus.data.status}</p> : null}
      {!deleteStatus.isLoading && !deleteStatus.error && !deleteStatus.data ? (
        <p className="state-line state-empty">Aucune demande de suppression pour le moment.</p>
      ) : null}
      {deleteStatus.error ? (
        <p className="chat-error">Erreur statut suppression: {(deleteStatus.error as PrivacyApiError).message}</p>
      ) : null}

      {exportError ? <p className="chat-error">Erreur demande export: {exportError.message}</p> : null}
      {deleteError ? <p className="chat-error">Erreur demande suppression: {deleteError.message}</p> : null}
    </section>
  )
}
