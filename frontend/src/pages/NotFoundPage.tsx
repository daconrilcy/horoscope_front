import { useNavigate } from "react-router-dom"

export function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <section className="panel">
      <h1>Page non trouvée</h1>
      <p>La page que vous recherchez n'existe pas ou a été déplacée.</p>
      <button type="button" onClick={() => navigate("/dashboard")}>
        Retour au tableau de bord
      </button>
    </section>
  )
}
