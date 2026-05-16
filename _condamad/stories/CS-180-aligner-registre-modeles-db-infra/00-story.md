# Story CS-180 aligner-registre-modeles-db-infra: Aligner le registre des modèles DB infra avec les tables applicatives

Status: done

## 1. Objective

Corriger l'ecart entre `backend/horoscope.db` et les modèles SQLAlchemy charges par
`Base.metadata`. La story rend `flagged_contents` visible dans le registre global,
classe les tables techniques sans modèle, et ajoute une garde deterministe.

## 2. Trigger / Source

- Source type: audit
- Source reference: audit Codex utilisateur du 2026-05-16 sur toutes les tables de `backend/horoscope.db`.
- Reason for change: l'audit a identifié `flagged_contents` comme table applicative
  avec modèle existant mais non charge par `Base.metadata`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/infra/db`
- In scope:
  - Registre des modèles SQLAlchemy sous `backend/app/infra/db/models`.
  - Garde d'architecture backend qui compare tables applicatives, fichiers de modèles et `Base.metadata`.
  - Artefact d'audit persistant des tables sans modèle applicatif.
- Out of scope:
  - Modifier les routeurs admin support au-delà de la vérification que `FlaggedContentModel` reste consommé.
  - Nettoyer physiquement la base locale `backend/horoscope.db`.
  - Créer une migration de suppression de table.
  - Changer le scheduler APScheduler ou sa table technique.
  - Modifier les modèles LLM déjà exportés depuis `app.infra.db.models.llm`.
- Explicit non-goals:
  - Ne pas supprimer `_alembic_tmp_astrologer_profiles` sans décision DB/migration séparée.
  - Ne pas créer de modèle applicatif pour `alembic_version`, `apscheduler_jobs` ou `llm_prompt_version_fallback_archives`.
  - Ne pas masquer une table applicative via une allowlist large.
  - Ne pas changer les invariants `RG-005`, `RG-008`, `RG-011` et `RG-111`.

## 4. Operation Contract

- Operation type: guard
- Primary archetype: architecture-guard-hardening
- Archetype reason: la correction durcit une garde d'architecture autour du registre canonique de modèles DB et des exceptions de registre.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `Base.metadata.tables` doit inclure `flagged_contents` après import canonique des modèles.
  - Les tables techniques ou historiques restent exclues seulement par classification exacte.
  - Aucun comportement HTTP, payload API ou contrat OpenAPI ne doit changer.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: l'implementation veut supprimer une table SQLite,
  créer une migration destructive ou déclarer `astrologer_prompt_profiles` morte.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La source de vérité est l'inventaire runtime SQLite + `Base.metadata.tables`. |
| Baseline Snapshot | yes | L'ecart avant/apres doit être prouvé par artefacts persistants. |
| Ownership Routing | yes | Les tables DB applicatives appartiennent à `infra/db/models`, pas aux routeurs consommateurs. |
| Allowlist Exception | yes | Les tables sans modèle applicatif doivent être classifiées exactement. |
| Contract Shape | no | Aucun DTO, API, erreur, export ou client généré n'est affecté. |
| Batch Migration | no | La story ne migre pas un lot de consommateurs ou de données. |
| Reintroduction Guard | yes | Une garde doit échouer si une table applicative reste hors registre. |
| Persistent Evidence | yes | L'audit DB avant/apres et la classification des exceptions doivent être conservés. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `backend/horoscope.db` inspecté via SQLite pour les tables existantes.
  - `app.infra.db.base.Base.metadata.tables` après import canonique des modèles.
  - Fichiers `backend/app/infra/db/models/**/*.py` portant `__tablename__`.
- Secondary evidence:
  - Scans `rg` des usages `FlaggedContentModel`, `SQLAlchemyJobStore`, `llm_prompt_version_fallback_archives`.
- Static scans alone are not sufficient for this story because:
  - Le bug concerne le chargement effectif de `Base.metadata`, pas seulement la présence textuelle d'un fichier de modèle.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-after.md`
- Expected invariant:
  - Toute table applicative non technique possède un modèle `infra` et est chargée dans `Base.metadata`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Modèle SQLAlchemy applicatif | `backend/app/infra/db/models/**` | `backend/app/api/**`, `backend/app/services/**` |
| Registre global des modèles non-LLM | `backend/app/infra/db/models/__init__.py` | Imports opportunistes depuis un routeur |
| Registre des modèles LLM | `backend/app/infra/db/models/llm/__init__.py` | Registre racine non-LLM |
| Classification des tables sans modèle applicatif | Artefact story + test de garde | Commentaire implicite ou allowlist en dur non documentée |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/horoscope.db` | `alembic_version` | Table technique Alembic, non applicative. | Permanente, doit rester classifiée. |
| `backend/horoscope.db` | `apscheduler_jobs` | Table technique APScheduler. | Permanente tant que `SQLAlchemyJobStore` est actif. |
| `backend/horoscope.db` | `llm_prompt_version_fallback_archives` | Archive de migration vide. | À revalider par une story archives LLM. |
| `backend/horoscope.db` | `_alembic_tmp_astrologer_profiles` | Table temporaire Alembic locale vide. | Blocage décision: hors correction. |

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Audit avant | `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-before.md` | Prouver l'ecart initial `flagged_contents` / `Base.metadata`. |
| Audit après | `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-after.md` | Prouver que les tables applicatives sont couvertes ou classifiées. |
| Classification exceptions | `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-table-exception-register.md` | Documenter chaque exception avec raison et statut. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if a DB/model registry misalignment is introduced or if a forbidden exception pattern appears.

The guard must check at least one deterministic source:

- tables déclarées dans les fichiers de modèles `infra`.
- tables chargées par `Base.metadata.tables`.
- exceptions exactes du registre de classification.
- forbidden symbols comme une exception wildcard `llm_*`, `_alembic_*` ou `*_archives`.

Required forbidden examples:

- Table applicative avec modèle fichier mais absente de `Base.metadata`.
- Table applicative sans modèle et sans classification exacte.
- Exception wildcard par préfixe de dossier ou famille.

Guard evidence:

- Evidence profile: `reintroduction_guard`; `pytest -q app/tests/unit/test_db_model_registry_guard.py` vérifie l'alignement DB/model registry.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `audit Codex utilisateur 2026-05-16#db-table-model-usage-audit`
- Closure proof required: artefacts before/after, registre des exceptions, test de garde et scans ciblés.
- Known residual in-domain work: aucune table applicative non classifiée ne doit rester.
- Deferred non-domain concerns: nettoyage physique de `_alembic_tmp_astrologer_profiles` et décision produit sur `astrologer_prompt_profiles`.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/infra/db/models/flagged_content.py` - `FlaggedContentModel` déclare `__tablename__ = "flagged_contents"`.
- Evidence 2: `backend/app/api/v1/routers/admin/support.py` - le routeur admin support importe et consomme `FlaggedContentModel`.
- Evidence 3: `backend/app/infra/db/models/__init__.py` - le registre racine n'importe pas `FlaggedContentModel`.
- Evidence 4: `backend/app/infra/db/models/llm/__init__.py` - les modèles LLM ont un registre séparé à conserver.
- Evidence 5: `backend/app/core/scheduler.py` - `SQLAlchemyJobStore(url=settings.database_url)` explique `apscheduler_jobs`.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - invariants consultés avant cadrage, notamment `RG-005`, `RG-008`, `RG-011` et `RG-111`.

## 6. Target State

After implementation:

- `FlaggedContentModel` est exporté par `backend/app/infra/db/models/__init__.py` et chargé par `Base.metadata`.
- Les seules tables sans modèle applicatif acceptées sont classifiées dans
  `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-table-exception-register.md`.
- `astrologer_prompt_profiles` reste classifiée comme table applicative avec modèle chargé mais usage runtime à décider séparément, sans suppression dans cette story.
- Une garde de test échoue si une table applicative future manque de modèle ou de chargement metadata.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-005` - la correction ne doit pas déplacer la persistance dans la couche API.
  - `RG-008` - les exceptions SQL/DB doivent rester exactes et justifiées.
  - `RG-011` - les tests DB ne doivent pas contourner les helpers/fixtures canoniques.
  - `RG-111` - les tables applicatives DB doivent rester alignées avec les modèles SQLAlchemy chargés.
- Non-applicable invariants:
  - `RG-107` - la story ne touche pas les contrats runtime astrology.
  - `RG-110` - la story ne touche pas les libellés prediction localisés.
- Required regression evidence:
  - `pytest -q app/tests/unit/test_db_model_registry_guard.py`
  - `pytest -q app/tests/integration/test_admin_support_api.py`
  - Audit before/after persistant dans le dossier de story.
- Allowed differences:
  - `Base.metadata.tables` gagne `flagged_contents`.
  - Aucun changement de tables SQLite runtime n'est autorisé par cette story.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `flagged_contents` est chargé par `Base.metadata`. | Evidence profile: `runtime_metadata`; `pytest -q app/tests/unit/test_db_model_registry_guard.py`. |
| AC2 | Les tables sans modèle applicatif sont classifiées exactement. | Evidence profile: `persistent_evidence`; `pytest -q app/tests/unit/test_db_model_registry_guard.py`. |
| AC3 | Zéro table applicative non classifiée hors metadata. | Evidence profile: `baseline_snapshot`; `pytest -q app/tests/unit/test_db_model_registry_guard.py`. |
| AC4 | Les usages de `FlaggedContentModel` restent fonctionnels. | Evidence profile: `targeted_integration`; `pytest -q app/tests/integration/test_admin_support_api.py`. |
| AC5 | Aucun nettoyage destructif n'est introduit. | Evidence profile: `negative_scan`; `rg -n "drop_table\\(|DROP TABLE" app migrations`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer l'audit avant (AC: AC2, AC3)
  - [x] Subtask 1.1 - Générer l'inventaire DB/model/metadata depuis le venv.
  - [x] Subtask 1.2 - Écrire
    `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-before.md`
    avec tables manquantes, tables non chargées et modèles sans usage runtime.

- [x] Task 2 - Corriger le registre des modèles (AC: AC1, AC4)
  - [x] Subtask 2.1 - Importer `FlaggedContentModel` dans `backend/app/infra/db/models/__init__.py`.
  - [x] Subtask 2.2 - Ajouter `FlaggedContentModel` à `__all__`.

- [x] Task 3 - Ajouter la garde DB/model registry (AC: AC1, AC2, AC3, AC5)
  - [x] Subtask 3.1 - Créer ou compléter `backend/app/tests/unit/test_db_model_registry_guard.py`.
  - [x] Subtask 3.2 - La garde doit parser les fichiers de modèles, comparer `Base.metadata.tables`, et autoriser uniquement les exceptions exactes documentées.
  - [x] Subtask 3.3 - La garde doit éviter tout accès destructif à `backend/horoscope.db`.

- [x] Task 4 - Persister les preuves après correction (AC: AC2, AC3)
  - [x] Subtask 4.1 - Écrire `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-table-exception-register.md`.
  - [x] Subtask 4.2 - Écrire `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-after.md`.

- [x] Task 5 - Valider sans élargir le scope (AC: AC4, AC5)
  - [x] Subtask 5.1 - Exécuter tests ciblés, lint et scans négatifs.
  - [x] Subtask 5.2 - Ne pas marquer la story complète si `astrologer_prompt_profiles` est supprimée ou repointée.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `app.infra.db.base.Base` pour l'inventaire metadata.
  - `backend/app/infra/db/models/__init__.py` comme registre non-LLM.
  - `backend/app/infra/db/models/llm/__init__.py` comme registre LLM séparé.
- Do not recreate:
  - Un second registre global des modèles.
  - Un scanner runtime DB dispersé dans les routes ou services.
  - Un modèle applicatif pour les tables techniques Alembic/APScheduler.
- Shared abstraction allowed only if:
  - Le code de garde devient réutilisé par au moins deux tests ou un script d'audit durable.

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

- Importer `FlaggedContentModel` seulement dans `admin/support.py` comme preuve de chargement metadata.
- Ajouter une exception par préfixe comme `llm_*`, `_alembic_*` ou `*_archives`.
- Supprimer ou migrer `_alembic_tmp_astrologer_profiles` dans cette story.
- Créer `requirements.txt`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chargement des modèles SQLAlchemy non-LLM | `backend/app/infra/db/models/__init__.py` | Imports opportunistes depuis routeurs/services |
| Chargement des modèles SQLAlchemy LLM | `backend/app/infra/db/models/llm/__init__.py` | Duplication dans le registre racine non-LLM |
| Persistance support flagged content | `backend/app/infra/db/models/flagged_content.py` | Définition locale dans `api/v1/routers/admin/support.py` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/infra/db/models/__init__.py`
- `backend/app/infra/db/models/flagged_content.py`
- `backend/app/infra/db/models/llm/__init__.py`
- `backend/app/infra/db/base.py`
- `backend/app/core/scheduler.py`
- `backend/app/api/v1/routers/admin/support.py`
- `backend/app/tests/integration/test_admin_support_api.py`
- `_condamad/stories/regression-guardrails.md`

## 18. Expected Files to Modify

Likely files:

- `backend/app/infra/db/models/__init__.py` - exporter `FlaggedContentModel`.
- `backend/app/tests/unit/test_db_model_registry_guard.py` - ajouter la garde d'alignement DB/model/metadata.
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-before.md` - preuve avant.
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-model-registry-after.md` - preuve après.
- `_condamad/stories/CS-180-aligner-registre-modeles-db-infra/db-table-exception-register.md` - exceptions exactes.

Likely tests:

- `backend/app/tests/unit/test_db_model_registry_guard.py` - couverture de registre.
- `backend/app/tests/integration/test_admin_support_api.py` - non-régression support flagged content.

Files not expected to change:

- `backend/migrations/**` - pas de migration destructive dans cette story.
- `backend/app/core/scheduler.py` - `apscheduler_jobs` est seulement classifiée.
- `backend/app/api/v1/routers/admin/support.py` - le consommateur reste inchangé sauf bug test explicite.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_db_model_registry_guard.py
pytest -q app/tests/integration/test_admin_support_api.py
rg -n "drop_table\(|DROP TABLE|_alembic_tmp_astrologer_profiles" app migrations ../_condamad/stories/CS-180-aligner-registre-modeles-db-infra
```

## 21. Regression Risks

- Risk: une table applicative existe mais n'est pas créée dans les bases de test car absente de `Base.metadata`.
  - Guardrail: `test_db_model_registry_guard.py` compare modèle fichier et metadata chargée.
- Risk: une table technique est masquée par une exception trop large.
  - Guardrail: registre d'exceptions exact, sans wildcard ni préfixe.
- Risk: la correction déclenche une migration destructive locale.
  - Guardrail: AC5 et scan négatif `drop_table|DROP TABLE`.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 23. References

- `backend/app/infra/db/models/__init__.py` - registre à corriger.
- `backend/app/infra/db/models/flagged_content.py` - modèle existant non chargé par le registre racine.
- `backend/app/api/v1/routers/admin/support.py` - consommateur runtime de `FlaggedContentModel`.
- `backend/app/core/scheduler.py` - justification de `apscheduler_jobs`.
- `_condamad/stories/regression-guardrails.md` - invariants applicables et `RG-111`.
