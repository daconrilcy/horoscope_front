# Story CS-021 aligner-documentation-entitlement-canonique-runtime: Aligner la documentation entitlement canonique avec les contrats runtime

Status: ready-to-dev

## 1. Objective

Decider et appliquer le statut de `backend/docs/entitlements-canonical-platform.md`. Si le document reste
canonique, ajouter des gardes de parite avec les routes, schemas, modeles, services et controles d'acces
runtime. Sinon, le marquer comme preuve historique non canonique et faire pointer les contrats actifs vers
les sources executables.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-docs/2026-05-04-1826/03-story-candidates.md#SC-002`
- Reason for change: le finding `F-002` indique que le document entitlement revendique un statut canonique/securite sans garde directe contre la derive runtime.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/services/canonical_entitlement`
- In scope:
  - Classer `backend/docs/entitlements-canonical-platform.md` comme canonique garde ou historique non canonique.
  - Si canonique, tester la parite des endpoints ops/admin/public cites, des tables/models entitlement, des workflows review/alert et des claims de securite.
  - Si historique, modifier le document pour supprimer toute ambiguite de source de verite active.
  - Integrer la classification dans `backend/docs/ownership-index.md` si `CS-020` est deja livree; sinon documenter l'hypothese.
- Out of scope:
  - Changer les regles produit d'entitlement.
  - Ajouter de nouvelles routes entitlement.
  - Modifier les schemas DB ou migrations Alembic.
  - Refondre toute la documentation `backend/docs`.
- Explicit non-goals:
  - Ne pas affaiblir `RG-002`, `RG-003`, `RG-004`, `RG-005`, `RG-006` ou `RG-015`.
  - Ne pas creer de contrat entitlement duplique hors runtime et tests.
  - Ne pas transformer une doc historique en source canonique par simple renommage.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: runtime-contract-preservation
- Archetype reason: la story preserve ou retire explicitement un contrat documentaire en le comparant aux sources runtime observables.
- Behavior change allowed: no
- Behavior change constraints:
  - Les endpoints, schemas, modeles et controles runtime ne doivent pas changer pour satisfaire la doc.
  - Tout ecart doit corriger le statut de la doc ou bloquer sur decision utilisateur.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le document doit rester canonique mais contient une promesse de route, table ou controle d'acces absente du runtime.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La parite doit venir d'OpenAPI, modeles SQLAlchemy et tests runtime, pas du prose. |
| Baseline Snapshot | yes | Le statut avant/apres du document et des routes entitlement doit etre capture. |
| Ownership Routing | no | Aucun deplacement de responsabilite applicative n'est prevu. |
| Allowlist Exception | no | Aucune exception implicite n'est autorisee pour les claims canoniques. |
| Contract Shape | yes | Le document decrit endpoints, schemas, tables et controles qui sont des contrats. |
| Batch Migration | no | Pas de migration multi-consommateur; uniquement parite ou declassement. |
| Reintroduction Guard | no | Aucun ancien chemin n'est supprime ou converge. |
| Persistent Evidence | yes | Les snapshots/parity reports doivent etre persistants. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `app.openapi()` pour les endpoints entitlement documentes.
  - SQLAlchemy metadata pour les tables/models entitlement mutation/audit/alert.
  - Tests d'integration ops/admin/public entitlement.
- Secondary evidence:
  - `rg -n "entitlements-canonical-platform|canonical_entitlement|entitlement_mutation" backend/app backend/tests`
  - sections du document `backend/docs/entitlements-canonical-platform.md`.
- Static scans alone are not sufficient for this story because:
  - Le document revendique des endpoints et controles effectifs; seule une source runtime peut prouver leur presence et forme.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-021-aligner-documentation-entitlement-canonique-runtime/entitlement-doc-runtime-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-021-aligner-documentation-entitlement-canonique-runtime/entitlement-doc-runtime-after.md`
- Expected invariant:
  - Les contrats runtime entitlement restent inchanges; seul le statut documentaire ou les gardes de parite changent.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - Documentation/runtime parity for entitlement HTTP routes, DB models and security claims.
- Fields:
  - route path: chemin OpenAPI documente.
  - method: methode HTTP attendue.
  - model/table: modele SQLAlchemy ou table documentee.
  - access control: dependance ou test prouvant le controle.
- Required fields:
  - route path
  - method
  - model/table when a DB table is documented
  - canonical status
- Optional fields:
  - historical note
  - migration/story reference
- Status codes:
  - Les status codes ne changent pas; les tests existants restent source runtime.
- Serialization names:
  - Noms OpenAPI et noms SQLAlchemy existants uniquement.
- Frontend type impact:
  - Aucun impact frontend attendu.
- Generated contract impact:
  - OpenAPI snapshot filtre entitlement requis si le document reste canonique.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Inventaire avant doc/runtime | `entitlement-doc-runtime-before.md` | Capturer claims documentaires et surfaces runtime avant changement. |
| Inventaire apres doc/runtime | `entitlement-doc-runtime-after.md` | Prouver le statut final et les gardes ajoutees. |
| OpenAPI filtre entitlement | `entitlement-openapi-snapshot.json` | Prouver les endpoints si le document reste canonique. |

## 4i. Reintroduction Guard

- Reintroduction guard: not applicable
- Reason: no removed, forbidden, or converged-away legacy surface can be reintroduced by this story.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - `E-003` signale `entitlements-canonical-platform.md` comme document volumineux.
- Evidence 2: `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - `E-007` ne trouve pas de reference directe au document dans les tests ou validateurs actifs.
- Evidence 3: `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py` - routeur ops entitlement cite comme surface a verifier par l'audit.
- Evidence 4: `backend/app/infra/db/models/canonical_entitlement_mutation_audit.py` - modele DB entitlement mutation a verifier si la doc reste canonique.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Le document entitlement a un statut explicite: `canonical-guarded` ou `historical-note`.
- Si `canonical-guarded`, une garde de parite echoue quand un endpoint/table/claim critique documente disparait du runtime.
- Si `historical-note`, le document ne revendique plus etre source de verite active et pointe vers OpenAPI/tests/modeles.
- Les preuves avant/apres restent dans le dossier de story.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-002` - les routeurs API v1 doivent rester organises sans logique metier opportuniste.
  - `RG-003` - les routes doivent rester montees via le mecanisme canonique et verifiees par OpenAPI/runtime.
  - `RG-004` - les erreurs HTTP ne doivent pas etre reconstruites localement pour satisfaire une doc.
  - `RG-005` - la couche API ne doit pas redevenir proprietaire de logique metier entitlement.
  - `RG-006` - les couches non API ne doivent pas importer `app.api`.
  - `RG-041` - invariant cree par cette story pour le statut doc/runtime entitlement.
- Non-applicable invariants:
  - `RG-021` - le registre LLM cleanup n'est pas touche.
  - `RG-039` - scheduled tasks/scripts non touches.
- Required regression evidence:
  - OpenAPI filtre, tests entitlement cibles, scans anti-import API inverse.
- Allowed differences:
  - Changement du statut/documentation; aucun changement runtime attendu.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le statut entitlement doc est explicite. | Evidence profile: `persistent_evidence`; `rg -n "canonical-guarded|historical-note"`. |
| AC2 | Endpoints verifies depuis `app.openapi()`. | Evidence profile: `runtime`; `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py`. |
| AC3 | Les tables entitlement documentees sont verifiees depuis SQLAlchemy metadata. | Evidence profile: `db_schema_runtime`; test `test_entitlement_docs_runtime_parity.py`. |
| AC4 | Les claims review/alert/security ont un statut garde ou historique. | Evidence profile: `contract_parity`; test `test_entitlement_docs_runtime_parity.py`. |
| AC5 | Les tests runtime entitlement restent passants. | Evidence profile: `runtime`; `pytest -q app/tests/integration/test_ops_entitlement_mutation_audits_api.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer claims documentaires et runtime actuel (AC: AC1, AC5)
- [x] Task 2 - Decider le statut `canonical-guarded` ou `historical-note` avec preuve (AC: AC1)
- [x] Task 3 - Ajouter les gardes OpenAPI/modeles si canonique (AC: AC2, AC3)
- [x] Task 4 - Traiter explicitement review/alert/security (AC: AC4)
- [x] Task 5 - Mettre a jour l'index `backend/docs/ownership-index.md` si disponible et executer validations (AC: AC1, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Les tests entitlement existants sous `backend/app/tests/unit` et `backend/app/tests/integration`.
  - `app.openapi()` plutot qu'un parseur ad hoc de routes.
  - Les modeles SQLAlchemy existants.
- Do not recreate:
  - Un nouveau catalogue endpoint entitlement concurrent.
  - Une copie manuelle de schema DB dans le test.
- Shared abstraction allowed only if:
  - Elle sert a extraire un inventaire reusable de claims documentaires et reste ciblee au document entitlement.

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

- doc revendiquant `canonical` sans garde ou statut historique explicite
- import `app.api` depuis `backend/app/services` ou `backend/app/domain`
- nouveau endpoint entitlement cree uniquement pour satisfaire une doc existante

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

- Generated contract check: applicable through filtered OpenAPI snapshot.
- Required generated-contract evidence:
  - OpenAPI path presence for documented entitlement endpoints when canonical.
  - Generated client/schema absence is not required because no frontend generated client is changed.
  - Route manifest absence is not applicable unless the repo has a generated route manifest.

## 18. Files to Inspect First

- `backend/docs/entitlements-canonical-platform.md`
- `backend/app/api/v1/routers/ops/entitlement_mutation_audits.py`
- `backend/app/api/v1/routers/admin/entitlements.py`
- `backend/app/api/v1/routers/public/entitlements.py`
- `backend/app/services/canonical_entitlement`
- `backend/app/services/api_contracts/ops/entitlement_mutation_audits.py`
- `backend/app/infra/db/models/canonical_entitlement_mutation_audit.py`
- `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/docs/entitlements-canonical-platform.md` - statut canonique ou historique explicite.
- `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py` - garde doc/runtime si canonique.
- `backend/docs/ownership-index.md` - classification si present.
- `_condamad/stories/CS-021-aligner-documentation-entitlement-canonique-runtime/entitlement-doc-runtime-before.md` - snapshot avant.
- `_condamad/stories/CS-021-aligner-documentation-entitlement-canonique-runtime/entitlement-doc-runtime-after.md` - snapshot apres.
- `_condamad/stories/CS-021-aligner-documentation-entitlement-canonique-runtime/entitlement-openapi-snapshot.json` - snapshot OpenAPI filtre si canonique.

Likely tests:

- `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py` - nouvelle garde.
- `backend/app/tests/integration/test_ops_entitlement_mutation_audits_api.py` - non-regression endpoint ops.
- `backend/app/tests/integration/test_entitlements_me_contract.py` - non-regression contrat public.

Files not expected to change:

- `backend/alembic` - aucun changement schema DB.
- `frontend/src` - aucun impact attendu.
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
pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py
pytest -q app/tests/integration/test_ops_entitlement_mutation_audits_api.py
pytest -q app/tests/integration/test_entitlements_me_contract.py
rg -n "from app\.api|import app\.api" app/services app/domain app/infra app/core -g "*.py"
Pop-Location
```

Then from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-021-aligner-documentation-entitlement-canonique-runtime/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-021-aligner-documentation-entitlement-canonique-runtime/00-story.md
```

## 22. Regression Risks

- Risk: la doc reste canonique sans garde exhaustive.
  - Guardrail: AC2, AC3 et AC4 imposent parite ou declassement.
- Risk: un test encode une copie manuelle fragile du runtime.
  - Guardrail: `app.openapi()` et metadata SQLAlchemy comme sources primaires.

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

- `_condamad/audits/backend-docs/2026-05-04-1826/03-story-candidates.md#SC-002` - candidate source.
- `_condamad/audits/backend-docs/2026-05-04-1826/02-finding-register.md#F-002` - finding source.
- `_condamad/audits/backend-docs/2026-05-04-1826/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
