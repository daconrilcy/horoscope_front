// Page theme natal: lancement unique du job Astral et reprise manuelle en cas d'echec.
import { useCallback, useEffect, useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { RefreshCw } from "lucide-react"

import { PageLayout } from "../layouts"
import {
  buildAstralClientRequestId,
  type AstralJobEvent,
  type AstralJobResponse,
  type AstralPlan,
  useAstralJobEvents,
  useAstralJobStatus,
  useSubmitAstralJob,
} from "../api/astral"
import { useEntitlementsSnapshot } from "../hooks/useEntitlementSnapshot"
import { hasUsableAccessToken, useAccessTokenSnapshot } from "../utils/authToken"
import "./NatalChartPage.css"

/** Derive le plan Astral a partir du code de variante expose par l'entitlement. */
function resolvePlan(variantCode?: string | null): AstralPlan {
  if (variantCode?.includes("premium")) return "premium"
  if (variantCode?.includes("basic") || variantCode === "single_astrologer") return "basic"
  return "free"
}

/** Rend le resultat Astral en texte simple ou en JSON selon la forme du payload. */
function renderReading(job: AstralJobResponse | undefined) {
  const result = job?.result
  if (!result) return null
  if (typeof result.reading === "string") {
    return <p className="natal-card__lead">{result.reading}</p>
  }
  return (
    <pre className="natal-card__json" aria-label="Resultat Astral">
      {JSON.stringify(result.reading ?? result, null, 2)}
    </pre>
  )
}

export function NatalChartPage() {
  const accessToken = useAccessTokenSnapshot()
  const hasValidSession = hasUsableAccessToken(accessToken)
  const entitlementsSnapshot = useEntitlementsSnapshot()
  const natalAccess = entitlementsSnapshot.data?.features.find(
    (feature) => feature.feature_code === "horoscope_daily",
  )
  const plan = useMemo(() => resolvePlan(natalAccess?.variant_code), [natalAccess?.variant_code])
  const [runId, setRunId] = useState<string | null>(null)
  const [eventJob, setEventJob] = useState<AstralJobResponse | null>(null)
  const submitJob = useSubmitAstralJob(accessToken)
  const jobStatus = useAstralJobStatus(accessToken, runId)
  const terminalJob = eventJob ?? jobStatus.data ?? submitJob.data
  const isWorking =
    submitJob.isPending ||
    terminalJob?.status === "queued" ||
    terminalJob?.status === "running"

  async function startNatalJob() {
    const response = await submitJob.mutateAsync({
      product: plan === "free" ? "natal_simplified" : "natal_full",
      plan,
      client_request_id: buildAstralClientRequestId("natal"),
      target_language_code: "fr",
      audience_level: plan === "premium" ? "advanced" : "beginner",
    })
    setRunId(response.run_id)
  }

  function requestNatalJob() {
    void startNatalJob().catch(() => undefined)
  }

  useEffect(() => {
    setEventJob(null)
  }, [runId])

  const handleAstralEvent = useCallback(
    (event: AstralJobEvent) => {
      if (typeof event.status !== "string") return
      if (typeof event.run_id === "string" && event.run_id !== runId) return
      setEventJob((previous) => ({
        ...(previous ?? jobStatus.data ?? submitJob.data ?? { run_id: runId ?? "", status: "queued" }),
        ...event,
      }))
    },
    [jobStatus.data, runId, submitJob.data],
  )

  useAstralJobEvents(accessToken, runId, handleAstralEvent)

  return (
    <PageLayout className="natal-page-container is-natal-page">
      <div className="natal-page-container__bg-halo" />
      <div className="natal-page-container__noise" />
      <header className="natal-page-header">
        <span className="natal-page-header__meta">Theme natal Astral</span>
        <h1 className="natal-page-header__title">Votre theme natal</h1>
      </header>

      <div className="natal-card">
        {submitJob.isError || jobStatus.isError ? (
          <div className="chat-error natal-card__error" role="alert">
            <p>Le calcul Astral n'a pas pu etre lance ou recupere.</p>
            <Link to="/profile" className="btn-link natal-card__secondary-link">
              Verifier mon profil de naissance
            </Link>
          </div>
        ) : isWorking ? (
          <div className="ni-loader-container" role="status" aria-live="polite" aria-busy="true">
            <RefreshCw size={32} className="ni-loader-spin" />
            <p className="natal-card__lead">
              Calcul externalise en cours via Astral. Statut: {terminalJob?.status ?? "queued"}.
            </p>
          </div>
        ) : terminalJob?.status === "completed" ? (
          <>
            <p className="natal-card__lead">Resultat Astral pret.</p>
            {renderReading(terminalJob)}
          </>
        ) : terminalJob?.status === "failed" ? (
          <div className="chat-error natal-card__error" role="alert">
            <p>Le job Astral a echoue.</p>
          </div>
        ) : (
          <button
            type="button"
            className="ni-action-btn ni-action-btn--regenerate"
            onClick={requestNatalJob}
            disabled={!hasValidSession}
          >
            Lancer le theme natal
          </button>
        )}
      </div>
    </PageLayout>
  )
}
