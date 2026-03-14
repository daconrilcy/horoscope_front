import { useMemo } from "react"
import { TIMEZONES } from "../data/timezones"
import { detectLang, TIMEZONE_SELECT_MESSAGES } from "../i18n/astrology"
import { Select } from "./ui/Select"
import "./TimezoneSelect.css"

/**
 * Props du composant TimezoneSelect.
 * @property value - Fuseau horaire IANA actuellement sélectionné (ex: "Europe/Paris")
 * @property onChange - Callback appelé lors de la sélection d'un fuseau horaire
 * @property disabled - Désactive le composant si true (défaut: false)
 * @property id - ID HTML pour le champ input (utilisé pour les labels et ARIA)
 * @property aria-invalid - Indique si le champ est en état d'erreur (ARIA)
 * @property aria-describedby - ID de l'élément décrivant le champ (ex: message d'erreur)
 * @property label - Label optionnel
 * @property error - Message d'erreur optionnel
 */
type TimezoneSelectProps = {
  value: string
  onChange: (tz: string) => void
  disabled?: boolean
  id?: string
  "aria-invalid"?: boolean
  "aria-describedby"?: string
  label?: string
  error?: string
}

/**
 * Composant de sélection de fuseau horaire IANA utilisant le composant générique Select.
 * @see Select pour l'implémentation générique
 * @see TIMEZONES pour la liste complète des fuseaux disponibles
 */
export function TimezoneSelect({
  value,
  onChange,
  disabled = false,
  id,
  "aria-invalid": ariaInvalid,
  "aria-describedby": ariaDescribedBy,
  label,
  error,
}: TimezoneSelectProps) {
  const lang = detectLang()

  const options = useMemo(() => {
    return TIMEZONES.map((tz) => {
      // Les fuseaux IANA sont souvent de la forme Region/City
      const parts = tz.split('/')
      const region = parts.length > 1 ? parts[0] : 'Autres'
      return {
        value: tz,
        label: tz,
        group: region
      }
    })
  }, [])

  return (
    <Select
      id={id}
      options={options}
      value={value}
      onChange={onChange}
      disabled={disabled}
      label={label}
      error={error || (ariaInvalid ? "Erreur" : undefined)}
      placeholder={TIMEZONE_SELECT_MESSAGES.placeholder[lang]}
      searchPlaceholder={TIMEZONE_SELECT_MESSAGES.placeholder[lang]}
      className="timezone-select-wrapper"
    />
  )
}
