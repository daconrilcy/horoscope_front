import { useState } from "react"

import {
  B2BEditorialApiError,
  useB2BEditorialConfig,
  useUpdateB2BEditorialConfig,
} from "../api/b2bEditorial"
import type { B2BEditorialConfig } from "../api/b2bEditorial"

function parseTerms(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter((item) => item.length > 0)
}

function formatErrorDetails(details: Record<string, unknown>): string {
  const entries = Object.entries(details)
  if (entries.length === 0) {
    return ""
  }
  return entries
    .map(([key, value]) => `${key}=${typeof value === "string" ? value : JSON.stringify(value)}`)
    .join(" | ")
}

export function B2BEditorialPanel() {
  const [apiKey, setApiKey] = useState("")
  const [loadedConfig, setLoadedConfig] = useState<B2BEditorialConfig | null>(null)
  const [tone, setTone] = useState<"neutral" | "friendly" | "premium">("neutral")
  const [lengthStyle, setLengthStyle] = useState<"short" | "medium" | "long">("medium")
  const [outputFormat, setOutputFormat] = useState<"paragraph" | "bullet">("paragraph")
  const [preferredTerms, setPreferredTerms] = useState("")
  const [avoidedTerms, setAvoidedTerms] = useState("")

  const readConfig = useB2BEditorialConfig()
  const updateConfig = useUpdateB2BEditorialConfig()

  const readError = readConfig.error as B2BEditorialApiError | null
  const updateError = updateConfig.error as B2BEditorialApiError | null
  const isBusy = readConfig.isPending || updateConfig.isPending
  const isEmpty = !isBusy && !readError && !updateError && loadedConfig === null

  return (
    <section className="panel">
      <h2>Personnalisation editoriale B2B</h2>
      <p>Configurez le style des reponses astrologiques selon votre ligne editoriale.</p>

      <label htmlFor="b2b-editorial-api-key">Cle API B2B</label>
      <input
        id="b2b-editorial-api-key"
        value={apiKey}
        onChange={(event) => setApiKey(event.target.value)}
        placeholder="b2b_xxxxx"
      />
      <button
        type="button"
        disabled={isBusy}
        onClick={async () => {
          const config = await readConfig.mutateAsync(apiKey.trim())
          setLoadedConfig(config)
          setTone(config.tone)
          setLengthStyle(config.length_style)
          setOutputFormat(config.output_format)
          setPreferredTerms(config.preferred_terms.join(", "))
          setAvoidedTerms(config.avoided_terms.join(", "))
        }}
      >
        Charger la configuration
      </button>

      {isBusy ? <p aria-busy="true">Chargement configuration editoriale...</p> : null}
      {readError ? (
        <p role="alert">
          Erreur lecture editoriale: {readError.message} ({readError.code})
          {readError.requestId ? ` [request_id=${readError.requestId}]` : ""}
          {Object.keys(readError.details).length > 0
            ? ` [details=${formatErrorDetails(readError.details)}]`
            : ""}
        </p>
      ) : null}
      {updateError ? (
        <p role="alert">
          Erreur mise a jour editoriale: {updateError.message} ({updateError.code})
          {updateError.requestId ? ` [request_id=${updateError.requestId}]` : ""}
          {Object.keys(updateError.details).length > 0
            ? ` [details=${formatErrorDetails(updateError.details)}]`
            : ""}
        </p>
      ) : null}
      {isEmpty ? <p>Aucune configuration chargee.</p> : null}

      {loadedConfig ? (
        <>
          <p>
            Version active: {loadedConfig.version_number} ({loadedConfig.is_active ? "active" : "inactive"})
          </p>

          <label htmlFor="b2b-editorial-tone">Ton</label>
          <select
            id="b2b-editorial-tone"
            value={tone}
            onChange={(event) => setTone(event.target.value as "neutral" | "friendly" | "premium")}
          >
            <option value="neutral">Neutral</option>
            <option value="friendly">Friendly</option>
            <option value="premium">Premium</option>
          </select>

          <label htmlFor="b2b-editorial-length">Longueur</label>
          <select
            id="b2b-editorial-length"
            value={lengthStyle}
            onChange={(event) => setLengthStyle(event.target.value as "short" | "medium" | "long")}
          >
            <option value="short">Short</option>
            <option value="medium">Medium</option>
            <option value="long">Long</option>
          </select>

          <label htmlFor="b2b-editorial-format">Format</label>
          <select
            id="b2b-editorial-format"
            value={outputFormat}
            onChange={(event) => setOutputFormat(event.target.value as "paragraph" | "bullet")}
          >
            <option value="paragraph">Paragraph</option>
            <option value="bullet">Bullet</option>
          </select>

          <label htmlFor="b2b-editorial-preferred">Mots a privilegier (comma separated)</label>
          <input
            id="b2b-editorial-preferred"
            value={preferredTerms}
            onChange={(event) => setPreferredTerms(event.target.value)}
            placeholder="focus, clarte"
          />

          <label htmlFor="b2b-editorial-avoided">Mots a eviter (comma separated)</label>
          <input
            id="b2b-editorial-avoided"
            value={avoidedTerms}
            onChange={(event) => setAvoidedTerms(event.target.value)}
            placeholder="drama, confusion"
          />

          <button
            type="button"
            disabled={isBusy}
            onClick={async () => {
              const updated = await updateConfig.mutateAsync({
                apiKey: apiKey.trim(),
                payload: {
                  tone,
                  length_style: lengthStyle,
                  output_format: outputFormat,
                  preferred_terms: parseTerms(preferredTerms),
                  avoided_terms: parseTerms(avoidedTerms),
                },
              })
              setLoadedConfig(updated)
              setPreferredTerms(updated.preferred_terms.join(", "))
              setAvoidedTerms(updated.avoided_terms.join(", "))
            }}
          >
            Enregistrer la configuration
          </button>
        </>
      ) : null}
    </section>
  )
}
