import { useState } from "react"

import "./UserAvatar.css"

export interface UserAvatarProps {
  email: string
  displayName?: string
  avatarUrl?: string
  size?: "sm" | "md" | "lg"
  onClick?: () => void
  "aria-expanded"?: boolean
}

export function UserAvatar({
  email,
  displayName,
  avatarUrl,
  size = "md",
  onClick,
  "aria-expanded": ariaExpanded,
}: UserAvatarProps) {
  const [imgError, setImgError] = useState(false)

  const initial = (email[0] ?? "?").toUpperCase()
  const label = displayName || email || "?"
  const showImage = Boolean(avatarUrl) && !imgError
  const className = `user-avatar user-avatar--${size}`

  const content = showImage ? (
    <img
      src={avatarUrl}
      alt={label}
      className="user-avatar__img"
      onError={() => setImgError(true)}
    />
  ) : (
    <span className="user-avatar__initial" aria-hidden="true">
      {initial}
    </span>
  )

  if (onClick) {
    return (
      <button
        type="button"
        className={className}
        onClick={onClick}
        aria-label={label}
        aria-expanded={ariaExpanded}
        aria-haspopup="menu"
      >
        {content}
      </button>
    )
  }

  if (showImage) {
    return <div className={className}>{content}</div>
  }

  return (
    <div className={className} role="img" aria-label={label}>
      {content}
    </div>
  )
}
