import { PageLayout } from "@layouts/PageLayout"
import "./HelpPage.css"

export function SubscriptionGuidePage() {
  return (
    <PageLayout className="is-settings-page">
      <div className="help-bg-halo" />
      <div className="help-noise" />
      <div className="help-page">
        <section className="help-section">
          <div className="settings-card help-placeholder-card">
            <h1 className="help-section__title">Guide des abonnements</h1>
            <p className="help-placeholder-card__text">
              Cette page sera dédiée à la description détaillée de chaque abonnement.
            </p>
          </div>
        </section>
      </div>
    </PageLayout>
  )
}
