import React from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { LayoutDashboard, Settings, Info, CheckCircle, Clock } from "lucide-react"
import { useTranslation } from "../../i18n"
import { Button } from "../../components/ui/Button"
import { useBillingSubscription } from "../../api/billing"
import "./billing-return.css"

export const BillingSuccessPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { success: t } = useTranslation("billing")

  const { data: subscription, isLoading } = useBillingSubscription()

  // Lecture du session_id pour conformité AC11 (même si purement informatif)
  const sessionId = searchParams.get("session_id")

  const status = subscription?.subscription_status

  const getStatusDisplay = () => {
    if (isLoading) {
      return {
        icon: <Clock size={40} className="animate-pulse" />,
        title: t.waitingForWebhook,
        message: t.waitingForWebhookMessage,
      }
    }

    if (status === "trialing") {
      return {
        icon: <CheckCircle size={40} className="text-success" />,
        title: t.trialStarted,
        message: t.trialStartedMessage,
      }
    }

    if (status === "active") {
      return {
        icon: <CheckCircle size={40} className="text-success" />,
        title: t.subscriptionActive,
        message: t.subscriptionActiveMessage,
      }
    }

    if (status === "incomplete") {
      return {
        icon: <Clock size={40} className="text-warning" />,
        title: t.activationPending,
        message: t.activationPendingMessage,
      }
    }

    return {
      icon: <Info size={40} />,
      title: t.waitingForWebhook,
      message: t.waitingForWebhookMessage,
    }
  }

  const display = getStatusDisplay()

  return (
    <div className="billing-return-container">
      <div className="billing-return-card glass-card glass-card--hero">
        <div className="billing-return-loader" />

        <div className="billing-return-icon">
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
