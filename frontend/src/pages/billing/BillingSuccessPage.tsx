import React from "react"
import { useNavigate, useSearchParams } from "react-router-dom"
import { LayoutDashboard, Settings, Info } from "lucide-react"
import { useTranslation } from "../../i18n"
import { Button } from "../../components/ui/Button/Button"
import "./billing-return.css"

export const BillingSuccessPage: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { success: t } = useTranslation("billing")
  
  // Lecture du session_id pour conformité AC11 (même si purement informatif)
  const sessionId = searchParams.get("session_id")

  return (
    <div className="billing-return-container">
      <div className="billing-return-card glass-card glass-card--hero">
        <div className="billing-return-loader" />
        
        <div className="billing-return-icon billing-return-icon--info">
          <Info size={40} />
        </div>

        <h1 className="billing-return-title">{t.waitingForWebhook}</h1>
        
        <p className="billing-return-message">
          {t.message}
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
