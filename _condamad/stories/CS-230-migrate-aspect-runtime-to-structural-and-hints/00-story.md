# Story CS-230 migrate-aspect-runtime-to-structural-and-hints: Migrate Aspect Runtime To Structural Runtime And Interpretive Hints
Status: done

## 1. Objective

Migrer l'execution des aspects vers une separation effective entre runtime structurel, hints interpretatifs et projection publique compatible.
La story retire la valence et l'energie des chemins de calcul structurels, tout en conservant les champs publics historiques du JSON natal.

## 2. Trigger / Source

- Source type: architecture-runtime-migration.
- Source reference: `_story_briefs/cs-230-migrate-aspect-runtime-to-structural-and-hints.md`.
- Reason for change: CS-229 a defini les contrats cibles, mais les calculateurs, builders et consommateurs transportent encore des champs interpretatifs.
- Selected story writer mode: Fast Story Writer Mode.
- Skill availability note: `.agents/skills/condamad-story-writer/SKILL.md`, le cheatsheet demande et `resolve_guardrails.py` ne sont pas presents.
- Source-alignment review: la story migre des surfaces backend-domain et projection publique, sans frontend, DB, doctrine, score ou route nouvelle.

## References

- `_story_briefs/cs-230-migrate-aspect-runtime-to-structural-and-hints.md`.
- `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/00-story.md`.
- `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/00-story.md`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-098|RG-099|RG-100|RG-101|RG-102|RG-145`.

## 3. Domain Boundary

Cette story appartient au domaine astrologie runtime, avec surfaces d'integration backend explicites:

- Domain: `backend/app/domain/astrology`.
- Integration surfaces:
  - `backend/app/services/chart/json_builder.py` pour la projection publique compatible;
  - `backend/app/domain/prediction` et `backend/app/services/prediction` pour le contrat prediction;
  - `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` pour les vues de referentiel structurelle et interpretative;
  - `backend/app/infra/db/repositories/reference_repository.py` pour exposer ces vues aux consommateurs runtime.
- In scope:
  - migrer `AspectDefinitionRuntimeData` vers une definition structurelle et un profil interpretatif;
  - migrer `AspectCalculationResult` pour que la forme structurelle ne porte plus de valence, energy type ou poids interpretatif;
  - creer `AspectInterpretiveHintResolver` ou adapter equivalent;
  - migrer `build_aspect_runtime_data` vers un builder structurel;
  - conserver une projection publique compatible pour `interpretive_valence` et `energy_type`;
  - migrer `ChartInterpretationInputBuilder` vers les hints interpretatifs;
  - migrer `json_builder` vers une projection alimentee par hints ou adapter public;
  - aligner `natal_calculation_nodes` et les mappers de referentiel avec deux vues: structurelle et interpretative;
  - auditer `dominant_aspects`, `pattern_runtime` et `prediction`;
  - ajouter tests unitaires, integration et architecture;
  - prouver l'absence de delta API volontaire avec `app.routes`, `app.openapi()`, `pytest` et `TestClient`.
- Out of scope:
  - supprimer les champs publics du JSON natal;
  - supprimer les tables DB de valence;
  - modifier `astral_aspect_profiles.json`;
  - changer les scores, orbes, doctrine astrologique ou golden cases;
  - modifier le frontend;
  - reecrire le moteur de prediction;
  - supprimer toutes les surfaces legacy du `NatalResult`;
  - migrer transits ou synastrie hors necessite prouvee par test cible.
- Explicit non-goals:
  - ne pas enrichir `_condamad/stories/regression-guardrails.md` pendant cette generation normale;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas deplacer les champs interpretatifs dans un dictionnaire libre;
  - ne pas produire de texte narratif long dans le resolver de hints;
  - ne pas introduire une seconde logique de calcul d'orbe ou de force.

## 4. Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: la story transforme des contrats et consommateurs backend-domain sans endpoint dedie ni schema HTTP nouveau.
- Behavior change allowed: constrained
- Behavior change constraints:
  - autorise: contrats structurels et interpretatifs separes pour aspects;
  - autorise: resolver ou adapter de hints interpretatifs depuis runtime structurel et profil;
  - autorise: facade legacy temporaire seulement documentee, bornee et alimentee par les hints;
  - autorise: projection publique stable des champs historiques `interpretive_valence` et `energy_type`;
  - interdit: changement volontaire de route, OpenAPI, JSON public, DB, frontend, scores, doctrine, prompts ou dependance externe.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: l'implementation supprime un champ public, modifie une migration DB, touche le frontend ou change un score astrologique.
- Additional validation rules:
  - le calculateur d'aspects produit uniquement des faits structurels;
  - `AspectStructuralRuntimeData` ne contient aucun champ de valence, energy type, prompt, meaning, narrative ou poids interpretatif;
  - `AspectCalculationResult` structurel ne porte pas `default_valence`, `interpretive_valence`, `energy_type` ou `interpretive_weight`;
  - `AspectDefinitionRuntimeData` se separe en vue structurelle et profil interpretatif;
  - `AspectInterpretiveHintResolver` ne calcule ni orbe, ni force technique, ni texte narratif;
  - `build_aspect_runtime_data` devient un builder structurel et ne cree pas de bloc interpretatif primaire;
  - toute facade `AspectRuntimeData.interpretation` restante est legacy, documentee et alimentee depuis le resolver;
  - `json_builder` construit les champs publics historiques depuis hints ou projection dediee;
  - `ChartInterpretationInputBuilder` consomme les hints, pas le runtime structurel hybride;
  - dominance, pattern runtime et prediction ne lisent pas la valence depuis le runtime structurel;
  - les nodes natals ne transmettent pas de vue interpretative aux calculateurs structurels;
  - `app.routes`, `app.openapi()`, `pytest` et `TestClient` prouvent l'absence de delta API volontaire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | `AspectStructuralRuntimeData` devient la source calculatoire interne des aspects. |
| Baseline Snapshot | yes | Les champs hybrides et consommateurs doivent etre classes avant migration. |
| Ownership Routing | yes | Calculateur, builder structurel, resolver, projection publique, prediction et legacy ont des owners distincts. |
| Allowlist Exception | yes | Les surfaces legacy conservees doivent etre bornees et rattachees au resolver. |
| Contract Shape | yes | La forme structurelle, les hints et la projection publique doivent lister champs autorises et interdits. |
| Batch Migration | yes | Contrats, builder, resolver, consommateurs, projection et preuves sont livres par lots controlables. |
| Reintroduction Guard | yes | Les guards bloquent le retour des champs interpretatifs dans les modules structurels. |
| Persistent Evidence | yes | Tests, scans, OpenAPI et decisions de transition doivent etre conserves dans le dossier CS-230. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `AspectStructuralDefinitionRuntimeData`;
  - `AspectStructuralRuntimeData`;
  - `AspectStrengthRuntimeData`;
  - `AspectInterpretiveProfileRuntimeData`;
  - `AspectInterpretiveHintsRuntimeData`;
  - `AspectInterpretiveHintResolver`;
  - `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` pour le routage graph.
- Runtime/domain artifacts:
  - contrats Python types;
  - builder structurel d'aspects;
  - resolver de hints interpretatifs;
  - projection publique compatible;
  - tests unitaires, integration et architecture;
  - preuves `app.routes`, `app.openapi()` et `TestClient`.
- Secondary evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_aspect_calculation_contracts.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py`;
  - `pytest -q backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_builder.py`;
  - `pytest -q backend/app/tests/unit/test_chart_json_builder.py`;
  - `pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`;
  - `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.
- Static scans alone are not sufficient because:
  - ils ne prouvent ni l'execution runtime du resolver, ni la compatibilite JSON publique, ni le routage prediction.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/runtime/aspect_calculation_contracts.py`;
  - `Get-Content backend/app/domain/astrology/calculators/aspects.py`;
  - `Get-Content backend/app/domain/astrology/builders/aspect_runtime_builder.py`;
  - `Get-Content backend/app/domain/astrology/runtime/natal_calculation_nodes.py`;
  - `Get-Content backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`;
  - `Get-Content backend/app/services/chart/json_builder.py`;
  - recherche ciblee `default_valence|interpretive_valence|energy_type|interpretive_weight`;
  - recherche ciblee `AspectCalculationResult|AspectDefinitionRuntimeData|AspectRuntimeData|AspectStructuralRuntimeData`;
  - `Select-String "RG-098|RG-099|RG-100|RG-101|RG-102|RG-145" _condamad/stories/regression-guardrails.md`.
- Comparison after implementation:
  - memes recherches ciblees apres implementation;
  - tests CS-230 du Validation Plan;
  - preuve `app.routes`;
  - preuve `app.openapi()`;
  - diff adjacent sur API, DB, migrations, frontend, prompts et prediction;
  - preuve que le resolver ne recalcule ni angle, ni orbe, ni force.
- Expected invariant:
  - le JSON natal public expose encore `interpretive_valence` et `energy_type`;
  - les valeurs astrologiques et scores restent inchanges;
  - les calculateurs d'aspects restent responsables de la geometrie;
  - les hints interpretatifs restent types et sources;
  - aucun endpoint public ne change volontairement.
- Allowed differences:
  - champs interpretatifs deplaces hors contrats structurels;
  - resolver ou adapter interpretatif dedie;
  - projection legacy bornee pour consommateurs historiques;
  - tests d'architecture anti-retour;
  - Registry gap: un invariant global dedie a la migration effective CS-230 pourra etre ajoute ulterieurement.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Geometrie d'aspect | calculateur d'aspects | resolver interpretatif |
| Orbe et seuil utilise | calculateur et builder structurel | profil interpretatif |
| Force technique | `AspectStrengthRuntimeData` | hints ou prediction directe |
| Definition structurelle | referentiel structurel d'aspects | profil interpretatif |
| Profil interpretatif | referentiel/profil d'aspect | calculateur structurel |
| Hints interpretatifs | `AspectInterpretiveHintResolver` | calculateur d'orbe ou force |
| Projection publique | `json_builder` ou adapter public | runtime structurel interne |
| Input interpretation | `ChartInterpretationInputBuilder` via hints | lecture du bloc hybride legacy |
| Prediction | contrat prediction ou projection dediee | lecture de valence depuis structurel |
| Graph natal | nodes structurels | transmission de profil au calculateur |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `AspectRuntimeData.interpretation` | legacy projection field | Compatibilite temporaire des consommateurs existants. | Temporary; exit condition: story de suppression dediee. |
| `AspectCalculationResult` legacy fields | flat legacy projection | Compatibilite d'un consommateur externe prouve. | Temporary; exit condition: migrer vers hints. |
| `json_builder.py` | champs publics historiques | Contrat public natal conserve. | Permanent pour `interpretive_valence` et `energy_type`. |
| prediction contracts | valence et energy type | Usage legitime via contrat prediction ou hints. | Permanent seulement hors runtime structurel. |
| tests et fixtures | champs historiques | Baseline et non-regression. | Borne aux tests et evidence. |

Validation rule:

- Toute nouvelle lecture de `default_valence`, `interpretive_valence`, `energy_type` ou `interpretive_weight` depuis un module structurel bloque CS-230.

## 4f. Contract Shape

- Contract type:
  - dataclasses ou Pydantic models coherents avec les contrats runtime existants;
  - resolver ou adapter interpretatif explicite;
  - projection publique stable;
  - aucune nouvelle API HTTP.
- Required functions/classes:
  - `AspectStructuralDefinitionRuntimeData`;
  - `AspectInterpretiveProfileRuntimeData`;
  - `AspectStructuralRuntimeData`;
  - `AspectInterpretiveHintsRuntimeData`;
  - `AspectInterpretiveHintResolver`;
  - builder structurel d'aspects;
  - projection publique des champs historiques depuis hints.

Fields:

- `aspect_code`;
- `planet_a`;
- `planet_b`;
- `chart_a`;
- `chart_b`;
- `angle`;
- `orb`;
- `orb_used`;
- `orb_max`;
- `family`;
- `is_major`;
- `is_minor`;
- `strength`;
- `metadata`;
- `default_valence`;
- `interpretive_valence`;
- `energy_type`;
- `semantic_axes`;
- `growth_axes`;
- `shadow_axes`;
- `relationship_axes`;
- `interpretive_weight`;
- `source_profile_code`;
- `source_codes`.

Required structural fields:

- `aspect_code`;
- `planet_a`;
- `planet_b`;
- `chart_a`;
- `chart_b`;
- `angle`;
- `orb`;
- `orb_used`;
- `orb_max`;
- `family`;
- `is_major`;
- `is_minor`;
- `strength`.

Required fields:

- structural: `aspect_code`, `planet_a`, `planet_b`, `angle`, `orb`, `orb_max`, `family`, `is_major`, `is_minor` et `strength`;
- interpretive hints: `aspect_code`, `default_valence`, `interpretive_valence`, `energy_type` et `source_codes`;
- public projection: `interpretive_valence` et `energy_type`.

Forbidden structural fields:

- `default_valence`;
- `interpretive_valence`;
- `energy_type`;
- `interpretive_weight`;
- `prompt_hint`;
- `meaning`;
- `narrative`;
- `prompt`;
- `llm`.

Required interpretive hint fields:

- `aspect_code`;
- `default_valence`;
- `interpretive_valence`;
- `energy_type`;
- `source_codes`.

Optional interpretive hint fields:

- `semantic_axes`;
- `growth_axes`;
- `shadow_axes`;
- `relationship_axes`;
- `interpretive_weight`;
- `source_profile_code`;
- `reference_version`.

Optional fields:

- structural: `metadata`, `chart_a`, `chart_b` et `orb_used`;
- interpretive hints: `semantic_axes`, `growth_axes`, `shadow_axes`, `relationship_axes`, `interpretive_weight` et `source_profile_code`;
- legacy projection: `AspectRuntimeData.interpretation` uniquement comme transition bornee.

- Required output surfaces:
  - structural calculation result;
  - structural runtime;
  - interpretive hints;
  - public aspect projection unchanged;
  - legacy aspect projection bounded.
- Required behavior:
  - structurel: relation geometrique, participants, orbe, famille, statut majeur/mineur et force technique;
  - interpretatif: valence, energy type, axes, poids et sources;
  - public: payload natal stable;
  - legacy: compatibilite historique nommee.
- Status codes:
  - no HTTP endpoint, method or status code is changed.
- Serialization names:
  - no public JSON key is renamed or removed by CS-230.
- Frontend type impact:
  - none; no frontend contract changes are allowed.
- Generated contract impact:
  - none; `app.routes`, `app.openapi()` and `TestClient` must show no public delta.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | contrat calcul hybride | resultat structurel | calculator tests | contract tests | no valence fields | champ interpretatif structurel |
| 2 | definition mixte | definition + profil | mapper reference | repository tests | vues distinctes | calculateur lit profil |
| 3 | builder hybride | builder structurel | runtime builder | builder tests | no interpretation primary | bloc primaire conserve |
| 4 | hints implicites | resolver hints | interpretation input | resolver tests | no orb recompute | recalcul geometrique |
| 5 | projection dispersee | adapter public | json builder | JSON tests | public stable | cle publique supprimee |
| 6 | prediction directe | contrat hints/prediction | prediction consumers | prediction tests | no structural valence | lecture directe runtime |
| 7 | graph node mixte | node structurel | natal graph | graph tests | no profile to calculator | profil transmis |
| 8 | preuve manuelle API | `app.routes` et `app.openapi()` | aucun public | TestClient smoke | zero public delta | route/schema modifie |

Completion rule: chaque batch conserve les sorties publiques, les scores, les orbes, la doctrine, `pytest`, `app.routes` et `app.openapi()`.

## 4h. Reintroduction Guard

- Guard target:
  - aucun champ `default_valence`, `interpretive_valence`, `energy_type` ou `interpretive_weight` dans les modules structurels cibles;
  - aucun champ `meaning`, `narrative`, `prompt` ou `llm` dans calculateur, contrats structurels ou builder structurel d'aspects;
  - aucun resolver interpretatif ne recalcule angle, orbe, seuil ou force;
  - aucune projection publique ne lit la valence depuis un runtime structurel hybride;
  - aucun node natal ne transmet un profil interpretatif a un calculateur structurel;
  - aucun changement volontaire de `app.routes`, `app.openapi()` ou payload public;
  - aucun changement DB, migration, frontend, prompt ou feature flag permanent.
- Guard mechanism:
  - tests unitaires des contrats de calcul et runtime;
  - tests de resolver de hints interpretatifs;
  - tests de `ChartInterpretationInputBuilder`, `json_builder`, dominance, pattern et prediction;
  - tests d'architecture AST sur modules structurels d'aspects;
  - scans cibles des termes interdits dans modules structurels;
  - preuve OpenAPI par `app.routes`, `app.openapi()` et `TestClient`.
- Guard owner:
  - `backend/tests/unit/domain/astrology/test_aspect_calculation_contracts.py`;
  - `backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`;
  - `backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py`;
  - `backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - `backend/tests/architecture/test_chart_interpretation_input_boundary.py`.
- Guard evidence:
  - chemin complet `pytest -q backend/tests/unit/domain/astrology/test_aspect_calculation_contracts.py`;
  - chemin complet `pytest -q backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py`;
  - chemin complet `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`;
  - token runtime `AST guard`, `app.routes`, `app.openapi()` et `TestClient`.

## 4i. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation evidence | `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/evidence/validation.md` | Conserver tests, lint et scans CS-230. |
| API neutrality evidence | `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/evidence/openapi-routes.md` | Conserver routes, OpenAPI et TestClient. |
| Aspect hints proof | `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/evidence/aspect-hints-boundary.md` | Prouver separation structurel/hints. |

## 5. Current State Evidence

- Le brief indique que `AspectDefinitionRuntimeData` porte `default_valence`, `interpretive_valence`, `energy_type` et `interpretive_weight`.
- Le brief indique que `AspectCalculationResult` transporte encore valence et energy type.
- Le brief indique que `AspectRuntimeData.interpretation` sert encore de bloc hybride vers interpretation et prediction.
- Le chemin actuel melange reference aspect, resultat de calcul, runtime, JSON chart, input interpretation et prediction.
- CS-229 a deja defini les couches `structural runtime`, `interpretive runtime`, `public projection` et `legacy projection`.
- Evidence 1: `_story_briefs/cs-230-migrate-aspect-runtime-to-structural-and-hints.md` - demande migration effective des consommateurs.
- Evidence 2: `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/00-story.md` - fournit contrats cibles et story de transition.
- Evidence 3: `_condamad/stories/CS-228-migrate-natal-runtime-to-calculation-graph/00-story.md` - documente neutralite API pendant migration runtime.
- Evidence 4: `backend` existe dans l'arborescence courante.
- Evidence 5: `.agents/skills/condamad-story-writer/scripts/condamad_story_validate.py` existe.
- Evidence 6: `.agents/skills/condamad-story-writer/scripts/condamad_story_lint.py` existe.
- Evidence 7: `.agents/skills/condamad-story-writer/SKILL.md` est absent; la story suit le brief, CS-229 et les diagnostics.

## 6. Target State

- Le calculateur d'aspects retourne une forme structurelle sans valence ni energy type.
- `AspectDefinitionRuntimeData` est separe entre definition structurelle et profil interpretatif.
- `AspectStructuralRuntimeData` represente les faits calculatoires d'aspect.
- `AspectInterpretiveHintResolver` produit les hints depuis runtime structurel et profil interpretatif.
- Le builder d'aspects construit le runtime structurel sans bloc interpretatif primaire.
- `ChartInterpretationInputBuilder` consomme les hints interpretatifs.
- `json_builder` expose les champs publics historiques depuis hints ou projection publique dediee.
- `natal_calculation_nodes` ne transmet pas de vue interpretative aux calculateurs structurels.
- Dominance, pattern runtime et prediction restent compatibles sans relire la valence depuis structurel.
- Les tests d'architecture bloquent la reintroduction des champs interpretatifs dans les modules structurels cibles.

## 6a. Regression Guardrails

Scope vector:

- backend-domain: yes;
- runtime-contracts: yes;
- astrology aspects: yes;
- interpretation hints: yes;
- prediction boundary: limited;
- API: no public delta;
- DB/migrations: no;
- frontend/style/build/i18n/auth: no.

Selected guardrails:

| ID | Applicability | Story-local use |
|---|---|---|
| RG-098 | local | `AspectStrengthRuntimeData` reste une force technique; le resolver ne modifie pas les raisons de force. |
| RG-099 | local | La projection publique des aspects conserve les champs historiques et les alimente depuis la surface canonique dediee. |
| RG-100 | local | L'assemblage interpretatif reste owner des profils et ne devient pas un calculateur structurel. |
| RG-101 | local | Dominance et inter-chart reutilisent le runtime et les referentiels d'aspects existants sans duplication. |
| RG-102 | local | La couche semantique des aspects reste separee du renderer editorial et des appels LLM. |
| RG-145 | local | Le moteur d'aspects continue a consommer les objets du theme via les frontieres chart-object, sans revenir aux collections legacy. |

Non-applicable examples:

- DB/migration guardrails: hors scope, aucune table ni migration Alembic n'est modifiee.
- Frontend/style/build guardrails: hors scope, aucun fichier React, CSS ou build n'est touche.
- Auth/i18n guardrails: hors scope, aucune authentification ou localisation n'est modifiee.

Registry gap:

- Aucun guardrail global dedie a l'interdiction des hints interpretatifs dans `AspectCalculationResult` structurel n'existe encore.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | Le calculateur produit un resultat sans champs interpretatifs. | `test_aspect_calculation_contracts.py`; AST guard. |
| AC2 | Le runtime structurel ne contient plus `interpretation` comme source primaire. | `test_aspect_runtime_builder.py`; AST guard. |
| AC3 | Un resolver ou adapter produit les hints interpretatifs d'aspects. | `test_aspect_interpretive_hint_resolver.py`; runtime pytest. |
| AC4 | Le JSON natal public conserve les champs interpretatifs historiques. | `pytest -q backend/app/tests/unit/test_chart_json_builder.py`; `app.openapi()`; `TestClient`. |
| AC5 | L'input interpretatif consomme les hints dedies. | `pytest -q backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_builder.py`; AST guard. |
| AC6 | Les tests d'architecture bloquent le retour des champs deplaces. | `pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py`; AST guard. |
| AC7 | Les usages prediction restent alimentes via projection ou contrat dedie. | `test_chart_interpretation_input_boundary.py`; scan prediction. |
| AC8 | Les nodes natals ne transmettent pas de vue interpretative aux calculateurs. | `test_natal_calculation_graph_execution.py`; AST guard. |

## 8. Implementation Tasks

- [x] Task: lire les contrats CS-229, le calculateur d'aspects, le builder, les nodes natals et les consommateurs cites. (AC: AC1, AC2, AC8)
- [x] Task: classer chaque usage de valence en structurel, hint interpretatif, projection publique, prediction contract, legacy temporaire ou test. (AC: AC1, AC7)
- [x] Task: separer `AspectDefinitionRuntimeData` en definition structurelle et profil interpretatif. (AC: AC1, AC3)
- [x] Task: migrer `AspectCalculationResult` vers une forme structurelle sans champs interpretatifs primaires. (AC: AC1)
- [x] Task: creer `AspectInterpretiveHintResolver` avec commentaire global et docstrings en francais. (AC: AC3)
- [x] Task: migrer `build_aspect_runtime_data` vers un builder structurel sans bloc interpretatif primaire. (AC: AC2)
- [x] Task: borner toute facade legacy `AspectRuntimeData.interpretation` et l'alimenter depuis les hints. (AC: AC2, AC3)
- [x] Task: migrer `ChartInterpretationInputBuilder` pour consommer les hints. (AC: AC5)
- [x] Task: migrer `json_builder` pour conserver les champs publics depuis hints ou projection dediee. (AC: AC4)
- [x] Task: aligner `natal_calculation_nodes` et les mappers de referentiel avec les deux vues. (AC: AC1, AC3, AC8)
- [x] Task: verifier `dominant_aspects` et `pattern_runtime` sans dependance aux hints interpretatifs. (AC: AC6)
- [x] Task: migrer les usages prediction de valence vers contrat dedie ou hints. (AC: AC7)
- [x] Task: ajouter les tests unitaires du calculateur, du builder structurel et du resolver. (AC: AC1, AC2, AC3)
- [x] Task: ajouter ou mettre a jour les tests JSON public et input interpretation. (AC: AC4, AC5)
- [x] Task: ajouter les tests dominance, pattern runtime et prediction. (AC: AC6, AC7)
- [x] Task: ajouter l'AST guard anti-retour dans les modules structurels cibles. (AC: AC1, AC2, AC6, AC8)
- [x] Task: ajouter la preuve `app.routes`, `app.openapi()` et `TestClient` de neutralite API. (AC: AC4)
- [x] Task: collecter l'evidence finale dans le dossier CS-230. (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8)

## 9. Mandatory Reuse / DRY Constraints

- Reutiliser les contrats CS-229 lorsqu'ils existent.
- Reutiliser `AspectStructuralRuntimeData`, `AspectStrengthRuntimeData` et les contrats participants/orbe existants.
- Reutiliser les profils d'aspects existants pour produire les hints.
- Reutiliser les builders et mappers actuels comme points d'integration.
- Reutiliser les tests existants d'aspects, interpretation, JSON public, graph natal, dominance et prediction.
- Ne pas creer un second calculateur d'aspects.
- Ne pas dupliquer les referentiels `astral_aspect_*` dans des constantes locales.
- Ne pas creer un second serializer public concurrent au JSON natal actuel.

## 10. No Legacy / Forbidden Paths

- Ne pas modifier le frontend.
- Ne pas ajouter de migration Alembic.
- Ne pas changer de route FastAPI, schema public, serializer public ou OpenAPI.
- Ne pas ajouter de dependance externe.
- Ne pas changer les scores, orbes, profils, dominance, pattern runtime ou doctrine astrologique.
- Ne pas supprimer les champs publics `interpretive_valence` et `energy_type` dans CS-230.
- Ne pas supprimer toutes les surfaces legacy du `NatalResult` dans CS-230.
- Ne pas ajouter de compatibility wrapper public ou prive non borne.
- Ne pas conserver de pont legacy non borne.
- Ne pas ajouter de fallback silencieux.
- Ne pas produire de prompt, texte narratif, appel LLM ou renderer editorial dans le runtime structurel.
- Ne pas ajouter `default_valence`, `interpretive_valence`, `energy_type` ou `interpretive_weight` a un contrat structurel.
- Ne pas brancher un calculateur structurel sur un profil interpretatif.
- Ne pas recalculer l'orbe, l'angle ou la force dans le resolver de hints.
- Ne pas utiliser un dictionnaire libre pour remplacer les contrats types.

## 11. Generated Contract Check

- Capture before:
  - `app.routes`;
  - `app.openapi()`;
  - un smoke `TestClient` sur OpenAPI;
  - un endpoint natal public couvert par les tests existants;
  - un payload natal qui contient `interpretive_valence` et `energy_type`.
- Capture after:
  - memes preuves.
- Expected result:
  - aucun endpoint, method, status code, schema public ou cle JSON publique ne change volontairement.

## 12. Files to Inspect First

- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`.
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`.
- `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py`.
- `backend/app/domain/astrology/calculators/aspects.py`.
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`.
- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py`.
- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py`.
- `backend/app/domain/astrology/interpretation/dominant_aspects.py`.
- `backend/app/domain/astrology/runtime/dominant_aspect_runtime_data.py`.
- `backend/app/domain/astrology/runtime/pattern_runtime_data.py`.
- `backend/app/services/chart/json_builder.py`.
- `backend/app/domain/prediction`.
- `backend/app/services/prediction`.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`.
- `backend/app/infra/db/repositories/reference_repository.py`.
- `_condamad/stories/regression-guardrails.md` avec recherche ciblee `RG-098|RG-099|RG-100|RG-101|RG-102|RG-145`.

## 13. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py`.
- `backend/app/domain/astrology/calculators/aspects.py`.
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`.
- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`.
- `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py`.
- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py`.
- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py`.
- `backend/app/services/chart/json_builder.py`.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`.
- `backend/app/infra/db/repositories/reference_repository.py`.
- `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/evidence/validation.md`.
- `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/evidence/openapi-routes.md`.
- `_condamad/stories/CS-230-migrate-aspect-runtime-to-structural-and-hints/evidence/aspect-hints-boundary.md`.

Likely tests:

- `backend/tests/unit/domain/astrology/test_aspect_calculation_contracts.py`.
- `backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py`.
- `backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py`.
- `backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_builder.py`.
- `backend/app/tests/unit/test_chart_json_builder.py`.
- `backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py`.
- `backend/tests/unit/domain/astrology/test_dominant_aspects.py`.
- `backend/tests/unit/domain/astrology/test_pattern_runtime_contract.py`.
- `backend/tests/architecture/test_aspect_runtime_boundary.py`.
- `backend/tests/architecture/test_chart_interpretation_input_boundary.py`.
- `backend/tests/architecture/test_api_contract_neutrality.py`.

Files not expected to change:

- `frontend/src`.
- `backend/alembic`.
- `backend/app/api`.
- prompt templates and LLM providers.
- `astral_aspect_profiles.json` values.

## 14. Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## 15. Validation Plan

Run all Python commands from repository root after activating the venv:

```powershell
.\.venv\Scripts\Activate.ps1
ruff format backend
ruff check backend
pytest -q backend/tests
```

Run targeted tests:

```powershell
pytest -q backend/tests/unit/domain/astrology/test_aspect_calculation_contracts.py
pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py
pytest -q backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py
pytest -q backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_builder.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py
pytest -q backend/tests/unit/domain/astrology/test_dominant_aspects.py
pytest -q backend/tests/unit/domain/astrology/test_pattern_runtime_contract.py
pytest -q backend/tests/architecture/test_aspect_runtime_boundary.py
pytest -q backend/tests/architecture/test_chart_interpretation_input_boundary.py
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

Run anti-regression scans:

```powershell
rg -n "default_valence|interpretive_valence|energy_type|interpretive_weight|meaning|narrative|prompt|llm" `
  backend/app/domain/astrology/runtime backend/app/domain/astrology/calculators backend/app/domain/astrology/builders -g "*.py"
rg -n "AspectInterpretiveHintResolver|AspectInterpretiveHintsRuntimeData|AspectStructuralRuntimeData" backend/app/domain/astrology backend/tests -g "*.py"
rg -n "default_valence|interpretive_valence|energy_type" backend/app/domain/prediction backend/app/services/prediction backend/app/services/chart -g "*.py"
git diff -- backend/app/api backend/alembic frontend/src
```

Run API neutrality proof:

```powershell
pytest -q backend/tests/architecture/test_api_contract_neutrality.py
```

The dedicated API neutrality evidence must name `app.routes`, `app.openapi()` and `TestClient`.

## 16. Regression Risks

- Un calculateur structurel peut continuer a produire valence ou energy type.
- Un profil interpretatif peut rester transmis aux calculateurs via les mappers de referentiel.
- Un resolver de hints peut recalculer orbe ou force.
- `json_builder` peut perdre les champs publics historiques.
- `ChartInterpretationInputBuilder` peut continuer a lire le bloc legacy hybride.
- Prediction peut relire le runtime structurel au lieu d'un contrat de hints.
- Le graph natal peut propager une vue interpretative aux nodes structurels.

## 17. Dev Agent Instructions

- Commencer par lire les fichiers de `Files to Inspect First`.
- Implement only CS-230.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Implementer le plus petit delta coherent.
- Garder les commentaires globaux et docstrings en francais dans les nouveaux fichiers applicatifs.
- Ne pas utiliser de style inline, CSS ou frontend: aucun fichier frontend n'est attendu.
- Ne pas creer de `requirements.txt`.
- Executer les validations apres activation du venv.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker in story evidence.
- Do not preserve legacy behavior through an unbounded fallback, shim or compatibility layer.
- Conserver dans l'evidence les commandes lancees, les resultats de tests, les scans et la preuve `app.routes` / `app.openapi()`.

## 18. CS-230 Final Evidence Template

```markdown
## CS-230 Final Evidence

### Structural Runtime
- Aspect calculation result contains only structural facts.
- Aspect structural runtime does not carry interpretive fields.
- Natal graph nodes pass structural views to calculators.

### Interpretive Hints
- AspectInterpretiveHintResolver produces typed hints.
- Resolver does not recalculate angle, orb or strength.
- ChartInterpretationInputBuilder consumes hints.

### Compatibility
- Public JSON still exposes interpretive_valence and energy_type.
- Prediction receives valence through hints or dedicated contract.
- app.routes, app.openapi() and TestClient are captured.

### Guardrails
- AST guard blocks interpretive fields in structural modules.
- Scans cover valence, energy_type, meaning, narrative, prompt and llm.

### Commands
- ruff format backend
- ruff check backend
- pytest -q backend/tests
- targeted aspect migration tests
```

## 19. Story Generation Validation Notes

- Story generated from `_story_briefs/cs-230-migrate-aspect-runtime-to-structural-and-hints.md`.
- Fast Story Writer Mode applied.
- The requested cheatsheet path was missing in this workspace, so the story uses the brief, adjacent CS-229 structure and validator diagnostics.
- `resolve_guardrails.py` is unavailable; guardrails were selected by targeted ID search only.
- No regression guardrail registry update was made.
- Story validation result after correction cycle: PASS.
- Strict lint result after correction cycle: PASS.

## 20. References

- Source brief: `_story_briefs/cs-230-migrate-aspect-runtime-to-structural-and-hints.md`.
- Story tracker: `_condamad/stories/story-status.md`.
- Guardrail registry: `_condamad/stories/regression-guardrails.md` (`RG-098`, `RG-099`, `RG-100`, `RG-101`, `RG-102`, `RG-145`).
- Previous story: `_condamad/stories/CS-229-aspect-runtime-structural-interpretive-contracts/00-story.md`.
