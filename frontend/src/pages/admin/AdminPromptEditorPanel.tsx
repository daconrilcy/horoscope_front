import { useEffect, useMemo, useState, type FormEvent } from "react"

import type {
  AdminLlmUseCase,
  AdminPromptDraftCreateInput,
  AdminPromptVersion,
} from "@api"
import type { AdminPromptsEditorStrings } from "../../i18n/adminPromptsEditor"

type EditorErrors = Partial<Record<keyof AdminPromptDraftCreateInput, string>>

type AdminPromptEditorPanelProps = {
  useCaseKey: string
  useCaseDisplayName: string
  versions: AdminPromptVersion[]
  activeVersion: AdminPromptVersion | null
  useCases: AdminLlmUseCase[]
  strings: AdminPromptsEditorStrings
  saveError: string | null
  saveSuccess: string | null
  isPending: boolean
  onSubmit: (payload: AdminPromptDraftCreateInput) => Promise<void>
}

type EditorFormState = {
  developer_prompt: string
  model: string
  temperature: string
  max_output_tokens: string
  fallback_use_case_key: string
}

function resolveBaseVersion(
  versions: AdminPromptVersion[],
  activeVersion: AdminPromptVersion | null,
): AdminPromptVersion | null {
  return activeVersion ?? versions[0] ?? null
}

function createInitialFormState(version: AdminPromptVersion | null): EditorFormState {
  return {
    developer_prompt: version?.developer_prompt ?? "",
    model: version?.model ?? "",
    temperature: version ? String(version.temperature) : "0.7",
    max_output_tokens: version ? String(version.max_output_tokens) : "2048",
    fallback_use_case_key: version?.fallback_use_case_key ?? "",
  }
}

function formatStatus(status: AdminPromptVersion["status"], strings: AdminPromptsEditorStrings): string {
  switch (status) {
    case "draft":
      return strings.statusDraft
    case "published":
      return strings.statusPublished
    case "inactive":
    case "archived":
      return strings.statusInactive
    default:
      return strings.statusUnknown
  }
}

function parseFormValues(
  form: EditorFormState,
  useCaseKey: string,
  strings: AdminPromptsEditorStrings,
): { data: AdminPromptDraftCreateInput | null; errors: EditorErrors } {
  const errors: EditorErrors = {}
  const developerPrompt = form.developer_prompt.trim()
  const model = form.model.trim()
  const temperatureInput = form.temperature.trim()
  const maxOutputTokensInput = form.max_output_tokens.trim()
  const temperature = Number(temperatureInput)
  const maxOutputTokens = Number(maxOutputTokensInput)
  const fallbackUseCaseKey = form.fallback_use_case_key.trim()

  if (!developerPrompt) {
    errors.developer_prompt = strings.validationDeveloperPromptRequired
  }
  if (!model) {
    errors.model = strings.validationModelRequired
  }
  if (!temperatureInput || !Number.isFinite(temperature)) {
    errors.temperature = strings.validationTemperatureNumber
  } else if (temperature < 0 || temperature > 2) {
    errors.temperature = strings.validationTemperatureRange
  }
  if (!Number.isInteger(maxOutputTokens) || maxOutputTokens <= 0) {
    errors.max_output_tokens = strings.validationMaxOutputTokensRequired
  }
  if (fallbackUseCaseKey && fallbackUseCaseKey === useCaseKey) {
    errors.fallback_use_case_key = strings.validationFallbackSameUseCase
  }

  if (Object.keys(errors).length > 0) {
    return { data: null, errors }
  }

  return {
    data: {
      developer_prompt: developerPrompt,
      model,
      temperature,
      max_output_tokens: maxOutputTokens,
      fallback_use_case_key: fallbackUseCaseKey || null,
    },
    errors,
  }
}

export function AdminPromptEditorPanel({
  useCaseKey,
  useCaseDisplayName,
  versions,
  activeVersion,
  useCases,
  strings,
  saveError,
  saveSuccess,
  isPending,
  onSubmit,
}: AdminPromptEditorPanelProps) {
  const baseVersion = useMemo(() => resolveBaseVersion(versions, activeVersion), [activeVersion, versions])
  const [form, setForm] = useState<EditorFormState>(() => createInitialFormState(baseVersion))
  const [errors, setErrors] = useState<EditorErrors>({})

  useEffect(() => {
    setForm(createInitialFormState(baseVersion))
    setErrors({})
  }, [baseVersion?.id, useCaseKey])

  const fallbackOptions = useMemo(
    () => useCases.filter((useCase) => useCase.key !== useCaseKey),
    [useCaseKey, useCases],
  )

  const parsed = useMemo(() => parseFormValues(form, useCaseKey, strings), [form, strings, useCaseKey])
  const hasChanges = useMemo(() => {
    if (!baseVersion) {
      return false
    }
    return (
      form.developer_prompt.trim() !== baseVersion.developer_prompt ||
      form.model.trim() !== baseVersion.model ||
      form.temperature.trim() !== String(baseVersion.temperature) ||
      form.max_output_tokens.trim() !== String(baseVersion.max_output_tokens) ||
      form.fallback_use_case_key.trim() !== (baseVersion.fallback_use_case_key ?? "")
    )
  }, [baseVersion, form])

  const summaryItems = useMemo(() => {
    if (!baseVersion || !parsed.data) {
      return []
    }
    const items: string[] = []
    if (parsed.data.developer_prompt !== baseVersion.developer_prompt) {
      items.push(
        strings.summaryDeveloperPrompt(
          baseVersion.developer_prompt.length,
          parsed.data.developer_prompt.length,
        ),
      )
    }
    if (parsed.data.model !== baseVersion.model) {
      items.push(strings.summaryModel(baseVersion.model, parsed.data.model))
    }
    if (parsed.data.temperature !== baseVersion.temperature) {
      items.push(strings.summaryTemperature(baseVersion.temperature, parsed.data.temperature))
    }
    if (parsed.data.max_output_tokens !== baseVersion.max_output_tokens) {
      items.push(
        strings.summaryMaxOutputTokens(baseVersion.max_output_tokens, parsed.data.max_output_tokens),
      )
    }
    if ((parsed.data.fallback_use_case_key ?? null) !== (baseVersion.fallback_use_case_key ?? null)) {
      items.push(
        strings.summaryFallback(
          baseVersion.fallback_use_case_key ?? strings.noFallbackSummary,
          parsed.data.fallback_use_case_key ?? strings.noFallbackSummary,
        ),
      )
    }
    return items
  }, [baseVersion, parsed.data, strings])

  const handleChange = (field: keyof EditorFormState, value: string) => {
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => {
      if (!current[field as keyof EditorErrors]) {
        return current
      }
      return { ...current, [field]: undefined }
    })
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const validation = parseFormValues(form, useCaseKey, strings)
    setErrors(validation.errors)
    if (!validation.data) {
      return
    }
    try {
      await onSubmit(validation.data)
    } catch {
      // The page owns backend error presentation; keep the form interactive.
    }
  }

  if (!baseVersion) {
    return (
      <section className="admin-prompts-editor panel" aria-labelledby="prompt-editor-heading">
        <div className="admin-prompts-editor__header">
          <div>
            <h4 id="prompt-editor-heading" className="admin-prompts-editor__title">
              {strings.sectionTitle}
            </h4>
            <p className="admin-prompts-editor__intro text-muted">{strings.sectionIntro}</p>
          </div>
        </div>
        <p className="admin-prompts-editor__empty text-muted" role="status">
          {strings.noBaseVersion}
        </p>
      </section>
    )
  }

  return (
    <section className="admin-prompts-editor panel" aria-labelledby="prompt-editor-heading">
      <div className="admin-prompts-editor__header">
        <div>
          <h4 id="prompt-editor-heading" className="admin-prompts-editor__title">
            {strings.sectionTitle}
          </h4>
          <p className="admin-prompts-editor__intro text-muted">{strings.sectionIntro}</p>
        </div>
        <dl className="admin-prompts-editor__meta">
          <div>
            <dt>{strings.currentStatusLabel}</dt>
            <dd>{formatStatus(baseVersion.status, strings)}</dd>
          </div>
          <div>
            <dt>{strings.basedOnLabel}</dt>
            <dd>
              {useCaseDisplayName} · <code>{baseVersion.id}</code>
            </dd>
          </div>
        </dl>
      </div>

      <p className="admin-prompts-editor__reference text-muted">{strings.basedOnHint}</p>

      {saveSuccess ? (
        <p className="state-line state-success" role="status" aria-live="polite">
          {saveSuccess}
        </p>
      ) : null}
      {saveError ? (
        <p className="chat-error" role="alert">
          {strings.backendErrorPrefix}: {saveError}
        </p>
      ) : null}

      <form
        className="admin-prompts-editor__form"
        noValidate
        onSubmit={(event) => void handleSubmit(event)}
      >
        <label className="admin-prompts-editor__field">
          <span>{strings.developerPromptLabel}</span>
          <textarea
            aria-label={strings.developerPromptLabel}
            value={form.developer_prompt}
            onChange={(event) => handleChange("developer_prompt", event.target.value)}
            rows={12}
            aria-invalid={errors.developer_prompt ? "true" : "false"}
          />
          <small className="text-muted">{strings.developerPromptHint}</small>
          {errors.developer_prompt ? (
            <span className="chat-error" role="alert">
              {errors.developer_prompt}
            </span>
          ) : null}
        </label>

        <div className="admin-prompts-editor__grid">
          <label className="admin-prompts-editor__field">
            <span>{strings.modelLabel}</span>
            <input
              aria-label={strings.modelLabel}
              type="text"
              value={form.model}
              onChange={(event) => handleChange("model", event.target.value)}
              aria-invalid={errors.model ? "true" : "false"}
            />
            <small className="text-muted">{strings.modelHint}</small>
            {errors.model ? (
              <span className="chat-error" role="alert">
                {errors.model}
              </span>
            ) : null}
          </label>

          <label className="admin-prompts-editor__field">
            <span>{strings.temperatureLabel}</span>
            <input
              aria-label={strings.temperatureLabel}
              type="number"
              min="0"
              max="2"
              step="0.1"
              value={form.temperature}
              onChange={(event) => handleChange("temperature", event.target.value)}
              aria-invalid={errors.temperature ? "true" : "false"}
            />
            <small className="text-muted">{strings.temperatureHint}</small>
            {errors.temperature ? (
              <span className="chat-error" role="alert">
                {errors.temperature}
              </span>
            ) : null}
          </label>

          <label className="admin-prompts-editor__field">
            <span>{strings.maxOutputTokensLabel}</span>
            <input
              aria-label={strings.maxOutputTokensLabel}
              type="number"
              min="1"
              step="1"
              value={form.max_output_tokens}
              onChange={(event) => handleChange("max_output_tokens", event.target.value)}
              aria-invalid={errors.max_output_tokens ? "true" : "false"}
            />
            <small className="text-muted">{strings.maxOutputTokensHint}</small>
            {errors.max_output_tokens ? (
              <span className="chat-error" role="alert">
                {errors.max_output_tokens}
              </span>
            ) : null}
          </label>

          <label className="admin-prompts-editor__field">
            <span>{strings.fallbackUseCaseLabel}</span>
            <select
              aria-label={strings.fallbackUseCaseLabel}
              value={form.fallback_use_case_key}
              onChange={(event) => handleChange("fallback_use_case_key", event.target.value)}
              aria-invalid={errors.fallback_use_case_key ? "true" : "false"}
            >
              <option value="">{strings.fallbackEmptyOption}</option>
              {fallbackOptions.map((useCase) => (
                <option key={useCase.key} value={useCase.key}>
                  {useCase.display_name} · {useCase.key}
                </option>
              ))}
            </select>
            <small className="text-muted">{strings.fallbackUseCaseHint}</small>
            {errors.fallback_use_case_key ? (
              <span className="chat-error" role="alert">
                {errors.fallback_use_case_key}
              </span>
            ) : null}
          </label>
        </div>

        <section className="admin-prompts-editor__summary" aria-labelledby="prompt-editor-summary-heading">
          <h5 id="prompt-editor-summary-heading" className="admin-prompts-editor__summary-title">
            {strings.summaryTitle}
          </h5>
          {summaryItems.length === 0 ? (
            <p className="admin-prompts-editor__summary-empty text-muted">{strings.summaryEmpty}</p>
          ) : (
            <ul className="admin-prompts-editor__summary-list">
              {summaryItems.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
        </section>

        <div className="admin-prompts-editor__actions">
          <button
            className="action-button action-button--primary"
            type="submit"
            disabled={isPending || !hasChanges}
          >
            {isPending ? strings.saving : strings.saveDraft}
          </button>
        </div>
      </form>
    </section>
  )
}
