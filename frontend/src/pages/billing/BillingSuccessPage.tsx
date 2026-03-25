import React, { useEffect, useState } from "react"
import { useNavigate } from "react-router-dom"
import { CheckCircle, LayoutDashboard, Settings } from "lucide-react"
import { useTranslation } from "../../i18n"
import { Button } from "../../components/ui/Button/Button"
import "./billing-return.css"

export const BillingSuccessPage: React.FC = () => {
  const navigate = useNavigate()
  const { success: t } = useTranslation("billing")
  const [isWaiting, setIsWaiting] = useState(true)

  // Simulation d'une attente pour laisser le temps au webhook de passer
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsWaiting(false)
    }, 3000)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="billing-return-container">
      <div className="billing-return-card glass-card glass-card--hero">
        {isWaiting ? (
          <>
            <div className="billing-return-loader" />
            <p className="billing-return-message">{t.waitingForWebhook}</p>
          </>
        ) : (
          <>
            <div className="billing-return-icon billing-return-icon--success">
              <CheckCircle size={40} />
            </div>
            <h1 className="billing-return-title">{t.title}</h1>
            <p className="billing-return-message">{t.message}</p>
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
          </>
        )}
      </div>
    </div>
  )
}

export default BillingSuccessPage
