import React from "react"
import { Link } from "react-router-dom"
import { useAstrologyLabels } from "../../../i18n/astrology"
import { getUpgradeBenefitLabel } from "../../../i18n/billing"
import { useUpgradeHint } from "../../../hooks/useEntitlementSnapshot"
import "./UpgradeCTA.css"

interface UpgradeCTAProps {
  featureCode: string
  variant?: "button" | "link"
  to?: string
}

export function UpgradeCTA({ featureCode, variant = "button", to = "/subscription-guide" }: UpgradeCTAProps) {
  const { lang } = useAstrologyLabels()
  const hint = useUpgradeHint(featureCode)

  if (!hint) {
    return null
  }

  const label = getUpgradeBenefitLabel(hint.benefit_key, lang)

  return (
    <Link
      to={to}
      className={`upgrade-cta upgrade-cta--${variant}`}
    >
      {label}
    </Link>
  )
}
