// @ts-nocheck
import { useNavigate } from "react-router-dom"
import { AuthLayout } from "../layouts"

export function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <AuthLayout>
      <section className="panel" style={{ textAlign: 'center' }}>
        <h1>Page non trouvée</h1>
        <p>La page que vous recherchez n'existe pas ou a été déplacée.</p>
        <button type="button" onClick={() => navigate("/dashboard")} className="btn btn--primary" style={{ marginTop: 'var(--space-4)' }}>
          Retour au tableau de bord
        </button>
      </section>
    </AuthLayout>
  )
}

