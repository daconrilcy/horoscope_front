# Story 61.64 : Configuration explicite du Stripe Customer Portal pour les upgrades SaaS avec prorata immédiat

Status: done

## Senior Developer Review (AI)

Review Date: 2026-03-30
Outcome: PASSED

All acceptance criteria for Story 61.64 have been implemented and verified:
- `StripeCustomerPortalService` now requires explicit `configuration_id`.
- Startup guard prevents execution without `STRIPE_PORTAL_CONFIGURATION_ID` when Stripe is active.
- Enhanced logging for portal sessions.
- Documentation and `.env.example` updated.
- Unit and integration tests cover the new requirements.

## Story

En tant que responsable technique de la plateforme,
je veux forcer l'usage d'une configuration Stripe Customer Portal dédiée pour toutes les sessions billing SaaS,
afin de garantir un comportement cohérent des flows billing SaaS, et en particulier de l'upgrade `basic -> premium` avec `proration_behavior=always_invoice`, sans dépendre silencieusement de la configuration portail par défaut du compte Stripe.

---

## Contexte

Après 61-53, 61-61, 61-62 et 61-63, le parcours billing user-facing est Stripe-first et les flows Portal fonctionnent. Cependant, un écart produit subsiste sur l'upgrade `basic -> premium` :

1. **La session portal générique dépend encore implicitement de la configuration Stripe par défaut**. Le code passe déjà `settings.stripe_portal_configuration_id` aux flows dédiés `subscription_update` et `subscription_cancel`, mais pas au portail générique.
2. **La documentation actuelle laisse entendre que `STRIPE_PORTAL_CONFIGURATION_ID` est optionnel**, ce qui ouvre la porte à un drift silencieux entre environnements Stripe (test/live) ou entre plusieurs configurations portal du même compte.
3. **Le besoin produit est maintenant explicite** : pour l'upgrade SaaS `basic -> premium`, la configuration Portal Stripe doit être dédiée, piloter les prix autorisés, activer `subscription_update`, et utiliser `proration_behavior=always_invoice` afin que Stripe génère immédiatement la facture de prorata et tente l'encaissement.
4. **La source de vérité applicative ne change pas** : même avec `always_invoice`, les droits Premium ne doivent être accordés qu'après réconciliation webhook Stripe du snapshot canonique.

Le risque n'est plus un bug de code pur, mais un **risque de dérive de configuration** : un mauvais portail par défaut peut casser l'upgrade immédiat, masquer des prix, ou réintroduire un comportement incohérent entre local, test et production.

---

## Acceptance Criteria

**AC1 — Toute session Portal billing passe explicitement une configuration Stripe**

- [x] `StripeCustomerPortalService.create_portal_session(...)` accepte et utilise `configuration_id: str | None`
- [x] `POST /v1/billing/stripe-customer-portal-session` passe explicitement `settings.stripe_portal_configuration_id`
- [x] `POST /v1/billing/stripe-customer-portal-subscription-update-session` continue de passer explicitement `settings.stripe_portal_configuration_id`
- [x] `POST /v1/billing/stripe-customer-portal-subscription-cancel-session` continue de passer explicitement `settings.stripe_portal_configuration_id`
- [x] Aucun code runtime applicatif ne crée de session Customer Portal Stripe sans paramètre `configuration` pour les flows billing SaaS

**AC2 — Garde-fou explicite sur la configuration applicative**

- [x] `STRIPE_PORTAL_CONFIGURATION_ID` est **requise dans tout environnement où les endpoints Portal billing sont activés**
- [x] **Double barrière** : si les endpoints Portal billing sont activés et que `STRIPE_PORTAL_CONFIGURATION_ID` est absente, le démarrage échoue avec une erreur explicite
- [x] **Double barrière** : si un appel runtime atteint malgré tout le service Portal sans `configuration_id` résolue, une erreur métier explicite `stripe_portal_configuration_missing` est levée plutôt qu'un fallback implicite vers la config Stripe par défaut
- [x] Les tests unitaires/intégration qui mockent Stripe ou n'exercent pas le Portal ne sont pas cassés par ce garde-fou

**AC3 — Observabilité du câblage Portal**

- [x] Chaque création de session Portal journalise l'ID de configuration Stripe utilisé, sans exposer de secret ni de données client sensibles
- [x] Les logs permettent de distinguer les sessions `portal`, `subscription_update` et `subscription_cancel`
- [x] Les événements d'audit existants restent émis et ne changent pas de contrat
- [x] En cas d'absence de configuration, l'erreur retournée est explicite et diagnostiquable (`stripe_portal_configuration_missing`)
- [x] Si `STRIPE_PORTAL_CONFIGURATION_ID` est présente mais invalide côté Stripe, le backend remonte une erreur Stripe diagnostiquable sans fallback local trompeur ni retry implicite vers une autre configuration

**AC4 — Contrat produit/documentation Portal alignés**

- [x] `docs/billing-self-service-mvp.md` n'indique plus que `STRIPE_PORTAL_CONFIGURATION_ID` est optionnelle pour le runtime SaaS
- [x] La documentation précise qu'une configuration Stripe Portal dédiée doit être créée dans le Dashboard Stripe
- [x] La documentation précise que cette configuration doit inclure :
  - `subscription_update.enabled = true`
  - les prix/plans SaaS autorisés explicitement
  - `subscription_update.proration_behavior = always_invoice` pour l'upgrade `basic -> premium`
  - les options de cancel déjà cadrées par le MVP (`at_period_end` si toujours retenu)
- [x] La documentation sépare clairement :
  - la configuration Stripe Dashboard requise
  - la règle applicative webhook-first selon laquelle les droits produit ne changent qu'après webhook, pas au clic utilisateur ni à la seule création de session portal
- [x] La documentation rappelle que `always_invoice` signifie facturation immédiate des proratas via invoice Stripe, pas une UX Checkout custom garantie

**AC5 — Couverture de tests et non-régression**

- [x] Tests unitaires du service Portal mis à jour pour vérifier que la session générique passe bien `configuration`
- [x] Tests unitaires couvrant le cas `configuration_id` absente → erreur métier explicite `stripe_portal_configuration_missing`
- [x] Tests unitaires couvrant le cas `configuration_id` invalide côté Stripe → erreur Stripe diagnostiquable
- [x] Tests d'intégration backend couvrant la création des trois types de session avec `configuration` injectée
- [x] Les tests existants sur erreurs Stripe (`stripe_unavailable`, `stripe_api_error`, `subscription_update feature disabled`) restent verts
- [x] `pytest` ciblé backend billing/portal passe

---

## Tasks / Subtasks

- [x] **Rendre la configuration Portal explicite partout** (AC: 1)
  - [x] Étendre `StripeCustomerPortalService.create_portal_session(...)` pour accepter `configuration_id`
  - [x] Injecter `settings.stripe_portal_configuration_id` dans l'endpoint `POST /v1/billing/stripe-customer-portal-session`
  - [x] Vérifier qu'aucun autre appel runtime de `client.billing_portal.sessions.create(...)` n'existe hors service central

- [x] **Ajouter le garde-fou de configuration** (AC: 2)
  - [x] Ajouter une validation explicite dans `Settings` ou dans un validateur startup dédié pour empêcher l'usage Portal billing sans `STRIPE_PORTAL_CONFIGURATION_ID` dans tout environnement où ces endpoints sont activés
  - [x] Implémenter explicitement la **double barrière** : validation au startup + validation défensive au niveau service
  - [x] Ajouter un code d'erreur métier dédié `stripe_portal_configuration_missing` côté service si la config n'est pas résolue à l'exécution
  - [x] Préserver la stabilité des tests et des contextes sans Stripe réel

- [x] **Durcir les logs et le diagnostic** (AC: 3)
  - [x] Logger `configuration_id` utilisée sur création de session sans secret ni donnée client sensible
  - [x] Logger le type de flow (`portal`, `subscription_update`, `subscription_cancel`)
  - [x] Mapper proprement l'erreur `stripe_portal_configuration_missing` dans `billing.py`
  - [x] Vérifier le comportement et le diagnostic si Stripe rejette une `configuration_id` invalide

- [x] **Aligner la documentation et le runbook Stripe** (AC: 4)
  - [x] Mettre à jour `docs/billing-self-service-mvp.md`
  - [x] Documenter dans `.env.example` et/ou docs billing que `STRIPE_PORTAL_CONFIGURATION_ID` est requise pour le SaaS
  - [x] Documenter la checklist Dashboard Stripe pour la config Portal dédiée
  - [x] Clarifier que `always_invoice` vise le cas d'upgrade immédiat et ne promet pas une UX Checkout custom

- [x] **Étendre la couverture de tests** (AC: 5)
  - [x] Mettre à jour `backend/app/tests/unit/test_stripe_customer_portal_service.py`
  - [x] Mettre à jour `backend/app/tests/integration/test_stripe_customer_portal_api.py`
  - [x] Vérifier les chemins `portal générique`, `update`, `cancel`, `missing configuration`, `invalid configuration`, `Stripe feature disabled`

---

## Dev Notes

### Décision technique à figer

Le backend **ne doit plus jamais dépendre implicitement de la configuration portal par défaut du compte Stripe** pour les sessions Customer Portal utilisées par le billing SaaS.

Règle d'implémentation :

> Le backend doit toujours passer explicitement `STRIPE_PORTAL_CONFIGURATION_ID` lors de la création de toute session Stripe Customer Portal utilisée pour le billing SaaS. La configuration Stripe référencée doit être une configuration dédiée au produit, avec `subscription_update` activé, les prix autorisés explicitement listés, et `proration_behavior=always_invoice` pour les upgrades immédiats. Les droits produit restent mis à jour uniquement après webhook.

### État actuel du code à corriger

- `backend/app/core/config.py` contient déjà `settings.stripe_portal_configuration_id`
- `backend/app/api/v1/routers/billing.py`
  - `POST /stripe-customer-portal-subscription-update-session` passe déjà `configuration_id=settings.stripe_portal_configuration_id`
  - `POST /stripe-customer-portal-subscription-cancel-session` passe déjà `configuration_id=settings.stripe_portal_configuration_id`
  - `POST /stripe-customer-portal-session` **ne passe pas encore** `configuration_id`
- `backend/app/services/stripe_customer_portal_service.py`
  - `_create_subscription_flow_session(...)` supporte déjà `configuration_id`
  - `create_portal_session(...)` **ne supporte pas encore** `configuration_id`
- `docs/billing-self-service-mvp.md` décrit encore `STRIPE_PORTAL_CONFIGURATION_ID` comme optionnelle et autorise donc implicitement le fallback vers la config par défaut Stripe

### Architecture / comportement attendu

- Ne pas réintroduire de mutation locale applicative du billing au clic utilisateur
- Ne pas modifier la logique webhook comme source de vérité
- Ne pas créer un flow custom de paiement/proration dans cette story
- Cette story est un **durcissement de configuration et d'observabilité**, pas une refonte du modèle de souscription

### Suggestion de garde-fou runtime

Le modèle attendu est une **double barrière** :

- **barrière 1 : startup** — empêcher un runtime mal configuré de démarrer si les endpoints Portal billing sont activés sans `STRIPE_PORTAL_CONFIGURATION_ID`
- **barrière 2 : service** — empêcher tout fallback implicite si un appel atteint malgré tout le service sans configuration résolue

Approche recommandée :

1. **Validation config** :
   - si les endpoints Portal billing sont activés
   - et `STRIPE_SECRET_KEY` est renseignée
   - alors `STRIPE_PORTAL_CONFIGURATION_ID` doit être non vide

2. **Validation de service** :
   - `StripeCustomerPortalService.create_portal_session(...)`
   - `create_subscription_update_session(...)`
   - `create_subscription_cancel_session(...)`
   doivent toutes lever l'erreur métier `stripe_portal_configuration_missing` si `configuration_id` est absente

3. **Mapping router** :
   - erreur `stripe_portal_configuration_missing`
   - code HTTP recommandé : `503` si considéré comme erreur de configuration serveur

4. **Cas de configuration invalide** :
   - si `STRIPE_PORTAL_CONFIGURATION_ID` est présente mais rejetée par Stripe, ne jamais fallback vers la configuration par défaut
   - remonter une erreur Stripe diagnostiquable via le mapping d'erreur existant

### Points Stripe à documenter

La configuration Portal dédiée doit être préparée côté Stripe Dashboard avec :

- `features.subscription_update.enabled = true`
- liste explicite des produits/prix SaaS autorisés
- `features.subscription_update.proration_behavior = always_invoice` pour le cas d'upgrade `basic -> premium`
- options de cancel alignées avec le MVP existant

Cette story ne doit pas essayer de créer ou modifier cette configuration via l'API Stripe. Le backend ne fait que **référencer** une configuration déjà créée et administrée côté Stripe.

Note produit à conserver :

- `always_invoice` signifie facturation immédiate des proratas via invoice Stripe et tentative d'encaissement immédiate
- cela ne garantit pas une UX de type mini-Checkout distincte du Customer Portal

### Project Structure Notes

- Config applicative : `backend/app/core/config.py`
- Service central Portal : `backend/app/services/stripe_customer_portal_service.py`
- Router billing : `backend/app/api/v1/routers/billing.py`
- Tests unitaires Portal : `backend/app/tests/unit/test_stripe_customer_portal_service.py`
- Tests intégration Portal : `backend/app/tests/integration/test_stripe_customer_portal_api.py`
- Documentation billing : `docs/billing-self-service-mvp.md`

### Previous Story Intelligence

- 61-53 a déjà introduit `STRIPE_PORTAL_CONFIGURATION_ID`, les flows dédiés `subscription_update` / `subscription_cancel`, et le pattern de service centralisé
- 61-61 a confirmé que le frontend user-facing dépend désormais des endpoints Stripe-first pour checkout et portal
- 61-63 a supprimé le legacy commercial restant, donc ce durcissement doit rester **100% Stripe-first** et ne pas rouvrir de fallback legacy
- Le pattern établi dans l'epic 61 est de ne pas accorder les droits produit au clic utilisateur mais seulement après webhook ; cette règle ne doit pas être affaiblie

### Git Intelligence Summary

Commits récents pertinents :

- `abf0d39 feat(billing): complete legacy commercial and pricing cleanup (Story 61-63)`
- `0d26c0e Stabilize local Stripe billing reconciliation`
- `4197db3 feat(billing): decommission legacy endpoints (checkout, retry, plan-change)`

Le pattern récent du chantier billing est :
- petit delta ciblé
- service Stripe centralisé
- tests backend d'intégration explicites
- documentation `docs/` et artefacts BMAD synchronisés avec le runtime

### Latest Tech Information

- Stripe Customer Portal Session accepte explicitement le paramètre `configuration`; s'il est absent, Stripe utilise la configuration par défaut du compte
- Stripe Customer Portal Configuration expose `features.subscription_update.proration_behavior` avec les valeurs `none`, `create_prorations`, `always_invoice`
- `always_invoice` est la valeur à viser pour un upgrade SaaS où Stripe doit générer immédiatement la facture de prorata et tenter l'encaissement

### References

- [Source: `backend/app/core/config.py`] — présence actuelle de `stripe_portal_configuration_id`
- [Source: `backend/app/services/stripe_customer_portal_service.py`] — service Portal à durcir
- [Source: `backend/app/api/v1/routers/billing.py`] — endpoints Portal actuels
- [Source: `backend/app/tests/integration/test_stripe_customer_portal_api.py`] — couverture d'intégration à étendre
- [Source: `docs/billing-self-service-mvp.md`] — documentation billing self-service à réaligner
- [Source: `_bmad-output/implementation-artifacts/61-53-portal-flows-upgrade-downgrade-cancel.md`] — story fondatrice des flows Portal
- [Source: `_bmad-output/implementation-artifacts/61-61-migration-frontend-commercial-vers-endpoints-stripe-first.md`] — dépendance frontend Stripe-first
- [Source: `_bmad-output/implementation-artifacts/61-63-suppression-legacy-commercial-billing-stripe.md`] — suppression du legacy commercial
- [Source: `https://docs.stripe.com/api/customer_portal/sessions/create`] — paramètre `configuration` des portal sessions
- [Source: `https://docs.stripe.com/api/customer_portal/configurations/object`] — `features.subscription_update.proration_behavior`

---

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

### Completion Notes List

- Story créée pour cadrer le durcissement de configuration Stripe Customer Portal après 61-63.
- Le périmètre est volontairement limité au backend/config/docs/tests ; aucun flow custom de paiement n'est demandé ici.
- Le comportement produit attendu reste webhook-first pour l'activation des droits.
- [AI Review Fix] Added STRIPE_PORTAL_CONFIGURATION_ID to .env.example.
- [AI Review Fix] Added missing integration tests for `missing configuration` and `invalid configuration` in `test_stripe_customer_portal_api.py`.

### File List

- `_bmad-output/implementation-artifacts/61-64-configuration-explicite-customer-portal-stripe-et-prorata-upgrade.md`
- `.env.example`
- `backend/app/tests/integration/test_stripe_customer_portal_api.py`
