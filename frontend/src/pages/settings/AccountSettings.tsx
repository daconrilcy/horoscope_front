import { useState } from "react"
import { Link } from "react-router-dom"
import { useAccessTokenSnapshot } from "../../utils/authToken"
import { useAuthMe } from "../../api/authMe"
import { PrivacyPanel } from "../../components/PrivacyPanel"
import { DeleteAccountModal } from "../../components/settings/DeleteAccountModal"
import { detectLang } from "../../i18n/astrology"
import { settingsTranslations } from "../../i18n/settings"
import { getLocale } from "../../utils/locale"

export function AccountSettings() {
  const lang = detectLang()
  const t = settingsTranslations.account[lang]
  const token = useAccessTokenSnapshot()
  const authMe = useAuthMe(token)
  const [showDeleteModal, setShowDeleteModal] = useState(false)

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
