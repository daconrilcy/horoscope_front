import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { getBirthData, saveBirthData, BirthProfileApiError } from "../api/birthProfile"
import { generateNatalChart, ApiError, type LatestNatalChart } from "../api/natalChart"
import { useAccessTokenSnapshot, getSubjectFromAccessToken } from "../utils/authToken"
import { GENERATION_TIMEOUT_LABEL } from "../utils/constants"
import type { ViewId } from "../App"

const birthProfileSchema = z.object({
  birth_date: z
    .string()
    .regex(/^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$/, "Format YYYY-MM-DD requis (ex: 1990-01-15)")
    .refine((val) => {
      const date = new Date(val)
      return !isNaN(date.getTime()) && date.toISOString().startsWith(val)
    }, "Date invalide")
    .refine((val) => {
      const date = new Date(val)
      return date <= new Date()
    }, "La date de naissance ne peut pas être dans le futur"),
  birth_time: z.string().regex(/^([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$/, "Format HH:MM(:SS) requis (ex: 10:30)"),
  birth_place: z.string().trim().min(1, "Le lieu de naissance est requis").max(255),
  birth_timezone: z
    .string()
    .trim()
    .min(1, "Le fuseau horaire est requis")
    .regex(/^[A-Za-z0-9_-]+(\/[A-Za-z0-9_-]+)+$/, "Format IANA requis (ex: Europe/Paris ou America/Argentina/Buenos_Aires)")
    .max(64),
})

type BirthProfileFormData = z.infer<typeof birthProfileSchema>

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

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["birth-profile", tokenSubject],
    queryFn: () => {
      if (!accessToken) throw new Error("No access token available")
      return getBirthData(accessToken)
    },
    enabled: Boolean(accessToken),
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })

  const generationMutation = useMutation<LatestNatalChart, ApiError>({
    mutationFn: async () => {
      if (!accessToken) throw new Error("No access token available")
      return generateNatalChart(accessToken)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["latest-natal-chart", tokenSubject] })
      onNavigate("natal")
    },
    onError: (err) => {
      setGenerationErrorRequestId(err.requestId || null)
      if (err.code === "natal_generation_timeout") {
        setGenerationError("La génération a pris trop de temps, veuillez réessayer.")
      } else if (err.code === "natal_engine_unavailable") {
        setGenerationError("Le service de génération est temporairement indisponible.")
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
    clearErrors,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<BirthProfileFormData>({
    resolver: zodResolver(birthProfileSchema),
  })

  useEffect(() => {
    if (data && !isSubmitting && !isDirty) {
      reset({
        birth_date: data.birth_date,
        birth_time: data.birth_time,
        birth_place: data.birth_place,
        birth_timezone: data.birth_timezone,
      })
    }
  }, [data, reset, isSubmitting, isDirty])

  async function onSubmit(formData: BirthProfileFormData) {
    if (!accessToken) return
    setSaveSuccess(false)
    setGlobalError(null)
    setSaveErrorRequestId(null)
    setGenerationError(null)
    setGenerationErrorRequestId(null)

    try {
      const updatedData = await saveBirthData(accessToken, formData)
      queryClient.setQueryData(["birth-profile", tokenSubject], updatedData)
      reset({
        birth_date: updatedData.birth_date,
        birth_time: updatedData.birth_time,
        birth_place: updatedData.birth_place,
        birth_timezone: updatedData.birth_timezone,
      })
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
              ID de requête: {error.requestId}
            </p>
          ) : null}
          <button type="button" onClick={() => refetch()} style={{ marginTop: "0.5rem" }}>
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
            if (globalError) setGlobalError(null)
            if (generationError) setGenerationError(null)
            clearErrors()
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
              aria-invalid={Boolean(errors.birth_time)}
              aria-describedby={errors.birth_time ? "birth-time-error" : undefined}
              {...register("birth_time")}
            />
            {errors.birth_time && (
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

          {globalError && (
            <div className="chat-error" role="alert">
              <p>{globalError}</p>
              {saveErrorRequestId ? (
                <p className="state-line" style={{ fontSize: "0.8rem", opacity: 0.7 }}>
                  ID de requête: {saveErrorRequestId}
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
        <div className="section-divider">
          <h3>Génération du thème astral</h3>
          {generationError && (
            <div className="chat-error" role="alert">
              <p>{generationError}</p>
              {generationErrorRequestId ? (
                <p className="state-line" style={{ fontSize: "0.8rem", opacity: 0.7 }}>
                  ID de requête: {generationErrorRequestId}
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
