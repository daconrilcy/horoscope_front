// Mode astrologue: il garde les details techniques derriere un toggle et un gate d'acces.
import { useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import type { FeatureEntitlementResponse } from "../../api/billing"
import type { PublicCopyLang } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"
import "./NatalAstrologerMode.css"

type NatalAstrologerModeProps = {
  access: FeatureEntitlementResponse | undefined
  children: ReactNode
  lang?: PublicCopyLang
}

function canSeeAstrologerMode(access: FeatureEntitlementResponse | undefined): boolean {
  if (!access?.granted) return false
  return access.variant_code === "multi_astrologer" || access.variant_code === "full"
}

/** Controle l'affichage des donnees techniques sans les exposer par defaut. */
export function NatalAstrologerMode({ access, children, lang }: NatalAstrologerModeProps) {
  const copy = getNatalPublicCopy(lang).astrologerMode
  const [isOpen, setIsOpen] = useState(false)
  const hasAccess = canSeeAstrologerMode(access)

  return (
    <section className="natal-astrologer-mode" aria-labelledby="natal-astrologer-mode-title">
      <div className="natal-astrologer-mode__header">
        <div>
          <span className="natal-section-eyebrow">{copy.eyebrow}</span>
          <h2 className="natal-astrologer-mode__title" id="natal-astrologer-mode-title">{copy.title}</h2>
        </div>
        <button
          type="button"
          className="natal-astrologer-mode__toggle"
          aria-expanded={isOpen}
          aria-controls={isOpen ? "natal-astrologer-mode-panel" : undefined}
          onClick={() => setIsOpen((current) => !current)}
        >
          {isOpen ? copy.hide : copy.show}
        </button>
      </div>
      {isOpen ? (
        <div id="natal-astrologer-mode-panel" className="natal-astrologer-mode__panel">
          {hasAccess ? (
            children
          ) : (
            <article className="natal-card natal-astrologer-mode__upsell">
              <h3>{copy.reserved}</h3>
              <p>{copy.upsell}</p>
              <Link className="btn-link" to="/settings/subscription">
                {copy.offers}
              </Link>
            </article>
          )}
        </div>
      ) : null}
    </section>
  )
}
