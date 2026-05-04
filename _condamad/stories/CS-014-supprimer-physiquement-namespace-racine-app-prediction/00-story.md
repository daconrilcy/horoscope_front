# Story CS-014 supprimer-physiquement-namespace-racine-app-prediction: Supprimer physiquement le namespace racine app.prediction

Status: done

## 1. Objective

Supprimer le package racine `backend/app/prediction` apres migration de tous ses consommateurs vers leurs owners canoniques, sans facade, alias, fallback, wrapper ni re-export.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md#SC-001`
- Reason for change: le finding `F-001` montre que `app.prediction` reste une surface runtime active avec fichiers, templates et imports.

## 3. Domain Boundary

- Domain: `backend/app/prediction`
- In scope:
  - Inventaire avant/apres des fichiers restants sous `backend/app/prediction`.
  - Migration finale des imports vers `app.domain.prediction`, `app.services.prediction`, `app.infra` ou contrats API canoniques.
  - Suppression physique de `backend/app/prediction`, y compris `__init__.py`, apres remplacement de tous les consommateurs.
  - Garde zero fichier et zero import pour `app.prediction`.
- Out of scope:
  - Changer les contrats HTTP prediction.
  - Ajouter un nouveau dossier de base sous `backend/`.
  - Refondre le calcul metier au-dela des migrations necessaires.
  - Modifier le frontend.
- Explicit non-goals:
  - Ne pas affaiblir `RG-026` a `RG-033`.
  - Ne pas creer de namespace transitoire concurrent.
  - Ne pas conserver `app.prediction` pour compatibilite.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: legacy-facade-removal
- Archetype reason: la story supprime le chemin historique `app.prediction` apres migration des consommateurs vers owners canoniques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les imports et chemins de modules changent.
  - Les sorties metier et contrats API existants doivent rester equivalentes.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un consommateur externe documente depend encore de `app.prediction`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde pytest et l'importabilite Python prouvent l'absence runtime du namespace. |
| Baseline Snapshot | yes | L'inventaire avant/apres du namespace est obligatoire. |
| Ownership Routing | yes | Chaque fichier doit avoir un owner canonique. |
| Allowlist Exception | no | Aucune exception durable a `app.prediction` n'est autorisee. |
| Contract Shape | no | Aucun contrat HTTP ou DTO public ne doit changer. |
| Batch Migration | no | Le plan de lots est une contrainte de sequencing, pas un contrat batch transverse. |
| Reintroduction Guard | yes | Le namespace supprime ne doit pas reapparaitre. |
| Persistent Evidence | yes | Les inventaires et audits doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard dans `backend/app/tests/unit/test_daily_prediction_guardrails.py`.
  - Importabilite Python: `python -c "import importlib.util; assert importlib.util.find_spec('app.prediction') is None"`.
- Secondary evidence:
  - `rg --files app/prediction` et scans d'import sous `app` et `tests`.
- Static scans alone are not sufficient for this story because:
  - Le package peut rester importable meme si certains imports nominaux ont ete migres.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-014-supprimer-physiquement-namespace-racine-app-prediction/prediction-namespace-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-014-supprimer-physiquement-namespace-racine-app-prediction/prediction-namespace-after.md`
- Expected invariant:
  - `rg --files backend/app/prediction` ne retourne aucun fichier apres suppression.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Moteur pur prediction | `backend/app/domain/prediction` | `backend/app/prediction` |
| Cas d'usage prediction | `backend/app/services/prediction` | `backend/app/api` |
| Read models DB | `backend/app/infra/db/repositories` ou owner decide par CS-016 | `backend/app/prediction` |
| Contrats API publics | `backend/app/services/api_contracts` ou owner API canonique | `backend/app/prediction` |
| Jobs applicatifs | `backend/app/jobs` consommant owners canoniques | `backend/app/prediction` |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: l'objectif final interdit toute exception active pour `backend/app/prediction`.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
- Batch migration plan: not applicable
- Reason: le contrat transverse batch n'est pas actif; le sequencing CS-015 a CS-017 est gere par les tasks et blockers.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Inventaire avant | `prediction-namespace-before.md` | Capturer fichiers et consommateurs avant suppression. |
| Inventaire apres | `prediction-namespace-after.md` | Prouver zero fichier et zero import actif. |
| Audit de suppression | `removal-audit.md` | Classer les surfaces supprimees ou bloquees. |

## 4i. Reintroduction Guard

- Guard target:
  - Aucun fichier sous `backend/app/prediction`.
  - Aucun import `from app.prediction` ou `import app.prediction` dans `backend/app` et `backend/tests`.
  - Source deterministe: importable python modules et AST guard collecte par pytest.
- The implementation must add or update an architecture guard that fails if the removed namespace is reintroduced.
- Guard evidence:
  - Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`.
  - Evidence profile: `repo_wide_negative_scan`; `rg -n "from app\\.prediction|import app\\.prediction" app tests -g "*.py"`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-04-1130/01-evidence-log.md` - `E-003` signale 39 fichiers Python et 16 templates.
- Evidence 2: `_condamad/audits/prediction/2026-05-04-1130/02-finding-register.md` - `F-001` demande la suppression sans shim.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage, notamment `RG-026` a `RG-033`.

## 6. Target State

- `backend/app/prediction` n'existe plus.
- Tous les consommateurs utilisent un owner canonique explicite.
- Les tests prediction passent sans import `app.prediction`.
- La garde anti-retour echoue si le namespace ou un import revient.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-026` - interdit les shims et re-exports depuis l'ancien namespace.
  - `RG-032` - doit evoluer de garde anti-croissance vers garde zero fichier.
  - `RG-034` - invariant cree par cette story pour l'extinction physique.
- Non-applicable invariants:
  - `RG-025` - Stripe n'est pas touche.
- Required regression evidence:
  - Inventaire avant/apres, test de garde, scans zero import.
- Allowed differences:
  - Suppression de `backend/app/prediction` et migration des imports.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | L'inventaire avant/apres du namespace est persiste. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC2 | Aucun fichier ne reste sous `backend/app/prediction`. | Evidence profile: `python_module_removed`; `rg --files app/prediction` depuis `backend` doit etre zero-hit. |
| AC3 | Aucun import actif `app.prediction` ne reste. | Evidence profile: `python_import_absence`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC4 | Les owners canoniques sont audites. | Evidence profile: `batch_migration_mapping`; Manual check: open `removal-audit.md` and verify expected owner. |
| AC5 | La garde d'extinction bloque la reintroduction. | Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer les inventaires avant et owners cibles (AC: AC1, AC4)
- [x] Task 2 - Migrer les consommateurs restants vers les owners canoniques (AC: AC3, AC4)
- [x] Task 3 - Supprimer physiquement `backend/app/prediction` (AC: AC2)
- [x] Task 4 - Adapter la garde d'extinction et les tests prediction (AC: AC3, AC5)
- [x] Task 5 - Persister l'audit apres suppression (AC: AC1, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/services/prediction` pour les cas d'usage.
  - `backend/app/domain/prediction` cree par CS-015 pour le moteur pur.
  - Owners de read models decides par CS-016.
- Do not recreate:
  - Un package `app.prediction` bis.
  - Des DTO dupliques pour passer les tests.
- Shared abstraction allowed only if:
  - Elle remplace une responsabilite identifiee dans l'audit de migration.

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
- `app.prediction.__init__`

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: fichier conserve uniquement si l'audit prouve qu'il est l'owner canonique, ce qui bloque la suppression.
- `external-active`: import externe documente hors repo ou contrat public connu.
- `historical-facade`: surface gardee seulement pour ancien chemin `app.prediction`.
- `dead`: surface sans consommateur apres migration.
- `needs-user-decision`: ambiguite restante apres scans.

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
| `backend/app/prediction` | module | needs-user-decision | Inventaire avant | Owners CS-015 a CS-017 | needs-user-decision | Audit `SC-001` | Consumers restants. |
| `backend/app/prediction/__init__.py` | file | historical-facade | Imports legacy apres migration | Aucun | delete | Scan zero import | Reintroduction du package. |
| Consumers `app.prediction.*` | import path | canonical-active | Services et tests avant migration | Owners canoniques | replace-consumer | Inventaire avant | Behavior drift. |
| Owner canonique confirme | module | canonical-active | Runtime apres migration | Lui-meme | keep | Tests passants | Suppression incorrecte. |

Audit output path when applicable:

- `_condamad/stories/CS-014-supprimer-physiquement-namespace-racine-app-prediction/removal-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Moteur pur prediction | `backend/app/domain/prediction` | `backend/app/prediction` |
| Services prediction | `backend/app/services/prediction` | `backend/app/prediction` |
| Read models persisted | Owner CS-016 | `backend/app/prediction/persisted_*.py` |
| Projection publique | Owner CS-017 | `backend/app/prediction/public_projection.py` |

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

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop and record exact external evidence, deletion risk, and user decision.

## 17. Generated Contract Check

Required generated-contract evidence:

- OpenAPI path absence: aucun chemin OpenAPI ne doit etre supprime par cette story.
- generated client/schema absence: aucun client genere ne doit contenir une reference `app.prediction`.
- route manifest absence: aucun manifest de routes ne doit referencer `app.prediction`.

## 18. Files to Inspect First

- `_condamad/audits/prediction/2026-05-04-1130/01-evidence-log.md`
- `backend/app/prediction`
- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/infra/db/repositories/daily_prediction_repository.py`
- `backend/app/api/v1/routers/public/predictions.py`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/prediction` - suppression apres migration.
- `backend/app/tests/unit/test_daily_prediction_guardrails.py` - garde zero fichier et zero import.
- `_condamad/stories/CS-014-supprimer-physiquement-namespace-racine-app-prediction/removal-audit.md` - audit persistant.

Likely tests:

- `backend/app/tests/unit/test_daily_prediction_guardrails.py` - garde d'extinction.
- `backend/app/tests/unit/test_engine_orchestrator.py` - imports moteur.
- `backend/app/tests/integration/test_daily_prediction_api.py` - non-regression API.

Files not expected to change:

- `frontend/src` - aucun contrat frontend ne doit changer.
- `backend/pyproject.toml` - aucune dependance nouvelle.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_engine_orchestrator.py
pytest -q app/tests/integration/test_daily_prediction_api.py
rg --files app/prediction
rg -n "from app\.prediction|import app\.prediction" app tests -g "*.py"
ruff check app tests
```

## 22. Regression Risks

- Risk: suppression avant migration complete.
  - Guardrail: `AC4` impose un audit par lot et bloque les items `needs-user-decision`.
- Risk: retour du namespace via re-export.
  - Guardrail: `AC5` impose une garde de reintroduction.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-04-1130/03-story-candidates.md#SC-001` - candidate source.
- `_condamad/audits/prediction/2026-05-04-1130/02-finding-register.md#F-001` - finding source.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
