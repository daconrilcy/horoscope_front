import { useState } from "react"

export interface TodayHeaderProps {
  userName?: string
  avatarUrl?: string
}

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
    return safeName.slice(0, 2).toUpperCase()
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
