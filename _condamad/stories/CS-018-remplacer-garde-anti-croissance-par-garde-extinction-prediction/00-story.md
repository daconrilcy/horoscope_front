# Story CS-018 remplacer-garde-anti-croissance-par-garde-extinction-prediction: Remplacer la garde anti-croissance par une garde d'extinction prediction

Status: done

## 1. Objective

Transformer la garde temporaire de CS-012 en garde finale: aucun fichier sous `backend/app/prediction` et aucun import `app.prediction` dans le runtime ou les tests collectes.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md#SC-005`
- Reason for change: le finding `F-005` indique que la garde actuelle autorise encore l'inventaire legacy au lieu de prouver l'extinction.

## 3. Domain Boundary

- Domain: `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- In scope:
  - Remplacement de l'allowlist CS-012 par une garde zero fichier et zero import.
  - Migration des fixtures et tests collectes vers owners canoniques.
  - Exceptions limitees aux artefacts historiques `_condamad`.
  - Preservation explicite de `RG-026` a `RG-033`.
- Out of scope:
  - Migration fonctionnelle du moteur, des DTO ou des routeurs.
  - Suppression physique du namespace avant CS-014.
  - Changement des contrats API.
  - Ajout de dependance de test.
- Explicit non-goals:
  - Ne pas garder l'allowlist temporaire comme preuve finale.
  - Ne pas accepter des imports legacy dans des tests collectes.
  - Ne pas masquer les hits dans une exception dossier-wide.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la story durcit un test d'architecture pour bloquer la reintroduction du namespace.
- Behavior change allowed: no
- Behavior change constraints:
  - Seuls les tests, fixtures et artefacts de garde changent.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: un test collecte doit rester consommateur nominal de `app.prediction`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde pytest est la source executable finale. |
| Baseline Snapshot | yes | La transition depuis l'allowlist CS-012 doit etre documentee. |
| Ownership Routing | no | Les owners sont etablis par CS-014 a CS-017. |
| Allowlist Exception | yes | Les seules exceptions admises sont les artefacts historiques `_condamad`. |
| Contract Shape | no | Aucun contrat public ne change. |
| Batch Migration | no | La migration fonctionnelle est hors scope. |
| Reintroduction Guard | yes | La story cree la garde anti-retour finale. |
| Persistent Evidence | yes | La preuve de retrait d'allowlist doit etre persistante. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard dans `backend/app/tests/unit/test_daily_prediction_guardrails.py`.
  - `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`.
- Secondary evidence:
  - Scans `rg --files app/prediction` et imports `app.prediction`.
- Static scans alone are not sufficient for this story because:
  - La regle doit echouer automatiquement dans la suite backend.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/guard-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/guard-after.md`
- Expected invariant:
  - L'ancienne allowlist ne permet plus aucun fichier runtime sous `backend/app/prediction`.

## 4d. Ownership Routing Rule

- Ownership routing rule: not applicable
- Reason: cette story verifie les owners migratoires etablis par CS-014 a CS-017 sans les redefinir.

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `prediction-namespace-allowlist.md` | references historiques `app.prediction` | Preuve historique non runtime. | Permanent historical artifact only. |
| `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md` | references audit `app.prediction` | Source d'audit non runtime. | Permanent historical artifact only. |

Rules:

- no wildcard
- no folder-wide exception
- no implicit exception
- every exception must be outside runtime and tests collectes

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: cette story est la garde finale apres migration, pas la migration par lots.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Garde avant | `_condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/guard-before.md` | Documenter l'allowlist CS-012 remplacee. |
| Garde apres | `_condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/guard-after.md` | Prouver la garde zero fichier et zero import. |

## 4i. Reintroduction Guard

- Guard target:
  - `backend/app/prediction` absent.
  - `from app.prediction` et `import app.prediction` absents dans `app` et `tests`.
  - Les artefacts `_condamad` restent exclus du scan runtime.
- Guard evidence:
  - Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`.
  - Evidence profile: `repo_wide_negative_scan`; `rg` zero-hit sous `app` et `tests`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-04-1130/01-evidence-log.md` - `E-014` montre que l'allowlist CS-012 autorise les fichiers actuels.
- Evidence 2: `_condamad/audits/prediction/2026-05-04-1130/02-finding-register.md` - `F-005` demande une garde zero-hit.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- La garde pytest echoue si `backend/app/prediction` existe.
- La garde pytest echoue si un test collecte ou runtime importe `app.prediction`.
- L'ancienne allowlist CS-012 reste seulement comme artefact historique.
- Les invariants `RG-026` a `RG-033` restent couverts.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-026` - pas de shim ou re-export legacy.
  - `RG-032` - doit etre remplace par l'invariant final zero fichier.
  - `RG-038` - invariant cree par cette story pour la garde d'extinction.
- Non-applicable invariants:
  - `RG-025` - Stripe n'est pas touche.
- Required regression evidence:
  - Test de garde, scans zero-hit, preuve de retrait de l'allowlist runtime.
- Allowed differences:
  - Remplacement de l'allowlist temporaire par une garde finale.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La garde echoue si `backend/app/prediction` existe. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC2 | La garde echoue si `app.prediction` est importe. | Evidence profile: `python_import_absence`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC3 | L'allowlist CS-012 n'est plus runtime. | Evidence profile: `allowlist_register_validated`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC4 | Les invariants prediction restent couverts. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC5 | Les artefacts `_condamad` sont seuls exceptes. | Evidence profile: `allowlist_register_validated`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer l'etat de la garde CS-012 avant durcissement (AC: AC3)
- [x] Task 2 - Remplacer l'allowlist runtime par une assertion zero fichier (AC: AC1)
- [x] Task 3 - Ajouter l'assertion zero import runtime et tests collectes (AC: AC2)
- [x] Task 4 - Migrer les tests ou fixtures restants vers owners canoniques (AC: AC2, AC4)
- [x] Task 5 - Persister la preuve finale et les exceptions historiques (AC: AC3, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/tests/unit/test_daily_prediction_guardrails.py` comme garde canonique.
  - `_condamad/stories/regression-guardrails.md` pour les invariants.
- Do not recreate:
  - Une deuxieme garde prediction dans un autre fichier.
  - Une allowlist runtime pour `backend/app/prediction`.
- Shared abstraction allowed only if:
  - Elle simplifie les helpers AST existants dans le meme fichier de garde.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `backend/app/prediction`
- `from app.prediction`
- `import app.prediction`
- `_PREDICTION_NAMESPACE_ALLOWLIST` comme exception runtime active.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Garde architecture prediction | `backend/app/tests/unit/test_daily_prediction_guardrails.py` | scripts manuels non collectes |
| Artefacts historiques | `_condamad` | runtime backend |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `_condamad/stories/CS-012-ajouter-garde-anti-croissance-app-prediction/prediction-namespace-allowlist.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/tests/unit/test_daily_prediction_service.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/tests/unit/test_daily_prediction_guardrails.py` - garde finale zero fichier et zero import.
- `_condamad/stories/CS-018-remplacer-garde-anti-croissance-par-garde-extinction-prediction/guard-after.md` - preuve finale.
- `_condamad/stories/regression-guardrails.md` - invariant final RG-038.

Likely tests:

- `backend/app/tests/unit/test_daily_prediction_guardrails.py` - garde principale.
- `backend/app/tests/unit/test_daily_prediction_service.py` - non-regression service.
- `backend/app/tests/integration/test_daily_prediction_api.py` - integration apres extinction.

Files not expected to change:

- `frontend/src` - aucun impact frontend.
- `backend/pyproject.toml` - aucune dependance nouvelle.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_daily_prediction_service.py
pytest -q app/tests/integration/test_daily_prediction_api.py
rg --files app/prediction
rg -n "from app\.prediction|import app\.prediction" app tests -g "*.py"
ruff check app/tests/unit/test_daily_prediction_guardrails.py
```

## 22. Regression Risks

- Risk: la garde ignore un test collecte encore legacy.
  - Guardrail: `AC2` impose le scan sous `app` et `tests`.
- Risk: les artefacts historiques deviennent une exception trop large.
  - Guardrail: `AC5` limite les exceptions a `_condamad`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md#SC-005` - candidate source.
- `_condamad/audits/prediction/2026-05-04-1130/02-finding-register.md#F-005` - finding source.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
