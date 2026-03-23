import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { API_BASE_URL, apiFetch } from "@api/client"
import { useAccessTokenSnapshot } from "@utils/authToken"
import { useAuthMe } from "@api/authMe"
import { PrivacyPanel } from "@components/PrivacyPanel"
import { DeleteAccountModal } from "@components/settings/DeleteAccountModal"
import { detectLang } from "@i18n/astrology"
import { settingsTranslations } from "@i18n/settings"
import { getLocale } from "@utils/locale"
import type { UserSettingsApiResponse } from "../../types/user"

const ASTROLOGER_STYLES = [
  "standard",
  "vedique",
  "humaniste",
  "karmique",
  "psychologique",
] as const

const USER_SETTINGS_ENDPOINT = `${API_BASE_URL}/v1/users/me/settings`

export function AccountSettings() {
  const lang = detectLang()
  const t = settingsTranslations.account[lang]
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)
  const [showDeleteModal, setShowDeleteModal] = useState(false)

  const [astrologerProfile, setAstrologerProfile] = useState<string>("standard")
  const [isSaving, setIsSaving] = useState(false)
  const [saveStatus, setSaveStatus] = useState<"idle" | "success" | "error">("idle")

  useEffect(() => {
    const fetchSettings = async () => {
      if (!token) return
      try {
        const response = await apiFetch(USER_SETTINGS_ENDPOINT, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (response.ok) {
          const result: UserSettingsApiResponse = await response.json()
          setAstrologerProfile(result.data.astrologer_profile)
        }
      } catch (err) {
        console.error("Failed to fetch settings", err)
      }
    }
    void fetchSettings()
  }, [token])

  const handleProfileChange = async (newProfile: string) => {
    if (!token || isSaving) return
    
    setAstrologerProfile(newProfile)
    setIsSaving(true)
    setSaveStatus("idle")

    try {
      const response = await apiFetch(USER_SETTINGS_ENDPOINT, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ astrologer_profile: newProfile }),
      })

      if (response.ok) {
        setSaveStatus("success")
        setTimeout(() => setSaveStatus("idle"), 3000)
      } else {
        setSaveStatus("error")
      }
    } catch (err) {
      console.error("Failed to save settings", err)
      setSaveStatus("error")
    } finally {
      setIsSaving(false)
    }
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
      <section className="panel">
        <h2>{t.title}</h2>
        {authMe.isLoading && (
          <p className="state-line state-loading" aria-busy="true">
            {t.loading}
          </p>
        )}
        {authMe.isError && (
          <div role="alert" className="chat-error">
            <p>{t.error}</p>
            <button type="button" onClick={() => void authMe.refetch()}>
              {t.retry}
            </button>
          </div>
        )}
        {authMe.data && (
          <div className="account-info-grid">
            <div className="account-info-item">
              <span className="account-info-label">{t.email}</span>
              <span className="account-info-value">{authMe.data.email}</span>
            </div>
            <div className="account-info-item">
              <span className="account-info-label">{t.memberSince}</span>
              <span className="account-info-value">
                {formatDate(authMe.data.created_at)}
              </span>
            </div>
            <div className="account-info-item">
              <span className="account-info-label">{t.role}</span>
              <span className="account-info-value">{authMe.data.role}</span>
            </div>
            <div className="account-info-item">
              <span className="account-info-label">{t.birthData}</span>
              <Link to="/profile" className="account-info-link">
                {t.editBirthData}
              </Link>
            </div>
          </div>
        )}

        <div className="section-divider" />

        <div className="astrologer-style-section">
          <h3>{t.astrologerStyle}</h3>
          <p className="section-desc">{t.astrologerStyleDesc}</p>
          
          <div className="style-grid" style={{ display: 'grid', gap: '12px', marginTop: '16px' }}>
            {ASTROLOGER_STYLES.map((style) => (
              <label 
                key={style} 
                className={`style-option ${astrologerProfile === style ? 'active' : ''}`}
                style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px',
                  padding: '12px',
                  borderRadius: '12px',
                  border: astrologerProfile === style ? '2px solid var(--primary)' : '1px solid var(--glass-border)',
                  background: astrologerProfile === style ? 'rgba(var(--purple_base), 0.05)' : 'transparent',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
              >
                <input
                  type="radio"
                  name="astrologer_profile"
                  value={style}
                  checked={astrologerProfile === style}
                  onChange={() => handleProfileChange(style)}
                  disabled={isSaving}
                  style={{ marginTop: '4px' }}
                />
                <div className="style-info">
                  <div style={{ fontWeight: 'bold', color: 'var(--text-1)' }}>
                    {t[style]}
                  </div>
                  <div style={{ fontSize: '0.85rem', color: 'var(--text-2)' }}>
                    {t[`${style}Desc`]}
                  </div>
                </div>
              </label>
            ))}
          </div>

          <div className="save-feedback" style={{ marginTop: '12px', height: '20px', fontSize: '0.85rem' }}>
            {isSaving && <span style={{ color: 'var(--text-2)' }}>{t.saving}</span>}
            {saveStatus === "success" && <span style={{ color: 'var(--success)' }}>{t.saved}</span>}
            {saveStatus === "error" && <span style={{ color: 'var(--error)' }}>{t.saveError}</span>}
          </div>
        </div>

        <div className="section-divider" />
        
        <button
          type="button"
          className="btn-danger"
          onClick={() => setShowDeleteModal(true)}
        >
          {t.deleteAccount}
        </button>
      </section>

      <PrivacyPanel />

      {showDeleteModal && (
        <DeleteAccountModal onClose={() => setShowDeleteModal(false)} />
      )}
    </div>
  )
}
