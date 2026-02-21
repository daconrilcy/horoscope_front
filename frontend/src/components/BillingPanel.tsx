import { useMemo, useState } from "react"

import {
  BillingApiError,
  type BillingCheckoutData,
  type BillingPlanChangeData,
  useBillingQuota,
  useChangePlan,
  useBillingSubscription,
  useCheckoutEntryPlan,
  useRetryCheckout,
} from "../api/billing"

export function BillingPanel() {
  const subscription = useBillingSubscription()
  const checkout = useCheckoutEntryPlan()
  const retryCheckout = useRetryCheckout()
  const changePlan = useChangePlan()
  const quota = useBillingQuota()
  const [paymentToken, setPaymentToken] = useState("pm_card_ok")
  const [targetPlanCode, setTargetPlanCode] = useState("premium-unlimited")
  const [lastFailedIdempotencyKey, setLastFailedIdempotencyKey] = useState<string | null>(null)
  const [lastCheckoutResult, setLastCheckoutResult] = useState<BillingCheckoutData | null>(null)
  const [lastRetryResult, setLastRetryResult] = useState<BillingCheckoutData | null>(null)
  const [lastPlanChangeResult, setLastPlanChangeResult] = useState<BillingPlanChangeData | null>(null)

  const checkoutError = checkout.error as BillingApiError | null
  const retryError = retryCheckout.error as BillingApiError | null
  const changePlanError = changePlan.error as BillingApiError | null

  const busy = checkout.isPending || retryCheckout.isPending || changePlan.isPending
  const failedReason = useMemo(() => {
    if (lastRetryResult?.subscription.failure_reason) {
      return lastRetryResult.subscription.failure_reason
    }
    if (lastCheckoutResult?.subscription.failure_reason) {
      return lastCheckoutResult.subscription.failure_reason
    }
    return subscription.data?.failure_reason ?? null
  }, [lastCheckoutResult, lastRetryResult, subscription.data])

  const showRetryAction =
    lastCheckoutResult?.payment_status === "failed" || lastRetryResult?.payment_status === "failed"
  const targetPlanLimitLabel = targetPlanCode === "premium-unlimited" ? "1000 messages/jour" : "5 messages/jour"

  return (
    <section className="panel">
      <h2>Abonnement</h2>
      <p>Souscrivez au plan Basic pour activer le service payant.</p>

      {subscription.isLoading ? <p aria-busy="true">Chargement du statut abonnement...</p> : null}
      {subscription.isError ? (
        <div role="alert">
          <p>Erreur abonnement: {(subscription.error as BillingApiError).message}</p>
          <button type="button" onClick={() => subscription.refetch()}>
            Reessayer
          </button>
        </div>
      ) : null}

      {subscription.data ? (
        <p>
          Statut: {subscription.data.status === "active" ? "actif" : "inactif"}
          {subscription.data.plan
            ? ` · Plan: ${subscription.data.plan.display_name} · Limite: ${subscription.data.plan.daily_message_limit}/jour`
            : ""}
        </p>
      ) : null}

      <label htmlFor="billing-payment-token">Simulation paiement</label>
      <select
        id="billing-payment-token"
        value={paymentToken}
        onChange={(event) => setPaymentToken(event.target.value)}
      >
        <option value="pm_card_ok">Paiement valide</option>
        <option value="pm_fail">Paiement refuse</option>
      </select>

      <button
        type="button"
        disabled={busy}
        onClick={async () => {
          const idempotencyKey = crypto.randomUUID()
          const result = await checkout.mutateAsync({
            plan_code: "basic-entry",
            payment_method_token: paymentToken,
            idempotency_key: idempotencyKey,
          })
          setLastCheckoutResult(result)
          setLastRetryResult(null)
          if (result.payment_status === "failed") {
            setLastFailedIdempotencyKey(idempotencyKey)
          } else {
            setLastFailedIdempotencyKey(null)
          }
          void subscription.refetch()
          void quota.refetch()
        }}
      >
        Souscrire au plan Basic (5 EUR/mois)
      </button>

      {showRetryAction ? (
        <button
          type="button"
          disabled={busy}
          onClick={async () => {
            const retryKey = lastFailedIdempotencyKey
              ? `${lastFailedIdempotencyKey}-retry`
              : crypto.randomUUID()
            const result = await retryCheckout.mutateAsync({
              plan_code: "basic-entry",
              payment_method_token: "pm_card_ok",
              idempotency_key: retryKey,
            })
            setLastRetryResult(result)
            void subscription.refetch()
            void quota.refetch()
          }}
        >
          Reessayer le paiement
        </button>
      ) : null}

      {subscription.data?.status === "active" ? (
        <>
          <label htmlFor="billing-target-plan">Changer de plan</label>
          <select
            id="billing-target-plan"
            value={targetPlanCode}
            onChange={(event) => setTargetPlanCode(event.target.value)}
          >
            <option value="basic-entry">Basic 5 EUR/mois</option>
            <option value="premium-unlimited">Premium 20 EUR/mois</option>
          </select>
          <p>Impact quota cible: {targetPlanLimitLabel}</p>
          <button
            type="button"
            disabled={busy}
            onClick={async () => {
              const result = await changePlan.mutateAsync({
                target_plan_code: targetPlanCode,
                idempotency_key: crypto.randomUUID(),
              })
              setLastPlanChangeResult(result)
              void subscription.refetch()
              void quota.refetch()
            }}
          >
            Changer de plan
          </button>
        </>
      ) : null}

      {lastCheckoutResult?.payment_status === "succeeded" ||
      lastRetryResult?.payment_status === "succeeded" ? (
        <p>Abonnement actif.</p>
      ) : null}
      {lastPlanChangeResult?.plan_change_status === "succeeded" ? (
        <p>
          Plan mis a jour: {lastPlanChangeResult.previous_plan_code} -&gt;{" "}
          {lastPlanChangeResult.target_plan_code}
        </p>
      ) : null}

      {failedReason ? <p>Motif echec paiement: {failedReason}</p> : null}
      {checkoutError ? <p>Erreur souscription: {checkoutError.message}</p> : null}
      {retryError ? <p>Erreur retry paiement: {retryError.message}</p> : null}
      {changePlanError ? <p>Erreur changement de plan: {changePlanError.message}</p> : null}
    </section>
  )
}
