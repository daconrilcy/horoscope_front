import { useEffect, useState } from "react"

import {
  useEnterpriseCredentials,
  useGenerateEnterpriseCredential,
  useRotateEnterpriseCredential,
  type EnterpriseCredentialsApiError,
} from "../api/enterpriseCredentials"

export function EnterpriseCredentialsPanel() {
  const [lastGeneratedSecret, setLastGeneratedSecret] = useState<string | null>(null)
  const [isSecretVisible, setIsSecretVisible] = useState(false)

  const credentials = useEnterpriseCredentials()

  const generateCredential = useGenerateEnterpriseCredential()
  const rotateCredential = useRotateEnterpriseCredential()

  const isBusy = generateCredential.isPending || rotateCredential.isPending
  const generateError = generateCredential.error as EnterpriseCredentialsApiError | null
  const rotateError = rotateCredential.error as EnterpriseCredentialsApiError | null

  useEffect(() => {
    if (!lastGeneratedSecret) {
      return
    }
    const timer = setTimeout(() => {
      setLastGeneratedSecret(null)
    }, 30000)
    return () => clearTimeout(timer)
  }, [lastGeneratedSecret])

  return (
    <section className="panel">
      <h2>API Entreprise</h2>
      <p>Générez et régénérez vos clés API B2B.</p>

      {credentials.isLoading ? <p>Chargement des credentials...</p> : null}
      {credentials.isError ? (
        <p className="chat-error">Impossible de charger les credentials.</p>
      ) : null}

      {credentials.data ? (
        <div className="grid">
          <article className="card">
            <h3>Compte: {credentials.data.company_name}</h3>
            <p>Status compte: <strong>{credentials.data.status}</strong></p>
          </article>
          {credentials.data.credentials.map((cred) => (
            <article key={cred.credential_id} className="card">
              <h3>Clé: {cred.key_prefix}***</h3>
              <p>
                Status: <strong>{cred.status}</strong>
              </p>
              <p>Créée le: {new Date(cred.created_at).toLocaleDateString()}</p>
            </article>
          ))}
        </div>
      ) : null}

      <div className="chat-form">
        <button
          type="button"
          disabled={isBusy}
          onClick={async () => {
            const data = await generateCredential.mutateAsync()
            setLastGeneratedSecret(data.api_key)
            setIsSecretVisible(false)
            void credentials.refetch()
          }}
        >
          Générer une clé API
        </button>
        <button
          type="button"
          disabled={isBusy}
          onClick={async () => {
            const data = await rotateCredential.mutateAsync()
            setLastGeneratedSecret(data.api_key)
            setIsSecretVisible(false)
            void credentials.refetch()
          }}
        >
          Régénérer la clé active
        </button>
      </div>

      {lastGeneratedSecret ? (
        <>
          <p role="status" className="state-line state-success">
            Nouvelle clé API (expirée de l'écran dans 30s):{" "}
            {isSecretVisible ? lastGeneratedSecret : "************************"}
          </p>
          <button type="button" onClick={() => setIsSecretVisible((current) => !current)}>
            {isSecretVisible ? "Masquer la clé" : "Afficher la clé"}
          </button>
        </>
      ) : null}
      {generateError ? <p role="alert" className="chat-error">Erreur génération clé: {generateError.message}</p> : null}
      {rotateError ? <p role="alert" className="chat-error">Erreur régénération clé: {rotateError.message}</p> : null}
    </section>
  )
}
