# Story CS-159 ajouter-garde-frontiere-astrology-prediction: Ajouter une garde AST de frontiere astrology vers prediction

Status: ready-to-dev

## 1. Objective

Ajouter une garde d'architecture deterministe qui echoue si
`backend/app/domain/astrology/**` importe prediction ou porte des symboles
produit comme `prediction_categories`, `house_category_weights`,
`visibility_weight`, `base_priority` et `routing_role`.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: demande utilisateur du 2026-05-13 sur le sens interdit `astrology -> prediction`.
- Reason for change: la separation durable ne peut pas reposer sur une convention; elle doit etre testee.

## 3. Domain Boundary

- Domain: `backend/app/tests/unit` architecture guards
- In scope:
  - ajouter ou etendre un test AST d'architecture backend;
  - couvrir les imports directs et les imports de symboles produit interdits;
  - documenter la commande de garde dans les evidences.
- Out of scope:
  - refactor fonctionnel des calculateurs;
  - migration SQL;
  - changement frontend.
- Explicit non-goals:
  - Ne pas ajouter d'allowlist large.
  - Ne pas bloquer le sens autorise `prediction -> astrology`.
  - Ne pas contourner avec des imports dynamiques.
  - Ne pas changer les invariants existants `RG-091` a `RG-094`.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story ajoute une garde anti-regression d'architecture.
- Behavior change allowed: no
- Behavior change constraints:
  - Aucun comportement runtime ne doit changer.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: un import `astrology -> prediction` existant est necessaire au runtime et ne peut pas etre supprime.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | la source executable est le test AST collecte par pytest. |
| Baseline Snapshot | yes | l'inventaire des imports interdits avant/apres doit etre conserve. |
| Ownership Routing | yes | le sens d'import autorise est le coeur de la story. |
| Allowlist Exception | yes | l'archetype exige une section explicite prouvant qu'aucune exception n'est ouverte. |
| Contract Shape | no | aucun contrat API/DTO n'est modifie. |
| Batch Migration | no | aucune migration de consommateurs. |
| Reintroduction Guard | yes | c'est l'objectif principal. |
| Persistent Evidence | yes | la preuve de garde doit etre conservee. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/app/tests/unit/test_astrology_prediction_boundary.py` executed by pytest.
- Secondary evidence:
  - `rg` scans under `backend/app/domain/astrology` for forbidden imports and symbols.
- Static scans alone are not sufficient for this story because:
  - the AST guard must catch import forms that plain text scans may miss.

## 4c. Baseline / Before-After Rule

- Baseline required: yes
- Baseline artifact before implementation:
  - `_condamad/stories/CS-159-ajouter-garde-frontiere-astrology-prediction/generated/astrology-prediction-imports-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-159-ajouter-garde-frontiere-astrology-prediction/generated/astrology-prediction-imports-after.md`
- Expected invariant:
  - `backend/app/domain/astrology/**` ne depend pas de prediction ni de symboles produit.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Faits et interpretation astrologiques | `backend/app/domain/astrology` | `backend/app/domain/prediction` |
| Scoring et categories produit | `backend/app/domain/prediction` | `backend/app/domain/astrology` |
| Garde de frontiere backend | `backend/app/tests/unit/test_astrology_prediction_boundary.py` | scans manuels seuls |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | aucune exception n'est autorisee pour `astrology -> prediction` | permanent |

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, DTO, schema, or generated contract shape is changed.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: no consumer migration is performed.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Import scan before | `generated/astrology-prediction-imports-before.md` | Initial boundary. |
| Import scan after | `_condamad/stories/CS-159-ajouter-garde-frontiere-astrology-prediction/generated/astrology-prediction-imports-after.md` | Prove the final boundary state. |
| Architecture guard result | `_condamad/stories/CS-159-ajouter-garde-frontiere-astrology-prediction/generated/architecture-guard-result.md` | Prove the AST guard command passed. |

## 4i. Reintroduction Guard

- Guard type: AST import guard plus targeted symbol scan.
- Test path: `backend/app/tests/unit/test_astrology_prediction_boundary.py` or nearest existing architecture guard file.
- Forbidden imports:
  - `app.domain.prediction`
  - `app.services.prediction`
- Forbidden symbols:
  - `prediction_categories`
  - `house_category_weights`
  - `visibility_weight`
  - `base_priority`
  - `routing_role`
  - `DomainRouter`
  - `PublicAstroFoundationProjector`
- Guard command: `pytest -q app/tests/unit/test_astrology_prediction_boundary.py` from `backend`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/domain/astrology` - contient le runtime et les builders astrologiques qui doivent rester independants.
- Evidence 2: `backend/app/domain/prediction/domain_router.py` - owner actuel du routage produit vers categories.
- Evidence 3: `backend/app/domain/prediction/natal_sensitivity.py` - owner actuel du scoring de sensibilite produit.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

After implementation:

- Un test AST echoue si `domain/astrology` importe prediction.
- Le test couvre aussi les symboles produit interdits meme sans import direct.
- Le sens `prediction -> astrology` reste autorise.
- Le nouveau guardrail durable est reference dans `regression-guardrails.md`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-091` - protege la purete des donnees astrologiques.
  - `RG-094` - protege `HouseRuntimeData` comme source runtime canonique.
  - `RG-095` - frontiere astrology vers prediction interdite par cette story.
- Non-applicable invariants:
  - `RG-035` - aucun fichier `domain/prediction` n'est modifie.
- Required regression evidence:
  - execution du test AST;
  - scan zero-hit des symboles interdits;
  - mise a jour du registre de guardrails.
- Allowed differences:
  - none.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Un test AST bloque les imports prediction depuis `domain/astrology`. | `pytest -q app/tests/unit/test_astrology_prediction_boundary.py`. |
| AC2 | La garde bloque les symboles produit dans `domain/astrology`. | `rg -n "prediction_categories|house_category_weights" app/domain/astrology -g "*.py"` zero-hit. |
| AC3 | Le registre contient l'invariant durable de frontiere. | `rg -n "RG-095.*Frontiere domain astrology vers prediction" _condamad/stories/regression-guardrails.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Ajouter la garde AST (AC: AC1, AC2)
  - [ ] Subtask 1.1 - Inspecter les guards backend existants.
  - [ ] Subtask 1.2 - Ajouter un test lisant les imports Python de `app/domain/astrology`.

- [ ] Task 2 - Ajouter les preuves persistantes (AC: AC1, AC2)
  - [ ] Subtask 2.1 - Capturer le scan before/after.
  - [ ] Subtask 2.2 - Enregistrer le resultat pytest.

- [ ] Task 3 - Enregistrer l'invariant durable (AC: AC3)
  - [ ] Subtask 3.1 - Ajouter `RG-095` au registre.
  - [ ] Subtask 3.2 - Verifier que la story cite ce guardrail.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - patterns de tests d'architecture existants sous `backend/app/tests/unit`.
  - helpers AST existants si disponibles.
- Do not recreate:
  - un second framework de lint;
  - un script hors pytest si un test suffit.
- Shared abstraction allowed only if:
  - au moins deux guards d'architecture backend l'utilisent.

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

- `backend/app/domain/astrology/** -> app.domain.prediction`
- `backend/app/domain/astrology/** -> app.services.prediction`
- `prediction_categories`
- `house_category_weights`
- `visibility_weight`
- `base_priority`
- `routing_role`
- `DomainRouter`
- `PublicAstroFoundationProjector`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Faits et interpretation astrologiques | `backend/app/domain/astrology` | `backend/app/domain/prediction` |
| Scoring et categories produit | `backend/app/domain/prediction` | `backend/app/domain/astrology` |
| Garde de frontiere backend | `backend/app/tests/unit/test_astrology_prediction_boundary.py` | scans manuels seuls |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/tests/unit`
- `backend/app/domain/astrology`
- `backend/app/domain/prediction`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/tests/unit/test_astrology_prediction_boundary.py` - nouvelle garde AST.
- `_condamad/stories/regression-guardrails.md` - nouvel invariant `RG-095`.

Likely tests:

- `backend/app/tests/unit/test_astrology_prediction_boundary.py` - garde frontiere.

Files not expected to change:

- `backend/app/domain/astrology/**` - seulement si un import interdit existant doit etre corrige.
- `backend/app/domain/prediction/**` - hors scope fonctionnel.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_astrology_prediction_boundary.py
ruff check .
rg -n "app\.domain\.prediction|app\.services\.prediction|prediction_categories|house_category_weights|visibility_weight|base_priority|routing_role" app/domain/astrology -g "*.py"
```

## 22. Regression Risks

- Risk: l'AST guard manque les imports relatifs.
  - Guardrail: tester imports absolus et relatifs dans des fixtures ou par inspection AST robuste.
- Risk: une allowlist trop large annule la garde.
  - Guardrail: aucune allowlist large; toute exception doit bloquer pour decision utilisateur.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unfinished work, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 24. References

- Demande utilisateur du 2026-05-13 - guardrail `astrology -> prediction` interdit.
- `_condamad/stories/regression-guardrails.md` - registre a enrichir.
- `backend/app/domain/astrology` - surface protegee.
