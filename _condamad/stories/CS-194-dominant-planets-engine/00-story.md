# Story CS-194 dominant-planets-engine: Construire le moteur des planetes dominantes

Status: done

## 0. Brief realignment addendum

Correction post-review du 2026-05-19: l'implementation est realignee sur le
brief initial `CS-194 — Dominant Planets Engine`.

- Le contrat public canonique est `NatalResult.dominant_planets` et le JSON
  top-level `dominant_planets`.
- Les tables runtime de dominance sont:
  `astral_dominance_factor_types`, `astral_dominance_score_profiles` et
  `astral_dominance_score_weights`.
- Le profil de scoring canonique est `natal_standard_v1`.
- Les contrats domaine canoniques sont `PlanetDominanceFactor`,
  `PlanetDominanceResult` et `DominantPlanetsResult`.
- Les niveaux stables `very_low`, `low`, `moderate`, `high` et `dominant`
  sont portes par le moteur v1.

## 1. Objective

Créer un moteur backend factuel `PlanetDominanceEngine` qui classe les planètes
dominantes du thème natal à partir des faits déjà calculés: positions, maisons,
dignités, profils conditionnels, signaux conditionnels, angularité, maîtrise du
thème et charge de maîtrises. Le moteur produit des faits structurés, pondérés,
explicables et exploitables par une future couche d’interprétation, sans
narration.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-19, `CS-194 — Dominant Planets Engine`.
- Reason for change: l’application calcule déjà la condition individuelle des
  planètes, mais ne dispose pas d’une couche canonique pour déterminer quelles
  planètes structurent le plus fortement le thème.

## 2a. Sequencing / Blocking Dependencies

- Depends on: `CS-193-planetary-condition-signals`.
- Required precondition before implementation:
  - `_condamad/stories/story-status.md` marks `CS-193` as `done`;
  - `backend/app/domain/astrology/natal_calculation.py::NatalResult` exposes
    `condition_signals`;
  - `backend/app/services/chart/json_builder.py` projects
    `planet_condition_signals` from `NatalResult.condition_signals`.
- If any precondition is missing:
  - stop before editing application code;
  - record the blocker in
    `_condamad/stories/CS-194-dominant-planets-engine/evidence/dominance-guard-evidence.md`;
  - do not create a partial dominance engine and do not duplicate CS-193 signal
    logic.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/dominance`
- In scope:
  - créer le référentiel DB `astral_dominance_factor_types` avec les lignes contractuelles de la section `4b.1`;
  - charger ce référentiel dans `AstrologyRuntimeReference` sous contrat immuable;
  - créer les contrats factuels de dominance planétaire;
  - créer `PlanetDominanceEngine` comme agrégateur pur de faits natals déjà calculés;
  - intégrer le résultat dans `NatalResult` et dans `build_chart_json`;
  - ajouter tests, snapshots et gardes anti-régression.
- Out of scope:
  - mutual reception;
  - translation of light et collection of light;
  - planetary war;
  - heliacal phases avancées;
  - scoring prédictif;
  - narration textuelle;
  - interprétation psychologique;
  - compatibilité relationnelle.
- Explicit non-goals:
  - ne pas modifier les règles de dignités CS-191;
  - ne pas modifier la signification des `PlanetConditionProfile` CS-192;
  - ne pas dupliquer les `PlanetConditionSignal` CS-193; si CS-193 n’est pas implémentée, bloquer avant toute modification applicative;
  - ne pas remplacer `ChartSignatureCalculator` sans classification exacte;
  - ne pas ajouter de logique prediction, LLM, prompt, UI ou texte éditorial;
  - ne pas contourner `RG-101`, `RG-107`, `RG-108`, `RG-112`, `RG-118`, `RG-119` et `RG-120`.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story crée un moteur domaine, un référentiel DB/runtime
  et une projection JSON sans route API nouvelle; aucun archétype standard ne
  couvre exactement ce flux.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `NatalResult` peut gagner `planet_dominance`;
  - le JSON public peut gagner `planet_dominance`;
  - les champs existants `chart_balance.dominant_planets`, `dignities`,
    `planet_condition_profiles`, `planet_condition_signals`, maisons, signes,
    aspects et points astraux ne doivent pas changer;
  - le moteur doit consommer les faits déjà construits et ne doit pas recalculer les dignités, profils conditionnels ou signaux conditionnels;
  - aucune route, méthode HTTP ou status code n’est ajouté.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: l’utilisateur veut exécuter CS-194 avant la clôture
  de CS-193; la seule décision acceptable est de replanifier l’ordre des
  stories ou de réécrire explicitement le scope, pas de livrer une version
  partielle.
- Additional validation rules:
  - prouver que chaque facteur de dominance provient du runtime `astral_dominance_factor_types`;
  - prouver que le score final est déterministe et explicable par facteurs;
  - prouver que `ChartSignatureCalculator` n’est pas conservé comme second moteur concurrent de dominance planétaire sans routage explicite;
  - prouver par scans que la couche dominance n’importe ni DB, ni API, ni services, ni prediction, ni LLM.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story
scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les types, poids par défaut et catégories de facteurs doivent provenir de `astral_dominance_factor_types`. |
| Baseline Snapshot | yes | le payload natal et le JSON public gagnent un bloc; un avant/après est requis pour prouver la stabilité de l’existant. |
| Ownership Routing | yes | la story touche infra DB, runtime domaine, moteur domaine, résultat natal et projection service. |
| Allowlist Exception | no | aucune exception, alias, fallback ou shim n’est autorisé. |
| Contract Shape | yes | les contrats `PlanetDominanceResult`, `NatalResult.planet_dominance` et `planet_dominance` ont une forme publique explicite. |
| Batch Migration | no | aucune migration par lots de consommateurs existants n’est effectuée. |
| Reintroduction Guard | yes | les pondérations locales, la narration, les imports DB/API/services et les doublons de moteur doivent être bloqués. |
| Persistent Evidence | yes | les snapshots, rapports runtime et rapports de garde doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config: `AstrologyRuntimeReference.dominance_factor_types` chargé depuis `astral_dominance_factor_types`.
- Secondary evidence:
  - migration/schema inspection, tests repository/runtime reference, tests du moteur dominance, snapshots de payload et scans cibles anti-poids local.
- Static scans alone are not sufficient for this story because:
  - le risque principal est un moteur qui encode localement les facteurs ou leurs poids; il faut donc exécuter le chargement runtime et valider les lignes actives.

### 4b.1 Dominance Factor Seed Contract

`astral_dominance_factor_types` must seed exactly these active v1 rows for the
default reference version. The values are part of the implementation contract;
the dev agent must not infer alternative weights from code or UI needs.

| code | label | category | default_weight | sort_order | is_active | description |
|---|---|---|---:|---:|---:|---|
| `chart_ruler` | Chart ruler | rulership | 1.20 | 10 | true | Poids du maître de l'ascendant ou du thème selon les maîtrises runtime. |
| `angularity` | Angularity | placement | 1.10 | 20 | true | Proximité factuelle aux angles et maisons angulaires déjà calculées. |
| `condition_strength` | Condition strength | condition | 1.00 | 30 | true | Force fonctionnelle issue de `PlanetConditionProfile`. |
| `visibility` | Visibility | condition | 0.90 | 40 | true | Visibilité issue de `PlanetConditionProfile`. |
| `most_elevated` | Most elevated | placement | 0.80 | 50 | true | Contribution de la planète la plus élevée ou proche du MC dans les faits natals. |
| `luminary_emphasis` | Luminary emphasis | luminary | 0.80 | 60 | true | Accent factuel Soleil/Lune sans interprétation psychologique. |
| `house_rulership_load` | House rulership load | rulership | 0.75 | 70 | true | Charge de maîtrises de maisons depuis `NatalResult.house_rulers`. |
| `aspect_centrality` | Aspect centrality | aspects | 0.70 | 80 | true | Centralité issue des aspects natals ou de `chart_balance.dominant_aspects`. |

Scoring rule:

- each raw factor value is normalized between `0.0` and `1.0`;
- each weighted value equals `raw_value * default_weight`;
- `normalized_score` equals the sum of weighted values divided by the sum of
  active weights;
- `dominance_score` equals `normalized_score` in v1;
- ranking is `dominance_score` descending, then `planet_code` ascending.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-194-dominant-planets-engine/evidence/planet-dominance-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-194-dominant-planets-engine/evidence/planet-dominance-after.json`
- Expected invariant:
  - tous les champs natals et chart JSON existants restent présents et inchangés; seul `planet_dominance` est ajouté au résultat natal et au JSON public.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Table, migration et modèle SQLAlchemy des facteurs | `backend/migrations/**`, `backend/app/infra/db/models/**` | `backend/app/domain/**` |
| Chargement SQLAlchemy du référentiel dominance | `backend/app/infra/db/repositories/**` | `backend/app/domain/**` |
| Contrats runtime des facteurs | `backend/app/domain/astrology/runtime/runtime_reference.py` | `backend/app/services/**` |
| Agrégation de dominance planétaire | `backend/app/domain/astrology/dominance/**` | `backend/app/api/**`, `backend/app/services/**`, `backend/app/domain/prediction/**` |
| Intégration du résultat natal | `backend/app/domain/astrology/natal_calculation.py` | routeurs API |
| Projection JSON publique | `backend/app/services/chart/json_builder.py` | calculateurs domaine |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - DTO domaine et payload `NatalResult.planet_dominance` / `planet_dominance`.
- Fields:
  - `score_profile: string` profil de calcul de dominance.
  - `reference_version: string` version du référentiel.
  - `factor_types: array` référentiel actif utilisé pour le calcul.
  - `factor_types[].code: string` code stable du facteur.
  - `factor_types[].label: string` libellé court.
  - `factor_types[].category: string` catégorie technique.
  - `factor_types[].description: string` description factuelle du facteur.
  - `factor_types[].default_weight: number` poids runtime.
  - `factor_types[].sort_order: integer` ordre runtime déterministe.
  - `factor_types[].is_active: boolean` statut actif du facteur.
  - `planets: array` classement des planètes.
  - `planets[].planet_code: string` code planète.
  - `planets[].rank: integer` rang stable.
  - `planets[].dominance_score: number` score normalisé final.
  - `planets[].normalized_score: number` score final entre `0.0` et `1.0`.
  - `planets[].factors: array` contributions par facteur.
  - `planets[].factors[].factor_code: string` code issu du référentiel.
  - `planets[].factors[].raw_value: number` valeur factuelle avant pondération.
  - `planets[].factors[].weight: number` poids runtime appliqué.
  - `planets[].factors[].weighted_value: number` contribution pondérée.
  - `planets[].factors[].evidence: array` faits courts de provenance.
  - `summary: object` synthèse non narrative.
  - `summary.primary_planet: string | null`
  - `summary.chart_ruler: string | null`
  - `summary.most_visible_planet: string | null`
  - `summary.most_functional_planet: string | null`
  - `summary.angular_dominant_planet: string | null`
- Required fields:
  - tous les champs listés ci-dessus sont requis, sauf les champs `summary.*` nullable.
- Optional fields:
  - aucun champ optionnel dans le contrat v1.
- Status codes:
  - aucune route API nouvelle n’est créée et aucun status code n’est modifié.
- Serialization names:
  - `NatalResult.planet_dominance` reste `planet_dominance`.
  - le JSON public expose `planet_dominance`.
  - les codes de facteurs gardent les noms du brief: `chart_ruler`,
    `angularity`, `condition_strength`, `visibility`, `most_elevated`,
    `luminary_emphasis`, `house_rulership_load`, `aspect_centrality`.
- Frontend type impact:
  - aucun fichier frontend n’est modifié dans cette story; le champ public est préparé pour consommation future.
- Generated contract impact:
  - OpenAPI ne doit changer que si le payload natal est déjà modélisé par schema généré; dans ce cas le snapshot doit documenter uniquement l’ajout `planet_dominance`.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: no old surface is migrated in batches; the story adds one new derived dominance layer and preserves existing chart balance.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Snapshot avant | `_condamad/stories/CS-194-dominant-planets-engine/evidence/planet-dominance-before.json` | État du payload avant ajout. |
| Snapshot après | `_condamad/stories/CS-194-dominant-planets-engine/evidence/planet-dominance-after.json` | Ajout exact de `planet_dominance`. |
| Rapport runtime | `_condamad/stories/CS-194-dominant-planets-engine/evidence/dominance-runtime-reference.md` | Table, lignes actives, poids et ordre chargés. |
| Rapport gardes | `_condamad/stories/CS-194-dominant-planets-engine/evidence/dominance-guard-evidence.md` | Scans anti-poids local, anti-DB, anti-LLM et anti-doublon. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- loaded runtime reference inventory;
- AST import graph when the existing guard pattern supports it;
- targeted forbidden symbol scans.

Required forbidden examples:

- `from app.infra` dans `backend/app/domain/astrology/dominance/**`
- `Session`, `select(` ou modèles SQLAlchemy dans `backend/app/domain/astrology/dominance/**`
- poids locaux comme `DOMINANCE_FACTORS`, `DOMINANCE_WEIGHTS`, `CHART_RULER_WEIGHT`, `ANGULARITY_WEIGHT` ou équivalent non dérivé du runtime
- imports ou symboles `AIEngineAdapter`, `OpenAI`, `prompt`, `narration`, `micro_note`, `app.domain.prediction`, `app.services.prediction`
- nouveau calcul de dominance planétaire dans `json_builder.py` ou dans les prompts/UI

Guard evidence:

- Evidence profile: `reintroduction_guard`;
  `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` ou un test
  de garde voisin vérifie les imports, poids locaux et symboles interdits.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/astrology/condition/contracts.py` -
  `PlanetConditionProfile` existe avec axes factuels `functional_strength`,
  `visibility`, `stability`, `intensity`, `coherence`, `support` et `constraint`.
- Evidence 2: `backend/app/domain/astrology/natal_calculation.py` -
  `NatalResult` expose déjà `dignities`, `condition_profiles`, `house_rulers`,
  `houses`, `signs_runtime` et `chart_balance`.
- Evidence 3: `backend/app/domain/astrology/interpretation/chart_signature.py` -
  `ChartSignatureCalculator` calcule déjà une dominance planétaire simple depuis
  les signes et dignités actives.
- Evidence 4: `backend/app/services/chart/json_builder.py` - le JSON public expose déjà `chart_balance.dominant_planets` et `planet_condition_profiles`.
- Evidence 5: `_condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md` - CS-192 établit les profils conditionnels comme couche dérivée de dignités, sans narration.
- Evidence 6: `_condamad/stories/CS-193-planetary-condition-signals/00-story.md` -
  CS-193 prévoit les signaux conditionnels et marque le moteur de planètes
  dominantes comme hors périmètre.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants de régression consultés avant finalisation du périmètre de la story.
- Evidence 8: `_condamad/stories/story-status.md` - `CS-193` est encore
  `ready-to-dev` au moment de la rédaction; CS-194 doit donc bloquer son
  implémentation applicative tant que CS-193 n'est pas `done`.

## 6. Target State

After implementation:

- La table `astral_dominance_factor_types` existe avec les huit facteurs de la section `4b.1`, leurs catégories, descriptions, poids par défaut, ordre et statut actif.
- `AstrologyRuntimeReference` expose les facteurs de dominance sous contrat immuable et tri déterministe.
- `PlanetDominanceEngine` produit un classement par planète à partir des résultats natals déjà calculés.
- Le moteur calcule et explique au minimum les facteurs `chart_ruler`,
  `angularity`, `condition_strength`, `visibility`, `most_elevated`,
  `luminary_emphasis`, `house_rulership_load` et `aspect_centrality`.
- `NatalResult.planet_dominance` expose les faits sans supprimer ni modifier `chart_balance.dominant_planets`.
- `build_chart_json` expose `planet_dominance` comme projection stricte, sans recalculer de score.
- Aucun prompt, texte psychologique, score prédictif, compatibilité relationnelle ou condition avancée CS-195 n’est introduit.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-101` - les aspects dominants restent le moteur canonique pour la centralité d’aspects et doivent être réutilisés au lieu d’être dupliqués.
  - `RG-107` - les données astrologiques runtime doivent rester typées et les JSON DB confinés à l’infra.
  - `RG-108` - le vocabulaire DB-backed des facteurs et poids ne doit pas être recréé en constantes locales.
  - `RG-112` - les constantes métier astrologiques et fallbacks legacy ne doivent pas revenir.
  - `RG-118` - le moteur de dignités reste factuel, sans interprétation, prediction ou LLM.
  - `RG-119` - les profils conditionnels restent une couche dérivée et ne doivent pas être recalculés par le moteur de dominance.
  - `RG-120` - les signaux conditionnels, s’ils sont disponibles, doivent rester gouvernés par le runtime CS-193.
  - `RG-121` - cette story établit `PlanetDominanceEngine` comme moteur canonique factuel des dominantes planétaires.
- Non-applicable invariants:
  - `RG-117` - cette story ne touche pas le scoring des étoiles fixes daily.
- Required regression evidence:
  - tests unitaires du moteur dominance, tests runtime repository, tests
    payload, snapshot avant/après, scan anti-import DB, scan anti-poids local,
    scan anti-LLM et scan anti-prediction.
- Allowed differences:
  - ajout de la table `astral_dominance_factor_types`, ajout du runtime associé, ajout de `planet_dominance` dans `NatalResult` et dans le JSON public.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `astral_dominance_factor_types` contient exactement les lignes de `4b.1`. | `pytest -q backend/app/tests/integration/test_reference_data_migrations.py` + rapport runtime. |
| AC2 | Le runtime expose uniquement les facteurs actifs triés par `sort_order`. | pytest: `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC3 | Les contrats de dominance sont immuables. | pytest: `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`. |
| AC4 | `PlanetDominanceEngine` classe par score décroissant puis code. | pytest: `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`. |
| AC5 | Chaque score contient un breakdown par facteur. | pytest: `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`. |
| AC6 | `chart_ruler` provient des maîtrises runtime. | pytest: `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` + `rg SIGN_RULERS`. |
| AC7 | `condition_strength` consomme `PlanetConditionProfile`. | pytest dominance engine + `rg PlanetConditionProfileService`. |
| AC8 | `aspect_centrality` vient des faits d’aspects natals. | pytest: `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py`. |
| AC9 | `NatalResult` expose `planet_dominance` sans modifier `chart_balance.dominant_planets`. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`. |
| AC10 | `build_chart_json` expose `planet_dominance` sans recalcul dans le serialiseur. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` + snapshot. |
| AC11 | La garde `RG-121` bloque les poids locaux. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py`. |
| AC12 | Le contrat public reste stable hors ajouts autorisés. | `ruff check .` + comparaison des snapshots evidence. |

## 8. Implementation Tasks

- [x] Task 1 - Ajouter le référentiel DB/runtime des facteurs de dominance (AC: AC1, AC2)
  - [x] Subtask 1.1 - Ajouter une migration Alembic pour `astral_dominance_factor_types`.
  - [x] Subtask 1.2 - Ajouter `AstralDominanceFactorTypeModel` dans le modèle de référence astrologique canonique et l'exporter via `backend/app/infra/db/models/__init__.py`.
  - [x] Subtask 1.3 - Seeder exactement les huit facteurs de `4b.1`.
  - [x] Subtask 1.4 - Charger et mapper les lignes dans `AstrologyRuntimeReference`.

- [x] Task 2 - Créer les contrats et le moteur domaine (AC: AC3, AC4, AC5, AC6, AC7, AC8)
  - [x] Subtask 2.1 - Créer `backend/app/domain/astrology/dominance/contracts.py`.
  - [x] Subtask 2.2 - Créer `backend/app/domain/astrology/dominance/planet_dominance_engine.py`.
  - [x] Subtask 2.3 - Réutiliser `PlanetConditionProfile`, `house_rulers`, `houses`, `planet_positions`, `aspects`, `chart_balance` et le runtime de maîtrises.
  - [x] Subtask 2.4 - Exporter explicitement les surfaces publiques depuis `dominance/__init__.py`.

- [x] Task 3 - Intégrer la dominance au résultat natal et au JSON public (AC: AC9, AC10)
  - [x] Subtask 3.1 - Ajouter `planet_dominance` à `NatalResult`.
  - [x] Subtask 3.2 - Construire la dominance après `condition_profiles`, `condition_signals` et les faits nécessaires dans `build_natal_result`.
  - [x] Subtask 3.3 - Ajouter `_serialize_planet_dominance` dans `json_builder.py` comme projection stricte.

- [x] Task 4 - Ajouter tests, preuves et gardes (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12)
  - [x] Subtask 4.1 - Ajouter les tests unitaires du moteur dominance.
  - [x] Subtask 4.2 - Étendre les tests runtime reference, contrat natal, chart JSON et résultat chart.
  - [x] Subtask 4.3 - Mettre à jour la garde d’architecture runtime avec les poids locaux interdits.
  - [x] Subtask 4.4 - Produire les artefacts evidence dans le dossier de story.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetConditionProfile` comme source unique de force fonctionnelle et visibilité.
  - `AstrologyRuntimeReference.dignities.sign_rulerships` comme source unique des maîtrises.
  - `HouseRulerResolver` / `NatalResult.house_rulers` comme source des maîtres de maisons.
  - `DominantAspectEvaluator` ou `chart_balance.dominant_aspects` pour la centralité d’aspects.
  - `build_chart_json` comme unique serialiseur public du thème natal.
- Do not recreate:
  - un deuxième moteur de dignités;
  - un deuxième moteur de profils conditionnels;
  - des mappings locaux de maîtres de signes, poids ou facteurs;
  - une projection publique concurrente du thème natal;
  - une narration ou un prompt dans le domaine dominance.
- Shared abstraction allowed only if:
  - elle remplace une duplication observée entre `ChartSignatureCalculator` et `PlanetDominanceEngine`;
  - elle reste dans le domaine astrology concerné;
  - elle ne crée pas de façade de compatibilité.

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

- `backend/app/domain/astrology/dominance/**` important `app.infra`, `app.api`, `app.services`, `app.domain.prediction` ou `app.services.prediction`.
- `backend/app/domain/astrology/dominance/**` contenant `Session`, `select(`,
  `OpenAI`, `AIEngineAdapter`, le mot exact `prompt`, `narration`,
  `micro_note` ou texte éditorial de restitution.
- `DOMINANCE_FACTORS`, `DOMINANCE_WEIGHTS`, `CHART_RULER_WEIGHT`, `ANGULARITY_WEIGHT`, `SIGN_RULERS`, `PLANET_RULERS` ou mapping équivalent non dérivé du runtime.
- Recalcul de `condition_profiles`, `condition_signals` ou `chart_balance` dans `backend/app/services/chart/json_builder.py`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Référentiel de facteurs de dominance | `backend/app/infra/db/models/**`, `backend/app/infra/db/repositories/**` | `backend/app/domain/**` |
| Contrat runtime des facteurs | `backend/app/domain/astrology/runtime/runtime_reference.py` | `backend/app/services/**`, `backend/app/api/**` |
| Moteur factuel des dominantes planétaires | `backend/app/domain/astrology/dominance/**` | `backend/app/services/chart/**`, `backend/app/domain/prediction/**`, prompts LLM |
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

- If OpenAPI includes the affected response schema, capture before/after and document that only `planet_dominance` is added.
- If OpenAPI does not model the dynamic chart JSON shape, record that fact in `_condamad/stories/CS-194-dominant-planets-engine/evidence/dominance-guard-evidence.md`.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/condition/contracts.py`
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
- `backend/app/domain/astrology/interpretation/chart_signature.py`
- `backend/app/domain/astrology/interpretation/dominant_aspects.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `_condamad/stories/regression-guardrails.md`

## 18. Expected Files to Modify

Likely files:

- `backend/migrations/versions/*.py` - ajouter la table référentielle des facteurs de dominance.
- `backend/app/infra/db/models/reference.py` - ajouter `AstralDominanceFactorTypeModel` comme référentiel astrologique canonique.
- `backend/app/infra/db/models/__init__.py` - exporter le modèle pour `Base.metadata`.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - ajouter le contrat runtime des facteurs de dominance.
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - charger les facteurs.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - mapper les facteurs vers le runtime.
- `backend/app/domain/astrology/dominance/contracts.py` - nouveau contrat domaine.
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py` - nouveau moteur pur.
- `backend/app/domain/astrology/dominance/__init__.py` - exports explicites.
- `backend/app/domain/astrology/natal_calculation.py` - intégrer `planet_dominance`.
- `backend/app/services/chart/json_builder.py` - exposer `planet_dominance`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_planet_dominance_engine.py` - couverture facteurs, pondération, classement, tie-break et absence narration.
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py` - contrat `NatalResult`.
- `backend/app/tests/unit/test_chart_json_builder.py` - projection publique.
- `backend/app/tests/unit/test_chart_result_service.py` - persistance payload via `chart_results.result_payload` si déjà couverte pour CS-192.
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - runtime des facteurs de dominance.
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` - garde anti-import, anti-poids local, anti-narration.
- `backend/app/tests/integration/test_reference_data_migrations.py` - schema/migration.

Files not expected to change:

- `frontend/**` - aucune UI ou type frontend dans cette story.
- `backend/app/domain/astrology/dignities/**` - aucun recalcul de dignités.
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py` - ne pas modifier la logique CS-192.
- `backend/app/services/llm_generation/**` - aucun prompt ou adapter LLM dans cette story.
- `backend/app/domain/prediction/**` - aucun scoring prédictif ou réemploi daily.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/test_planet_dominance_engine.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py
pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py
pytest -q backend/app/tests/integration/test_reference_data_migrations.py
ruff format .
ruff check .
rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|from app\.services\.prediction" `
  backend/app/domain/astrology/dominance -g "*.py"
rg -n "OpenAI|AIEngineAdapter|chat\.completions|\bprompt\b|narration|micro_note" backend/app/domain/astrology/dominance -g "*.py"
rg -n "DOMINANCE_FACTORS|DOMINANCE_WEIGHTS|CHART_RULER_WEIGHT|ANGULARITY_WEIGHT|SIGN_RULERS|PLANET_RULERS" `
  backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"
rg -n "planet_dominance|PlanetDominance" `
  backend/app/services/chart/json_builder.py `
  backend/app/domain/astrology/natal_calculation.py `
  backend/app/domain/astrology/dominance -g "*.py"
```

Expected scan result:

- the first two `rg` commands return zero hits;
- the third `rg` command returns zero hits for hardcoded dominance maps;
- the fourth `rg` command shows only projection/integration sites, not local scoring in `json_builder.py`.

## 21. Regression Risks

- Risk: le moteur devient une interprétation narrative déguisée.
  - Guardrail: AC3, AC11 et scans anti-LLM/anti-narration limitent le résultat à des faits, scores et preuves.
- Risk: les facteurs ou poids sont codés localement.
  - Guardrail: AC1, AC2, AC5 et `RG-121` imposent la table DB/runtime.
- Risk: le serialiseur public recalcule la dominance.
  - Guardrail: AC10 exige une projection stricte depuis `NatalResult.planet_dominance`.
- Risk: `ChartSignatureCalculator` et `PlanetDominanceEngine` divergent en deux moteurs concurrents non documentés.
  - Guardrail: AC4, AC8 et les tâches de réutilisation imposent une classification et une source canonique.
- Risk: CS-193 n’est pas encore implémentée au moment du développement.
  - Guardrail: le dev agent doit stopper ou consigner une décision utilisateur avant de dupliquer les signaux conditionnels.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not add mutual reception, translation of light, collection of light,
  planetary war, advanced heliacal phases, predictive scoring, relationship
  compatibility, prompts, UI or interpretation adapter logic.
- Do not duplicate CS-193 signal logic if `condition_signals` is not available.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 23. References

- `backend/app/domain/astrology/condition/contracts.py` - source actuelle de `PlanetConditionProfile`.
- `backend/app/domain/astrology/interpretation/chart_signature.py` - dominance structurelle existante à classifier ou réutiliser.
- `backend/app/domain/astrology/interpretation/dominant_aspects.py` - évaluateur canonique des aspects dominants.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - propriétaire du contrat runtime à étendre.
- `backend/app/domain/astrology/natal_calculation.py` - propriétaire de `NatalResult`.
- `backend/app/services/chart/json_builder.py` - propriétaire de la projection JSON publique.
- `_condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md` - story précédente sur les profils conditionnels.
- `_condamad/stories/CS-193-planetary-condition-signals/00-story.md` - story voisine sur les signaux conditionnels.
- `_condamad/stories/regression-guardrails.md` - registre des invariants consulté et enrichi pour CS-194.
