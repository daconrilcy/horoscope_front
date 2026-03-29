#!/usr/bin/env pwsh
# Usage: .\scripts\stripe-listen-webhook.ps1
# Forwarde les evenements Stripe billing standardises vers l'API locale (port 8001).
# Le secret whsec_... affiche au demarrage doit etre copie dans .env.local.

stripe listen `
  --events checkout.session.completed,customer.subscription.created,customer.subscription.updated,customer.subscription.deleted,invoice.paid,invoice.payment_failed,invoice.payment_action_required `
  --forward-to http://localhost:8001/v1/billing/stripe-webhook
