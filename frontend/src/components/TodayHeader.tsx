import { useState } from "react"

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

  const getInitials = (name: string) => {
    const safeName = (name || "U").trim()
    if (!safeName) return "U"
    
    const parts = safeName.split(/\s+/)
    if (parts.length >= 2) {
      const first = parts[0]?.[0] || ""
      const last = parts[parts.length - 1]?.[0] || ""
      if (first && last) return (first + last).toUpperCase()
    }
    return (safeName[0] || "U").toUpperCase()
  }

  const initials = getInitials(userName)
  const showImage = avatarUrl && !imgError

  return (
    <header className="today-header">
      <div className="today-header__content">
        <p className="today-header__kicker">Aujourd'hui</p>
        <h1 className="today-header__title">Horoscope</h1>
      </div>
      <div
        className="today-header__avatar"
        role="img"
        aria-label={`Profil de ${userName}`}
      >
        {showImage ? (
          <img
            src={avatarUrl}
            alt=""
            onError={() => setImgError(true)}
            decoding="async"
          />
        ) : (
          <span aria-hidden="true">{initials}</span>
        )}
      </div>
    </header>
  )
}
