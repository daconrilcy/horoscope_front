// Rendu des états du job Astral natal sans orchestration API.
import { Link } from "react-router-dom"
import { RefreshCw } from "lucide-react"

import type { AstralJobResponse } from "../../api/astral"
import type { NatalChartPageCopy } from "../../i18n/natalChart"
import { NatalAstralReading } from "./NatalAstralReading"
import type { NatalInterpretationViewModel } from "./natalAstralReadingViewModel"
import type { NatalJobViewState } from "./natalJobViewState"
import "./NatalJobCard.css"

type NatalJobCardProps = {
  viewState: NatalJobViewState
  currentJob: AstralJobResponse | undefined
  reading: NatalInterpretationViewModel | null
  copy: NatalChartPageCopy
  canStart: boolean
  canRetry: boolean
  onStart: () => void
  onRetry: () => void
}

/** Affiche les états utilisateur du job Astral natal. */
export function NatalJobCard({
  viewState,
  currentJob,
  reading,
  copy,
  canStart,
  canRetry,
  onStart,
  onRetry,
}: NatalJobCardProps) {
  return (
    <div className="natal-card">
      {viewState === "transport-error" ? (
        <div className="natal-card__error" role="alert">
          <p>{copy.jobLaunchError}</p>
          <Link to="/profile" className="btn-link natal-card__secondary-link">
            {copy.profileLink}
          </Link>
        </div>
      ) : null}

      {viewState === "working" ? (
        <div className="natal-card__status" role="status" aria-live="polite" aria-busy="true">
          <RefreshCw size={32} className="natal-card__spinner" />
          <p className="natal-card__lead">
            {copy.jobLoading}{" "}
            <span className="natal-card__status-detail">
              {copy.jobStatusLabel}: {currentJob?.status ?? "queued"}.
            </span>
          </p>
        </div>
      ) : null}

      {viewState === "completed" ? (
        <>
          {reading ? (
            <NatalAstralReading reading={reading} />
          ) : (
            <p className="natal-card__lead">{copy.readingUnavailable}</p>
          )}
        </>
      ) : null}

      {viewState === "terminal-error" ? (
        <div className="natal-card__error" role="alert">
          <p>{copy.jobError}</p>
          <button
            type="button"
            className="natal-card__action natal-card__action--primary"
            onClick={() => {
              onRetry()
            }}
            disabled={!canRetry}
          >
            {copy.retryButton}
          </button>
          <Link to="/profile" className="btn-link natal-card__secondary-link">
            {copy.profileLink}
          </Link>
        </div>
      ) : null}

      {viewState === "idle" ? (
        <button
          type="button"
          className="natal-card__action natal-card__action--primary"
          onClick={() => {
            onStart()
          }}
          disabled={!canStart}
        >
          {copy.startButton}
        </button>
      ) : null}
    </div>
  )
}
