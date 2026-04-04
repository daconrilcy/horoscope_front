import React from "react"
import { Link } from "react-router-dom"
import { useAstrologyLabels } from "../../../i18n/astrology"
import { getUpgradeBenefitLabel } from "../../../i18n/billing"
import { useUpgradeHint } from "../../../hooks/useEntitlementSnapshot"
import "./UpgradeCTA.css"

interface UpgradeCTAProps {
  featureCode: string
  variant?: "button" | "link"
}

export function UpgradeCTA({ featureCode, variant = "button" }: UpgradeCTAProps) {
  const { lang } = useAstrologyLabels()
  const hint = useUpgradeHint(featureCode)

  if (!hint) {
    return null
  }

  const label = getUpgradeBenefitLabel(hint.benefit_key, lang)

  return (
    <Link
      to="/subscription-guide"
      className={`upgrade-cta upgrade-cta--${variant}`}
    >
      {label}
    </Link>
  )
}
