# Story CS-195 advanced-planetary-conditions: Ajouter les conditions planetaires avancees

Status: done

## 1. Objective

Etendre le moteur backend de condition planetaire avec des conditions
astrologiques avancees traditionnelles et structurelles, calculees
dynamiquement puis integrees aux `PlanetConditionProfile`, aux signaux
conditionnels, a la dominance planetaire et au JSON public. Le resultat doit
rester factuel, deterministe, explicable, versionne et sans narration.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-19, `CS-195 — Advanced Planetary Conditions`.
- Reason for change: CS-191 a livre les dignites, CS-192 les profils
  conditionnels, CS-193 les signaux conditionnels et CS-194 la dominance; il
  manque maintenant les conditions avancees majeures qui modulent la condition
  reelle d'une planete sans produire d'interpretation.

## 2b. Post-review correction note

- Correction date: 2026-05-19.
- Brief compliance review found three gaps after initial closure:
  - aspect conditions had to be detected from configured aspects, runtime
    planet natures and longitudinal enclosure, not only from synthetic
    accidental dignity facts;
  - heliacal phase conditions had to be derived from governed heliacal
    accidental facts, not from a local half-circle heuristic;
  - `astral_advanced_condition_types` had to keep the brief-level
    `description` field for explainable reference data.
- These corrections are now in scope for final CS-195 closure and are tracked
  in `generated/11-code-review.md` and `generated/10-final-evidence.md`.

## 2a. Sequencing / Blocking Dependencies

- Depends on: `CS-192-planetary-condition-profile-v1`, `CS-193-planetary-condition-signals`, `CS-194-dominant-planets-engine`.
- Required precondition before implementation:
  - `_condamad/stories/story-status.md` marks `CS-192`, `CS-193` and `CS-194` as `done`;
  - `backend/app/domain/astrology/natal_calculation.py::NatalResult` exposes
    `condition_profiles`, `condition_signals` and `dominant_planets`;
  - `backend/app/services/chart/json_builder.py` projects
    `planet_condition_profiles`, `planet_condition_signals` and
    `dominant_planets` from `NatalResult`.
- If any precondition is missing:
  - stop before editing application code;
  - record the blocker in
    `_condamad/stories/CS-195-advanced-planetary-conditions/evidence/advanced-condition-guard-evidence.md`;
  - do not duplicate CS-192, CS-193 or CS-194 logic.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/advanced_conditions`
- In scope:
  - creer les referentiels DB `astral_advanced_condition_types`,
    `astral_advanced_condition_score_profiles` et
    `astral_advanced_condition_weights`;
  - charger ces referentiels dans `AstrologyRuntimeReference` sous contrats
    immuables;
  - creer les contrats domaine `AdvancedPlanetaryCondition` et
    `PlanetConditionAxisImpact`;
  - creer les calculateurs purs `mutual_reception_calculator.py`,
    `hayz_calculator.py`, `planet_speed_classifier.py`,
    `heliacal_condition_calculator.py`, `aspect_condition_detector.py` et
    `advanced_condition_engine.py`;
  - enrichir `PlanetConditionProfile.breakdown` et
    `PlanetConditionProfile.explanation_facts` sans remplacer le profil;
  - exposer les conditions avancees dans `NatalResult` et dans le JSON public
    sous `advanced_conditions`;
  - faire contribuer les conditions avancees a `PlanetDominanceResult` via le
    moteur de scoring et les poids `ranking_weight`;
  - ajouter tests, snapshots et gardes anti-regression.
- Out of scope:
  - texte interpretatif ou narration editoriale;
  - prompts LLM, moteur d'IA ou adapter d'interpretation;
  - horoscopes, predictions evenementielles et compatibilite relationnelle;
  - translation of light, collection of light, planetary war, antiscia,
    contra-antiscia, primary directions, zodiacal releasing, firdaria et annual
    profections;
  - modification des calculateurs de positions astronomiques ou de SwissEph;
  - frontend et affichage UI.
- Explicit non-goals:
  - ne pas recalculer les dignites CS-191;
  - ne pas remplacer `PlanetConditionProfile` CS-192;
  - ne pas dupliquer les signaux CS-193;
  - ne pas creer un second moteur de dominance concurrent a CS-194;
  - ne pas lire SQLAlchemy ou la DB depuis `advanced_conditions/**`;
  - ne pas coder de logique produit, prompt, LLM, prediction ou UI;
  - ne pas contourner `RG-107`, `RG-108`, `RG-112`, `RG-115`, `RG-116`,
    `RG-118`, `RG-119`, `RG-120` et `RG-121`.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story cree un moteur domaine, trois referentiels
  DB/runtime, une extension de contrats natals et une projection JSON sans route
  API nouvelle; aucun archetype standard ne couvre exactement ce flux avance.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `NatalResult` peut gagner `advanced_conditions`;
  - le JSON public peut gagner `advanced_conditions`;
  - `PlanetConditionProfile.breakdown` peut recevoir des items de famille
    avancee et `PlanetConditionProfile.explanation_facts` peut recevoir des
    faits courts avances;
  - `PlanetConditionSignalBuilder` peut consommer les profils enrichis, mais ne
    doit pas recalculer les conditions avancees;
  - `PlanetDominanceEngine` peut prendre en compte les impacts avances via
    `ranking_weight`;
  - les champs existants `dignities`, `planet_condition_profiles`,
    `planet_condition_signals`, `dominant_planets`, maisons, signes, aspects et
    points astraux ne doivent pas changer hors ajouts documentes;
  - aucune route, methode HTTP ou status code n'est ajoute.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: une condition du brief exige une regle
  astrologique non representable avec les faits natals existants, les
  referentiels deja presents ou les trois nouveaux referentiels; le dev agent
  doit bloquer au lieu d'inventer une heuristique produit.
- Additional validation rules:
  - prouver que chaque condition avancee produite est rattachee a un type runtime actif;
  - prouver que les impacts d'axes viennent des poids runtime ou des valeurs
    par defaut des types, pas de constantes locales;
  - prouver que les calculateurs sont purs et sans dependance DB/API/services;
  - prouver que le serialiseur projette `NatalResult.advanced_conditions` sans calcul.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story
scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les types, profils et poids des conditions avancees doivent provenir des trois tables runtime. |
| Baseline Snapshot | yes | le payload natal et le JSON public gagnent un bloc et les profils/signaux/dominance peuvent etre enrichis. |
| Ownership Routing | yes | la story touche infra DB, runtime domaine, calculateurs domaine, resultat natal, dominance et projection service. |
| Allowlist Exception | no | aucune exception, alias, fallback ou shim n'est autorise. |
| Contract Shape | yes | `AdvancedPlanetaryCondition`, `NatalResult.advanced_conditions` et le JSON `advanced_conditions` ont une forme explicite. |
| Batch Migration | no | aucune migration par lots de consommateurs existants n'est effectuee. |
| Reintroduction Guard | yes | les imports DB/API/services, seuils locaux, narration et recalculs du serialiseur doivent etre bloques. |
| Persistent Evidence | yes | les snapshots, rapports runtime et rapports de garde doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config: `AstrologyRuntimeReference.advanced_condition_types`,
    `AstrologyRuntimeReference.advanced_condition_score_profiles` et
    `AstrologyRuntimeReference.advanced_condition_weights` charges depuis
    `astral_advanced_condition_types`,
    `astral_advanced_condition_score_profiles` et
    `astral_advanced_condition_weights`.
- Secondary evidence:
  - migration/schema inspection, tests repository/runtime reference, tests des
    calculateurs avances, tests du moteur avance, snapshots de payload et scans
    cibles anti-import/anti-narration.
- Static scans alone are not sufficient for this story because:
  - le risque principal est un moteur avance qui encode localement les types,
    poids ou axes; il faut donc executer le chargement runtime et valider les
    lignes actives.

### 4b.1 Advanced Condition Type Seed Contract

`astral_advanced_condition_types` must seed exactly these active parent v1 rows
for the default reference version. Emitted subtypes listed below must map to
these parent rows through `condition_type_code`; the dev agent must not add
extra active type rows for subtypes unless the story is explicitly amended.

| code | label | category | functional_effect | expression_effect | intensity_effect | visibility_effect | default_weight | sort_order | is_active |
|---|---|---|---|---|---|---|---:|---:|---:|
| `mutual_reception` | Mutual reception | reception | supporting | harmonizing | moderate | neutral | 1.20 | 10 | true |
| `hayz` | Hayz | sect | supporting | stabilizing | moderate | moderate | 1.10 | 20 | true |
| `out_of_sect` | Out of sect | sect | weakening | destabilizing | contextual | neutral | -1.00 | 30 | true |
| `stationary` | Stationary | motion | intensifying | focusing | high | moderate | 1.00 | 40 | true |
| `besiegement` | Besiegement | aspect_condition | constraining | pressured | high | neutral | -1.30 | 50 | true |
| `bonification` | Bonification | aspect_condition | supporting | stabilizing | moderate | neutral | 1.00 | 60 | true |
| `maltreatment` | Maltreatment | aspect_condition | constraining | destabilizing | high | neutral | -1.20 | 70 | true |
| `fast_motion` | Fast motion | motion | supporting | mobilizing | moderate | neutral | 0.70 | 80 | true |
| `slow_motion` | Slow motion | motion | weakening | slowing | moderate | neutral | -0.60 | 90 | true |
| `heliacal_rising` | Heliacal rising | solar_phase | supporting | emerging | moderate | high | 0.90 | 100 | true |
| `heliacal_setting` | Heliacal setting | solar_phase | weakening | withdrawing | moderate | low | -0.80 | 110 | true |
| `oriental` | Oriental | orientation | contextual | orienting | contextual | neutral | 0.40 | 120 | true |
| `occidental` | Occidental | orientation | contextual | orienting | contextual | neutral | 0.40 | 130 | true |

Mandatory V1 condition codes emitted by the engine:

- `hayz`
- `out_of_sect`
- `stationary_direct`
- `stationary_retrograde`
- `fast_motion`
- `slow_motion`
- `heliacal_rising`
- `heliacal_setting`
- `mutual_reception_by_domicile`
- `mutual_reception_by_exaltation`
- `besiegement`
- `bonification`
- `maltreatment`
- `oriental`
- `occidental`

Canonical mapping rule:

- emitted subtype codes such as `stationary_direct`,
  `stationary_retrograde`, `mutual_reception_by_domicile` and
  `mutual_reception_by_exaltation` must reference a parent runtime type through
  the explicit `condition_type_code` field of `AdvancedPlanetaryCondition`; they
  must not create hidden local type vocabularies.
- emitted codes that already match an active runtime type, such as
  `besiegement`, `bonification`, `maltreatment`, `fast_motion`,
  `slow_motion`, `heliacal_rising`, `heliacal_setting`, `hayz`,
  `out_of_sect`, `oriental` and `occidental`, must set
  `condition_type_code` to the same value as `condition_code`.

### 4b.2 Advanced Condition Score Profile Seed Contract

`astral_advanced_condition_score_profiles` must seed this active row:

| code | label | tradition_code | description | reference_version_code | is_active |
|---|---|---|---|---|---:|
| `traditional_advanced_v1` | Traditional advanced planetary conditions v1 | traditional | Profil standard des conditions avancees. | v1 | true |

### 4b.3 Advanced Condition Weight Contract

`astral_advanced_condition_weights` must expose one row per active parent
condition type used by the default profile. Missing rows may use
`astral_advanced_condition_types.default_weight` only when the runtime contract
records that fallback explicitly as `uses_default_weight=true` on the mapped
runtime weight.

Required weight axes:

- `functional_strength_weight`
- `visibility_weight`
- `stability_weight`
- `intensity_weight`
- `coherence_weight`
- `support_weight`
- `constraint_weight`
- `ranking_weight`

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-195-advanced-planetary-conditions/evidence/advanced-conditions-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-195-advanced-planetary-conditions/evidence/advanced-conditions-after.json`
- Expected invariant:
  - tous les champs natals et chart JSON existants restent presents et
    compatibles; seuls `advanced_conditions`, les breakdowns/faits avances des
    profils conditionnels, les signaux derives des profils enrichis et les
    scores de dominance via `ranking_weight` peuvent changer.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Tables, migrations et modeles SQLAlchemy des conditions avancees | `backend/migrations/**`, `backend/app/infra/db/models/**` | `backend/app/domain/**` |
| Chargement SQLAlchemy des referentiels avances | `backend/app/infra/db/repositories/**` | `backend/app/domain/**` |
| Contrats runtime des conditions avancees | `backend/app/domain/astrology/runtime/runtime_reference.py` | `backend/app/services/**` |
| Calculateurs purs de conditions avancees | `backend/app/domain/astrology/advanced_conditions/**` | `backend/app/infra/**`, `backend/app/api/**`, `backend/app/services/**` |
| Enrichissement des profils conditionnels | `backend/app/domain/astrology/condition/**` ou orchestrateur natal apres calcul avance | `backend/app/services/chart/**` |
| Integration dominance via score deja calcule | `backend/app/domain/astrology/dominance/**` | `backend/app/services/chart/**`, serialiseur |
| Integration du resultat natal | `backend/app/domain/astrology/natal_calculation.py` | routeurs API |
| Projection JSON publique | `backend/app/services/chart/json_builder.py` | calculateurs domaine |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - DTO domaine et payload `NatalResult.advanced_conditions` /
    `advanced_conditions`.
- Fields:
  - `condition_code: string` code emis stable, par exemple
    `mutual_reception_by_domicile`.
  - `condition_type_code: string` code parent issu de
    `astral_advanced_condition_types`, par exemple `mutual_reception`.
  - `source_planet_code: string` planete qualifiee.
  - `target_planet_code: string | null` planete cible quand la condition est relationnelle.
  - `score_profile: string` profil avance applique.
  - `reference_version: string` version du referentiel.
  - `score_impact: number` impact total normalise.
  - `ranking_weight: number` contribution potentielle au ranking de dominance.
  - `axes_impact: object` impacts par axe normalise.
  - `axes_impact.functional_strength_delta: number`
  - `axes_impact.visibility_delta: number`
  - `axes_impact.stability_delta: number`
  - `axes_impact.intensity_delta: number`
  - `axes_impact.coherence_delta: number`
  - `axes_impact.support_delta: number`
  - `axes_impact.constraint_delta: number`
  - `reason: string` fait court structurel, non narratif.
- Required fields:
  - tous les champs listes ci-dessus sont requis; `target_planet_code` est
    requis mais nullable.
- Optional fields:
  - aucun champ optionnel dans le contrat v1.
- Status codes:
  - aucune route API nouvelle n'est creee et aucun status code n'est modifie.
- Serialization names:
  - `NatalResult.advanced_conditions` reste `advanced_conditions`.
  - le JSON public expose `advanced_conditions` comme liste d'objets.
  - les axes publics peuvent etre projetes en noms courts
    `functional_strength`, `visibility`, `stability`, `intensity`,
    `coherence`, `support`, `constraint`, mais le contrat domaine conserve les
    suffixes `_delta`.
- Frontend type impact:
  - aucun fichier frontend n'est modifie dans cette story; le champ public est
    prepare pour consommation future.
- Generated contract impact:
  - OpenAPI ne doit changer que si le payload natal est deja modelise par schema
    genere; dans ce cas le snapshot doit documenter uniquement l'ajout
    `advanced_conditions` et les enrichissements autorises.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: no old surface is migrated in batches; the story adds one advanced
  condition layer and preserves existing condition, signal and dominance
  surfaces.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Snapshot avant | `_condamad/stories/CS-195-advanced-planetary-conditions/evidence/advanced-conditions-before.json` | Etat du payload avant ajout. |
| Snapshot apres | `_condamad/stories/CS-195-advanced-planetary-conditions/evidence/advanced-conditions-after.json` | Ajout exact des conditions avancees. |
| Rapport runtime | `_condamad/stories/CS-195-advanced-planetary-conditions/evidence/advanced-condition-runtime-reference.md` | Tables, lignes actives, profils et poids charges. |
| Rapport gardes | `_condamad/stories/CS-195-advanced-planetary-conditions/evidence/advanced-condition-guard-evidence.md` | Scans anti-import, anti-poids, anti-narration. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- loaded runtime reference inventory;
- AST import graph when the existing guard pattern supports it;
- targeted forbidden symbol scans.

Required forbidden examples:

- `from app.infra` dans `backend/app/domain/astrology/advanced_conditions/**`
- `Session`, `select(` ou modeles SQLAlchemy dans
  `backend/app/domain/astrology/advanced_conditions/**`
- poids ou types locaux comme `ADVANCED_CONDITION_TYPES`,
  `ADVANCED_CONDITION_WEIGHTS`, `HAYZ_RULES`, `MUTUAL_RECEPTION_RULES`,
  `PLANET_SPEED_THRESHOLDS`, `HELIACAL_PHASES`, `BENEFIC_PLANETS`,
  `MALEFIC_PLANETS` ou equivalent non derive du runtime
- imports ou symboles `AIEngineAdapter`, `OpenAI`, `prompt`, `narration`,
  `micro_note`, `app.domain.prediction`, `app.services.prediction`
- calcul de `advanced_conditions` dans `json_builder.py`
- calcul de dominance avancee dans le serialiseur au lieu de
  `PlanetDominanceEngine`

Guard evidence:

- Evidence profile: `reintroduction_guard`;
  `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` ou un test
  de garde voisin verifie les imports, poids locaux, symboles interdits et
  projection du serialiseur.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/astrology/condition/contracts.py` -
  `PlanetConditionProfile`, `PlanetConditionBreakdownItem`,
  `PlanetConditionSignal` et `PlanetConditionSignalSet` existent deja.
- Evidence 2: `backend/app/domain/astrology/dominance/contracts.py` -
  `PlanetDominanceResult` existe avec scores et contributions par facteur.
- Evidence 3: `backend/app/domain/astrology/runtime/runtime_reference.py` -
  `AstrologyRuntimeReference` expose deja les profils de signaux conditionnels
  et les facteurs de dominance, mais pas les referentiels de conditions avancees.
- Evidence 4: `backend/app/domain/astrology/natal_calculation.py` -
  `NatalResult` integre deja `dignities`, `condition_profiles`,
  `condition_signals` et `dominant_planets`.
- Evidence 5: `backend/app/services/chart/json_builder.py` - le JSON public
  projette deja `planet_condition_profiles`, `planet_condition_signals` et
  `dominant_planets` sans recalculer les moteurs.
- Evidence 6: `backend/app/infra/db/models/dignity_reference.py` - les
  referentiels existants `astral_accidental_dignity_condition_schemas`,
  `astral_condition_operators`, `astral_planet_motion_states`,
  `astral_speed_relations`, `astral_heliacal_conditions` et
  `astral_planet_natures` existent dans le modele infra.
- Evidence 7: `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` -
  le repository normalise deja les JSON de conditions accidentelles en codes
  runtime et valide les profils de signaux/dominance.
- Evidence 8: `_condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md`,
  `_condamad/stories/CS-193-planetary-condition-signals/00-story.md` et
  `_condamad/stories/CS-194-dominant-planets-engine/00-story.md` - les couches
  condition, signaux et dominance sont closes et doivent etre reutilisees.
- Evidence 9: `_condamad/stories/story-status.md` - `CS-192`, `CS-193` et
  `CS-194` sont marques `done` au moment de la redaction.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - invariants de
  regression consultes avant finalisation du perimetre de la story.

## 6. Target State

After implementation:

- Les trois tables `astral_advanced_condition_types`,
  `astral_advanced_condition_score_profiles` et
  `astral_advanced_condition_weights` existent avec modeles SQLAlchemy, seeds et
  chargement runtime.
- `AstrologyRuntimeReference` expose les types, profils et poids avances sous
  contrats immuables et tries de facon deterministe.
- `advanced_conditions/**` contient uniquement des calculateurs purs qui
  consomment positions, maisons, aspects, dignites, profils conditionnels et le
  runtime transmis.
- Le moteur detecte V1: `hayz`, `out_of_sect`, `stationary_direct`,
  `stationary_retrograde`, `fast_motion`, `slow_motion`, `heliacal_rising`,
  `heliacal_setting`, `mutual_reception_by_domicile`,
  `mutual_reception_by_exaltation`, `besiegement`, `bonification`,
  `maltreatment`, `oriental` et `occidental`.
- `PlanetConditionProfile` reste la couche canonique et est enrichi par des
  breakdowns/faits avances, sans nouvelle persistance de profils.
- `PlanetConditionSignalBuilder` continue de produire les signaux depuis les
  profils conditionnels enrichis et les profils runtime de signaux.
- `PlanetDominanceEngine` integre les conditions avancees via `ranking_weight`
  dans le scoring, jamais dans le serialiseur.
- `NatalResult.advanced_conditions` et le JSON public `advanced_conditions`
  exposent une liste structurelle, sans storytelling.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-107` - les donnees astrologiques runtime doivent rester typees et les JSON DB confines a l'infra.
  - `RG-108` - le vocabulaire DB-backed des conditions avancees ne doit pas etre recree en constantes locales.
  - `RG-112` - les constantes metier astrologiques et fallbacks legacy ne doivent pas revenir.
  - `RG-115` - le runtime natal reste objectif et fonde sur des contrats explicites.
  - `RG-116` - les calculateurs/adapters natals ne doivent pas importer les services d'interpretation.
  - `RG-118` - le moteur de dignites reste factuel, sans DB directe, interpretation, prediction ou LLM.
  - `RG-119` - les profils conditionnels restent la couche canonique a enrichir, pas a remplacer.
  - `RG-120` - les signaux conditionnels restent derives des profils et du runtime de signaux.
  - `RG-121` - la dominance planetaire reste calculee par `PlanetDominanceEngine`.
  - `RG-122` - cette story etablit `AdvancedConditionEngine` comme moteur canonique factuel des conditions avancees.
- Non-applicable invariants:
  - `RG-117` - cette story ne touche pas le scoring des etoiles fixes daily.
- Required regression evidence:
  - tests unitaires des calculateurs avances, tests runtime repository, tests
    payload, tests dominance integration, snapshot avant/apres, scan anti-import
    DB, scan anti-poids local, scan anti-LLM, scan anti-narration et scan
    anti-recalcul serialiseur.
- Allowed differences:
  - ajout des trois tables de referentiel avance, ajout du runtime associe,
    ajout de `advanced_conditions`, enrichissement des profils/signaux et
    modification de la dominance uniquement via `ranking_weight`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le schema des trois tables avancees existe. | pytest: `backend/app/tests/integration/test_reference_data_migrations.py`. |
| AC2 | Le runtime expose les contrats avances immuables. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC3 | Les contrats avances existent sans dict libre ni narration. | `pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py`. |
| AC4 | Les receptions mutuelles V1 sont detectees. | `pytest -q backend/tests/unit/domain/astrology/test_mutual_reception_calculator.py`. |
| AC5 | Les conditions de secte V1 sont detectees. | `pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py`. |
| AC6 | Les conditions de vitesse V1 sont detectees. | `pytest -q backend/tests/unit/domain/astrology/test_speed_classifier.py`. |
| AC7 | Les conditions solaires V1 sont detectees. | `pytest -q backend/tests/unit/domain/astrology/test_heliacal_conditions.py`. |
| AC8 | Les conditions aspectuelles V1 sont detectees. | `pytest -q backend/tests/unit/domain/astrology/test_besiegement_detector.py`. |
| AC9 | Les conditions avancees enrichissent les profils sans remplacer l'existant. | pytest: `test_advanced_condition_engine.py`, `test_natal_result_contract.py`. |
| AC10 | Les signaux consomment les profils enrichis sans recalcul avance. | pytest: `backend/tests/unit/domain/astrology/test_planet_condition_signal_builder.py`. |
| AC11 | La dominance integre les conditions avancees via `ranking_weight`. | `pytest -q backend/tests/unit/domain/astrology/test_dominance_integration.py`. |
| AC12 | Le JSON public expose `advanced_conditions` sans calcul serialiseur. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py` + snapshot evidence. |
| AC13 | La garde bloque les dependances interdites des calculateurs avances. | pytest: `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`. |
| AC14 | Les conditions explicitement reportees ne sont pas implementees ni exposees. | Le `rg` des techniques reportees dans le Validation Plan doit retourner zero hit. |
| AC15 | Le contrat public reste stable hors ajouts autorises. | `ruff check .` + comparaison des snapshots evidence avant/apres. |

## 8. Implementation Tasks

- [ ] Task 1 - Ajouter les referentiels DB/runtime des conditions avancees (AC: AC1, AC2)
  - [ ] Subtask 1.1 - Ajouter une migration Alembic pour les trois tables avancees avec contraintes de code, profil, version et unicite.
  - [ ] Subtask 1.2 - Ajouter les modeles SQLAlchemy infra et les exporter via `backend/app/infra/db/models/__init__.py`.
  - [ ] Subtask 1.3 - Seeder les lignes de `4b.1`, `4b.2` et les poids V1.
  - [ ] Subtask 1.4 - Charger et mapper les lignes dans `AstrologyRuntimeReference`.

- [ ] Task 2 - Creer les contrats et calculateurs purs (AC: AC3, AC4, AC5, AC6, AC7, AC8, AC13, AC14)
  - [ ] Subtask 2.1 - Creer `backend/app/domain/astrology/advanced_conditions/contracts.py`.
  - [ ] Subtask 2.2 - Creer les calculateurs specialises demandes par le brief.
  - [ ] Subtask 2.3 - Reutiliser les referentiels existants de mouvement,
    vitesse, heliacal, natures planetaires, operateurs et dignites runtime.
  - [ ] Subtask 2.4 - Exporter explicitement les surfaces publiques depuis `advanced_conditions/__init__.py`.

- [ ] Task 3 - Implementer `AdvancedConditionEngine` et enrichir la condition (AC: AC3, AC9, AC10)
  - [ ] Subtask 3.1 - Orchestrer les calculateurs avances dans `advanced_condition_engine.py`.
  - [ ] Subtask 3.2 - Appliquer `PlanetConditionAxisImpact` aux profils conditionnels sans muter les objets existants.
  - [ ] Subtask 3.3 - Ajouter des breakdowns/faits courts avances avec raisons structurelles et sans texte editorial.

- [ ] Task 4 - Integrer le resultat natal, la dominance et le JSON public (AC: AC11, AC12, AC15)
  - [ ] Subtask 4.1 - Ajouter `advanced_conditions` a `NatalResult`.
  - [ ] Subtask 4.2 - Construire les conditions avancees apres positions, maisons, aspects, dignites et profils conditionnels.
  - [ ] Subtask 4.3 - Passer les conditions avancees a `PlanetDominanceEngine` pour appliquer `ranking_weight`.
  - [ ] Subtask 4.4 - Ajouter `_serialize_advanced_conditions` dans `json_builder.py` comme projection stricte.

- [ ] Task 5 - Ajouter tests, preuves et gardes (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15)
  - [ ] Subtask 5.1 - Ajouter les tests unitaires des calculateurs et du moteur avance.
  - [ ] Subtask 5.2 - Etendre les tests runtime reference, contrat natal, chart JSON et chart result service.
  - [ ] Subtask 5.3 - Ajouter le test d'integration dominance avancee.
  - [ ] Subtask 5.4 - Mettre a jour la garde d'architecture runtime.
  - [ ] Subtask 5.5 - Produire les artefacts evidence dans le dossier de story.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetConditionProfile` comme couche canonique a enrichir.
  - `PlanetConditionBreakdownItem` et `PlanetConditionExplanationFact` pour
    rattacher les impacts avances aux profils.
  - `PlanetConditionSignalBuilder` pour produire les signaux depuis les profils enrichis.
  - `PlanetDominanceEngine` pour toute influence sur le classement dominant.
  - `AstrologyRuntimeReference.dignity_reference` et `sign_rulerships` pour les
    receptions par domicile/exaltation.
  - les referentiels existants `astral_planet_motion_states`,
    `astral_speed_relations`, `astral_heliacal_conditions`,
    `astral_planet_natures`, `astral_condition_operators`.
  - `build_chart_json` comme unique serialiseur public du theme natal.
- Do not recreate:
  - un nouveau calculateur de positions astronomiques;
  - un deuxieme moteur de dignites;
  - un deuxieme moteur de profils conditionnels;
  - un deuxieme builder de signaux;
  - un deuxieme moteur de dominance;
  - des mappings locaux de benefiques/malefiques, vitesses, phases solaires,
    seuils, poids ou types avances hors runtime.
- Shared abstraction allowed only if:
  - elle remplace une duplication observee entre les calculateurs avances;
  - elle reste sous `backend/app/domain/astrology/advanced_conditions`;
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

- `backend/app/domain/astrology/advanced_conditions/**` qui importent
  `app.infra`, `app.api`, `app.services`, `app.domain.prediction` ou
  `app.services.prediction`.
- `backend/app/domain/astrology/advanced_conditions/**` contenant `Session`,
  `select(`, `OpenAI`, `AIEngineAdapter`, le mot exact `prompt`, `narration`,
  `micro_note` ou texte editorial de restitution.
- `ADVANCED_CONDITION_TYPES`, `ADVANCED_CONDITION_WEIGHTS`, `HAYZ_RULES`,
  `MUTUAL_RECEPTION_RULES`, `PLANET_SPEED_THRESHOLDS`, `HELIACAL_PHASES`,
  `BENEFIC_PLANETS`, `MALEFIC_PLANETS` ou mapping equivalent non derive du runtime.
- `translation_of_light`, `collection_of_light`, `planetary_war`, `antiscia`,
  `contra_antiscia`, `contra-antiscia`, `primary_directions`,
  `primary directions`, `zodiacal_releasing`, `zodiacal releasing`, `firdaria`,
  `annual_profections` ou `annual profections` dans l'implementation runtime.
- Recalcul de `advanced_conditions`, `condition_signals` ou
  `dominant_planets` dans `backend/app/services/chart/json_builder.py`.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Referentiels de conditions avancees | `backend/app/infra/db/models/**`, `backend/app/infra/db/repositories/**` | `backend/app/domain/**` |
| Contrats runtime des conditions avancees | `backend/app/domain/astrology/runtime/runtime_reference.py` | `backend/app/services/**`, `backend/app/api/**` |
| Detection et scoring des conditions avancees | `backend/app/domain/astrology/advanced_conditions/**` | serialiseurs, prediction, prompts LLM |
| Profil conditionnel enrichi | `backend/app/domain/astrology/condition/**` | serialiseur, API, UI |
| Dominance planetaire impactee | `backend/app/domain/astrology/dominance/**` | serialiseur, API, UI |
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

- If OpenAPI includes the affected response schema, capture before/after and
  document that only `advanced_conditions` and the authorized nested additions
  are added.
- If OpenAPI does not model the dynamic chart JSON shape, record that fact in
  `_condamad/stories/CS-195-advanced-planetary-conditions/evidence/advanced-condition-guard-evidence.md`.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/condition/contracts.py`
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
- `backend/app/domain/astrology/condition/planet_condition_signal_builder.py`
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py`
- `backend/app/domain/astrology/dominance/contracts.py`
- `backend/app/domain/astrology/dignities/contracts.py`
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

- `backend/migrations/versions/*.py` - ajouter les trois tables referentielles avancees.
- `backend/app/infra/db/models/dignity_reference.py` - ajouter les modeles SQLAlchemy avances si le projet conserve ces referentiels dans ce fichier.
- `backend/app/infra/db/models/__init__.py` - exporter les nouveaux modeles pour `Base.metadata`.
- `backend/app/services/reference_data/dignity_seed_service.py` - synchroniser les seeds JSON des referentiels avances.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - ajouter les contrats runtime avances.
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - charger et valider les referentiels avances.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - mapper les lignes vers le runtime.
- `backend/app/domain/astrology/advanced_conditions/contracts.py` - nouveau contrat domaine.
- `backend/app/domain/astrology/advanced_conditions/advanced_condition_engine.py` - orchestration pure.
- `backend/app/domain/astrology/advanced_conditions/mutual_reception_calculator.py` - reception mutuelle.
- `backend/app/domain/astrology/advanced_conditions/hayz_calculator.py` - hayz et out-of-sect.
- `backend/app/domain/astrology/advanced_conditions/planet_speed_classifier.py` - vitesse et stations.
- `backend/app/domain/astrology/advanced_conditions/heliacal_condition_calculator.py` - phases heliacales et orientation.
- `backend/app/domain/astrology/advanced_conditions/aspect_condition_detector.py` - besiegement, bonification, maltreatment.
- `backend/app/domain/astrology/advanced_conditions/__init__.py` - exports explicites.
- `backend/app/domain/astrology/condition/contracts.py` - etendre le breakdown
  des faits avances sans casser les champs existants.
- `backend/app/domain/astrology/natal_calculation.py` - integrer `advanced_conditions`.
- `backend/app/domain/astrology/dominance/planet_dominance_engine.py` - consommer l'impact avance via `ranking_weight`.
- `backend/app/services/chart/json_builder.py` - exposer `advanced_conditions`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_mutual_reception_calculator.py` - receptions domicile/exaltation.
- `backend/tests/unit/domain/astrology/test_hayz_calculator.py` - hayz et out-of-sect.
- `backend/tests/unit/domain/astrology/test_besiegement_detector.py` - besiegement, bonification, maltreatment.
- `backend/tests/unit/domain/astrology/test_heliacal_conditions.py` - heliacal rising/setting et oriental/occidental.
- `backend/tests/unit/domain/astrology/test_speed_classifier.py` - fast/slow/stationary direct/retrograde.
- `backend/tests/unit/domain/astrology/test_advanced_condition_engine.py` - orchestration, axes, tri, facts et absence narration.
- `backend/tests/unit/domain/astrology/test_natal_result_contract.py` - contrat `NatalResult`.
- `backend/tests/unit/domain/astrology/test_dominance_integration.py` - influence `ranking_weight`.
- `backend/app/tests/unit/test_chart_json_builder.py` - projection publique.
- `backend/app/tests/unit/test_chart_result_service.py` - persistance payload si deja couverte.
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - runtime avance.
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` - garde anti-import, anti-poids local, anti-narration.
- `backend/app/tests/integration/test_reference_data_migrations.py` - schema/migration.

Files not expected to change:

- `frontend/**` - aucune UI ou type frontend dans cette story.
- `backend/app/domain/astrology/calculators/**` - aucun recalcul de positions astronomiques.
- `backend/app/domain/astrology/dignities/**` - aucun changement de detection des dignites hors reutilisation de resultats.
- `backend/app/services/llm_generation/**` - aucun prompt ou adapter LLM.
- `backend/app/domain/prediction/**` - aucun scoring predictif ou daily.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/test_mutual_reception_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_hayz_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_besiegement_detector.py
pytest -q backend/tests/unit/domain/astrology/test_heliacal_conditions.py
pytest -q backend/tests/unit/domain/astrology/test_speed_classifier.py
pytest -q backend/tests/unit/domain/astrology/test_advanced_condition_engine.py
pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py
pytest -q backend/tests/unit/domain/astrology/test_dominance_integration.py backend/tests/unit/domain/astrology/test_planet_dominance_engine.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py
pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py
pytest -q backend/app/tests/integration/test_reference_data_migrations.py
ruff format .
ruff check .
rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|from app\.services\.prediction" `
  backend/app/domain/astrology/advanced_conditions -g "*.py"
rg -n "OpenAI|AIEngineAdapter|chat\.completions|\bprompt\b|narration|micro_note" `
  backend/app/domain/astrology/advanced_conditions -g "*.py"
rg -n "ADVANCED_CONDITION_TYPES|ADVANCED_CONDITION_WEIGHTS|HAYZ_RULES|MUTUAL_RECEPTION_RULES|PLANET_SPEED_THRESHOLDS|HELIACAL_PHASES|BENEFIC_PLANETS|MALEFIC_PLANETS" `
  backend/app backend/tests frontend/src -g "*.py" -g "*.ts" -g "*.tsx"
rg -n "translation[_ ]of[_ ]light|collection[_ ]of[_ ]light|planetary[_ ]war|antiscia|contra[_ -]antiscia|primary[_ ]directions|zodiacal[_ ]releasing|firdaria|annual[_ ]profections" `
  backend/app/domain/astrology/advanced_conditions backend/app/services/chart/json_builder.py -g "*.py"
rg -n "advanced_conditions|AdvancedCondition|AdvancedPlanetaryCondition" `
  backend/app/services/chart/json_builder.py `
  backend/app/domain/astrology/natal_calculation.py `
  backend/app/domain/astrology/advanced_conditions `
  backend/app/domain/astrology/dominance -g "*.py"
```

Expected scan result:

- the first two `rg` commands return zero hits;
- the third `rg` command returns zero hits for hardcoded advanced condition maps;
- the fourth `rg` command returns zero hits for deferred techniques;
- the fifth `rg` command shows only projection, integration and domain engine
  sites, not local calculation in `json_builder.py`.

## 21. Regression Risks

- Risk: les conditions avancees deviennent une narration deguisee.
  - Guardrail: AC3, AC12, AC13 et scans anti-LLM/anti-narration limitent le
    resultat a des codes, axes, poids, impacts et raisons courtes.
- Risk: les regles traditionnelles sont codees localement.
  - Guardrail: AC1, AC2 et `RG-122` imposent les types, profils et poids runtime.
- Risk: le serialiseur recalcule les conditions ou la dominance.
  - Guardrail: AC12 et AC13 exigent une projection stricte depuis `NatalResult`.
- Risk: le moteur avance remplace les profils conditionnels.
  - Guardrail: AC9 impose un enrichissement des profils existants.
- Risk: les techniques reportees entrent dans le scope.
  - Guardrail: AC14 et les scans dedies bloquent les symboles reportes.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not add frontend, prompts, LLM, prediction, compatibility relationnelle,
  horoscopes or editorial interpretation logic.
- Do not implement `translation_of_light`, `collection_of_light`,
  `planetary_war`, `antiscia`, `contra-antiscia`, `primary directions`,
  `zodiacal releasing`, `firdaria` or `annual profections`.
- Do not duplicate CS-192, CS-193 or CS-194 logic when a canonical result is
  already available.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.

## 23. References

- `backend/app/domain/astrology/condition/contracts.py` - source actuelle de
  `PlanetConditionProfile`, `PlanetConditionBreakdownItem` et signaux.
- `backend/app/domain/astrology/dominance/contracts.py` - contrat de dominance a
  enrichir via le moteur de scoring.
- `backend/app/domain/astrology/runtime/runtime_reference.py` - proprietaire du
  runtime a etendre.
- `backend/app/infra/db/models/dignity_reference.py` - proprietaire probable des
  modeles de referentiels astrologiques avances.
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
  - repository runtime a etendre et source des referentiels existants a
  reutiliser.
- `backend/app/domain/astrology/natal_calculation.py` - proprietaire de
  `NatalResult` et de l'orchestration natale.
- `backend/app/services/chart/json_builder.py` - proprietaire de la projection
  JSON publique.
- `_condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md` -
  couche conditionnelle a enrichir.
- `_condamad/stories/CS-193-planetary-condition-signals/00-story.md` - couche de
  signaux a reutiliser.
- `_condamad/stories/CS-194-dominant-planets-engine/00-story.md` - moteur de
  dominance a reutiliser.
- `_condamad/stories/regression-guardrails.md` - registre des invariants
  consulte et a enrichir pour CS-195.
