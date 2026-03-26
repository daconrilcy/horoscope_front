import { useState } from "react"

import {
  BillingApiError,
  type BillingCheckoutData,
  type BillingPlanChangeData,
  useChatEntitlementUsage,
  useChangePlan,
  useBillingSubscription,
  useCheckoutEntryPlan,
  useRetryPayment,
} from "@api"
import { useTranslation } from "../i18n"

export function BillingPanel() {
  const t = useTranslation("admin").b2b.billing_v2
  const quota = useChatEntitlementUsage()
  const subscription = useBillingSubscription()
  const checkout = useCheckoutEntryPlan()
  const retry = useRetryPayment()
  const changePlan = useChangePlan()

  const [paymentToken, setPaymentToken] = useState("pm_card_ok")
  const [targetPlanCode, setTargetPlanCode] = useState("basic-entry")

  const lastCheckoutResult = checkout.data
  const lastRetryResult = retry.data
  const checkoutError = checkout.error as BillingApiError | null
  const retryError = retry.error as BillingApiError | null
  const changePlanError = changePlan.error as BillingApiError | null

  const handleCheckout = () => {
    checkout.mutate({
      plan_code: "basic-entry",
      payment_method_token: paymentToken,
    })
  }

  const handleRetry = () => {
    if (retry.isPending) return
    retry.mutate({
      plan_code: "basic-entry",
      payment_method_token: paymentToken,
    })
  }

  const handleChangePlan = () => {
    changePlan.mutate({ target_plan_code: targetPlanCode })
  }

  const failedReason =
    lastCheckoutResult?.subscription.failure_reason ||
    lastRetryResult?.subscription.failure_reason ||
    subscription.data?.failure_reason
  const showRetryAction =
    lastCheckoutResult?.payment_status === "failed" || lastRetryResult?.payment_status === "failed"
  const targetPlanLimitLabel = targetPlanCode === "premium-unlimited" ? "1000 messages/jour" : "5 messages/jour"

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

      <div className="action-row mt-6">
        <label htmlFor="billing-payment-token">{t.paymentSimLabel}</label>
        <select
          id="billing-payment-token"
          value={paymentToken}
          onChange={(e) => setPaymentToken(e.target.value)}
        >
          <option value="pm_card_ok">{t.paymentOptions.ok}</option>
          <option value="pm_fail">{t.paymentOptions.fail}</option>
        </select>
      </div>

      <div className="billing-actions mt-4">
        {subscription.data?.status !== "active" && (
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleCheckout}
            disabled={checkout.isPending || retry.isPending}
          >
            Subscribe Basic
          </button>
        )}

        {showRetryAction && (
          <button
            type="button"
            className="btn btn-danger ml-2"
            onClick={handleRetry}
            disabled={retry.isPending}
          >
            Retry Payment
          </button>
        )}
      </div>

      {subscription.data?.status === "active" && (
        <div className="plan-change-section mt-8 border-t pt-6">
          <label htmlFor="billing-target-plan">{t.changePlanLabel}</label>
          <div className="action-row">
            <select
              id="billing-target-plan"
              value={targetPlanCode}
              onChange={(e) => setTargetPlanCode(e.target.value)}
            >
              <option value="basic-entry">{t.planOptions.basic}</option>
              <option value="premium-unlimited">{t.planOptions.premium}</option>
            </select>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleChangePlan}
              disabled={changePlan.isPending}
            >
              Apply Change
            </button>
          </div>
          <p className="state-line">{t.impactQuota(targetPlanLimitLabel)}</p>
        </div>
      )}

      {subscription.data?.status === "active" ? (
        <p className="state-line state-success">{t.statusActive}</p>
      ) : null}
      {quota.data && (
        <p className="state-line">
          Quota: {quota.data.consumed}/{quota.data.limit}
        </p>
      )}

      {failedReason ? <p className="state-line state-empty">{t.failedReason(failedReason)}</p> : null}
      {checkoutError ? <p className="chat-error">{t.errorCheckout(checkoutError.message)}</p> : null}
      {retryError ? <p className="chat-error">{t.errorRetry(retryError.message)}</p> : null}
      {changePlanError ? <p className="chat-error">{t.errorChange(changePlanError.message)}</p> : null}
    </section>
  )
}
