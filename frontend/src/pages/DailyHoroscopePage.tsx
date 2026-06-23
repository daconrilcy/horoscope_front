import { useCallback, useEffect, useMemo, useState } from "react"
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
import { useAccessTokenSnapshot } from "../utils/authToken"
import { useFeatureAccess } from "../hooks/useEntitlementSnapshot"
import "./DailyHoroscopePage.css"

function resolvePlan(variantCode?: string | null): AstralPlan {
  if (variantCode?.includes("premium")) return "premium"
  if (variantCode?.includes("basic")) return "basic"
  return "free"
}

function renderAstralResult(job: AstralJobResponse | undefined) {
  const result = job?.result
  if (!result) return null
  if (typeof result.reading === "string") {
    return <p className="daily-page-state__lead">{result.reading}</p>
  }
  return (
    <pre className="daily-page-state__json" aria-label="Resultat horoscope Astral">
      {JSON.stringify(result.reading ?? result, null, 2)}
    </pre>
  )
}

export default function DailyHoroscopePage() {
  const accessToken = useAccessTokenSnapshot()
  const featureAccess = useFeatureAccess("horoscope_daily")
  const plan = useMemo(() => resolvePlan(featureAccess?.variant_code), [featureAccess?.variant_code])
  const [runId, setRunId] = useState<string | null>(null)
  const [eventJob, setEventJob] = useState<AstralJobResponse | null>(null)
  const submitJob = useSubmitAstralJob(accessToken)
  const jobStatus = useAstralJobStatus(accessToken, runId)
  const job = eventJob ?? jobStatus.data ?? submitJob.data
  const isWorking = submitJob.isPending || job?.status === "queued" || job?.status === "running"

  async function startDailyJob() {
    const response = await submitJob.mutateAsync({
      product: "horoscope_daily",
      plan,
      period: "daily",
      client_request_id: buildAstralClientRequestId("daily"),
      target_language_code: "fr",
      audience_level: plan === "premium" ? "advanced" : "beginner",
    })
    setRunId(response.run_id)
  }

  function requestDailyJob() {
    void startDailyJob().catch(() => undefined)
  }

  useEffect(() => {
    if (!accessToken || runId || submitJob.isPending || submitJob.data) return
    requestDailyJob()
    // Le demarrage automatique doit rester lie au token et au plan courant.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [accessToken, plan, runId, submitJob.data, submitJob.isPending])

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
    <PageLayout>
      <div className="daily-layout">
        <div className="daily-layout__bg-halo-3" />
        <div className="daily-layout__noise" />
        <header className="daily-page-header">
          <p className="daily-page-header__kicker">Horoscope Astral</p>
          <h1 className="daily-page-header__title">Votre horoscope du jour</h1>
        </header>

        <div className="app-panel daily-page-state">
          {submitJob.isError || jobStatus.isError ? (
            <>
              <p>Le job Astral n'a pas pu etre lance ou recupere.</p>
              <button type="button" onClick={requestDailyJob}>
                Reessayer
              </button>
            </>
          ) : isWorking ? (
            <div role="status" aria-live="polite" aria-busy="true">
              <RefreshCw size={28} className="ni-loader-spin" />
              <p>Calcul externalise en cours. Statut: {job?.status ?? "queued"}.</p>
            </div>
          ) : job?.status === "completed" ? (
            <>
              <p className="daily-page-state__lead">Resultat Astral pret.</p>
              {renderAstralResult(job)}
            </>
          ) : job?.status === "failed" ? (
            <p>Le job Astral a echoue.</p>
          ) : (
            <button type="button" onClick={requestDailyJob} disabled={!accessToken}>
              Lancer l'horoscope
            </button>
          )}
        </div>
      </div>
    </PageLayout>
  )
}
