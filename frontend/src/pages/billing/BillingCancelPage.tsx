import React from "react"
import { useNavigate } from "react-router-dom"
import { XCircle, RefreshCw, Settings } from "lucide-react"
import { useTranslation } from "../../i18n"
import { Button } from "../../components/ui/Button/Button"
import "./billing-return.css"

export const BillingCancelPage: React.FC = () => {
  const navigate = useNavigate()
  const { cancel: t } = useTranslation("billing")

  return (
    <div className="billing-return-container">
      <div className="billing-return-card glass-card glass-card--hero">
        <div className="billing-return-icon billing-return-icon--cancel">
          <XCircle size={40} />
        </div>
        <h1 className="billing-return-title">{t.title}</h1>
        <p className="billing-return-message">{t.message}</p>
        <div className="billing-return-actions">
          <Button 
            variant="primary" 
            onClick={() => navigate("/settings?tab=subscription")}
            leftIcon={<RefreshCw size={18} />}
          >
            {t.tryAgain}
          </Button>
          <Button 
            variant="secondary" 
            onClick={() => navigate("/settings")}
            leftIcon={<Settings size={18} />}
          >
            {t.backToSettings}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default BillingCancelPage
