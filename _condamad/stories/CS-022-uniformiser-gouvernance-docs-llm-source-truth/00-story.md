# Story CS-022 uniformiser-gouvernance-docs-llm-source-truth: Uniformiser la gouvernance des docs LLM source-of-truth

Status: ready-to-dev

## 1. Objective

Uniformiser le statut des documents LLM sous `backend/docs/`. Chaque document source-of-truth doit etre
genere, valide par une garde executable, ou marque comme note humaine non canonique. La story conserve les
gardes existantes de `llm-model-structure.md` et `llm-db-cleanup-registry.json`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-docs/2026-05-04-1826/03-story-candidates.md#SC-003`
- Reason for change: le finding `F-003` montre une gouvernance LLM inegale entre docs generees/executees et prose source-of-truth non gardee.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/llm`
- In scope:
  - Classer `backend/docs/llm-*.md` et `backend/docs/llm-db-cleanup-registry.json`.
  - Preserver la garde de generation de `llm-model-structure.md`.
  - Preserver le contrat executable du registre `llm-db-cleanup-registry.json`.
  - Ajouter un statut explicite pour `llm-runtime-source-of-truth.md` et `llm-canonical-consumption-rebuild.md`.
  - Ajouter une garde doc/source-of-truth pour tout document LLM qui reste normatif.
- Out of scope:
  - Modifier le runtime LLM, les prompts, assemblies ou providers.
  - Deplacer le registre JSON hors `backend/docs` sans decision utilisateur.
  - Changer les migrations LLM ou la DB.
  - Reorganiser toute la documentation backend hors docs LLM.
- Explicit non-goals:
  - Ne pas affaiblir `RG-007`, `RG-018`, `RG-019`, `RG-020`, `RG-021` ou `RG-022`.
  - Ne pas dupliquer les registres LLM existants.
  - Ne pas recreer des fallbacks prompts supportes.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story durcit les regles de gouvernance documentaire LLM via tests et classifications sans changer le runtime.
- Behavior change allowed: no
- Behavior change constraints:
  - Les comportements LLM runtime, prompts, providers et DB ne changent pas.
  - Les docs changent uniquement pour clarifier leur statut ou ajouter des gardes.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un document LLM non garde doit rester source de verite normative mais aucune source runtime deterministe n'est disponible.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les docs normatives LLM doivent etre verifiees par code, registre ou runtime observable. |
| Baseline Snapshot | yes | L'inventaire des docs LLM et de leurs gardes doit etre capture avant/apres. |
| Ownership Routing | no | Pas de deplacement de responsabilite applicative. |
| Allowlist Exception | yes | Les docs LLM non normatives restantes doivent etre des exceptions explicites et testees. |
| Contract Shape | no | Aucun API, DTO, OpenAPI ou type frontend n'est touche. |
| Batch Migration | no | Pas de migration multi-lot. |
| Reintroduction Guard | yes | La garde doit bloquer une nouvelle source-of-truth LLM non classee/non gardee. |
| Persistent Evidence | yes | La classification LLM doit rester auditable. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard dans `backend/app/tests/unit/test_llm_docs_governance.py`.
  - `backend/tests/unit/test_llm_canonical_perimeter.py` pour `llm-model-structure.md`.
  - `backend/tests/integration/test_llm_db_cleanup_registry.py` et `app.ops.llm.db_cleanup_validator` pour le registre JSON.
  - Garde a ajouter pour les statuts LLM source-of-truth restants.
- Secondary evidence:
  - `rg -n "llm-runtime-source-of-truth|llm-canonical-consumption-rebuild|llm-model-structure|llm-db-cleanup-registry" backend/app backend/tests`
- Static scans alone are not sufficient for this story because:
  - Une doc peut etre referencee sans etre normative; la garde doit prouver le lien a une source executable.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/llm-doc-governance-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/llm-doc-governance-after.md`
- Expected invariant:
  - Toute doc LLM normative est generee, validee par source executable, ou declassifiee comme non canonique.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/docs/llm-runtime-source-of-truth.md` | LLM runtime prose | Non canonique ou garde runtime. | Decision permanente. |
| `backend/docs/llm-canonical-consumption-rebuild.md` | LLM rebuild prose | Note de rebuild uniquement si non canonique. | Decision permanente. |

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
| Classification LLM docs | `llm-doc-governance.md` | Classer chaque doc LLM par statut, source executable et garde. |
| Inventaire avant | `llm-doc-governance-before.md` | Capturer le statut initial des docs LLM. |
| Inventaire apres | `llm-doc-governance-after.md` | Prouver le statut final et les gardes associees. |

## 4i. Reintroduction Guard

- Guard target:
  - Nouveau document `backend/docs/llm-*` qui revendique `source-of-truth`, `canonical` ou `canonique` sans garde ou statut historique.
  - Suppression des gardes existantes pour `llm-model-structure.md` ou `llm-db-cleanup-registry.json`.
- Guard evidence:
  - Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_llm_docs_governance.py`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - `E-004` prouve que `llm-model-structure.md` est garde par generation.
- Evidence 2: `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - `E-005` prouve que `llm-db-cleanup-registry.json` est consomme par un validateur.
- Evidence 3: `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - `E-006` ne trouve pas
  de garde directe active pour `llm-runtime-source-of-truth.md` et `llm-canonical-consumption-rebuild.md`.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Chaque doc LLM sous `backend/docs/` a un statut exact dans `llm-doc-governance.md` ou `backend/docs/ownership-index.md`.
- `llm-model-structure.md` reste genere et compare au code.
- `llm-db-cleanup-registry.json` reste executable et valide.
- Les docs source-of-truth restantes sont gardees ou declassifiees comme notes historiques/humaines.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-007` - les endpoints admin LLM observability restent possedes par leur router canonique.
  - `RG-018` - les familles prompt supportees ne doivent pas redevenir proprietaires via fallback.
  - `RG-021` - les cles fallback restantes doivent garder une decision persistante exacte.
  - `RG-022` - les plans de validation prompt-generation doivent pointer vers des tests collectes.
  - `RG-042` - invariant cree par cette story pour la gouvernance des docs LLM source-of-truth.
- Non-applicable invariants:
  - `RG-025` - Stripe n'est pas touche.
  - `RG-039` - scheduled tasks/scripts non touches.
- Required regression evidence:
  - Tests LLM existants, nouvelle garde doc governance, scan des termes `source-of-truth/canonical/canonique`.
- Allowed differences:
  - Clarification documentaire uniquement; aucun changement runtime LLM.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les docs LLM sont classees dans le registre. | Evidence profile: `ownership_inventory`; `pytest -q app/tests/unit/test_llm_docs_governance.py`. |
| AC2 | `llm-model-structure.md` conserve sa garde de generation exacte. | Evidence profile: `generated_doc_guard`; `pytest -q tests/unit/test_llm_canonical_perimeter.py`. |
| AC3 | `llm-db-cleanup-registry.json` conserve son validateur. | Evidence profile: `executable_registry_guard`; `pytest -q tests/integration/test_llm_db_cleanup_registry.py`. |
| AC4 | Les docs LLM non gardees ne sont plus normatives. | Evidence profile: `source_of_truth_guard`; `pytest -q app/tests/unit/test_llm_docs_governance.py`. |
| AC5 | Les tests runtime LLM cibles restent passants. | Evidence profile: `runtime`; `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Inventorier les docs LLM et leurs gardes existantes (AC: AC1, AC2, AC3)
- [x] Task 2 - Ecrire `llm-doc-governance.md` ou completer l'index docs si disponible (AC: AC1)
- [x] Task 3 - Classer ou garder `llm-runtime-source-of-truth.md` et `llm-canonical-consumption-rebuild.md` (AC: AC4)
- [x] Task 4 - Ajouter une garde anti source-of-truth non classee (AC: AC1, AC4)
- [x] Task 5 - Executer les tests LLM et scans anti-regression (AC: AC2, AC3, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/tests/unit/test_llm_canonical_perimeter.py`.
  - `backend/app/ops/llm/db_cleanup_validator.py`.
  - `backend/tests/integration/test_llm_db_cleanup_registry.py`.
- Do not recreate:
  - Un second registre LLM cleanup.
  - Un second rendu de structure LLM concurrent.
  - Des copies manuelles de registres prompt/governance.
- Shared abstraction allowed only if:
  - Elle parse la classification LLM pour les tests et reste compatible avec `backend/docs/ownership-index.md`.

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

- doc `backend/docs/llm-*` revendiquant `source-of-truth`, `canonical` ou `canonique` sans garde
- suppression de la comparaison generee de `llm-model-structure.md`
- contournement de `LlmDbCleanupValidator`

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

- `backend/docs/llm-model-structure.md`
- `backend/docs/llm-db-cleanup-registry.json`
- `backend/docs/llm-db-governance.md`
- `backend/docs/llm-runtime-source-of-truth.md`
- `backend/docs/llm-canonical-consumption-rebuild.md`
- `backend/tests/unit/test_llm_canonical_perimeter.py`
- `backend/tests/integration/test_llm_db_cleanup_registry.py`
- `backend/app/ops/llm/db_cleanup_validator.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `_condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/llm-doc-governance.md` - classification persistante.
- `backend/docs/llm-runtime-source-of-truth.md` - statut canonique ou historique explicite.
- `backend/docs/llm-canonical-consumption-rebuild.md` - statut canonique ou historique explicite.
- `backend/docs/ownership-index.md` - classification si present.
- `backend/app/tests/unit/test_llm_docs_governance.py` - nouvelle garde.

Likely tests:

- `backend/app/tests/unit/test_llm_docs_governance.py` - garde nouvelle.
- `backend/tests/unit/test_llm_canonical_perimeter.py` - garde doc generee.
- `backend/tests/integration/test_llm_db_cleanup_registry.py` - garde registre executable.
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - non-regression prompt governance.

Files not expected to change:

- `backend/app/domain/llm/runtime` - aucun changement runtime.
- `backend/app/infra/providers/llm` - aucun changement provider.
- `backend/alembic` - aucune migration DB.
- `frontend/src` - aucun impact frontend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_llm_docs_governance.py
pytest -q tests/unit/test_llm_canonical_perimeter.py
pytest -q tests/integration/test_llm_db_cleanup_registry.py
pytest -q tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py
rg -n "source-of-truth|Source de verite|canonical|canonique" docs/llm* app tests
Pop-Location
```

Then from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/00-story.md
```

## 22. Regression Risks

- Risk: une doc LLM semble source de verite sans garde.
  - Guardrail: AC4 et scan cible des termes normatifs.
- Risk: la consolidation casse le registre cleanup executable.
  - Guardrail: AC3 et tests integration existants.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Keep new or significantly modified Python files documented with a French file-level comment and French docstrings for public or non-trivial functions/classes.

## 24. References

- `_condamad/audits/backend-docs/2026-05-04-1826/03-story-candidates.md#SC-003` - candidate source.
- `_condamad/audits/backend-docs/2026-05-04-1826/02-finding-register.md#F-003` - finding source.
- `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
