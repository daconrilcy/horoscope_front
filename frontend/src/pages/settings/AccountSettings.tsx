import { useState } from "react"
import { Link } from "react-router-dom"
import { useAccessTokenSnapshot } from "@utils/authToken"
import { useAuthMe } from "@api/authMe"
import { useAstrologers } from "@api/astrologers"
import { useUserSettings, useUpdateUserSettings } from "@api/userSettings"
import { DeleteAccountModal } from "@components/settings/DeleteAccountModal"
import { detectLang } from "@i18n/astrology"
import { settingsTranslations } from "@i18n/settings"
import { getLocale } from "@utils/locale"
import { Check } from "lucide-react"
import "./Settings.css"

export function AccountSettings() {
  const lang = detectLang()
  const t = settingsTranslations.account[lang]
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)
  const { data: astrologers, isLoading: isLoadingAstrologers } = useAstrologers()
  const { data: settings, isLoading: isLoadingSettings } = useUserSettings()
  const updateSettings = useUpdateUserSettings()
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const handleDefaultAstrologerChange = (id: string | null) => {
    if (updateSettings.isPending) return
    updateSettings.mutate({ default_astrologer_id: id })
  }

  const formatDate = (isoDate: string): string => {
    const date = new Date(isoDate)
    if (isNaN(date.getTime())) {
      return "—"
    }
    return date.toLocaleDateString(getLocale(lang), {
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  return (
    <div className="account-settings">
      <section className="settings-card">
        <h2 className="settings-section-title settings-section-title--decorated">
          {t.title}
        </h2>
        
        {authMe.isLoading && (
          <p className="settings-save-feedback settings-save-feedback--saving" aria-busy="true">
            {t.loading}
          </p>
        )}
        
        {authMe.isError && (
          <div role="alert" className="settings-save-feedback settings-save-feedback--error">
            <p>{t.error}</p>
            <button type="button" className="settings-tab" onClick={() => void authMe.refetch()}>
              {t.retry}
            </button>
          </div>
        )}
        
        {authMe.data && (
          <div className="settings-card--soft" style={{ marginTop: '24px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div>
                <div className="usage-stat-label">{t.email}</div>
                <div className="default-astrologer-option__name">{authMe.data.email}</div>
              </div>
              <div>
                <div className="usage-stat-label">{t.memberSince}</div>
                <div className="default-astrologer-option__name">
                  {formatDate(authMe.data.created_at)}
                </div>
              </div>
              <div>
                <div className="usage-stat-label">{t.role}</div>
                <div className="default-astrologer-option__name">{authMe.data.role}</div>
              </div>
              <div>
                <div className="usage-stat-label">{t.birthData}</div>
                <Link to="/profile" className="settings-tab" style={{ marginTop: '4px', textDecoration: 'none', height: 'auto', minHeight: '32px' }}>
                  {t.editBirthData}
                </Link>
              </div>
            </div>
          </div>
        )}

        <div className="settings-divider" />

        <div className="default-astrologer-section">
          <h3 className="settings-section-title">{t.defaultAstrologer}</h3>
          <p className="default-astrologer-option__style">{t.defaultAstrologerDesc}</p>
          
          {(isLoadingAstrologers || isLoadingSettings) ? (
            <p className="settings-save-feedback settings-save-feedback--saving">{t.loading}</p>
          ) : (
            <div className="default-astrologer-grid">
              {/* Option Automatique */}
              <div 
                className={`default-astrologer-option ${settings?.default_astrologer_id === null ? 'default-astrologer-option--selected' : ''}`}
                onClick={() => handleDefaultAstrologerChange(null)}
              >
                <div className="default-astrologer-option__avatar--placeholder">
                  ✨
                </div>
                <div className="default-astrologer-option__name">{t.automatic}</div>
                <div className="default-astrologer-option__style">{t.automaticDesc}</div>
                {settings?.default_astrologer_id === null && (
                  <div className="default-astrologer-option__check">
                    <Check size={12} /> {t.selected}
                  </div>
                )}
              </div>

              {/* Astrologues réels */}
              {astrologers?.map((astro) => (
                <div 
                  key={astro.id}
                  className={`default-astrologer-option ${settings?.default_astrologer_id === astro.id ? 'default-astrologer-option--selected' : ''}`}
                  onClick={() => handleDefaultAstrologerChange(astro.id)}
                >
                  {astro.avatar_url ? (
                    <img 
                      src={astro.avatar_url} 
                      alt={astro.name} 
                      className="default-astrologer-option__avatar" 
                    />
                  ) : (
                    <div className="default-astrologer-option__avatar--placeholder">
                      {astro.first_name[0]}
                    </div>
                  )}
                  <div className="default-astrologer-option__name">{astro.name}</div>
                  <div className="default-astrologer-option__style">{astro.style}</div>
                  {settings?.default_astrologer_id === astro.id && (
                    <div className="default-astrologer-option__check">
                      <Check size={12} /> {t.selected}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          <div className="settings-save-feedback">
            {updateSettings.isPending && (
              <span className="settings-save-feedback--saving">{t.saving}</span>
            )}
            {updateSettings.isSuccess && (
              <span className="settings-save-feedback--success">{t.saved}</span>
            )}
            {updateSettings.isError && (
              <span className="settings-save-feedback--error">{t.saveError}</span>
            )}
          </div>
        </div>

        <div className="settings-divider" />
        
        <button
          type="button"
          className="settings-tab"
          style={{ background: 'rgba(192, 57, 43, 0.1)', color: '#c0392b', borderColor: 'rgba(192, 57, 43, 0.2)' }}
          onClick={() => setShowDeleteModal(true)}
        >
          {t.deleteAccount}
        </button>
      </section>

      {showDeleteModal && (
        <DeleteAccountModal onClose={() => setShowDeleteModal(false)} />
      )}
    </div>
  )
}
