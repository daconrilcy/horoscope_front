// Composant de navigation d'upgrade reutilisable par les surfaces verrouillees.
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
  label?: string
}

/** Affiche un CTA d'upgrade base sur le hint d'entitlement ou sur un libelle explicite. */
export function UpgradeCTA({ featureCode, variant = "button", to = "/subscription-guide", label }: UpgradeCTAProps) {
  const { lang } = useAstrologyLabels()
  const hint = useUpgradeHint(featureCode)

  if (!hint && !label) {
    return null
  }

  const ctaLabel = label ?? getUpgradeBenefitLabel(hint!.benefit_key, lang)

  return (
    <Link
      to={to}
      className={`upgrade-cta upgrade-cta--${variant}`}
    >
      {ctaLabel}
    </Link>
  )
}
