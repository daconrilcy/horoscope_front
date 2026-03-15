import React from "react"
import { useTranslation } from "../i18n"
import {
  useB2BCredentials,
  useGenerateB2BCredential,
  useRotateB2BCredential,
} from "../api/enterpriseCredentials"

export function EnterpriseCredentialsPanel() {
  const t = useTranslation("admin").b2b.credentials
  const credentials = useB2BCredentials()
  const generateCredential = useGenerateB2BCredential()
  const rotateCredential = useRotateB2BCredential()

  const generateError = generateCredential.error as Error | null
  const rotateError = rotateCredential.error as Error | null

  return (
    <section className="panel">
      <h2>{t.title}</h2>
      <p>{t.description}</p>

      {credentials.isLoading ? <p>{t.loading}</p> : null}
      {credentials.isError ? (
        <p className="chat-error">{t.errorLoad}</p>
      ) : null}

      {credentials.data && (
        <div className="credentials-container">
          <div className="company-info mb-6">
            <h3>{t.accountTitle(credentials.data.company_name)}</h3>
            <p>{t.accountStatus(credentials.data.status)}</p>
          </div>

          <div className="credentials-list">
            {credentials.data.credentials.map((cred) => (
              <div key={cred.credential_id} className="credential-card mb-4 p-4 border rounded">
                <h3>{t.keyTitle(cred.key_prefix)}</h3>
                <p>
                  Scope: {cred.scope} | Status: {cred.is_active ? "active" : "inactive"}
                </p>
                <p>{t.createdDate(new Date(cred.created_at).toLocaleDateString())}</p>
                
                <button
                  type="button"
                  className="btn btn-secondary mt-2"
                  disabled={rotateCredential.isPending}
                  onClick={() => rotateCredential.mutate(cred.credential_id)}
                >
                  Regenerate Key
                </button>
              </div>
            ))}
          </div>

          <button
            type="button"
            className="btn btn-primary mt-4"
            disabled={generateCredential.isPending}
            onClick={() => generateCredential.mutate({ scope: "full" })}
          >
            Generate New Key
          </button>
        </div>
      )}

      {generateError ? <p role="alert" className="chat-error">{t.errorGenerate(generateError.message)}</p> : null}
      {rotateError ? <p role="alert" className="chat-error">{t.errorRotate(rotateError.message)}</p> : null}
    </section>
  )
}
