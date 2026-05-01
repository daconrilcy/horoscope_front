# Story block-supported-family-prompt-fallbacks: Block fallback prompts for supported LLM families

Status: ready-for-dev

## 1. Objective

Bloquer `PROMPT_FALLBACK_CONFIGS` comme second proprietaire de prompts pour `chat`,
`guidance`, `natal` et `horoscope_daily`. Les assemblies et profils gouvernes
deviennent la source runtime unique pour les familles supportees.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prompt-generation/2026-04-30-1810`
- Reason for change: F-002 montre des prompts fallback executables pour des familles deja supportees.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/llm/prompting`
- In scope:
  - Retirer les cles supportees de `PROMPT_FALLBACK_CONFIGS`.
  - Encadrer strictement tout bootstrap non-prod conserve.
  - Ajouter une garde qui echoue si une famille supportee revient dans le fallback.
  - Prouver que la prod ne bascule jamais sur cette source.
- Out of scope:
  - Refaire le catalogue admin LLM.
  - Changer les routes QA 70.16.
  - Modifier les prompts versionnes publies.
- Explicit non-goals:
  - Ne pas recreer un runtime de secours concurrent.
  - Ne pas affaiblir les invariants `RG-004`, `RG-005`, `RG-006`.
  - Ne pas contourner les assemblies pour les familles supportees.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story durcit une regle runtime autour des fallbacks autorises.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les familles supportees echouent explicitement si leur assembly manque en prod.
  - Un bootstrap non-prod ne peut exister que par exception exacte.
  - Les fixtures de test restent separees du runtime nominal.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: le bootstrap dev sans assembly doit rester actif hors exception exacte.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La config chargee doit prouver la source effective. |
| Baseline Snapshot | no | La story ne preserve pas un comportement de fallback. |
| Ownership Routing | no | Aucun deplacement de responsabilite n'est requis. |
| Allowlist Exception | yes | Le bootstrap non-prod doit etre explicite s'il reste. |
| Contract Shape | no | Aucun DTO ou contrat HTTP n'est modifie. |
| Batch Migration | no | Une seule regle de catalogue est ciblee. |
| Reintroduction Guard | yes | Le retour des cles supportees doit echouer. |
| Persistent Evidence | yes | Les exceptions bootstrap doivent rester auditables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard over the loaded prompt catalog.
  - Test chargeant `build_fallback_use_case_config` pour chaque famille supportee.
  - Test gateway `missing_assembly` sur `chat`, `guidance`, `natal`, `horoscope_daily`.
- Secondary evidence:
  - `rg -n "PROMPT_FALLBACK_CONFIGS|build_fallback_use_case_config" backend/app backend/tests`
- Static scans alone are not sufficient for this story because:
  - la presence d'une cle n'indique pas si le gateway l'utilise en prod.

## 4c. Baseline / Before-After Rule

- Baseline rule: not applicable
- Reason: no behavior-preserving refactor, migration, route restructuring, or API contract change is involved.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/domain/llm/prompting/catalog.py` | test-only synthetic keys | Fixtures synthetiques hors familles supportees | permanent only for synthetic tests |
| `backend/app/ops/llm/bootstrap` | explicit non-prod bootstrap | Base vide dev uniquement apres decision | permanent condition: non-prod flag plus observable audit |

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

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Fallback exception audit | `_condamad/stories/block-supported-family-prompt-fallbacks/fallback-exception-audit.md` | Documenter les exceptions bootstrap. |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if:

- `PROMPT_FALLBACK_CONFIGS` contient `chat`;
- `PROMPT_FALLBACK_CONFIGS` contient `chat_astrologer`;
- `PROMPT_FALLBACK_CONFIGS` contient `guidance_contextual`;
- `PROMPT_FALLBACK_CONFIGS` contient `natal_interpretation`;
- `PROMPT_FALLBACK_CONFIGS` contient `horoscope_daily`.

Required architecture guard against reintroduction:
- Deterministic source: forbidden symbols.
- Evidence profile: `reintroduction_guard`; `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py` checks `PROMPT_FALLBACK_CONFIGS`.
- The guard must fail when supported fallback keys are reintroduced.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prompt-generation/2026-04-30-1810/01-evidence-log.md` - E-006 signale les prompts fallback.
- Evidence 2: `backend/app/domain/llm/prompting/catalog.py` - `PROMPT_FALLBACK_CONFIGS` contient des cles supportees.
- Evidence 3: `backend/app/domain/llm/runtime/gateway.py` - le gateway porte deja une logique de rejet missing assembly.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Aucune famille supportee ne possede de prompt runtime dans `PROMPT_FALLBACK_CONFIGS`.
- Le cas base vide non-prod est borne par flag et preuve observable si conserve.
- Les routes QA 70.16 continuent de verifier le pipeline canonique.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-006` - les couches non API ne doivent pas importer `app.api`.
  - `RG-004` - les erreurs applicatives restent centralisees.
- Non-applicable invariants:
  - `RG-016` - la story ne touche pas les tests narrator legacy.
  - `RG-007` - la story ne touche pas les routes admin observability.
- Required regression evidence:
  - Test missing assembly par famille.
  - Guard contre les cles fallback supportees.
  - Tests QA 70.16 cibles.
- Allowed differences:
  - Suppression des fallback prompts des familles supportees.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Supported fallback keys absent. | Evidence profile: `targeted_forbidden_symbol_scan`; `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py`. |
| AC2 | Production missing assembly rejected. | Evidence profile: `ast_architecture_guard`; `pytest -q tests/llm_orchestration/test_assembly_resolution.py`. |
| AC3 | Bootstrap exceptions exact. | Evidence profile: `allowlist_register_validated`; `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py`. |
| AC4 | QA pipeline remains canonical. | Evidence profile: `reintroduction_guard`; `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Inventorier les cles fallback supportees (AC: AC1)
- [ ] Task 2 - Retirer les prompts fallback supportes du runtime (AC: AC1)
- [ ] Task 3 - Encoder l'exception bootstrap exacte ou bloquer le bootstrap (AC: AC2, AC3)
- [ ] Task 4 - Ajouter une garde anti-reintroduction de cles supportees (AC: AC1, AC4)
- [ ] Task 5 - Executer les tests gateway et gouvernance dans le venv (AC: AC2, AC3, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/domain/llm/configuration/canonical_use_case_registry.py` pour les use cases supportes.
  - `backend/app/domain/llm/runtime/gateway.py` pour le rejet missing assembly.
  - `backend/app/ops/llm/bootstrap` pour le bootstrap borne.
- Do not recreate:
  - Un second catalogue de prompts.
  - Un fallback prompt par famille supportee.
  - Une source de modele separee du profil canonique.
- Shared abstraction allowed only if:
  - Elle valide une liste canonique de familles supportees deja exposee par la configuration.

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

- `PROMPT_FALLBACK_CONFIGS["chat"]`
- `PROMPT_FALLBACK_CONFIGS["chat_astrologer"]`
- `PROMPT_FALLBACK_CONFIGS["guidance_contextual"]`
- `PROMPT_FALLBACK_CONFIGS["natal_interpretation"]`
- `PROMPT_FALLBACK_CONFIGS["horoscope_daily"]`
- `legacy_use_case_fallback`

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

Codex must inspect before editing:

- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/llm/prompting/catalog.py` - retirer les cles supportees.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - ajouter la garde.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - verifier exceptions exactes.

Likely tests:

- `backend/tests/llm_orchestration/test_assembly_resolution.py` - couvrir missing assembly.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - bloquer les fallbacks supportes.

Files not expected to change:

- `frontend/src` - aucune surface frontend n'est dans le scope.
- `backend/app/api/v1/routers` - aucune route API n'est dans le scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\block-supported-family-prompt-fallbacks\00-story.md
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\block-supported-family-prompt-fallbacks\00-story.md
pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py
pytest -q tests/llm_orchestration/test_prompt_governance_registry.py
pytest -q tests/llm_orchestration/test_assembly_resolution.py
rg -n "PROMPT_FALLBACK_CONFIGS|legacy_use_case_fallback" app tests
ruff check .
```

## 22. Regression Risks

- Risk: base dev vide inutilisable.
  - Guardrail: exception bootstrap exacte avec flag non-prod.
- Risk: prompt runtime duplique.
  - Guardrail: test anti cles supportees dans `PROMPT_FALLBACK_CONFIGS`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Run every Python command after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/prompt-generation/2026-04-30-1810/03-story-candidates.md` - SC-002.
- `_condamad/audits/prompt-generation/2026-04-30-1810/01-evidence-log.md` - E-006, E-007, E-009.
- `_bmad-output/implementation-artifacts/70-16-documenter-valider-et-exposer-des-routes-de-test-pour-la-generation-llm.md` - QA canonique.
