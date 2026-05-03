#!/usr/bin/env pwsh
# Usage: .\scripts\stripe-listen-webhook.ps1
# Forwarde les evenements Stripe billing supportes vers l'API locale (port 8001).
# Le secret whsec_... affiche au demarrage doit etre copie dans .env.local.

stripe listen `
  --events checkout.session.completed,checkout.session.async_payment_succeeded,customer.subscription.created,customer.subscription.updated,customer.subscription.deleted,customer.subscription.paused,customer.subscription.resumed,customer.subscription.trial_will_end,subscription_schedule.created,subscription_schedule.updated,subscription_schedule.canceled,subscription_schedule.completed,customer.updated,invoice.paid,invoice.payment_failed,invoice.payment_action_required `
  --forward-to http://localhost:8001/v1/billing/stripe-webhook
