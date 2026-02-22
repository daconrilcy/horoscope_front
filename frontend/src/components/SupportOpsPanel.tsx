import { useMemo, useState } from "react"

import {
  SupportApiError,
  type SupportIncident,
  useCreateSupportIncident,
  useSupportContext,
  useSupportIncidents,
  useUpdateSupportIncident,
} from "../api/support"

function nextStatus(current: SupportIncident["status"]): SupportIncident["status"] | null {
  if (current === "open") {
    return "in_progress"
  }
  if (current === "in_progress") {
    return "resolved"
  }
  if (current === "resolved") {
    return "closed"
  }
  return null
}

export function SupportOpsPanel() {
  const [targetUserId, setTargetUserId] = useState(1)
  const [title, setTitle] = useState("Incident support")
  const [description, setDescription] = useState("Description de l incident.")
  const [category, setCategory] = useState<"account" | "subscription" | "content">("account")
  const [priority, setPriority] = useState<"low" | "medium" | "high">("medium")

  const supportContext = useSupportContext(targetUserId, true)
  const incidents = useSupportIncidents({ user_id: targetUserId }, true)
  const createIncident = useCreateSupportIncident()
  const updateIncident = useUpdateSupportIncident()

  const createError = createIncident.error as SupportApiError | null
  const updateError = updateIncident.error as SupportApiError | null

  const orderedIncidents = useMemo(() => incidents.data?.incidents ?? [], [incidents.data?.incidents])

  return (
    <section className="panel">
      <h2>Support et operations</h2>
      <p>Consultez le dossier utilisateur et gerez les incidents.</p>

      <label htmlFor="support-target-user">Utilisateur cible</label>
      <div className="action-row">
        <input
          id="support-target-user"
          type="number"
          min={1}
          value={targetUserId}
          onChange={(event) => setTargetUserId(Number(event.target.value) || 1)}
        />
        <button
          type="button"
          onClick={() => {
            void supportContext.refetch()
            void incidents.refetch()
          }}
        >
          Charger le dossier support
        </button>
      </div>

      {supportContext.isLoading ? (
        <p aria-busy="true" className="state-line state-loading">
          Chargement contexte support...
        </p>
      ) : null}
      {supportContext.error ? (
        <p role="alert" className="chat-error">
          Erreur contexte: {(supportContext.error as SupportApiError).message}
        </p>
      ) : null}
      {supportContext.data ? (
        <>
          <p className="state-line">
            Compte: {supportContext.data.user.email} ({supportContext.data.user.role})
          </p>
          <p className="state-line">
            Abonnement: {supportContext.data.subscription.status}
            {supportContext.data.subscription.plan
              ? ` · ${supportContext.data.subscription.plan.display_name}`
              : ""}
          </p>
          <p className="state-line">Demandes RGPD: {supportContext.data.privacy_requests.length}</p>
          {supportContext.data.privacy_requests.length > 0 ? (
            <ul className="chat-list compact-list">
              {supportContext.data.privacy_requests.map((item) => (
                <li key={item.request_id} className="chat-item">
                  RGPD #{item.request_id} · {item.request_kind} · {item.status}
                </li>
              ))}
            </ul>
          ) : (
            <p className="state-line state-empty">Aucune demande RGPD.</p>
          )}
          <h3>Audit recent</h3>
          {supportContext.data.audit_events.length > 0 ? (
            <ul className="chat-list compact-list">
              {supportContext.data.audit_events.map((event) => (
                <li key={event.event_id} className="chat-item">
                  Audit #{event.event_id} · {event.action} · {event.status}
                </li>
              ))}
            </ul>
          ) : (
            <p className="state-line state-empty">Aucun evenement d audit recent.</p>
          )}
        </>
      ) : null}
      {!supportContext.isLoading && !supportContext.error && !supportContext.data ? (
        <p className="state-line state-empty">Aucun dossier charge.</p>
      ) : null}

      <h3>Creer un incident</h3>
      <label htmlFor="support-category">Categorie</label>
      <div className="action-row">
        <select
          id="support-category"
          value={category}
          onChange={(event) => setCategory(event.target.value as "account" | "subscription" | "content")}
        >
          <option value="account">Compte</option>
          <option value="subscription">Abonnement</option>
          <option value="content">Contenu</option>
        </select>
      </div>
      <label htmlFor="support-priority">Priorite</label>
      <div className="action-row">
        <select
          id="support-priority"
          value={priority}
          onChange={(event) => setPriority(event.target.value as "low" | "medium" | "high")}
        >
          <option value="low">Faible</option>
          <option value="medium">Moyenne</option>
          <option value="high">Haute</option>
        </select>
      </div>
      <label htmlFor="support-title">Titre</label>
      <input id="support-title" value={title} onChange={(event) => setTitle(event.target.value)} />
      <label htmlFor="support-description">Description</label>
      <textarea
        id="support-description"
        value={description}
        onChange={(event) => setDescription(event.target.value)}
      />
      <div className="action-row">
        <button
          type="button"
          disabled={createIncident.isPending}
          onClick={async () => {
            await createIncident.mutateAsync({
              user_id: targetUserId,
              category,
              title,
              description,
              priority,
            })
            void supportContext.refetch()
            void incidents.refetch()
          }}
        >
          Creer incident
        </button>
      </div>
      {createError ? (
        <p role="alert" className="chat-error">
          Erreur creation incident: {createError.message}
        </p>
      ) : null}

      <h3>Incidents</h3>
      {incidents.isLoading ? (
        <p aria-busy="true" className="state-line state-loading">
          Chargement incidents...
        </p>
      ) : null}
      {incidents.error ? (
        <p role="alert" className="chat-error">
          Erreur incidents: {(incidents.error as SupportApiError).message}
        </p>
      ) : null}
      {!incidents.isLoading && !incidents.error && orderedIncidents.length === 0 ? (
        <p className="state-line state-empty">Aucun incident pour cet utilisateur.</p>
      ) : null}
      {orderedIncidents.length > 0 ? (
        <ul className="chat-list compact-list">
          {orderedIncidents.map((incident) => (
            <li key={incident.incident_id} className="chat-item">
              <p>
                #{incident.incident_id} · {incident.category} · {incident.priority} · {incident.status}
              </p>
              <p>{incident.title}</p>
              <p>{incident.description}</p>
              <button
                type="button"
                disabled={updateIncident.isPending || nextStatus(incident.status) === null}
                onClick={async () => {
                  const status = nextStatus(incident.status)
                  if (status === null) {
                    return
                  }
                  await updateIncident.mutateAsync({
                    incidentId: incident.incident_id,
                    payload: { status },
                  })
                  void supportContext.refetch()
                  void incidents.refetch()
                }}
              >
                {incident.status === "open"
                  ? "Passer en cours"
                  : incident.status === "in_progress"
                    ? "Resoudre"
                    : incident.status === "resolved"
                      ? "Clore"
                      : "Clos"}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      {updateError ? (
        <p role="alert" className="chat-error">
          Erreur mise a jour incident: {updateError.message}
        </p>
      ) : null}
    </section>
  )
}
