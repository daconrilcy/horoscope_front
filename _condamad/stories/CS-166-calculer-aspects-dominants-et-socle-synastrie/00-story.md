# Story CS-166 calculer-aspects-dominants-et-socle-synastrie: Calculer les aspects dominants et preparer le socle synastrie

Status: ready-to-dev

## 1. Objective

Ajouter `DominantAspectEvaluator` base sur `AspectRuntimeData` et definir le
contrat minimal reutilisable pour calculer des aspects inter-chart. Aucun
endpoint de synastrie n'est cree dans cette story.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-14, priorites 6 `Dominant Aspects` et 7 `Synastrie`.
- Reason for change: les maisons dominantes existent conceptuellement, mais les aspects dominants et le calcul inter-chart n'ont pas de service canonique.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology`
- In scope:
  - creer un evaluateur d'aspects dominants;
  - definir le contrat de score dominant aspect;
  - extraire un calculateur reutilisable pour aspects intra-chart et inter-chart;
  - ajouter tests unitaires sur classement et reutilisation inter-chart.
- Out of scope:
  - creer une API de synastrie;
  - creer une UI de compatibilite;
  - generer des interpretations relationnelles LLM;
  - modifier les referentiels SQL.
- Explicit non-goals:
  - Ne pas ajouter de tables synastrie.
  - Ne pas dupliquer `astral_aspect_definitions`, `astral_aspect_orb_rules`, `astral_aspect_profiles` ou `astral_aspect_interpretation_profiles`.
  - Ne pas introduire de scoring produit prediction.

## 4. Operation Contract

- Operation type: create
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story ajoute des contrats runtime derives sans changer les referentiels ni les APIs.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le classement dominant doit etre deterministe.
  - Les facteurs autorises sont orbe, luminaire, angularite si disponible, famille aspect et intensite planetaire.
  - Le socle inter-chart reutilise le meme resolver d'aspects.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: la ponderation astrologique des dominants doit devenir produit/editoriale.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les dominants derivent d'`AspectRuntimeData`. |
| Baseline Snapshot | yes | Le classement dominant attendu doit etre documente. |
| Ownership Routing | yes | Astrology possede le calcul, prediction/API/UI consommeront plus tard. |
| Allowlist Exception | no | Aucun scoring fallback n'est autorise. |
| Contract Shape | yes | Le contrat `DominantAspectRuntimeData` doit etre explicite. |
| Batch Migration | no | Aucun consommateur n'est migre ici. |
| Reintroduction Guard | yes | La duplication des referentiels pour synastrie doit etre bloquee. |
| Persistent Evidence | yes | Exemples de classement et scans anti-duplication requis. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AspectRuntimeData`, resolver d'aspects existant et AST guard anti-duplication synastrie.
- Secondary evidence:
  - tests dominants et inter-chart.
- Static scans alone are not sufficient for this story because:
  - le classement doit etre prouve sur fixtures deterministes.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-166-calculer-aspects-dominants-et-socle-synastrie/generated/dominant-aspects-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-166-calculer-aspects-dominants-et-socle-synastrie/generated/dominant-aspects-after.md`
- Expected invariant:
  - aucun referentiel aspect n'est duplique pour la synastrie.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Classement aspects dominants | `backend/app/domain/astrology/interpretation` ou `runtime` | `domain/prediction` |
| Calcul inter-chart aspect | `backend/app/domain/astrology/calculators` | endpoint API dedie |
| Synastrie publique/API | story future | cette story |

## 4e. Allowlist / Exception Register

- Allowlist exception: not applicable
- Reason: aucune exception ou duplication de referentiel n'est autorisee.

## 4f. Contract Shape

- Contract type:
  - Python runtime data contract.
- Fields:
  - `aspect_runtime`, `dominance_score`, `rank`, `reasons`, `score_factors`.
- Required fields:
  - `aspect_runtime`, `dominance_score`, `rank`, `reasons`.
- Optional fields:
  - `score_factors`.
- Status codes:
  - none.
- Serialization names:
  - snake_case.
- Frontend type impact:
  - none direct.
- Generated contract impact:
  - none.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: aucun consommateur n'est migre.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Dominants before | `_condamad/stories/CS-166-calculer-aspects-dominants-et-socle-synastrie/generated/dominant-aspects-before.md` | Absence d'evaluateur. |
| Dominants after | `_condamad/stories/CS-166-calculer-aspects-dominants-et-socle-synastrie/generated/dominant-aspects-after.md` | Classement fixture. |
| Synastry reuse scan | `generated/synastry-reference-reuse-scan.md` | Absence de duplication referentielle. |

## 4i. Reintroduction Guard

- Guard type: unit tests + scan.
- Forbidden patterns:
  - nouvelle table de definitions/orbes synastrie;
  - copie locale de familles/profils aspect pour synastrie;
  - scoring dominant dans `domain/prediction`.
- Guard command:
  `pytest -q tests/unit/domain/astrology/test_dominant_aspects.py tests/unit/domain/astrology/test_interchart_aspects.py`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/domain/astrology/calculators/aspects.py` - calcul et resolution des aspects existants.
- Evidence 2: `backend/app/domain/astrology/runtime/house_runtime_data.py` - precedent de runtime dominant maison.
- Evidence 3: `backend/app/domain/prediction/natal_sensitivity.py` - certains consommateurs calculent deja des poids d'aspects cote produit.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- Un evaluateur classe les aspects dominants de facon deterministe.
- Les raisons de dominance sont structurees.
- Le calcul inter-chart reutilise les definitions/orbes/profils existants.
- Aucune surface API synastrie n'est creee dans cette story.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-095` - astrology ne depend pas de prediction.
  - `RG-097` - les regles d'orbes par systeme restent canoniques.
  - `RG-098` - le runtime aspect canonique reste la source.
  - `RG-100` - l'interpretation aspect reste separee du LLM/API.
- Non-applicable invariants:
  - `RG-091` a `RG-094` - pas de changement SQL maisons/signes.
- Required regression evidence:
  - tests classement dominant;
  - tests inter-chart reutilisant les aspects;
  - scan anti-duplication de referentiels synastrie.
- Allowed differences:
  - ajout de contrats runtime internes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les aspects dominants sont tries par score deterministe. | `pytest -q tests/unit/domain/astrology/test_dominant_aspects.py`. |
| AC2 | Le score de dominance augmente quand l'orbe se resserre. | `pytest -q tests/unit/domain/astrology/test_dominant_aspects.py`. |
| AC3 | Le calcul inter-chart reutilise le resolver aspect existant. | `pytest -q tests/unit/domain/astrology/test_interchart_aspects.py`. |
| AC4 | Aucun referentiel synastrie duplique n'est cree. | `rg -n "synastry.*aspect|aspect.*synastry" app docs -g "*.py" -g "*.md"` avec classification. |
| AC5 | `domain/prediction` ne devient pas owner des dominants. | `rg -n "DominantAspect|dominant_aspect" app/domain/prediction -g "*.py"` attendu zero hit. |

## 8. Implementation Tasks

- [ ] Task 1 - Definir le contrat de dominance (AC: AC1, AC2)
  - [ ] Ajouter le runtime/data contract dominant aspect.
  - [ ] Definir les raisons/facteurs de score.

- [ ] Task 2 - Implementer l'evaluateur dominant (AC: AC1, AC2, AC5)
  - [ ] Calculer le classement depuis `AspectRuntimeData`.
  - [ ] Garder la logique hors prediction.

- [ ] Task 3 - Extraire le socle inter-chart (AC: AC3, AC4)
  - [ ] Reutiliser le resolver aspect existant pour deux ensembles de positions.
  - [ ] Ne pas creer de nouveau referentiel.

- [ ] Task 4 - Ajouter preuves et guards (AC: AC1, AC2, AC3, AC4, AC5)
  - [ ] Ajouter tests unitaires.
  - [ ] Capturer artefacts generated.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AspectRuntimeData`.
  - `backend/app/domain/astrology/calculators/aspects.py`.
  - referentiels `astral_aspect_*` existants.
- Do not recreate:
  - tables ou JSON synastrie dedies aux aspects;
  - ponderations produit prediction;
  - resolver d'orbes.
- Shared abstraction allowed only if:
  - elle sert effectivement natal et inter-chart sans changer les contrats publics.

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

- nouvelle table `synastry_aspect_*`
- copie de `astral_aspect_definitions` pour synastrie
- `DominantAspect` dans `backend/app/domain/prediction`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Dominance aspects | `backend/app/domain/astrology` | prediction, API |
| Inter-chart aspect calculation | `backend/app/domain/astrology/calculators` | routeur synastrie |
| API synastrie | story future | cette story |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/astrology/runtime/aspect_runtime_data.py`
- `backend/app/domain/astrology/interpretation/aspect_strength.py`
- `backend/app/domain/prediction/natal_sensitivity.py`
- `backend/app/tests/unit/test_aspects_calculator.py`
- `backend/app/tests/unit/test_aspect_orb_overrides.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/dominant_aspects.py` - evaluateur dominant.
- `backend/app/domain/astrology/runtime/dominant_aspect_runtime_data.py` - contrat de sortie.
- `backend/app/domain/astrology/calculators/aspects.py` - extraction reutilisable inter-chart.

Likely tests:

- `backend/tests/unit/domain/astrology/test_dominant_aspects.py` - classement.
- `backend/tests/unit/domain/astrology/test_interchart_aspects.py` - reutilisation inter-chart.
- `backend/app/tests/unit/test_aspect_orb_overrides.py` - non-regression orbes.

Files not expected to change:

- `backend/migrations/**` - aucun changement SQL.
- `frontend/**` - pas d'UI synastrie.
- `backend/app/api/**` - pas d'endpoint synastrie.

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
pytest -q tests/unit/domain/astrology/test_dominant_aspects.py tests/unit/domain/astrology/test_interchart_aspects.py
pytest -q app/tests/unit/test_aspect_orb_overrides.py
rg -n "DominantAspect|dominant_aspect" app/domain/prediction -g "*.py"
rg -n "synastry.*aspect|aspect.*synastry" app docs -g "*.py" -g "*.md"
rg -n "app\\.domain\\.prediction|app\\.services\\.prediction" app/domain/astrology -g "*.py"
```

## 22. Regression Risks

- Risk: dominance devient un scoring produit cache.
  - Guardrail: owner astrology + scan prediction.
- Risk: synastrie duplique les referentiels.
  - Guardrail: scan anti-duplication et tests inter-chart.
- Risk: classement instable.
  - Guardrail: fixture deterministe.

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

- Demande utilisateur du 2026-05-14 - priorites `Dominant Aspects` et `Synastrie`.
- `_condamad/stories/CS-163-creer-runtime-canonique-force-aspects/00-story.md` - prerequis runtime.
- `backend/app/domain/astrology/calculators/aspects.py` - resolver aspect existant.
