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
      message: "Merci pour votre confiance. Votre abonnement a été mis à jour avec succès. Vous pouvez maintenant profiter de toutes les fonctionnalités premium.",
      backToDashboard: "Aller au tableau de bord",
      viewSubscription: "Voir mon abonnement",
      waitingForWebhook: "Finalisation de votre commande...",
    },
    en: {
      title: "Payment Successful!",
      message: "Thank you for your trust. Your subscription has been successfully updated. You can now enjoy all premium features.",
      backToDashboard: "Go to Dashboard",
      viewSubscription: "View my subscription",
      waitingForWebhook: "Finalizing your order...",
    },
    es: {
      title: "¡Pago exitoso!",
      message: "Gracias por su confianza. Su suscripción ha sido actualizada con éxito. Ahora peut disfrutar de todas las funciones premium.",
      backToDashboard: "Ir al panel de control",
      viewSubscription: "Ver mi suscripción",
      waitingForWebhook: "Finalizando su pedido...",
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
      backToSettings: "Retour aux paramètres",
      tryAgain: "Réessayer",
    },
    en: {
      title: "Payment Cancelled",
      message: "The payment process was interrupted. No amount has been debited from your account.",
      backToSettings: "Back to Settings",
      tryAgain: "Try Again",
    },
    es: {
      title: "Pago cancelado",
      message: "El proceso de pago fue interrumpido. No se ha debitado ningún importe de su cuenta.",
      backToSettings: "Volver a ajustes",
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
