import { useEffect, useRef, useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { getBirthData, saveBirthData, BirthProfileApiError } from "../api/birthProfile"
import { generateNatalChart, ApiError, type LatestNatalChart } from "../api/natalChart"
import { geocodeCity } from "../api/geocoding"
import { useAccessTokenSnapshot, getSubjectFromAccessToken } from "../utils/authToken"
import { GENERATION_TIMEOUT_LABEL } from "../utils/constants"
import type { ViewId } from "../App"

const birthProfileSchema = z.object({
  birth_date: z
    .string()
    .min(1, "La date de naissance est indispensable pour calculer votre thème natal.")
    .regex(/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/, "Format YYYY-MM-DD requis (ex: 1990-01-15)")
    .refine((val) => {
      const date = new Date(val)
      return !isNaN(date.getTime()) && date.toISOString().startsWith(val)
    }, "Date invalide")
    .refine((val) => {
      const date = new Date(val)
      return date <= new Date()
    }, "La date de naissance ne peut pas être dans le futur"),
  birth_time: z
    .string()
    .regex(/^([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$/, "Format HH:MM(:SS) requis (ex: 10:30)")
    .or(z.literal("")),
  birth_place: z.string().trim().min(1, "Le lieu de naissance est requis").max(255),
  birth_timezone: z
    .string()
    .trim()
    .min(1, "Le fuseau horaire est requis")
    .regex(/^[A-Za-z0-9_-]+(\/[A-Za-z0-9_-]+)*$/, "Format IANA requis (ex: Europe/Paris, UTC ou America/Argentina/Buenos_Aires)")
    .max(64),
  birth_city: z.string().trim().max(255).optional(),
  birth_country: z.string().trim().max(100).optional(),
})

type BirthProfileFormData = z.infer<typeof birthProfileSchema>

type GeocodingState = "idle" | "loading" | "success" | "error_not_found" | "error_unavailable"

interface BirthProfilePageProps {
  onNavigate: (viewId: ViewId) => void
}

export function BirthProfilePage({ onNavigate }: BirthProfilePageProps) {
  const queryClient = useQueryClient()
  const accessToken = useAccessTokenSnapshot()
  const tokenSubject = getSubjectFromAccessToken(accessToken) ?? "anonymous"
  const [saveSuccess, setSaveSuccess] = useState(false)
  const [globalError, setGlobalError] = useState<string | null>(null)
  const [saveErrorRequestId, setSaveErrorRequestId] = useState<string | null>(null)
  const [generationError, setGenerationError] = useState<string | null>(null)
  const [generationErrorRequestId, setGenerationErrorRequestId] = useState<string | null>(null)
  const [geocodingState, setGeocodingState] = useState<GeocodingState>("idle")
  const [resolvedGeoLabel, setResolvedGeoLabel] = useState<string | null>(null)
  const [birthCoords, setBirthCoords] = useState<{ lat: number; lon: number } | null>(null)
  const geocodeAbortRef = useRef<AbortController | null>(null)
  const [birthTimeUnknown, setBirthTimeUnknown] = useState(false)

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["birth-profile", tokenSubject],
    queryFn: () => {
      if (!accessToken) throw new Error("No access token available")
      return getBirthData(accessToken)
    },
    enabled: Boolean(accessToken),
    retry: 1,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })

  const generationMutation = useMutation<LatestNatalChart, Error | ApiError>({
    mutationFn: async () => {
      if (!accessToken) throw new Error("No access token available")
      return generateNatalChart(accessToken)
    },
    onSuccess: (newChart) => {
      queryClient.setQueryData(["latest-natal-chart", tokenSubject], newChart)
      onNavigate("natal")
    },
    onError: (err) => {
      const requestId = err instanceof ApiError ? err.requestId : undefined
      setGenerationErrorRequestId(requestId || null)

      const code = err instanceof ApiError ? err.code : undefined
      const status = err instanceof ApiError ? err.status : undefined
      if (code === "natal_generation_timeout") {
        setGenerationError("La génération a pris trop de temps, veuillez réessayer.")
      } else if (code === "natal_engine_unavailable") {
        setGenerationError("Le service de génération est temporairement indisponible.")
      } else if (code === "unprocessable_entity" || status === 422) {
        setGenerationError("Vos données de naissance sont invalides ou incomplètes. Veuillez vérifier votre profil natal.")
      } else {
        setGenerationError("Une erreur est survenue. Veuillez réessayer.")
      }
    },
  })

  const {
    register,
    handleSubmit,
    reset,
    setError,
    getValues,
    setValue,
    watch,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<BirthProfileFormData>({
    resolver: zodResolver(birthProfileSchema),
  })

  const birthCity = watch("birth_city")
  const birthCountry = watch("birth_country")
  const canGeocode = Boolean(birthCity?.trim() && birthCountry?.trim())

  useEffect(() => {
    return () => { geocodeAbortRef.current?.abort() }
  }, [])

  useEffect(() => {
    if (data && !isSubmitting && !isDirty) {
      syncFormWithProfileData(data)
    }
  }, [data, reset, isSubmitting, isDirty])

  function resetGeocodingState() {
    setGeocodingState("idle")
    setBirthCoords(null)
    setResolvedGeoLabel(null)
  }

  function syncFormWithProfileData(profileData: NonNullable<typeof data>) {
    reset({
      birth_date: profileData.birth_date,
      birth_time: profileData.birth_time ?? "",
      birth_place: profileData.birth_place,
      birth_timezone: profileData.birth_timezone,
      birth_city: profileData.birth_city ?? "",
      birth_country: profileData.birth_country ?? "",
    })
    setBirthTimeUnknown(profileData.birth_time === null)
  }

  async function handleGeocode() {
    const city = (getValues("birth_city") ?? "").trim()
    const country = (getValues("birth_country") ?? "").trim()
    if (!city || !country) return

    const controller = new AbortController()
    geocodeAbortRef.current = controller

    setGeocodingState("loading")
    try {
      const result = await geocodeCity(city, country, controller.signal)
      if (result === null) {
        setGeocodingState("error_not_found")
        setBirthCoords(null)
        setResolvedGeoLabel(null)
      } else {
        setGeocodingState("success")
        setBirthCoords({ lat: result.lat, lon: result.lon })
        setResolvedGeoLabel(result.display_name)
        // Automatically sync birth_place (truncated to Zod max 255)
        setValue("birth_place", result.display_name.slice(0, 255), { shouldDirty: true })
      }
    } catch {
      setGeocodingState("error_unavailable")
      setBirthCoords(null)
      setResolvedGeoLabel(null)
    }
  }

  async function onSubmit(formData: BirthProfileFormData) {
    if (!accessToken) return
    setSaveSuccess(false)
    setGlobalError(null)
    setSaveErrorRequestId(null)
    setGenerationError(null)
    setGenerationErrorRequestId(null)

    try {
      // birth_time is null if checkbox "Heure inconnue" is checked OR if field was left empty
      const payload = {
        ...formData,
        birth_time: (birthTimeUnknown || !formData.birth_time) ? null : formData.birth_time,
        birth_city: formData.birth_city?.trim() || undefined,
        birth_country: formData.birth_country?.trim() || undefined,
        ...(birthCoords ? { birth_lat: birthCoords.lat, birth_lon: birthCoords.lon } : {}),
      }
      const updatedData = await saveBirthData(accessToken, payload)
      queryClient.setQueryData(["birth-profile", tokenSubject], updatedData)
      syncFormWithProfileData(updatedData)
      setSaveSuccess(true)
    } catch (err) {
      const defaultError = "Erreur lors de la sauvegarde. Veuillez réessayer."
      if (err instanceof BirthProfileApiError) {
        setSaveErrorRequestId(err.requestId || null)
        if (err.code === "invalid_birth_time") {
          setError("birth_time", { message: err.message || "Format HH:MM(:SS) requis (ex: 10:30)" })
        } else if (err.code === "invalid_timezone") {
          setError("birth_timezone", { message: err.message || "Fuseau horaire invalide (ex: Europe/Paris)." })
        } else if (err.code === "invalid_birth_input") {
          setGlobalError("Données invalides. Vérifiez les champs.")
        } else {
          setGlobalError(err.message || defaultError)
        }
      } else {
        setGlobalError(defaultError)
      }
    }
  }

  return (
    <section className="panel">
      <h2 id="birth-profile-title">Mon profil natal</h2>

      {isLoading ? (
        <p className="state-line" aria-busy="true" role="status">
          <span className="state-loading" aria-hidden="true" />
          Chargement de votre profil natal...
        </p>
      ) : null}

      {isError && !isLoading ? (
        <div className="chat-error" role="alert">
          <p>Impossible de charger votre profil natal. Veuillez réessayer plus tard.</p>
          {error instanceof BirthProfileApiError && error.requestId ? (
            <p className="state-line" style={{ fontSize: "0.8rem", opacity: 0.7 }}>
              <span aria-hidden="true">ID de requête: </span>
              <span aria-label={`Identifiant de support technique: ${error.requestId}`}>{error.requestId}</span>
            </p>
          ) : null}
          <button type="button" onClick={() => void refetch()} style={{ marginTop: "0.5rem" }}>
            Réessayer
          </button>
        </div>
      ) : null}

      {!isLoading && !isError ? (
        <form
          className="chat-form"
          onSubmit={handleSubmit(onSubmit)}
          onChange={() => {
            if (saveSuccess) setSaveSuccess(false)
            if (globalError) { setGlobalError(null); setSaveErrorRequestId(null) }
            if (generationError) { setGenerationError(null); setGenerationErrorRequestId(null) }
          }}
          noValidate
          aria-labelledby="birth-profile-title"
        >
          <div>
            <label htmlFor="birth-date">Date de naissance (YYYY-MM-DD)</label>
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
            <label htmlFor="birth-time">Heure de naissance (HH:MM)</label>
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
              style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginTop: "0.25rem" }}
            >
              <input
                id="birth-time-unknown"
                type="checkbox"
                checked={birthTimeUnknown}
                onChange={(e) => {
                  setBirthTimeUnknown(e.target.checked)
                  if (e.target.checked) {
                    setValue("birth_time", "", { shouldValidate: false })
                  }
                }}
              />
              Heure inconnue
            </label>
            {!birthTimeUnknown && errors.birth_time && (
              <span id="birth-time-error" className="chat-error" role="alert">
                {errors.birth_time.message}
              </span>
            )}
          </div>

          <div>
            <label htmlFor="birth-place">Lieu de naissance</label>
            <input
              id="birth-place"
              type="text"
              placeholder="Paris, France"
              aria-invalid={Boolean(errors.birth_place)}
              aria-describedby={errors.birth_place ? "birth-place-error" : undefined}
              {...register("birth_place")}
            />
            {errors.birth_place && (
              <span id="birth-place-error" className="chat-error" role="alert">
                {errors.birth_place.message}
              </span>
            )}
          </div>

          <div>
            <label htmlFor="birth-timezone">Fuseau horaire IANA (ex: Europe/Paris)</label>
            <input
              id="birth-timezone"
              type="text"
              placeholder="Europe/Paris"
              aria-invalid={Boolean(errors.birth_timezone)}
              aria-describedby={errors.birth_timezone ? "birth-timezone-error" : undefined}
              {...register("birth_timezone")}
            />
            {errors.birth_timezone && (
              <span id="birth-timezone-error" className="chat-error" role="alert">
                {errors.birth_timezone.message}
              </span>
            )}
          </div>

          <fieldset style={{ border: "1px solid var(--line)", borderRadius: "4px", padding: "0.75rem" }}>
            <legend>Géolocalisation précise <span style={{ fontWeight: "normal", fontSize: "0.9em" }}>(optionnel)</span></legend>
            <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "flex-end" }}>
              <div style={{ flex: 1, minWidth: "8rem" }}>
                <label htmlFor="birth-city">Ville</label>
                <input
                  id="birth-city"
                  type="text"
                  placeholder="Paris"
                  {...register("birth_city", {
                    onChange: resetGeocodingState,
                  })}
                />
              </div>
              <div style={{ flex: 1, minWidth: "8rem" }}>
                <label htmlFor="birth-country">Pays</label>
                <input
                  id="birth-country"
                  type="text"
                  placeholder="France"
                  {...register("birth_country", {
                    onChange: resetGeocodingState,
                  })}
                />
              </div>
              <button
                type="button"
                onClick={() => void handleGeocode()}
                disabled={geocodingState === "loading" || !canGeocode}
                aria-busy={geocodingState === "loading"}
              >
                {geocodingState === "loading" ? (
                  <span className="state-line">
                    <span className="state-loading" aria-hidden="true" />
                    Recherche...
                  </span>
                ) : (
                  "Valider les coordonnées"
                )}
              </button>
            </div>

            {geocodingState === "success" && resolvedGeoLabel !== null && (
              <p className="state-line state-success" role="status">
                ✓ {resolvedGeoLabel} · lat: {birthCoords?.lat.toFixed(4)}, lon: {birthCoords?.lon.toFixed(4)}
              </p>
            )}
            {geocodingState === "error_not_found" && (
              <div className="chat-error" role="alert">
                <p>Lieu introuvable. Vérifiez la ville et le pays, ou laissez le lieu vide pour utiliser le mode dégradé (maisons égales).</p>
              </div>
            )}
            {geocodingState === "error_unavailable" && (
              <div className="chat-error" role="alert">
                <p>Service de géocodage indisponible. Vous pouvez sauvegarder sans coordonnées (mode dégradé).</p>
              </div>
            )}
          </fieldset>

          {globalError && (
            <div className="chat-error" role="alert">
              <p>{globalError}</p>
              {saveErrorRequestId ? (
                <p className="state-line" style={{ fontSize: "0.8rem", opacity: 0.7 }}>
                  <span aria-hidden="true">ID de requête: </span>
                  <span aria-label={`Identifiant de support technique: ${saveErrorRequestId}`}>{saveErrorRequestId}</span>
                </p>
              ) : null}
            </div>
          )}

          {saveSuccess && (
            <p className="state-line state-success" role="status">
              Profil natal sauvegardé.
            </p>
          )}

          <button type="submit" disabled={isSubmitting} aria-busy={isSubmitting}>
            {isSubmitting ? (
              <span className="state-line">
                <span className="state-loading" aria-hidden="true" />
                Sauvegarde en cours...
              </span>
            ) : (
              "Sauvegarder"
            )}
          </button>
        </form>
      ) : null}

      {data && !isLoading && !isError ? (
        <div className="section-divider" aria-labelledby="natal-generation-title">
          <h3 id="natal-generation-title">Génération du thème astral</h3>
          {generationError && (
            <div className="chat-error" role="alert">
              <p>{generationError}</p>
              {generationErrorRequestId ? (
                <p className="state-line" style={{ fontSize: "0.8rem", opacity: 0.7 }}>
                  <span aria-hidden="true">ID de requête: </span>
                  <span aria-label={`Identifiant de support technique: ${generationErrorRequestId}`}>{generationErrorRequestId}</span>
                </p>
              ) : null}
            </div>
          )}
          <button
            type="button"
            onClick={() => {
              setGenerationError(null)
              setGenerationErrorRequestId(null)
              generationMutation.mutate()
            }}
            disabled={generationMutation.isPending}
            aria-busy={generationMutation.isPending}
          >
            {generationMutation.isPending ? (
              <span className="state-line" role="status">
                <span className="state-loading" aria-hidden="true" />
                Génération en cours (max {GENERATION_TIMEOUT_LABEL})...
              </span>
            ) : (
              "Générer mon thème astral"
            )}
          </button>
        </div>
      ) : null}
    </section>
  )
}
