import { useEffect, useState } from "react"
import type { FormEvent } from "react"

import { BillingApiError, useBillingQuota } from "../api/billing"
import {
  ChatApiError,
  useExecuteModule,
  type SendChatResponse,
  useChatConversationHistory,
  useChatConversations,
  useModuleAvailability,
  useSendChatMessage,
} from "../api/chat"
import {
  GuidanceApiError,
  useRequestContextualGuidance,
  useRequestGuidance,
} from "../api/guidance"

type ChatUiMessage = {
  id: string
  role: "user" | "assistant"
  content: string
}

function asString(value: unknown): string | null {
  return typeof value === "string" ? value : null
}

export function ChatPage() {
  const quota = useBillingQuota()
  const sendMessage = useSendChatMessage()
  const requestGuidance = useRequestGuidance()
  const requestContextualGuidance = useRequestContextualGuidance()
  const conversations = useChatConversations(20, 0)
  const moduleAvailability = useModuleAvailability()
  const executeModule = useExecuteModule()
  const [inputValue, setInputValue] = useState("")
  const [contextSituation, setContextSituation] = useState("")
  const [contextObjective, setContextObjective] = useState("")
  const [contextTimeHorizon, setContextTimeHorizon] = useState("")
  const [messages, setMessages] = useState<ChatUiMessage[]>([])
  const [lastRecovery, setLastRecovery] = useState<SendChatResponse["recovery"] | null>(null)
  const [lastAttemptedMessage, setLastAttemptedMessage] = useState("")
  const [selectedConversationId, setSelectedConversationId] = useState<number | null>(null)
  const [moduleQuestion, setModuleQuestion] = useState("")
  const [moduleSituation, setModuleSituation] = useState("")
  const [moduleResults, setModuleResults] = useState<Record<string, string>>({})
  const [moduleErrorByKey, setModuleErrorByKey] = useState<Record<string, string>>({})
  const [moduleInProgressByKey, setModuleInProgressByKey] = useState<Record<string, boolean>>({})
  const history = useChatConversationHistory(selectedConversationId)
  const activeConversationId = selectedConversationId
  const quotaBlocked = quota.data?.blocked === true
  const anyModuleInProgress = Object.values(moduleInProgressByKey).some((value) => value)
  const displayedMessages = history.data
    ? history.data.messages.map((message) => ({
        id: `${message.role}-${message.message_id}`,
        role: message.role as "user" | "assistant",
        content: message.content,
      }))
    : messages

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const content = inputValue.trim()
    if (!content || sendMessage.isPending || quotaBlocked) {
      return
    }
    setLastAttemptedMessage(content)
    setInputValue("")
    try {
      const response = await sendMessage.mutateAsync({
        message: content,
        ...(selectedConversationId ? { conversation_id: selectedConversationId } : {}),
      })
      setLastRecovery(response.recovery)
      setSelectedConversationId(response.conversation_id)
      void conversations.refetch()
      void quota.refetch()
      if (selectedConversationId) {
        void history.refetch()
      }
      setMessages((current) => [
        ...current,
        {
          id: `u-${response.user_message.message_id}`,
          role: "user",
          content: response.user_message.content,
        },
        {
          id: `a-${response.assistant_message.message_id}`,
          role: "assistant",
          content: response.assistant_message.content,
        },
      ])
    } catch {
      // Error is handled by mutation state.
    }
  }

  const handleRetry = async () => {
    if (!lastAttemptedMessage || sendMessage.isPending || quotaBlocked) {
      return
    }
    try {
      const response = await sendMessage.mutateAsync({
        message: lastAttemptedMessage,
        ...(selectedConversationId ? { conversation_id: selectedConversationId } : {}),
      })
      setLastRecovery(response.recovery)
      setSelectedConversationId(response.conversation_id)
      void conversations.refetch()
      void quota.refetch()
      if (selectedConversationId) {
        void history.refetch()
      }
      setMessages((current) => [
        ...current,
        {
          id: `u-${response.user_message.message_id}`,
          role: "user",
          content: response.user_message.content,
        },
        {
          id: `a-${response.assistant_message.message_id}`,
          role: "assistant",
          content: response.assistant_message.content,
        },
      ])
    } catch {
      // Error is handled by mutation state.
    }
  }

  const error = sendMessage.error as ChatApiError | null
  const quotaError = quota.error as BillingApiError | null
  const guidanceError = requestGuidance.error as GuidanceApiError | null
  const contextualGuidanceError = requestContextualGuidance.error as GuidanceApiError | null

  useEffect(() => {
    const modules = moduleAvailability.data?.modules ?? []
    const unavailableModules = modules
      .filter((module) => !module.available)
      .map((module) => module.module)
    if (unavailableModules.length === 0) {
      return
    }
    setModuleResults((current) => {
      const next = { ...current }
      for (const key of unavailableModules) {
        delete next[key]
      }
      return next
    })
    setModuleErrorByKey((current) => {
      const next = { ...current }
      for (const key of unavailableModules) {
        delete next[key]
      }
      return next
    })
  }, [moduleAvailability.data])

  const handleModuleExecution = async (module: "tarot" | "runes") => {
    if (anyModuleInProgress || moduleInProgressByKey[module] || quotaBlocked) {
      return
    }
    const moduleEntry = moduleAvailability.data?.modules.find((item) => item.module === module)
    if (!moduleEntry || !moduleEntry.available) {
      return
    }
    const question = moduleQuestion.trim()
    if (!question) {
      setModuleErrorByKey((current) => ({
        ...current,
        [module]: "Question module requise.",
      }))
      return
    }
    setModuleInProgressByKey((current) => ({ ...current, [module]: true }))
    setModuleErrorByKey((current) => ({ ...current, [module]: "" }))
    try {
      const response = await executeModule.mutateAsync({
        module,
        payload: {
          question,
          ...(moduleSituation.trim() ? { situation: moduleSituation.trim() } : {}),
          ...(selectedConversationId ? { conversation_id: selectedConversationId } : {}),
        },
      })
      setModuleResults((current) => ({
        ...current,
        [module]: response.interpretation,
      }))
      if (response.conversation_id) {
        setSelectedConversationId(response.conversation_id)
      }
      void conversations.refetch()
      void moduleAvailability.refetch()
      void quota.refetch()
      if (selectedConversationId || response.conversation_id) {
        void history.refetch()
      }
    } catch (caught) {
      const transportError = caught as ChatApiError
      setModuleErrorByKey((current) => ({
        ...current,
        [module]: transportError.message,
      }))
    } finally {
      setModuleInProgressByKey((current) => ({ ...current, [module]: false }))
    }
  }

  return (
    <section className="panel">
      <h1>Chat astrologue</h1>
      <p>Echangez en direct avec votre astrologue virtuel.</p>
      <h2>Quota quotidien</h2>
      {quota.isLoading ? <p aria-busy="true">Chargement du quota...</p> : null}
      {quotaError ? (
        <p>Erreur quota: {quotaError.message}</p>
      ) : null}
      {quota.data ? (
        <p>
          Quota: {quota.data.consumed}/{quota.data.limit} utilises · Restant: {quota.data.remaining} ·
          Reset: {new Date(quota.data.reset_at).toLocaleString()}
        </p>
      ) : null}
      {quota.data?.blocked ? (
        <p role="status">Quota journalier atteint. Vous pourrez reprendre apres le reset.</p>
      ) : null}
      <h2>Guidance periodique</h2>
      <div className="chat-form">
        <button
          type="button"
          onClick={() =>
            requestGuidance.mutate({
              period: "daily",
              ...(selectedConversationId ? { conversation_id: selectedConversationId } : {}),
            })
          }
          disabled={requestGuidance.isPending}
        >
          Guidance du jour
        </button>
        <button
          type="button"
          onClick={() =>
            requestGuidance.mutate({
              period: "weekly",
              ...(selectedConversationId ? { conversation_id: selectedConversationId } : {}),
            })
          }
          disabled={requestGuidance.isPending}
        >
          Guidance de la semaine
        </button>
      </div>
      {requestGuidance.isPending ? <p aria-busy="true">Generation de la guidance en cours...</p> : null}
      {guidanceError ? <p>Erreur guidance: {guidanceError.message}</p> : null}
      {!requestGuidance.data ? <p>Aucune guidance demandee pour le moment.</p> : null}
      {requestGuidance.data ? (
        <article className="card">
          <h3>
            Guidance {requestGuidance.data.period === "daily" ? "quotidienne" : "hebdomadaire"}
          </h3>
          <p>{requestGuidance.data.summary}</p>
          <h4>Points clefs</h4>
          <ul>
            {requestGuidance.data.key_points.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <h4>Conseils actionnables</h4>
          <ul>
            {requestGuidance.data.actionable_advice.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <p>{requestGuidance.data.disclaimer}</p>
        </article>
      ) : null}
      <h2>Guidance contextuelle</h2>
      <form
        className="chat-form"
        onSubmit={(event) => {
          event.preventDefault()
          if (requestContextualGuidance.isPending) {
            return
          }
          const normalizedSituation = contextSituation.trim()
          const normalizedObjective = contextObjective.trim()
          if (!normalizedSituation || !normalizedObjective) {
            return
          }
          requestContextualGuidance.mutate({
            situation: normalizedSituation,
            objective: normalizedObjective,
            ...(contextTimeHorizon.trim() ? { time_horizon: contextTimeHorizon.trim() } : {}),
            ...(selectedConversationId ? { conversation_id: selectedConversationId } : {}),
          })
        }}
      >
        <label htmlFor="context-situation">Situation</label>
        <textarea
          id="context-situation"
          name="context-situation"
          value={contextSituation}
          onChange={(event) => setContextSituation(event.target.value)}
          rows={2}
          placeholder="Ex: Je dois choisir entre deux opportunites."
        />
        <label htmlFor="context-objective">Objectif</label>
        <textarea
          id="context-objective"
          name="context-objective"
          value={contextObjective}
          onChange={(event) => setContextObjective(event.target.value)}
          rows={2}
          placeholder="Ex: Prendre une decision sereine."
        />
        <label htmlFor="context-time-horizon">Horizon temporel (optionnel)</label>
        <input
          id="context-time-horizon"
          name="context-time-horizon"
          value={contextTimeHorizon}
          onChange={(event) => setContextTimeHorizon(event.target.value)}
          placeholder="Ex: 48h"
        />
        <button type="submit" disabled={requestContextualGuidance.isPending}>
          Demander une guidance contextuelle
        </button>
      </form>
      {requestContextualGuidance.isPending ? (
        <p aria-busy="true">Generation de la guidance contextuelle en cours...</p>
      ) : null}
      {contextualGuidanceError ? <p>Erreur guidance contextuelle: {contextualGuidanceError.message}</p> : null}
      {!requestContextualGuidance.data ? <p>Aucune guidance contextuelle demandee pour le moment.</p> : null}
      {requestContextualGuidance.data ? (
        <article className="card">
          <h3>Guidance contextuelle</h3>
          <p>{requestContextualGuidance.data.summary}</p>
          <h4>Points clefs</h4>
          <ul>
            {requestContextualGuidance.data.key_points.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <h4>Conseils actionnables</h4>
          <ul>
            {requestContextualGuidance.data.actionable_advice.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <p>{requestContextualGuidance.data.disclaimer}</p>
        </article>
      ) : null}
      <h2>Modules specialises</h2>
      <p>Tarot et runes sont actives progressivement via feature flags.</p>
      <div className="chat-form">
        <label htmlFor="module-question">Question module</label>
        <textarea
          id="module-question"
          name="module-question"
          rows={2}
          value={moduleQuestion}
          onChange={(event) => setModuleQuestion(event.target.value)}
          placeholder="Ex: Quelle direction privilegier cette semaine ?"
        />
        <label htmlFor="module-situation">Contexte (optionnel)</label>
        <textarea
          id="module-situation"
          name="module-situation"
          rows={2}
          value={moduleSituation}
          onChange={(event) => setModuleSituation(event.target.value)}
          placeholder="Ex: Decision professionnelle imminente."
        />
      </div>
      {moduleAvailability.isPending ? <p aria-busy="true">Chargement des modules...</p> : null}
      {moduleAvailability.error ? <p>Erreur modules: indisponibles pour le moment.</p> : null}
      {moduleAvailability.data ? (
        <div className="chat-form" aria-label="Modules specialises">
          {moduleAvailability.data.modules.map((module) => {
            const moduleName = module.module === "tarot" ? "Tarot" : "Runes"
            const isInProgress = moduleInProgressByKey[module.module] === true
            const hasCompleted = module.available && Boolean(moduleResults[module.module])
            const hasError = Boolean(moduleErrorByKey[module.module])
            let visualStatus: string = module.status
            if (hasError) {
              visualStatus = "error"
            }
            if (isInProgress) {
              visualStatus = "in-progress"
            }
            if (hasCompleted) {
              visualStatus = "completed"
            }
            return (
              <article key={module.module} className="card">
                <h3>{moduleName}</h3>
                <p>
                  Etat: <strong>{visualStatus}</strong>
                </p>
                {!module.available ? <p>Module verrouille ({module.reason}).</p> : null}
                <button
                  type="button"
                  disabled={!module.available || isInProgress || anyModuleInProgress || quotaBlocked}
                  onClick={() => handleModuleExecution(module.module)}
                >
                  Lancer {moduleName}
                </button>
                {isInProgress ? <p aria-busy="true">Execution en cours...</p> : null}
                {moduleErrorByKey[module.module] ? (
                  <p role="alert">Erreur {moduleName}: {moduleErrorByKey[module.module]}</p>
                ) : null}
                {moduleResults[module.module] ? (
                  <p>{moduleResults[module.module]}</p>
                ) : (
                  <p>Aucun resultat module.</p>
                )}
              </article>
            )
          })}
        </div>
      ) : null}
      {activeConversationId ? <p>Conversation active: #{activeConversationId}</p> : null}
      <h2>Historique</h2>
      {conversations.isPending ? <p>Chargement de l historique...</p> : null}
      {conversations.error ? <p>Erreur de chargement de l historique.</p> : null}
      {conversations.data && conversations.data.conversations.length === 0 ? (
        <p>Aucune conversation precedente.</p>
      ) : null}
      {conversations.data && conversations.data.conversations.length > 0 ? (
        <ul className="chat-list">
          {conversations.data.conversations.map((conversation) => (
            <li key={conversation.conversation_id}>
              <button
                type="button"
                onClick={() => setSelectedConversationId(conversation.conversation_id)}
              >
                #{conversation.conversation_id} - {conversation.last_message_preview || "Sans message"}
              </button>
            </li>
          ))}
        </ul>
      ) : null}

      {displayedMessages.length === 0 ? (
        <p>Aucun message pour le moment. Posez votre premiere question.</p>
      ) : (
        <ul className="chat-list" aria-live="polite">
          {displayedMessages.map((message) => (
            <li key={message.id} className={`chat-item chat-item-${message.role}`}>
              <strong>{message.role === "user" ? "Vous" : "Astrologue"}:</strong> {message.content}
            </li>
          ))}
        </ul>
      )}

      {sendMessage.isPending ? (
        <p aria-busy="true">Generation de la reponse en cours...</p>
      ) : null}
      {history.isPending && selectedConversationId ? <p>Chargement du fil...</p> : null}
      {lastRecovery && lastRecovery.recovery_applied ? (
        <div className="chat-error" role="status">
          <p>
            Recuperation automatique appliquee ({lastRecovery.recovery_strategy}) pour recentrer la
            reponse.
          </p>
          {lastRecovery.recovery_strategy === "safe_fallback" ? (
            <p>Essayez de reformuler votre question avec un contexte plus precis.</p>
          ) : null}
        </div>
      ) : null}

      {error ? (
        <div role="alert" className="chat-error">
          <p>Une erreur est survenue: {error.message}</p>
          {error.code === "quota_exceeded" ? (
            <p>
              Quota atteint ({asString(error.details.consumed) ?? "?"}/{asString(error.details.limit) ?? "?"}
              ). Reprise possible apres{" "}
              {asString(error.details.reset_at)
                ? new Date(asString(error.details.reset_at) as string).toLocaleString()
                : "le reset"}.
            </p>
          ) : null}
          {asString(error.details.fallback_message) ? (
            <p>{asString(error.details.fallback_message)}</p>
          ) : null}
          <button type="button" onClick={handleRetry} disabled={quotaBlocked || sendMessage.isPending}>
            Reessayer
          </button>
        </div>
      ) : null}

      <form onSubmit={handleSubmit} className="chat-form">
        <label htmlFor="chat-input">Votre message</label>
        <textarea
          id="chat-input"
          name="chat-input"
          value={inputValue}
          onChange={(event) => setInputValue(event.target.value)}
          rows={3}
          placeholder="Ex: Quelle energie dois-je surveiller cette semaine ?"
        />
        <button type="submit" disabled={sendMessage.isPending || quotaBlocked}>
          Envoyer
        </button>
      </form>
    </section>
  )
}
