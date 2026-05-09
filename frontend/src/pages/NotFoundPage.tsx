import { useNavigate } from "react-router-dom"
import { AuthLayout } from "../layouts"
import "./NotFoundPage.css"

export function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <AuthLayout>
      <section className="app-panel not-found-panel">
        <h1>Page non trouvée</h1>
        <p>La page que vous recherchez n'existe pas ou a été déplacée.</p>
        <button type="button" onClick={() => navigate("/dashboard")} className="btn btn--primary not-found-panel__action">
          Retour au tableau de bord
        </button>
      </section>
    </AuthLayout>
  )
}

