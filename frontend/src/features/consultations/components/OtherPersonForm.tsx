import { useEffect, useRef, useState } from "react"
import {
  detectLang,
  GEOCODING_MESSAGES,
  type GeocodingMessageKey,
} from "../../../i18n/astrology"
import { geocodeCity, GeocodingError } from "../../../api/geocoding"
import { t } from "../../../i18n/consultations"
import { formatBirthPlace } from "../../../utils/constants"
import { type OtherPersonDraft } from "../../../types/consultation"

type OtherPersonFormProps = {
  value: OtherPersonDraft | null
  onChange: (value: OtherPersonDraft | null) => void
}

type GeocodingState = "idle" | "loading" | "success" | "error_not_found" | "error_unavailable"

const EMPTY_VALUE: OtherPersonDraft = {
  birthDate: "",
  birthTime: "",
  birthTimeKnown: true,
  birthPlace: "",
  birthCity: "",
  birthCountry: "",
  placeResolvedId: null,
  birthLat: null,
  birthLon: null,
}

export function OtherPersonForm({ value, onChange }: OtherPersonFormProps) {
  const lang = detectLang()
  const [internalValue, setInternalValue] = useState<OtherPersonDraft>(value ?? EMPTY_VALUE)
  const [geocodingState, setGeocodingState] = useState<GeocodingState>("idle")
  const [resolvedGeoLabel, setResolvedGeoLabel] = useState<string | null>(value?.birthPlace ?? null)
  const geocodeAbortRef = useRef<AbortController | null>(null)

  useEffect(() => {
    setInternalValue(value ?? EMPTY_VALUE)
    setResolvedGeoLabel(value?.placeResolvedId ? value.birthPlace : null)
  }, [value])

  useEffect(() => {
    return () => {
      geocodeAbortRef.current?.abort()
    }
  }, [])

  const notifyParent = (nextValue: OtherPersonDraft) => {
    if (nextValue.birthDate && nextValue.birthCity.trim() && nextValue.birthCountry.trim()) {
      onChange(nextValue)
      return
    }
    onChange(null)
  }

  const handleChange = (updates: Partial<OtherPersonDraft>) => {
    const newValue = { ...internalValue, ...updates }
    if ("birthCity" in updates || "birthCountry" in updates) {
      newValue.placeResolvedId = null
      newValue.birthLat = null
      newValue.birthLon = null
      newValue.birthPlace =
        newValue.birthCity.trim() && newValue.birthCountry.trim()
          ? formatBirthPlace(newValue.birthCity.trim(), newValue.birthCountry.trim())
          : ""
      setGeocodingState("idle")
      setResolvedGeoLabel(null)
    }
    setInternalValue(newValue)
    notifyParent(newValue)
  }

  const handleResolveBirthPlace = async () => {
    const city = internalValue.birthCity.trim()
    const country = internalValue.birthCountry.trim()
    if (!city || !country) {
      return
    }

    geocodeAbortRef.current?.abort()
    const controller = new AbortController()
    geocodeAbortRef.current = controller
    setGeocodingState("loading")

    try {
      const result = await geocodeCity(city, country, controller.signal)
      if (result === null) {
        const fallbackValue = {
          ...internalValue,
          birthPlace: formatBirthPlace(city, country),
          placeResolvedId: null,
          birthLat: null,
          birthLon: null,
        }
        setInternalValue(fallbackValue)
        setResolvedGeoLabel(null)
        setGeocodingState("error_not_found")
        notifyParent(fallbackValue)
        return
      }

      const resolvedValue = {
        ...internalValue,
        birthPlace: result.display_name,
        placeResolvedId: result.place_resolved_id,
        birthLat: result.lat,
        birthLon: result.lon,
      }
      setInternalValue(resolvedValue)
      setResolvedGeoLabel(result.display_name)
      setGeocodingState("success")
      notifyParent(resolvedValue)
    } catch (error) {
      const fallbackValue = {
        ...internalValue,
        birthPlace: formatBirthPlace(city, country),
        placeResolvedId: null,
        birthLat: null,
        birthLon: null,
      }
      setInternalValue(fallbackValue)
      setResolvedGeoLabel(null)
      setGeocodingState(
        error instanceof GeocodingError ? "error_unavailable" : "error_not_found"
      )
      notifyParent(fallbackValue)
    }
  }

  return (
    <div className="other-person-form">
      <h3 className="other-person-form-title">{t("other_person_title", lang)}</h3>
      <p className="other-person-form-hint">{t("other_person_hint", lang)}</p>

      <div className="form-group">
        <label htmlFor="other-birth-date">{t("birth_date_label", lang)}</label>
        <input
          id="other-birth-date"
          type="date"
          value={internalValue.birthDate}
          onChange={(e) => handleChange({ birthDate: e.target.value })}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="other-birth-time">{t("birth_time_label", lang)}</label>
        <div className="birth-time-input-row">
          <input
            id="other-birth-time"
            type="time"
            value={internalValue.birthTime ?? ""}
            onChange={(e) => handleChange({ birthTime: e.target.value })}
            disabled={!internalValue.birthTimeKnown}
          />
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={!internalValue.birthTimeKnown}
              onChange={(e) =>
                handleChange({
                  birthTimeKnown: !e.target.checked,
                  birthTime: e.target.checked ? null : internalValue.birthTime,
                })
              }
            />
            {t("unknown_time_label", lang)}
          </label>
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="other-birth-city">{t("birth_city_label", lang)}</label>
        <input
          id="other-birth-city"
          type="text"
          placeholder={t("birth_city_placeholder", lang)}
          value={internalValue.birthCity}
          onChange={(e) => handleChange({ birthCity: e.target.value })}
          onBlur={() => void handleResolveBirthPlace()}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="other-birth-country">{t("birth_country_label", lang)}</label>
        <input
          id="other-birth-country"
          type="text"
          placeholder={t("birth_country_placeholder", lang)}
          value={internalValue.birthCountry}
          onChange={(e) => handleChange({ birthCountry: e.target.value })}
          onBlur={() => void handleResolveBirthPlace()}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="other-birth-place">{t("birth_place_label", lang)}</label>
        <input
          id="other-birth-place"
          type="text"
          value={internalValue.birthPlace}
          readOnly
          placeholder={t("birth_place_placeholder", lang)}
        />
      </div>

      <div aria-live="polite" aria-atomic="true">
        {geocodingState !== "idle" && (
          <p
            className={
              geocodingState === "success"
                ? "state-line state-success"
                : geocodingState === "loading"
                  ? "state-line"
                  : "chat-error degraded-warning"
            }
            role={geocodingState.startsWith("error") ? "alert" : "status"}
            aria-busy={geocodingState === "loading"}
          >
            {geocodingState === "loading" && <span className="state-loading" aria-hidden="true" />}
            {geocodingState === "success"
              ? `✓ ${GEOCODING_MESSAGES.success[lang]} : ${resolvedGeoLabel}`
              : GEOCODING_MESSAGES[geocodingState as GeocodingMessageKey][lang]}
          </p>
        )}
      </div>
    </div>
  )
}
