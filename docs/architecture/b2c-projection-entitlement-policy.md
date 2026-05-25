<!-- Commentaire global: ce document fixe la politique produit des droits B2C pour les projections publiques sans ajouter de route, de paiement ni de surface runtime. -->

# B2C Projection Entitlement Policy

## Identite du contrat

- `policy_id`: `b2c_projection_entitlement_policy`
- Owner canonique: `docs/architecture/b2c-projection-entitlement-policy.md`
- Plans autorises: `free`, `basic`, `premium`
- Sources de vocabulaire: `backend/app/services/billing/models.py`, `backend/app/services/entitlement/**`, CS-256, CS-257, CS-258 et CS-259.
- Portee: matrice produit documentaire pour les futures verifications d'autorisation API.

Cette politique ne cree pas de route, serializer, schema OpenAPI, table, migration, paiement, client frontend, prompt ou provider integration. Les futures stories d'API doivent consommer cette matrice comme source produit et conserver les payloads techniques hors des reponses B2C.

## Projection Matrix

| projection_id | minimum_plan | free | basic | premium | allowed_content_depth |
|---|---|---|---|---|---|
| `structured_facts_v1` | `free` | autorise comme base factuelle controlee quand un contrat API public existe | autorise comme base factuelle controlee quand un contrat API public existe | autorise comme base factuelle controlee quand un contrat API public existe | faits stables, hashables et non narratifs; aucun prompt, debug ou raw runtime |
| `beginner_summary_v1` | `free` | resume deterministe court, vulgarise, sans details techniques | resume deterministe complet pour lecture debutant | resume deterministe complet avec contexte de support, sans runtime brut | langage client, labels compacts, highlights et disclaimers |
| `client_interpretation_projection_v1` | `free` | profondeur courte `free_short`, guidance limitee et paywall/degraded states | profondeur `basic`, narration plus complete et aide de lecture | profondeur `premium`, narration longue et support enrichi | variation par narration et aide client; jamais par exposition de runtime technique |

`authorized_projections` contient uniquement `structured_facts_v1`, `beginner_summary_v1` et `client_interpretation_projection_v1` pour les clients B2C dans le scope natal public actuel. Toute nouvelle projection client ou transit reste hors de cette politique tant qu'une decision produit separee et un contrat API dedie ne l'autorisent pas.

## Denied Internal Projections

`denied_internal_projections` interdit aux clients B2C:

- les projections expert, dont `expert_technical_projection_v1`;
- les projections admin, dont `astrology_full_data_v1`, `admin_chart_diagnostics_v1` et les payloads d'audit;
- les surfaces debug, traces, graphes de calcul, provider internals et model internals;
- les surfaces raw runtime, `ChartObjectRuntimeData`, raw calculation graph payloads et proof internals;
- les prompts, prompt payloads, prompt refs brutes, provider responses et audit rows.

Une projection interne ne devient pas B2C par fallback, alias, shim, compat path ou champ optionnel dans une projection client. Si un appel futur demande une projection interne avec un plan B2C, la reponse attendue est un refus controle, pas une degradation silencieuse vers un payload technique partiel.

## Plan Insufficient Error

`plan_insufficient_error` definit la forme stable de l'erreur `plan_insufficient` pour les futures autorisations API:

| field | required | policy |
|---|---|---|
| `code` | oui | valeur exacte `plan_insufficient` |
| `message` | oui | message client-readable, sans detail runtime, prompt, provider, debug ou audit payload |
| `current_plan` | oui | plan courant parmi `free`, `basic`, `premium` ou valeur runtime controlee si aucun plan actif |
| `required_plan` | oui | premier plan necessaire selon la `projection_matrix` |
| `projection_id` | oui | projection client demandee; jamais une projection interne detaillee |
| `upgrade_hint` | optionnel | conseil lisible, non technique, sans exposer de prix Stripe, d'identifiant provider ou de payload interne |

Les futures routes ne doivent pas redefinir cette erreur localement. Elles doivent produire une erreur explicite et testable, sans fallback vers une projection moins protegee sauf decision produit documentee dans une story separee.

## Audit Trigger Policy

`audit_trigger_policy` rattache les reponses narratives B2C a `narrative_answer_audit_v1`:

- toute reponse `basic` declenche `narrative_answer_audit_v1`;
- toute reponse `premium` declenche `narrative_answer_audit_v1`;
- toute reponse narrative `long` declenche `narrative_answer_audit_v1`, quel que soit le plan;
- toute reponse `sensitive` declenche `narrative_answer_audit_v1`, quel que soit le plan;
- une reponse `free` courte peut rester hors persistance d'audit seulement si elle n'est ni longue, ni sensitive, ni generee comme reponse narrative soumise a audit par CS-259.

L'audit conserve ses propres contrats et ne doit pas injecter `audit rows`, prompt payloads, provider internals ou proof internals dans les projections client.

## Quota Policy

`quota_policy` reutilise uniquement les decisions existantes de quota et limit presentes dans les services billing et entitlement, notamment les bindings de plan, `PlanFeatureQuotaModel`, `quota_runtime.py` et les gates existants.

Aucun quota de projection B2C n'est cree par cette story. Si la matrice exige demain un compteur par projection, une separate product decision est obligatoire avant toute migration, route, middleware, feature binding ou test d'autorisation.

## Ownership Et Non-Goals

- Le registre public reste `docs/architecture/official-product-primitives-public-projections.md`.
- Les contrats payload restent CS-256, CS-257 et CS-258; cette politique ne duplique pas leurs schemas.
- Le contrat d'audit reste `docs/architecture/narrative-answer-audit-v1-contract.md`.
- Les futurs tests d'autorisation API peuvent s'appuyer sur `policy_id`, `projection_matrix`, `plan_insufficient_error` et `audit_trigger_policy`.
- Les dossiers `backend/app/**`, `frontend/src/**`, `backend/migrations/**` et les clients OpenAPI generes sont hors scope pour cette story.
