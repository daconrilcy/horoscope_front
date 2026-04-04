import React from "react"
import { Lock } from "lucide-react"
import "./LockedSection.css"

interface LockedSectionProps {
  children: React.ReactNode
  cta?: React.ReactNode
  label?: string
}

export function LockedSection({ children, cta, label }: LockedSectionProps) {
  return (
    <div className="locked-section">
      <div className="locked-section__content" aria-hidden="true">{children}</div>
      <div className="locked-section__overlay">
        <div className="locked-section__icon-container">
          <Lock className="locked-section__icon" />
        </div>
        {label && <span className="locked-section__label">{label}</span>}
        <div className="locked-section__cta-container">{cta}</div>
      </div>
    </div>
  )
}
