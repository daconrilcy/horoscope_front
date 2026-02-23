import { useState, useMemo, useRef, useEffect } from "react"
import { TIMEZONES } from "../data/timezones"
import { detectLang, TIMEZONE_SELECT_MESSAGES } from "../i18n/astrology"
import { classNames } from "../utils/classNames"
import "./TimezoneSelect.css"

/** Délai de debounce en ms pour la recherche dans le sélecteur de timezone */
export const DEBOUNCE_MS = 150
/**
 * Limite le nombre d'options rendues pour éviter les problèmes de performance DOM.
 * La liste TIMEZONES contient ~425 entrées IANA; cette limite affiche un sous-ensemble
 * avec un hint invitant l'utilisateur à filtrer pour accéder aux autres.
 * @see TIMEZONES dans data/timezones.ts pour la liste complète
 */
export const MAX_VISIBLE_OPTIONS = 100

/**
 * Props du composant TimezoneSelect.
 * @property value - Fuseau horaire IANA actuellement sélectionné (ex: "Europe/Paris")
 * @property onChange - Callback appelé lors de la sélection d'un fuseau horaire
 * @property disabled - Désactive le composant si true (défaut: false)
 * @property id - ID HTML pour le champ input (utilisé pour les labels et ARIA)
 * @property aria-invalid - Indique si le champ est en état d'erreur (ARIA)
 * @property aria-describedby - ID de l'élément décrivant le champ (ex: message d'erreur)
 */
type TimezoneSelectProps = {
  value: string
  onChange: (tz: string) => void
  disabled?: boolean
  id?: string
  "aria-invalid"?: boolean
  "aria-describedby"?: string
}

/**
 * Composant de sélection de fuseau horaire IANA avec recherche et navigation clavier.
 * Affiche une liste filtrable des ~425 fuseaux horaires standards avec debounce (150ms).
 * Conforme WCAG 2.1 AA (aria-expanded, aria-controls, aria-activedescendant).
 * @see TIMEZONES pour la liste complète des fuseaux disponibles
 */
export function TimezoneSelect({
  value,
  onChange,
  disabled = false,
  id,
  "aria-invalid": ariaInvalid,
  "aria-describedby": ariaDescribedBy,
}: TimezoneSelectProps) {
  const lang = detectLang()
  const [searchTerm, setSearchTerm] = useState("")
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState("")
  const [isOpen, setIsOpen] = useState(false)
  const [highlightedIndex, setHighlightedIndex] = useState(0)
  const containerRef = useRef<HTMLDivElement>(null)
  const listRef = useRef<HTMLUListElement>(null)

  const listboxId = id ? `${id}-listbox` : "timezone-listbox"

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearchTerm(searchTerm), DEBOUNCE_MS)
    return () => clearTimeout(timer)
  }, [searchTerm])

  const filteredTimezones = useMemo(() => {
    let base: string[]
    if (!debouncedSearchTerm.trim()) {
      base = TIMEZONES.slice(0, MAX_VISIBLE_OPTIONS)
    } else {
      const term = debouncedSearchTerm.toLowerCase()
      base = TIMEZONES.filter((tz) => tz.toLowerCase().includes(term)).slice(0, MAX_VISIBLE_OPTIONS)
    }
    // Always include current value if not already in list (ensures no duplicate keys)
    // The !base.includes(value) check guarantees uniqueness for React key={tz}
    if (value && !base.includes(value) && TIMEZONES.includes(value)) {
      return [value, ...base]
    }
    return base
  }, [debouncedSearchTerm, value])

  const highlightedOptionId = filteredTimezones[highlightedIndex]
    ? `${listboxId}-option-${highlightedIndex}`
    : undefined

  useEffect(() => {
    setHighlightedIndex(0)
  }, [filteredTimezones])

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  useEffect(() => {
    if (isOpen && listRef.current) {
      const highlighted = listRef.current.children[highlightedIndex] as HTMLElement | undefined
      highlighted?.scrollIntoView({ block: "nearest" })
    }
  }, [highlightedIndex, isOpen])

  function handleSelect(tz: string) {
    onChange(tz)
    setSearchTerm("")
    setIsOpen(false)
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (!isOpen && (e.key === "ArrowDown" || e.key === "ArrowUp" || e.key === "Enter")) {
      setIsOpen(true)
      e.preventDefault()
      return
    }

    if (!isOpen) return

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault()
        setHighlightedIndex((prev) => Math.min(prev + 1, filteredTimezones.length - 1))
        break
      case "ArrowUp":
        e.preventDefault()
        setHighlightedIndex((prev) => Math.max(prev - 1, 0))
        break
      case "Enter":
        e.preventDefault()
        if (filteredTimezones[highlightedIndex]) {
          handleSelect(filteredTimezones[highlightedIndex])
        }
        break
      case "Escape":
        e.preventDefault()
        setIsOpen(false)
        setSearchTerm("")
        break
      case "Tab":
        setIsOpen(false)
        break
    }
  }

  return (
    <div ref={containerRef} className="timezone-select" data-testid="timezone-select">
      <input
        id={id}
        type="text"
        value={isOpen ? searchTerm : value}
        onChange={(e) => {
          setSearchTerm(e.target.value)
          if (!isOpen) setIsOpen(true)
        }}
        onFocus={() => {
          setIsOpen(true)
          setSearchTerm("")
        }}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder={TIMEZONE_SELECT_MESSAGES.placeholder[lang]}
        aria-invalid={ariaInvalid}
        aria-describedby={ariaDescribedBy}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-autocomplete="list"
        aria-controls={isOpen ? listboxId : undefined}
        aria-activedescendant={isOpen ? highlightedOptionId : undefined}
        role="combobox"
        autoComplete="off"
        data-testid="timezone-select-input"
      />
      {isOpen && filteredTimezones.length > 0 && (
        <div className="timezone-dropdown-wrapper">
          <ul
            ref={listRef}
            id={listboxId}
            role="listbox"
            className="timezone-dropdown"
            data-testid="timezone-select-listbox"
          >
            {filteredTimezones.map((tz, index) => (
              <li
                key={tz}
                id={`${listboxId}-option-${index}`}
                role="option"
                aria-selected={tz === value}
                onClick={() => handleSelect(tz)}
                onMouseEnter={() => setHighlightedIndex(index)}
                className={classNames("timezone-option", index === highlightedIndex && "highlighted", tz === value && "selected")}
                data-testid={`timezone-option-${tz.replace(/\//g, "-")}`}
              >
                {tz}
              </li>
            ))}
          </ul>
          {/* Hint affiché si >= MAX_VISIBLE_OPTIONS (peut être 101 si value préfixée, comportement attendu) */}
          {filteredTimezones.length >= MAX_VISIBLE_OPTIONS && !debouncedSearchTerm.trim() && (
            <div className="timezone-hint" data-testid="timezone-hint" role="status" aria-live="polite">
              {TIMEZONE_SELECT_MESSAGES.hint[lang]} ({TIMEZONES.length})
            </div>
          )}
        </div>
      )}
      {isOpen && filteredTimezones.length === 0 && (
        <div className="timezone-no-results" data-testid="timezone-no-results" role="status" aria-live="polite">
          {TIMEZONE_SELECT_MESSAGES.no_results[lang]}
        </div>
      )}
    </div>
  )
}
