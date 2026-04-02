import React, { useState } from "react"
import { Link } from "react-router-dom"
import { useTranslation } from "@i18n"
import { PageLayout } from "@layouts/PageLayout"
import {
  LayoutDashboard,
  MessageSquare,
  Sparkles,
  ScrollText,
  ChevronRight,
  ArrowRight,
  CheckCircle2,
} from "lucide-react"
import { Button } from "@ui/Button"
import { SupportCategorySelect } from "./support/SupportCategorySelect"
import { SupportTicketForm } from "./support/SupportTicketForm"
import { SupportTicketList } from "./support/SupportTicketList"
import "./HelpPage.css"

export default function HelpPage() {
  const { help } = useTranslation("support")
  const [selectedCategory, setSelectedCategory] = useState<{ code: string; label: string } | null>(null)
  const [ticketCreatedCount, setTicketCreatedCount] = useState(0)
  const [showSuccessMessage, setShowSuccessMessage] = useState(false)

  const handleCategorySelect = (code: string, label: string) => {
    setSelectedCategory({ code, label })
    setShowSuccessMessage(false)
  }

  const handleTicketSuccess = () => {
    setSelectedCategory(null)
    setTicketCreatedCount((prev) => prev + 1)
    setShowSuccessMessage(true)

    const element = document.getElementById("help-support-section")
    if (element && typeof element.scrollIntoView === "function") {
      element.scrollIntoView({ behavior: "smooth" })
    }
  }

  const scrollToSupport = () => {
    const element = document.getElementById("help-support-section")
    if (element && typeof element.scrollIntoView === "function") {
      element.scrollIntoView({ behavior: "smooth" })
    }
  }

  const shortcuts = [
    { icon: LayoutDashboard, key: "dashboard", to: "/today" },
    { icon: MessageSquare, key: "chat", to: "/chat" },
    { icon: Sparkles, key: "natal", to: "/natal-chart" },
    { icon: ScrollText, key: "consultations", to: "/consultations" },
  ]

  return (
    <PageLayout className="is-settings-page">
      <div className="help-bg-halo" />
      <div className="help-noise" />

      <div className="help-page">
        <section className="hero-panel glass-card">
          <div className="hero-panel__content">
            <p className="section-kicker">{help.hero.kicker}</p>
            <h1 className="help-hero__title">{help.hero.title}</h1>
            <p className="help-hero__subtitle">{help.hero.subtitle}</p>
            <div className="help-hero__actions">
              <Button
                variant="primary"
                size="lg"
                className="help-hero__primary-btn"
                onClick={scrollToSupport}
                rightIcon={<ArrowRight size={20} />}
              >
                {help.hero.primaryCta}
              </Button>
              <Button
                as={Link}
                to="/settings/subscription"
                variant="primary"
                size="lg"
                className="help-hero__primary-btn"
              >
                {help.hero.secondaryCta}
              </Button>
            </div>

            <div className="help-hero-metrics">
              {help.hero.metrics.map((metric: { label: string; value: string; description: string }) => (
                <article key={metric.label} className="help-metric-card glass-card glass-card--soft">
                  <span className="help-metric-card__label">{metric.label}</span>
                  <strong>{metric.value}</strong>
                  <p>{metric.description}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        <section className="content-grid">
          <div className="main-column">
            <section className="section-card glass-card">
              <div className="section-heading">
                <div>
                  <p className="section-kicker">{help.shortcutsKicker}</p>
                  <h2>{help.shortcutsSectionTitle}</h2>
                </div>
                <p className="section-heading__text">{help.shortcutsSectionDescription}</p>
              </div>

              <div className="shortcut-grid">
                {shortcuts.map(({ icon: Icon, key, to }) => (
                  <Link key={key} to={to} className="help-shortcut-card">
                    <span className="help-shortcut-card__icon">
                      <Icon size={20} />
                    </span>
                    <h3>{(help.shortcuts as any)[key].title}</h3>
                    <p>{(help.shortcuts as any)[key].benefit}</p>
                    <span className="help-shortcut-card__link">
                      {(help.shortcuts as any)[key].action}
                    </span>
                  </Link>
                ))}
              </div>
            </section>

            <section className="section-card glass-card">
              <div className="section-heading">
                <div>
                  <p className="section-kicker">{help.tokens.kicker}</p>
                  <h2>{help.tokens.title}</h2>
                </div>
                <p className="section-heading__text">{help.tokens.headingDescription}</p>
              </div>

              <div className="plans-layout">
                <article className="token-story glass-card glass-card--soft">
                  <div className="token-story__callout">{help.tokens.subscriptionTitle}</div>
                  <p>{help.tokens.intro}</p>
                  <p>{help.tokens.structure}</p>
                </article>

                <article className="token-story glass-card glass-card--soft">
                  <div className="token-story__callout">{help.tokens.tokenTitle}</div>
                  <p>{help.tokens.tokenExample}</p>
                  <p>{help.tokens.tokenCounting}</p>
                  <Button
                    as={Link}
                    to="/help/subscriptions"
                    variant="primary"
                    size="lg"
                    className="help-hero__primary-btn"
                    rightIcon={<ChevronRight size={18} />}
                  >
                    {help.tokens.cta}
                  </Button>
                </article>
              </div>
            </section>
          </div>

          <aside className="side-column">
            <section className="section-card glass-card section-card--compact">
              <p className="section-kicker">{help.billing.kicker}</p>
              <h2>{help.billing.title}</h2>
              <p className="section-card__text">{help.billing.intro}</p>
              <ul className="feature-list">
                {help.billing.features.map((feature: string) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>
              <Button
                as={Link}
                to="/settings/subscription"
                variant="primary"
                size="lg"
                className="help-hero__primary-btn help-billing-card__button--block"
                rightIcon={<ChevronRight size={18} />}
              >
                {help.billing.cta}
              </Button>
            </section>

            <section id="help-support-section" className="section-card glass-card section-card--compact help-support-panel">
              <p className="section-kicker">{help.categories.kicker}</p>
              <h2>{help.categories.title}</h2>
              <div className="help-hero__steps help-hero__steps--support">
                {help.hero.steps.map((step: string, i: number) => (
                  <div key={i} className="help-hero__step">
                    <span className="help-hero__step-number">{i + 1}</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>

              {showSuccessMessage ? (
                <div className="help-ticket-success">
                  <CheckCircle2 size={24} />
                  {help.form.successMessage}
                </div>
              ) : null}

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
          </aside>
        </section>

        <section className="section-card glass-card section-card--compact help-tickets-section">
          <p className="section-kicker">{help.tickets.kicker}</p>
          <h2>{help.tickets.title}</h2>
          <SupportTicketList refreshTrigger={ticketCreatedCount} />
        </section>
      </div>
    </PageLayout>
  )
}
