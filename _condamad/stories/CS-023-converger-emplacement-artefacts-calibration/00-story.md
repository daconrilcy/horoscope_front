# Story CS-023 converger-emplacement-artefacts-calibration: Converger l'emplacement des artefacts de calibration

Status: ready-to-dev

## 1. Objective

Choisir et appliquer un emplacement canonique unique pour les artefacts generes de calibration.
Supprimer ou migrer `backend/docs/calibration/percentile_report.json` sans laisser deux chemins actifs.
Ajouter une garde contre le retour d'une sortie generee sous `backend/docs/calibration` si `docs/calibration`
reste l'owner canonique.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-docs/2026-05-04-1826/03-story-candidates.md#SC-004`
- Reason for change: le finding `F-004` montre une surface legacy probable:
  le code courant produit sous `docs/calibration`, tandis qu'un rapport reste sous `backend/docs/calibration`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/services/calibration`
- In scope:
  - Inventorier les producteurs et consommateurs d'artefacts calibration.
  - Decider le chemin canonique entre `docs/calibration`, `backend/artifacts` ou un autre chemin approuve.
  - Supprimer ou migrer `backend/docs/calibration/percentile_report.json` selon classification.
  - Mettre a jour producteurs/docs/tests coheremment.
  - Ajouter une garde anti split-output-path.
- Out of scope:
  - Changer l'algorithme de calcul des percentiles.
  - Changer le format metier du rapport sauf necessite documentee par la migration.
  - Modifier les contrats API ou frontend.
  - Deplacer d'autres docs hors calibration.
- Explicit non-goals:
  - Ne pas affaiblir `RG-010`, `RG-011`, `RG-013`, `RG-015` ou `RG-039`.
  - Ne pas conserver `backend/docs/calibration` comme alias si un autre chemin devient canonique.
  - Ne pas ajouter un nouveau dossier de base sous `backend/` sans accord explicite.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: dead-code-removal
- Archetype reason: la story supprime ou migre un artefact genere stale apres audit de consommation.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le contenu fonctionnel des rapports et grilles doit rester equivalent.
  - Le chemin de sortie peut changer uniquement vers le chemin canonique documente.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: le chemin canonique ne peut pas etre decide ou si l'artefact backend/docs est externe-actif.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les producteurs de fichiers et tests doivent prouver le chemin effectif. |
| Baseline Snapshot | yes | Les chemins et consommateurs d'artefacts doivent etre captures avant/apres suppression. |
| Ownership Routing | no | Le contrat principal est une politique d'artefacts, sans deplacement de responsabilite applicative. |
| Allowlist Exception | no | Aucune exception durable n'est autorisee pour conserver deux chemins actifs. |
| Contract Shape | no | Aucun API, DTO, OpenAPI ou type frontend n'est touche. |
| Batch Migration | no | Un seul artefact legacy connu est traite. |
| Reintroduction Guard | yes | La garde doit bloquer les chemins de sortie concurrents. |
| Persistent Evidence | yes | L'audit de chemin et la decision canonique doivent rester persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard dans `backend/app/tests/unit/test_calibration_artifact_locations.py`.
  - Tests des producteurs `compute_calibration_percentiles.py` et `generate_review_grid.py`.
  - Verification filesystem des chemins produits pendant les tests.
- Secondary evidence:
  - `rg -n "docs/calibration|backend/docs/calibration|percentile_report|review-grid" backend/app backend/tests backend/scripts scripts docs`
  - `rg --files backend/docs/calibration docs/calibration`
- Static scans alone are not sufficient for this story because:
  - Les chemins peuvent etre construits dynamiquement; les tests doivent prouver l'ecriture effective.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-023-converger-emplacement-artefacts-calibration/calibration-artifacts-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-023-converger-emplacement-artefacts-calibration/calibration-artifacts-after.md`
- Expected invariant:
  - Un seul emplacement canonique reste actif pour les artefacts generes calibration.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit chemins calibration | `calibration-artifact-location-audit.md` | Classer producteurs, consommateurs et chemin canonique. |
| Inventaire avant | `calibration-artifacts-before.md` | Capturer les chemins et consommateurs avant suppression. |
| Inventaire apres | `calibration-artifacts-after.md` | Prouver l'emplacement canonique final. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- filesystem inventory of generated calibration artifact paths
- forbidden symbols or states

- Guard target:
  - `backend/docs/calibration` si le chemin canonique final est `docs/calibration` ou un autre dossier.
  - Toute ecriture de rapport calibration vers un chemin non canonique.
- Guard evidence:
  - Architecture guard required against reintroduction of split calibration artifact paths.
  - Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_calibration_artifact_locations.py`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - `E-009` indique que les producteurs courants ciblent `docs/calibration`.
- Evidence 2: `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - `E-002` inventorie `backend/docs/calibration/percentile_report.json`.
- Evidence 3: `backend/app/scheduled_tasks/compute_calibration_percentiles.py` - producteur de rapport percentile a verifier.
- Evidence 4: `backend/app/services/calibration/generate_review_grid.py` - producteur de grille de revue a verifier.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Un seul chemin canonique existe pour les artefacts generes calibration.
- `backend/docs/calibration/percentile_report.json` est supprime ou migre selon l'audit persistant.
- Les producteurs et docs pointent vers le chemin canonique.
- Une garde echoue si un nouveau chemin concurrent de sortie apparait.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-010` - les tests ajoutes doivent rester sous les racines collectees.
  - `RG-011` - les tests ne doivent pas importer directement `SessionLocal` ou `engine`.
  - `RG-013` - pas d'import de helpers depuis modules `test_*.py`.
  - `RG-015` - les tests docs/scripts/ops/calibration ajoutes par cette story doivent etre inventories.
  - `RG-039` - la frontiere scheduled tasks/scripts ne doit pas etre contournee.
  - `RG-043` - invariant cree par cette story pour le chemin canonique des artefacts calibration.
- Non-applicable invariants:
  - `RG-003` - aucune route API n'est touchee.
  - `RG-021` - registre LLM non touche.
- Required regression evidence:
  - Audit persistant, tests calibration cibles, scans zero-hit du chemin non canonique.
- Allowed differences:
  - Deplacement ou suppression de l'artefact stale; aucun changement d'algorithme de calibration.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le chemin canonique des artefacts calibration est documente. | Evidence profile: `persistent_evidence`; `rg -n "canonical path" calibration-artifact-location-audit.md`. |
| AC2 | Les producteurs ecrivent vers le chemin canonique. | Evidence profile: `runtime_source_of_truth`; `pytest -q app/tests/unit/test_calibration_artifact_locations.py`. |
| AC3 | L'artefact backend/docs est supprime ou migre. | Evidence profile: `reintroduction_guard`; `rg --files backend/docs/calibration docs/calibration`. |
| AC4 | Une garde bloque la reintroduction de chemins split. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_calibration_artifact_locations.py`. |
| AC5 | Les tests calibration existants restent passants. | Evidence profile: `targeted_regression`; `pytest -q app/tests/unit/test_calibration_job.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Auditer producteurs, consommateurs et artefacts existants (AC: AC1)
- [x] Task 2 - Choisir le chemin canonique ou bloquer sur decision utilisateur (AC: AC1)
- [x] Task 3 - Supprimer ou migrer `backend/docs/calibration/percentile_report.json` (AC: AC3)
- [x] Task 4 - Mettre a jour producteurs/docs/tests vers le chemin canonique (AC: AC2, AC5)
- [x] Task 5 - Ajouter la garde anti split-output-path et executer validations (AC: AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/scheduled_tasks/compute_calibration_percentiles.py` comme producteur existant.
  - `backend/app/services/calibration/generate_review_grid.py` comme producteur existant.
  - Tests calibration existants sous `backend/app/tests/unit`.
- Do not recreate:
  - Un second generateur de rapports percentile.
  - Une seconde constante de chemin concurrente.
  - Un alias `backend/docs/calibration` vers le chemin canonique.
- Shared abstraction allowed only if:
  - Elle centralise le chemin canonique et remplace des constantes dupliquees.

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

- `backend/docs/calibration` comme sortie active si `docs/calibration` est canonique
- deux constantes actives pour la destination de rapport percentile
- copie simultanee du meme `percentile_report.json` dans deux dossiers suivis

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| backend/docs report | generated artifact | needs-user-decision until scanned | unknown | audit path | keep, replace-consumer, or delete | audit | stale reference |

Audit output path when applicable:

- `_condamad/stories/CS-023-converger-emplacement-artefacts-calibration/calibration-artifact-location-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Calibration percentile report | Path decided in `calibration-artifact-location-audit.md` | `backend/docs/calibration` unless explicitly selected |
| Calibration review grid | Path decided in `calibration-artifact-location-audit.md` | duplicate generated output paths |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If `backend/docs/calibration/percentile_report.json` is classified as `external-active`, it must not be deleted.
The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `backend/docs/calibration/percentile_report.json`
- `docs/calibration/percentile_report.json`
- `docs/calibration/review-grid-template.md`
- `backend/app/scheduled_tasks/compute_calibration_percentiles.py`
- `backend/app/services/calibration/generate_review_grid.py`
- `backend/app/tests/unit/test_calibration_job.py`
- `backend/app/tests/unit/test_calibration_runtime.py`
- `backend/app/tests/unit/test_v3_calibration.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/docs/calibration/percentile_report.json` - supprimer ou migrer selon audit.
- `backend/app/scheduled_tasks/compute_calibration_percentiles.py` - verifier ou corriger le chemin canonique.
- `backend/app/services/calibration/generate_review_grid.py` - verifier ou corriger le chemin canonique.
- `backend/app/tests/unit/test_calibration_artifact_locations.py` - nouvelle garde.
- `_condamad/stories/CS-023-converger-emplacement-artefacts-calibration/calibration-artifact-location-audit.md` - preuve persistante.
- `backend/docs/ownership-index.md` - classification si present.

Likely tests:

- `backend/app/tests/unit/test_calibration_artifact_locations.py` - garde nouvelle.
- `backend/app/tests/unit/test_calibration_job.py` - producteur percentile.
- `backend/app/tests/unit/test_calibration_runtime.py` - runtime calibration.
- `backend/app/tests/unit/test_v3_calibration.py` - non-regression calibration.

Files not expected to change:

- `backend/app/api` - aucun contrat API.
- `backend/alembic` - aucune migration DB.
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
pytest -q app/tests/unit/test_calibration_artifact_locations.py
pytest -q app/tests/unit/test_calibration_job.py app/tests/unit/test_calibration_runtime.py app/tests/unit/test_v3_calibration.py
rg -n "backend/docs/calibration|docs/calibration|percentile_report|review-grid" app tests scripts ../docs
rg --files docs/calibration
rg --files docs
Pop-Location
```

Then from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-023-converger-emplacement-artefacts-calibration/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-023-converger-emplacement-artefacts-calibration/00-story.md
```

## 22. Regression Risks

- Risk: un producteur continue d'ecrire vers l'ancien dossier.
  - Guardrail: AC2 et garde filesystem.
- Risk: l'artefact stale est supprime alors qu'il est externe-actif.
  - Guardrail: audit de consommation et external usage blocker.
- Risk: la convergence cree une constante de chemin dupliquee.
  - Guardrail: DRY constraint et scan des chemins.

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

- `_condamad/audits/backend-docs/2026-05-04-1826/03-story-candidates.md#SC-004` - candidate source.
- `_condamad/audits/backend-docs/2026-05-04-1826/02-finding-register.md#F-004` - finding source.
- `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
