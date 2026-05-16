// Sélecteur de langue d'interface synchronisé avec les préférences utilisateur.
import { Languages } from "lucide-react"
import { useEffect, useMemo, useState } from "react"

import { useLanguages } from "@api/languages"
import { useUpdateUserSettings, useUserSettings } from "@api/userSettings"
import { SUPPORTED_LANGS, useAstrologyLabels, type AstrologyLang } from "@i18n/astrology"
import { commonTranslations } from "@i18n/common"

const LANGUAGE_FLAGS: Record<AstrologyLang, string> = {
  fr: "🇫🇷",
  en: "🇬🇧",
  es: "🇪🇸",
}

const LANGUAGE_NAMES: Record<AstrologyLang, string> = {
  fr: "Français",
  en: "English",
  es: "Español",
}

function isSupportedInterfaceLanguage(code: string): code is AstrologyLang {
  return SUPPORTED_LANGS.includes(code as AstrologyLang)
}

function resolveDetectedLocale(): string | null {
  return typeof navigator !== "undefined" ? navigator.language || null : null
}

function resolveDetectedCountryCode(locale: string | null): string | null {
  const region = locale?.split("-")[1]
  return region && region.length === 2 ? region.toUpperCase() : null
}

function resolveDetectedTimezone(): string | null {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || null
  } catch {
    return null
  }
}

function buildLocalizationPayload() {
  const detectedLocale = resolveDetectedLocale()
  return {
    detected_locale: detectedLocale,
    detected_country_code: resolveDetectedCountryCode(detectedLocale),
    detected_timezone: resolveDetectedTimezone(),
  }
}

export function LanguageSelector() {
  const { lang, setLang } = useAstrologyLabels()
  const t = commonTranslations(lang)
  const [isOpen, setIsOpen] = useState(false)
  const languagesQuery = useLanguages()
  const settingsQuery = useUserSettings()
  const updateSettings = useUpdateUserSettings()

  const languageOptions = useMemo(
    () =>
      (languagesQuery.data ?? [])
        .flatMap((language) => {
          if (!isSupportedInterfaceLanguage(language.code)) {
            return []
          }
          const code = language.code
          return [{
            code,
            flag: LANGUAGE_FLAGS[code],
            label: LANGUAGE_NAMES[code],
          }]
        }),
    [languagesQuery.data],
  )

  useEffect(() => {
    const defaultCode = settingsQuery.data?.default_language_code
    if (defaultCode && isSupportedInterfaceLanguage(defaultCode) && defaultCode !== lang) {
      setLang(defaultCode)
    }
  }, [lang, setLang, settingsQuery.data?.default_language_code])

  useEffect(() => {
    if (!settingsQuery.data || updateSettings.isPending) {
      return
    }
    const payload = buildLocalizationPayload()
    const isSameLocalization =
      settingsQuery.data.detected_locale === payload.detected_locale &&
      settingsQuery.data.detected_country_code === payload.detected_country_code &&
      settingsQuery.data.detected_timezone === payload.detected_timezone
    if (!isSameLocalization) {
      updateSettings.mutate(payload)
    }
  }, [settingsQuery.data, updateSettings])

  const current = languageOptions.find((language) => language.code === lang)

  function selectLanguage(code: AstrologyLang) {
    setLang(code)
    updateSettings.mutate({
      default_language_code: code,
      ...buildLocalizationPayload(),
    })
    setIsOpen(false)
  }

  return (
    <div className="app-header-language-wrapper">
      <button
        type="button"
        className="app-header-language-toggle"
        onClick={() => setIsOpen((value) => !value)}
        aria-label={t.header.chooseLanguage}
        aria-expanded={isOpen}
      >
        <Languages size={18} aria-hidden="true" />
        <span className="app-header-language-flag" aria-hidden="true">
          {current?.flag ?? LANGUAGE_FLAGS.fr}
        </span>
      </button>
      {isOpen ? (
        <div className="app-header-language-menu" role="menu">
          {languageOptions.map((language) => (
            <button
              key={language.code}
              type="button"
              className="app-header-language-option"
              role="menuitemradio"
              aria-checked={language.code === lang}
              onClick={() => selectLanguage(language.code)}
            >
              <span aria-hidden="true">{language.flag}</span>
              <span>{language.label}</span>
            </button>
          ))}
        </div>
      ) : null}
    </div>
  )
}
