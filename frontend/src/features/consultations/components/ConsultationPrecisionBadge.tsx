// Badge de precision propre au parcours de consultation.
import { type ReactNode } from "react"
import { type ConsultationPrecheckData } from "@api/consultations"
import "./ConsultationPrecisionBadge.css"

type ConsultationPrecisionBadgeProps = {
  precisionLevel: ConsultationPrecheckData["precision_level"]
  children: ReactNode
}

/** Affiche le niveau de precision calcule par le precheck consultation. */
export function ConsultationPrecisionBadge({
  precisionLevel,
  children,
}: ConsultationPrecisionBadgeProps) {
  return (
    <p className={`consultation-precision-badge consultation-precision-badge--${precisionLevel}`}>
      {children}
    </p>
  )
}
