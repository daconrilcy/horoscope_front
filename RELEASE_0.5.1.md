# Release 0.5.1 — Billing Configuration & Terminal Testing

## Résumé

Cette release ajoute la prise de conscience de la configuration billing, enrichit le checkout, durcit les pages success/cancel, améliore le portal avec gestion whitelist, ajoute un simulateur Terminal en dev, des outils admin, l'observabilité frontend, la documentation complète, et des tests conformes à la documentation Stripe Terminal.

## Issues complétées

### FE-13 — Billing config awareness & dev debug panel (#49)

- ✅ Service `billingConfigService` pour récupérer la config depuis `/v1/config` avec fallback sur variables d'environnement
- ✅ Hook `useBillingConfig` pour React Query
- ✅ Panel de debug dev-only (`BillingDebugPanel`) affichant configuration, feature flags, URLs, warnings
- ✅ Headers de corrélation (`X-Client-Version`, `X-Request-Source`) sur toutes les requêtes
- ✅ Tests unitaires complets

### FE-14 — Checkout enrichi (#50)

- ✅ Extension des schémas Zod pour `CheckoutSessionPayload` (ab_bucket, trial_days, coupon, address, tax_ids)
- ✅ Génération automatique d'Idempotency-Key côté client (UUID v4)
- ✅ Validation stricte des payloads avec Zod
- ✅ Hook `useCheckout` mis à jour

### FE-15 — Billing success/cancel hardening (#51)

- ✅ Page `/billing/success` avec validation de `session_id` et revalidation automatique
- ✅ Page `/billing/cancel` avec retry et messages clairs
- ✅ Tests unitaires complets

### FE-16 — Portal session with whitelist UX & fallback (#52)

- ✅ Support de `return_url` optionnel avec fallback automatique
- ✅ Détection et gestion des erreurs de whitelist
- ✅ Tests unitaires couvrant tous les scénarios

### FE-17 — Stripe Terminal dev console (#53)

- ✅ Service `terminalService` avec tous les endpoints (connect, createPaymentIntent, process, capture, cancel, refund)
- ✅ Composant `DevTerminalConsole` avec machine à états
- ✅ Page `/dev/terminal` (dev-only)
- ✅ Tests unitaires et E2E complets

### FE-18 — Admin dev: clear price_lookup cache (#54)

- ✅ Service `adminService` avec `clearPriceLookupCache()`
- ✅ Bouton dans `BillingDebugPanel`
- ✅ Tests unitaires complets

### FE-19 — Billing front observability correlation (#55)

- ✅ Emission d'événements `api:request` pour toutes les requêtes HTTP
- ✅ Composant `DebugDrawer` (dev-only) accessible via `Ctrl+Shift+D`
- ✅ Affichage des breadcrumbs avec request_id, latence, et bouton "Copy CURL"
- ✅ Tests unitaires complets

### FE-20 — Docs: billing/terminal quickstart & env (#56)

- ✅ Documentation complète des variables d'environnement
- ✅ Section Quickstart Billing et Terminal
- ✅ Guide Troubleshooting
- ✅ Documentation des headers de corrélation

### Tests Stripe Terminal conformes à la documentation officielle

- ✅ Tests unitaires pour montants avec décimales spécifiques (00, 01, 02, 03, 05, 55, 65, 75)
- ✅ Tests pour cartes de test standard (Visa, Mastercard, Amex, etc.)
- ✅ Tests pour cas de succès spécifiques (offline PIN, online PIN)
- ✅ Tests pour cas d'erreur (charge_declined, insufficient_funds, expired_card, etc.)
- ✅ Tests pour scénarios de remboursement (total et partiel)
- ✅ Tests E2E pour flow complet Terminal
- ✅ Documentation complète dans `docs/STRIPE_TERMINAL_TESTING.md`

## Statistiques

- **26 nouveaux tests unitaires** pour les services billing/config/admin/terminal
- **7 nouveaux tests** pour les hooks billing
- **10 tests** pour `DevTerminalConsole` (dont 3 scénarios Stripe Terminal)
- **16 tests spécifiques Stripe Terminal** conformes à la documentation
- **1 fichier E2E** pour tests Terminal
- **Tous les tests passent** (522 tests au total)

## Références

- [Documentation Stripe Terminal Testing](https://docs.stripe.com/terminal/references/testing)
- Issues: #49, #50, #51, #52, #53, #54, #55, #56
