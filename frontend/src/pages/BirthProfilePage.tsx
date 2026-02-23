import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"

import { getBirthData, saveBirthData, BirthProfileApiError } from "../api/birthProfile"
import { generateNatalChart, ApiError, type LatestNatalChart } from "../api/natalChart"
import { geocodeCity, GeocodingError } from "../api/geocoding"
import { useAccessTokenSnapshot, getSubjectFromAccessToken } from "../utils/authToken"
import { ANONYMOUS_SUBJECT, GENERATION_TIMEOUT_LABEL, UNKNOWN_BIRTH_TIME_SENTINEL, logSupportRequestId, formatBirthPlace } from "../utils/constants"
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
  })
}

type BirthProfileFormData = z.infer<ReturnType<typeof createBirthProfileSchema>>

type GeocodingState = "idle" | "loading" | "success" | "error_not_found" | "error_unavailable"

type GeoResult = { lat: number; lon: number; display_name: string } | null

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
  const [birthTimeUnknown, setBirthTimeUnknown] = useState(false)

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
      return generateNatalChart(accessToken)
    },
    onSuccess: (newChart) => {
      queryClient.setQueryData(["latest-natal-chart", tokenSubject], newChart)
      navigate("/natal")
    },
    onError: (err) => {
      if (err instanceof ApiError) {
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
    formState: { errors, isSubmitting, isDirty },
  } = useForm<BirthProfileFormData>({
    resolver: zodResolver(schema),
    defaultValues: {
      birth_timezone: getUserTimezone(),
    },
  })

  useEffect(() => {
    return () => { geocodeAbortRef.current?.abort() }
  }, [])

  /**
   * Synchronise le formulaire avec les données du profil API.
   * useCallback requis car utilisé comme dépendance du useEffect suivant,
   * évitant des appels reset() superflus lors de re-renders.
   */
  const syncFormWithProfileData = useCallback(
    (profileData: NonNullable<typeof data>) => {
      const isTimeUnknown = profileData.birth_time === null || profileData.birth_time === UNKNOWN_BIRTH_TIME_SENTINEL
      reset({
        birth_date: profileData.birth_date,
        birth_time: isTimeUnknown ? "" : (profileData.birth_time ?? ""),
        birth_place: profileData.birth_place ?? "",
        birth_timezone: profileData.birth_timezone || getUserTimezone(),
        birth_city: profileData.birth_city ?? "",
        birth_country: profileData.birth_country ?? "",
      })
      setBirthTimeUnknown(isTimeUnknown)
    },
    [reset],
  )

  useEffect(() => {
    if (data && !isSubmitting && !isDirty) {
      syncFormWithProfileData(data)
    }
  }, [data, syncFormWithProfileData, isSubmitting, isDirty])

  useEffect(() => {
    if (isError && error instanceof BirthProfileApiError) {
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
   * Le controller externe permet d'annuler la requête au démontage du composant.
   * geocodeCity gère son propre timeout interne et chaîne le signal externe.
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

  async function onSubmit(formData: BirthProfileFormData) {
    if (!accessToken) return
    setSaveSuccess(false)
    setGlobalError(null)
    setGenerationError(null)
    resetGeocodingState()

    const city = formData.birth_city.trim()
    const country = formData.birth_country.trim()

    setGeocodingState("loading")
    const { result: geoResult, isServiceUnavailable } = await performGeocode(city, country)

    let coords: { lat: number; lon: number } | null = null
    let resolvedPlace = formData.birth_place?.trim() || ""

    if (geoResult === null) {
      setGeocodingState(isServiceUnavailable ? "error_unavailable" : "error_not_found")
    } else {
      setGeocodingState("success")
      coords = { lat: geoResult.lat, lon: geoResult.lon }
      resolvedPlace = geoResult.display_name.slice(0, 255)
      setResolvedGeoLabel(geoResult.display_name)
    }

    try {
      const payload = {
        ...formData,
        birth_time: (birthTimeUnknown || !formData.birth_time) ? UNKNOWN_BIRTH_TIME_SENTINEL : formData.birth_time,
        birth_place: resolvedPlace || formatBirthPlace(city, country),
        birth_city: city,
        birth_country: country,
        ...(coords ? { birth_lat: coords.lat, birth_lon: coords.lon } : {}),
      }
      const updatedData = await saveBirthData(accessToken, payload)
      queryClient.setQueryData(["birth-profile", tokenSubject], updatedData)
      syncFormWithProfileData(updatedData)
      setSaveSuccess(true)
    } catch (err) {
      if (err instanceof BirthProfileApiError) {
        logSupportRequestId(err)
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
    <section className="panel">
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
          <div>
            <label htmlFor="birth-date">{t.labels.birthDate}</label>
            <input
              id="birth-date"
              type="text"
              placeholder="1990-01-15"
              aria-invalid={Boolean(errors.birth_date)}
              aria-describedby={errors.birth_date ? "birth-date-error" : undefined}
              {...register("birth_date")}
            />
            {errors.birth_date && (
              <span id="birth-date-error" className="chat-error" role="alert">
                {errors.birth_date.message}
              </span>
            )}
          </div>

          <div>
            <label htmlFor="birth-time">{t.labels.birthTime}</label>
            <input
              id="birth-time"
              type="text"
              placeholder="10:30"
              disabled={birthTimeUnknown}
              aria-invalid={!birthTimeUnknown && Boolean(errors.birth_time)}
              aria-describedby={!birthTimeUnknown && errors.birth_time ? "birth-time-error" : undefined}
              {...register("birth_time")}
            />
            <label
              htmlFor="birth-time-unknown"
              className="birth-time-unknown-label"
            >
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
            {!birthTimeUnknown && errors.birth_time && (
              <span id="birth-time-error" className="chat-error" role="alert">
                {errors.birth_time.message}
              </span>
            )}
          </div>

          <div className="birth-location-row">
            <div className="birth-location-field">
              <label htmlFor="birth-city">{t.labels.birthCity}</label>
              <input
                id="birth-city"
                type="text"
                placeholder="Paris"
                aria-invalid={Boolean(errors.birth_city)}
                aria-describedby={errors.birth_city ? "birth-city-error" : undefined}
                {...register("birth_city", {
                  onChange: resetGeocodingState,
                })}
              />
              {errors.birth_city && (
                <span id="birth-city-error" className="chat-error" role="alert">
                  {errors.birth_city.message}
                </span>
              )}
            </div>
            <div className="birth-location-field">
              <label htmlFor="birth-country">{t.labels.birthCountry}</label>
              <input
                id="birth-country"
                type="text"
                placeholder="France"
                aria-invalid={Boolean(errors.birth_country)}
                aria-describedby={errors.birth_country ? "birth-country-error" : undefined}
                {...register("birth_country", {
                  onChange: resetGeocodingState,
                })}
              />
              {errors.birth_country && (
                <span id="birth-country-error" className="chat-error" role="alert">
                  {errors.birth_country.message}
                </span>
              )}
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

          <button type="submit" disabled={isSubmitting} aria-busy={isSubmitting}>
            {isSubmitting ? (
              <span className="state-line">
                <span className="state-loading" aria-hidden="true" />
                {t.buttons.saving}
              </span>
            ) : (
              t.buttons.save
            )}
          </button>
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
          <button
            type="button"
            onClick={() => {
              setGenerationError(null)
              generationMutation.mutate()
            }}
            disabled={generationMutation.isPending}
            aria-busy={generationMutation.isPending}
          >
            {generationMutation.isPending ? (
              <span className="state-line" role="status">
                <span className="state-loading" aria-hidden="true" />
                {t.buttons.generating.replace("{timeout}", GENERATION_TIMEOUT_LABEL)}
              </span>
            ) : (
              t.buttons.generate
            )}
          </button>
        </div>
      ) : null}
    </section>
  )
}
