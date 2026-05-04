# Story CS-025 repositionner-note-historique-entitlement: Repositionner la note historique entitlement hors backend/docs

Status: done

## 1. Objective

Conserver la note historique entitlement en la deplacant vers
`docs/architecture/entitlements-canonical-platform.md`. Le statut
`historical-note` reste preserve.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/backend-docs/2026-05-04-2028/03-story-candidates.md#SC-002`
- Reason for change: le finding `F-002` indique que la note entitlement est
  historique mais reste sous `backend/docs/` avec un nom d'apparence canonique.

## 3. Domain Boundary

- Domain: `backend/docs`
- In scope:
  - Deplacer `backend/docs/entitlements-canonical-platform.md` vers
    `docs/architecture/entitlements-canonical-platform.md`.
  - Preserver le header `Document status: historical-note`.
  - Mettre a jour `backend/docs/ownership-index.md`.
  - Adapter `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py`.
  - Capturer une preuve avant/apres du statut et des references.
- Out of scope:
  - Supprimer le document historique.
  - Recrire le modele entitlement runtime.
  - Modifier les endpoints, tables, claims securite ou OpenAPI entitlement.
- Explicit non-goals:
  - Ne pas affaiblir `RG-040`.
  - Ne pas affaiblir `RG-041`.
  - Ne pas introduire une copie legacy sous `backend/docs/`.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: suppression de l'ancien chemin documentaire apres
  conservation du contenu historique sous `docs/architecture/`.
- Behavior change allowed: no
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: l'implementation veut supprimer le contenu
  historique plutot que l'ancien chemin seulement.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde entitlement continue a verifier OpenAPI/tables/statut. |
| Baseline Snapshot | yes | Le chemin et le statut doivent etre prouves avant/apres. |
| Ownership Routing | yes | La note sort de `backend/docs`. |
| Allowlist Exception | yes | L'exception conservee vit sous `docs/architecture/`. |
| Contract Shape | no | Aucun contrat API n'est modifie. |
| Batch Migration | no | Reason: un seul document est deplace. |
| Reintroduction Guard | yes | Le retour sous `backend/docs` doit echouer. |
| Persistent Evidence | yes | Le deplacement reste auditable. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py`
  - `backend/app/tests/unit/test_backend_docs_ownership.py`
- Secondary evidence:
  - `rg -n "entitlements-canonical-platform|Document status: historical-note" backend docs _condamad`
- Static scans alone are not sufficient because la garde lit `app.openapi()`,
  `Base.metadata` et le fichier conserve pour prouver la parite runtime/statut.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-025-repositionner-note-historique-entitlement/entitlement-doc-path-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-025-repositionner-note-historique-entitlement/entitlement-doc-path-after.md`
- Expected invariant: le document existe sous `docs/architecture/`, conserve
  `Document status: historical-note`, et l'ancien chemin sous `backend/docs/`
  est absent.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Note historique architecture entitlement | `docs/architecture/` | `backend/docs/` |
| Runtime entitlement | services, API, models et tests existants | doc historique comme source de verite |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `docs/architecture/entitlements-canonical-platform.md` | `historical-note` | Note historique hors `backend/docs`. | Permanent. |

## 4f. Contract Shape

- Contract shape: not applicable.
- Reason: no API, DTO, schema, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable.
- Reason: a single markdown file is moved; no multi-batch migration is required.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Inventaire avant | `_condamad/stories/CS-025-repositionner-note-historique-entitlement/entitlement-doc-path-before.md` | Capturer chemin initial, statut et references. |
| Inventaire apres | `_condamad/stories/CS-025-repositionner-note-historique-entitlement/entitlement-doc-path-after.md` | Prouver chemin final et absence d'ancien fichier. |

## 4i. Reintroduction Guard

- Guard target: retour de `backend/docs/entitlements-canonical-platform.md`.
- Guard evidence: architecture guard against reintroduced forbidden symbols via
  `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py app/tests/unit/test_backend_docs_ownership.py`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/backend-docs/2026-05-04-2028/00-audit-report.md` recommande `docs/architecture/` si la note est retenue.
- Evidence 2: `backend/docs/ownership-index.md` classe le document sous `backend/docs/`.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `docs/architecture/entitlements-canonical-platform.md` contient la note.
- `backend/docs/entitlements-canonical-platform.md` n'existe plus.
- La garde entitlement valide le chemin final et l'absence de reintroduction.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La note historique cible `docs/architecture/`. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py`. |
| AC2 | Aucun ancien fichier entitlement canonique ne reste sous `backend/docs/`. | `pytest -q app/tests/unit/test_backend_docs_ownership.py`. |
| AC3 | `backend/docs/ownership-index.md` couvre les fichiers `backend/docs/**`. | `pytest -q app/tests/unit/test_backend_docs_ownership.py`. |
| AC4 | Les controles entitlement runtime restent actifs. | Evidence profile: `runtime_openapi_contract`; `pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py`. |
| AC5 | Supprimer le contenu conserve exige une decision utilisateur. | `rg -n "docs/architecture/entitlements-canonical-platform.md" docs`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le baseline du chemin, du statut et des references (AC: AC1, AC5).
- [x] Task 2 - Deplacer la note historique vers `docs/architecture/` (AC: AC1, AC2).
- [x] Task 3 - Mettre a jour `backend/docs/ownership-index.md` (AC: AC2, AC3).
- [x] Task 4 - Adapter la garde entitlement (AC: AC1, AC4).
- [x] Task 5 - Capturer l'inventaire apres et executer les validations ciblees (AC: AC1, AC2, AC3, AC4, AC5).

## 9. Mandatory Reuse / DRY Constraints

- Reuse `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py`.
- Reuse `backend/docs/ownership-index.md`.
- Reuse `docs/architecture/` comme owner racine existant.

## 10. No Legacy / Forbidden Paths

- `backend/docs/entitlements-canonical-platform.md`
- une copie active de `entitlements-canonical-platform.md` sous `backend/docs/`
- suppression du header `Document status: historical-note`
- compatibility wrappers, legacy aliases, silent fallback behavior

## 11. Removal Classification Rules

- `historical-facade`: ancien chemin conserve uniquement par apparence canonique.
- `external-active`: bloque la suppression sans decision utilisateur.
- `canonical-active`: doit etre conserve.
- `dead`: peut etre supprime.
- `needs-user-decision`: bloque l'implementation sans decision.

## 12. Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `backend/docs/entitlements-canonical-platform.md` | md path | `historical-facade` | docs tests | `docs/architecture/` file | `delete` | tests | duplicate old path |

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.
Audit output path: `_condamad/stories/CS-025-repositionner-note-historique-entitlement/entitlement-doc-path-after.md`.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Note historique entitlement | `docs/architecture/entitlements-canonical-platform.md` | `backend/docs/entitlements-canonical-platform.md` |

## 14. Delete-Only Rule

The removable legacy surface is the old path only:

- `backend/docs/entitlements-canonical-platform.md`

It must be deleted, not repointed. Forbidden: wrapper, alias, fallback and re-export.

## 15. External Usage Blocker

If the old path is classified as `external-active`, deletion must stop for a
user decision because external-active content must not be deleted. This story
retains the content under `docs/architecture/`.

## 17. Generated Contract Check

- Generated contract check: required
- Evidence: no runtime/API/client files are modified; parity test keeps OpenAPI
  route checks active.

## 18. Files to Inspect First

- `backend/docs/entitlements-canonical-platform.md`
- `backend/docs/ownership-index.md`
- `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py`
- `backend/app/tests/unit/test_backend_docs_ownership.py`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `docs/architecture/entitlements-canonical-platform.md`
- `backend/docs/ownership-index.md`
- `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py`

Likely tests:

- `backend/app/tests/unit/test_entitlement_docs_runtime_parity.py`
- `backend/app/tests/unit/test_backend_docs_ownership.py`

Files not expected to change:

- `backend/app/api`
- `backend/app/services`
- `backend/app/infra/db`
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
pytest -q app/tests/unit/test_entitlement_docs_runtime_parity.py
Pop-Location
rg -n "entitlements-canonical-platform|Document status: historical-note" backend docs _condamad
```

## 22. Regression Risks

- Risk: la note conservee est interpretee comme source canonique active.
- Risk: `backend/docs` conserve une copie legacy.
- Risk: une suppression opportuniste retire du contexte utile.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.

## 24. References

- `_condamad/audits/backend-docs/2026-05-04-2028/03-story-candidates.md#SC-002`
- `_condamad/audits/backend-docs/2026-05-04-2028/00-audit-report.md`
- `_condamad/stories/regression-guardrails.md`
