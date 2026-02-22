type HomePageProps = {
  onSignIn: () => void
  onRegister: () => void
}

export function HomePage({ onSignIn, onRegister }: HomePageProps) {
  return (
    <section className="panel">
      <h1>Bienvenue</h1>
      <p>Votre astrologue virtuel personnel, disponible 24h/24.</p>
      <div className="chat-form">
        <button type="button" onClick={onSignIn}>
          Se connecter
        </button>
        <button type="button" onClick={onRegister}>
          Créer un compte
        </button>
      </div>
    </section>
  )
}
