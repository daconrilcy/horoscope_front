import { PageLayout } from "../layouts"
import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import { Field } from "@ui/Field"
import { Button } from "@ui/Button"

import { getBirthData, saveBirthData, BirthProfileApiError, type BirthProfileData } from "@api"
import { generateNatalChart, ApiError, type LatestNatalChart } from "@api"
import { geocodeCity, GeocodingError, reverseGeocode } from "../api/geocoding"
import { useAccessTokenSnapshot, getSubjectFromAccessToken } from "../utils/authToken"
import { ANONYMOUS_SUBJECT, GENERATION_TIMEOUT_LABEL, logSupportRequestId, formatBirthPlace } from "../utils/constants"
import { TimezoneSelect } from "../components/TimezoneSelect"
import { getUserTimezone } from "../data/timezones"
import { detectLang, GEOCODING_MESSAGES } from "../i18n/astrology"
import { birthProfileTranslations, type BirthProfileValidation } from "../i18n/birthProfile"
import "./BirthProfilePage.css"

function createBirthProfileSchema(v: BirthProfileValidation) {
  return z.object({
    birth_date: z
      .string()
      .min(1, v.dateRequired)
      .regex(/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/, v.dateFormat)
      .refine((val) => {
        const date = new Date(val)
        return !isNaN(date.getTime()) && date.toISOString().startsWith(val)
      }, v.dateInvalid)
      .refine((val) => {
        const date = new Date(val)
        return date <= new Date()
      }, v.dateFuture),
    birth_time: z
      .string()
      .regex(/^([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$/, v.timeFormat)
      .or(z.literal("")),
    birth_place: z.string().trim().max(255).optional(),
    birth_timezone: z
      .string()
      .trim()
      .min(1, v.timezoneRequired)
      .regex(/^[A-Za-z][A-Za-z0-9_+-]*(\/[A-Za-z0-9][A-Za-z0-9_+-]*)+$|^UTC$/, v.timezoneFormat)
      .max(64),
    birth_city: z.string().trim().min(1, v.cityRequired).max(255),
    birth_country: z.string().trim().min(1, v.countryRequired).max(100),
    geolocation_consent: z.boolean(),
    current_city: z.string().trim().max(255).optional(),
    current_country: z.string().trim().max(100).optional(),
  })
}

type BirthProfileFormData = z.infer<ReturnType<typeof createBirthProfileSchema>>

type GeocodingState = "idle" | "loading" | "success" | "error_not_found" | "error_unavailable"
type CurrentLocationState = "idle" | "detecting" | "resolving" | "success" | "error"

type GeoResult = {
  place_resolved_id: number
  lat: number
  lon: number
  display_name: string
  timezone_iana?: string | null
} | null

function shouldLogSupportForApiError(error: { status: number }): boolean {
  return error.status >= 500
}

function inferCityCountryFromBirthPlace(
  birthPlace: string | undefined,
): { city: string; country: string } {
  if (!birthPlace) return { city: "", country: "" }
  const chunks = birthPlace
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
  if (chunks.length === 0) return { city: "", country: "" }
  if (chunks.length === 1) return { city: chunks[0], country: "" }
  return {
    city: chunks[0],
    country: chunks[chunks.length - 1],
  }
}

export function BirthProfilePage() {
  const lang = detectLang()
  const t = birthProfileTranslations[lang]
  const queryClient = useQueryClient()
  const accessToken = useAccessTokenSnapshot()
  const navigate = useNavigate()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? ANONYMOUS_SUBJECT
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [globalError, setGlobalError] = useState<string | null>(null)
  const [generationError, setGenerationError] = useState<string | null>(null)
  const [geocodingState, setGeocodingState] = useState<GeocodingState>("idle")
  const [resolvedGeoLabel, setResolvedGeoLabel] = useState<string | null>(null)
  const geocodeAbortRef = useRef<AbortController | null>(null)
  const autoLocationRefreshAttemptedRef = useRef(false)
  const [birthTimeUnknown, setBirthTimeUnknown] = useState(false)
  
  // Story 30.19: Current location states
  const [currentLocationState, setCurrentLocationState] = useState<CurrentLocationState>("idle")
  const [currentLocationLabel, setCurrentLocationLabel] = useState<string | null>(null)
  const [currentLocationError, setCurrentLocationError] = useState<string | null>(null)

  const schema = useMemo(
    () => createBirthProfileSchema(birthProfileTranslations[lang].validation),
    [lang],
  )

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["birth-profile", tokenSubject],
    queryFn: () => {
      if (!accessToken) throw new Error("No access token available")
      return getBirthData(accessToken)
    },
    enabled: Boolean(accessToken),
    staleTime: 1000 * 60 * 5, // 5 minutes
  })

  const generationMutation = useMutation<LatestNatalChart, Error | ApiError>({
    mutationFn: async () => {
      if (!accessToken) throw new Error("No access token available")
      return generateNatalChart(accessToken, true)
    },
    onSuccess: () => {
      // Le POST /natal-chart ne contient pas toujours les champs enrichis
      // (created_at, astro_profile) retournés par /natal-chart/latest.
      // On purge donc la cache pour forcer un fetch frais sur la page /natal.
      queryClient.removeQueries({ queryKey: ["latest-natal-chart", tokenSubject], exact: true })
      navigate("/natal")
    },
    onError: (err) => {
      if (err instanceof ApiError && shouldLogSupportForApiError(err)) {
        logSupportRequestId(err)
      }

      const code = err instanceof ApiError ? err.code : undefined
      const status = err instanceof ApiError ? err.status : undefined
      if (code === "natal_generation_timeout") {
        setGenerationError(t.errors.generationTimeout)
      } else if (code === "natal_engine_unavailable") {
        setGenerationError(t.errors.generationUnavailable)
      } else if (code === "unprocessable_entity" || status === 422) {
        setGenerationError(t.errors.generationInvalidData)
      } else {
        setGenerationError(t.errors.generationGeneric)
      }
    },
  })

  const {
    register,
    handleSubmit,
    reset,
    setError,
    setValue,
    control,
    watch,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<BirthProfileFormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      birth_timezone: getUserTimezone(),
      geolocation_consent: false,
      current_city: "",
      current_country: "",
    },
  })

  const geolocationConsent = watch("geolocation_consent")

  useEffect(() => {
    return () => { geocodeAbortRef.current?.abort() }
  }, [])

  useEffect(() => {
    autoLocationRefreshAttemptedRef.current = false
  }, [tokenSubject])

  useEffect(() => {
    if (!geolocationConsent && currentLocationState !== "error") {
      setCurrentLocationState("idle")
      setCurrentLocationError(null)
    }
  }, [currentLocationState, geolocationConsent])

  /**
   * Synchronise le formulaire avec les données du profil API.
   */
  const syncFormWithProfileData = useCallback(
    (profileData: BirthProfileData) => {
      const isTimeUnknown = profileData.birth_time === null
      const inferred = inferCityCountryFromBirthPlace(profileData.birth_place)
      reset({
        birth_date: profileData.birth_date,
        birth_time: isTimeUnknown ? "" : (profileData.birth_time ?? ""),
        birth_place: profileData.birth_place ?? "",
        birth_timezone: profileData.birth_timezone || getUserTimezone(),
        birth_city: profileData.birth_city ?? inferred.city,
        birth_country: profileData.birth_country ?? inferred.country,
        geolocation_consent: profileData.geolocation_consent ?? false,
        current_city: profileData.current_city ?? "",
        current_country: profileData.current_country ?? "",
      })
      setBirthTimeUnknown(isTimeUnknown)
      if (profileData.current_location_display) {
        setCurrentLocationLabel(
          profileData.current_timezone
            ? `${profileData.current_location_display} (${profileData.current_timezone})`
            : profileData.current_location_display,
        )
        setCurrentLocationState("success")
      } else {
        setCurrentLocationLabel(null)
        setCurrentLocationState("idle")
      }
      setCurrentLocationError(null)
    },
    [reset],
  )

  useEffect(() => {
    if (data && !isSubmitting && !isDirty) {
      syncFormWithProfileData(data)
    }
  }, [data, syncFormWithProfileData, isSubmitting, isDirty])

  useEffect(() => {
    if (isError && error instanceof BirthProfileApiError && shouldLogSupportForApiError(error)) {
      logSupportRequestId(error)
    }
  }, [isError, error])

  function resetGeocodingState() {
    setGeocodingState("idle")
    setResolvedGeoLabel(null)
  }

  /** Réinitialise tous les états de feedback utilisateur (succès, erreurs globales et erreurs de génération) */
  function clearFormFeedback() {
    setSaveSuccess(false)
    setGlobalError(null)
    setGenerationError(null)
  }

  /**
   * Exécute le géocodage avec gestion d'annulation.
   */
  async function performGeocode(city: string, country: string): Promise<{ result: GeoResult; isServiceUnavailable: boolean }> {
    if (!city || !country) return { result: null, isServiceUnavailable: false }

    const controller = new AbortController()
    geocodeAbortRef.current = controller

    try {
      const result = await geocodeCity(city, country, controller.signal)
      return { result, isServiceUnavailable: false }
    } catch (err) {
      return { result: null, isServiceUnavailable: err instanceof GeocodingError }
    }
  }

  async function resolveCurrentLocation(
    city: string,
    country: string,
  ): Promise<{
    current_city: string | null
    current_country: string | null
    current_lat: number | null
    current_lon: number | null
    current_location_display: string | null
    current_timezone: string | null
  }> {
    const trimmedCity = city.trim()
    const trimmedCountry = country.trim()
    if (!trimmedCity || !trimmedCountry || !accessToken) {
      return {
        current_city: null,
        current_country: null,
        current_lat: null,
        current_lon: null,
        current_location_display: null,
        current_timezone: null,
      }
    }

    const { result, isServiceUnavailable } = await performGeocode(trimmedCity, trimmedCountry)
    if (result === null) {
      throw new GeocodingError(
        "Current location could not be resolved",
        isServiceUnavailable ? "service_unavailable" : "not_found",
      )
    }

    // Si le forward geocoding a résolu la timezone, on l'utilise directement.
    // Sinon, on tente un reverse geocoding pour l'obtenir (fallback).
    if (result.timezone_iana) {
      return {
        current_city: trimmedCity,
        current_country: trimmedCountry,
        current_lat: result.lat,
        current_lon: result.lon,
        current_location_display: result.display_name,
        current_timezone: result.timezone_iana,
      }
    }

    const reverseResult = await reverseGeocode(result.lat, result.lon, accessToken, lang)
    return {
      current_city: reverseResult.city ?? trimmedCity,
      current_country: reverseResult.country ?? trimmedCountry,
      current_lat: reverseResult.lat,
      current_lon: reverseResult.lon,
      current_location_display: reverseResult.display_name,
      current_timezone: reverseResult.timezone_iana,
    }
  }

  async function persistDetectedCurrentLocation(
    profileData: BirthProfileData | null,
    latitude: number,
    longitude: number,
    result: Awaited<ReturnType<typeof reverseGeocode>>,
  ): Promise<void> {
    if (!accessToken || !profileData) {
      return
    }
    const updatedPayload: BirthProfileData = {
      ...profileData,
      geolocation_consent: true,
      current_lat: latitude,
      current_lon: longitude,
      current_city: result.city,
      current_country: result.country,
      current_location_display: result.display_name,
      current_timezone: result.timezone_iana,
    }
    const updated = await saveBirthData(accessToken, updatedPayload)
    queryClient.setQueryData(["birth-profile", tokenSubject], updated)
    syncFormWithProfileData(updated)
  }

  function applyDetectedCurrentLocation(
    result: Awaited<ReturnType<typeof reverseGeocode>>,
    options: { markDirty: boolean },
  ) {
    setCurrentLocationState("success")
    setCurrentLocationLabel(
      result.timezone_iana
        ? `${result.display_name} (${result.timezone_iana})`
        : result.display_name,
    )
    setCurrentLocationError(null)
    setValue("current_city", result.city ?? "", { shouldDirty: options.markDirty })
    setValue("current_country", result.country ?? "", { shouldDirty: options.markDirty })
  }

  function handleLocationFailure(options: {
    preserveSavedLocation: boolean
    message: string
  }) {
    if (options.preserveSavedLocation && currentLocationLabel) {
      setCurrentLocationState("success")
      setCurrentLocationError(null)
      return
    }
    setCurrentLocationState("error")
    setCurrentLocationError(options.message)
  }

  async function detectLocation(options: {
    markDirty: boolean
    preserveSavedLocationOnError: boolean
  }): Promise<void> {
    if (!accessToken) return
    if (!navigator.geolocation) {
      handleLocationFailure({
        preserveSavedLocation: options.preserveSavedLocationOnError,
        message: t.errors.geolocationUnavailable,
      })
      return
    }
    setCurrentLocationState("detecting")
    setCurrentLocationError(null)

    await new Promise<void>((resolve) => {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords
          setCurrentLocationState("resolving")

          try {
            const result = await reverseGeocode(latitude, longitude, accessToken, lang)
            applyDetectedCurrentLocation(result, { markDirty: options.markDirty })
            await persistDetectedCurrentLocation(data ?? null, latitude, longitude, result)
          } catch {
            handleLocationFailure({
              preserveSavedLocation: options.preserveSavedLocationOnError,
              message: t.errors.locationFailed,
            })
          } finally {
            resolve()
          }
        },
        (err) => {
          handleLocationFailure({
            preserveSavedLocation: options.preserveSavedLocationOnError,
            message:
              err.code === err.PERMISSION_DENIED
                ? t.errors.geolocationDenied
                : t.errors.locationFailed,
          })
          resolve()
        },
        { timeout: 10000, maximumAge: 300_000 }
      )
    })
  }

  const handleDetectLocation = () => {
    void detectLocation({
      markDirty: true,
      preserveSavedLocationOnError: false,
    })
  }

  useEffect(() => {
    if (!accessToken || !data || !data.geolocation_consent) {
      return
    }
    if (isSubmitting || isDirty || autoLocationRefreshAttemptedRef.current) {
      return
    }
    autoLocationRefreshAttemptedRef.current = true
    void detectLocation({
      markDirty: false,
      preserveSavedLocationOnError: Boolean(data.current_location_display),
    })
  }, [accessToken, data, isDirty, isSubmitting])

  async function onSubmit(formData: BirthProfileFormData) {
    if (!accessToken) return
    setSaveSuccess(false)
    setGlobalError(null)
    setGenerationError(null)
    resetGeocodingState()

    const city = formData.birth_city.trim()
    const country = formData.birth_country.trim()
    const currentCity = formData.current_city?.trim() ?? ""
    const currentCountry = formData.current_country?.trim() ?? ""

    setGeocodingState("loading")
    const { result: geoResult, isServiceUnavailable } = await performGeocode(city, country)

    let coords: { lat: number; lon: number } | null = null
    let resolvedPlaceId: number | null = null
    let resolvedPlace = formData.birth_place?.trim() || ""

    if (geoResult === null) {
      setGeocodingState(isServiceUnavailable ? "error_unavailable" : "error_not_found")
    } else {
      setGeocodingState("success")
      resolvedPlaceId = geoResult.place_resolved_id
      coords = { lat: geoResult.lat, lon: geoResult.lon }
      resolvedPlace = geoResult.display_name.slice(0, 255)
      setResolvedGeoLabel(geoResult.display_name)
    }

    try {
      let currentLocationPayload: Pick<
        BirthProfileData,
        | "current_city"
        | "current_country"
        | "current_lat"
        | "current_lon"
        | "current_location_display"
        | "current_timezone"
      >

      if (!formData.geolocation_consent) {
        if (currentCity && currentCountry) {
          currentLocationPayload = await resolveCurrentLocation(currentCity, currentCountry)
        } else {
          currentLocationPayload = {
            current_city: null,
            current_country: null,
            current_lat: null,
            current_lon: null,
            current_location_display: null,
            current_timezone: null,
          }
        }
      } else {
        currentLocationPayload = {
          current_city: data?.current_city ?? (currentCity || null),
          current_country: data?.current_country ?? (currentCountry || null),
          current_lat: data?.current_lat ?? null,
          current_lon: data?.current_lon ?? null,
          current_location_display: data?.current_location_display ?? null,
          current_timezone: data?.current_timezone ?? null,
        }
      }

      const payload: BirthProfileData = {
        ...formData,
        birth_time: (birthTimeUnknown || !formData.birth_time) ? null : formData.birth_time,
        birth_place: resolvedPlace || formatBirthPlace(city, country),
        birth_city: city,
        birth_country: country,
        ...(resolvedPlaceId !== null ? { place_resolved_id: resolvedPlaceId } : {}),
        ...(coords ? { birth_lat: coords.lat, birth_lon: coords.lon } : {}),
        current_city: currentLocationPayload.current_city,
        current_country: currentLocationPayload.current_country,
        current_lat: currentLocationPayload.current_lat,
        current_lon: currentLocationPayload.current_lon,
        current_location_display: currentLocationPayload.current_location_display,
        current_timezone: currentLocationPayload.current_timezone,
      }
      const updatedData = await saveBirthData(accessToken, payload)
      queryClient.setQueryData(["birth-profile", tokenSubject], updatedData)
      syncFormWithProfileData(updatedData)
      setSaveSuccess(true)
    } catch (err) {
      if (err instanceof GeocodingError) {
        setCurrentLocationError(t.errors.locationFailed)
        setGlobalError(t.errors.locationFailed)
      } else if (err instanceof BirthProfileApiError) {
        if (shouldLogSupportForApiError(err)) {
          logSupportRequestId(err)
        }
        if (err.code === "invalid_birth_time") {
          setError("birth_time", { message: err.message || t.validation.timeFormat })
        } else if (err.code === "invalid_timezone") {
          setError("birth_timezone", { message: err.message || t.validation.timezoneFormat })
        } else if (err.code === "invalid_birth_input") {
          setGlobalError(t.errors.saveInvalidData)
        } else {
          setGlobalError(err.message || t.errors.saveNetwork)
        }
      } else {
        setGlobalError(t.errors.saveNetwork)
      }
    }
  }

  return (
    <PageLayout className="panel">
      <h2 id="birth-profile-title">{t.title}</h2>

      {isLoading ? (
        <p className="state-line" aria-busy="true" role="status">
          <span className="state-loading" aria-hidden="true" />
          {t.loading}
        </p>
      ) : null}

      {isError && !isLoading ? (
        <div className="chat-error" role="alert">
          <p>{t.loadError}</p>
          <button type="button" onClick={() => void refetch()} className="retry-button">
            {t.retry}
          </button>
        </div>
      ) : null}

      {!isLoading && !isError ? (
        <form
          className="chat-form"
          onSubmit={handleSubmit(onSubmit)}
          onChange={clearFormFeedback}
          noValidate
          aria-labelledby="birth-profile-title"
        >
          <div className="section-header">
            <h3>{t.labels.birthInfo || "Informations de naissance"}</h3>
          </div>

          <Field
            id="birth-date"
            label={t.labels.birthDate}
            type="text"
            placeholder="1990-01-15"
            error={errors.birth_date?.message}
            {...register("birth_date")}
          />

          <div>
            <Field
              id="birth-time"
              label={t.labels.birthTime}
              type="text"
              placeholder="10:30"
              disabled={birthTimeUnknown}
              error={!birthTimeUnknown ? errors.birth_time?.message : undefined}
              {...register("birth_time")}
            />
            <label htmlFor="birth-time-unknown" className="birth-time-unknown-label">
              <input
                id="birth-time-unknown"
                type="checkbox"
                checked={birthTimeUnknown}
                onChange={(e) => {
                  const checked = e.target.checked
                  setBirthTimeUnknown(checked)
                  if (checked) setValue("birth_time", "", { shouldValidate: false })
                }}
              />
              {t.labels.unknownTime}
            </label>
          </div>

          <div className="birth-location-row">
            <div className="birth-location-field">
              <Field
                id="birth-city"
                label={t.labels.birthCity}
                type="text"
                placeholder="Paris"
                error={errors.birth_city?.message}
                {...register("birth_city", { onChange: resetGeocodingState })}
              />
            </div>
            <div className="birth-location-field">
              <Field
                id="birth-country"
                label={t.labels.birthCountry}
                type="text"
                placeholder="France"
                error={errors.birth_country?.message}
                {...register("birth_country", { onChange: resetGeocodingState })}
              />
            </div>
          </div>

          <div aria-live="polite" aria-atomic="true">
            {geocodingState === "loading" && (
              <p className="state-line" aria-busy="true" role="status">
                <span className="state-loading" aria-hidden="true" />
                {GEOCODING_MESSAGES.loading[lang]}
              </p>
            )}
            {geocodingState === "success" && resolvedGeoLabel !== null && (
              <p className="state-line state-success" role="status">
                ✓ {GEOCODING_MESSAGES.success[lang]} : {resolvedGeoLabel}
              </p>
            )}
            {geocodingState === "error_not_found" && (
              <div className="chat-error degraded-warning" role="alert">
                <p>{GEOCODING_MESSAGES.error_not_found[lang]}</p>
              </div>
            )}
            {geocodingState === "error_unavailable" && (
              <div className="chat-error degraded-warning" role="alert">
                <p>{GEOCODING_MESSAGES.error_unavailable[lang]}</p>
              </div>
            )}
          </div>

          <div>
            <label htmlFor="birth-timezone">{t.labels.birthTimezone}</label>
            <Controller
              name="birth_timezone"
              control={control}
              render={({ field }) => (
                <TimezoneSelect
                  id="birth-timezone"
                  value={field.value ?? ""}
                  onChange={field.onChange}
                  disabled={isSubmitting}
                  aria-invalid={Boolean(errors.birth_timezone)}
                  aria-describedby={errors.birth_timezone ? "birth-timezone-error" : undefined}
                />
              )}
            />
            {errors.birth_timezone && (
              <span id="birth-timezone-error" className="chat-error" role="alert">
                {errors.birth_timezone.message}
              </span>
            )}
          </div>

          <div className="section-divider">
            <h3 id="current-location-title">{t.labels.currentLocation || "Localisation actuelle"}</h3>
            <p className="help-text">
              {t.labels.locationHelp || "La localisation actuelle permet de personnaliser vos guidances avec les énergies du lieu où vous vous trouvez."}
            </p>
            
            <div className="consent-field">
              <label htmlFor="geolocation-consent" className="consent-label">
                <input
                  id="geolocation-consent"
                  type="checkbox"
                  {...register("geolocation_consent")}
                />
                {t.labels.allowGeolocation || "Autoriser la géolocalisation pour personnaliser mes guidances"}
              </label>
            </div>

            {geolocationConsent && (
              <div className="current-location-controls">
                {currentLocationLabel ? (
                  <p className="state-line state-success">
                    ✓ {t.labels.locationDetected || "Lieu détecté"} : {currentLocationLabel}
                  </p>
                ) : (
                  <p className="state-line">
                    {t.labels.noLocation || "Aucun lieu détecté"}
                  </p>
                )}
                
                <button
                  type="button"
                  onClick={handleDetectLocation}
                  disabled={currentLocationState === "detecting" || currentLocationState === "resolving"}
                  className="secondary-button"
                >
                  {currentLocationState === "detecting" || currentLocationState === "resolving" ? (
                    <span className="state-line">
                      <span className="state-loading" aria-hidden="true" />
                      {t.labels.detecting || "Détection..."}
                    </span>
                  ) : (
                    t.labels.detectNow || "Me localiser maintenant"
                  )}
                </button>
                
                {currentLocationState === "error" && (
                  <p className="chat-error">{currentLocationError ?? t.errors.locationFailed}</p>
                )}
              </div>
            )}

            {(!geolocationConsent || currentLocationState === "error") && (
              <div className="current-location-controls">
                <p className="help-text">
                  {t.labels.manualLocationHelp}
                </p>
                <div className="birth-location-row">
                  <div className="birth-location-field">
                    <Field
                      id="current-city"
                      label={t.labels.currentCity}
                      type="text"
                      placeholder="Paris"
                      {...register("current_city")}
                    />
                  </div>
                  <div className="birth-location-field">
                    <Field
                      id="current-country"
                      label={t.labels.currentCountry}
                      type="text"
                      placeholder="France"
                      {...register("current_country")}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>

          {globalError && (
            <div className="chat-error" role="alert">
              <p>{globalError}</p>
            </div>
          )}

          {saveSuccess && (
            <p className="state-line state-success" role="status">
              {t.status.saveSuccess}
            </p>
          )}

          <Button type="submit" loading={isSubmitting} fullWidth>
            {t.buttons.save}
          </Button>
        </form>
      ) : null}

      {data && !isLoading && !isError ? (
        <div className="section-divider" aria-labelledby="natal-generation-title">
          <h3 id="natal-generation-title">{t.status.generationSection}</h3>
          {generationError && (
            <div className="chat-error" role="alert">
              <p>{generationError}</p>
            </div>
          )}
          <Button
            type="button"
            loading={generationMutation.isPending}
            onClick={() => {
              setGenerationError(null)
              generationMutation.mutate()
            }}
          >
            {generationMutation.isPending
              ? t.buttons.generating.replace("{timeout}", GENERATION_TIMEOUT_LABEL)
              : t.buttons.generate}
          </Button>
        </div>
      ) : null}
    </PageLayout>
  )
}

