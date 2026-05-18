# Story CS-183 fix-long-pytest-daily-prediction-aspects: Corriger les echecs longs des predictions quotidiennes lies aux aspects

Status: ready-to-review

## 1. Objective

Corriger les echecs de `pytest -q --long` lies aux aspects des predictions quotidiennes.
La correction doit conserver le runtime canonique des aspects, charger les profils depuis la
reference persistante du snapshot et refuser les fallbacks silencieux.

## 2. Trigger / Source

- Source type: user request
- Source reference: demande utilisateur du 2026-05-18 avec sortie `pytest -q --long`.
- Reason for change: les tests longs echouaient sur la resolution d'orbes natales, la projection
  publique des profils d'aspects et des doubles de tests incomplets par rapport au contrat runtime.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/prediction`
- In scope:
  - Corriger la resolution des orbes d'aspects natals dans le moteur de prediction.
  - Corriger le chargement des profils d'aspects pour les projections publiques et QA.
  - Aligner les tests et fixtures sur le contrat runtime canonique.
  - Mettre a jour les preuves CONDAMAD de la story.
- Out of scope:
  - Modifier le frontend.
  - Ajouter une dependance.
  - Ajouter une migration de schema.
  - Reecrire les poids produit ou les interpretations editoriales.
- Explicit non-goals:
  - Ne pas creer de regle generique `natal any/any`.
  - Ne pas charger une version active quand un snapshot fournit une reference persistante.
  - Ne pas ajouter de fallback silencieux pour un profil d'aspect manquant.
  - Ne pas creer de dossier de base dans `backend/`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story corrige un comportement runtime existant sans changer le contrat public
  attendu des routes quotidiennes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les orbes natales utilisent les regles ciblees existantes ou l'orbe canonique de l'aspect.
  - Les snapshots persistants gardent leur `reference_version_id` comme source de chargement.
  - Les doubles de test sans reference restent explicites.
  - Aucun schema HTTP public ne change.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: la correction exige une nouvelle source de verite astrologique.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les profils d'aspects et orbes doivent venir du runtime canonique. |
| Baseline Snapshot | yes | La suite longue avait un etat d'echec avant correction. |
| Ownership Routing | no | La frontiere prediction reste la meme. |
| Allowlist Exception | no | Aucune exception n'est autorisee. |
| Contract Shape | yes | Les profils d'aspects exposes au runtime portent l'orbe canonique. |
| Batch Migration | no | La story ne migre pas plusieurs surfaces par lots. |
| Reintroduction Guard | no | Aucun symbole legacy n'est supprime dans cette story. |
| Persistent Evidence | yes | Les validations longues doivent rester consignees dans la capsule. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - DB schema et snapshots persistants pour la version de reference chargee au runtime.
  - `backend/app/domain/prediction/aspect_reference.py` pour les profils d'aspects prediction.
  - `backend/app/domain/astrology/builders/aspect_runtime_builder.py` pour l'orbe canonique.
  - `reference_version_id` persistant du snapshot pour la projection publique.
- Secondary evidence:
  - Tests longs API daily, QA interne et regression moteur.
  - Fixtures de regression regenerees avec le runtime corrige.
  - AST guard et `MetaData` disponibles dans les validations backend existantes.
- Static scans alone are not sufficient for this story because:
  - Le risque principal apparait au chargement runtime des profils et des snapshots.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `artifacts/full_pytest_first_fail.log`
- Comparison after implementation:
  - `_condamad/stories/CS-183-fix-long-pytest-daily-prediction-aspects/generated/10-final-evidence.md`
- Expected invariant:
  - `pytest -q --long` passe sans regle `natal any/any` ajoutee.
  - Les fixtures de regression restent coherentes avec les profils d'aspects canoniques.
  - La projection publique utilise le `reference_version_id` persistant quand il existe.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: la story conserve les proprietaires existants du domaine prediction, des services et des
  routeurs.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - Dataclasses et profils runtime internes.
- Fields:
  - `AspectDefinition.default_orb_deg`
  - `AspectProfile.orb_max`
  - `DailyPredictionSnapshot.reference_version_id`
- Required fields:
  - `default_orb_deg` pour l'orbe canonique de l'aspect.
  - `orb_max` pour les aspects construits dans les tests de sensibilite natale.
  - `reference_version_id` quand un snapshot persistant le fournit.
- Optional fields:
  - Aucun champ optionnel nouveau.
- Status codes:
  - Aucun changement de statut HTTP attendu.
- Serialization names:
  - Aucun renommage de champ public.
- Frontend type impact:
  - Aucun impact frontend.
- Generated contract impact:
  - Aucun changement OpenAPI attendu.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Final evidence | `_condamad/stories/CS-183-fix-long-pytest-daily-prediction-aspects/generated/10-final-evidence.md` | Resultats Ruff et pytest longs. |
| Acceptance traceability | `_condamad/stories/CS-183-fix-long-pytest-daily-prediction-aspects/generated/03-acceptance-traceability.md` | Lien AC vers preuves. |
| Writing review | `_condamad/stories/CS-183-fix-long-pytest-daily-prediction-aspects/generated/11-writing-review.md` | Cycles review et corrections. |

## 4i. Reintroduction Guard

- Reintroduction guard: not applicable
- Reason: no legacy route, namespace, module, field or import is removed.

## 4j. Source Finding Closure

For non-audit stories:

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `artifacts/full_pytest_first_fail.log` - la suite longue exposait des echecs lies aux
  aspects des predictions quotidiennes.
- Evidence 2: `backend/app/domain/prediction/aspect_reference.py` - la resolution d'orbes prediction
  depend des profils runtime.
- Evidence 3: `backend/app/domain/astrology/builders/aspect_runtime_builder.py` - les definitions
  d'aspects portent l'orbe canonique.
- Evidence 4: `backend/app/domain/prediction/public_projection.py` - la projection publique charge les
  profils d'aspects du snapshot.
- Evidence 5: `backend/app/tests/unit/test_natal_structural_v3.py` - certains tests fabriquent des
  aspects natals.

## 6. Target State

After implementation:

- Les calculs natals resolvent les orbes via les regles ciblees ou l'orbe canonique d'aspect.
- Les projections publiques quotidiennes et QA chargent les profils par `reference_version_id`.
- Les doubles de test sans reference persistante restent explicites.
- Les tests de sensibilite natale construisent des aspects complets.
- Ruff et `pytest -q --long` passent dans le venv PowerShell du projet.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-035` - la frontiere du domaine prediction reste pure.
  - `RG-097` - les regles d'orbes d'aspects restent canoniques.
  - `RG-106` - les referentiels astrologiques runtime restent source de verite.
  - `RG-108` - les vocabulaires DB-backed ne doivent pas etre recrees en constantes locales.
  - `RG-112` - les constantes astrologiques DB-backed ne doivent pas revenir.
- Non-applicable invariants:
  - `RG-109` - la story ne modifie pas les libelles localises.
  - `RG-114` - la story ne traite pas les profils structurels de signes.
- Required regression evidence:
  - Tests longs des routes quotidiennes/API.
  - Tests longs QA interne.
  - Tests longs regression moteur.
  - Ruff.
- Allowed differences:
  - Fixtures de regression regenerees avec l'orbe canonique corrige.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Calculs natals sans regle generique. | Evidence profile: `runtime_openapi_contract`; `pytest app/tests/regression/test_engine_non_regression.py -q --long`. |
| AC2 | Projection publique par reference persistante. | Evidence profile: `runtime_openapi_contract`; `pytest app/tests/integration/test_daily_prediction_api.py -q --long`. |
| AC3 | Doubles de test sans version active implicite. | Evidence profile: `runtime_openapi_contract`; `pytest app/tests/integration/test_daily_prediction_qa.py -q --long`. |
| AC4 | Aspects natals de test complets. | Evidence profile: `json_contract_shape`; `pytest app/tests/unit/test_natal_structural_v3.py -q`. |
| AC5 | Validation longue complete verte. | Evidence profile: `runtime_openapi_contract`; `pytest -q --long`. |

## 8. Implementation Tasks

- [x] Task 1 - Corriger la resolution d'orbes natales (AC: AC1)
  - [x] Utiliser les regles ciblees par type et par corps.
  - [x] Utiliser l'orbe canonique de definition quand aucune regle ciblee ne correspond.

- [x] Task 2 - Corriger la projection publique des profils (AC: AC2, AC3)
  - [x] Charger les profils depuis le `reference_version_id` du snapshot.
  - [x] Garder explicites les doubles de test sans reference persistante.

- [x] Task 3 - Aligner les tests sur le contrat runtime (AC: AC4)
  - [x] Ajouter `orb_max` aux aspects natals fabriques par les tests.
  - [x] Regenerer les fixtures de regression avec le runtime corrige.

- [x] Task 4 - Valider la correction (AC: AC5)
  - [x] Executer Ruff dans le venv.
  - [x] Executer les tests cibles et `pytest -q --long` dans le venv.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AspectReferenceCatalog`
  - `AspectDefinition.default_orb_deg`
  - `reference_version_id` persistant du snapshot
  - repository de projection publique existant
- Do not recreate:
  - tables locales de profils d'aspects;
  - regles d'orbes concurrentes;
  - chemin actif de chargement des profils d'aspects.
- Shared abstraction allowed only if:
  - elle reste dans la frontiere prediction existante;
  - elle retire une duplication reelle;
  - elle ne devient pas une source de verite concurrente.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- fallback vers une regle generique natal any/any
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- regle generique natal any/any
- resolution publique par version active quand le snapshot fournit une reference persistante
- constante d'orbe hardcodee dans le moteur
- nouveau `requirements.txt`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Profils d'aspects prediction | `backend/app/domain/prediction/aspect_reference.py` | tables locales dans services ou routeurs |
| Orbe canonique d'aspect | `backend/app/domain/astrology/builders/aspect_runtime_builder.py` | constantes hardcodees dans le moteur |
| Projection publique | `backend/app/domain/prediction/public_projection.py` | chargement direct dans routeurs |
| Orchestration daily | `backend/app/services/prediction/public_predictions.py` | logique de projection dans API |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable.
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/prediction/aspect_reference.py`
- `backend/app/domain/prediction/event_detector.py`
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/api/v1/routers/internal/llm/qa.py`
- `backend/app/tests/unit/test_natal_structural_v3.py`
- `backend/app/tests/regression/test_engine_non_regression.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/prediction/aspect_reference.py`
- `backend/app/domain/prediction/event_detector.py`
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/services/prediction/public_predictions.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/api/v1/routers/internal/llm/qa.py`

Likely tests:

- `backend/app/tests/unit/test_natal_structural_v3.py`
- `backend/app/tests/integration/test_daily_prediction_api.py`
- `backend/app/tests/integration/test_daily_prediction_qa.py`
- `backend/app/tests/regression/test_engine_non_regression.py`
- `backend/app/tests/regression/fixtures/snapshot_full_day_A.json`
- `backend/app/tests/regression/fixtures/snapshot_full_day_B.json`

Files not expected to change:

- `frontend/src/App.tsx`
- `frontend/src/pages/Dashboard.tsx`
- `backend/pyproject.toml`
- `backend/requirements.txt`
- `backend/migrations/versions/20260322_0052_add_structured_fields_to_astrologer_profiles.py`

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest app/tests/integration/test_daily_prediction_api.py -q --long
pytest app/tests/regression/test_engine_non_regression.py -q --long
pytest app/tests/integration/test_daily_prediction_qa.py -q --long
pytest app/tests/unit/test_natal_structural_v3.py -q
pytest -q --long
```

Story validation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-183-fix-long-pytest-daily-prediction-aspects/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-183-fix-long-pytest-daily-prediction-aspects/00-story.md
```

## 22. Regression Risks

- Risk: une regle generique masque une reference manquante.
  - Guardrail: tests longs regression moteur et absence de fallback silencieux.
- Risk: les snapshots persistants chargent des profils incoherents.
  - Guardrail: tests API daily et QA interne par `reference_version_id`.
- Risk: les fixtures de test deviennent la source de verite.
  - Guardrail: tests unitaires alignes sur le contrat runtime.
- Risk: une validation Python est lancee hors venv.
  - Guardrail: commandes PowerShell avec activation depuis la racine.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not create compatibility wrappers, aliases, shims, silent fallbacks or duplicate profile sources.
- Do not add a backend base folder.
- All Python commands must run after `.\.venv\Scripts\Activate.ps1`.
- Keep the global French file comment and French docstrings on new or significantly modified Python files.

## 24. References

- `backend/app/domain/prediction/aspect_reference.py` - profils d'aspects prediction.
- `backend/app/domain/prediction/event_detector.py` - detection et orbes runtime.
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py` - orbe canonique de definition.
- `backend/app/domain/prediction/public_projection.py` - projection publique des snapshots.
- `backend/app/services/prediction/public_predictions.py` - orchestration des routes publiques.
- `backend/app/tests/unit/test_natal_structural_v3.py` - tests de sensibilite natale.
- `_condamad/stories/CS-183-fix-long-pytest-daily-prediction-aspects/generated/10-final-evidence.md` - preuves finales.
