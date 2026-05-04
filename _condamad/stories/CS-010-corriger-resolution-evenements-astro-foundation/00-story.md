# Story CS-010 corriger-resolution-evenements-astro-foundation: Corriger la resolution des evenements astro_foundation

Status: ready-to-review

## 1. Objective

Corriger `PublicAstroFoundationPolicy` pour qu'elle lise les evenements canoniques exposes par le moteur, y compris `detected_events`, et reconnaisse les types `aspect_exact_*`.
Le schema public ne doit pas changer hors remplissage attendu de `astro_foundation`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-005`
- Reason for change: le finding `F-005` identifie un drift runtime ou `astro_foundation` peut etre absent quand les evenements arrivent via `detected_events`.

## 3. Domain Boundary

- Domain: `backend/app/prediction/public_projection.py`
- In scope:
  - Resolution `core.events` puis fallback `core.detected_events`.
  - Support des types `aspect_exact_to_angle`, `aspect_exact_to_luminary` et `aspect_exact_to_personal`.
  - Tests unitaires dedies pour `PublicAstroFoundationPolicy`.
- Out of scope:
  - Refonte de projection publique.
  - Changement de schema public.
  - Appel LLM ou narration.
  - Migration namespace prediction.
- Explicit non-goals:
  - Ne pas modifier les invariants LLM `RG-016` a `RG-019`.
  - Ne pas ajouter de fallback silencieux hors sources canoniques auditees.
  - Ne pas changer le payload public hors valeurs attendues de `astro_foundation`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story corrige un comportement runtime en preservant la forme du contrat public.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `astro_foundation` peut etre mieux rempli.
  - Aucun champ public nouveau ou supprime n'est autorise.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: les sources d'evenements canoniques different de `events` et `detected_events`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le bug concerne la lecture effective d'un payload moteur. |
| Baseline Snapshot | yes | Le payload public doit rester stable hors valeur corrigee. |
| Ownership Routing | no | Aucun deplacement de responsabilite. |
| Allowlist Exception | no | Aucune exception. |
| Contract Shape | yes | La forme JSON publique est protegee. |
| Batch Migration | no | Pas de migration par lots. |
| Reintroduction Guard | no | Aucune surface legacy supprimee. |
| Persistent Evidence | yes | Les cas avant apres doivent etre documentes. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - Tests unitaires et `TestClient` instanciant un `engine_output` avec `detected_events`.
- Secondary evidence:
  - Scan exact des types `aspect_exact_to_angle`, `aspect_exact_to_luminary`, `aspect_exact_to_personal`.
- Static scans alone are not sufficient for this story because:
  - Le bug depend du contenu runtime de `engine_output`.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/astro-foundation-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/astro-foundation-after.md`
- Expected invariant:
  - La forme du payload public reste identique hors remplissage `astro_foundation`.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

Use when the story touches an API, HTTP error, payload, export, DTO, OpenAPI contract, generated client, or frontend type.

- Contract type:
  - Payload public `astro_foundation`.
- Fields:
  - `astro_foundation`: objet public existant rempli depuis evenements canoniques.
- Required fields:
  - Aucun nouveau champ requis.
- Optional fields:
  - Champs existants de `astro_foundation`.
- Status codes:
  - Aucun changement HTTP.
- Serialization names:
  - Noms existants inchanges.
- Frontend type impact:
  - Aucun type frontend ne doit changer.
- Generated contract impact:
  - Aucun changement OpenAPI attendu.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| bug baseline | `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/astro-foundation-before.md` | Capturer les cas non couverts. |
| fixed behavior | `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/astro-foundation-after.md` | Prouver les cas corriges. |

## 4i. Reintroduction Guard

- Reintroduction guard: not applicable
- Reason: no removed, forbidden, or converged-away legacy surface can be reintroduced by this story.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-013` montre que la policy ne lit que `core.events` et `event_type == "aspect"`.
- Evidence 2: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-014` montre que les tests ne couvrent pas `detected_events`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `PublicAstroFoundationPolicy` lit `events` et `detected_events` dans l'ordre documente.
- Les aspects exacts sont traites comme aspects dominants.
- Les tests prouvent le bugfix sans changement de schema.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-030` - `astro_foundation` doit rester aligne sur les sources d'evenements canoniques.
- Non-applicable invariants:
  - `RG-017` - aucun runtime LLM n'est touche.
  - `RG-025` - Stripe n'est pas touche.
- Required regression evidence:
  - Tests unitaires `test_public_astro_foundation.py` et tests API V4 concernes.
- Allowed differences:
  - `astro_foundation` est rempli dans des cas auparavant vides.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `detected_events` alimente `astro_foundation`. | Evidence profile: `json_contract_shape`; `pytest -q tests/unit/prediction/test_public_astro_foundation.py`. |
| AC2 | Les aspects exacts sont reconnus. | Evidence profile: `json_contract_shape`; `pytest -q tests/unit/prediction/test_public_astro_foundation.py`. |
| AC3 | Le schema public reste stable. | Evidence profile: `json_contract_shape`; `pytest -q app/tests/unit/test_public_projection.py`. |
| AC4 | Les preuves du bugfix sont persistees. | Evidence profile: `baseline_before_after_diff`; `pytest -q tests/unit/prediction/test_public_astro_foundation.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le cas bug actuel (AC: AC1, AC4)
- [x] Task 2 - Corriger la resolution d'evenements (AC: AC1)
- [x] Task 3 - Ajouter les aspects exacts (AC: AC2)
- [x] Task 4 - Verifier la forme publique (AC: AC3)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/prediction/public_astro_daily_events.py` pour la semantique des types exacts.
  - Tests existants `backend/tests/unit/prediction/test_public_astro_foundation.py`.
- Do not recreate:
  - Une taxonomie d'aspects concurrente.
  - Un fallback legacy non documente.
  - Un schema public alternatif.
- Shared abstraction allowed only if:
  - Elle evite une duplication prouvee avec `public_astro_daily_events.py`.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- Nouveau champ public pour remplacer `astro_foundation`.
- Nouvelle source non canonique hors `events` ou `detected_events`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

- Canonical ownership: not applicable

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `backend/app/prediction/public_projection.py`
- `backend/app/prediction/public_astro_daily_events.py`
- `backend/tests/unit/prediction/test_public_astro_foundation.py`
- `backend/app/tests/unit/test_public_projection.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/prediction/public_projection.py` - corriger la policy.
- `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/astro-foundation-before.md` - preuve avant.
- `_condamad/stories/CS-010-corriger-resolution-evenements-astro-foundation/astro-foundation-after.md` - preuve apres.

Likely tests:

- `backend/tests/unit/prediction/test_public_astro_foundation.py` - nouveaux cas.
- `backend/app/tests/unit/test_public_projection.py` - non-regression.

Files not expected to change:

- `frontend/src` - schema inchange.
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py` - LLM hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app/prediction/public_projection.py tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py
pytest -q tests/unit/prediction/test_public_astro_foundation.py app/tests/unit/test_public_projection.py app/tests/integration/test_daily_prediction_api.py
rg -n "aspect_exact_to_angle|aspect_exact_to_luminary|aspect_exact_to_personal|detected_events" app/prediction
```

## 22. Regression Risks

- Risk: le fallback masque une source invalide.
  - Guardrail: `AC1` limite les sources a `events` et `detected_events`.
- Risk: un champ public est modifie par erreur.
  - Guardrail: `AC3` impose les tests de contrat.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - preuves `E-013`, `E-014`.
- `_condamad/audits/prediction/2026-05-03-2214/02-finding-register.md#F-005` - finding source.
- `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-005` - candidate d'origine.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
