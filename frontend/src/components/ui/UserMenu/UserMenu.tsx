import { useEffect, useRef } from "react"
import { useNavigate } from "react-router-dom"

import { useTranslation } from "@i18n"
import { clearAccessToken } from "@utils/authToken"

import { UserAvatar } from "../UserAvatar/UserAvatar"
import "./UserMenu.css"

export interface UserMenuProps {
  email: string
  role: string
  avatarUrl?: string
  isOpen: boolean
  onClose: () => void
}

function translateRole(role: string, defaultRole: string): string {
  if (role === "user") {
    return defaultRole
  }
  return role
}

export function UserMenu({ email, role, avatarUrl, isOpen, onClose }: UserMenuProps) {
  const navigate = useNavigate()
  const t = useTranslation("common")
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!isOpen) {
      return
    }

    const handleOutside = (event: MouseEvent | TouchEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose()
      }
    }

    document.addEventListener("mousedown", handleOutside)
    document.addEventListener("touchstart", handleOutside)
    return () => {
      document.removeEventListener("mousedown", handleOutside)
      document.removeEventListener("touchstart", handleOutside)
    }
  }, [isOpen, onClose])

  useEffect(() => {
    if (!isOpen) {
      return
    }

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose()
      }
    }

    document.addEventListener("keydown", handleEscape)
    return () => {
      document.removeEventListener("keydown", handleEscape)
    }
  }, [isOpen, onClose])

  if (!isOpen) {
    return null
  }

  const handleNavigate = (path: string) => {
    onClose()
    navigate(path)
  }

  const handleLogout = () => {
    clearAccessToken()
    onClose()
    navigate("/login", { replace: true })
  }

  return (
    <div ref={menuRef} className="user-menu" role="menu">
      <div className="user-menu__header">
        <UserAvatar email={email} avatarUrl={avatarUrl} size="lg" />
        <div className="user-menu__user-info">
          <span className="user-menu__email">{email}</span>
          <span className="user-menu__role">{translateRole(role, t.header.defaultRole)}</span>
        </div>
      </div>

      <div className="user-menu__divider" role="separator" />

      <button
        type="button"
        role="menuitem"
        className="user-menu__item"
        onClick={() => handleNavigate("/settings")}
      >
        {t.userMenu.editAccount}
      </button>
      <button
        type="button"
        role="menuitem"
        className="user-menu__item"
        onClick={handleLogout}
      >
        {t.userMenu.logout}
      </button>
      <button
        type="button"
        role="menuitem"
        className="user-menu__item"
        onClick={() => handleNavigate("/settings")}
      >
        {t.userMenu.settings}
      </button>
    </div>
  )
}
