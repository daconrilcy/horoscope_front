# Story CS-132 centraliser-enveloppes-erreurs-api-frontend: Centraliser les enveloppes et erreurs API frontend

Status: ready-to-dev

## 1. Objective

Creer un owner unique pour les enveloppes de reponse, les enveloppes d'erreur, le parsing JSON d'erreur et la conversion vers l'erreur transport frontend.
Les modules API doivent consommer ce helper au lieu de redefinir localement `ErrorEnvelope`, `ResponseEnvelope`, `parseError`, `toTransportError` ou des erreurs equivalentes.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-002`
- Reason for change: l'audit `frontend-api` signale `F-002`, une duplication de gestion d'enveloppes et d'erreurs dans les modules API.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/api`
- In scope:
  - Creer ou etendre `frontend/src/api/client.ts` ou `frontend/src/api/core/errors.ts`.
  - Migrer les modules API listes par `SC-002` vers le helper partage.
  - Conserver les classes d'erreur publiques seulement si leur statut est decide et teste.
- Out of scope:
  - Modifier les routes backend ou OpenAPI.
  - Reorganiser physiquement les modules volumineux, couvert par `CS-133`.
  - Migrer le transport `fetch`, couvert par `CS-131`.
- Explicit non-goals:
  - Ne pas modifier les invariants `RG-053`, `RG-057`, `RG-064` et `RG-069`.
  - Ne pas conserver deux parsers JSON concurrents.
  - Ne pas masquer les erreurs serveur par des messages generiques non testes.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: api-error-contract-centralization
- Archetype reason: les contrats d'erreur API frontend doivent avoir une source de verite partagee.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les messages publics existants restent preserves sauf divergence documentee par tests.
  - Les types d'erreur publics conserves doivent deleguer au helper canonique.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une classe `*ApiError` est consommee comme API publique et ne peut pas converger sans changer son contrat.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | le helper d'erreur devient source de verite executable des erreurs frontend. |
| Baseline Snapshot | yes | les parsers locaux doivent etre inventories avant/apres pour fermer la duplication. |
| Ownership Routing | yes | les parsers locaux doivent router vers l'owner canonique. |
| Allowlist Exception | yes | les wrappers d'erreur publics restants doivent etre exacts. |
| Contract Shape | yes | les enveloppes d'erreur et de reponse sont un contrat TypeScript runtime. |
| Batch Migration | yes | `SC-002` impose une migration par phases admin/support/B2B puis prediction/natal/chat/billing/hooks. |
| Reintroduction Guard | yes | les duplications de parser doivent etre bloquees. |
| Persistent Evidence | yes | la carte des wrappers conserves et phases migrees doit persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - helper partage dans `frontend/src/api/client.ts` ou `frontend/src/api/core/errors.ts`.
  - tests API ciblant les modules migres.
- Secondary evidence:
  - scan des symboles d'enveloppes et parsers locaux.
- Static scans alone are not sufficient:
  - le test `api-architecture` doit agir comme AST guard des owners de parsing.
  - AST guard evidence: `npm run test -- api-architecture`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-132-centraliser-enveloppes-erreurs-api-frontend/error-centralization-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-132-centraliser-enveloppes-erreurs-api-frontend/error-centralization-after.md`
- Expected invariant:
  - aucun parser local non delegue ne reste hors classification.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Type d'enveloppe erreur | `client.ts` ou `core/errors.ts` | definition locale par module |
| Parsing erreur JSON | helper partage | `parseError` local non delegue |
| Conversion erreur transport | helper partage | `throw new Error` construit depuis payload API |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `error-wrapper-map.md` | retained API error wrappers | wrappers publics delegues | permanent when consumer documented |

## 4f. Contract Shape

- Contract type:
  - frontend API error and response envelopes.
- Fields:
  - `error`, `code`, `message`, `details`, `data`, `success` when already present in current module contracts.
- Required fields:
  - fields required by current module tests before migration.
- Optional fields:
  - optional payload metadata currently accepted by typed wrappers.
- Status codes:
  - no HTTP status code change; statuses remain owned by backend and `ApiError`.
- Serialization names:
  - existing JSON names are preserved exactly.
- Frontend type impact:
  - local duplicate envelope types are replaced by shared exported types or aliases backed by shared types.
- Generated contract impact:
  - no generated OpenAPI or generated client is changed.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| phase-1 | admin, support, B2B parsers | shared error helper | module internals | admin/support/B2B tests | scan parser symbols | public error class ambiguity |
| phase-2 | prediction, natal, chat, billing, hooks | shared error helper | module internals | targeted API tests | scan parser symbols | user decision on public wrappers |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| parser baseline | `_condamad/stories/CS-132-centraliser-enveloppes-erreurs-api-frontend/error-centralization-before.md` | capturer les parsers et enveloppes locaux initiaux. |
| wrapper map | `_condamad/stories/CS-132-centraliser-enveloppes-erreurs-api-frontend/error-wrapper-map.md` | classer chaque wrapper ou parser conserve. |
| phase result | `_condamad/stories/CS-132-centraliser-enveloppes-erreurs-api-frontend/error-centralization-after.md` | prouver les duplications restantes ou fermees. |

## 4i. Reintroduction Guard

The implementation must add or update a guard that fails when a module API recreates a local parser or envelope owner.

Deterministic source: forbidden symbols in `frontend/src/api`.

Required guard evidence:

```powershell
cd frontend
npm run test -- api-architecture
rg -l "ErrorEnvelope|ResponseEnvelope|parseError|toTransportError|extractAdminApiErrorMessage|throw new Error" src/api -g "*.ts"
```

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md` - `F-002` classe la duplication d'erreur comme finding high.
- Evidence 2: `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md` - `SC-002` liste les fichiers et phases de migration.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Un helper partage possede les enveloppes et parsers d'erreur API frontend.
- Les wrappers publics restants deleguent au helper et sont listes dans `error-wrapper-map.md`.
- Le scan final ne montre aucun parser local non delegue dans `frontend/src/api`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-053` - aucune compatibilite runtime historique n'est recreee.
  - `RG-057` - aucun vocabulaire legacy ou fallback de compatibilite n'est ajoute.
  - `RG-064` - les pages restent hors parsing API local.
  - `RG-069` - les composants partages restent hors orchestration API.
- Required regression evidence:
  - `npm run test -- api-architecture page-architecture component-architecture`
  - scan des symboles d'erreur dupliques.
- Allowed differences:
  - import interne et owner de type, sans changement de payload public.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Un helper partage porte le parsing commun. | Evidence profile: `api_error_shape_contract`; `npm run test -- apiClient api-architecture`. |
| AC2 | Les modules de phase 1 deleguent au helper canonique. | Evidence profile: `ast_architecture_guard`; `npm run test -- adminPromptsApi b2b support`. |
| AC3 | Les modules de phase 2 sont migres ou bloques par decision exacte. | Evidence profile: `batch_migration_mapping`; `npm run test -- Reconciliation privacy guidance`. |
| AC4 | Les wrappers publics conserves sont classes. | Evidence profile: `allowlist_register_validated`; audit `error-wrapper-map.md` et `npm run test -- api-architecture`. |
| AC5 | Les duplications de parser ne peuvent pas revenir sans echec de guard. | Evidence profile: `reintroduction_guard`; scan cible et `npm run test -- api-architecture`. |

## 8. Implementation Tasks

- [ ] Task 1 - Classer les parsers et wrappers existants (AC: AC3, AC4)
  - [ ] Ecrire `error-wrapper-map.md`.
  - [ ] Identifier les blockers de public API.
- [ ] Task 2 - Creer le helper partage (AC: AC1)
  - [ ] Porter les types et conversions communs.
  - [ ] Ajouter les tests du contrat d'erreur.
- [ ] Task 3 - Migrer les phases auditees (AC: AC2, AC3)
  - [ ] Migrer admin/support/B2B.
  - [ ] Migrer prediction/natal/chat/billing/hooks ou enregistrer un blocker exact.
- [ ] Task 4 - Ajouter les guards et preuve finale (AC: AC4, AC5)
  - [ ] Ajouter le test `api-architecture`.
  - [ ] Ecrire `error-centralization-after.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `ApiError` existant.
  - conventions de tests API existantes.
- Do not recreate:
  - `ErrorEnvelope` ou `ResponseEnvelope` local par module.
  - parser JSON d'erreur local.
  - `throw new Error` base sur payload API sans conversion canonique.
- Shared abstraction allowed only if:
  - elle remplace au moins deux duplications listees par `SC-002`.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers non classes
- legacy imports
- fallback parser behavior
- duplicate active implementations
- silent fallback behavior

Specific forbidden symbols / paths:

- `ErrorEnvelope` local hors helper canonique
- `ResponseEnvelope` local hors helper canonique
- `parseError` local non delegue
- `toTransportError` local non delegue
- `extractAdminApiErrorMessage` comme owner durable

## 11. Removal Classification Rules

- Removal classification: not applicable
- Reason: les wrappers publics ne sont retires que si leur classification est couverte par `error-wrapper-map.md`.

## 12. Removal Audit Format

- Removal audit: not applicable
- Reason: cette story centralise et classe avant toute suppression contractuelle publique.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Enveloppes API frontend | `client.ts` ou `core/errors.ts` | types locaux dupliques |
| Parsing erreur | helper partage | parsers locaux |
| Erreur transport | `ApiError` ou wrapper public delegue | `Error` generique local |

## 14. Delete-Only Rule

- Delete-only rule: not applicable
- Reason: la suppression de wrappers publics depend de la classification et d'une decision si ambigu.

## 15. External Usage Blocker

- External usage blocker: not applicable
- Reason: les exports publics frontend sont verifies par import inventory interne.

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: aucun OpenAPI ou client genere n'est produit par cette story.

## 17. Files to Inspect First

- `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md`
- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md`
- `frontend/src/api/client.ts`
- `frontend/src/api/adminPrompts.ts`
- `frontend/src/api/natalChart.ts`
- `frontend/src/api/chat.ts`
- `frontend/package.json`

## 18. Expected Files to Modify

Likely files:

- `frontend/src/api/client.ts` - helper partage ou exports.
- `frontend/src/api/core/errors.ts` - helper si sous-module approuve par structure existante.
- modules listes par `SC-002` - migration vers helper.
- `_condamad/stories/CS-132-centraliser-enveloppes-erreurs-api-frontend/error-wrapper-map.md` - classification.
- `_condamad/stories/CS-132-centraliser-enveloppes-erreurs-api-frontend/error-centralization-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/api-architecture-guards.test.ts` - guard anti-duplication.
- tests API existants des modules migres.

Files not expected to change:

- `backend/app/**` - aucun changement backend.
- `frontend/src/pages/**` - pas de parsing page.
- `frontend/src/components/**` - pas de parsing composant.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
cd frontend
npm run test -- apiClient adminPromptsApi b2b Reconciliation privacy guidance chat natalChartApi
npm run test -- api-architecture page-architecture component-architecture
npm run lint
npm run typecheck
rg -l "ErrorEnvelope|ResponseEnvelope|parseError|toTransportError|extractAdminApiErrorMessage|throw new Error" src/api -g "*.ts"
```

## 21. Regression Risks

- Risk: un message d'erreur utilisateur change.
  - Guardrail: tests API cibles sur messages existants.
- Risk: wrappers publics casses.
  - Guardrail: `error-wrapper-map.md` et tests consommateurs.
- Risk: parser local restant.
  - Guardrail: guard `api-architecture`.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Keep public wrappers only with documented owner and tests.
- Keep all Python commands behind `.\\.venv\\Scripts\\Activate.ps1`.

## 23. References

- `_condamad/audits/frontend-api/2026-05-10-1850/00-audit-report.md`
- `_condamad/audits/frontend-api/2026-05-10-1850/02-finding-register.md#F-002`
- `_condamad/audits/frontend-api/2026-05-10-1850/03-story-candidates.md#SC-002`
- `_condamad/stories/regression-guardrails.md`
