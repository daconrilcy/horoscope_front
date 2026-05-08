// Regroupe les sous-sections UI des sample payloads admin hors de la route appelante.
type AdminSamplePayloadsToolbarProps = {
  featureOptions: string[]
  localeOptions: string[]
  feature: string
  locale: string
  includeInactive: boolean
  onFeatureChange: (value: string) => void
  onLocaleChange: (value: string) => void
  onIncludeInactiveChange: (value: boolean) => void
  onCreate: () => void
}

type AdminSamplePayloadDeleteDialogProps = {
  name: string
  error: string | null
  isPending: boolean
  onCancel: () => void
  onConfirm: () => void
}

/** Rend les filtres de gestion des sample payloads sans posseder les requetes. */
export function AdminSamplePayloadsToolbar({
  featureOptions,
  localeOptions,
  feature,
  locale,
  includeInactive,
  onFeatureChange,
  onLocaleChange,
  onIncludeInactiveChange,
  onCreate,
}: AdminSamplePayloadsToolbarProps) {
  return (
    <div className="sample-payloads-admin__toolbar">
      <label>
        Feature
        <select aria-label="Feature pour les sample payloads" value={feature} onChange={(event) => onFeatureChange(event.target.value)}>
          <option value="">—</option>
          {featureOptions.map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </select>
      </label>
      <label>
        Locale
        <select aria-label="Locale pour les sample payloads" value={locale} onChange={(event) => onLocaleChange(event.target.value)}>
          <option value="">—</option>
          {localeOptions.map((value) => (
            <option key={value} value={value}>
              {value}
            </option>
          ))}
        </select>
      </label>
      <label className="sample-payloads-admin__toolbar-actions">
        <span>Afficher les inactifs</span>
        <input
          type="checkbox"
          checked={includeInactive}
          onChange={(event) => onIncludeInactiveChange(event.target.checked)}
          aria-label="Afficher les sample payloads inactifs"
        />
      </label>
      <div className="sample-payloads-admin__toolbar-actions">
        <button className="action-button action-button--primary" type="button" onClick={onCreate} disabled={!feature || !locale}>
          Nouveau sample payload
        </button>
      </div>
    </div>
  )
}

/** Rend la confirmation de suppression sans connaitre la mutation. */
export function AdminSamplePayloadDeleteDialog({
  name,
  error,
  isPending,
  onCancel,
  onConfirm,
}: AdminSamplePayloadDeleteDialogProps) {
  return (
    <div className="modal-overlay" role="presentation">
      <div className="modal-content admin-prompts-modal" role="dialog" aria-modal="true" aria-labelledby="sample-payload-delete-title">
        <h3 id="sample-payload-delete-title">Supprimer le sample payload</h3>
        <p className="admin-prompts-modal__copy">
          Confirmer la suppression de <strong>{name}</strong> ? Cette action est irréversible.
        </p>
        {error ? (
          <p className="chat-error" role="alert">
            {error}
          </p>
        ) : null}
        <div className="modal-actions">
          <button className="text-button" type="button" onClick={onCancel}>
            Annuler
          </button>
          <button className="action-button action-button--secondary" type="button" onClick={onConfirm} disabled={isPending}>
            {isPending ? "Suppression…" : "Supprimer"}
          </button>
        </div>
      </div>
    </div>
  )
}
