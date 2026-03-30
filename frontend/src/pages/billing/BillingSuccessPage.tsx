import React from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { LayoutDashboard, Settings, Info, CheckCircle, Clock, AlertCircle, RefreshCw } from "lucide-react"
import { useTranslation } from "../../i18n"
import { Button } from "../../components/ui/Button"
import { useBillingSubscription } from "../../api/billing"
import "./billing-return.css"

export const BillingSuccessPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { success: t } = useTranslation("billing")

  const { data: subscription, isLoading, isError, error, refetch } = useBillingSubscription()

  // Lecture du session_id pour conformité AC11 (même si purement informatif)
  const sessionId = searchParams.get("session_id")

  const status = subscription?.subscription_status
  const hasBillingError = isError || error != null

  const getStatusDisplay = () => {
    if (isLoading) {
      return {
        toneClassName: "billing-return-icon--loading",
        icon: <Clock size={40} className="animate-pulse" />,
        title: t.waitingForWebhook,
        message: t.waitingForWebhookMessage,
        showLoader: true,
        showRetry: false,
      }
    }

    if (hasBillingError) {
      return {
        toneClassName: "billing-return-icon--error",
        icon: <AlertCircle size={40} />,
        title: t.billingStateUnavailable,
        message: t.billingStateUnavailableMessage,
        showLoader: false,
        showRetry: true,
      }
    }

    if (status === "trialing") {
      return {
        toneClassName: "billing-return-icon--success",
        icon: <CheckCircle size={40} />,
        title: t.trialStarted,
        message: t.trialStartedMessage,
        showLoader: false,
        showRetry: false,
      }
    }

    if (status === "active") {
      return {
        toneClassName: "billing-return-icon--success",
        icon: <CheckCircle size={40} />,
        title: t.subscriptionActive,
        message: t.subscriptionActiveMessage,
        showLoader: false,
        showRetry: false,
      }
    }

    if (status === "incomplete") {
      return {
        toneClassName: "billing-return-icon--warning",
        icon: <Clock size={40} />,
        title: t.activationPending,
        message: t.activationPendingMessage,
        showLoader: false,
        showRetry: false,
      }
    }

    return {
      toneClassName: "billing-return-icon--pending",
      icon: <Info size={40} />,
      title: t.pendingStateTitle,
      message: t.pendingStateMessage,
      showLoader: false,
      showRetry: false,
    }
  }

  const display = getStatusDisplay()

  return (
    <div className="billing-return-container">
      <div className="billing-return-card glass-card glass-card--hero">
        {display.showLoader && <div className="billing-return-loader" />}

        <div className={`billing-return-icon ${display.toneClassName}`}>
          {display.icon}
        </div>

        <h1 className="billing-return-title">{display.title}</h1>

        <p className="billing-return-message">
          {display.message}
        </p>


        {sessionId && (
          <p className="billing-return-session">
            Session: {sessionId}
          </p>
        )}

        <div className="billing-return-actions">
          {display.showRetry && (
            <Button
              variant="ghost"
              onClick={() => {
                void refetch()
              }}
              leftIcon={<RefreshCw size={18} />}
            >
              {t.retryStatusCheck}
            </Button>
          )}
          <Button 
            variant="primary" 
            onClick={() => navigate("/dashboard")}
            leftIcon={<LayoutDashboard size={18} />}
          >
            {t.backToDashboard}
          </Button>
          <Button 
            variant="secondary" 
            onClick={() => navigate("/settings?tab=subscription")}
            leftIcon={<Settings size={18} />}
          >
            {t.viewSubscription}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default BillingSuccessPage
