# Story CS-192 planetary-condition-profile-v1: Construire les profils conditionnels planetaires v1

Status: done

## 1. Objective

Construire une couche backend de normalisation `PlanetConditionProfile`
au-dessus des `PlanetDignityResult` existants. Cette couche produit un profil
conditionnel synthetique par planete, expose dans `NatalResult.condition_profiles`
puis dans le JSON public sous `planet_condition_profiles`, sans ajouter de
nouvelles regles astrologiques expertes.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: demande utilisateur du 2026-05-19 apres validation du cadrage CS-192 et cloture de CS-191.
- Reason for change: le moteur de dignites planetaires retourne deja des scores
  factuels, mais le produit a besoin d'un modele unifie pour classer les
  planetes, exposer les axes de condition et alimenter plus tard les
  interpretations sans dependance directe aux seuils bruts de dignite.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/condition`
- In scope:
  - ajouter les axes de poids conditionnels aux tables et modeles de poids de dignites existants;
  - etendre le runtime reference pour transporter ces axes sous contrats types;
  - creer les contrats immutables `PlanetConditionProfile`, `PlanetConditionBreakdownItem` et `PlanetConditionExplanationFact`;
  - creer `PlanetConditionProfileService` comme agregateur pur au-dessus de `PlanetDignityResult`;
  - integrer `condition_profiles` dans `NatalResult`;
  - exposer le bloc public `planet_condition_profiles` dans `build_chart_json`;
  - ajouter tests, snapshots et gardes anti-regression.
- Out of scope:
  - mutual reception;
  - hayz;
  - heliacal phases;
  - besiegement;
  - bonification ou maltreatment avances;
  - translation of light et collection of light;
  - aspect-based conditions avancees;
  - table dediee `astral_chart_planet_condition_profiles`;
  - frontend et affichage UI.
- Explicit non-goals:
  - ne pas transformer CS-192 en nouveau moteur astrologique;
  - ne pas ajouter de nouvelles regles accidentelles ou essentielles;
  - ne pas faire lire la DB directement par `domain/astrology/condition/**`;
  - ne pas produire de narration editoriale, prompt ou appel LLM;
  - ne pas utiliser `expression_quality_score` comme axe canonique du nouveau profil; il reste un champ de compatibilite des dignites;
  - ne pas contourner `RG-107`, `RG-108`, `RG-112`, `RG-115`, `RG-116` et `RG-118`.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story cree une couche de contrat et de service domaine non
  couverte par un archetype standard; elle etend aussi un payload de resultat
  existant sans route API nouvelle.
- Behavior change allowed: constrained
- Behavior change constraints:
  - le payload natal peut gagner `condition_profiles` et le JSON public peut gagner `planet_condition_profiles`;
  - les champs existants de `NatalResult`, `dignities`, `chart_balance`, maisons, signes, aspects et points astraux ne doivent pas changer;
  - `PlanetDignityResult` reste la source unique des scores d'entree du profil conditionnel;
  - `expression_quality_score` peut rester expose dans `dignities`, mais ne doit pas devenir un axe central de `PlanetConditionProfile`;
  - les nouvelles colonnes DB de poids conditionnels doivent accepter `NULL` ou avoir une valeur par defaut `0.0` pour ne pas casser les seeds existants.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: le dev agent estime qu'un axe demande une nouvelle regle astrologique experte au lieu d'une aggregation derivee des `PlanetDignityResult`.
- Additional validation rules:
  - prouver que `PlanetConditionProfileService` consomme uniquement `PlanetDignityResult` et le contexte runtime transmis;
  - prouver par tests que les axes, le score de classement et les niveaux sont deterministes;
  - prouver par snapshot que les payloads existants restent stables hors ajout `condition_profiles` et `planet_condition_profiles`;
  - prouver par scans que `domain/astrology/condition/**` n'importe ni DB, ni API, ni services, ni prediction, ni LLM.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story
scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les nouveaux axes de poids doivent provenir du runtime reference derive des tables de dignites, pas de constantes locales. |
| Baseline Snapshot | yes | le payload natal et le JSON public gagnent des blocs; un avant/apres est requis pour prouver la stabilite de l'existant. |
| Ownership Routing | yes | la story touche infra, runtime domaine, calcul domaine et projection service; chaque responsabilite doit rester chez son proprietaire canonique. |
| Allowlist Exception | no | aucune exception, alias, fallback ou shim n'est autorise. |
| Contract Shape | yes | `PlanetConditionProfile`, `NatalResult.condition_profiles` et `planet_condition_profiles` ont une forme publique explicite. |
| Batch Migration | no | la story ajoute une couche unique et ne migre pas plusieurs surfaces anciennes vers une nouvelle surface. |
| Reintroduction Guard | yes | les regressions DB directes, scoring local, interpretation, prediction et LLM dans la couche condition doivent echouer. |
| Persistent Evidence | yes | les snapshots et rapports de garde doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config: `AstrologyRuntimeReference.dignity_reference` charge depuis les tables de dignites et contenant les axes de poids conditionnels.
- Secondary evidence:
  - tests repository/runtime reference, tests du domaine condition, snapshots de payload et scans cibles anti-import.
- Static scans alone are not sufficient for this story because:
  - le risque principal est une reference runtime incomplete ou un axe non transporte; il faut donc executer le chargement runtime et valider la forme typee.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-192-planetary-condition-profile-v1/evidence/natal-condition-profile-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-192-planetary-condition-profile-v1/evidence/natal-condition-profile-after.json`
- Expected invariant:
  - tous les champs natals et chart JSON existants restent presents et inchanges;
    seuls `condition_profiles` dans `NatalResult` et `planet_condition_profiles`
    dans le JSON public sont ajoutes.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Migration et modeles SQLAlchemy des nouveaux axes de poids | `backend/migrations/**`, `backend/app/infra/db/models/**` | `backend/app/domain/**` |
| Chargement SQLAlchemy des poids de dignites | `backend/app/infra/db/repositories/**` | `backend/app/domain/**` |
| Contrats runtime immutables | `backend/app/domain/astrology/runtime/runtime_reference.py` | `backend/app/services/**` |
| Contrats et aggregation conditionnelle pure | `backend/app/domain/astrology/condition/**` | `backend/app/infra/**`, `backend/app/api/**`, `backend/app/services/**` |
| Integration du resultat natal | `backend/app/domain/astrology/natal_calculation.py` | `backend/app/api/**` |
| Projection JSON publique | `backend/app/services/chart/json_builder.py` | calculateurs domaine |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - DTO domaine et payload `NatalResult.condition_profiles` / `planet_condition_profiles`.
- Fields:
  - `planet_code: string` code planete.
  - `score_profile: string` profil de scoring de dignites source.
  - `tradition: string` systeme astrologique source.
  - `reference_version: string` version de reference.
  - `sect: string` secte calculee.
  - `functional_strength: number` axe fonctionnel derive des poids.
  - `visibility: number` axe de visibilite derive des poids.
  - `stability: number` axe de stabilite derive des poids.
  - `intensity: number` axe d'intensite derive des poids.
  - `coherence: number` axe de coherence derive des poids.
  - `support: number` axe de support derive des poids.
  - `constraint: number` axe de contrainte derive des poids.
  - `ranking_score: number` score de classement stable, derive uniquement des axes.
  - `condition_level: string` niveau discret stable, derive de `ranking_score`.
  - `breakdown: array` contributions factuelles rattachees aux correspondances de dignite.
  - `explanation_facts: array` faits courts et non narratifs, utilisables par une future couche de rendu.
- Required fields:
  - tous les champs listes ci-dessus sont requis pour chaque profil planete.
- Optional fields:
  - aucun champ optionnel dans `PlanetConditionProfile` v1.
- Status codes:
  - aucune route API nouvelle n'est creee et aucun status code n'est modifie.
- Serialization names:
  - `NatalResult.condition_profiles` reste `condition_profiles`.
  - le JSON public expose `planet_condition_profiles`.
  - les axes internes `functional_strength`, `visibility`, `stability`, `intensity`, `coherence`, `support`, `constraint` gardent ces noms exacts.
- Frontend type impact:
  - aucun fichier frontend n'est modifie dans cette story; le champ public est prepare pour consommation future.
- Generated contract impact:
  - OpenAPI ne doit changer que si le payload natal est deja modelise par schema genere; dans ce cas le snapshot doit documenter uniquement l'ajout `planet_condition_profiles`.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: no old surface is migrated in batches; the story adds one new derived profile layer and preserves the existing dignity surface.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Snapshot avant | `_condamad/stories/CS-192-planetary-condition-profile-v1/evidence/natal-condition-profile-before.json` | Etat du payload avant ajout. |
| Snapshot apres | `_condamad/stories/CS-192-planetary-condition-profile-v1/evidence/natal-condition-profile-after.json` | Ajout exact des profils. |
| Rapport runtime | `_condamad/stories/CS-192-planetary-condition-profile-v1/evidence/condition-runtime-reference.md` | Axes runtime charges. |
| Rapport gardes | `_condamad/stories/CS-192-planetary-condition-profile-v1/evidence/condition-guard-evidence.md` | Scans anti-DB, anti-LLM et anti-prediction. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- forbidden symbols or states
- runtime reference inventory
- AST import graph when the existing guard pattern supports it

Required forbidden examples:

- `from app.infra` dans `backend/app/domain/astrology/condition/**`
- `Session`, `select(` ou modeles SQLAlchemy dans `backend/app/domain/astrology/condition/**`
- mappings locaux de poids conditionnels comme `VISIBILITY_WEIGHTS`, `CONDITION_SCORES`, `CONDITION_LEVELS` ou equivalent non derive du runtime
- imports ou symboles `AIEngineAdapter`, `OpenAI`, `prompt`, `interpretation`, `app.domain.prediction`, `app.services.prediction`
- table dediee `astral_chart_planet_condition_profiles` dans cette story v1

Guard evidence:

- Evidence profile: `reintroduction_guard`; `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` ou un test de garde voisin verifie les imports et symboles interdits.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/astrology/dignities/contracts.py` -
  `PlanetDignityResult` expose deja les scores essentiels, accidentels, total,
  fonctionnel, expression et intensite avec breakdowns.
- Evidence 2: `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` - le service orchestre deja les dignites sans DB directe.
- Evidence 3: `backend/app/domain/astrology/natal_calculation.py` - `NatalResult` expose deja `dignities` et calcule les resultats depuis `PlanetDignityScoringService`.
- Evidence 4: `backend/app/services/chart/json_builder.py` - le JSON public expose deja `dignities` via `_serialize_dignities`.
- Evidence 5: `backend/app/infra/db/models/dignity_reference.py` - les tables de poids de dignites existent et peuvent recevoir les nouveaux axes conditionnels.
- Evidence 6: `_condamad/stories/CS-191-advanced-planet-dignity-engine/generated/03-acceptance-traceability.md` -
  CS-191 est clos sur le moteur de dignites et excluait interpretation et
  persistance dediee.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants de regression consultes avant finalisation du perimetre de la story.

## 6. Target State

After implementation:

- Les poids de dignites runtime transportent les cinq axes conditionnels ajoutes, `visibility`, `stability`, `coherence`, `support` et `constraint`, avec valeurs par defaut `0.0`.
- `PlanetConditionProfileService` produit un profil par planete a partir des `PlanetDignityResult` existants.
- Les axes canoniques du profil sont `functional_strength`, `visibility`, `stability`, `intensity`, `coherence`, `support` et `constraint`; `functional_strength` et `intensity` restent derives des scores existants de `PlanetDignityResult`.
- `ranking_score` et `condition_level` sont deterministes et documentes par tests.
- `NatalResult.condition_profiles` expose les profils sans supprimer ni modifier `dignities`.
- `build_chart_json` expose `planet_condition_profiles` sans recalcul dans le serialiseur.
- Aucun nouveau moteur de condition avancee, aucune table audit dediee et aucune narration ne sont introduits.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-107` - les donnees astrologiques runtime doivent rester typees et les JSON DB confines a l'infra.
  - `RG-108` - les referentiels DB-backed de poids et axes ne doivent pas etre recrees sous forme de constantes locales.
  - `RG-112` - les constantes metier astrologiques et fallbacks legacy ne doivent pas revenir.
  - `RG-115` - le runtime natal reste objectif et fonde sur des contrats explicites.
  - `RG-116` - les calculateurs/adapters natals ne doivent pas importer les services d'interpretation.
  - `RG-118` - le moteur de dignites reste factuel, sans DB directe, interpretation, prediction ou LLM.
  - `RG-119` - cette story etablit `PlanetConditionProfile` comme couche derivee et non comme nouveau moteur expert.
- Non-applicable invariants:
  - `RG-117` - cette story ne touche pas le scoring des etoiles fixes daily.
- Required regression evidence:
  - tests unitaires condition, tests runtime repository, tests payload, snapshot avant/apres, scan anti-import DB, scan anti-LLM, scan anti-prediction et scan anti-table audit v1.
- Allowed differences:
  - ajout de `condition_profiles` dans `NatalResult`, ajout de `planet_condition_profiles` dans le JSON public, ajout de colonnes de poids conditionnels avec valeur par defaut `0.0` ou acceptation de `NULL`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les poids de dignites exposent les cinq nouveaux axes avec valeur par defaut `0.0` ou acceptation de `NULL` compatible. | `pytest -q backend/app/tests/integration/test_reference_data_migrations.py`. |
| AC2 | Le runtime transporte les nouveaux axes. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC3 | Les contrats condition existent sans narration ni dict libre. | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`. |
| AC4 | Le service derive les axes canoniques depuis `PlanetDignityResult`. | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`. |
| AC5 | `NatalResult` expose `condition_profiles` sans casser `dignities`. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`. |
| AC6 | `build_chart_json` expose `planet_condition_profiles` sans recalcul. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` + snapshot evidence. |
| AC7 | La couche condition respecte la garde d'architecture `RG-119`. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py`. |
| AC8 | Le contrat public reste stable hors ajouts autorises. | `ruff check .` + tests cibles + comparaison des snapshots evidence. |
| AC9 | Le classement conditionnel est deterministe. | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Etendre les poids DB/runtime des dignites (AC: AC1, AC2)
  - [x] Subtask 1.1 - Ajouter une migration Alembic pour les cinq colonnes de
    poids conditionnels avec valeur par defaut `0.0` ou acceptation de `NULL` compatible.
  - [x] Subtask 1.2 - Mettre a jour les modeles SQLAlchemy de poids dans `dignity_reference.py`.
  - [x] Subtask 1.3 - Etendre `DignityScoreWeightReferenceData`, le repository runtime et le mapper sans dict libre.

- [x] Task 2 - Creer les contrats et le service condition (AC: AC3, AC4, AC9)
  - [x] Subtask 2.1 - Creer `backend/app/domain/astrology/condition/contracts.py`.
  - [x] Subtask 2.2 - Creer `backend/app/domain/astrology/condition/planet_condition_profile_service.py`.
  - [x] Subtask 2.3 - Ajouter `__init__.py` avec exports explicites si le domaine l'utilise deja pour les autres packages.

- [x] Task 3 - Integrer le profil au resultat natal et au JSON public (AC: AC5, AC6)
  - [x] Subtask 3.1 - Ajouter `condition_profiles` a `NatalResult`.
  - [x] Subtask 3.2 - Calculer les profils apres les `dignities` dans `build_natal_result`.
  - [x] Subtask 3.3 - Ajouter `_serialize_condition_profiles` dans `json_builder.py` sans recalculer les axes.

- [x] Task 4 - Ajouter les tests et preuves persistantes (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9)
  - [x] Subtask 4.1 - Ajouter les tests unitaires du service condition.
  - [x] Subtask 4.2 - Etendre les tests runtime reference, contrat natal, chart JSON et resultat chart.
  - [x] Subtask 4.3 - Mettre a jour ou ajouter la garde d'architecture condition.
  - [x] Subtask 4.4 - Produire les artefacts evidence dans le dossier de story.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetDignityResult` comme entree unique du profil conditionnel.
  - `DignityScoreWeightReferenceData` comme source runtime des axes de poids.
  - `PlanetDignityScoringService` et ses tests existants pour alimenter `NatalResult.dignities`.
  - `build_chart_json` comme unique serialiseur public du theme natal.
- Do not recreate:
  - un nouveau calculateur de dignites;
  - des mappings locaux de scores ou de niveaux astrologiques;
  - une deuxieme projection publique du theme natal;
  - une table audit dediee en v1.
- Shared abstraction allowed only if:
  - elle remplace une duplication observee dans les tests ou serialiseurs touches;
  - elle reste dans le domaine astrology concerne;
  - elle ne cree pas de facade de compatibilite.

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

- `backend/app/domain/astrology/condition/**` important `app.infra`, `app.api`, `app.services`, `app.domain.prediction` ou `app.services.prediction`.
- `backend/app/domain/astrology/condition/**` contenant `Session`, `select(`, `OpenAI`, `AIEngineAdapter`, `prompt`, `interpretation` ou `micro_note`.
- `VISIBILITY_WEIGHTS`, `CONDITION_SCORES`, `CONDITION_LEVELS` ou mapping equivalent de poids metier non derive du runtime.
- `astral_chart_planet_condition_profiles` dans les migrations, modeles ou repositories de cette story v1.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Agregation conditionnelle planetaire | `backend/app/domain/astrology/condition/**` | `backend/app/services/**`, `backend/app/api/**`, `backend/app/domain/prediction/**` |
| Dignity scoring source | `backend/app/domain/astrology/dignities/**` | `backend/app/domain/astrology/condition/**` ne doit pas recalculer les correspondances |
| Payload natal objectif | `backend/app/domain/astrology/natal_calculation.py` | routeurs API |
| Projection JSON publique | `backend/app/services/chart/json_builder.py` | calculateurs domaine |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: applicable if the natal chart endpoint exposes a generated schema for the chart JSON.
- Reason: the story adds public JSON fields but no route, method or status code.

Required generated-contract evidence:

- If OpenAPI includes the affected response schema, capture before/after and document that only `planet_condition_profiles` is added.
- If OpenAPI does not model the dynamic chart JSON shape, record that fact in `_condamad/stories/CS-192-planetary-condition-profile-v1/evidence/condition-guard-evidence.md`.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `_condamad/stories/regression-guardrails.md`

## 18. Expected Files to Modify

Likely files:

- `backend/migrations/versions/*.py` - ajouter les colonnes de poids conditionnels.
- `backend/app/infra/db/models/dignity_reference.py` - ajouter les colonnes aux modeles SQLAlchemy.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - etendre `DignityScoreWeightReferenceData`.
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - charger les nouveaux axes.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - mapper les nouveaux axes.
- `backend/app/domain/astrology/condition/contracts.py` - nouveau contrat domaine.
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py` - nouveau service pur.
- `backend/app/domain/astrology/condition/__init__.py` - exports explicites du package condition.
- `backend/app/domain/astrology/natal_calculation.py` - integrer `condition_profiles`.
- `backend/app/services/chart/json_builder.py` - exposer `planet_condition_profiles`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py` - couverture axes, classement, niveaux et faits.
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py` - contrat `NatalResult`.
- `backend/app/tests/unit/test_chart_json_builder.py` - projection publique.
- `backend/app/tests/unit/test_chart_result_service.py` - persistance payload via `chart_results.result_payload`.
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - runtime axes.
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` - garde anti-import et anti-surface interdite.
- `backend/app/tests/integration/test_reference_data_migrations.py` - schema/migration si le fichier couvre deja les tables astrology.

Files not expected to change:

- `frontend/**` - aucune UI ou type frontend dans cette story.
- `backend/app/domain/astrology/dignities/essential_dignity_calculator.py` - pas de nouvelle regle de dignite essentielle.
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` - pas de nouvelle condition astrologique avancee.
- `backend/app/infra/db/models/dignity_reference.py` hors ajout des axes de poids - ne pas ajouter `AstralChartPlanetConditionProfileModel` en v1.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py
pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py
pytest -q backend/app/tests/integration/test_reference_data_migrations.py
ruff format .
ruff check .
rg -n "Session|select\\(|from app\\.infra|from app\\.services|from app\\.api|from app\\.domain\\.prediction|from app\\.services\\.prediction" `
  backend/app/domain/astrology/condition -g "*.py"
rg -n "OpenAI|AIEngineAdapter|chat\\.completions|prompt|interpretation|micro_note" backend/app/domain/astrology/condition -g "*.py"
rg -n "VISIBILITY_WEIGHTS|CONDITION_SCORES|CONDITION_LEVELS|astral_chart_planet_condition_profiles" backend/app backend/migrations backend/tests -g "*.py"
```

Expected scan result:

- the first two `rg` commands return zero hits;
- the third `rg` command returns zero hits for hardcoded condition maps and for `astral_chart_planet_condition_profiles`.

## 21. Regression Risks

- Risk: le profil conditionnel devient un second moteur astrologique.
  - Guardrail: AC4 et AC7 obligent une derivation depuis `PlanetDignityResult` et des scans anti-regles locales.
- Risk: les nouveaux axes cassent les seeds ou migrations existants.
  - Guardrail: AC1 impose une valeur par defaut `0.0` ou une acceptation de `NULL` compatible et une validation schema.
- Risk: le serialiseur recalcule des seuils ou axes.
  - Guardrail: AC6 exige une projection sans recalcul dans `json_builder.py`.
- Risk: une table audit dediee est ajoutee trop tot.
  - Guardrail: AC7 interdit `astral_chart_planet_condition_profiles` en v1.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not add mutual reception, hayz, heliacal phases, besiegement, bonification, maltreatment, translation of light or collection of light.
- Do not create `astral_chart_planet_condition_profiles` or a corresponding SQLAlchemy model in v1.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 23. References

- `backend/app/domain/astrology/dignities/contracts.py` - source actuelle de `PlanetDignityResult`.
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` - service de dignites que le profil conditionnel doit consommer indirectement via ses resultats.
- `backend/app/domain/astrology/natal_calculation.py` - proprietaire de `NatalResult`.
- `backend/app/services/chart/json_builder.py` - proprietaire de la projection JSON publique.
- `_condamad/stories/CS-191-advanced-planet-dignity-engine/00-story.md` - story precedente dont CS-192 depend.
- `_condamad/stories/regression-guardrails.md` - registre des invariants consultes et enrichi pour CS-192.
