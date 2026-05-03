# Story CS-006 converger-namespace-racine-app-prediction: Converger le namespace racine app.prediction

Status: done

## 1. Objective

Definir puis appliquer la convergence du package `backend/app/prediction` vers des owners canoniques existants sans creer de facade de compatibilite.
La story doit produire une cartographie persistante fichier par fichier avant tout deplacement, migrer un premier lot coherent, puis bloquer la croissance du namespace racine.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-001`
- Reason for change: le finding `F-001` montre que `app.prediction` porte simultanement domaine, services, infra, projection publique, templates, orchestration et LLM.

## 3. Domain Boundary

- Domain: `backend/app/prediction`
- In scope:
  - Inventaire complet des fichiers Python et templates sous `backend/app/prediction`.
  - Classification vers `domain`, `services`, `infra`, `api/contracts` ou `ops`.
  - Migration du premier lot sans re-export depuis l'ancien package.
  - Garde d'architecture contre l'ajout de nouvelles responsabilites sous `app.prediction`.
- Out of scope:
  - Changement fonctionnel du moteur de prediction.
  - Refonte du narrateur LLM horoscope.
  - Ajout d'un nouveau dossier racine sous `backend/`.
  - Migration complete de tous les fichiers si un blocage produit reste ouvert.
- Explicit non-goals:
  - Ne pas modifier les invariants LLM proteges par `RG-016`, `RG-017`, `RG-018` et `RG-019`.
  - Ne pas recreer `backend/app/prediction/llm_narrator.py`.
  - Ne pas creer de shim, alias ou re-export `app.prediction` pour masquer les imports consommateurs.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: namespace-convergence
- Archetype reason: la story converge un package racine multi-couches vers des namespaces canoniques.
- Behavior change allowed: no
- Behavior change constraints:
  - Les sorties publiques et tests prediction existants doivent rester equivalentes.
  - Les differences autorisees sont limitees aux imports, chemins de modules et artefacts d'audit.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: le moteur pur ne peut pas etre route vers `backend/app/domain/prediction` sans choix produit explicite.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde d'architecture doit etre prouvee par un test AST executable. |
| Baseline Snapshot | yes | La convergence doit comparer l'inventaire avant et apres migration. |
| Ownership Routing | yes | Chaque responsabilite doit avoir un owner canonique cible. |
| Allowlist Exception | no | Aucune exception large n'est autorisee dans cette story. |
| Contract Shape | no | Aucun schema public ne doit changer. |
| Batch Migration | yes | Les fichiers doivent etre traites par lots independants. |
| Reintroduction Guard | yes | Le namespace racine ne doit pas regrossir apres convergence. |
| Persistent Evidence | yes | La cartographie et les baselines doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - AST guard `backend/app/tests/unit/test_daily_prediction_guardrails.py`.
- Secondary evidence:
  - Scans exacts des imports `app.prediction` et inventaire `rg --files app/prediction`.
- Static scans alone are not sufficient for this story because:
  - La convergence doit etre bloquee automatiquement pendant pytest.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/prediction-namespace-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/prediction-namespace-after.md`
- Expected invariant:
  - Les tests prediction cibles restent passants et aucun re-export legacy ne remplace un deplacement reel.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `services/**` | `api/**` |
| HTTP-only adapter | `api/v1/**` | `services/**` |
| Pure cross-cutting helper | `core/**` | `api/**` |
| Persistence detail | `infra/**` | `api/**` |
| Domain invariant | `domain/**` | `api/**` |
| Prediction pure engine | `backend/app/domain/prediction` | `backend/app/prediction` |
| Prediction application orchestration | `backend/app/services/prediction` | `backend/app/prediction` |
| Prediction DB adapter | `backend/app/infra/**` | `backend/app/prediction` |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

Use when the archetype or scope requires migration by independent batches.

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| inventory | `backend/app/prediction` | mapping document | none | guardrails test | file inventory captured | mapping incomplete |
| pure-engine | `app.prediction` calculators | `app.domain.prediction` | backend imports | prediction tests | zero old re-export | product rejects owner |
| service-owned | `engine_orchestrator.py` | `app.services.prediction` | service imports | daily prediction tests | zero shim import | behavior diff |

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| before namespace inventory | `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/prediction-namespace-before.md` | Prouver l'etat avant. |
| after namespace inventory | `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/prediction-namespace-after.md` | Prouver l'etat apres. |
| migration map | `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/prediction-namespace-map.md` | Lier chaque fichier a son owner cible. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route, field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- `backend/app/prediction/llm_narrator.py`
- `from app.prediction.llm_narrator import LLMNarrator`
- `from app.prediction import LLMNarrator`
- Nouveau fichier Python sous `backend/app/prediction` absent de la cartographie approuvee.

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py` checks namespace growth.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - `E-001` compte 40 fichiers Python et 16 templates sous `backend/app/prediction`.
- Evidence 2: `_condamad/audits/prediction/2026-05-03-2214/00-audit-report.md` - le rapport propose des owners cibles par groupe de fichiers.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage, notamment `RG-016` a `RG-019`.

## 6. Target State

- Une cartographie persistante definit l'owner canonique de chaque fichier actuel.
- Le premier lot migre n'est plus importe via `app.prediction`.
- Les consommateurs internes utilisent le namespace canonique.
- Une garde interdit les nouveaux fichiers ou imports interdits sous le namespace racine.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-016` - les tests ne doivent pas redevenir consommateurs de `LLMNarrator`.
  - `RG-017` - le runtime horoscope daily ne doit pas recreer un provider OpenAI direct.
  - `RG-019` - l'assembly prompt horoscope daily reste hors `AstrologerPromptBuilder`.
  - `RG-026` - la convergence `app.prediction` ne doit pas etre contournee par des shims.
- Non-applicable invariants:
  - `RG-025` - la story ne touche pas Stripe.
- Required regression evidence:
  - Tests prediction cibles, guard AST namespace, scans exacts `LLMNarrator` et inventaire avant/apres.
- Allowed differences:
  - Chemins d'import internes des fichiers migres.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La cartographie couvre chaque fichier actuel. | Evidence profile: `batch_migration_mapping`; `rg --files backend/app/prediction`. |
| AC2 | Le premier lot migre utilise les owners canoniques. | Evidence profile: `namespace_converged`; `pytest -q app/tests/unit/test_engine_orchestrator.py`. |
| AC3 | Aucun re-export legacy ne remplace la migration. | Evidence profile: `repo_wide_negative_scan`; `rg -n "LLMNarrator" backend/app backend/tests`. |
| AC4 | Une garde bloque la croissance du namespace. | Evidence profile: `ast_architecture_guard`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |
| AC5 | Les preuves avant apres sont persistees. | Evidence profile: `baseline_before_after_diff`; `pytest -q app/tests/unit/test_daily_prediction_guardrails.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer l'inventaire initial (AC: AC1, AC5)
- [x] Task 2 - Produire la cartographie owner cible (AC: AC1)
- [x] Task 3 - Migrer un premier lot coherent (AC: AC2, AC3)
- [x] Task 4 - Ajouter la garde anti-croissance (AC: AC4)
- [x] Task 5 - Executer la validation finale (AC: AC2, AC3, AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/services/prediction` pour les use cases deja presents.
  - `backend/app/domain` pour les invariants purs.
  - `backend/app/infra` pour les dependances DB.
- Do not recreate:
  - Un nouveau dossier racine sous `backend/`.
  - Un package concurrent `backend/app/prediction_v2`.
  - Une facade `app.prediction` qui re-exporte les nouveaux owners.
- Shared abstraction allowed only if:
  - Elle remplace une duplication prouvee dans la cartographie et possede un seul owner.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- `backend/app/prediction/llm_narrator.py`
- `from app.prediction.llm_narrator import LLMNarrator`
- `from app.prediction import LLMNarrator`
- Re-export depuis `backend/app/prediction/__init__.py` vers un owner canonique.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Calcul prediction pur | `backend/app/domain/prediction` | `backend/app/prediction` |
| Orchestration prediction | `backend/app/services/prediction` | `backend/app/prediction/engine_orchestrator.py` |
| Persistence prediction | `backend/app/infra/**` ou service dedie | `backend/app/prediction/persistence_service.py` |

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

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop and record the exact external evidence.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `backend/app/prediction`
- `backend/app/services/prediction`
- `backend/app/tests/unit/test_daily_prediction_guardrails.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`
- `_condamad/audits/prediction/2026-05-03-2214/00-audit-report.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/prediction/__init__.py` - reduire ou supprimer les exports non canoniques.
- `backend/app/domain/prediction/__init__.py` - exposer le premier lot pur si le dossier existe ou est cree sous owner autorise.
- `backend/app/services/prediction` - heberger l'orchestration applicative du lot migre.
- `_condamad/stories/CS-006-converger-namespace-racine-app-prediction/prediction-namespace-map.md` - cartographie persistante.

Likely tests:

- `backend/app/tests/unit/test_daily_prediction_guardrails.py` - garde anti-croissance.
- `backend/app/tests/unit/test_engine_orchestrator.py` - non-regression orchestration.
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py` - non-retour LLMNarrator.

Files not expected to change:

- `frontend/src` - aucune surface frontend n'est dans le scope.
- `backend/app/api/v1/routers/public/predictions.py` - la projection publique sera traitee par une story separee.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check app tests
pytest -q app/tests/unit/test_daily_prediction_guardrails.py app/tests/unit/test_engine_orchestrator.py tests/unit/prediction/test_llm_narrator_deprecation_guard.py
rg -n "from app\\.prediction\\.llm_narrator import LLMNarrator|LLMNarrator\\(|LLMNarrator\\.narrate" app tests
rg --files app/prediction
```

## 22. Regression Risks

- Risk: un import consommateur est migre vers un mauvais owner.
  - Guardrail: `AC1` impose la cartographie et `AC2` impose les tests du lot.
- Risk: un re-export rend la migration invisible.
  - Guardrail: `AC3` et `AC4` interdisent les shims.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## 24. References

- `_condamad/audits/prediction/2026-05-03-2214/00-audit-report.md` - source du routing cible.
- `_condamad/audits/prediction/2026-05-03-2214/01-evidence-log.md` - preuves `E-001`, `E-002`, `E-017`.
- `_condamad/audits/prediction/2026-05-03-2214/03-story-candidates.md#SC-001` - candidate d'origine.
- `_condamad/stories/regression-guardrails.md` - invariants transverses.
