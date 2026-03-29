#!/usr/bin/env bash
# Usage: ./scripts/stripe-listen-webhook.sh
# Forwarde les événements Stripe billing vers l'API locale (port 8001).
# Le secret whsec_... affiché au démarrage doit être copié dans .env.local.

stripe listen \
  --events checkout.session.completed,customer.subscription.created,customer.subscription.updated,customer.subscription.deleted,invoice.paid,invoice.payment_failed,invoice.payment_action_required \
  --forward-to http://localhost:8001/v1/billing/stripe-webhook
