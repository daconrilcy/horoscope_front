import type { AstrologyLang } from "./astrology"

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
