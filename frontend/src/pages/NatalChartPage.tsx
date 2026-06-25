// Page thème natal: lancement unique du job Astral et reprise manuelle en cas d'échec.
import { useCallback, useEffect, useMemo, useState } from "react"
import { Link, useSearchParams } from "react-router-dom"
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
import { NatalAstralReading } from "../features/natal-chart/NatalAstralReading"
import { buildNatalInterpretationViewModel } from "../features/natal-chart/natalAstralReadingViewModel"
import { NatalChartGuide } from "../components/NatalChartGuide"
import { useAstrologyLabels } from "../i18n/astrology"
import { useEntitlementsSnapshot } from "../hooks/useEntitlementSnapshot"
import { hasUsableAccessToken, useAccessTokenSnapshot } from "../utils/authToken"
import "./NatalChartPage.css"

const ASTRAL_TERMINAL_ERROR_STATUSES = new Set(["failed", "safety_rejected", "cancelled", "expired"])
const PUBLIC_ASTRAL_JOB_ERROR_MESSAGE =
  "Le service Astral n'a pas pu produire votre thème natal pour le moment. Veuillez réessayer plus tard."
const NATAL_PAGE_CONTEXT =
  "Une synthèse structurée de vos marqueurs personnels, de leurs appuis et des tensions majeures de votre ciel de naissance."

/** Derive le plan Astral a partir du code de variante expose par l'entitlement. */
function resolvePlan(variantCode?: string | null): AstralPlan {
  if (variantCode?.includes("premium")) return "premium"
  if (variantCode?.includes("basic") || variantCode === "single_astrologer") return "basic"
  return "free"
}

function mergeAstralJobState(
  eventJob: AstralJobResponse | null,
  statusJob: AstralJobResponse | undefined,
  submittedJob: AstralJobResponse | undefined,
): AstralJobResponse | undefined {
  if (!eventJob) return statusJob ?? submittedJob
  return {
    ...(submittedJob ?? {}),
    ...(statusJob ?? {}),
    ...eventJob,
    result: eventJob.result ?? statusJob?.result ?? submittedJob?.result ?? null,
    error: eventJob.error ?? statusJob?.error ?? submittedJob?.error ?? null,
    token_usage: eventJob.token_usage ?? statusJob?.token_usage ?? submittedJob?.token_usage,
  }
}

export function NatalChartPage() {
  const accessToken = useAccessTokenSnapshot()
  const { lang } = useAstrologyLabels()
  const [searchParams, setSearchParams] = useSearchParams()
  const initialRunId = searchParams.get("runId")
  const hasValidSession = hasUsableAccessToken(accessToken)
  const entitlementsSnapshot = useEntitlementsSnapshot()
  const natalAccess = entitlementsSnapshot.data?.features.find(
    (feature) => feature.feature_code === "horoscope_daily",
  )
  const plan = useMemo(() => resolvePlan(natalAccess?.variant_code), [natalAccess?.variant_code])
  const [runId, setRunId] = useState<string | null>(initialRunId)
  const [eventJob, setEventJob] = useState<AstralJobResponse | null>(null)
  const submitJob = useSubmitAstralJob(accessToken)
  const jobStatus = useAstralJobStatus(accessToken, runId)
  const terminalJob = mergeAstralJobState(eventJob, jobStatus.data, submitJob.data)
  const natalReading = useMemo(
    () => buildNatalInterpretationViewModel(terminalJob, plan),
    [plan, terminalJob],
  )
  const isWorking =
    submitJob.isPending ||
    terminalJob?.status === "queued" ||
    terminalJob?.status === "running"

  async function startNatalJob() {
    const response = await submitJob.mutateAsync({
      product: "natal_full",
      plan,
      client_request_id: buildAstralClientRequestId("natal"),
      target_language_code: "fr",
      audience_level: plan === "premium" ? "expert" : "beginner",
    })
    setRunId(response.run_id)
    const nextParams = new URLSearchParams(searchParams)
    nextParams.set("runId", response.run_id)
    setSearchParams(nextParams, { replace: true })
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
        <span className="natal-page-header__meta">Thème natal Astral</span>
        <h1 className="natal-page-header__title">Votre thème natal</h1>
        <p className="natal-page-header__context">{NATAL_PAGE_CONTEXT}</p>
        {natalReading?.highlightFacts.length ? (
          <div className="natal-page-portrait" aria-label="Portrait astral">
            <div className="natal-page-portrait__copy">
              <div className="natal-page-portrait__head">
                <span className="natal-section-eyebrow">Portrait astral</span>
                <span className="natal-badge natal-badge--report-status">{natalReading.label}</span>
              </div>
              <p>{natalReading.shortText ?? NATAL_PAGE_CONTEXT}</p>
            </div>
            <div className="natal-page-portrait__facts" aria-label="Marqueurs clés du portrait astral">
              {natalReading.highlightFacts.map((fact) => (
                <span
                  className="natal-page-portrait__fact natal-badge natal-badge--astro-data"
                  key={`${fact.label}-${fact.value}-${fact.detail ?? ""}`}
                >
                  <span className="natal-page-portrait__label">{fact.label}</span>
                  <strong>{fact.value}</strong>
                  {fact.detail ? <span className="natal-page-portrait__detail">{fact.detail}</span> : null}
                </span>
              ))}
            </div>
          </div>
        ) : null}
      </header>

      <div className="natal-card">
        {submitJob.isError || jobStatus.isError ? (
          <div className="chat-error natal-card__error" role="alert">
            <p>Le calcul Astral n'a pas pu être lancé ou récupéré.</p>
            <Link to="/profile" className="btn-link natal-card__secondary-link">
              Vérifier mon profil de naissance
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
            {natalReading ? (
              <NatalAstralReading reading={natalReading} showSummary={natalReading.highlightFacts.length === 0} />
            ) : (
              <p className="natal-card__lead">La lecture est indisponible pour ce job Astral.</p>
            )}
          </>
        ) : terminalJob?.status && ASTRAL_TERMINAL_ERROR_STATUSES.has(terminalJob.status) ? (
          <div className="chat-error natal-card__error" role="alert">
            <p>{PUBLIC_ASTRAL_JOB_ERROR_MESSAGE}</p>
            <button
              type="button"
              className="ni-action-btn ni-action-btn--regenerate"
              onClick={requestNatalJob}
              disabled={!hasValidSession || submitJob.isPending}
            >
              Relancer le thème natal
            </button>
            <Link to="/profile" className="btn-link natal-card__secondary-link">
              Vérifier mon profil de naissance
            </Link>
          </div>
        ) : (
          <button
            type="button"
            className="ni-action-btn ni-action-btn--regenerate"
            onClick={requestNatalJob}
            disabled={!hasValidSession}
          >
            Lancer le thème natal
          </button>
        )}
      </div>

      <NatalChartGuide lang={lang} missingBirthTime={Boolean(natalReading?.isPartial)} />
    </PageLayout>
  )
}
