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
      <h2>Confidentialite et donnees</h2>
      <p>Demandez un export de vos donnees ou la suppression de votre compte.</p>

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
      {exportStatus.isLoading ? <p aria-busy="true">Chargement statut export...</p> : null}
      {exportStatus.data ? <p>Statut export: {exportStatus.data.status}</p> : null}
      {!exportStatus.isLoading && !exportStatus.error && !exportStatus.data ? (
        <p>Aucune demande d export pour le moment.</p>
      ) : null}
      {exportStatus.error ? (
        <p>Erreur statut export: {(exportStatus.error as PrivacyApiError).message}</p>
      ) : null}

      <button
        type="button"
        disabled={requestDelete.isPending}
        onClick={async () => {
          const confirmed = window.confirm(
            "Confirmez-vous la suppression de vos donnees personnelles ?",
          )
          if (!confirmed) {
            return
          }
          await requestDelete.mutateAsync()
          void deleteStatus.refetch()
        }}
      >
        Supprimer mes donnees
      </button>
      {deleteStatus.isLoading ? <p aria-busy="true">Chargement statut suppression...</p> : null}
      {deleteStatus.data ? <p>Statut suppression: {deleteStatus.data.status}</p> : null}
      {!deleteStatus.isLoading && !deleteStatus.error && !deleteStatus.data ? (
        <p>Aucune demande de suppression pour le moment.</p>
      ) : null}
      {deleteStatus.error ? (
        <p>Erreur statut suppression: {(deleteStatus.error as PrivacyApiError).message}</p>
      ) : null}

      {exportError ? <p>Erreur demande export: {exportError.message}</p> : null}
      {deleteError ? <p>Erreur demande suppression: {deleteError.message}</p> : null}
    </section>
  )
}
