import type { AstrologyLang } from "./astrology"

export type UpgradeBenefitKey =
  | "upgrade.horoscope_daily.full_access"
  | "upgrade.natal_chart_long.full_interpretation"
  | "upgrade.astrologer_chat.unlimited_messages"

export const UPGRADE_BENEFIT_LABELS: Record<UpgradeBenefitKey, Record<AstrologyLang, string>> = {
  "upgrade.horoscope_daily.full_access": {
    fr: "Accéder à l'horoscope complet",
    en: "Get full horoscope",
    es: "Obtener el horóscopo completo",
  },
  "upgrade.natal_chart_long.full_interpretation": {
    fr: "Débloquer l'interprétation complète",
    en: "Unlock full interpretation",
    es: "Desbloquear la interpretación completa",
  },
  "upgrade.astrologer_chat.unlimited_messages": {
    fr: "Échanger sans limite",
    en: "Chat without limits",
    es: "Chatear sin límites",
  },
}

export function getUpgradeBenefitLabel(key: string, lang: AstrologyLang): string {
  const entry = UPGRADE_BENEFIT_LABELS[key as UpgradeBenefitKey]
  if (!entry) return key
  return entry[lang] ?? entry["fr"]
}

export type ChatQuotaMessages = {
  remaining: (remaining: number, limit: number) => string
  exhausted: (date: string) => string
  resetDate: (date: string) => string
}

const CHAT_QUOTA_MESSAGES: Record<AstrologyLang, ChatQuotaMessages> = {
  fr: {
    remaining: (r, l) => `${r}/${l} message(s) restant(s)`,
    exhausted: (d) => `Quota atteint — rechargement le ${d}`,
    resetDate: (d) => `Rechargement le ${d}`,
  },
  en: {
    remaining: (r, l) => `${r}/${l} message(s) left`,
    exhausted: (d) => `Quota reached — resets on ${d}`,
    resetDate: (d) => `Resets on ${d}`,
  },
  es: {
    remaining: (r, l) => `${r}/${l} mensaje(s) restante(s)`,
    exhausted: (d) => `Cuota alcanzada — reinicia el ${d}`,
    resetDate: (d) => `Reinicio el ${d}`,
  },
}

export function getChatQuotaMessages(lang: AstrologyLang): ChatQuotaMessages {
  return CHAT_QUOTA_MESSAGES[lang] ?? CHAT_QUOTA_MESSAGES.fr
}

export type BillingTranslation = {
  success: {
    trialStarted: string
    trialStartedMessage: string
    activationPending: string
    activationPendingMessage: string
    subscriptionActive: string
    subscriptionActiveMessage: string
    backToDashboard: string
    viewSubscription: string
    waitingForWebhook: string
    waitingForWebhookMessage: string
    billingStateUnavailable: string
    billingStateUnavailableMessage: string
    retryStatusCheck: string
    pendingStateTitle: string
    pendingStateMessage: string
  }
  cancel: {
    title: string
    message: string
    backToSettings: string
    tryAgain: string
  }
}

export const billingTranslations = (lang: AstrologyLang): BillingTranslation => ({
  success: {
    trialStarted: billingData.success[lang].trialStarted,
    trialStartedMessage: billingData.success[lang].trialStartedMessage,
    activationPending: billingData.success[lang].activationPending,
    activationPendingMessage: billingData.success[lang].activationPendingMessage,
    subscriptionActive: billingData.success[lang].subscriptionActive,
    subscriptionActiveMessage: billingData.success[lang].subscriptionActiveMessage,
    backToDashboard: billingData.success[lang].backToDashboard,
    viewSubscription: billingData.success[lang].viewSubscription,
    waitingForWebhook: billingData.success[lang].waitingForWebhook,
    waitingForWebhookMessage: billingData.success[lang].waitingForWebhookMessage,
    billingStateUnavailable: billingData.success[lang].billingStateUnavailable,
    billingStateUnavailableMessage: billingData.success[lang].billingStateUnavailableMessage,
    retryStatusCheck: billingData.success[lang].retryStatusCheck,
    pendingStateTitle: billingData.success[lang].pendingStateTitle,
    pendingStateMessage: billingData.success[lang].pendingStateMessage,
  },
  cancel: {
    title: billingData.cancel[lang].title,
    message: billingData.cancel[lang].message,
    backToSettings: billingData.cancel[lang].backToSettings,
    tryAgain: billingData.cancel[lang].tryAgain,
  },
})

const billingData = {
  success: {
    fr: {
      trialStarted: "Essai gratuit démarré",
      trialStartedMessage:
        "Votre essai gratuit a bien démarré. L'accès produit suit désormais le statut Stripe réel.",
      activationPending: "Activation en cours de confirmation",
      activationPendingMessage:
        "Votre souscription est en attente de confirmation. Le premier paiement doit encore être validé par Stripe.",
      subscriptionActive: "Abonnement activé",
      subscriptionActiveMessage:
        "Votre abonnement est maintenant actif. Vous pouvez utiliser les fonctionnalités correspondant à votre plan.",
      backToDashboard: "Retour au tableau de bord",
      viewSubscription: "Voir mon abonnement",
      waitingForWebhook: "Paiement en cours de confirmation...",
      waitingForWebhookMessage:
        "Nous attendons encore la réconciliation Stripe. Rechargez cette page dans quelques instants si le statut n'a pas évolué.",
      billingStateUnavailable: "Vérification de l'état billing impossible",
      billingStateUnavailableMessage:
        "Nous n'avons pas pu récupérer l'état de votre abonnement pour le moment. Vérifiez à nouveau dans quelques instants.",
      retryStatusCheck: "Réessayer",
      pendingStateTitle: "Statut billing en attente de synchronisation",
      pendingStateMessage:
        "Le backend n'a pas encore confirmé un état exploitable. Revenez dans quelques instants pour vérifier la réconciliation.",
    },
    en: {
      trialStarted: "Free trial started",
      trialStartedMessage:
        "Your free trial has started. Product access now follows the real Stripe subscription status.",
      activationPending: "Activation pending confirmation",
      activationPendingMessage:
        "Your subscription is still awaiting confirmation. Stripe must finish validating the first payment.",
      subscriptionActive: "Subscription activated",
      subscriptionActiveMessage:
        "Your subscription is now active. You can use the features included in your plan.",
      backToDashboard: "Back to Dashboard",
      viewSubscription: "View my subscription",
      waitingForWebhook: "Payment confirmation in progress...",
      waitingForWebhookMessage:
        "Stripe reconciliation is still in progress. Reload this page in a moment if the status has not changed yet.",
      billingStateUnavailable: "Unable to verify billing status",
      billingStateUnavailableMessage:
        "We could not retrieve your subscription state right now. Please try again in a moment.",
      retryStatusCheck: "Try again",
      pendingStateTitle: "Billing status pending synchronization",
      pendingStateMessage:
        "The backend has not confirmed a usable state yet. Check back in a moment for Stripe reconciliation.",
    },
    es: {
      trialStarted: "Prueba gratuita iniciada",
      trialStartedMessage:
        "Su prueba gratuita ha comenzado. El acceso al producto ahora sigue el estado real de suscripción en Stripe.",
      activationPending: "Activación pendiente de confirmación",
      activationPendingMessage:
        "Su suscripción sigue pendiente de confirmación. Stripe debe validar primero el pago inicial.",
      subscriptionActive: "Suscripción activada",
      subscriptionActiveMessage:
        "Su suscripción ya está activa. Puede usar las funciones incluidas en su plan.",
      backToDashboard: "Volver al panel",
      viewSubscription: "Ver mi suscripción",
      waitingForWebhook: "Confirmación de pago en curso...",
      waitingForWebhookMessage:
        "La reconciliación de Stripe sigue en curso. Recargue esta página en unos instantes si el estado no cambia todavía.",
      billingStateUnavailable: "No se puede verificar el estado de facturación",
      billingStateUnavailableMessage:
        "No pudimos recuperar el estado de su suscripción por ahora. Inténtelo de nuevo en unos instantes.",
      retryStatusCheck: "Reintentar",
      pendingStateTitle: "Estado de facturación pendiente de sincronización",
      pendingStateMessage:
        "El backend todavía no ha confirmado un estado utilizable. Vuelva dentro de unos instantes para comprobar la reconciliación.",
    },
  } as Record<
    AstrologyLang,
    {
      trialStarted: string
      trialStartedMessage: string
      activationPending: string
      activationPendingMessage: string
      subscriptionActive: string
      subscriptionActiveMessage: string
      backToDashboard: string
      viewSubscription: string
      waitingForWebhook: string
      waitingForWebhookMessage: string
      billingStateUnavailable: string
      billingStateUnavailableMessage: string
      retryStatusCheck: string
      pendingStateTitle: string
      pendingStateMessage: string
    }
  >,
  cancel: {
    fr: {
      title: "Paiement annulé",
      message: "Le processus de paiement a été interrompu. Aucun montant n'a été débité de votre compte.",
      backToSettings: "Retour aux abonnements",
      tryAgain: "Réessayer",
    },
    en: {
      title: "Payment Cancelled",
      message: "The payment process was interrupted. No amount has been debited from your account.",
      backToSettings: "Back to subscriptions",
      tryAgain: "Try Again",
    },
    es: {
      title: "Pago cancelado",
      message: "El proceso de pago fue interrumpido. No se ha debitado ningún importe de su cuenta.",
      backToSettings: "Volver a suscripciones",
      tryAgain: "Reintentar",
    },
  } as Record<
    AstrologyLang,
    {
      title: string
      message: string
      backToSettings: string
      tryAgain: string
    }
  >,
}
