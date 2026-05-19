# Story CS-196 interpretation-adapter-layer: Creer la couche d'adaptation interpretative

Status: done

## 1. Objective

Creer une couche backend pure `Interpretation Adapter Layer` qui transforme les
faits astrologiques deja calcules en signaux semantiques normalises, themes
actives, priorites narratives techniques et faits explicables consommables par
les futurs prompts. Cette couche ne genere aucun texte narratif, n'appelle aucun
LLM et ne fait aucun recalcul astrologique deja porte par les moteurs
`dignities`, `condition`, `advanced_conditions` ou `dominance`.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-19, `CS-196 — Interpretation Adapter Layer`.
- Reason for change: CS-191 a livre les dignites, CS-192 les profils
  conditionnels, CS-193 les signaux conditionnels, CS-194 les dominantes et
  CS-195 les conditions avancees; il manque une couche canonique
  `Astrological facts -> Interpretation-ready semantic signals` afin que les
  prompts, la narration, l'UI et les produits astrologiques ne recalculent pas
  implicitement des priorites divergentes.

## 2a. Sequencing / Blocking Dependencies

- Depends on: `CS-192-planetary-condition-profile-v1`, `CS-193-planetary-condition-signals`, `CS-194-dominant-planets-engine`, `CS-195-advanced-planetary-conditions`.
- Required precondition before implementation:
  - `_condamad/stories/story-status.md` marks `CS-192`, `CS-193`, `CS-194` and `CS-195` as `done`;
  - `backend/app/domain/astrology/natal_calculation.py::NatalResult` exposes
    `condition_profiles`, `condition_signals`, `advanced_conditions` and
    `dominant_planets`;
  - `backend/app/services/chart/json_builder.py` projects those facts without
    recalculating them.
- If any precondition is missing:
  - stop before editing application code;
  - record the blocker in
    `_condamad/stories/CS-196-interpretation-adapter-layer/evidence/interpretation-adapter-guard-evidence.md`;
  - do not duplicate CS-192, CS-193, CS-194 or CS-195 logic.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/interpretation_adapters`
- In scope:
  - creer les tables `astral_interpretation_signal_types`,
    `astral_interpretation_themes` et `astral_interpretation_adapter_rules`;
  - charger ces referentiels dans `AstrologyRuntimeReference` sous contrats
    immuables;
  - creer les contrats domaine `InterpretationSignal`,
    `InterpretationThemeActivation` et `InterpretationAdapterResult`;
  - creer `InterpretationAdapterEngine`, `SignalBuilder`,
    `ThemeAggregator` et `PriorityRanker`;
  - exposer les tensions, soutiens, axes psychologiques et axes fonctionnels
    sous forme de codes, categories et themes normalises, sans phrase
    interpretative;
  - consommer les faits presents dans `NatalResult.planets`,
    `NatalResult.aspects`, `NatalResult.dignities`,
    `NatalResult.condition_profiles`, `NatalResult.condition_signals`,
    `NatalResult.advanced_conditions` et `NatalResult.dominant_planets`;
  - integrer `interpretation_adapter` dans `NatalResult` et le JSON public;
  - ajouter tests, snapshots et gardes anti-regression.
- Out of scope:
  - generation de textes;
  - appel LLM, provider IA ou prompt assembly;
  - horoscope, prediction evenementielle ou matching amoureux;
  - personas d'astrologues;
  - HTML, UI frontend ou composants React;
  - modification des moteurs de dignites, profils, signaux, conditions
    avancees ou dominance.
- Explicit non-goals:
  - ne pas produire de phrase comme `Mars dominant vous rend impulsif`;
  - ne pas lire SQLAlchemy ou la DB depuis `interpretation_adapters/**`;
  - ne pas coder de regles de priorite, themes ou signaux hors runtime;
  - ne pas recalculer `condition_signals`, `advanced_conditions` ou
    `dominant_planets`;
  - ne pas mettre de logique d'adaptation dans `json_builder.py`;
  - ne pas contourner `RG-107`, `RG-108`, `RG-112`, `RG-118`, `RG-119`,
    `RG-120`, `RG-121` et `RG-122`.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story cree une couche domaine, trois referentiels
  DB/runtime, une extension de contrat natal et une projection JSON sans route
  API nouvelle; aucun archetype standard ne couvre exactement cette adaptation
  semantique non narrative.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `NatalResult` peut gagner `interpretation_adapter`;
  - le JSON public peut gagner `interpretation_adapter`;
  - les champs existants `dignities`, `planet_condition_profiles`,
    `planet_condition_signals`, `advanced_conditions`, `dominant_planets`,
    maisons, signes, aspects et points astraux ne doivent pas changer hors
    ajout documente;
  - les signaux interpretatifs doivent etre derives uniquement des faits natals
    deja construits et des regles runtime actives;
  - aucune route, methode HTTP ou status code n'est ajoute.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: une regle semantique attendue par le brief ne peut
  pas etre exprimee par `source_type`, `source_code`, `condition_json` et les
  faits natals existants; le dev agent doit bloquer au lieu d'inventer une
  heuristique locale.
- Additional validation rules:
  - prouver que chaque signal emis reference un `signal_code` runtime actif;
  - prouver que chaque theme active reference un `theme_code` runtime actif;
  - prouver que les tensions, soutiens, axes psychologiques et axes
    fonctionnels sont representes par les categories et themes runtime, pas par
    du texte narratif;
  - prouver que les priorites viennent de `priority_override` ou
    `priority_default`, et que leur ordre vient des rangs runtime associes,
    pas de mappings locaux;
  - prouver que le serialiseur projette `NatalResult.interpretation_adapter`
    sans calcul.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story
scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les signaux, themes, regles, poids et priorites doivent provenir des trois tables runtime. |
| Baseline Snapshot | yes | le payload natal et le JSON public gagnent un bloc; un avant/apres est requis pour prouver la stabilite de l'existant. |
| Ownership Routing | yes | la story touche infra DB, runtime domaine, moteur domaine, resultat natal et projection service. |
| Allowlist Exception | no | aucune exception, alias, fallback ou shim n'est autorise. |
| Contract Shape | yes | `InterpretationAdapterResult`, `NatalResult.interpretation_adapter` et le JSON `interpretation_adapter` ont une forme explicite. |
| Batch Migration | no | aucune migration par lots de consommateurs existants n'est effectuee. |
| Reintroduction Guard | yes | les regles locales, la narration, les imports DB/API/services et les recalculs du serialiseur doivent etre bloques. |
| Persistent Evidence | yes | les snapshots, rapports runtime et rapports de garde doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config: `AstrologyRuntimeReference.interpretation_adapter_reference`
    charge depuis `astral_interpretation_signal_types`,
    `astral_interpretation_themes` et `astral_interpretation_adapter_rules`.
- Secondary evidence:
  - migration/schema inspection, tests repository/runtime reference, tests du
    moteur adapter, snapshots de payload et scans cibles anti-import,
    anti-regle locale et anti-narration.
- Static scans alone are not sufficient for this story because:
  - le risque principal est une priorisation ou un mapping semantique encode
    localement; il faut donc executer le chargement runtime et valider les
    lignes actives.

### 4b.1 Interpretation Signal Type Seed Contract

`astral_interpretation_signal_types` must seed exactly these active v1 rows for
the default reference version. The dev agent must not add extra active signal
types unless the story is explicitly amended.

`priority_default_rank` is the runtime ordering source for
`priority_default`; lower values are more important. The domain ranker must use
this runtime value and must not define a local priority order.

| code | label | category | theme_code | description | priority_default | priority_default_rank | is_active | sort_order |
|---|---|---|---|---|---|---:|---:|---:|
| `dominant_mars_signature` | Dominant Mars Signature | planetary_signature | `drive_assertion_action` | Dominance martienne structurante. | `critical` | 10 | true | 1 |
| `high_externalization` | High Externalization | expression_pattern | `visibility_expression` | Signal de forte exteriorisation de l'energie planetaire. | `high` | 20 | true | 2 |
| `constraint_on_action` | Constraint On Action | tension_pattern | `frustration_pressure` | Signal de contrainte ou de pression sur l'action. | `medium` | 30 | true | 3 |
| `structural_endurance` | Structural Endurance | planetary_signature | `responsibility_structure` | Signal de persistance structurelle liee a Saturne. | `high` | 20 | true | 4 |

Allowed priorities are exactly:

- `critical`
- `high`
- `medium`
- `low`
- `background`

### 4b.2 Interpretation Theme Seed Contract

`astral_interpretation_themes` must seed exactly these active v1 rows. The dev
agent must not add extra active themes unless the story is explicitly amended.

Theme categories are the v1 representation of the brief's psychological and
functional axes:

- `behavioral` and `expression` carry psychological/expression axes.
- `tension` carries pressure or conflict axes.
- `functional` carries support, structure or stabilisation axes.

| code | label | category | description | is_active |
|---|---|---|---|---:|
| `drive_assertion_action` | Drive / Assertion / Action | behavioral | Thematique liee a l'action, l'affirmation et l'impulsion. | true |
| `visibility_expression` | Visibility / Expression | expression | Thematique liee a l'expression visible et exterieure. | true |
| `frustration_pressure` | Frustration / Pressure | tension | Thematique de tension, pression ou limitation. | true |
| `responsibility_structure` | Responsibility / Structure | functional | Thematique de responsabilite, stabilite et structuration. | true |

### 4b.3 Interpretation Adapter Rule Seed Contract

`astral_interpretation_adapter_rules` must seed exactly these active v1 rows.
`condition_json` is parsed in infra and converted to a typed runtime condition;
the domain must not receive free-form mutable dictionaries.

`priority_override_rank`, when present, is the runtime ordering source for
`priority_override`; lower values are more important. When a rule has no
override, the emitted signal uses the active signal type
`priority_default_rank`.

For the `compound` source `saturn_stability`, `source_code` identifies the
Saturn dominance requirement and `condition_json.min` identifies the minimum
stability threshold.

| code | source_type | source_code | condition_json | signal_code | priority_override | priority_override_rank | weight | is_active | reference_version_code |
|---|---|---|---|---|---|---:|---:|---:|---|
| `dominant_mars_to_signature` | `dominant_planet` | `mars` | `{"dominance_level":"dominant"}` | `dominant_mars_signature` | `critical` | 10 | 1.0 | true | `v1` |
| `high_visibility_to_externalization` | `condition_axis` | `visibility` | `{"min":0.7}` | `high_externalization` | `high` | 20 | 0.8 | true | `v1` |
| `constraint_to_action_pressure` | `condition_axis` | `constraint` | `{"min":0.6}` | `constraint_on_action` | `medium` | 30 | 0.7 | true | `v1` |
| `saturn_stability_to_endurance` | `compound` | `saturn_stability` | `{"min":0.7}` | `structural_endurance` | `high` | 20 | 0.9 | true | `v1` |

Supported `source_type` values for v1 are exactly:

- `dominant_planet`
- `condition_axis`
- `condition_signal`
- `advanced_condition`
- `compound`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-196-interpretation-adapter-layer/evidence/interpretation-adapter-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-196-interpretation-adapter-layer/evidence/interpretation-adapter-after.json`
- Expected invariant:
  - tous les champs natals et chart JSON existants restent presents et
    compatibles; seul `interpretation_adapter` est ajoute au resultat natal et
    au JSON public.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Tables, migrations et modeles SQLAlchemy des referentiels d'adaptation | `backend/migrations/**`, `backend/app/infra/db/models/**` | `backend/app/domain/**` |
| Chargement SQLAlchemy des referentiels d'adaptation | `backend/app/infra/db/repositories/**` | `backend/app/domain/**` |
| Contrats runtime des signaux, themes et regles | `backend/app/domain/astrology/runtime/runtime_reference.py` | `backend/app/services/**` |
| Adaptation semantique pure | `backend/app/domain/astrology/interpretation_adapters/**` | `backend/app/api/**`, `backend/app/services/**`, `backend/app/domain/prediction/**` |
| Integration du resultat natal | `backend/app/domain/astrology/natal_calculation.py` | routeurs API |
| Projection JSON publique | `backend/app/services/chart/json_builder.py` | calculateurs domaine |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - DTO domaine et payload `NatalResult.interpretation_adapter` /
    `interpretation_adapter`.
- Fields:
  - `signals: array` liste triee de signaux interpretatifs.
  - `signals[].signal_code: string` code issu de
    `astral_interpretation_signal_types`.
  - `signals[].theme_code: string` theme issu du signal type.
  - `signals[].source_type: string` type de fait source.
  - `signals[].source_code: string` code source, par exemple `mars` ou
    `visibility`.
  - `signals[].priority: string` priorite stable parmi les cinq valeurs v1.
  - `signals[].priority_rank: number` rang runtime de tri; plus la valeur est
    basse, plus la priorite est forte.
  - `signals[].weight: number` poids de la regle runtime.
  - `signals[].semantic_category: string` categorie runtime du signal, par
    exemple `planetary_signature`, `expression_pattern` ou `tension_pattern`.
  - `signals[].theme_category: string` categorie runtime du theme, par exemple
    `behavioral`, `expression`, `tension` ou `functional`.
  - `signals[].explanation_fact: string` fait court non narratif expliquant le
    match, par exemple `dominant_planet:mars:rank=1`.
  - `activated_themes: array` themes agreges.
  - `activated_themes[].theme_code: string` code theme actif.
  - `activated_themes[].theme_category: string` categorie runtime du theme.
  - `activated_themes[].activation_score: number` score normalise entre `0.0`
    et `1.0`.
  - `activated_themes[].priority: string` priorite maximum des signaux
    contributeurs.
  - `activated_themes[].priority_rank: number` meilleur rang runtime des
    signaux contributeurs.
  - `activated_themes[].contributing_signals: array[string]` codes des signaux
    contributeurs.
  - `dominant_topics: array[string]` themes principaux tries par score puis code.
  - `dominant_axes: array[string]` categories de themes principales triees par
    activation, pour exposer les axes psychologiques et fonctionnels sans texte.
  - `tension_patterns: array[string]` signaux rattaches a un theme de categorie
    `tension`.
  - `support_patterns: array[string]` signaux rattaches a un theme de categorie
    `functional`.
  - `critical_patterns: array[string]` signaux de priorite `critical`.
  - `narrative_priorities: array[string]` codes de signaux ou themes a consommer
    par la future couche narrative, sans texte.
- Required fields:
  - tous les champs listes ci-dessus sont requis dans le contrat v1.
- Optional fields:
  - `NatalResult.interpretation_adapter` peut etre `None` uniquement en mode
    degrade sans temps si la dominance factuelle n'est pas calculee; sinon le
    moteur doit retourner un `InterpretationAdapterResult` avec tuples vides
    quand aucune regle ne matche.
- Status codes:
  - aucune route API nouvelle n'est creee et aucun status code n'est modifie.
- Serialization names:
  - `NatalResult.interpretation_adapter` reste `interpretation_adapter`.
  - le JSON public expose `interpretation_adapter`.
  - le JSON public serialise `signal_code` sous le nom court `signal` et
    `theme_code` sous le nom court `theme` dans `signals` et
    `activated_themes`.
- Frontend type impact:
  - aucun fichier frontend n'est modifie dans cette story; le champ public est
    prepare pour consommation future.
- Generated contract impact:
  - OpenAPI ne doit changer que si le payload natal est deja modelise par schema
    genere; dans ce cas le snapshot doit documenter uniquement l'ajout
    `interpretation_adapter`.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: no old surface is migrated in batches; the story adds one adapter
  layer and preserves existing factual surfaces.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Snapshot avant | `_condamad/stories/CS-196-interpretation-adapter-layer/evidence/interpretation-adapter-before.json` | Etat du payload avant ajout. |
| Snapshot apres | `_condamad/stories/CS-196-interpretation-adapter-layer/evidence/interpretation-adapter-after.json` | Ajout exact de `interpretation_adapter`. |
| Rapport runtime | `_condamad/stories/CS-196-interpretation-adapter-layer/evidence/interpretation-adapter-runtime-reference.md` | Lignes runtime chargees. |
| Rapport gardes | `_condamad/stories/CS-196-interpretation-adapter-layer/evidence/interpretation-adapter-guard-evidence.md` | Scans anti-drift. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- loaded runtime reference inventory;
- AST import graph when the existing guard pattern supports it;
- targeted forbidden symbol scans.

Required forbidden examples:

- `from app.infra` dans `backend/app/domain/astrology/interpretation_adapters/**`
- `Session`, `select(` ou modeles SQLAlchemy dans
  `backend/app/domain/astrology/interpretation_adapters/**`
- mappings locaux comme `INTERPRETATION_RULES`, `SIGNAL_TYPES`,
  `THEME_CODES`, `PRIORITY_ORDER`, `ADAPTER_RULES`,
  `DOMINANT_MARS_SIGNATURE`, `HIGH_EXTERNALIZATION_THRESHOLD` ou equivalent
  non derive du runtime
- imports ou symboles `AIEngineAdapter`, `OpenAI`, `chat.completions`,
  `prompt`, `narration`, `persona`, `horoscope`, `matching`,
  `app.domain.prediction`, `app.services.prediction`
- calcul de `interpretation_adapter` dans `json_builder.py`

Guard evidence:

- Evidence profile: `reintroduction_guard`;
  `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` ou un test
  de garde voisin verifie les imports, mappings locaux, symboles interdits et
  projection du serialiseur.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/astrology/condition/contracts.py` -
  `PlanetConditionProfile`, `PlanetConditionSignal` et
  `PlanetConditionSignalSet` existent deja comme faits conditionnels et signaux
  techniques non narratifs.
- Evidence 2: `backend/app/domain/astrology/dominance/contracts.py` -
  `DominantPlanetsResult` expose un classement factuel avec rangs, niveaux,
  facteurs et faits explicables.
- Evidence 3: `backend/app/domain/astrology/advanced_conditions/contracts.py` -
  `AdvancedPlanetaryCondition` expose des conditions avancees factuelles avec
  impacts d'axes et `ranking_weight`.
- Evidence 4: `backend/app/domain/astrology/runtime/runtime_reference.py` -
  `AstrologyRuntimeReference` transporte deja les referentiels de signaux
  conditionnels, dominance et conditions avancees sous contrats immuables.
- Evidence 5: `backend/app/domain/astrology/natal_calculation.py` -
  `NatalResult` integre deja `dignities`, `condition_profiles`,
  `condition_signals`, `advanced_conditions` et `dominant_planets`.
- Evidence 6: `backend/app/services/chart/json_builder.py` - le JSON public
  projette deja `planet_condition_profiles`, `planet_condition_signals`,
  `advanced_conditions` et `dominant_planets` depuis `NatalResult`.
- Evidence 7: `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md` -
  CS-195 exclut explicitement les prompts, LLM et adapter d'interpretation, ce
  qui laisse CS-196 comme couche suivante.
- Evidence 8: `_condamad/stories/story-status.md` - `CS-192`, `CS-193`,
  `CS-194` et `CS-195` sont marques `done` au moment de la redaction.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - invariants de
  regression consultes avant finalisation du perimetre de la story.

## 6. Target State

After implementation:

- Les trois tables d'adaptation interpretative existent avec contraintes de
  code, version, activite et integrite theme/signal/regle.
- `AstrologyRuntimeReference` expose les signaux, themes et regles
  d'adaptation sous contrat immuable et tri deterministe.
- `InterpretationAdapterEngine` produit des `InterpretationSignal`
  deterministes a partir des faits natals et des regles runtime.
- `ThemeAggregator` regroupe les signaux par theme avec score d'activation et
  priorite stable.
- `ThemeAggregator` expose aussi les axes dominants, tensions et soutiens sous
  forme de codes et categories runtime.
- `PriorityRanker` applique les rangs runtime de priorite, qui encodent l'ordre
  `critical > high > medium > low > background`, sans mapping local concurrent.
- `NatalResult.interpretation_adapter` expose le resultat sans modifier les
  faits existants.
- `build_chart_json` expose `interpretation_adapter` comme projection stricte,
  sans recalculer ni prioriser.
- Aucun texte narratif, prompt, LLM, persona, horoscope ou logique UI n'est
  introduit.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-107` - les donnees astrologiques runtime doivent rester typees et les JSON DB confines a l'infra.
  - `RG-108` - le vocabulaire DB-backed des signaux, themes et regles ne doit pas etre recree en constantes locales.
  - `RG-112` - les constantes metier astrologiques et fallbacks legacy ne doivent pas revenir.
  - `RG-118` - le moteur de dignites reste factuel et ne doit pas etre relu par une interpretation narrative.
  - `RG-119` - les profils conditionnels restent une couche derivee, pas un second moteur expert dans l'adapter.
  - `RG-120` - les signaux conditionnels doivent rester gouvernes par runtime et etre consommes, pas reconstruits.
  - `RG-121` - les dominantes planetaires doivent rester produites par `PlanetDominanceEngine`.
  - `RG-122` - les conditions avancees doivent rester produites par `AdvancedConditionEngine`.
  - `RG-123` - cette story etablit `InterpretationAdapterEngine` comme couche canonique non narrative d'adaptation semantique.
- Non-applicable invariants:
  - `RG-117` - cette story ne touche pas le scoring des etoiles fixes daily.
- Required regression evidence:
  - tests unitaires des builders/rankers/aggregators, tests runtime repository,
    tests payload, snapshot avant/apres, scan anti-import DB, scan anti-regle
    locale, scan anti-LLM et scan anti-narration.
- Allowed differences:
  - ajout des trois tables `astral_interpretation_*`, ajout du runtime associe,
    ajout de `interpretation_adapter` dans `NatalResult` et dans le JSON public.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les trois tables `astral_interpretation_*` existent avec seeds v1 actifs. | `pytest -q --long backend/app/tests/integration/test_reference_data_migrations.py` + rapport runtime. |
| AC2 | Le runtime expose `interpretation_adapter_reference` sous contrat immuable. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC3 | `SignalBuilder` emet des `InterpretationSignal` deterministes depuis les faits natals. | `pytest -q backend/tests/unit/domain/astrology/test_signal_builder.py`. |
| AC4 | `PriorityRanker` applique les rangs runtime v1 sans constante metier concurrente. | `pytest -q backend/tests/unit/domain/astrology/test_priority_ranker.py`. |
| AC5 | `ThemeAggregator` calcule `activation_score` par theme actif. | `pytest -q backend/tests/unit/domain/astrology/test_theme_aggregator.py`. |
| AC6 | `InterpretationAdapterEngine` ne produit aucun texte narratif. | `pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py`. |
| AC7 | `NatalResult` expose `interpretation_adapter` apres `dominant_planets`. | `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`. |
| AC8 | Le JSON public expose `interpretation_adapter` comme projection stricte. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py`. |
| AC9 | Le chart payload persiste `interpretation_adapter` quand le JSON public est persiste. | `pytest -q backend/app/tests/unit/test_chart_result_service.py`. |
| AC10 | La garde `RG-123` bloque les mappings locaux d'adaptation. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py`. |
| AC11 | Le contrat expose les axes psychologiques sous codes runtime. | `pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py`. |
| AC12 | Le contrat expose les axes fonctionnels sous codes runtime. | `pytest -q backend/tests/unit/domain/astrology/test_theme_aggregator.py`. |
| AC13 | Le contrat expose les tensions sans texte narratif. | `pytest -q backend/tests/unit/domain/astrology/test_theme_aggregator.py`. |
| AC14 | Le contrat expose les soutiens sans texte narratif. | `pytest -q backend/tests/unit/domain/astrology/test_theme_aggregator.py`. |
| AC15 | Le contrat public reste stable hors ajouts autorises. | Evidence profile: `baseline_before_after_diff`; `ruff check .` + comparaison des snapshots evidence. |

## 8. Implementation Tasks

- [x] Task 1 - Ajouter les referentiels DB/runtime d'adaptation (AC: AC1, AC2)
  - [x] Subtask 1.1 - Ajouter une migration Alembic pour les trois tables `astral_interpretation_*`.
  - [x] Subtask 1.2 - Ajouter les modeles SQLAlchemy infra et les exporter via `backend/app/infra/db/models/__init__.py`.
  - [x] Subtask 1.3 - Seeder les lignes de `4b.1`, `4b.2` et `4b.3`.
  - [x] Subtask 1.4 - Mapper les lignes vers des contrats runtime immuables dans `AstrologyRuntimeReference`.

- [x] Task 2 - Creer les contrats et composants domaine (AC: AC3, AC4, AC5, AC6)
  - [x] Subtask 2.1 - Creer `backend/app/domain/astrology/interpretation_adapters/contracts.py`.
  - [x] Subtask 2.2 - Creer `signal_builder.py` pour appliquer les regles runtime aux faits natals.
  - [x] Subtask 2.3 - Creer `priority_ranker.py` pour trier signaux, themes et priorites.
  - [x] Subtask 2.4 - Creer `theme_aggregator.py` pour produire les activations de themes.
  - [x] Subtask 2.5 - Creer `interpretation_adapter_engine.py` comme orchestrateur pur.
  - [x] Subtask 2.6 - Exporter explicitement les surfaces publiques depuis `interpretation_adapters/__init__.py`.

- [x] Task 3 - Integrer l'adapter au resultat natal et au JSON public (AC: AC7, AC8, AC9, AC11, AC12, AC13, AC14, AC15)
  - [x] Subtask 3.1 - Ajouter `interpretation_adapter` a `NatalResult`.
  - [x] Subtask 3.2 - Construire l'adapter apres `dominant_planets` dans `build_natal_result`.
  - [x] Subtask 3.3 - Ajouter `_serialize_interpretation_adapter` dans `json_builder.py` comme projection stricte.
  - [x] Subtask 3.4 - Verifier la persistance du payload via les tests du chart result service.

- [x] Task 4 - Ajouter tests, preuves et gardes (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15)
  - [x] Subtask 4.1 - Ajouter les tests unitaires des composants adapter.
  - [x] Subtask 4.2 - Etendre les tests runtime reference, contrat natal, chart JSON et chart result service.
  - [x] Subtask 4.3 - Mettre a jour la garde d'architecture runtime avec les symboles interdits CS-196.
  - [x] Subtask 4.4 - Produire les artefacts evidence dans le dossier de story.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetConditionProfile` pour les axes conditionnels.
  - `PlanetConditionSignalSet` pour les signaux conditionnels deja gouvernes.
  - `AdvancedPlanetaryCondition` pour les conditions avancees deja detectees.
  - `DominantPlanetsResult` pour les dominances, rangs et niveaux.
  - `AstrologyRuntimeReference` comme source unique des regles, themes,
    signaux et priorites.
  - `build_chart_json` comme unique serialiseur public du theme natal.
- Do not recreate:
  - un nouveau moteur de dignites;
  - un nouveau moteur de profils conditionnels;
  - un nouveau builder de signaux conditionnels;
  - un nouveau moteur de dominance;
  - un nouveau moteur de conditions avancees;
  - des mappings locaux de themes, signaux, priorites, seuils ou regles;
  - une narration, un prompt ou un assembleur LLM.
- Shared abstraction allowed only if:
  - elle remplace une duplication observee entre `SignalBuilder`,
    `ThemeAggregator` et `PriorityRanker`;
  - elle reste sous `backend/app/domain/astrology/interpretation_adapters`;
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

- `backend/app/domain/astrology/interpretation_adapters/**` qui importent
  `app.infra`, `app.api`, `app.services`, `app.domain.prediction` ou
  `app.services.prediction`.
- `backend/app/domain/astrology/interpretation_adapters/**` contenant
  `Session`, `select(`, `OpenAI`, `AIEngineAdapter`, `chat.completions`,
  le mot exact `prompt`, `narration`, `persona`, `horoscope`, `matching` ou
  texte editorial de restitution.
- `INTERPRETATION_RULES`, `SIGNAL_TYPES`, `THEME_CODES`, `PRIORITY_ORDER`,
  `ADAPTER_RULES`, `DOMINANT_MARS_SIGNATURE`,
  `HIGH_EXTERNALIZATION_THRESHOLD`, `CONSTRAINT_ON_ACTION_THRESHOLD` ou mapping
  equivalent non derive du runtime.
- Recalcul de `interpretation_adapter`, `condition_signals`,
  `advanced_conditions` ou `dominant_planets` dans
  `backend/app/services/chart/json_builder.py`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Referentiels d'adaptation interpretative | `backend/app/infra/db/models/**`, `backend/app/infra/db/repositories/**` | `backend/app/domain/**` |
| Contrats runtime d'adaptation | `backend/app/domain/astrology/runtime/runtime_reference.py` | `backend/app/services/**`, `backend/app/api/**` |
| Adaptation semantique non narrative | `backend/app/domain/astrology/interpretation_adapters/**` | serialiseurs, prediction, prompts LLM, UI |
| Payload natal objectif enrichi | `backend/app/domain/astrology/natal_calculation.py` | routeurs API |
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
  document that only `interpretation_adapter` is added.
- If OpenAPI does not model the dynamic chart JSON shape, record that fact in
  `_condamad/stories/CS-196-interpretation-adapter-layer/evidence/interpretation-adapter-guard-evidence.md`.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/condition/contracts.py`
- `backend/app/domain/astrology/condition/planet_condition_signal_builder.py`
- `backend/app/domain/astrology/dominance/contracts.py`
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py`
- `backend/app/domain/astrology/advanced_conditions/contracts.py`
- `backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `_condamad/stories/regression-guardrails.md`

## 18. Expected Files to Modify

Likely files:

- `backend/migrations/versions/*.py` - ajouter les trois tables referentielles d'adaptation.
- `backend/app/infra/db/models/dignity_reference.py` ou `backend/app/infra/db/models/reference.py` - ajouter les modeles SQLAlchemy selon l'owner de referentiels existant.
- `backend/app/infra/db/models/__init__.py` - exporter les nouveaux modeles pour `Base.metadata`.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - ajouter les contrats runtime d'adaptation.
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - charger et valider les referentiels d'adaptation.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - mapper les lignes vers le runtime.
- `backend/app/domain/astrology/interpretation_adapters/contracts.py` - nouveaux contrats domaine.
- `backend/app/domain/astrology/interpretation_adapters/interpretation_adapter_engine.py` - orchestration pure.
- `backend/app/domain/astrology/interpretation_adapters/signal_builder.py` - construction des signaux interpretatifs.
- `backend/app/domain/astrology/interpretation_adapters/theme_aggregator.py` - aggregation des themes.
- `backend/app/domain/astrology/interpretation_adapters/priority_ranker.py` - priorisation deterministe.
- `backend/app/domain/astrology/interpretation_adapters/__init__.py` - exports explicites.
- `backend/app/domain/astrology/natal_calculation.py` - integrer `interpretation_adapter`.
- `backend/app/services/chart/json_builder.py` - exposer `interpretation_adapter`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py` - orchestration, absence narration et determinisme.
- `backend/tests/unit/domain/astrology/test_signal_builder.py` - mappings dominance, axes, signaux conditionnels et conditions avancees.
- `backend/tests/unit/domain/astrology/test_theme_aggregator.py` - scores d'activation, contributeurs, priorite.
- `backend/tests/unit/domain/astrology/test_priority_ranker.py` - ordre stable et tie-breaks.
- `backend/tests/unit/domain/astrology/test_interpretation_adapter_result.py` - contrat tensions, soutiens et axes.
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py` - contrat `NatalResult`.
- `backend/app/tests/unit/test_chart_json_builder.py` - projection publique.
- `backend/app/tests/unit/test_chart_result_service.py` - persistance payload.
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - runtime d'adaptation.
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` - garde anti-import, anti-regle locale, anti-narration.
- `backend/app/tests/integration/test_reference_data_migrations.py` - schema/migration.

Files not expected to change:

- `frontend/**` - aucune UI ou type frontend dans cette story.
- `backend/app/domain/astrology/dignities/**` - aucun recalcul de dignites.
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py` - aucun changement du profil conditionnel.
- `backend/app/domain/astrology/condition/planet_condition_signal_builder.py` -
  aucun remplacement des signaux conditionnels; adaptation minimale seulement
  si un contrat existant doit etre expose sans changer sa logique.
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py` - aucun remplacement du moteur de dominance.
- `backend/app/domain/astrology/advanced_conditions/**` - aucun nouveau calcul avance.
- `backend/app/services/llm_generation/**` - aucun prompt, adapter LLM ou narration.
- `backend/app/domain/prediction/**` - aucun scoring predictif ou daily.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/test_signal_builder.py
pytest -q backend/tests/unit/domain/astrology/test_theme_aggregator.py
pytest -q backend/tests/unit/domain/astrology/test_priority_ranker.py
pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_engine.py
pytest -q backend/tests/unit/domain/astrology/test_interpretation_adapter_result.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py
pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py
pytest -q backend/app/tests/integration/test_reference_data_migrations.py
ruff format .
ruff check .
rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|from app\.services\.prediction" `
  backend/app/domain/astrology/interpretation_adapters -g "*.py"
rg -n "OpenAI|AIEngineAdapter|chat\.completions|\bprompt\b|narration|persona|horoscope|matching" `
  backend/app/domain/astrology/interpretation_adapters -g "*.py"
rg -n "INTERPRETATION_RULES|SIGNAL_TYPES|THEME_CODES|PRIORITY_ORDER|ADAPTER_RULES|DOMINANT_MARS_SIGNATURE|HIGH_EXTERNALIZATION_THRESHOLD|CONSTRAINT_ON_ACTION_THRESHOLD" `
  backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"
rg -n "interpretation_adapter|InterpretationAdapter|InterpretationSignal|InterpretationThemeActivation" `
  backend/app/services/chart/json_builder.py `
  backend/app/domain/astrology/natal_calculation.py `
  backend/app/domain/astrology/interpretation_adapters -g "*.py"
```

Expected scan result:

- the first two `rg` commands return zero hits;
- the third `rg` command returns zero hits for hardcoded adapter maps outside
  tests or runtime guard fixtures explicitly justified in evidence;
- the fourth `rg` command shows only projection, integration and domain adapter
  sites, not local calculation in `json_builder.py`.

## 21. Regression Risks

- Risk: l'adapter devient une narration deguisee.
  - Guardrail: AC6, AC10 et scans anti-LLM/anti-narration limitent le resultat
    a des codes, themes, priorites, poids et faits courts.
- Risk: les regles semantiques ou priorites sont codees localement.
  - Guardrail: AC1, AC2, AC4 et `RG-123` imposent les tables DB/runtime.
- Risk: le serialiseur recalcule les signaux ou themes.
  - Guardrail: AC8 et AC10 exigent une projection stricte depuis `NatalResult`.
- Risk: l'adapter duplique les moteurs CS-192 a CS-195.
  - Guardrail: AC3, AC6 et les contraintes DRY imposent la consommation des
    faits existants.
- Risk: un futur prompt recommence a relire les faits bruts et diverge.
  - Guardrail: le payload `interpretation_adapter` expose les priorites
    techniques et les themes actives comme contrat public stable.
- Risk: les tensions, soutiens et axes restent implicites et sont reconstruits
  plus tard par les prompts.
  - Guardrail: AC11 a AC14 imposent leur exposition sous codes et categories
    runtime, sans texte narratif.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not add frontend, prompts, LLM, prediction, compatibility relationnelle,
  horoscopes, personas or editorial interpretation logic.
- Do not duplicate CS-192, CS-193, CS-194 or CS-195 logic when a canonical
  result is already available.
- Keep CS-196 as preparation for `CS-197 Narrative Context Builder`,
  `CS-198 LLM Interpretation Runtime`, `CS-199 Astrologer Personas` and
  `CS-200 Narrative Composition Engine`; do not implement those future stories
  here.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 23. References

- `backend/app/domain/astrology/condition/contracts.py` - source actuelle des profils et signaux conditionnels.
- `backend/app/domain/astrology/dominance/contracts.py` - source actuelle des dominantes planetaires factuelles.
- `backend/app/domain/astrology/advanced_conditions/contracts.py` - source actuelle des conditions avancees factuelles.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - proprietaire du runtime a etendre.
- `backend/app/domain/astrology/natal_calculation.py` - proprietaire de `NatalResult` et de l'orchestration natale.
- `backend/app/services/chart/json_builder.py` - proprietaire de la projection JSON publique.
- `_condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md` - couche conditionnelle source.
- `_condamad/stories/CS-193-planetary-condition-signals/00-story.md` - couche de signaux conditionnels a consommer.
- `_condamad/stories/CS-194-dominant-planets-engine/00-story.md` - moteur de dominance a consommer.
- `_condamad/stories/CS-195-advanced-planetary-conditions/00-story.md` - conditions avancees a consommer.
- `_condamad/stories/regression-guardrails.md` - registre des invariants consulte et a enrichir pour CS-196.
