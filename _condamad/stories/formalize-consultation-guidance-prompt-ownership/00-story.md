# Story formalize-consultation-guidance-prompt-ownership: Formalize consultation prompt ownership

Status: completed

## 1. Objective

Formaliser les consultations specifiques comme sous-cas canonique de `guidance_contextual`
ou bloquer l'implementation si une nouvelle famille LLM est exigee. Cette story adopte
l'hypothese repo indiquee par l'audit: les consultations thematiques restent sous `guidance`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prompt-generation/2026-04-30-1810`
- Reason for change: F-004 demande une decision explicite sur l'ownership prompt des consultations.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/services/llm_generation/guidance`
- In scope:
  - Documenter `consultation specifique` comme sous-cas de `guidance_contextual`.
  - Verifier les placeholders `situation`, `objective`, `natal_chart_summary`, contexte tiers.
  - Prouver qu'un refus precheck ne genere aucun prompt LLM.
  - Ajouter un guard contre des templates `prompt_content` divergents.
- Out of scope:
  - Creer une nouvelle famille LLM `consultation`.
  - Refaire le wizard consultation frontend.
  - Modifier les endpoints produit consultation.
- Explicit non-goals:
  - Ne pas creer de prompt owner dans `consultation_generation_service.py`.
  - Ne pas changer les invariants `RG-004`, `RG-005`, `RG-006`.
  - Ne pas introduire un fallback prompt de consultation.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: ownership-routing-refactor
- Archetype reason: la story decide le proprietaire canonique des prompts consultation.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les consultations continuent d'appeler `guidance_contextual`.
  - Les refus precheck restent sans appel LLM.
  - `prompt_content` ne devient pas un prompt LLM durable concurrent.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: le produit refuse l'ownership `guidance_contextual`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Une garde AST prouve le routage consultation vers guidance. |
| Baseline Snapshot | yes | Le mapping consultation vers guidance doit etre compare. |
| Ownership Routing | yes | Les responsabilites consultation doivent etre classees. |
| Allowlist Exception | yes | Les contenus DB autorises doivent etre bornes. |
| Contract Shape | no | Aucun contrat HTTP ou DTO n'est modifie. |
| Batch Migration | no | Aucun lot multi-famille n'est prevu. |
| Reintroduction Guard | yes | Une nouvelle famille `consultation` ne doit pas apparaitre sans decision. |
| Persistent Evidence | yes | Le mapping consultation avant/apres doit rester consultable. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard over `consultation_generation_service.py` and `guidance_service.py`.
  - Loaded config evidence for `guidance_contextual`.
- Secondary evidence:
  - `rg -n "guidance_contextual|consultation_contextual" backend/app/services backend/app/domain`
- Static scans alone are not sufficient for this story because:
  - le refus precheck doit prouver l'absence d'appel LLM par test executable.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/formalize-consultation-guidance-prompt-ownership/consultation-routing-before.md`
- Comparison after implementation:
  - `_condamad/stories/formalize-consultation-guidance-prompt-ownership/consultation-routing-after.md`
- Expected invariant:
  - Les consultations thematiques routent vers `guidance_contextual`.
- Allowed differences:
  - Documentation plus garde explicite de non-divergence.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Consultation orchestration | `backend/app/services/llm_generation/consultation_generation_service.py` | prompt durable |
| Contextual guidance prompt | `backend/app/services/llm_generation/guidance/guidance_service.py` | consultation template DB |
| Prompt governance | `backend/app/domain/llm/governance` | service feature ad hoc |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/infra/db/models/consultation_template.py` | `prompt_content` | Objectif produit court non prompt durable | permanent with guard against LLM instructions |
| `backend/app/services/llm_generation/consultation_generation_service.py` | precheck refusal text | Message metier avant LLM | permanent as non-provider path |

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
| Consultation routing before | `_condamad/stories/formalize-consultation-guidance-prompt-ownership/consultation-routing-before.md` | Capturer le mapping initial. |
| Consultation routing after | `_condamad/stories/formalize-consultation-guidance-prompt-ownership/consultation-routing-after.md` | Prouver la taxonomie finale. |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if:

- une famille `consultation` apparait dans `prompt_governance_registry.json`;
- un use case `consultation_contextual` apparait sans decision produit;
- `prompt_content` est traite comme `developer_prompt`;
- un refus precheck appelle `GuidanceService`.

Required architecture guard against reintroduction:
- Deterministic source: forbidden symbols.
- Evidence profile: `reintroduction_guard`; `pytest -q tests/unit/test_guidance_service.py` checks `consultation_contextual`.
- The guard must fail when a consultation LLM family is reintroduced.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prompt-generation/2026-04-30-1810/01-evidence-log.md` - E-012 route la consultation via guidance.
- Evidence 2: `backend/app/services/llm_generation/guidance/guidance_service.py` - le service utilise `guidance_contextual`.
- Evidence 3: `backend/app/services/llm_generation/consultation_generation_service.py` - `prompt_content` peut fournir l'objectif consultation.
- Evidence 4: `docs/llm-prompt-generation-by-feature.md` - documentation cible a mettre a jour.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- La documentation declare `consultation specifique` comme sous-cas de `guidance_contextual`.
- Les placeholders attendus sont testes.
- Les refus precheck bloquent toute generation LLM.
- `prompt_content` reste une donnee produit courte, pas une consigne provider durable.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-004` - les erreurs applicatives restent centralisees.
  - `RG-006` - les services ne doivent pas importer `app.api`.
- Non-applicable invariants:
  - `RG-016` - la story ne touche pas la narration horoscope.
  - `RG-007` - la story ne touche pas les endpoints observability.
- Required regression evidence:
  - Tests consultation precheck.
  - Tests guidance placeholders.
  - Scan de la registry gouvernance.
- Allowed differences:
  - Documentation du sous-cas consultation.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Consultation ownership documented. | Evidence profile: `targeted_forbidden_symbol_scan`; `rg -n "guidance_contextual" docs/llm-prompt-generation-by-feature.md`. |
| AC2 | Placeholder contract tested. | Evidence profile: `json_contract_shape`; `pytest -q tests/unit/test_guidance_service.py`. |
| AC3 | Precheck refusal stops LLM. | Evidence profile: `ast_architecture_guard`; `pytest -q tests/unit/test_consultation_generation_service.py`. |
| AC4 | No consultation family drift. | Evidence profile: `reintroduction_guard`; `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le mapping consultation vers guidance avant modification (AC: AC1)
- [x] Task 2 - Mettre a jour la documentation feature prompt (AC: AC1)
- [x] Task 3 - Ajouter les tests placeholders guidance contextual (AC: AC2)
- [x] Task 4 - Ajouter le test refus precheck sans appel LLM (AC: AC3)
- [x] Task 5 - Ajouter la garde anti nouvelle famille consultation (AC: AC4)
- [x] Task 6 - Executer les validations dans le venv (AC: AC2, AC3, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `GuidanceService.request_contextual_guidance_async` comme chemin LLM.
  - `backend/app/domain/llm/configuration/canonical_use_case_registry.py` pour le contrat `guidance_contextual`.
  - `docs/llm-prompt-generation-by-feature.md` pour la documentation.
- Do not recreate:
  - Une famille LLM `consultation`.
  - Un prompt durable dans `prompt_content`.
  - Une generation LLM apres refus precheck.
- Shared abstraction allowed only if:
  - Elle normalise les placeholders consultation vers guidance sans creer de prompt concurrent.

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

- `"consultation"` as LLM feature in `prompt_governance_registry.json`
- `consultation_contextual`
- `developer_prompt` sourced from `prompt_content`
- `PROMPT_FALLBACK_CONFIGS["consultation"]`
- `app.services.ai_engine_adapter`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Consultation objective | `consultation_generation_service.py` | `developer_prompt` DB |
| Contextual prompt execution | `guidance/guidance_service.py` | new consultation family |
| Prompt taxonomy | `domain/llm/governance` | service local registry |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/services/llm_generation/consultation_generation_service.py`
- `backend/app/services/llm_generation/guidance/guidance_service.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json`
- `docs/llm-prompt-generation-by-feature.md`

## 19. Expected Files to Modify

Likely files:

- `docs/llm-prompt-generation-by-feature.md` - documenter la taxonomie.
- `backend/app/services/llm_generation/consultation_generation_service.py` - clarifier le precheck ou la normalisation.
- `backend/app/services/llm_generation/guidance/guidance_service.py` - renforcer les placeholders.

Likely tests:

- `backend/tests/unit/test_guidance_service.py` - verifier le contrat placeholders.
- `backend/tests/unit/test_consultation_generation_service.py` - verifier refus precheck.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - bloquer la derive de taxonomie.

Files not expected to change:

- `frontend/src` - aucun changement de wizard.
- `backend/app/api/v1/routers` - aucun endpoint produit.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\formalize-consultation-guidance-prompt-ownership\00-story.md
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\formalize-consultation-guidance-prompt-ownership\00-story.md
pytest -q tests/unit/test_guidance_service.py
pytest -q tests/unit/test_consultation_generation_service.py
pytest -q tests/llm_orchestration/test_prompt_governance_registry.py
rg -n "\"consultation\"|consultation_contextual|developer_prompt.*prompt_content|PROMPT_FALLBACK_CONFIGS" app/domain app/services tests
ruff check .
```

## 22. Regression Risks

- Risk: nouvelle taxonomie implicite.
  - Guardrail: scan registry.
- Risk: refus precheck appelant le LLM.
  - Guardrail: test consultation avec mock guidance.

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

- `_condamad/audits/prompt-generation/2026-04-30-1810/03-story-candidates.md` - SC-004.
- `_condamad/audits/prompt-generation/2026-04-30-1810/01-evidence-log.md` - E-012.
- `_bmad-output/implementation-artifacts/70-16-documenter-valider-et-exposer-des-routes-de-test-pour-la-generation-llm.md` - guidance contextual canonique.
- `docs/llm-prompt-generation-by-feature.md` - documentation cible.
