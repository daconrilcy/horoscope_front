import React, { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useTranslation } from "@i18n"
import { PageLayout } from "@layouts/PageLayout"
import { 
  LayoutDashboard, 
  MessageSquare, 
  Sparkles, 
  ScrollText, 
  Coins, 
  CreditCard,
  ExternalLink
} from "lucide-react"
import { Button } from "@ui/Button"
import { SupportCategorySelect } from "./support/SupportCategorySelect"
import { SupportTicketForm } from "./support/SupportTicketForm"
import { SupportTicketList } from "./support/SupportTicketList"
import "./HelpPage.css"

export default function HelpPage() {
  const { help } = useTranslation('support')
  const navigate = useNavigate()
  const [selectedCategory, setSelectedCategory] = useState<{ code: string; label: string } | null>(null)
  const [ticketCreatedCount, setTicketCreatedCount] = useState(0)

  const handleCategorySelect = (code: string, label: string) => {
    setSelectedCategory({ code, label })
  }

  const handleTicketSuccess = () => {
    setSelectedCategory(null)
    setTicketCreatedCount(prev => prev + 1)
  }

  return (
    <PageLayout title={help.pageTitle} className="help-page-container">
      <div className="help-page">
        {/* Section 1: How it works */}
        <section className="help-section">
          <h2 className="help-section__title">{help.sections.howItWorks.title}</h2>
          <div className="help-grid">
            <div className="help-card">
              <div className="help-card__icon"><LayoutDashboard size={32} /></div>
              <h3 className="help-card__title">{help.sections.howItWorks.items.dashboard.title}</h3>
              <p className="help-card__desc">{help.sections.howItWorks.items.dashboard.desc}</p>
            </div>
            <div className="help-card">
              <div className="help-card__icon"><MessageSquare size={32} /></div>
              <h3 className="help-card__title">{help.sections.howItWorks.items.chat.title}</h3>
              <p className="help-card__desc">{help.sections.howItWorks.items.chat.desc}</p>
            </div>
            <div className="help-card">
              <div className="help-card__icon"><Sparkles size={32} /></div>
              <h3 className="help-card__title">{help.sections.howItWorks.items.natal.title}</h3>
              <p className="help-card__desc">{help.sections.howItWorks.items.natal.desc}</p>
            </div>
            <div className="help-card">
              <div className="help-card__icon"><ScrollText size={32} /></div>
              <h3 className="help-card__title">{help.sections.howItWorks.items.consultations.title}</h3>
              <p className="help-card__desc">{help.sections.howItWorks.items.consultations.desc}</p>
            </div>
          </div>
        </section>

        {/* Section 2: Tokens */}
        <section className="help-section">
          <div className="help-section__header">
            <Coins className="help-section__icon" size={24} />
            <h2 className="help-section__title">{help.sections.tokens.title}</h2>
          </div>
          <div className="help-card help-card--wide">
            <p className="help-card__desc">{help.sections.tokens.intro}</p>
            <table className="tokens-table">
              <tbody>
                <tr><td>{help.sections.tokens.plans.free}</td></tr>
                <tr><td>{help.sections.tokens.plans.basic}</td></tr>
                <tr><td>{help.sections.tokens.plans.premium}</td></tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Section 3: Subscriptions */}
        <section className="help-section">
          <div className="help-section__header">
            <CreditCard className="help-section__icon" size={24} />
            <h2 className="help-section__title">{help.sections.subscriptions.title}</h2>
          </div>
          <div className="subscriptions-cta">
            <Button 
              variant="primary" 
              rightIcon={<ExternalLink size={18} />}
              onClick={() => navigate("/settings/subscription")}
            >
              {help.sections.subscriptions.cta}
            </Button>
          </div>
        </section>

        <hr className="settings-divider" />

        {/* Support Ticketing */}
        <section className="help-section">
          <h2 className="help-section__title">{help.categories.title}</h2>
          {!selectedCategory ? (
            <SupportCategorySelect onSelect={handleCategorySelect} />
          ) : (
            <SupportTicketForm 
              category={selectedCategory} 
              onCancel={() => setSelectedCategory(null)}
              onSuccess={handleTicketSuccess}
            />
          )}
        </section>

        {/* Ticket List */}
        <section className="help-section">
          <h2 className="help-section__title">{help.tickets.title}</h2>
          <SupportTicketList refreshTrigger={ticketCreatedCount} />
        </section>
      </div>
    </PageLayout>
  )
}
