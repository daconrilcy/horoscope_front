// Mode astrologue: il garde les details techniques derriere un toggle et un gate d'acces.
import { useState, type ReactNode } from "react"
import { Link } from "react-router-dom"
import type { FeatureEntitlementResponse } from "../../api/billing"

type NatalAstrologerModeProps = {
  access: FeatureEntitlementResponse | undefined
  children: ReactNode
}

function canSeeAstrologerMode(access: FeatureEntitlementResponse | undefined): boolean {
  if (!access?.granted) return false
  return access.variant_code === "multi_astrologer" || access.variant_code === "full"
}

/** Controle l'affichage des donnees techniques sans les exposer par defaut. */
export function NatalAstrologerMode({ access, children }: NatalAstrologerModeProps) {
  const [isOpen, setIsOpen] = useState(false)
  const hasAccess = canSeeAstrologerMode(access)

  return (
    <section className="natal-astrologer-mode" aria-labelledby="natal-astrologer-mode-title">
      <div className="natal-astrologer-mode__header">
        <div>
          <span className="natal-section-eyebrow">Mode astrologue</span>
          <h2 id="natal-astrologer-mode-title">Details techniques</h2>
        </div>
        <button
          type="button"
          className="natal-astrologer-mode__toggle"
          aria-expanded={isOpen}
          aria-controls={isOpen ? "natal-astrologer-mode-panel" : undefined}
          onClick={() => setIsOpen((current) => !current)}
        >
          {isOpen ? "Masquer les details techniques" : "Afficher les details techniques"}
        </button>
      </div>
      {isOpen ? (
        <div id="natal-astrologer-mode-panel" className="natal-astrologer-mode__panel">
          {hasAccess ? (
            children
          ) : (
            <article className="natal-card natal-astrologer-mode__upsell">
              <h3>Mode astrologue reserve</h3>
              <p>Passez a Premium pour consulter le panneau expert et les donnees techniques completes.</p>
              <Link className="btn-link" to="/settings/subscription">
                Voir les offres
              </Link>
            </article>
          )}
        </div>
      ) : null}
    </section>
  )
}
