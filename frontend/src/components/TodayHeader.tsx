import { useState } from "react"
import { Moon, Sun } from "lucide-react"
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
}

/**
 * TodayHeader displays the main page title ("Horoscope") and the user profile avatar.
 * It automatically handles initials fallback if the image fails to load.
 */
export function TodayHeader({ userName = "U", avatarUrl }: TodayHeaderProps) {
  const [imgError, setImgError] = useState(false)
  const { theme, toggleTheme } = useTheme()

  const isLoading = userName === "loading"
  const displayName = isLoading ? "" : userName
  const initials = getInitials(displayName || "U")
  const showImage = avatarUrl && !imgError && !isLoading

  return (
    <header className="today-header">
      <button
        type="button"
        className="today-header__theme-toggle"
        onClick={toggleTheme}
        aria-label={theme === "dark" ? "Passer en mode clair" : "Passer en mode sombre"}
        title={theme === "dark" ? "Passer en mode clair" : "Passer en mode sombre"}
      >
        {theme === "dark"
          ? <Sun size={20} strokeWidth={1.75} aria-hidden="true" />
          : <Moon size={20} strokeWidth={1.75} aria-hidden="true" />
        }
      </button>

      <div className="today-header__content">
        <p className="today-header__kicker">Aujourd'hui</p>
        <h1 className="today-header__title">Horoscope</h1>
      </div>
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
