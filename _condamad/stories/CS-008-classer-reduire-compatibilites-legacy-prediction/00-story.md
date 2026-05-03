# Story CS-008 classer-reduire-compatibilites-legacy-prediction: Classer et reduire les compatibilites legacy prediction restantes

Status: ready-to-review

## 1. Objective

Produire un registre exhaustif des compatibilites legacy restantes dans prediction, puis supprimer les surfaces classees `dead` ou `historical-facade` sans consommateur externe.
Les surfaces ambigues doivent bloquer l'implementation avec une decision explicite au lieu d'etre conservees par confort.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-003`
- Reason for change: le finding `F-003` confirme plusieurs surfaces legacy prediction encore actives.

## 3. Domain Boundary

- Domain: `backend/app/prediction`
- In scope:
  - Inventaire des surfaces legacy nommees par l'audit.
  - Classification `canonical-active`, `external-active`, `historical-facade`, `dead` ou `needs-user-decision`.
  - Suppression des surfaces amovibles avec migration de consumers internes.
  - Garde anti-reintroduction pour les surfaces supprimees.
- Out of scope:
  - Suppression du payload public `categories` sans decision externe.
  - Refonte complete des schemas publics.
  - Retour de `LLMNarrator`.
  - Refactor cosmetique des tests.
- Explicit non-goals:
  - Ne pas affaiblir `RG-016` et `RG-017`.
  - Ne pas encoder une compatibilite legacy comme comportement nominal de test.
  - Ne pas supprimer une surface `external-active` sans decision utilisateur documentee.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story classe et supprime des facades, alias et compatibilites historiques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les consumers internes doivent utiliser les surfaces canoniques.
  - Les surfaces externes documentees restent bloquees jusqu'a decision utilisateur.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: `categories` ou une surface OpenAPI apparait `external-active`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les payloads publics et imports effectifs doivent etre verifies. |
| Baseline Snapshot | yes | Le registre legacy doit comparer l'etat avant apres. |
| Ownership Routing | yes | Chaque surface legacy doit avoir un owner canonique. |
| Allowlist Exception | no | Les exceptions non supprimees passent par classification, pas allowlist. |
| Contract Shape | yes | Les champs publics et DTO touches doivent etre explicites. |
| Batch Migration | no | La classification pilote les suppressions une par une. |
| Reintroduction Guard | yes | Les symboles supprimes ne doivent pas revenir. |
| Persistent Evidence | yes | Le registre legacy est un artefact obligatoire. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - `app.openapi()` et tests de serialization prediction si une surface publique est touchee.
- Secondary evidence:
  - Scans exacts des symboles `EngineOutput`, `TimeBlock`, `engine_output`, `categories`.
- Static scans alone are not sufficient for this story because:
  - Un champ peut etre expose par serialization meme si son usage textuel semble limite.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/legacy-surface-audit.md`
- Comparison after implementation:
  - `_condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/legacy-surface-after.md`
- Expected invariant:
  - Les surfaces supprimees ont zero consumer nominal et les surfaces conservees ont une decision explicite.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `services/**` | `api/**` |
| HTTP-only adapter | `api/v1/**` | `services/**` |
| Pure cross-cutting helper | `core/**` | `api/**` |
| Persistence detail | `infra/**` | `api/**` |
| Domain invariant | `domain/**` | `api/**` |
| Internal prediction DTO | `backend/app/domain/prediction` ou `backend/app/services/prediction/types.py` | legacy aliases |
| Public prediction payload | `backend/app/services/prediction/public_predictions.py` | implicit compatibility fields |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

Use when the story touches an API, HTTP error, payload, export, DTO, OpenAPI contract, generated client, or frontend type.

- Contract type:
  - Payload public prediction et DTO internes prediction.
- Fields:
  - `categories`: champ public legacy a classifier.
  - `EngineOutput`: type interne legacy a classifier.
  - `TimeBlock`: type interne legacy a classifier.
  - `engine_output`: argument legacy a classifier.
- Required fields:
  - Les champs publics canoniques actuels hors surfaces classees ne changent pas.
- Optional fields:
  - Les surfaces classees `external-active` restent optionnelles seulement avec preuve.
- Status codes:
  - Aucun changement HTTP attendu.
- Serialization names:
  - Les noms publics existants restent inchanges sauf suppression approuvee.
- Frontend type impact:
  - Verifier zero consumer frontend avant suppression d'un champ public.
- Generated contract impact:
  - OpenAPI doit etre capture si `categories` change.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| legacy registry | `_condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/legacy-surface-audit.md` | Classer chaque surface legacy. |
| after registry | `_condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/legacy-surface-after.md` | Prouver les suppressions et decisions. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route, field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- importable Python modules
- generated OpenAPI paths
- forbidden symbols or states

Required forbidden examples:

- `LLMNarrator`
- `EngineOutput` si classe `dead` ou `historical-facade`
- `TimeBlock` si classe `dead` ou `historical-facade`
- `engine_output=` si remplace par un contrat canonique

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py` plus test de garde legacy prediction.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-008` liste les surfaces de compatibilite actives.
- Evidence 2: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-009` et `E-011` prouvent que `llm_narrator` est deja supprime.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage, notamment `RG-016` et `RG-017`.

## 6. Target State

- Chaque surface legacy dispose d'une classification deterministe.
- Les surfaces removables sont supprimees sans wrapper ni alias.
- Les surfaces `external-active` bloquent la suppression avec preuve.
- Les tests prouvent que les consumers internes utilisent les owners canoniques.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-016` - les tests prediction ne doivent pas redevenir consommateurs de `LLMNarrator`.
  - `RG-017` - le runtime horoscope daily ne doit pas reintroduire `LLMNarrator`.
  - `RG-028` - les surfaces legacy prediction restantes doivent rester classees.
- Non-applicable invariants:
  - `RG-025` - Stripe n'est pas touche.
- Required regression evidence:
  - Registre legacy, tests V3/V4, OpenAPI si champ public touche, scans exacts des symboles classes.
- Allowed differences:
  - Suppression des surfaces classees `dead` ou `historical-facade`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le registre legacy classe chaque surface auditee. | Evidence profile: `external_usage_blocker`; `pytest -q app/tests/unit/test_schemas_v3.py`. |
| AC2 | Les surfaces removables sont supprimees. | Evidence profile: `repo_wide_negative_scan`; `rg -n "EngineOutput|TimeBlock|engine_output=" app tests`. |
| AC3 | Les surfaces publiques gardees ont une preuve externe. | Evidence profile: `json_contract_shape`; `pytest -q app/tests/unit/test_public_projection.py`. |
| AC4 | Aucun narrateur legacy ne revient. | Evidence profile: `reintroduction_guard`; `pytest -q tests/unit/prediction/test_llm_narrator_deprecation_guard.py`. |
| AC5 | La suppression ne modifie pas les contrats non vises. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_schemas_v3.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le registre legacy initial (AC: AC1)
- [x] Task 2 - Classer chaque item avec preuve (AC: AC1, AC3)
- [x] Task 3 - Supprimer les items removables (AC: AC2)
- [x] Task 4 - Ajouter les guards anti-retour (AC: AC2, AC4)
- [x] Task 5 - Capturer l'etat final (AC: AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Types canoniques existants dans `backend/app/prediction/schemas.py` ou leur futur owner.
  - Tests V3/V4 existants pour detecter les regressions.
- Do not recreate:
  - Nouveaux alias de compatibilite.
  - Re-export pour conserver un ancien chemin.
  - Tests nominalisant une surface legacy.
- Shared abstraction allowed only if:
  - Elle remplace une surface legacy par un contrat canonique unique.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `backend/app/prediction/llm_narrator.py`
- `LLMNarrator`
- `EngineOutput` sans classification `canonical-active` ou `external-active`.
- `TimeBlock` sans classification `canonical-active` ou `external-active`.
- `engine_output=` sans remplacement canonique documente.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/legacy-surface-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Prediction engine output contract | canonical schema owner apres classification | `EngineOutput` si historique |
| Public categories payload | public contract owner apres decision | `categories` legacy |
| Persistence input contract | service persistence canonique | `engine_output` kwarg legacy |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## 17. Generated Contract Check

Use this section when generated contracts exist or the archetype affects API surfaces.

Required generated-contract evidence:

- OpenAPI before/after if `categories` changes.
- Generated client/schema absence when a public field is removed.
- Route manifest absence is skipped unless an API route is touched.

## 18. Files to Inspect First

- `backend/app/prediction/schemas.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/persistence_service.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/tests/unit/test_schemas_v3.py`
- `backend/app/tests/unit/test_public_projection.py`
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/prediction/schemas.py` - supprimer ou classifier aliases et types.
- `backend/app/prediction/persistence_service.py` - supprimer le kwarg legacy si removable.
- `backend/app/prediction/public_projection.py` - conserver ou retirer `categories` selon decision.
- `_condamad/stories/CS-008-classer-reduire-compatibilites-legacy-prediction/legacy-surface-audit.md` - registre.

Likely tests:

- `backend/app/tests/unit/test_schemas_v3.py` - contrats V3.
- `backend/app/tests/unit/test_public_projection.py` - payload public.
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py` - garde LLM legacy.

Files not expected to change:

- `frontend/src` - sauf preuve de consumer public `categories`.
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py` - LLM hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app tests
pytest -q app/tests/unit/test_schemas_v3.py app/tests/unit/test_public_projection.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py
rg -n "EngineOutput|TimeBlock|engine_output=|\\bcategories\\b|LLMNarrator" app tests
python -c "from app.main import app; schema = app.openapi(); assert 'paths' in schema"
```

## 22. Regression Risks

- Risk: `categories` est retire alors qu'un client externe le consomme.
  - Guardrail: `AC3` impose preuve OpenAPI ou decision utilisateur.
- Risk: un alias legacy reste sous un autre nom.
  - Guardrail: `AC2` impose scan cible et registre.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - preuves `E-008` a `E-012`.
- `_condamad/audits/prediction/2026-05-03-2214/02-finding-register.md#F-003` - finding source.
- `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-003` - candidate d'origine.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
