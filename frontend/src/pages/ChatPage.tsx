import { useMemo, useState } from "react"
import type { FormEvent } from "react"

import { useBillingQuota } from "../api/billing"
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
  const displayedMessages = useMemo(() => {
    const historyMsgs =
      history.data?.messages.map((message) => ({
        id: `${message.role}-${message.message_id}`,
        role: message.role as "user" | "assistant",
        content: message.content,
      })) ?? []

    // If we have history, we might still have some "optimistic" local messages 
    // that haven't been captured by the last history fetch yet.
    // For simplicity in this implementation, we merge them by ID.
    const localOnly = messages.filter(
      (m) => !historyMsgs.some((hm) => hm.id === m.id),
    )

    return [...historyMsgs, ...localOnly]
  }, [history.data, messages])

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
    setInputValue(lastAttemptedMessage)
    // Clear lastAttemptedMessage so next try uses the new inputValue
    setLastAttemptedMessage("")
  }

  const handleModuleExecution = async (moduleName: string) => {
    const question = moduleQuestion.trim()
    if (!question || quotaBlocked) {
      return
    }
    const typedModule = moduleName as "tarot" | "runes"
    setModuleInProgressByKey((prev) => ({ ...prev, [typedModule]: true }))
    setModuleErrorByKey((prev) => ({ ...prev, [typedModule]: "" }))
    try {
      const response = await executeModule.mutateAsync({
        module: typedModule,
        payload: {
          question,
          situation: moduleSituation.trim() || undefined,
          conversation_id: selectedConversationId || undefined,
        },
      })
      setModuleResults((prev) => ({ ...prev, [typedModule]: response.interpretation }))
      void quota.refetch()
    } catch (err) {
      setModuleErrorByKey((prev) => ({
        ...prev,
        [typedModule]: err instanceof Error ? err.message : "Erreur inconnue",
      }))
    } finally {
      setModuleInProgressByKey((prev) => ({ ...prev, [typedModule]: false }))
    }
  }

  const conversationError = (history.error as ChatApiError | null) || (sendMessage.error as ChatApiError | null)
  const guidanceError = requestGuidance.error as GuidanceApiError | null
  const contextualGuidanceError = requestContextualGuidance.error as GuidanceApiError | null

  return (
    <section className="panel">
      <h1>Conversation</h1>

      <div className="action-row">
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
      {requestGuidance.isPending ? <p aria-busy="true">Génération de la guidance en cours...</p> : null}
      {guidanceError ? <p>Erreur guidance: {guidanceError.message}</p> : null}
      {!requestGuidance.data ? <p>Aucune guidance demandée pour le moment.</p> : null}
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
          placeholder="Ex: Je dois choisir entre deux opportunités."
        />
        <label htmlFor="context-objective">Objectif</label>
        <textarea
          id="context-objective"
          name="context-objective"
          value={contextObjective}
          onChange={(event) => setContextObjective(event.target.value)}
          rows={2}
          placeholder="Ex: Prendre une décision sereine."
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
        <p aria-busy="true">Génération de la guidance contextuelle en cours...</p>
      ) : null}
      {contextualGuidanceError ? <p>Erreur guidance contextuelle: {contextualGuidanceError.message}</p> : null}
      {!requestContextualGuidance.data ? <p>Aucune guidance contextuelle demandée pour le moment.</p> : null}
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
      <h2>Modules spécialisés</h2>
      <p>Tarot et runes sont activés progressivement via feature flags.</p>
      <div className="chat-form">
        <label htmlFor="module-question">Question module</label>
        <textarea
          id="module-question"
          name="module-question"
          rows={2}
          value={moduleQuestion}
          onChange={(event) => setModuleQuestion(event.target.value)}
          placeholder="Ex: Quelle direction privilégier cette semaine ?"
        />
        <label htmlFor="module-situation">Contexte (optionnel)</label>
        <textarea
          id="module-situation"
          name="module-situation"
          rows={2}
          value={moduleSituation}
          onChange={(event) => setModuleSituation(event.target.value)}
          placeholder="Ex: Décision professionnelle imminente."
        />
      </div>
      {moduleAvailability.isPending ? <p aria-busy="true">Chargement des modules...</p> : null}
      {moduleAvailability.error ? <p>Erreur modules: indisponibles pour le moment.</p> : null}
      {moduleAvailability.data ? (
        <div className="chat-form" aria-label="Modules spécialisés">
          {moduleAvailability.data.modules.map((module) => {
            const moduleName = module.module === "tarot" ? "Tarot" : "Runes"
            const isInProgress = moduleInProgressByKey[module.module] === true
            const hasCompleted = module.available && Boolean(moduleResults[module.module])
            const hasError = Boolean(moduleErrorByKey[module.module])
            let visualStatus: string = module.status
            if (hasError) {
              visualStatus = "erreur"
            }
            if (isInProgress) {
              visualStatus = "en cours"
            }
            if (hasCompleted) {
              visualStatus = "terminé"
            }
            return (
              <article key={module.module} className="card">
                <h3>{moduleName}</h3>
                <p>
                  État: <strong>{visualStatus}</strong>
                </p>
                {!module.available ? <p>Module verrouillé ({module.reason}).</p> : null}
                <button
                  type="button"
                  disabled={!module.available || isInProgress || anyModuleInProgress || quotaBlocked}
                  onClick={() => handleModuleExecution(module.module)}
                >
                  Lancer {moduleName}
                </button>
                {isInProgress ? <p aria-busy="true">Exécution en cours...</p> : null}
                {moduleErrorByKey[module.module] ? (
                  <p role="alert">Erreur {moduleName}: {moduleErrorByKey[module.module]}</p>
                ) : null}
                {moduleResults[module.module] && module.available ? (
                  <p>{moduleResults[module.module]}</p>
                ) : (
                  <p>Aucun résultat module.</p>
                )}
              </article>
            )
          })}
        </div>
      ) : null}
      {activeConversationId ? <p>Conversation active: #{activeConversationId}</p> : null}
      <h2>Historique</h2>
      {conversations.isPending ? <p>Chargement de l'historique...</p> : null}
      {conversations.error ? <p>Erreur de chargement de l'historique.</p> : null}
      {conversations.data && conversations.data.conversations.length === 0 ? (
        <p>Aucune conversation précédente.</p>
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
        <p className="state-line state-empty">Aucun message dans cette conversation.</p>
      ) : (
        <ul className="chat-list">
          {displayedMessages.map((msg) => (
            <li
              key={msg.id}
              className={`chat-item ${msg.role === "assistant" ? "chat-item-assistant" : ""}`}
              data-testid="chat-message"
            >
              <strong>{msg.role === "user" ? "Vous" : "Astrologue"}:</strong>{" "}
              <span data-testid="chat-message-content">{msg.content}</span>
            </li>
          ))}
        </ul>
      )}

      {sendMessage.isPending ? (
        <p aria-busy="true" className="state-line state-loading">
          Génération de la réponse en cours...
        </p>
      ) : null}

      {lastRecovery?.recovery_applied ? (
        <div className="chat-error" role="alert">
          <p>
            {lastRecovery.off_scope_detected
              ? "Désolé, je ne peux traiter que les sujets liés à l'astrologie."
              : "Une situation critique a été détectée."}
          </p>
          <p>Raison: {lastRecovery.recovery_reason}</p>
        </div>
      ) : null}

      {conversationError ? (
        <div className="chat-error" role="alert">
          <p>Erreur: {conversationError.message}</p>
          {conversationError.code === "quota_exceeded" && conversationError.details?.reset_at ? (
            <p>
              Quota épuisé. Réessayez après le{" "}
              {asString(conversationError.details.reset_at)
                ? new Date(asString(conversationError.details.reset_at) as string).toLocaleString()
                : "le reset"}.
            </p>
          ) : null}
          {asString(conversationError.details?.fallback_message) ? (
            <p>{asString(conversationError.details.fallback_message)}</p>
          ) : null}
          <button type="button" onClick={handleRetry} disabled={quotaBlocked || sendMessage.isPending}>
            Réessayer
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
          placeholder="Posez votre question aux astres..."
          disabled={quotaBlocked || sendMessage.isPending}
        />
        <button type="submit" disabled={!inputValue.trim() || sendMessage.isPending || quotaBlocked}>
          Envoyer
        </button>
      </form>

      {quotaBlocked ? (
        <p className="chat-error">
          Votre quota quotidien est épuisé. Veuillez revenir demain ou changer de plan.
        </p>
      ) : null}
    </section>
  )
}
