import { useEffect, useState } from "react"

import {
  EnterpriseCredentialsApiError,
  useEnterpriseCredentials,
  useGenerateEnterpriseCredential,
  useRotateEnterpriseCredential,
} from "../api/enterpriseCredentials"

export function EnterpriseCredentialsPanel() {
  return <EnterpriseCredentialsPanelContent />
}

function EnterpriseCredentialsPanelContent() {
  const [lastGeneratedSecret, setLastGeneratedSecret] = useState<string | null>(null)
  const [isSecretVisible, setIsSecretVisible] = useState(false)
  const credentials = useEnterpriseCredentials(true)
  const generateCredential = useGenerateEnterpriseCredential()
  const rotateCredential = useRotateEnterpriseCredential()

  const isBusy = generateCredential.isPending || rotateCredential.isPending
  const credentialsError = credentials.error as EnterpriseCredentialsApiError | null
  const generateError = generateCredential.error as EnterpriseCredentialsApiError | null
  const rotateError = rotateCredential.error as EnterpriseCredentialsApiError | null

  useEffect(() => {
    if (!lastGeneratedSecret) {
      return
    }
    const timeout = setTimeout(() => {
      setLastGeneratedSecret(null)
      setIsSecretVisible(false)
    }, 30_000)
    return () => clearTimeout(timeout)
  }, [lastGeneratedSecret])

  return (
    <section className="panel">
      <h2>Credentials API entreprise</h2>
      <p>Generez et regenez vos cles API B2B.</p>

      {credentials.isPending ? <p aria-busy="true">Chargement credentials...</p> : null}
      {credentialsError ? <p role="alert">Erreur credentials: {credentialsError.message}</p> : null}
      {!credentials.isPending &&
      !credentialsError &&
      credentials.data &&
      credentials.data.credentials.length === 0 ? (
        <p>Aucun credential configure pour ce compte.</p>
      ) : null}

      {credentials.data ? (
        <>
          <p>
            Compte entreprise: {credentials.data.company_name} ({credentials.data.status})
          </p>
          <ul className="chat-list">
            {credentials.data.credentials.map((item) => (
              <li key={item.credential_id} className="chat-item">
                Credential #{item.credential_id} · {item.key_prefix} · {item.status}
              </li>
            ))}
          </ul>
        </>
      ) : null}

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
        Generer une cle API
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
        Regenerer la cle active
      </button>

      {lastGeneratedSecret ? (
        <>
          <p role="status">
            Nouvelle cle API (expiree de l ecran dans 30s):{" "}
            {isSecretVisible ? lastGeneratedSecret : "************************"}
          </p>
          <button type="button" onClick={() => setIsSecretVisible((current) => !current)}>
            {isSecretVisible ? "Masquer la cle" : "Afficher la cle"}
          </button>
        </>
      ) : null}
      {generateError ? <p role="alert">Erreur generation cle: {generateError.message}</p> : null}
      {rotateError ? <p role="alert">Erreur regeneration cle: {rotateError.message}</p> : null}
    </section>
  )
}
