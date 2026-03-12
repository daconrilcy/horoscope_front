import { useState } from "react"
import { Moon, Sun, ChevronLeft } from "lucide-react"
import { getInitials } from "../utils/user"
import { useTheme } from "../state/ThemeProvider"

/**
 * Props for the TodayHeader component
 */
export interface TodayHeaderProps {
  /** Display name of the user to generate initials or alt text */
  userName?: string
  /** URL of the user's avatar image */
  avatarUrl?: string
  /** Optional callback for back navigation */
  onBackClick?: () => void
  /** Loading state */
  isLoading?: boolean
}

/**
 * TodayHeader displays the main page title ("Horoscope"), a dark/light toggle top-left,
 * and the user profile avatar top-right.
 * It automatically handles initials fallback if the image fails to load.
 */
export function TodayHeader({ userName = "U", avatarUrl, onBackClick, isLoading: forceLoading }: TodayHeaderProps) {
  const [imgError, setImgError] = useState(false)
  const { theme, toggleTheme } = useTheme()

  const isLoading = userName === "loading" || forceLoading
  const displayName = isLoading ? "" : userName
  const initials = getInitials(displayName || "U")
  const showImage = avatarUrl && !imgError && !isLoading

  return (
    <header className="today-header">
      {/* Top left actions: Back button OR Theme toggle */}
      <div className="today-header__left-actions">
        {onBackClick ? (
          <button
            type="button"
            className="today-header__back"
            onClick={onBackClick}
            aria-label="Retour au tableau de bord"
          >
            <ChevronLeft size={24} strokeWidth={2} aria-hidden="true" />
          </button>
        ) : (
          <button
            type="button"
            className="today-header__toggle"
            onClick={toggleTheme}
            aria-label={theme === "dark" ? "Passer en mode clair" : "Passer en mode sombre"}
            aria-pressed={theme === "dark"}
          >
            {theme === "dark"
              ? <Sun size={20} strokeWidth={1.75} aria-hidden="true" />
              : <Moon size={20} strokeWidth={1.75} aria-hidden="true" />
            }
          </button>
        )}
      </div>

      <div className="today-header__content">
        <p className="today-header__kicker">Aujourd'hui</p>
        <h1 className="today-header__title">Horoscope</h1>
      </div>

      {/* Avatar — top right */}
      <div
        className={`today-header__avatar ${isLoading ? "today-header__avatar--loading" : ""}`}
        role="img"
        aria-label={isLoading ? "Chargement du profil" : `Profil de ${displayName}`}
      >
        {showImage ? (
          <img
            src={avatarUrl}
            alt=""
            onError={() => setImgError(true)}
            decoding="async"
          />
        ) : (
          !isLoading && <span aria-hidden="true">{initials}</span>
        )}
      </div>
    </header>
  )
}
