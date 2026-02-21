import { useMemo, useState } from "react"

import {
  SupportApiError,
  type SupportIncident,
  useCreateSupportIncident,
  useSupportContext,
  useSupportIncidents,
  useUpdateSupportIncident,
} from "../api/support"

function getRoleFromAccessToken(): string | null {
  const token = localStorage.getItem("access_token")
  if (!token) {
    return null
  }
  const parts = token.split(".")
  if (parts.length < 2) {
    return null
  }
  const base64Url = parts[1]
  const padding = "=".repeat((4 - (base64Url.length % 4)) % 4)
  try {
    const payload = JSON.parse(
      atob(`${base64Url}${padding}`.replace(/-/g, "+").replace(/_/g, "/")),
    ) as { role?: string }
    return payload.role ?? null
  } catch {
    return null
  }
}

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
  const role = getRoleFromAccessToken()
  const canAccess = role === "support" || role === "ops"

  const [targetUserId, setTargetUserId] = useState(1)
  const [title, setTitle] = useState("Incident support")
  const [description, setDescription] = useState("Description de l incident.")
  const [category, setCategory] = useState<"account" | "subscription" | "content">("account")
  const [priority, setPriority] = useState<"low" | "medium" | "high">("medium")

  const supportContext = useSupportContext(targetUserId, canAccess)
  const incidents = useSupportIncidents({ user_id: targetUserId }, canAccess)
  const createIncident = useCreateSupportIncident()
  const updateIncident = useUpdateSupportIncident()

  const createError = createIncident.error as SupportApiError | null
  const updateError = updateIncident.error as SupportApiError | null

  const orderedIncidents = useMemo(() => incidents.data?.incidents ?? [], [incidents.data?.incidents])

  if (!canAccess) {
    return null
  }

  return (
    <section className="panel">
      <h2>Support et operations</h2>
      <p>Consultez le dossier utilisateur et gerez les incidents.</p>

      <label htmlFor="support-target-user">Utilisateur cible</label>
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

      {supportContext.isLoading ? <p aria-busy="true">Chargement contexte support...</p> : null}
      {supportContext.error ? (
        <p role="alert">Erreur contexte: {(supportContext.error as SupportApiError).message}</p>
      ) : null}
      {supportContext.data ? (
        <>
          <p>
            Compte: {supportContext.data.user.email} ({supportContext.data.user.role})
          </p>
          <p>
            Abonnement: {supportContext.data.subscription.status}
            {supportContext.data.subscription.plan
              ? ` · ${supportContext.data.subscription.plan.display_name}`
              : ""}
          </p>
          <p>Demandes RGPD: {supportContext.data.privacy_requests.length}</p>
          {supportContext.data.privacy_requests.length > 0 ? (
            <ul className="chat-list">
              {supportContext.data.privacy_requests.map((item) => (
                <li key={item.request_id} className="chat-item">
                  RGPD #{item.request_id} · {item.request_kind} · {item.status}
                </li>
              ))}
            </ul>
          ) : (
            <p>Aucune demande RGPD.</p>
          )}
          <h3>Audit recent</h3>
          {supportContext.data.audit_events.length > 0 ? (
            <ul className="chat-list">
              {supportContext.data.audit_events.map((event) => (
                <li key={event.event_id} className="chat-item">
                  Audit #{event.event_id} · {event.action} · {event.status}
                </li>
              ))}
            </ul>
          ) : (
            <p>Aucun evenement d audit recent.</p>
          )}
        </>
      ) : null}
      {!supportContext.isLoading && !supportContext.error && !supportContext.data ? (
        <p>Aucun dossier charge.</p>
      ) : null}

      <h3>Creer un incident</h3>
      <label htmlFor="support-category">Categorie</label>
      <select
        id="support-category"
        value={category}
        onChange={(event) => setCategory(event.target.value as "account" | "subscription" | "content")}
      >
        <option value="account">Compte</option>
        <option value="subscription">Abonnement</option>
        <option value="content">Contenu</option>
      </select>
      <label htmlFor="support-priority">Priorite</label>
      <select
        id="support-priority"
        value={priority}
        onChange={(event) => setPriority(event.target.value as "low" | "medium" | "high")}
      >
        <option value="low">Faible</option>
        <option value="medium">Moyenne</option>
        <option value="high">Haute</option>
      </select>
      <label htmlFor="support-title">Titre</label>
      <input id="support-title" value={title} onChange={(event) => setTitle(event.target.value)} />
      <label htmlFor="support-description">Description</label>
      <textarea
        id="support-description"
        value={description}
        onChange={(event) => setDescription(event.target.value)}
      />
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
      {createError ? <p role="alert">Erreur creation incident: {createError.message}</p> : null}

      <h3>Incidents</h3>
      {incidents.isLoading ? <p aria-busy="true">Chargement incidents...</p> : null}
      {incidents.error ? (
        <p role="alert">Erreur incidents: {(incidents.error as SupportApiError).message}</p>
      ) : null}
      {!incidents.isLoading && !incidents.error && orderedIncidents.length === 0 ? (
        <p>Aucun incident pour cet utilisateur.</p>
      ) : null}
      {orderedIncidents.length > 0 ? (
        <ul className="chat-list">
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
      {updateError ? <p role="alert">Erreur mise a jour incident: {updateError.message}</p> : null}
    </section>
  )
}
