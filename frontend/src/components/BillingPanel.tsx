import {
  BillingApiError,
  useChatEntitlementUsage,
  useBillingSubscription,
  useStripeCheckoutSession,
  useStripePortalSession,
} from "@api"
import { useTranslation } from "../i18n"

export function BillingPanel() {
  const t = useTranslation("admin").b2b.billing_v2
  const quota = useChatEntitlementUsage()
  const subscription = useBillingSubscription()
  const checkoutSession = useStripeCheckoutSession()
  const portalSession = useStripePortalSession()

  const portalError = portalSession.error as BillingApiError | null
  const checkoutError = checkoutSession.error as BillingApiError | null

  const handleOpenPortal = () => {
    if (portalSession.isPending) return
    portalSession.mutate(undefined, {
      onSuccess: (data) => {
        window.location.href = data.url
      },
    })
  }

  const handleOpenCheckout = () => {
    if (checkoutSession.isPending) return
    checkoutSession.mutate("basic", {
      onSuccess: (data) => {
        window.location.href = data.checkout_url
      },
    })
  }

  return (
    <section className="panel">
      <h2>{t.title}</h2>
      <p>{t.description}</p>

      {subscription.isLoading ? (
        <p aria-busy="true" className="state-line state-loading">
          Loading...
        </p>
      ) : null}
      {subscription.isError ? (
        <div className="chat-error" role="alert">
          <p>{t.error((subscription.error as BillingApiError).message)}</p>
        </div>
      ) : null}

      <div className="billing-actions mt-4">
        {subscription.data?.status !== "active" && (
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleOpenCheckout}
            disabled={checkoutSession.isPending}
          >
            {checkoutSession.isPending ? "..." : t.openCheckout}
          </button>
        )}

        <button
          type="button"
          className="btn btn-secondary"
          onClick={handleOpenPortal}
          disabled={portalSession.isPending}
        >
          {portalSession.isPending ? "..." : t.openPortal}
        </button>
      </div>

      {subscription.data?.status === "active" ? (
        <p className="state-line state-success">{t.statusActive}</p>
      ) : null}
      {quota.data && (
        <p className="state-line">
          Quota: {quota.data.consumed}/{quota.data.limit}
        </p>
      )}

      {portalError ? <p className="chat-error">{t.errorPortal(portalError.message)}</p> : null}
      {checkoutError ? <p className="chat-error">{t.errorCheckout(checkoutError.message)}</p> : null}
    </section>
  )
}
