import { useEffect, useState } from "react"
import { useQueryClient } from "@tanstack/react-query"

import {
  useAdminLlmPersonas,
  useAdminPersonaDetail,
  useUpdateAdminPersona,
  type AdminLlmPersona,
} from "@api"
import "./PersonasAdmin.css"

type TogglePersonaModalProps = {
  affectedUsersCount: number
  isPending: boolean
  persona: AdminLlmPersona
  onCancel: () => void
  onConfirm: () => void
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString("fr-FR")
}

function TogglePersonaModal({
  affectedUsersCount,
  isPending,
  persona,
  onCancel,
  onConfirm,
}: TogglePersonaModalProps) {
  const nextStatusLabel = persona.enabled ? "inactive" : "active"

  return (
    <div className="modal-overlay" role="presentation">
      <div className="modal-content personas-admin-modal" role="dialog" aria-modal="true" aria-labelledby="persona-toggle-title">
        <h3 id="persona-toggle-title">
          {persona.enabled ? "Désactiver la persona" : "Réactiver la persona"}
        </h3>
        <p className="personas-admin-modal__copy">
          La persona <strong>{persona.name}</strong> passera au statut <strong>{nextStatusLabel}</strong>.
        </p>
        {affectedUsersCount > 0 ? (
          <p className="state-line state-warning">
            Cette persona est utilisée par {affectedUsersCount} utilisateurs actifs. La désactiver peut affecter leur expérience.
          </p>
        ) : null}
        <div className="modal-actions">
          <button className="text-button" type="button" onClick={onCancel}>
            Annuler
          </button>
          <button
            className={`action-button ${persona.enabled ? "action-button--secondary" : "action-button--primary"}`}
            type="button"
            onClick={onConfirm}
            disabled={isPending}
          >
            {isPending ? "Sauvegarde..." : persona.enabled ? "Confirmer la désactivation" : "Confirmer l'activation"}
          </button>
        </div>
      </div>
    </div>
  )
}

function StatusBadge({ enabled }: { enabled: boolean }) {
  return (
    <span className={`badge ${enabled ? "badge--status-active" : "badge--status-deprecated"}`}>
      {enabled ? "active" : "inactive"}
    </span>
  )
}

export function PersonasAdmin() {
  const queryClient = useQueryClient()
  const personasQuery = useAdminLlmPersonas()
  const personas = personasQuery.data ?? []
  const [selectedPersonaId, setSelectedPersonaId] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [personaToToggle, setPersonaToToggle] = useState<AdminLlmPersona | null>(null)

  useEffect(() => {
    if (!selectedPersonaId && personas.length > 0) {
      setSelectedPersonaId(personas[0].id)
    }
  }, [personas, selectedPersonaId])

  const personaDetailQuery = useAdminPersonaDetail(selectedPersonaId, Boolean(selectedPersonaId))
  const updatePersonaMutation = useUpdateAdminPersona()
  const detail = personaDetailQuery.data

  const handleTogglePersona = async () => {
    if (!personaToToggle) {
      return
    }
    try {
      setErrorMessage(null)
      const updatedPersona = await updatePersonaMutation.mutateAsync({
        personaId: personaToToggle.id,
        payload: { enabled: !personaToToggle.enabled },
      })
      setSuccessMessage(
        updatedPersona.enabled
          ? `Persona ${updatedPersona.name} réactivée.`
          : `Persona ${updatedPersona.name} désactivée.`,
      )
      setPersonaToToggle(null)
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["admin-llm-personas"] }),
        queryClient.invalidateQueries({ queryKey: ["admin-llm-persona-detail", updatedPersona.id] }),
        queryClient.invalidateQueries({ queryKey: ["admin-llm-use-cases"] }),
      ])
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erreur inconnue."
      setErrorMessage(`Impossible de mettre à jour la persona. ${message}`)
    }
  }

  const hasError = personasQuery.isError || personaDetailQuery.isError

  return (
    <section className="personas-admin" aria-labelledby="personas-admin-title">
      <header className="personas-admin__header">
        <div>
          <h2 id="personas-admin-title" data-testid="personas-admin-title">
            Personas astrologues
          </h2>
          <p className="personas-admin__intro">
            Consultez le détail des personas LLM et activez ou désactivez-les sans redéploiement.
          </p>
        </div>
      </header>

      {successMessage ? <p className="state-line state-success">{successMessage}</p> : null}
      {errorMessage ? <p className="chat-error">{errorMessage}</p> : null}
      {personasQuery.isPending ? <div className="loading-placeholder">Chargement des personas...</div> : null}
      {hasError ? (
        <p className="chat-error">Impossible de charger les personas admin. Rafraîchissez puis réessayez.</p>
      ) : null}

      {!personasQuery.isPending && !hasError ? (
        <div className="personas-admin__layout">
          <aside className="personas-admin__sidebar" aria-label="Liste des personas">
            {personas.map((persona) => (
              <button
                key={persona.id}
                type="button"
                className={`personas-admin__card ${
                  selectedPersonaId === persona.id ? "personas-admin__card--active" : ""
                }`}
                onClick={() => {
                  setSelectedPersonaId(persona.id)
                  setSuccessMessage(null)
                  setErrorMessage(null)
                }}
              >
                <div className="personas-admin__card-topline">
                  <span className="personas-admin__card-title">{persona.name}</span>
                  <StatusBadge enabled={persona.enabled} />
                </div>
                <p className="personas-admin__card-copy">{persona.description || "Aucune description."}</p>
                <span className="personas-admin__card-meta">
                  Dernière modification: {formatDate(persona.updated_at)}
                </span>
              </button>
            ))}
          </aside>

          <section className="personas-admin__detail panel" aria-label="Détail persona">
            {detail ? (
              <>
                <div className="personas-admin__detail-header">
                  <div>
                    <div className="personas-admin__detail-title">
                      <h3>{detail.persona.name}</h3>
                      <StatusBadge enabled={detail.persona.enabled} />
                    </div>
                    <p>{detail.persona.description || "Aucune description fournie pour cette persona."}</p>
                  </div>
                  <button
                    className={`action-button ${detail.persona.enabled ? "action-button--secondary" : "action-button--primary"}`}
                    type="button"
                    onClick={() => setPersonaToToggle(detail.persona)}
                  >
                    {detail.persona.enabled ? "Désactiver" : "Activer"}
                  </button>
                </div>

                <dl className="personas-admin__meta">
                  <div>
                    <dt>Ton</dt>
                    <dd>{detail.persona.tone}</dd>
                  </div>
                  <div>
                    <dt>Verbosité</dt>
                    <dd>{detail.persona.verbosity}</dd>
                  </div>
                  <div>
                    <dt>Dernière modification</dt>
                    <dd>{formatDate(detail.persona.updated_at)}</dd>
                  </div>
                  <div>
                    <dt>Utilisateurs impactés</dt>
                    <dd>{detail.affected_users_count}</dd>
                  </div>
                </dl>

                <div className="personas-admin__grid">
                  <article className="personas-admin__panel">
                    <h4>Contraintes de comportement</h4>
                    <ul>
                      {detail.persona.boundaries.length > 0 ? (
                        detail.persona.boundaries.map((item) => <li key={item}>{item}</li>)
                      ) : (
                        <li>Aucune contrainte spécifique.</li>
                      )}
                    </ul>
                  </article>

                  <article className="personas-admin__panel">
                    <h4>Marqueurs de style</h4>
                    <ul>
                      {detail.persona.style_markers.length > 0 ? (
                        detail.persona.style_markers.map((item) => <li key={item}>{item}</li>)
                      ) : (
                        <li>Aucun marqueur déclaré.</li>
                      )}
                    </ul>
                  </article>

                  <article className="personas-admin__panel">
                    <h4>Use cases associés</h4>
                    <ul>
                      {detail.use_cases.length > 0 ? (
                        detail.use_cases.map((item) => <li key={item}>{item}</li>)
                      ) : (
                        <li>Aucun use case associé.</li>
                      )}
                    </ul>
                  </article>

                  <article className="personas-admin__panel">
                    <h4>Format de réponse</h4>
                    <ul>
                      {Object.entries(detail.persona.formatting).map(([key, value]) => (
                        <li key={key}>
                          {key}: {value ? "oui" : "non"}
                        </li>
                      ))}
                    </ul>
                  </article>
                </div>
              </>
            ) : (
              <div className="loading-placeholder">Sélectionnez une persona pour voir son détail.</div>
            )}
          </section>
        </div>
      ) : null}

      {personaToToggle && detail ? (
        <TogglePersonaModal
          affectedUsersCount={detail.affected_users_count}
          isPending={updatePersonaMutation.isPending}
          persona={personaToToggle}
          onCancel={() => setPersonaToToggle(null)}
          onConfirm={() => void handleTogglePersona()}
        />
      ) : null}
    </section>
  )
}
