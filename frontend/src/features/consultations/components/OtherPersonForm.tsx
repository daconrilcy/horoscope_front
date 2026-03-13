import { useState } from "react"
import { detectLang } from "../../../i18n/astrology"
import { t } from "../../../i18n/consultations"
import { type OtherPersonDraft } from "../../../types/consultation"

type OtherPersonFormProps = {
  value: OtherPersonDraft | null
  onChange: (value: OtherPersonDraft | null) => void
}

export function OtherPersonForm({ value, onChange }: OtherPersonFormProps) {
  const lang = detectLang()
  const [internalValue, setInternalValue] = useState<OtherPersonDraft>(
    value ?? {
      birthDate: "",
      birthTime: "",
      birthTimeKnown: true,
      birthPlace: "",
    }
  )

  const handleChange = (updates: Partial<OtherPersonDraft>) => {
    const newValue = { ...internalValue, ...updates }
    setInternalValue(newValue)
    // Only notify parent if essential fields are present
    if (newValue.birthDate && newValue.birthPlace) {
      onChange(newValue)
    } else {
      onChange(null)
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
        <label htmlFor="other-birth-place">{t("birth_place_label", lang)}</label>
        <input
          id="other-birth-place"
          type="text"
          placeholder={t("birth_place_placeholder", lang)}
          value={internalValue.birthPlace}
          onChange={(e) => handleChange({ birthPlace: e.target.value })}
          required
        />
      </div>
    </div>
  )
}
