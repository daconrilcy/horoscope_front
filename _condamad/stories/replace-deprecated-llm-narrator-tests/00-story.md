# Story replace-deprecated-llm-narrator-tests: Replace deprecated LLMNarrator tests with canonical adapter coverage

Status: ready-for-dev

## 1. Objective

Traiter les warnings de deprecation `LLMNarrator` dans les tests de prediction.
La couverture doit cibler l'adaptateur canonique `AIEngineAdapter.generate_horoscope_narration`.
Toute compatibilite temporaire doit etre documentee avec une sortie precise.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- Reason for change: F-105 signale 7 warnings deprecation `LLMNarrator` persistants.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: prediction LLM narration tests
- In scope:
  - Inventorier les tests qui instancient `LLMNarrator`.
  - Migrer la couverture vers `AIEngineAdapter.generate_horoscope_narration` quand le comportement est canonique.
  - Borner toute compatibilite temporaire par un registre et une garde warning.
  - Faire passer les tests prediction sous `-W error::DeprecationWarning`.
- Out of scope:
  - Reconcevoir le moteur LLM.
  - Changer les prompts produit.
  - Modifier les routes API.
- Explicit non-goals:
  - Ne pas masquer les warnings par filtre global.
  - Ne pas maintenir `LLMNarrator` comme facade nominale sans decision.
  - Ne pas affaiblir les gardes de frontiere API/service.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: service-boundary-refactor
- Archetype reason: les tests doivent cibler le service ou adaptateur canonique au lieu d'une facade depreciee.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les assertions de narration horoscope restent equivalentes.
  - La compatibilite `LLMNarrator` ne reste active que si une decision persistante l'exige.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: `LLMNarrator` doit rester supporte temporairement pour un consommateur externe ou un chemin produit non migre.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les warnings doivent etre prouves par execution pytest avec policy warnings. |
| Baseline Snapshot | yes | Les warnings deprecation doivent etre captures avant/apres. |
| Ownership Routing | yes | La narration canonique appartient a l'adaptateur LLM cible. |
| Allowlist Exception | yes | Toute compatibilite temporaire doit etre explicite. |
| Contract Shape | no | Aucun contrat API ou DTO n'est modifie. |
| Batch Migration | no | La migration cible une suite prediction bornee. |
| Reintroduction Guard | yes | Une garde doit echouer si un test nominal reinstancie `LLMNarrator`. |
| Persistent Evidence | yes | La decision migrate-or-keep et les warnings doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard plus `pytest -q -W error::DeprecationWarning tests/unit/prediction`.
- Secondary evidence:
  - Scan des imports `LLMNarrator` dans `backend/tests` et `backend/app/tests`.
- Static scans alone are not sufficient for this story because:
  - l'objectif est de supprimer les warnings emis au runtime pytest.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-warnings-before.md`
- Comparison after implementation:
  - `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-warnings-after.md`
- Expected invariant:
  - La suite prediction ne produit plus de `DeprecationWarning` non classe.
- Allowed differences:
  - Les tests migrent vers l'adaptateur canonique ou une compatibilite temporaire exacte est documentee.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Horoscope narration generation | `AIEngineAdapter.generate_horoscope_narration` | `LLMNarrator` facade nominale |
| Prediction narration tests | `backend/tests/unit/prediction` | Warnings ignores globaux |
| Temporary compatibility decision | `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md` | Memoire reviewer |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-decision.md` | `LLMNarrator` | Temporary compatibility. | Until exit condition is named. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Warning baseline | `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-warnings-before.md` | Capturer les 7 warnings actuels. |
| Deprecation decision | `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md` | Decider migration ou compatibilite temporaire. |
| Warning after | `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-warnings-after.md` | Prouver absence de warning non classe. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- AST imports in prediction tests
- pytest warning policy
- deprecation decision register

Required forbidden examples:

- `from app.prediction.llm_narrator import LLMNarrator`
- `LLMNarrator()`
- global ignore of `DeprecationWarning` for prediction tests

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q -W error::DeprecationWarning tests/unit/prediction` checks warning regressions.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md` - F-105 mentionne 7 warnings `LLMNarrator`.
- Evidence 2: `backend/tests/unit/prediction/test_llm_narrator.py` - le fichier importe et instancie `LLMNarrator`.
- Evidence 3: `backend/tests/integration/test_llm_governance_registry.py` - le fichier importe `LLMNarrator` avec filtre de warning local.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les tests de narration utilisent l'adaptateur canonique.
- La suite prediction passe avec `-W error::DeprecationWarning`.
- Toute compatibilite `LLMNarrator` restante est decidee, bornee et gardee.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-006` - la frontiere adaptateur API et services ne doit pas etre contournee.
  - `RG-014` - les tests remplaces doivent rester executables.
- Non-applicable invariants:
  - `RG-010` - aucune racine pytest n'est modifiee.
  - `RG-011` - aucun harnais DB n'est modifie.
- Required regression evidence:
  - `pytest -q -W error::DeprecationWarning tests/unit/prediction`
  - scan des usages `LLMNarrator`.
- Allowed differences:
  - Import test remplace par l'adaptateur canonique ou compatibilite documentee.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | LLMNarrator warning baseline is persisted. | Evidence profile: `baseline_before_after_diff`; `pytest -q tests/unit/prediction/test_llm_narrator.py`. |
| AC2 | Canonical narration adapter has equivalent coverage. | Evidence profile: `ast_architecture_guard`; `pytest -q tests/unit/prediction/test_llm_narrator.py`. |
| AC3 | Prediction tests reject unclassified deprecations. | Evidence profile: `runtime_openapi_contract`; `pytest -q -W error::DeprecationWarning tests/unit/prediction`. |
| AC4 | LLMNarrator nominal usage is guarded. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "LLMNarrator|llm_narrator" tests app/tests -g "test_*.py"`. |
| AC5 | Compatibility decision is persisted. | Evidence profile: `allowlist_register_validated`; `rg -n "LLMNarrator|llm_narrator" tests app/tests -g "test_*.py"`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture current warning baseline (AC: AC1)
- [ ] Task 2 - Decide migrate or temporary compatibility (AC: AC5)
- [ ] Task 3 - Move nominal coverage to canonical adapter (AC: AC2)
- [ ] Task 4 - Add warning and forbidden usage guard (AC: AC3, AC4)
- [ ] Task 5 - Persist after evidence (AC: AC1, AC3)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AIEngineAdapter.generate_horoscope_narration` for canonical narration behavior.
  - Existing prediction fixtures and prompt context builders where they preserve the same behavior.
- Do not recreate:
  - A second narrator facade for tests.
  - A global warning filter hiding `DeprecationWarning`.
- Shared abstraction allowed only if:
  - It is reused by multiple canonical adapter tests without reintroducing `LLMNarrator`.

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

- `from app.prediction.llm_narrator import LLMNarrator`
- `LLMNarrator()`
- `warnings.simplefilter("ignore", DeprecationWarning)` in nominal prediction tests
- global pytest warning ignore for `LLMNarrator`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Horoscope narration generation | `AIEngineAdapter.generate_horoscope_narration` | `LLMNarrator` test facade |
| Deprecation decision | `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md` | Inline warning suppression |
| Prediction warning guard | `backend/tests/unit/prediction` command with `-W error::DeprecationWarning` | Global ignore |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

If a product or external consumer still requires `LLMNarrator`, the dev agent must stop.
The consumer, exit condition and warning classification must be persisted before changing nominal tests.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md`
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/tests/unit/prediction/test_llm_narrator.py`
- `backend/tests/integration/test_llm_governance_registry.py`
- `backend/app/domain/llm/runtime/adapter.py`

## 19. Expected Files to Modify

Likely files:

- `backend/tests/unit/prediction/test_llm_narrator.py` - migrate nominal tests or rename target to canonical adapter coverage.
- `backend/tests/integration/test_llm_governance_registry.py` - classify any remaining compatibility use.
- `_condamad/stories/replace-deprecated-llm-narrator-tests/llm-narrator-deprecation-decision.md` - decision artifact.

Likely tests:

- `backend/tests/unit/prediction/test_llm_narrator.py` - canonical adapter coverage.
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py` - guard if a dedicated file is needed.

Files not expected to change:

- `backend/app/api` - no API behavior change.
- `frontend/src` - no frontend change.
- `requirements.txt` - must not be created.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests/unit/prediction/test_llm_narrator.py
pytest -q -W error::DeprecationWarning tests/unit/prediction
rg -n "LLMNarrator|llm_narrator" tests app/tests -g "test_*.py"
```

## 22. Regression Risks

- Risk: adapter tests lose an assertion previously covered by `LLMNarrator`.
  - Guardrail: one-to-one baseline of current test assertions before migration.
- Risk: warning filter hides a real deprecation.
  - Guardrail: `-W error::DeprecationWarning` command in validation.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respecter l'activation du venv avant toute commande Python.
- Ne pas creer de `requirements.txt`.

## 24. References

- `_condamad/audits/backend-tests/2026-04-29-1510/00-audit-report.md` - finding F-105.
- `_condamad/audits/backend-tests/2026-04-29-1510/03-story-candidates.md` - candidat SC-105.
- `_condamad/stories/regression-guardrails.md` - invariants RG-006 et RG-014.
- `backend/tests/unit/prediction/test_llm_narrator.py` - source de warnings deprecation.
