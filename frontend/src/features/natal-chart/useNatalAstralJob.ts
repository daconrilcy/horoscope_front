// Orchestration du job Astral natal et projection de lecture pour la page thème natal.
import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { useSearchParams } from "react-router-dom"

import {
  type AstralJobEvent,
  type AstralJobResponse,
  useAstralJobEvents,
  useAstralJobStatus,
  useSubmitAstralJob,
} from "../../api/astral"
import { useBirthData } from "../../api/useBirthData"
import { useEntitlementsSnapshot } from "../../hooks/useEntitlementSnapshot"
import { hasUsableAccessToken, useAccessTokenSnapshot } from "../../utils/authToken"
import {
  NATAL_ENTITLEMENT_FEATURE_CODE,
  buildNatalAstralJobRequest,
  resolveNatalAstralPlan,
} from "./natalAstralJobConfig"
import {
  buildNatalInterpretationViewModel,
  type NatalInterpretationViewModel,
} from "./natalAstralReadingViewModel"

/** Fusionne les sources Astral en conservant les champs omis par les événements partiels. */
export function mergeCurrentAstralJobState(
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

export type UseNatalAstralJobResult = {
  currentJob: AstralJobResponse | undefined
  natalReading: NatalInterpretationViewModel | null
  isWorking: boolean
  hasTransportError: boolean
  hasValidSession: boolean
  canStart: boolean
  canRetry: boolean
  startJob: () => void
}

/** Fournit l'état complet du job Astral natal sans exposer l'orchestration à la page. */
export function useNatalAstralJob(): UseNatalAstralJobResult {
  const accessToken = useAccessTokenSnapshot()
  const [searchParams, setSearchParams] = useSearchParams()
  const initialRunId = searchParams.get("runId")
  const hasValidSession = hasUsableAccessToken(accessToken)
  const entitlementsSnapshot = useEntitlementsSnapshot()
  const birthDataSnapshot = useBirthData(accessToken)
  const natalAccess = entitlementsSnapshot.data?.features.find(
    (feature) => feature.feature_code === NATAL_ENTITLEMENT_FEATURE_CODE,
  )
  const plan = useMemo(
    () => resolveNatalAstralPlan(natalAccess?.variant_code),
    [natalAccess?.variant_code],
  )
  const [runId, setRunId] = useState<string | null>(initialRunId)
  const [eventJob, setEventJob] = useState<AstralJobResponse | null>(null)
  const startInFlightRef = useRef(false)
  const submitJob = useSubmitAstralJob(accessToken)
  const jobStatus = useAstralJobStatus(accessToken, runId)
  const currentJob = mergeCurrentAstralJobState(eventJob, jobStatus.data, submitJob.data)
  const natalReading = useMemo(
    () => buildNatalInterpretationViewModel(currentJob, plan, birthDataSnapshot.data ?? null),
    [birthDataSnapshot.data, currentJob, plan],
  )
  const isWorking =
    submitJob.isPending ||
    currentJob?.status === "queued" ||
    currentJob?.status === "running"
  const hasTransportError = submitJob.isError || jobStatus.isError
  const canStart = hasValidSession && !submitJob.isPending && !isWorking
  const canRetry = canStart

  const startJob = useCallback(() => {
    if (!hasValidSession || submitJob.isPending || isWorking || startInFlightRef.current) return
    startInFlightRef.current = true
    submitJob.mutate(buildNatalAstralJobRequest({ plan }), {
      onSuccess: (response) => {
        setRunId(response.run_id)
        const nextParams = new URLSearchParams(searchParams)
        nextParams.set("runId", response.run_id)
        setSearchParams(nextParams, { replace: true })
      },
      onSettled: () => {
        startInFlightRef.current = false
      },
    })
  }, [hasValidSession, isWorking, plan, searchParams, setSearchParams, submitJob])

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

  return {
    currentJob,
    natalReading,
    isWorking,
    hasTransportError,
    hasValidSession,
    canStart,
    canRetry,
    startJob,
  }
}
