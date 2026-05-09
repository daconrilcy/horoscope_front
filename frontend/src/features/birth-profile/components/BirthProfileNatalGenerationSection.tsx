// Isole la section de generation natale pour garder la route de profil compacte.
import type React from "react"

import { Button } from "@ui/Button"

type BirthProfileLoadStateProps = {
  isLoading: boolean
  isError: boolean
  loadingLabel: string
  errorLabel: string
  retryLabel: string
  onRetry: () => void
}

type BirthProfileNatalGenerationSectionProps = {
  title: string
  error: string | null
  isPending: boolean
  buttonLabel: string
  onGenerate: () => void
}

type BirthProfileCurrentLocationSectionProps = {
  title: string
  help: string
  consentLabel: string
  consentInput: React.ReactNode
  geolocationConsent: boolean
  currentLocationLabel: string | null
  currentLocationState: "idle" | "detecting" | "resolving" | "success" | "error"
  currentLocationError: string | null
  locationDetectedLabel: string
  noLocationLabel: string
  detectingLabel: string
  detectNowLabel: string
  locationFailedLabel: string
  manualLocationHelp: string
  manualCityField: React.ReactNode
  manualCountryField: React.ReactNode
  onDetectLocation: () => void
}

type BirthProfileGeocodingStatusProps = {
  state: "idle" | "loading" | "success" | "error_not_found" | "error_unavailable"
  successLabel: string
  loadingLabel: string
  notFoundLabel: string
  unavailableLabel: string
  resolvedGeoLabel: string | null
}

/** Rend les etats de chargement et d'erreur du profil de naissance. */
export function BirthProfileLoadState({
  isLoading,
  isError,
  loadingLabel,
  errorLabel,
  retryLabel,
  onRetry,
}: BirthProfileLoadStateProps) {
  if (isLoading) {
    return (
      <p className="app-state" aria-busy="true" role="status">
        <span className="app-spinner" aria-hidden="true" />
        {loadingLabel}
      </p>
    )
  }

  if (isError) {
    return (
      <div className="chat-error" role="alert">
        <p>{errorLabel}</p>
        <button type="button" onClick={onRetry} className="retry-button">
          {retryLabel}
        </button>
      </div>
    )
  }

  return null
}

/** Rend le feedback de geocodage du lieu de naissance. */
export function BirthProfileGeocodingStatus({
  state,
  successLabel,
  loadingLabel,
  notFoundLabel,
  unavailableLabel,
  resolvedGeoLabel,
}: BirthProfileGeocodingStatusProps) {
  return (
    <div aria-live="polite" aria-atomic="true">
      {state === "loading" && (
        <p className="app-state" aria-busy="true" role="status">
          <span className="app-spinner" aria-hidden="true" />
          {loadingLabel}
        </p>
      )}
      {state === "success" && resolvedGeoLabel !== null && (
        <p className="app-state app-state--success" role="status">
          ✓ {successLabel} : {resolvedGeoLabel}
        </p>
      )}
      {state === "error_not_found" && (
        <div className="chat-error degraded-warning" role="alert">
          <p>{notFoundLabel}</p>
        </div>
      )}
      {state === "error_unavailable" && (
        <div className="chat-error degraded-warning" role="alert">
          <p>{unavailableLabel}</p>
        </div>
      )}
    </div>
  )
}

/** Rend la section de localisation actuelle en deleguant les champs au formulaire parent. */
export function BirthProfileCurrentLocationSection({
  title,
  help,
  consentLabel,
  consentInput,
  geolocationConsent,
  currentLocationLabel,
  currentLocationState,
  currentLocationError,
  locationDetectedLabel,
  noLocationLabel,
  detectingLabel,
  detectNowLabel,
  locationFailedLabel,
  manualLocationHelp,
  manualCityField,
  manualCountryField,
  onDetectLocation,
}: BirthProfileCurrentLocationSectionProps) {
  const isDetecting = currentLocationState === "detecting" || currentLocationState === "resolving"

  return (
    <div className="app-section-divider">
      <h3 id="current-location-title">{title}</h3>
      <p className="help-text">{help}</p>

      <div className="consent-field">
        <label htmlFor="geolocation-consent" className="consent-label">
          {consentInput}
          {consentLabel}
        </label>
      </div>

      {geolocationConsent && (
        <div className="current-location-controls">
          {currentLocationLabel ? (
            <p className="app-state app-state--success">
              ✓ {locationDetectedLabel} : {currentLocationLabel}
            </p>
          ) : (
            <p className="app-state">{noLocationLabel}</p>
          )}

          <button type="button" onClick={onDetectLocation} disabled={isDetecting} className="secondary-button">
            {isDetecting ? (
              <span className="app-state">
                <span className="app-spinner" aria-hidden="true" />
                {detectingLabel}
              </span>
            ) : (
              detectNowLabel
            )}
          </button>

          {currentLocationState === "error" && (
            <p className="chat-error">{currentLocationError ?? locationFailedLabel}</p>
          )}
        </div>
      )}

      {(!geolocationConsent || currentLocationState === "error") && (
        <div className="current-location-controls">
          <p className="help-text">{manualLocationHelp}</p>
          <div className="birth-location-row">
            <div className="birth-location-field">{manualCityField}</div>
            <div className="birth-location-field">{manualCountryField}</div>
          </div>
        </div>
      )}
    </div>
  )
}

/** Rend le CTA de generation natale sans posseder la mutation API. */
export function BirthProfileNatalGenerationSection({
  title,
  error,
  isPending,
  buttonLabel,
  onGenerate,
}: BirthProfileNatalGenerationSectionProps) {
  return (
    <div className="app-section-divider" aria-labelledby="natal-generation-title">
      <h3 id="natal-generation-title">{title}</h3>
      {error && (
        <div className="chat-error" role="alert">
          <p>{error}</p>
        </div>
      )}
      <Button type="button" loading={isPending} onClick={onGenerate}>
        {buttonLabel}
      </Button>
    </div>
  )
}
