import React, { useState } from "react"
import { Link } from "react-router-dom"
import { useTranslation } from "@i18n"
import { PageLayout } from "@layouts/PageLayout"
import { 
  LayoutDashboard, 
  MessageSquare, 
  Sparkles, 
  ScrollText, 
  Check,
  ChevronRight,
  ArrowRight,
  CreditCard,
  CheckCircle2
} from "lucide-react"
import { Button } from "@ui/Button"
import { SupportCategorySelect } from "./support/SupportCategorySelect"
import { SupportTicketForm } from "./support/SupportTicketForm"
import { SupportTicketList } from "./support/SupportTicketList"
import "./HelpPage.css"

export default function HelpPage() {
  const { help } = useTranslation('support')
  const [selectedCategory, setSelectedCategory] = useState<{ code: string; label: string } | null>(null)
  const [ticketCreatedCount, setTicketCreatedCount] = useState(0)
  const [showSuccessMessage, setShowSuccessMessage] = useState(false)

  const handleCategorySelect = (code: string, label: string) => {
    setSelectedCategory({ code, label })
    setShowSuccessMessage(false)
  }

  const handleTicketSuccess = () => {
    setSelectedCategory(null)
    setTicketCreatedCount(prev => prev + 1)
    setShowSuccessMessage(true)
    
    // Scroll to the success message
    const element = document.getElementById("help-support-section")
    if (element && typeof element.scrollIntoView === 'function') {
      element.scrollIntoView({ behavior: "smooth" })
    }
  }

  const scrollToSupport = () => {
    const element = document.getElementById("help-support-section")
    if (element && typeof element.scrollIntoView === 'function') {
      element.scrollIntoView({ behavior: "smooth" })
    }
  }

  const shortcuts = [
    { icon: LayoutDashboard, key: 'dashboard', to: '/today' },
    { icon: MessageSquare, key: 'chat', to: '/chat' },
    { icon: Sparkles, key: 'natal', to: '/natal-chart' },
    { icon: ScrollText, key: 'consultations', to: '/consultations' },
  ]

  const tokenPlans = ['free', 'basic', 'premium'] as const

  return (
    <PageLayout title={help.pageTitle} className="is-settings-page">
      <div className="help-bg-halo" />
      <div className="help-noise" />

      <div className="help-page">
        {/* AC1 — Hero d'orientation premium */}
        <header className="help-hero">
          <h1 className="help-hero__title">{help.hero.title}</h1>
          <p className="help-hero__subtitle">{help.hero.subtitle}</p>
          <div className="help-hero__actions">
            <Button 
              variant="primary" 
              size="lg"
              onClick={scrollToSupport}
              rightIcon={<ArrowRight size={20} />}
            >
              {help.hero.primaryCta}
            </Button>
            <Button 
              as={Link}
              to="/settings/subscription"
              variant="ghost" 
              size="lg"
            >
              {help.hero.secondaryCta}
            </Button>
          </div>

          <div className="help-hero__steps">
            {help.hero.steps.map((step: string, i: number) => (
              <div key={i} className="help-hero__step">
                <span className="help-hero__step-number">{i + 1}</span>
                <span>{step}</span>
              </div>
            ))}
          </div>
        </header>

        {/* AC2 — Raccourcis vers les fonctionnalités clés */}
        <section className="help-section">
          <div className="help-shortcuts-grid">
            {shortcuts.map(({ icon: Icon, key, to }) => (
              <Link key={key} to={to} className="shortcut-card">
                <div className="shortcut-card__icon"><Icon size={24} /></div>
                <div className="shortcut-card__content">
                  <span className="shortcut-card__title">{(help.shortcuts as any)[key].title}</span>
                  <span className="shortcut-card__benefit">{(help.shortcuts as any)[key].benefit}</span>
                </div>
                <span className="shortcut-card__action">
                  {(help.shortcuts as any)[key].action} <ChevronRight size={16} />
                </span>
              </Link>
            ))}
          </div>
        </section>

        {/* AC3 — Bloc tokens/quota comparatif */}
        <section className="help-section">
          <div className="help-section__header">
            <h2 className="help-section__title">{help.tokens.title}</h2>
          </div>
          <p className="help-card__desc">{help.tokens.intro}</p>
          <div className="tokens-grid">
            {tokenPlans.map((plan) => (
              <div 
                key={plan} 
                className={`token-plan-card ${plan === 'premium' ? 'token-plan-card--premium' : ''}`}
              >
                <div className="token-plan-card__header">
                  <span className="token-plan-card__name">{(help.tokens.plans as any)[plan].name}</span>
                  <span className="token-plan-card__quota">{(help.tokens.plans as any)[plan].quota}</span>
                </div>
                <ul className="token-plan-card__features">
                  {(help.tokens.plans as any)[plan].features.map((feature: string, i: number) => (
                    <li key={i} className="token-plan-card__feature">
                      <Check size={16} className="token-plan-card__feature-icon" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <span className="token-plan-card__tagline">{(help.tokens.plans as any)[plan].tagline}</span>
              </div>
            ))}
          </div>
        </section>

        {/* AC4 — Carte abonnement/facturation dédiée */}
        <section className="help-section">
          <div className="settings-card help-billing-card">
            <div className="help-billing-card__icon">
              <CreditCard size={32} />
            </div>
            <div className="help-billing-card__content">
              <h3 className="help-billing-card__title">{help.billing.title}</h3>
              <ul className="help-billing-card__features">
                {help.billing.features.map((f: string, i: number) => (
                  <li key={i} className="help-billing-card__feature">
                    <span className="help-billing-card__dot" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>
            <Button 
              as={Link}
              to="/settings/subscription"
              variant="ghost" 
              rightIcon={<ChevronRight size={18} />}
            >
              {help.billing.cta}
            </Button>
          </div>
        </section>

        <hr className="settings-divider" />

        {/* Support Ticketing */}
        <section id="help-support-section" className="help-section">
          <h2 className="help-section__title">{help.categories.title}</h2>
          
          {showSuccessMessage && (
            <div className="help-ticket-success">
              <CheckCircle2 size={24} />
              {help.form.successMessage}
            </div>
          )}

          {!selectedCategory ? (
            <SupportCategorySelect onSelect={handleCategorySelect} />
          ) : (
            <div className="ticket-form-card">
              <SupportTicketForm 
                category={selectedCategory} 
                onCancel={() => setSelectedCategory(null)}
                onSuccess={handleTicketSuccess}
              />
            </div>
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
