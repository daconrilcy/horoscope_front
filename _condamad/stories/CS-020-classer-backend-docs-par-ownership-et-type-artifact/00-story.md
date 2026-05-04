# Story CS-020 classer-backend-docs-par-ownership-et-type-artifact: Classer backend docs par ownership et type d'artefact

Status: ready-to-dev

## 1. Objective

Ajouter un index local d'ownership pour `backend/docs/` qui classe chaque fichier existant par owner,
type d'artefact, statut canonique et garde attendue. La story doit rendre impossible l'ajout silencieux
d'un nouveau fichier non classe sous `backend/docs/`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-docs/2026-05-04-1826/03-story-candidates.md#SC-001`
- Reason for change: le finding `F-001` montre que `backend/docs/` melange docs, registre executable, specs et artefacts generes sans index local.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/docs`
- In scope:
  - Inventorier tous les fichiers sous `backend/docs/`.
  - Creer un index d'ownership local pour classifier chaque fichier.
  - Ajouter une garde de test qui echoue si un fichier `backend/docs/**` n'est pas classe.
  - Documenter le traitement des fichiers generes et registres executables.
- Out of scope:
  - Deplacer ou supprimer les fichiers existants.
  - Decider du statut canonique detaille des docs entitlement, LLM ou calibration traitees par `CS-021`, `CS-022` et `CS-023`.
  - Modifier les contrats API, schemas DB ou runtime applicatif.
- Explicit non-goals:
  - Ne pas affaiblir `RG-015`, `RG-021`, `RG-022` ni `RG-039`.
  - Ne pas creer un second registre concurrent pour les invariants CONDAMAD.
  - Ne pas ajouter de dossier de base sous `backend/`.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story ajoute une garde d'architecture documentaire et une classification deterministe sans deplacement de code applicatif.
- Behavior change allowed: no
- Behavior change constraints:
  - Aucun comportement runtime applicatif ne doit changer.
  - Seule la gouvernance documentaire et les tests associes changent.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le projet refuse d'avoir un index local dans `backend/docs/` ou exige un emplacement different.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde executable doit inspecter l'inventaire reel des fichiers. |
| Baseline Snapshot | yes | L'inventaire `backend/docs/**` doit etre capture avant/apres l'ajout de l'index. |
| Ownership Routing | yes | Chaque fichier doit etre route vers un owner et un type d'artefact. |
| Allowlist Exception | yes | Les fichiers toleres sous `backend/docs/` deviennent une allowlist exacte. |
| Contract Shape | no | Aucun API, DTO, OpenAPI ou type frontend n'est touche. |
| Batch Migration | no | La story classe l'etat courant sans migration multi-lot. |
| Reintroduction Guard | yes | La garde doit bloquer l'ajout non classe de fichiers. |
| Persistent Evidence | yes | L'index d'ownership est une preuve persistante. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard et filesystem inventory dans `backend/app/tests/unit/test_backend_docs_ownership.py`.
  - La garde compare l'inventaire `Path("docs").rglob("*")` aux lignes de l'index depuis la racine `backend`.
  - Commande cible: `pytest -q app/tests/unit/test_backend_docs_ownership.py`.
- Secondary evidence:
  - `rg --files backend/docs`
  - revue de `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md`
- Static scans alone are not sufficient for this story because:
  - Un scan manuel peut oublier un fichier; la garde doit echouer automatiquement pendant les tests.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-020-classer-backend-docs-par-ownership-et-type-artifact/backend-docs-inventory-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-020-classer-backend-docs-par-ownership-et-type-artifact/backend-docs-inventory-after.md`
- Expected invariant:
  - Tous les fichiers presents sous `backend/docs/**` sont classes dans `backend/docs/ownership-index.md`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Documentation backend toleree | `backend/docs/ownership-index.md` | fichier non classe sous `backend/docs/**` |
| Registre executable | owner applicatif declare dans l'index | doc prose sans garde |
| Documentation generee | producteur declare + test de generation | edition manuelle non gardee |
| Spec canonique | owner runtime declare + garde de parite | doc canonique sans source executable |
| Note historique | statut `historical` explicite | document ambigu presente comme source de verite |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/docs/ownership-index.md` | inventory row per file | Source locale de classification. | Permanent tant que `backend/docs/` existe. |
| `backend/docs/llm-db-cleanup-registry.json` | executable registry | Consomme par le validateur LLM. | Permanent, garde executable obligatoire. |

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
| Ownership index | `backend/docs/ownership-index.md` | Classer chaque fichier `backend/docs/**` avec owner, type, statut canonique et garde. |
| Inventaire avant | `backend-docs-inventory-before.md` | Capturer les fichiers presents avant implementation. |
| Inventaire apres | `backend-docs-inventory-after.md` | Prouver que l'index couvre l'inventaire final. |

## 4i. Reintroduction Guard

- Guard target:
  - Tout fichier sous `backend/docs/**` absent de `backend/docs/ownership-index.md`.
  - Toute classification sans type d'artefact autorise.
- Guard evidence:
  - Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_backend_docs_ownership.py`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - `E-002` inventorie sept fichiers sous `backend/docs/`.
- Evidence 2: `_condamad/audits/backend-docs/2026-05-04-1826/02-finding-register.md#F-001` - aucun index local ne classe les fichiers.
- Evidence 3: `docs/backend-structure-governance.md` - `backend/docs/` est tolere comme documentation technique backend, sans classification par fichier.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `backend/docs/ownership-index.md` existe avec une ligne exacte par fichier.
- Les types autorises sont explicites: `generated-doc`, `executable-registry`, `canonical-spec`, `human-runbook`, `historical-note`, `governance-doc`, `generated-artifact`.
- Un test cible bloque tout ajout non classe.
- Les fichiers LLM, entitlement et calibration sont classes sans resoudre les decisions de fond des stories suivantes.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-015` - les tests qualite/docs/ops doivent rester declares dans le registre d'ownership des tests backend si un nouveau test docs est ajoute.
  - `RG-021` - le registre LLM cleanup doit conserver sa gouvernance executable.
  - `RG-040` - invariant cree par cette story pour l'ownership de `backend/docs`.
- Non-applicable invariants:
  - `RG-003` - aucune route API ou OpenAPI n'est touchee.
  - `RG-039` - la frontiere scheduled tasks / scripts n'est pas modifiee.
- Required regression evidence:
  - Test d'ownership docs, inventaire `rg --files backend/docs`, test d'ownership qualite si le fichier de test docs est ajoute.
- Allowed differences:
  - Ajout de l'index et d'une garde de test uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Tous les fichiers `backend/docs/**` sont classes dans un index local. | Evidence profile: `ownership_inventory`; test `test_backend_docs_ownership.py`. |
| AC2 | Chaque ligne de l'index declare les champs obligatoires. | Evidence profile: `contract_shape_doc`; test `test_backend_docs_ownership.py`. |
| AC3 | Un type d'artefact inconnu est refuse. | Evidence profile: `allowlist_exact`; test `test_backend_docs_ownership.py`. |
| AC4 | Un nouveau fichier non classe sous `backend/docs/` fait echouer le test. | Evidence profile: `reintroduction_guard`; test `test_backend_docs_ownership.py`. |
| AC5 | Les guardrails applicables restent respectes. | Evidence profile: `regression_guardrails`; test `test_backend_quality_test_ownership.py` si requis. |

## 8. Implementation Tasks

- [x] Task 1 - Inventorier l'etat courant de `backend/docs` (AC: AC1)
- [x] Task 2 - Creer `backend/docs/ownership-index.md` avec les classifications exactes (AC: AC1, AC2, AC3)
- [x] Task 3 - Ajouter la garde `test_backend_docs_ownership.py` (AC: AC1, AC3, AC4)
- [x] Task 4 - Mettre a jour l'ownership des tests qualite si requis (AC: AC5)
- [x] Task 5 - Executer validation, lint et scans cibles (AC: AC1, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `docs/backend-structure-governance.md` pour la classification de haut niveau de `backend/docs`.
  - Les patterns de garde existants dans `backend/app/tests/unit/test_backend_quality_test_ownership.py`.
- Do not recreate:
  - Un second registre global de stories ou de guardrails.
  - Une classification differente dans plusieurs fichiers.
- Shared abstraction allowed only if:
  - Elle sert uniquement a parser l'index d'ownership et reste reutilisee par les tests docs suivants.

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

- fichier `backend/docs/**` absent de `backend/docs/ownership-index.md`
- type d'artefact libre non teste
- classification `misc`, `todo`, `unknown` ou `other`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Classification de `backend/docs` | `backend/docs/ownership-index.md` | classification implicite dans audit ou README global |
| Garde d'inventaire docs backend | `backend/app/tests/unit/test_backend_docs_ownership.py` | scan manuel non teste |

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
- `backend/docs/entitlements-canonical-platform.md`
- `backend/docs/calibration/percentile_report.json`
- `docs/backend-structure-governance.md`
- `backend/app/tests/unit/test_backend_quality_test_ownership.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/docs/ownership-index.md` - nouvel index local.
- `backend/app/tests/unit/test_backend_docs_ownership.py` - nouvelle garde d'inventaire.
- `backend/app/tests/unit/ops-quality-test-ownership.md` - a mettre a jour si le registre existe et couvre le nouveau test.

Likely tests:

- `backend/app/tests/unit/test_backend_docs_ownership.py` - couverture principale.
- `backend/app/tests/unit/test_backend_quality_test_ownership.py` - non-regression ownership tests qualite.

Files not expected to change:

- `backend/app/api` - aucun contrat HTTP.
- `backend/app/services` - aucun runtime applicatif.
- `frontend/src` - aucun impact frontend.
- `backend/pyproject.toml` - aucune dependance nouvelle.

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
pytest -q app/tests/unit/test_backend_docs_ownership.py
pytest -q app/tests/unit/test_backend_quality_test_ownership.py
rg --files docs
Pop-Location
```

Then from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-020-classer-backend-docs-par-ownership-et-type-artifact/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-020-classer-backend-docs-par-ownership-et-type-artifact/00-story.md
```

## 22. Regression Risks

- Risk: l'index devient declaratif mais non exhaustif.
  - Guardrail: test comparant l'inventaire disque a l'index.
- Risk: un fichier generated/executable est traite comme doc prose.
  - Guardrail: types finis et champ de garde attendue obligatoire.

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

- `_condamad/audits/backend-docs/2026-05-04-1826/03-story-candidates.md#SC-001` - candidate source.
- `_condamad/audits/backend-docs/2026-05-04-1826/02-finding-register.md#F-001` - finding source.
- `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
