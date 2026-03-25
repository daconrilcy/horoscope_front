import type { AstrologyLang } from "./astrology"

export type BillingTranslation = {
  success: {
    title: string
    message: string
    backToDashboard: string
    viewSubscription: string
    waitingForWebhook: string
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
    title: billingData.success[lang].title,
    message: billingData.success[lang].message,
    backToDashboard: billingData.success[lang].backToDashboard,
    viewSubscription: billingData.success[lang].viewSubscription,
    waitingForWebhook: billingData.success[lang].waitingForWebhook,
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
      title: "Paiement réussi !",
      message: "Votre paiement est en cours de traitement. Votre abonnement sera activé automatiquement dans quelques instants. Vous pouvez retourner au tableau de bord.",
      backToDashboard: "Retour au tableau de bord",
      viewSubscription: "Voir mon abonnement",
      waitingForWebhook: "Paiement en cours de confirmation...",
    },
    en: {
      title: "Payment Successful!",
      message: "Your payment is being processed. Your subscription will be activated automatically in a few moments. You can return to the dashboard.",
      backToDashboard: "Back to Dashboard",
      viewSubscription: "View my subscription",
      waitingForWebhook: "Payment confirmation in progress...",
    },
    es: {
      title: "¡Pago exitoso!",
      message: "Su pago está siendo procesado. Su suscripción se activará automáticamente en unos momentos. Puede volver al panel de control.",
      backToDashboard: "Volver al panel",
      viewSubscription: "Ver mi suscripción",
      waitingForWebhook: "Confirmación de pago en curso...",
    },
  } as Record<
    AstrologyLang,
    {
      title: string
      message: string
      backToDashboard: string
      viewSubscription: string
      waitingForWebhook: string
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
