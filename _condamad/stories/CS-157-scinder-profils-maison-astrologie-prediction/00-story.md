# Story CS-157 scinder-profils-maison-astrologie-prediction: Scinder les profils maison astrologie et prediction

Status: ready-to-dev

## 1. Objective

Remplacer l'ambiguite de `HouseProfileData` par deux contrats explicites:
`HouseAstrologyProfile` pour les attributs astrologiques stables et
`HousePredictionProfile` pour les poids, priorites, mots-cles et notes produit.
Les poids `house_category_weights` restent dans le contexte prediction.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: demande utilisateur du 2026-05-13 sur `HouseAstrologyProfile` et `HousePredictionProfile`.
- Reason for change: `HouseProfileData` porte actuellement des champs produit comme `visibility_weight` et `base_priority`, ce qui rend la responsabilite de la maison ambigue.

## 3. Domain Boundary

- Domain: `backend/app/infra/db/repositories` contracts prediction/reference
- In scope:
  - creer des dataclasses distinctes pour profils astrologiques et profils prediction;
  - adapter `PredictionReferenceRepository` et `PredictionContext` sans changer les tables SQL;
  - garder `house_category_weights` comme donnee produit.
- Out of scope:
  - changement de noms de tables SQL;
  - migration des calculateurs vers `HouseRuntimeData`;
  - suppression physique immediate de tous les usages de `HouseProfileData` si cela demande une story produit separee.
- Explicit non-goals:
  - Ne pas recreer une table `houses`.
  - Ne pas deplacer les poids categorie vers `domain/astrology`.
  - Ne pas modifier les seeds metier hors adaptation de noms de contrats.
  - Ne pas changer les invariants `RG-092` et `RG-093`.

## 4. Operation Contract

- Operation type: split
- Primary archetype: custom
- Archetype reason: la story combine une scission de contrat Python interne et
  une migration bornee de consommateurs.
- Additional validation rules:
  - Les tests repository prouvent la charge DB des deux contrats scindes.
  - Les scans prouvent que `HouseProfileData` ne reste pas un contrat actif ambigu.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le contenu charge depuis la DB doit rester equivalent.
  - Les scores prediction ne doivent pas changer.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un consommateur externe depend nominalement de `HouseProfileData`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | la source runtime de verification est le schema DB charge par repository et contexte. |
| Baseline Snapshot | yes | les objets de contexte prediction avant/apres doivent etre compares. |
| Ownership Routing | yes | les champs astrologiques et produit doivent avoir des owners distincts. |
| Allowlist Exception | no | aucune compatibilite ou alias durable n'est autorise. |
| Contract Shape | yes | les dataclasses nouvelles sont le coeur de la story. |
| Batch Migration | yes | les consommateurs de `HouseProfileData` doivent etre migres par lot borne. |
| Reintroduction Guard | yes | `HouseProfileData` ne doit pas rester un contrat actif ambigu. |
| Persistent Evidence | yes | inventaire des consommateurs avant/apres requis. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - DB schema inspected through `inspect()` plus
    `backend/app/infra/db/repositories/prediction_reference_repository.py`.
- Secondary evidence:
  - scans for `HouseProfileData`, `visibility_weight`, `base_priority` and `routing_role` in target packages.
- Static scans alone are not sufficient for this story because:
  - the repository and context loader must prove the split contracts are loaded and frozen correctly.

## 4c. Baseline / Before-After Rule

- Baseline required: yes
- Baseline artifact before implementation:
  - `_condamad/stories/CS-157-scinder-profils-maison-astrologie-prediction/generated/house-profile-consumers-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-157-scinder-profils-maison-astrologie-prediction/generated/house-profile-consumers-after.md`
- Expected invariant:
  - les valeurs chargees depuis les tables prediction restent equivalentes; seule la shape Python est scindee.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Profil astrologique stable maison | `backend/app/domain/astrology/reference` | `backend/app/domain/prediction` |
| Profil produit maison | `backend/app/infra/db/repositories/prediction_schemas.py` or product reference contract module | `backend/app/domain/astrology` |
| Poids maison categorie | `PredictionContext.house_category_weights` | `backend/app/domain/astrology` |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: la story ne doit pas conserver `HouseProfileData` comme alias de compatibilite durable.

## 4f. Contract Shape

Contract type:
- Python dataclasses.
Fields:
- `HouseAstrologyProfile`: `house_number`, `house_kind`, `natural_theme`.
- `HousePredictionProfile`: `house_number`, `visibility_weight`, `base_priority`, `keywords`, `micro_note`.
Required fields:
- `HouseAstrologyProfile.house_number`.
- `HouseAstrologyProfile.house_kind`.
- `HousePredictionProfile.house_number`.
- `HousePredictionProfile.visibility_weight`.
- `HousePredictionProfile.base_priority`.
Optional fields:
- `natural_theme`.
- `keywords`.
- `micro_note`.
Status codes:
- none.
Serialization names:
- Internal Python contract only.
Frontend type impact:
- none.
Generated contract impact:
- none.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | `HouseProfileData` | split profiles | repository/context | repo/context tests | scan old symbol | external consumer |
| 2 | `PredictionContext.house_profiles` | explicit profiles | prediction context | prediction tests | no alias | scoring diff |

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `generated/house-profile-consumers-before.md` | Known consumers. |
| After inventory | `generated/house-profile-consumers-after.md` | Residual hits classified. |
| Context shape | `generated/prediction-context-shape-after.md` | Explicit profiles loaded. |

## 4i. Reintroduction Guard

- Guard type: targeted scan or AST test.
- Forbidden patterns:
  - active `class HouseProfileData` after migration unless explicitly deleted in same story;
  - `visibility_weight` under `backend/app/domain/astrology`;
  - `base_priority` under `backend/app/domain/astrology`.
- Guard command:
  `rg -n "class HouseProfileData|HouseProfileData|visibility_weight|base_priority" app/domain app/infra/db/repositories app/services/prediction app/tests tests -g "*.py"`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/infra/db/repositories/prediction_schemas.py` - `HouseProfileData` contient `visibility_weight` et `base_priority`.
- Evidence 2: `backend/app/infra/db/repositories/prediction_reference_repository.py` - `get_house_profiles` construit `HouseProfileData`.
- Evidence 3: `backend/app/services/prediction/context_loader.py` - le contexte prediction fige `HouseProfileData`.
- Evidence 4: `docs/tables-maisons-et-roles.md` - `house_category_weights` est documente comme routage maison vers categorie.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- Les attributs astrologiques stables de maison ont un contrat distinct.
- Les attributs produit de prediction ont un contrat distinct.
- Les consommateurs de contexte prediction lisent le profil produit explicite.
- Les residus de `HouseProfileData` sont supprimes ou classes comme historiques dans les preuves, sans alias actif.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-092` - ne pas reversionner les referentiels structurels.
  - `RG-093` - ne pas ramener les anciens noms actifs de signes ou maitrises.
- Non-applicable invariants:
  - `RG-094` - cette story ne change pas la serialization des maitres runtime.
- Required regression evidence:
  - tests repository/context loader;
  - scans des anciens symboles;
  - preuve de shape context before/after.
- Allowed differences:
  - noms de dataclasses et champs scindes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les deux profils remplacent le contrat ambigu. | `pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_context_loader.py`. |
| AC2 | Les champs produit restent hors `domain/astrology`. | `rg -n "visibility_weight|base_priority|routing_role" app/domain/astrology -g "*.py"` zero-hit. |
| AC3 | Les calculateurs gardent des scores equivalents. | `pytest -q app/tests/unit/test_domain_router.py app/tests/unit/test_natal_sensitivity.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Scinder les dataclasses de profil maison (AC: AC1)
  - [ ] Subtask 1.1 - Inventorier les usages de `HouseProfileData`.
  - [ ] Subtask 1.2 - Introduire les deux contrats explicites au bon owner.

- [ ] Task 2 - Migrer le chargement et le contexte prediction (AC: AC1, AC3)
  - [ ] Subtask 2.1 - Adapter `PredictionReferenceRepository`.
  - [ ] Subtask 2.2 - Adapter `context_loader` et les tests.

- [ ] Task 3 - Verrouiller la separation (AC: AC2)
  - [ ] Subtask 3.1 - Ajouter la preuve de scan anti-produit dans astrology.
  - [ ] Subtask 3.2 - Classer ou supprimer les residus `HouseProfileData`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PredictionContext` existant pour porter les donnees produit.
  - les modeles SQL `HouseProfileModel` et `HouseCategoryWeightModel`.
- Do not recreate:
  - un repository maison parallele;
  - une seconde source SQL pour les profils prediction;
  - des aliases `HouseProfileData = HousePredictionProfile`.
- Shared abstraction allowed only if:
  - elle remplace un usage concret de contrat duplique et a un seul owner.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `HouseProfileData` comme contrat actif ambigu.
- `backend/app/domain/astrology/**` contenant `visibility_weight`, `base_priority`, `routing_role`.
- `HousePredictionProfile` sous `backend/app/domain/astrology`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Profil astrologique stable maison | `backend/app/domain/astrology/reference` | prediction repository if product fields mixed |
| Profil produit maison | `backend/app/infra/db/repositories/prediction_schemas.py` or product reference contract | `backend/app/domain/astrology` |
| Poids maison -> categorie | `PredictionContext.house_category_weights` | astrology runtime/reference |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/services/prediction/context_loader.py`
- `backend/app/domain/prediction/domain_router.py`
- `backend/app/domain/prediction/natal_sensitivity.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/unit/test_context_loader.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/infra/db/repositories/prediction_schemas.py` - scinder les dataclasses.
- `backend/app/infra/db/repositories/prediction_reference_repository.py` - construire les nouveaux contrats.
- `backend/app/services/prediction/context_loader.py` - freezer les nouveaux contrats.

Likely tests:

- `backend/app/tests/unit/test_prediction_reference_repository.py` - shape repository.
- `backend/app/tests/unit/test_context_loader.py` - freezing context.
- `backend/app/tests/unit/test_engine_orchestrator.py` - non-regression orchestration.

Files not expected to change:

- `backend/migrations/**` - aucun changement de schema.
- `backend/app/domain/astrology/runtime/house_runtime_data.py` - runtime maison traite par CS-155.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_context_loader.py
pytest -q app/tests/unit/test_domain_router.py app/tests/unit/test_natal_sensitivity.py app/tests/unit/test_engine_orchestrator.py
ruff check .
rg -n "visibility_weight|base_priority|routing_role" app/domain/astrology -g "*.py"
rg -n "HouseProfileData" app tests -g "*.py"
```

## 22. Regression Risks

- Risk: les scores prediction changent par erreur pendant la scission de contrat.
  - Guardrail: tests `DomainRouter`, `NatalSensitivityCalculator`, `EngineOrchestrator`.
- Risk: un alias legacy masque la migration.
  - Guardrail: scan `HouseProfileData` et preuve de classification.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unfinished work, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 24. References

- Demande utilisateur du 2026-05-13 - scission `HouseAstrologyProfile` / `HousePredictionProfile`.
- `docs/tables-maisons-et-roles.md` - roles actuels des tables et calculateurs.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
