# Story CS-164 enrichir-aspect-result-projection-publique: Enrichir AspectResult et la projection publique des aspects

Status: ready-to-dev

## 1. Objective

Faire consommer le runtime canonique des aspects par `AspectResult` et par la
projection chart publique. Le payload expose les champs enrichis sans lookups
disperses.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-14, priorite 4 `Enrichir AspectResult`.
- Reason for change: le resultat aspect reste plat et force les consommateurs a refaire des lookups vers les referentiels.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/services/chart`
- In scope:
  - enrichir la serialization chart des aspects depuis `AspectRuntimeData`;
  - conserver les champs existants `aspect_code`, `planet_a`, `planet_b`, `orb`, `orb_used`, `orb_max`;
  - mettre a jour les tests de JSON chart et contrats publics existants.
- Out of scope:
  - creer le runtime aspect lui-meme;
  - modifier les textes LLM;
  - modifier les tables SQL;
  - changer le frontend.
- Explicit non-goals:
  - Ne pas exposer de donnees produit prediction.
  - Ne pas supprimer de champ public existant sans decision utilisateur.
  - Ne pas changer `RG-091` a `RG-097`.

## 4. Operation Contract

- Operation type: update
- Primary archetype: api-contract-change
- Archetype reason: la story ajoute des champs au payload public chart sans retirer les champs existants.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Ajouts compatibles uniquement.
  - Champs historiques preserves.
  - Les valeurs enrichies viennent du runtime canonique, pas de lookups locaux.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un champ public existant doit etre renomme ou retire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le payload doit provenir d'`AspectRuntimeData`. |
| Baseline Snapshot | yes | Le JSON chart avant/apres doit etre compare. |
| Ownership Routing | yes | `services/chart` projette; `domain/astrology` calcule. |
| Allowlist Exception | no | Aucun fallback local n'est autorise. |
| Contract Shape | yes | La forme publique des aspects change par ajout. |
| Batch Migration | no | Migration frontend hors scope. |
| Reintroduction Guard | yes | Les lookups disperses et champs dupliques doivent etre bloques. |
| Persistent Evidence | yes | Snapshots JSON before/after requis. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AspectRuntimeData` produit par `backend/app/domain/astrology` et AST guard de serialization chart.
- Secondary evidence:
  - `backend/app/services/chart/json_builder.py` et tests de payload.
- Static scans alone are not sufficient for this story because:
  - le JSON public doit prouver que les champs enrichis sont serialises.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-164-enrichir-aspect-result-projection-publique/generated/aspect-public-payload-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-164-enrichir-aspect-result-projection-publique/generated/aspect-public-payload-after.md`
- Expected invariant:
  - les champs historiques restent presents; les nouveaux champs sont ajoutes.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Calcul runtime aspect | `backend/app/domain/astrology` | `services/chart` |
| Projection JSON publique | `backend/app/services/chart` | routeurs API |
| Types publics frontend | story ulterieure frontend | backend domain |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucun fallback ou exception n'est autorise.

## 4f. Contract Shape

- Contract type:
  - public chart JSON aspect item.
- Fields:
  - existing: `aspect_code`, `planet_a`, `planet_b`, `angle`, `orb`, `orb_used`, `orb_max`;
  - added: `family`, `strength_level`, `normalized_strength`, `phase_type`, `interpretive_valence`, `energy_type`, `is_exact`, `is_tight`.
- Required fields:
  - existing fields remain required where they are already required.
- Optional fields:
  - added fields may be nullable only when source reference data is absent and the absence is tested.
- Status codes:
  - no HTTP status change.
- Serialization names:
  - snake_case.
- Frontend type impact:
  - frontend may consume fields later; no required change here.
- Generated contract impact:
  - OpenAPI / schema diff if chart response schemas are generated.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: frontend migration is intentionally outside this backend story.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Payload before | `_condamad/stories/CS-164-enrichir-aspect-result-projection-publique/generated/aspect-public-payload-before.md` | Champs publics actuels. |
| Payload after | `_condamad/stories/CS-164-enrichir-aspect-result-projection-publique/generated/aspect-public-payload-after.md` | Champs enrichis. |
| OpenAPI diff | `generated/openapi-aspects-before-after.md` | Impact contrat public quand un schema chart existe. |

## 4i. Reintroduction Guard

- Guard type: unit tests de serialization + scan.
- Forbidden patterns:
  - recomposer `strength_level` dans `services/chart` par seuil local;
  - relire directement les tables de reference depuis le serializer;
  - retirer les champs historiques sans story de rupture.
- Guard command:
  `pytest -q app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/domain/astrology/natal_calculation.py` - `AspectResult` porte les champs plats.
- Evidence 2: `backend/app/services/chart/json_builder.py` - construit le JSON public chart.
- Evidence 3: `backend/app/tests/unit/test_chart_json_builder.py` - couvre la serialization publique.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- Les aspects publics incluent les champs enrichis issus du runtime canonique.
- Les champs plats existants restent presents.
- Aucun lookup de reference aspect n'est duplique dans la projection.
- Le diff public est documente.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-094` - la projection chart doit rester basee sur les runtime data canoniques.
  - `RG-095` - pas de dependance astrology vers prediction.
  - `RG-098` - le runtime aspect canonique doit rester la source de verite.
- Non-applicable invariants:
  - `RG-091` a `RG-093` - referentiels SQL non modifies.
- Required regression evidence:
  - tests JSON chart;
  - snapshot payload before/after;
  - scan anti-lookup local.
- Allowed differences:
  - ajout de champs publics aspect.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le payload aspect conserve les champs historiques. | `pytest -q app/tests/unit/test_chart_json_builder.py`. |
| AC2 | Le payload aspect expose `family`, `strength_level`, `normalized_strength`, `is_exact`, `is_tight`. | `pytest -q app/tests/unit/test_chart_json_builder.py`. |
| AC3 | Le runtime est l'unique source des champs d'interpretation. | `pytest -q app/tests/unit/test_chart_json_builder.py` + scan des champs enrichis. |
| AC4 | Le contrat public avant/apres est persiste. | `pytest -q app/tests/unit/test_chart_json_builder.py` + artefacts payload before/after. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le payload courant (AC: AC1, AC4)
  - [ ] Produire le snapshot before.

- [ ] Task 2 - Brancher la projection sur `AspectRuntimeData` (AC: AC2, AC3)
  - [ ] Adapter le builder/serializer chart.
  - [ ] Preserver les champs historiques.

- [ ] Task 3 - Tester le contrat public (AC: AC1, AC2, AC4)
  - [ ] Ajouter les assertions JSON.
  - [ ] Produire le snapshot after.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AspectRuntimeData` comme source enrichie.
  - `backend/app/services/chart/json_builder.py` comme owner de projection.
- Do not recreate:
  - des seuils de force aspect dans `services/chart`;
  - des lookups SQL locaux;
  - une deuxieme shape publique incompatible.
- Shared abstraction allowed only if:
  - elle supprime une duplication effective dans les serializers chart.

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

- seuils locaux `strong_ratio` dans `backend/app/services/chart`
- suppression de `aspect_code`, `planet_a`, `planet_b`, `orb`, `orb_max`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Runtime enrichi | `backend/app/domain/astrology/runtime` | serializer chart |
| Projection publique | `backend/app/services/chart` | routeurs API |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: constrained
- Reason: si une schema OpenAPI couvre les aspects chart, le diff doit montrer seulement des ajouts compatibles.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/runtime/aspect_runtime_data.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/chart/result_service.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/natal_calculation.py` - ajouter ou relier les champs runtime compatibles.
- `backend/app/services/chart/json_builder.py` - serializer les champs enrichis.
- `backend/app/services/chart/result_service.py` - transporter le runtime lorsque le service lit un resultat persiste.

Likely tests:

- `backend/app/tests/unit/test_chart_json_builder.py` - payload enrichi.
- `backend/app/tests/unit/test_chart_result_service.py` - persistance/lecture des champs enrichis.

Files not expected to change:

- `backend/migrations/**` - pas de changement SQL.
- `frontend/**` - consommation UI hors scope.
- `backend/app/domain/prediction/**` - pas de scoring produit.

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
pytest -q app/tests/unit/test_chart_json_builder.py app/tests/unit/test_chart_result_service.py
rg -n "strength_level|interpretive_valence|energy_type" app/services/chart app/domain/astrology -g "*.py"
```

## 22. Regression Risks

- Risk: rupture involontaire du payload chart.
  - Guardrail: snapshot before/after et tests JSON.
- Risk: duplication de logique runtime dans le serializer.
  - Guardrail: scan cible et review des owners.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respecter l'AGENTS.md: toute commande Python doit etre executee apres `.\.venv\Scripts\Activate.ps1`.

## 24. References

- Demande utilisateur du 2026-05-14 - priorite `Enrichir AspectResult`.
- `backend/app/services/chart/json_builder.py` - projection publique chart.
- `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/00-story.md` - prerequis runtime.
