# Story CS-193 planetary-condition-signals: Construire les signaux interpretatifs types des conditions planetaires

Status: ready-to-dev

## 1. Objective

Ajouter une couche backend `PlanetConditionSignal` au-dessus des
`PlanetConditionProfile` existants. Cette couche traduit les axes numeriques
conditionnels en signaux interpretatifs types, gouvernes par une table
referentielle versionnee, exposes dans `NatalResult.condition_signals` puis dans
le JSON public sous `planet_condition_signals`, sans produire de narration.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: demande utilisateur du 2026-05-19 apres cloture de CS-192.
- Reason for change: CS-192 fournit deja `dignities -> PlanetConditionProfile`;
  les prompts, l'UI et les futurs moteurs d'interpretation ont besoin d'une
  couche stable `PlanetConditionProfile -> signaux exploitables` afin de ne pas
  repliquer des conditions locales comme `if score > 0.7`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/condition`
- In scope:
  - creer le contrat immuable `PlanetConditionSignal`;
  - creer `PlanetConditionSignalBuilder` comme transformateur pur de
    `PlanetConditionProfile` vers signaux;
  - ajouter le referentiel DB `astral_planet_condition_signal_profiles`;
  - charger ce referentiel dans `AstrologyRuntimeReference` sous contrats types;
  - integrer `condition_signals` dans `NatalResult`;
  - exposer `planet_condition_signals` dans `build_chart_json`;
  - ajouter tests, snapshots et gardes anti-regression.
- Out of scope:
  - narration editoriale;
  - prompts LLM et templates de prompt;
  - UI frontend;
  - moteur de planetes dominantes CS-194;
  - conditions avancees CS-195;
  - adapter d'interpretation CS-196;
  - recalcul des dignites ou des profils conditionnels CS-192.
- Explicit non-goals:
  - ne pas faire lire la DB directement par `domain/astrology/condition/**`;
  - ne pas coder de seuils locaux dans les prompts, l'UI, `json_builder.py` ou
    le builder;
  - ne pas ajouter de texte narratif, phrase utilisateur, persona, langue ou
    microcopy longue dans le domaine condition;
  - ne pas modifier la signification des axes de CS-192;
  - ne pas contourner `RG-107`, `RG-108`, `RG-112`, `RG-115`, `RG-116`,
    `RG-118` et `RG-119`.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story cree une couche de signaux domaine derivee d'un
  contrat existant, plus un referentiel DB/runtime et une projection JSON; aucun
  archetype standard ne couvre exactement ce flux derive sans route API nouvelle.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `NatalResult` peut gagner `condition_signals`;
  - le JSON public peut gagner `planet_condition_signals`;
  - les champs existants `dignities`, `planet_condition_profiles`, `chart_balance`,
    maisons, signes, aspects et points astraux ne doivent pas changer;
  - les signaux doivent etre derives uniquement des axes deja presents dans
    `PlanetConditionProfile` et du referentiel runtime charge depuis la DB;
  - aucune route, methode HTTP ou status code n'est ajoute.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: le dev agent estime qu'un signal exige une nouvelle
  regle astrologique experte non derivable d'un axe de `PlanetConditionProfile`.
- Additional validation rules:
  - prouver que `PlanetConditionSignalBuilder` consomme uniquement
    `PlanetConditionProfile` et le referentiel runtime;
  - prouver que les plages `level_min` / `level_max` viennent de la DB/runtime;
  - prouver que les signaux sont tries de facon deterministe par
    `priority_weight`, axe, code;
  - prouver par scans que les prompts, l'UI et le JSON public ne portent aucun
    seuil local de condition planetaire.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story
scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les seuils et metadonnees des signaux doivent provenir du runtime reference charge depuis `astral_planet_condition_signal_profiles`. |
| Baseline Snapshot | yes | le payload natal et le JSON public gagnent un bloc; un avant/apres est requis pour prouver la stabilite de l'existant. |
| Ownership Routing | yes | la story touche infra DB, runtime domaine, builder domaine, resultat natal et projection service. |
| Allowlist Exception | no | aucune exception, alias, fallback ou shim n'est autorise. |
| Contract Shape | yes | `PlanetConditionSignal`, `NatalResult.condition_signals` et `planet_condition_signals` ont une forme publique explicite. |
| Batch Migration | no | aucune migration par lots de consommateurs existants n'est effectuee. |
| Reintroduction Guard | yes | les seuils locaux, la narration et les dependances DB/API/services doivent etre bloques. |
| Persistent Evidence | yes | les snapshots, rapports runtime et rapports de garde doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config: `AstrologyRuntimeReference.condition_signal_profiles` charge
    depuis `astral_planet_condition_signal_profiles`.
- Secondary evidence:
  - migration/schema inspection, tests repository/runtime reference, tests du
    builder condition, snapshots de payload et scans cibles anti-seuil local.
- Static scans alone are not sufficient for this story because:
  - le risque principal est une traduction score -> signal gouvernee hors DB; il
    faut donc executer le chargement runtime et valider les plages chargees.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-193-planetary-condition-signals/evidence/natal-condition-signals-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-193-planetary-condition-signals/evidence/natal-condition-signals-after.json`
- Expected invariant:
  - tous les champs natals et chart JSON existants restent presents et inchanges;
    seuls `condition_signals` dans `NatalResult` et
    `planet_condition_signals` dans le JSON public sont ajoutes.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Table, migration et modele SQLAlchemy du referentiel de signaux | `backend/migrations/**`, `backend/app/infra/db/models/**` | `backend/app/domain/**` |
| Chargement SQLAlchemy des profils de signaux | `backend/app/infra/db/repositories/**` | `backend/app/domain/**` |
| Contrats runtime immutables des signaux | `backend/app/domain/astrology/runtime/runtime_reference.py` | `backend/app/services/**` |
| Transformation profil -> signaux | `backend/app/domain/astrology/condition/**` | `backend/app/infra/**`, `backend/app/api/**`, `backend/app/services/**` |
| Integration du resultat natal | `backend/app/domain/astrology/natal_calculation.py` | routeurs API |
| Projection JSON publique | `backend/app/services/chart/json_builder.py` | calculateurs domaine |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - DTO domaine et payload `NatalResult.condition_signals` /
    `planet_condition_signals`.
- Fields:
  - `planet_code: string` code planete.
  - `score_profile: string` profil de scoring de dignites source.
  - `tradition: string` systeme astrologique source.
  - `reference_version: string` version de reference.
  - `signals: array` liste triee de signaux.
  - `signals[].code: string` code stable du signal.
  - `signals[].label: string` libelle court non narratif du signal.
  - `signals[].axis: string` axe conditionnel source.
  - `signals[].level: string` niveau discret du signal.
  - `signals[].level_min: number` borne inclusive minimale issue du referentiel.
  - `signals[].level_max: number` borne inclusive maximale issue du referentiel.
  - `signals[].axis_value: number` valeur du profil ayant matche la plage.
  - `signals[].interpretation_use: string` usage technique attendu par les prompts/UI.
  - `signals[].priority_weight: number` poids de priorisation.
  - `signals[].prompt_hint: string` hint court gouverne, non narratif,
    destine aux prompts, a l'UI et aux futurs consommateurs sans produire de
    texte de restitution.
- Required fields:
  - tous les champs listes ci-dessus sont requis pour chaque signal.
- Optional fields:
  - aucun champ optionnel dans `PlanetConditionSignal` v1.
- Status codes:
  - aucune route API nouvelle n'est creee et aucun status code n'est modifie.
- Serialization names:
  - `NatalResult.condition_signals` reste `condition_signals`.
  - le JSON public expose `planet_condition_signals`.
  - le champ interne `condition_axis` du referentiel est serialise comme `axis`.
- Frontend type impact:
  - aucun fichier frontend n'est modifie dans cette story; le champ public est
    prepare pour consommation future.
- Generated contract impact:
  - OpenAPI ne doit changer que si le payload natal est deja modelise par schema
    genere; dans ce cas le snapshot doit documenter uniquement l'ajout
    `planet_condition_signals`.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: no old surface is migrated in batches; the story adds one new derived
  signal layer and preserves the existing profile surface.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Snapshot avant | `_condamad/stories/CS-193-planetary-condition-signals/evidence/natal-condition-signals-before.json` | Etat du payload avant ajout. |
| Snapshot apres | `_condamad/stories/CS-193-planetary-condition-signals/evidence/natal-condition-signals-after.json` | Ajout exact des signaux. |
| Rapport runtime | `_condamad/stories/CS-193-planetary-condition-signals/evidence/condition-signal-runtime-reference.md` | Table, lignes et plages chargees. |
| Rapport gardes | `_condamad/stories/CS-193-planetary-condition-signals/evidence/condition-signal-guard-evidence.md` | Scans anti-seuil, anti-DB et anti-LLM. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- loaded runtime reference inventory;
- AST import graph when the existing guard pattern supports it;
- targeted forbidden symbol scans.

Required forbidden examples:

- `from app.infra` dans `backend/app/domain/astrology/condition/**`
- `Session`, `select(` ou modeles SQLAlchemy dans `backend/app/domain/astrology/condition/**`
- seuils locaux comme `SIGNAL_THRESHOLDS`, `CONDITION_SIGNAL_RULES`,
  `if profile.visibility >`, `if profile.functional_strength >` ou equivalent
  hors comparaison aux `level_min` / `level_max` du referentiel runtime
- imports ou symboles `AIEngineAdapter`, `OpenAI`, `prompt`, `narration`,
  `micro_note`, `app.domain.prediction`, `app.services.prediction`
- `planet_condition_signals` calcule dans `json_builder.py` autrement que par
  projection des resultats deja presents dans `NatalResult.condition_signals`

Guard evidence:

- Evidence profile: `reintroduction_guard`; `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
  ou un test de garde voisin verifie les imports, seuils locaux et symboles interdits.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/astrology/condition/contracts.py` -
  `PlanetConditionProfile` existe avec axes canoniques, score de classement,
  breakdown et faits courts non narratifs.
- Evidence 2: `backend/app/domain/astrology/condition/planet_condition_profile_service.py` -
  `PlanetConditionProfileService` derive les profils depuis `PlanetDignityResult`
  et les poids runtime, sans DB directe.
- Evidence 3: `backend/app/domain/astrology/natal_calculation.py` -
  `NatalResult` expose deja `condition_profiles` et les calcule apres les dignites.
- Evidence 4: `backend/app/services/chart/json_builder.py` - le JSON public
  expose deja `planet_condition_profiles` via `_serialize_condition_profiles`.
- Evidence 5: `backend/app/domain/astrology/runtime/runtime_reference.py` -
  le runtime astrologique transporte deja les dignites et les poids conditionnels
  sous contrats immutables.
- Evidence 6: `backend/app/infra/db/models/dignity_reference.py` - les modeles
  SQLAlchemy des dignites et resultats existent; aucune table de signaux
  conditionnels n'est encore visible dans le fichier inspecte.
- Evidence 7: `_condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md` -
  CS-192 etablit le profil conditionnel et exclut narration, UI et table audit dediee.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - invariants de
  regression consultes avant finalisation du perimetre de la story.

## 6. Target State

After implementation:

- La table `astral_planet_condition_signal_profiles` existe avec
  `id`, `condition_axis`, `level_min`, `level_max`, `signal_code`,
  `signal_label`, `signal_level`, `interpretation_use`, `priority_weight`,
  `prompt_hint` et `reference_version_id`.
- Le runtime reference expose les profils de signaux conditionnels sous contrat
  immuable, indexes ou iterables de facon deterministe.
- `PlanetConditionSignalBuilder` produit une liste de signaux par planete depuis
  `PlanetConditionProfile` et les profils runtime, sans seuil local.
- `NatalResult.condition_signals` expose les signaux sans supprimer ni modifier
  `condition_profiles`.
- `build_chart_json` expose `planet_condition_signals` sans recalculer les
  signaux dans le serialiseur.
- Les prompts, l'UI et les modules futurs peuvent consommer `signal_code`,
  `axis`, `level`, `interpretation_use`, `priority_weight` et `prompt_hint`
  sans inspecter directement les scores.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-107` - les donnees astrologiques runtime doivent rester typees et les JSON DB confines a l'infra.
  - `RG-108` - le vocabulaire DB-backed des signaux ne doit pas etre recree en constantes locales.
  - `RG-112` - les constantes metier astrologiques et fallbacks legacy ne doivent pas revenir.
  - `RG-115` - le runtime natal reste objectif et fonde sur des contrats explicites.
  - `RG-116` - les calculateurs/adapters natals ne doivent pas importer les services d'interpretation.
  - `RG-118` - le moteur de dignites reste factuel, sans interpretation, prediction ou LLM.
  - `RG-119` - les signaux doivent rester une couche derivee du profil conditionnel, pas un second moteur expert.
  - `RG-120` - cette story etablit les signaux conditionnels comme traduction gouvernee score -> usage interpretatif.
- Non-applicable invariants:
  - `RG-117` - cette story ne touche pas le scoring des etoiles fixes daily.
- Required regression evidence:
  - tests unitaires du builder de signaux, tests runtime repository, tests payload,
    snapshot avant/apres, scan anti-import DB, scan anti-seuil local, scan
    anti-LLM et scan anti-narration.
- Allowed differences:
  - ajout de `condition_signals` dans `NatalResult`, ajout de
    `planet_condition_signals` dans le JSON public, ajout de la table
    `astral_planet_condition_signal_profiles` et de son modele infra.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La table referentielle existe avec contraintes. | `pytest -q backend/app/tests/integration/test_reference_data_migrations.py`. |
| AC2 | Le runtime expose les profils de signaux types. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC3 | Le builder ne produit aucune narration. | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py`. |
| AC4 | Les profils de signaux charges dans le runtime sont disponibles pour le builder. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC5 | Les plages inclusives runtime selectionnent les signaux sans table locale. | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py`. |
| AC6 | `NatalResult` expose `condition_signals`. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`. |
| AC7 | `build_chart_json` expose `planet_condition_signals`. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` + snapshot. |
| AC8 | La garde `RG-120` passe. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py`. |
| AC9 | Le contrat public reste stable hors ajouts. | `ruff check .` + comparaison snapshots. |
| AC10 | Le tri des signaux est deterministe. | `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Ajouter le referentiel DB/runtime des signaux (AC: AC1, AC2)
  - [ ] Subtask 1.1 - Ajouter une migration Alembic pour `astral_planet_condition_signal_profiles`.
  - [ ] Subtask 1.2 - Ajouter le modele SQLAlchemy infra avec contraintes de version, code et axe.
  - [ ] Subtask 1.3 - Charger et mapper les lignes dans `AstrologyRuntimeReference`.
  - [ ] Subtask 1.4 - Seeder un jeu minimal de signaux couvrant les axes CS-192.

- [ ] Task 2 - Creer les contrats et le builder domaine (AC: AC3, AC4, AC5, AC10)
  - [ ] Subtask 2.1 - Ajouter `PlanetConditionSignal` dans `condition/contracts.py` ou un fichier voisin du meme package.
  - [ ] Subtask 2.2 - Ajouter `PlanetConditionSignalBuilder` dans `backend/app/domain/astrology/condition/**`.
  - [ ] Subtask 2.3 - Exporter explicitement les nouveaux contrats depuis `condition/__init__.py` si le package exporte deja ses surfaces.

- [ ] Task 3 - Integrer les signaux au resultat natal et au JSON public (AC: AC6, AC7)
  - [ ] Subtask 3.1 - Ajouter `condition_signals` a `NatalResult`.
  - [ ] Subtask 3.2 - Construire les signaux apres `condition_profiles` dans `build_natal_result`.
  - [ ] Subtask 3.3 - Ajouter `_serialize_condition_signals` dans `json_builder.py` comme projection stricte.

- [ ] Task 4 - Ajouter tests, preuves et gardes (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10)
  - [ ] Subtask 4.1 - Ajouter les tests unitaires du builder de signaux.
  - [ ] Subtask 4.2 - Etendre les tests runtime reference, contrat natal, chart JSON et resultat chart.
  - [ ] Subtask 4.3 - Mettre a jour la garde d'architecture condition avec seuils locaux interdits.
  - [ ] Subtask 4.4 - Produire les artefacts evidence dans le dossier de story.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetConditionProfile` comme entree unique des signaux.
  - `AstrologyRuntimeReference` comme source unique des profils de signaux.
  - `PlanetConditionProfileService` comme source existante de `condition_profiles`.
  - `build_chart_json` comme unique serialiseur public du theme natal.
- Do not recreate:
  - un nouveau calculateur de dignites;
  - un nouveau calculateur de profils conditionnels;
  - des mappings locaux de seuils, niveaux, libelles ou usages;
  - une projection publique concurrente du theme natal;
  - une narration ou un prompt dans le domaine condition.
- Shared abstraction allowed only if:
  - elle remplace une duplication observee dans le builder ou les tests touches;
  - elle reste dans le package `backend/app/domain/astrology/condition`;
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

- `backend/app/domain/astrology/condition/**` important `app.infra`, `app.api`,
  `app.services`, `app.domain.prediction` ou `app.services.prediction`.
- `backend/app/domain/astrology/condition/**` contenant `Session`, `select(`,
  `OpenAI`, `AIEngineAdapter`, le mot exact `prompt`, `narration`,
  `micro_note` ou texte editorial de restitution. Le champ gouverne
  `prompt_hint` reste autorise comme metadonnee courte non narrative.
- `SIGNAL_THRESHOLDS`, `CONDITION_SIGNAL_RULES`, `CONDITION_SIGNAL_PROFILES`,
  `FUNCTIONAL_STRENGTH_THRESHOLDS`, `VISIBILITY_SIGNAL_LEVELS` ou mapping
  equivalent non derive du runtime.
- Comparaisons directes aux scores dans `backend/app/services/chart/json_builder.py`,
  `frontend/**`, `backend/app/services/llm_generation/**` ou `backend/app/domain/prediction/**`
  pour decider des signaux conditionnels.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Referentiel de profils de signaux | `backend/app/infra/db/models/**`, `backend/app/infra/db/repositories/**` | `backend/app/domain/**` |
| Contrat runtime des profils de signaux | `backend/app/domain/astrology/runtime/runtime_reference.py` | `backend/app/services/**`, `backend/app/api/**` |
| Transformation profil -> signaux | `backend/app/domain/astrology/condition/**` | `backend/app/services/chart/**`, `frontend/**`, prompts LLM |
| Payload natal objectif | `backend/app/domain/astrology/natal_calculation.py` | routeurs API |
| Projection JSON publique | `backend/app/services/chart/json_builder.py` | calculateurs domaine |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: applicable if the natal chart endpoint exposes a
  generated schema for the chart JSON.
- Reason: the story adds public JSON fields but no route, method or status code.

Required generated-contract evidence:

- If OpenAPI includes the affected response schema, capture before/after and
  document that only `planet_condition_signals` is added.
- If OpenAPI does not model the dynamic chart JSON shape, record that fact in
  `_condamad/stories/CS-193-planetary-condition-signals/evidence/condition-signal-guard-evidence.md`.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/condition/contracts.py`
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py`
- `_condamad/stories/regression-guardrails.md`

## 18. Expected Files to Modify

Likely files:

- `backend/migrations/versions/*.py` - ajouter la table referentielle des signaux.
- `backend/app/infra/db/models/dignity_reference.py` - ajouter le modele SQLAlchemy ou un modele voisin si le projet a un fichier plus canonique.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - ajouter le contrat runtime des profils de signaux.
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - charger les profils de signaux.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - mapper les profils de signaux vers le runtime.
- `backend/app/domain/astrology/condition/contracts.py` - ajouter les contrats de signaux.
- `backend/app/domain/astrology/condition/planet_condition_signal_builder.py` - nouveau builder pur.
- `backend/app/domain/astrology/condition/__init__.py` - exports explicites.
- `backend/app/domain/astrology/natal_calculation.py` - integrer `condition_signals`.
- `backend/app/services/chart/json_builder.py` - exposer `planet_condition_signals`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py` - couverture plages, axes, tri et absence narration.
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py` - contrat `NatalResult`.
- `backend/app/tests/unit/test_chart_json_builder.py` - projection publique.
- `backend/app/tests/unit/test_chart_result_service.py` - persistance payload via `chart_results.result_payload` si deja couverte pour CS-192.
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - runtime des profils de signaux.
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` - garde anti-import, anti-seuil local, anti-narration.
- `backend/app/tests/integration/test_reference_data_migrations.py` - schema/migration.

Files not expected to change:

- `frontend/**` - aucune UI ou type frontend dans cette story.
- `backend/app/domain/astrology/dignities/**` - aucun recalcul de dignites.
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py` - ne pas modifier la logique CS-192.
- `backend/app/services/llm_generation/**` - aucun prompt ou adapter LLM dans cette story.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py
pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py
pytest -q backend/app/tests/integration/test_reference_data_migrations.py
ruff format .
ruff check .
rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|from app\.services\.prediction" `
  backend/app/domain/astrology/condition -g "*.py"
rg -n "OpenAI|AIEngineAdapter|chat\.completions|\bprompt\b|narration|micro_note" backend/app/domain/astrology/condition -g "*.py"
rg -n "SIGNAL_THRESHOLDS|CONDITION_SIGNAL_RULES|CONDITION_SIGNAL_PROFILES|FUNCTIONAL_STRENGTH_THRESHOLDS|VISIBILITY_SIGNAL_LEVELS" `
  backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"
rg -n "planet_condition_signals|condition_signals" `
  backend/app/services/chart/json_builder.py `
  backend/app/domain/astrology/natal_calculation.py `
  backend/app/domain/astrology/condition -g "*.py"
```

Expected scan result:

- the first two `rg` commands return zero hits;
- the third `rg` command returns zero hits for hardcoded signal maps;
- the fourth `rg` command shows only projection/integration sites, not local
  threshold decisions in `json_builder.py`.

## 21. Regression Risks

- Risk: les signaux deviennent une narration deguisee.
  - Guardrail: AC3, AC8 et scans anti-LLM/anti-narration limitent les signaux a
    des codes, labels courts, usages et hints non narratifs.
- Risk: le builder encode des seuils locaux au lieu de lire le runtime.
  - Guardrail: AC2, AC4, AC5 et `RG-120` imposent les plages DB/runtime.
- Risk: le serialiseur public recalcule les signaux.
  - Guardrail: AC7 exige une projection stricte depuis `NatalResult.condition_signals`.
- Risk: les prompts ou l'UI recommencent a lire directement les scores.
  - Guardrail: scans cibles et evidence de garde interdisent les seuils locaux
    dans les surfaces consommatrices.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not add dominant planets, advanced planetary conditions, prompts, UI or
  interpretation adapter logic.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 23. References

- `backend/app/domain/astrology/condition/contracts.py` - source actuelle de `PlanetConditionProfile`.
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py` - service que les signaux doivent consommer indirectement via ses resultats.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - proprietaire du contrat runtime a etendre.
- `backend/app/domain/astrology/natal_calculation.py` - proprietaire de `NatalResult`.
- `backend/app/services/chart/json_builder.py` - proprietaire de la projection JSON publique.
- `_condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md` - story precedente dont CS-193 depend.
- `_condamad/stories/regression-guardrails.md` - registre des invariants consulte et enrichi pour CS-193.
