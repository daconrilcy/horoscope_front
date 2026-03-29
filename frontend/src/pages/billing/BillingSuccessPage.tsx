import React, { useEffect } from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { LayoutDashboard, Settings, Info, CheckCircle, Clock } from "lucide-react"
import { useTranslation } from "../../i18n"
import { Button } from "../../components/ui/Button"
import { useBillingSubscription } from "../../api/billing"
import "./billing-return.css"

const BillingSuccessPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { success: t } = useTranslation("billing")

  // Story 61.55 - Real-time subscription status
  const { data: subscription, isLoading, refetch } = useBillingSubscription()
  const isTrial = searchParams.get("is_trial") === "true"
  
  // Lecture du session_id pour conformité AC11 (même si purement informatif)
  const sessionId = searchParams.get("session_id")

  // On rafraîchit au montage pour être sûr d'avoir le dernier état webhook
  useEffect(() => {
    refetch()
  }, [refetch])

  const status = subscription?.subscription_status

  const getStatusDisplay = () => {
    if (isLoading) {
      return {
        icon: <Clock size={40} className="animate-pulse" />,
        title: t.waitingForWebhook,
        message: t.message,
      }
    }

    if (status === "trialing" || isTrial) {
      return {
        icon: <CheckCircle size={40} className="text-success" />,
        title: t.trialTitle,
        message: t.trialMessage,
      }
    }

    if (status === "active") {
      return {
        icon: <CheckCircle size={40} className="text-success" />,
        title: t.subscriptionActive,
        message: t.message,
      }
    }

    if (status === "incomplete") {
      return {
        icon: <Clock size={40} className="text-warning" />,
        title: t.activationPending,
        message: t.message,
      }
    }

    return {
      icon: <Info size={40} />,
      title: t.waitingForWebhook,
      message: t.message,
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
