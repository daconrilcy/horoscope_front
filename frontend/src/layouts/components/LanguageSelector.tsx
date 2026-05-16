// Sélecteur de langue d'interface synchronisé avec les préférences utilisateur.
import { Languages } from "lucide-react"
import { useEffect, useMemo, useRef, useState } from "react"

import { useLanguages } from "@api/languages"
import { useUpdateUserSettings, useUserSettings } from "@api/userSettings"
import { SUPPORTED_LANGS, useAstrologyLabels, type AstrologyLang } from "@i18n/astrology"
import { commonTranslations } from "@i18n/common"

const LANGUAGE_FLAGS: Record<AstrologyLang, string> = {
  fr: "🇫🇷",
  en: "🇬🇧",
  es: "🇪🇸",
}

function isSupportedInterfaceLanguage(code: string): code is AstrologyLang {
  return SUPPORTED_LANGS.includes(code as AstrologyLang)
}

function resolveDetectedLocale(): string | null {
  return typeof navigator !== "undefined" ? navigator.language || null : null
}

function resolveDetectedCountryCode(locale: string | null): string | null {
  if (!locale) return null
  try {
    const region = new Intl.Locale(locale).region
    if (region && /^[A-Za-z]{2}$/.test(region)) {
      return region.toUpperCase()
    }
  } catch {
    // Les locales navigateur non canoniques restent traitees par le parseur de secours.
  }
  const region = locale
    .split(/[-_]/)
    .slice(1)
    .find((part) => /^[A-Za-z]{2}$/.test(part))
  return region ? region.toUpperCase() : null
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
  const lastSubmittedLocalization = useRef<string | null>(null)
  const pendingLanguageCode = useRef<AstrologyLang | null>(null)
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
            label: language.name,
          }]
        }),
    [languagesQuery.data],
  )
  const supportedLanguageCodes = useMemo(
    () => new Set(languageOptions.map((language) => language.code)),
    [languageOptions],
  )

  useEffect(() => {
    const defaultCode = settingsQuery.data?.default_language_code
    if (pendingLanguageCode.current) {
      if (defaultCode === pendingLanguageCode.current) {
        pendingLanguageCode.current = null
      }
      return
    }
    if (
      defaultCode &&
      isSupportedInterfaceLanguage(defaultCode) &&
      supportedLanguageCodes.has(defaultCode) &&
      defaultCode !== lang
    ) {
      setLang(defaultCode)
    }
  }, [lang, setLang, settingsQuery.data?.default_language_code, supportedLanguageCodes])

  useEffect(() => {
    if (!settingsQuery.data || updateSettings.isPending) {
      return
    }
    const payload = buildLocalizationPayload()
    const isSameLocalization =
      settingsQuery.data.detected_locale === payload.detected_locale &&
      settingsQuery.data.detected_country_code === payload.detected_country_code &&
      settingsQuery.data.detected_timezone === payload.detected_timezone
    const payloadKey = JSON.stringify(payload)
    if (isSameLocalization) {
      lastSubmittedLocalization.current = null
      return
    }
    if (lastSubmittedLocalization.current === payloadKey) {
      return
    }
    lastSubmittedLocalization.current = payloadKey
    updateSettings.mutate(payload, {
      onError: () => {
        lastSubmittedLocalization.current = null
      },
    })
  }, [settingsQuery.data, updateSettings])

  const current = languageOptions.find((language) => language.code === lang)

  function selectLanguage(code: AstrologyLang) {
    pendingLanguageCode.current = code
    setLang(code)
    updateSettings.mutate({
      default_language_code: code,
      ...buildLocalizationPayload(),
    }, {
      onError: () => {
        pendingLanguageCode.current = null
      },
      onSuccess: (settings) => {
        if (settings.default_language_code === code) {
          pendingLanguageCode.current = null
        }
      },
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
