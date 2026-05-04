# Story CS-024 repositionner-notes-llm-non-canoniques: Repositionner les notes LLM non canoniques hors backend/docs

Status: done

## 1. Objective

Deplacer les notes LLM humaines non canoniques encore stockees sous
`backend/docs/` vers `docs/llm/`. Les artefacts LLM generes ou executables
restent sous `backend/docs/`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-docs/2026-05-04-2028/03-story-candidates.md#SC-001`
- Reason for change: le finding `F-001` signale que trois notes LLM humaines
  non canoniques restent sous `backend/docs/`.

## 3. Domain Boundary

- Domain: `backend/docs`
- In scope:
  - Deplacer `backend/docs/llm-db-governance.md`,
    `backend/docs/llm-runtime-source-of-truth.md` et
    `backend/docs/llm-canonical-consumption-rebuild.md` vers `docs/llm/`.
  - Mettre a jour `backend/docs/ownership-index.md`.
  - Mettre a jour `_condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/llm-doc-governance.md`.
  - Mettre a jour `backend/docs/llm-db-cleanup-registry.json`.
  - Adapter les gardes LLM/docs existantes.
- Out of scope:
  - Deplacer `backend/docs/llm-model-structure.md`.
  - Deplacer `backend/docs/llm-db-cleanup-registry.json`.
  - Modifier le runtime LLM, les migrations, prompts, assemblies ou providers.
- Explicit non-goals:
  - Ne pas affaiblir `RG-040`.
  - Ne pas affaiblir `RG-042`.
  - Ne pas creer de copie concurrente aux anciens chemins.

## 4. Operation Contract

- Operation type: move
- Primary archetype: module-move
- Archetype reason: deplacement documentaire avec mise a jour des registres et gardes.
- Behavior change allowed: no
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: `docs/llm/` est refuse comme emplacement final.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le registre JSON conserve un champ `governance_doc` valide. |
| Baseline Snapshot | yes | Les chemins avant/apres doivent prouver le deplacement. |
| Ownership Routing | yes | Les documents humains et artefacts backend ont des owners distincts. |
| Allowlist Exception | yes | Les artefacts LLM autorises sous `backend/docs/` restent exacts. |
| Contract Shape | yes | La cle JSON `governance_doc` est preservee. |
| Batch Migration | yes | Trois notes sont migrees ensemble. |
| Reintroduction Guard | yes | Les anciens chemins ne doivent pas revenir. |
| Persistent Evidence | yes | Les inventaires restent auditables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard `backend/app/tests/unit/test_llm_docs_governance.py`
  - AST/filesystem guard `backend/app/tests/unit/test_backend_docs_ownership.py`
  - Loaded config/JSON registry guard `backend/tests/integration/test_llm_db_cleanup_registry.py`
- Secondary evidence:
  - `rg -n "llm-db-governance|llm-runtime-source-of-truth|llm-canonical-consumption-rebuild" backend docs _condamad/stories`
- Static scans alone are not sufficient because le registre JSON est charge par
  `LlmDbCleanupValidator` et les inventaires sont gardes par tests AST/fichiers.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-024-repositionner-notes-llm-non-canoniques/llm-doc-paths-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-024-repositionner-notes-llm-non-canoniques/llm-doc-paths-after.md`
- Expected invariant: les trois notes existent sous `docs/llm/`, les anciens
  chemins sous `backend/docs/` sont absents, et les artefacts LLM executables
  restent sous `backend/docs/`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Note LLM humaine non canonique | `docs/llm/` | `backend/docs/` |
| Registre LLM executable | `backend/docs/llm-db-cleanup-registry.json` | prose racine non lue |
| Document LLM genere | `backend/docs/llm-model-structure.md` | copie manuelle sous `docs/llm/` |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/docs/llm-model-structure.md` | generated LLM structure doc | Document genere. | Permanent tant que le generateur le produit. |
| `backend/docs/llm-db-cleanup-registry.json` | executable cleanup registry | Registre lu par `LlmDbCleanupValidator`. | Permanent tant que le validateur lit ce chemin. |

## 4f. Contract Shape

Contract type:
- JSON registry field and markdown governance rows.
Fields:
- `governance_doc`, `File`, `Status`, `Runtime source`, `Guard`.
Required fields:
- All existing registry/governance columns remain present.
Optional fields:
- none.
Status codes:
- none; no HTTP surface is affected.
Serialization names:
- preserve JSON key `governance_doc`.
Frontend type impact:
- none.
Generated contract impact:
- none.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| B1 | `backend/docs/llm-db-governance.md` | `docs/llm/llm-db-governance.md` | registry, docs, index | LLM docs + registry tests | old file absent | `docs/llm/` rejected |
| B2 | `backend/docs/llm-runtime-source-of-truth.md` | `docs/llm/llm-runtime-source-of-truth.md` | governance, index | LLM docs test | old file absent | deletion chosen |
| B3 | `backend/docs/llm-canonical-consumption-rebuild.md` | `docs/llm/llm-canonical-consumption-rebuild.md` | governance, index | LLM docs test | old absent | deletion chosen |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Inventaire avant | `_condamad/stories/CS-024-repositionner-notes-llm-non-canoniques/llm-doc-paths-before.md` | Capturer chemins et references avant. |
| Inventaire apres | `_condamad/stories/CS-024-repositionner-notes-llm-non-canoniques/llm-doc-paths-after.md` | Prouver chemins finaux et absence de doublons. |

## 4i. Reintroduction Guard

- Guard target: retour des trois anciens chemins sous `backend/docs/`.
- Guard evidence: architecture guard `pytest -q app/tests/unit/test_llm_docs_governance.py app/tests/unit/test_backend_docs_ownership.py`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-docs/2026-05-04-2028/00-audit-report.md` demande le deplacement.
- Evidence 2: `backend/docs/ownership-index.md` classe les trois notes sous `backend/docs/`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les trois notes existent sous `docs/llm/`.
- Les anciens chemins sous `backend/docs/` n'existent plus.
- Les artefacts `backend/docs/llm-model-structure.md` et
  `backend/docs/llm-db-cleanup-registry.json` restent sous `backend/docs/`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les trois notes LLM sont sous `docs/llm/`. | `pytest -q app/tests/unit/test_llm_docs_governance.py` et scan cible des trois noms. |
| AC2 | `backend/docs/ownership-index.md` classe les fichiers `backend/docs/**`. | `pytest -q app/tests/unit/test_backend_docs_ownership.py`. |
| AC3 | La gouvernance LLM reference les nouveaux chemins non canoniques. | `pytest -q app/tests/unit/test_llm_docs_governance.py`. |
| AC4 | Le registre DB LLM pointe vers le nouveau chemin de gouvernance. | Evidence profile: `json_contract_shape`; `pytest -q tests/integration/test_llm_db_cleanup_registry.py`. |
| AC5 | Les artefacts LLM gardes restent sous `backend/docs/`. | Evidence profile: `reintroduction_guard`; `pytest -q tests/unit/test_llm_canonical_perimeter.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer l'inventaire avant des chemins et references LLM (AC: AC1).
- [x] Task 2 - Deplacer les trois notes LLM vers `docs/llm/` (AC: AC1).
- [x] Task 3 - Mettre a jour ownership backend docs et gouvernance LLM (AC: AC2, AC3).
- [x] Task 4 - Mettre a jour le registre DB LLM et ses tests (AC: AC4).
- [x] Task 5 - Capturer l'inventaire apres et executer les validations ciblees (AC: AC1, AC2, AC3, AC4, AC5).

## 9. Mandatory Reuse / DRY Constraints

- Reuse `backend/docs/ownership-index.md`.
- Reuse `_condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/llm-doc-governance.md`.
- Reuse les tests LLM/docs existants.

## 10. No Legacy / Forbidden Paths

- `backend/docs/llm-db-governance.md`
- `backend/docs/llm-runtime-source-of-truth.md`
- `backend/docs/llm-canonical-consumption-rebuild.md`
- `governance_doc` pointant vers `backend/docs/llm-db-governance.md`
- compatibility wrappers, legacy aliases, silent fallback behavior

## 18. Files to Inspect First

- `backend/docs/ownership-index.md`
- `backend/docs/llm-db-governance.md`
- `backend/docs/llm-runtime-source-of-truth.md`
- `backend/docs/llm-canonical-consumption-rebuild.md`
- `backend/docs/llm-db-cleanup-registry.json`
- `backend/app/tests/unit/test_backend_docs_ownership.py`
- `backend/app/tests/unit/test_llm_docs_governance.py`
- `backend/tests/integration/test_llm_db_cleanup_registry.py`

## 19. Expected Files to Modify

Likely files:

- `docs/llm/llm-db-governance.md`
- `docs/llm/llm-runtime-source-of-truth.md`
- `docs/llm/llm-canonical-consumption-rebuild.md`
- `backend/docs/ownership-index.md`
- `_condamad/stories/CS-022-uniformiser-gouvernance-docs-llm-source-truth/llm-doc-governance.md`
- `backend/docs/llm-db-cleanup-registry.json`

Likely tests:

- `backend/app/tests/unit/test_backend_docs_ownership.py`
- `backend/app/tests/unit/test_llm_docs_governance.py`
- `backend/tests/integration/test_llm_db_cleanup_registry.py`

Files not expected to change:

- `backend/app/domain/llm`
- `backend/migrations`
- `frontend/src`

## 20. Dependency Policy

- New dependencies: none.
- Justification: deplacement documentaire et tests existants uniquement; aucune
  dependance Python ou frontend n'est requise.

## 21. Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_backend_docs_ownership.py
pytest -q app/tests/unit/test_llm_docs_governance.py
pytest -q tests/unit/test_llm_canonical_perimeter.py
pytest -q tests/integration/test_llm_db_cleanup_registry.py
Pop-Location
rg -n "llm-db-governance|llm-runtime-source-of-truth|llm-canonical-consumption-rebuild" backend docs _condamad\stories
```

## 22. Regression Risks

- Risk: le registre DB LLM pointe vers un chemin inexistant.
- Risk: une copie legacy reste sous `backend/docs/`.
- Risk: les artefacts LLM executables sont deplaces par erreur.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.

## 24. References

- `_condamad/audits/backend-docs/2026-05-04-2028/03-story-candidates.md#SC-001`
- `_condamad/audits/backend-docs/2026-05-04-2028/00-audit-report.md`
- `_condamad/stories/regression-guardrails.md`
