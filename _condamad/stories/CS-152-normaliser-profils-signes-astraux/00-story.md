# Story CS-152 normaliser-profils-signes-astraux: Normaliser les profils des signes astraux

Status: ready-to-dev

## 1. Objective

Normaliser le referentiel des signes astrologiques.
Le schema cible renomme `signs` vers `astral_signs`, ajoute les taxonomies stables,
puis cree `astral_sign_profiles`.
La table existante `sign_rulerships` est renommee en `astral_sign_rulerships`.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-13 dans Codex.
- Reason for change: `signs` et `sign_rulerships` n'exposent pas le profil
  structurel element/modalite/polarite, alors que ces donnees sont invariantes.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/infra/db/models` et referentiels astrologiques backend.
- In scope:
  - Renommer la table `signs` en `astral_signs` et adapter le modele SQLAlchemy canonique.
  - Creer `astral_elements`, `astral_modalities`, `astral_polarities` avec les valeurs stables demandees.
  - Creer `astral_sign_profiles` avec un profil unique par signe et les mots-cles issus de `docs/recherches astro/signs_keywords.json`.
  - Renommer `sign_rulerships` en `astral_sign_rulerships`, sans recreation parallele.
  - Supprimer `reference_version_id` des maitrises de signes et ajouter `system`.
  - Adapter repositories, seeds, migrations et tests backend touches par ces tables.
- Out of scope:
  - Changer le calcul astronomique, les ephemerides, les maisons, les aspects, les planetes ou les rulesets.
  - Modifier les contrats API publics sauf consequence documentee du payload de reference si `signs` y est encore expose comme cle JSON.
  - Ajouter une interface frontend de consultation des profils.
- Explicit non-goals:
  - Ne pas recreer `astro_characteristics` ou une table generique equivalente.
  - Ne pas reintroduire `reference_version_id` sur les referentiels structurels couverts par `RG-092`.
  - Ne pas ajouter de compatibilite active `signs` ou `sign_rulerships` sous forme de vue, alias ORM, shim, wrapper ou re-export durable.
  - Ne pas masquer le conflit entre le DDL demande avec `UNIQUE` sur les dimensions
    partagees et les 12 donnees de base qui reutilisent ces dimensions.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: registry-catalog-refactor
- Archetype reason: la story restructure un catalogue de reference backend et ses seeds, sans changer le moteur de prediction.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les noms de tables et les relations changent selon le nouveau modele.
  - Le mapping metier des 12 signes, elements, modalites, polarites et maitrises doit rester deterministic et complet.
  - Les consommateurs existants doivent migrer vers les nouveaux modeles sans surface legacy active.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une dependance externe exige les tables physiques
  `signs` ou `sign_rulerships`, ou si les contraintes `UNIQUE` demandees sur
  element/modalite/polarite doivent etre conservees malgre le conflit de donnees.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La source de verite executable est le schema DB migre inspecte par SQLAlchemy/Alembic, complete par les modeles ORM. |
| Baseline Snapshot | yes | Le schema et le seed doivent etre compares avant/apres pour prouver les renames et nouvelles tables. |
| Ownership Routing | yes | Les owners des referentiels astraux doivent etre explicites pour eviter un second catalogue concurrent. |
| Allowlist Exception | no | Aucune exception, alias ou compatibilite n'est autorisee dans cette story. |
| Contract Shape | no | Pas de changement de contrat HTTP public impose; tout impact API doit etre couvert par les tests existants. |
| Batch Migration | yes | Le rename de tables et la migration des consommateurs doivent etre executes comme une migration de catalogue bornee. |
| Reintroduction Guard | no | Le contrat durable est couvert par Persistent Evidence et par l'ajout de `RG-093`; pas de section active separee requise par l'archetype. |
| Persistent Evidence | yes | La migration de referentiel doit laisser des preuves persistantes de schema, seed et scans anti-retour. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - DB schema migre inspecte via SQLAlchemy `inspect(engine)` dans `backend/app/tests/integration/test_reference_data_migrations.py`.
  - Modeles ORM actifs dans `backend/app/infra/db/models/reference.py` et `backend/app/infra/db/models/prediction_reference.py`.
- Secondary evidence:
  - Scans `rg` cibles sur les anciens noms de tables et le versioning des maitrises.
  - Tests de repository et seed.
- Static scans alone are not sufficient for this story because:
  - Les renames de tables, contraintes FK, unicites et donnees seedees doivent etre prouves sur un schema migre executable, pas seulement par absence de texte.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-152-normaliser-profils-signes-astraux/schema-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-152-normaliser-profils-signes-astraux/schema-after.md`
- Expected invariant:
  - Les 12 signes restent presents, les maitrises traditionnelles restent disponibles, et les referentiels structurels restent non versionnes.
- Required comparison:
  - Inventaire des tables `signs`, `sign_rulerships`, `astral_*` avant/apres.
  - Inventaire des colonnes et contraintes de `astral_sign_profiles` et `astral_sign_rulerships`.
  - Comptages seed: 12 signes, 4 elements, 3 modalites, 2 polarites, 12 profils.
  - Preuve que `astral_sign_rulerships` provient du rename de `sign_rulerships`.
- Allowed differences:
  - `signs` devient `astral_signs`.
  - `sign_rulerships` devient `astral_sign_rulerships`.
  - `reference_version_id` disparait des maitrises de signes.
  - Si le DDL exact est garde, les donnees seed doivent etre bloquees comme conflit.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Signes astraux structurels | `backend/app/infra/db/models/reference.py` | Table active `signs`, modele actif `SignModel.__tablename__ = "signs"` |
| Profils element/modalite/polarite | `backend/app/infra/db/models/reference.py` + seed canonique | Mapping duplique dans services, API, frontend ou tests nominaux |
| Maitrises de signes | `backend/app/infra/db/models/prediction_reference.py` | Table active `sign_rulerships` ou maitrises filtrees par `reference_version_id` |
| Seed de reference | `backend/app/services/prediction/reference_seed_service.py` | Script alternatif ou seed local non idempotent |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: cette story ne doit pas ajouter d'allowlist, d'exception wildcard, de compatibilite ou de shim.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: aucun nouveau contrat HTTP, DTO public ou schema frontend genere n'est demande.
  Si un endpoint expose les referentiels, ses tests doivent documenter l'impact exact.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | `signs` table | `astral_signs` | ORM, FK, repositories, seeds | Migration reference | Scan zero-hit table active | Usage externe de `signs` |
| 2 | Taxonomies absentes | `astral_elements`, `astral_modalities`, `astral_polarities`, profils | Seed reference | Tests seed/FK | Comptages exacts | Keywords JSON absent |
| 3 | `sign_rulerships` versionnee | `astral_sign_rulerships` non versionnee | Repository + seed | Tests repository | Scan anti versioning | Besoin de ruleset |

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Schema baseline | `_condamad/stories/CS-152-normaliser-profils-signes-astraux/schema-before.md` | Etat initial des tables signe. |
| Schema final | `_condamad/stories/CS-152-normaliser-profils-signes-astraux/schema-after.md` | Tables `astral_*`, FK, unicites. |
| Seed final | `_condamad/stories/CS-152-normaliser-profils-signes-astraux/reference-seed-after.md` | Mappings, keywords, maitrises. |

## 4i. Reintroduction Guard

- Reintroduction guard: not applicable as a separate contract
- Reason: le guard durable est porte par `RG-093` et par les tests de migration/repository ajoutes ou modifies dans cette story.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/infra/db/models/reference.py` - `SignModel` utilise encore `__tablename__ = "signs"` avec seulement `id`, `code`, `name`.
- Evidence 2: `backend/app/infra/db/models/prediction_reference.py` - `SignRulershipModel` utilise encore `__tablename__ = "sign_rulerships"` et porte `reference_version_id`.
- Evidence 3: `backend/app/services/prediction/reference_seed_service.py` - le seed courant
  alimente 12 maitrises avec `reference_version_id=v2.id`.
- Evidence 4: `backend/app/infra/db/repositories/prediction_reference_repository.py` - `get_sign_rulerships(reference_version_id)` filtre les maitrises par version.
- Evidence 5: `docs/recherches astro/signs_keywords.json` - le fichier source des `keywords` et `shadow_keywords` par signe existe.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage; `RG-091` et `RG-092` s'appliquent.

## 6. Target State

After implementation:

- `astral_signs` est la table canonique des 12 signes et remplace `signs`.
- `astral_elements`, `astral_modalities` et `astral_polarities` contiennent exactement les valeurs demandees.
- `astral_sign_profiles` contient exactement un profil par signe, avec FK vers les taxonomies partagees et JSON texte charge depuis `signs_keywords.json`.
- `astral_sign_rulerships` est le resultat du rename de `sign_rulerships`.
- `astral_sign_rulerships` contient les maitrises non versionnees avec `rulership_type`, `system`, `weight`, `is_primary`.
- Les repositories et seeds lisent les maitrises et profils depuis les nouvelles tables sans `reference_version_id`.
- Les tests de migration, seed et repository bloquent le retour des anciens noms actifs et du versioning sur les maitrises de signes.

## 6b. Structures Et Valeurs Demandees

Le brief demande explicitement les structures et valeurs suivantes.
Elles doivent apparaitre dans la story et guider la migration.

Tables a generer:

```sql
astral_elements : les elements 'fire', 'earth', 'air', 'water'
astral_modalities : 'cardinal', 'fixed', 'mutable'
astral_polarities : 'yang', 'yin'
```

Table `astral_sign_profiles` a creer:

```sql
id INTEGER PRIMARY KEY,
astral_sign_id INTEGER NOT NULL UNIQUE,
astral_element_id INTEGER NOT NULL UNIQUE,
astral_modality_id INTEGER NOT NULL UNIQUE,
astral_polarity_id INTEGER NOT NULL UNIQUE,
keywords_json TEXT,
shadow_keywords_json TEXT,
FOREIGN KEY (astral_sign_id) REFERENCES astral_signs(id)
FOREIGN KEY (astral_element_id) REFERENCES astral_elements(id)
FOREIGN KEY (astral_modality_id) REFERENCES astral_modalities(id)
FOREIGN KEY (astral_polarity_id) REFERENCES astral_polarities(id)
```

Donnees de base a charger dans `astral_sign_profiles`:

```text
aries       | fire  | cardinal | yang
taurus      | earth | fixed    | yin
gemini      | air   | mutable  | yang
cancer      | water | cardinal | yin
leo         | fire  | fixed    | yang
virgo       | earth | mutable  | yin
libra       | air   | cardinal | yang
scorpio     | water | fixed    | yin
sagittarius | fire  | mutable  | yang
capricorn   | earth | cardinal | yin
aquarius    | air   | fixed    | yang
pisces      | water | mutable  | yin
```

Point de coherence a traiter avant implementation:

- Les `UNIQUE` demandes sur `astral_element_id`, `astral_modality_id` et
  `astral_polarity_id` entrent en conflit avec les donnees ci-dessus.
- Exemple: `fire` est utilise par `aries`, `leo` et `sagittarius`.
- Le dev agent doit demander une decision si ces `UNIQUE` doivent rester exacts.
- Sans decision contraire, la cible executable garde `UNIQUE` seulement sur
  `astral_sign_id`.

Les champs `keywords_json` et `shadow_keywords_json` viennent de:

```text
docs/recherches astro/signs_keywords.json
```

Table existante a renommer puis simplifier:

```text
sign_rulerships -> astral_sign_rulerships
```

Structure cible de `astral_sign_rulerships`:

```sql
id INTEGER PRIMARY KEY,
astral_sign_id INTEGER NOT NULL,
planet_id INTEGER NOT NULL,
rulership_type TEXT NOT NULL,
system TEXT NOT NULL,
weight REAL NOT NULL,
is_primary BOOLEAN NOT NULL,
FOREIGN KEY (astral_sign_id) REFERENCES astral_signs(id),
FOREIGN KEY (planet_id) REFERENCES planets(id)
```

Valeurs obligatoires pour les maitrises seedees:

```text
rulership_type = domicile
system         = traditional ou modern
weight         = 1.0
is_primary     = true
```

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-091` - la story touche les donnees de reference astrologiques et ne doit pas recreer `astro_characteristics` comme solution generique.
  - `RG-092` - la story touche les signes et les maitrises; `reference_version_id` ne doit pas revenir sur les referentiels structurels.
- Non-applicable invariants:
  - `RG-001` - aucune route historique ou facade API n'est modifiee.
  - `RG-064` - aucune page React ni architecture frontend n'est modifiee.
- Required regression evidence:
  - `pytest app/tests/unit/test_prediction_reference_repository.py app/tests/integration/test_reference_data_migrations.py app/tests/integration/test_seed_31_prediction_v2.py -q`
  - Scan cible anti-retour des anciens noms actifs et de `SignRulershipModel.reference_version_id`.
- Allowed differences:
  - Les anciens noms de tables disparaissent des surfaces actives au profit des noms `astral_*`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `signs` devient `astral_signs` avec 12 signes conserves. | Evidence profile: `baseline_before_after_diff`; migration pytest. |
| AC2 | Les trois taxonomies `astral_*` existent avec les valeurs de `6b`. | Evidence profile: `json_contract_shape`; migration pytest. |
| AC3 | `astral_sign_profiles` contient les 12 profils listes en `6b`. | Evidence profile: `baseline_before_after_diff`; seed pytest. |
| AC4 | Seul `astral_sign_id` est unique dans `astral_sign_profiles`. | Evidence profile: `ast_architecture_guard`; migration pytest. |
| AC5 | `sign_rulerships` est renomme en `astral_sign_rulerships`. | Evidence profile: `baseline_before_after_diff`; migration pytest + scan. |
| AC6 | Les maitrises utilisent les valeurs obligatoires de `6b`. | Evidence profile: `json_contract_shape`; seed pytest. |
| AC7 | Le repository lit les maitrises sans filtre de version. | Evidence profile: `ast_architecture_guard`; repository pytest. |
| AC8 | Aucun shim/vue ne garde les anciens noms. | Evidence profile: `repo_wide_negative_scan`; migration pytest + `rg -n "__tablename__ = \"signs\"" app tests`. |
| AC9 | `RG-091`, `RG-092`, `RG-093` restent satisfaits. | Evidence profile: `reintroduction_guard`; repository pytest + scans anti-retour. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline du schema et des seeds actuels (AC: AC1, AC5)
  - [ ] Subtask 1.1 - Ecrire `_condamad/stories/CS-152-normaliser-profils-signes-astraux/schema-before.md`.
  - [ ] Subtask 1.2 - Identifier les consommateurs actifs de `SignModel`, `signs`, `SignRulershipModel` et `sign_rulerships`.

- [ ] Task 2 - Migrer le schema des signes et profils astraux (AC: AC1, AC2, AC3, AC4)
  - [ ] Subtask 2.1 - Ajouter une migration Alembic qui renomme `signs` en `astral_signs`.
  - [ ] Subtask 2.2 - Ajouter les tables `astral_elements`, `astral_modalities`, `astral_polarities`, `astral_sign_profiles`.
  - [ ] Subtask 2.3 - Definir les contraintes FK et unicite compatibles avec les donnees partagees.

- [ ] Task 3 - Migrer les maitrises de signes (AC: AC5, AC6, AC7)
  - [ ] Subtask 3.1 - Renommer `sign_rulerships` en `astral_sign_rulerships`.
  - [ ] Subtask 3.2 - Supprimer `reference_version_id` de la table, du modele et du repository.
  - [ ] Subtask 3.3 - Ajouter `system` et appliquer les valeurs obligatoires de `6b`.

- [ ] Task 4 - Adapter modeles, repositories et seeds (AC: AC2, AC3, AC6, AC7)
  - [ ] Subtask 4.1 - Mettre a jour `backend/app/infra/db/models/reference.py`.
  - [ ] Subtask 4.2 - Mettre a jour `backend/app/infra/db/models/prediction_reference.py`.
  - [ ] Subtask 4.3 - Charger `docs/recherches astro/signs_keywords.json` via une fonction de seed testable.
  - [ ] Subtask 4.4 - Adapter `ReferenceRepository` et `PredictionReferenceRepository`.

- [ ] Task 5 - Ajouter ou adapter les tests et guards (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9)
  - [ ] Subtask 5.1 - Mettre a jour les tests de migration de reference.
  - [ ] Subtask 5.2 - Mettre a jour les tests de repository prediction.
  - [ ] Subtask 5.3 - Mettre a jour les tests de seed 31 prediction v2.
  - [ ] Subtask 5.4 - Ajouter un scan/test anti-retour des anciens noms actifs et du versioning des maitrises.

- [ ] Task 6 - Capturer l'etat final et valider (AC: AC1, AC8, AC9)
  - [ ] Subtask 6.1 - Ecrire `schema-after.md` et `reference-seed-after.md`.
  - [ ] Subtask 6.2 - Executer lint/tests backend dans le venv.
  - [ ] Subtask 6.3 - Documenter tout impact API exact si un payload expose encore la cle JSON `signs`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/infra/db/repositories/reference_repository.py` pour le seed du vocabulaire structurel invariant.
  - `backend/app/services/prediction/reference_seed_service.py` pour le seed canonique prediction.
  - `docs/recherches astro/signs_keywords.json` comme source unique des mots-cles de signes.
- Do not recreate:
  - Un second mapping hardcode de keywords dans les tests ou le runtime.
  - Un catalogue parallele `sign_profiles` hors namespace `astral_*`.
  - Une table `astral_sign_rulerships` nouvelle sans rename de `sign_rulerships`.
  - Une table generique de caracteristiques astrologiques.
- Shared abstraction allowed only if:
  - Elle remplace une duplication prouvee entre seed et tests.
  - Elle reste localisee au domaine referentiel backend.

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

- `__tablename__ = "signs"` dans les modeles actifs.
- `__tablename__ = "sign_rulerships"` dans les modeles actifs.
- `SignRulershipModel.reference_version_id`
- `reference_version_id=` lors de la creation de `SignRulershipModel`.
- Vue SQL ou modele ORM de compatibilite nomme `signs` ou `sign_rulerships`.
- Reintroduction de `AstroCharacteristicModel` ou `astro_characteristics`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Signes astrologiques structurels | `AstralSignModel` dans `backend/app/infra/db/models/reference.py` | Table physique `signs`, modele actif avec tablename `signs` |
| Profils element/modalite/polarite | `AstralSignProfileModel` et taxonomies `astral_*` | Mapping hardcode hors seed canonique |
| Maitrises de signes | `AstralSignRulershipModel` dans `backend/app/infra/db/models/prediction_reference.py` | `sign_rulerships` versionnee |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: aucune generation client ou OpenAPI n'est directement demandee.
  Si des endpoints de reference exposent ces donnees, leurs tests documentent l'impact.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/migrations/versions`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`
- `docs/recherches astro/signs_keywords.json`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/infra/db/models/reference.py` - renommer le modele/table signe et ajouter les modeles de taxonomies/profils.
- `backend/app/infra/db/models/prediction_reference.py` - renommer et simplifier le modele de maitrises.
- `backend/app/infra/db/models/__init__.py` - exporter les nouveaux modeles.
- `backend/app/infra/db/repositories/reference_repository.py` - seed et lecture des nouveaux referentiels.
- `backend/app/infra/db/repositories/prediction_reference_repository.py` - lecture des maitrises non versionnees.
- `backend/app/services/prediction/reference_seed_service.py` - seed profils, taxonomies et maitrises.
- `backend/migrations/versions/2026xxxx_xxxx_*.py` - migration schema/data.
- `_condamad/stories/regression-guardrails.md` - ajouter `RG-093`.

Likely tests:

- `backend/app/tests/unit/test_prediction_reference_repository.py` - attentes repository.
- `backend/app/tests/unit/test_reference_data_service.py` - payload reference si impacte.
- `backend/app/tests/integration/test_reference_data_migrations.py` - schema et contraintes.
- `backend/app/tests/integration/test_seed_31_prediction_v2.py` - seed complet.

Files not expected to change:

- `frontend/src/**` - aucune UI ou consommation frontend directe n'est dans le scope.
- `backend/app/domain/prediction/**` - pas de changement du moteur pur.
- `backend/app/api/v1/routers/**` - pas de logique routeur attendue sauf si un test API revele un payload de reference a adapter.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py -q
pytest app/tests/integration/test_reference_data_migrations.py app/tests/integration/test_seed_31_prediction_v2.py -q
rg -n "SignRulershipModel\\.reference_version_id|SignRulershipModel\\(reference_version_id" app tests
rg -n "get_sign_rulerships\\(reference_version_id\\)|__tablename__ = \"signs\"" app tests
rg -n "__tablename__ = \"sign_rulerships\"" app tests
rg -n "AstroCharacteristicModel|astro_characteristics" app tests
```

Expected scan handling:

- Hits inside migration history, generated story artefacts, or explicit guard tests must be classified in `reference-seed-after.md`.
- Runtime/model/repository hits for old active surfaces fail validation.

## 22. Regression Risks

- Risk: casser les FK existantes vers `signs`.
  - Guardrail: migration test + baseline before/after des contraintes FK.
- Risk: introduire des contraintes `UNIQUE` impossibles sur element/modalite/polarite.
  - Guardrail: test inspectant les contraintes de `astral_sign_profiles` et les 12 profils seedes.
- Risk: garder deux catalogues actifs `signs` et `astral_signs`.
  - Guardrail: scan anti anciens noms actifs et absence de shim/vue de compatibilite.
- Risk: casser le contexte prediction en retirant `reference_version_id` des maitrises.
  - Guardrail: tests `PredictionReferenceRepository` et seed 31.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, shim, alias, TODO,
  or hidden residual in-domain work.
- Treat the user-provided `UNIQUE` constraints on element/modality/polarity as rejected by data consistency unless the user explicitly overrides the mathematical conflict.

## 24. References

- `docs/recherches astro/signs_keywords.json` - source des keywords de signes.
- `backend/app/infra/db/models/reference.py` - modele actuel `SignModel`.
- `backend/app/infra/db/models/prediction_reference.py` - modele actuel `SignRulershipModel`.
- `backend/app/services/prediction/reference_seed_service.py` - seed actuel des maitrises.
- `_condamad/stories/regression-guardrails.md` - invariants `RG-091`, `RG-092` et futur `RG-093`.
