# Story CS-216 advanced-planetary-conditions-interpretation-profiles: Structurer les profils interpretatifs des conditions planetaires avancees

Status: done

## 1. Objective

Introduire une couche symbolique structuree et pre-narrative pour les
conditions planetaires avancees afin que le runtime natal puisse exposer, par
planete, des profils interpretatifs immuables couvrant mots-cles, themes,
manifestations, axes psychologiques, axes comportementaux, polarite et
intensite. La story ne doit produire aucun texte final utilisateur, aucun
prompt, aucun scoring et aucune projection publique dediee.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-22 pour `CS-216 - Advanced
  Planetary Conditions Interpretation Profiles`.
- Reason for change: CS-214 expose les conditions planetaires avancees dans le
  runtime natal et CS-215 les consomme pour les dignites accidentelles, mais il
  manque une couche de vocabulaire astrologique structuree entre calcul factuel
  et futurs moteurs narratifs.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story conserve la separation demandee
  `calcul != profil symbolique != interpretation narrative`. Les AC couvrent
  contrats, catalogue, runtime de resolution, priorite
  `planet + tradition -> planet generic -> tradition generic -> global
  generic`, integration runtime natal, multiples profils, conditions absentes,
  profils manquants, absence de scoring, absence de texte final utilisateur,
  absence de prompt/LLM/API/DB/frontend et tests unitaires.
- Brief-stakes alignment: l'enjeu est de preparer les futurs moteurs narratifs,
  prompts LLM, renderers, analyses explicatives et systemes de synthese sans
  les implementer. La story cree donc uniquement des blocs symboliques
  deterministes exploitables plus tard.
- Brief pipeline alignment: la cible du brief
  `calculs astronomiques -> conditions avancees -> dignites -> profils
  interpretatifs -> moteur narratif futur` est conservee: CS-216 consomme les
  faits runtime CS-214 et reste apres CS-215 sans modifier le scoring.
- Brief target-file resolution: le brief autorise `AdvancedPlanetaryConditionsResult`
  ou `NatalResult`; le repo et les tests existants placent l'exposition interne
  sur `NatalResult` dans `natal_calculation.py`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/interpretation`
- In scope:
  - creer
    `backend/app/domain/astrology/interpretation/advanced_conditions/contracts.py`;
  - creer
    `backend/app/domain/astrology/interpretation/advanced_conditions/advanced_condition_profile_catalog.py`;
  - creer
    `backend/app/domain/astrology/interpretation/advanced_conditions/profile_runtime.py`;
  - creer `__init__.py` dans le nouveau sous-package pour les exports
    explicites;
  - definir `AdvancedConditionInterpretationProfile`,
    `InterpretationPolarity` et `InterpretationIntensity`;
  - couvrir les conditions minimales `combust`, `cazimi`, `retrograde`,
    `stationary`, `under_beams`, `invisible`, `emerging`, `oriental`,
    `occidental`, `full_moon` et `new_moon`;
  - supporter les profils globaux, par planete, par tradition, par polarite et
    mixtes planete+tradition;
  - resoudre les profils depuis `PlanetaryConditionsBundle` et
    `MoonPhaseCondition`;
  - enrichir le runtime natal avec
    `interpretation_profiles_by_planet` comme mapping de planete vers tuple
    immutable de `AdvancedConditionInterpretationProfile`
    strictement interne;
  - ajouter les tests unitaires cibles du runtime de resolution;
  - ajouter un commentaire global en francais et des docstrings francaises dans
    les fichiers applicatifs nouveaux ou significativement modifies.
- Out of scope:
  - generation narrative finale;
  - prompts, LLM, IA, OpenAI ou orchestration de modele;
  - rendering UI, frontend, TypeScript ou composants React;
  - endpoint API dedie, schema FastAPI volontaire, OpenAPI volontaire ou client
    genere;
  - DB, migrations, seeders, repositories ou persistence;
  - scoring, deltas de score, poids de force ou modification des dignites;
  - nouveaux calculateurs astronomiques ou recalcul des conditions avancees;
  - modification des profils de scoring CS-215;
  - paragraphes editoriaux, analyse redigee ou texte final utilisateur.
- Explicit non-goals:
  - ne pas modifier `backend/app/domain/astrology/dignities/**`;
  - ne pas modifier `backend/app/domain/astrology/planetary_conditions/**` sauf
    si une annotation de type minimale devient inevitable et doit etre
    documentee comme blocker;
  - ne pas modifier `backend/app/domain/astrology/advanced_conditions/**`;
  - ne pas modifier `backend/app/domain/astrology/interpretation_adapters/**`;
  - ne pas modifier `backend/app/services/chart/json_builder.py`;
  - ne pas modifier `backend/app/api/**`, `backend/app/infra/**`,
    `backend/migrations/**` ou `frontend/src/**`;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas creer shim, alias, fallback silencieux, second runtime de
    conditions avancees ou second owner des conditions factuelles;
  - ne pas changer les invariants `RG-135` a `RG-142`.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story cree un sous-package de profils symboliques dans
  le domaine interpretation et branche un resultat interne au runtime natal;
  aucun archetype API, migration, suppression, route, namespace ou scoring ne
  couvre exactement ce cas.
- Additional validation rules:
  - les nouveaux modules doivent rester purs, deterministes, sans IO, sans DB,
    sans API, sans settings, sans logging et sans appel ephemeride;
  - le runtime de resolution consomme uniquement `PlanetaryConditionsBundle`,
    `MoonPhaseCondition` et un `tradition_key` optionnel;
  - les profils doivent rester des briques symboliques courtes: polarite,
    intensite, tuples de mots-cles, themes, manifestations, axes et notes;
  - les manifestations et notes ne doivent pas devenir des paragraphes de
    lecture utilisateur;
  - le runtime ne doit jamais arbitrer une contradiction de polarite; il expose
    tous les profils applicables;
  - les conditions absentes `motion=None`, `visibility=None`,
    `solar_proximity=None`, `solar_phase_relation=None` et `moon_phase=None`
    doivent etre tolerees;
  - les profils manquants doivent appliquer la resolution contractuelle
    explicite de la section 4f quand un profil generique statique existe, sans
    creer de texte invente a l'execution.
- Behavior change allowed: constrained
- Behavior change constraints:
  - nouveau comportement autorise: `NatalResult` expose
    `interpretation_profiles_by_planet` en champ runtime interne exclu du
    schema public;
  - le calcul des conditions avancees, les dignites, les scores, la projection
    publique JSON, l'API, la DB et le frontend ne changent pas volontairement.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: l'enrichissement runtime ne peut pas etre fait
  sans modifier volontairement API, OpenAPI, JSON public, DB, migrations,
  frontend ou scoring; le dev agent doit bloquer au lieu d'elargir le scope.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le runtime de resolution et le champ natal doivent prouver la verite consommee par les futures couches narratives. |
| Baseline Snapshot | yes | Les surfaces CS-214/CS-215 et le runtime natal doivent etre compares avant/apres pour eviter scoring, API ou projection publique. |
| Ownership Routing | yes | Les faits restent dans `planetary_conditions`, le scoring dans `dignities`, les profils symboliques dans `interpretation/advanced_conditions`. |
| Allowlist Exception | yes | Aucune exception shim/fallback/compatibilite n'est autorisee; toute exception doit bloquer. |
| Contract Shape | yes | La forme des dataclasses, enums, catalogue, fonction publique et champ runtime est le coeur de la story. |
| Batch Migration | no | Aucun consommateur existant n'est migre par lots. |
| Reintroduction Guard | yes | Les scans doivent bloquer texte final, scoring, prompt/LLM, API, DB, frontend et recalcul des conditions. |
| Persistent Evidence | yes | Les tests, scans et snapshots doivent etre conserves dans l'evidence de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `resolve_advanced_condition_profiles`;
  - `AdvancedConditionInterpretationProfile`;
  - `NatalResult.interpretation_profiles_by_planet`.
- Pipeline source of truth:
  - `AdvancedPlanetaryConditionsResult.conditions_by_planet` fournit les
    bundles factuels par planete;
  - `AdvancedPlanetaryConditionsResult.moon_phase` fournit la phase lunaire
    globale;
  - le catalogue fournit les profils statiques, sans construction dynamique de
    texte.
- Runtime artifacts:
  - `backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py`;
  - `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py`
    si le champ est ajoute sur `NatalResult`.
  - AST guard artifact:
    `backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py`
    doit verifier la forme contractuelle, les fragments courts et les
    interdits de texte final.
- Secondary evidence:
  - scans anti-scoring, anti-prompt/LLM, anti-API/DB/frontend et anti-texte
    final;
  - tests CS-214 et CS-215 maintenus;
  - `ruff check .` et `pytest -q`.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas la priorite de resolution, la resolution generique, les
    multiples profils, les conditions absentes ou l'enrichissement natal.
- Forbidden sources:
  - API, infra, DB, migrations, services chart, frontend, scoring, prompts,
    LLM et recalcul astronomique.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/planetary_conditions/contracts.py`;
  - `Get-Content backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`;
  - `Get-Content backend/app/domain/astrology/dignities/advanced_condition_modifiers.py`;
  - `Get-Content backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py`;
  - `Get-Content backend/app/domain/astrology/natal_calculation.py`;
  - `Test-Path backend/app/domain/astrology/interpretation/advanced_conditions/contracts.py`;
  - `rg -n "interpretation_profiles_by_planet|AdvancedConditionInterpretationProfile|resolve_advanced_condition_profiles" backend/app backend/tests -g "*.py"`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137|RG-138|RG-139|RG-140|RG-141|RG-142|RG-143"`.
- Comparison after implementation:
  - `Test-Path backend/app/domain/astrology/interpretation/advanced_conditions/contracts.py`;
  - `Test-Path backend/app/domain/astrology/interpretation/advanced_conditions/profile_runtime.py`;
  - `Test-Path backend/app/domain/astrology/interpretation/advanced_conditions/advanced_condition_profile_catalog.py`;
  - `rg -n "AdvancedConditionInterpretationProfile|resolve_advanced_condition_profiles|interpretation_profiles_by_planet" backend/app/domain/astrology backend/tests -g "*.py"`;
  - targeted pytest commands listed in the Validation Plan;
  - diff adjacent sur `dignities`, `planetary_conditions`, `json_builder.py`,
    API, infra, migrations et frontend.
- Expected invariant:
  - les conditions avancees restent factuelles;
  - les dignites accidentelles restent proprietaires du scoring;
  - la nouvelle couche produit uniquement des profils symboliques structures;
  - aucun texte final, prompt, LLM, API, DB ou frontend n'est ajoute.
- Allowed differences:
  - nouveau sous-package `interpretation/advanced_conditions`;
  - exports publics explicites du nouveau sous-package;
  - ajout interne sur `NatalResult`;
  - branchement minimal dans `calculate_natal_chart` pour renseigner les
    profils;
  - nouveaux tests et evidence.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Conditions avancees factuelles | `backend/app/domain/astrology/planetary_conditions` | `interpretation/advanced_conditions` ne recalcule pas ces faits |
| Scoring accidentel issu des conditions | `backend/app/domain/astrology/dignities` | `interpretation/advanced_conditions` |
| Profils symboliques des conditions avancees | `backend/app/domain/astrology/interpretation/advanced_conditions` | `planetary_conditions`, `dignities`, API, services, frontend |
| Resolution profil depuis bundle | `interpretation/advanced_conditions/profile_runtime.py` | `natal_calculation.py`, `json_builder.py`, frontend |
| Catalogue statique de vocabulaire | `interpretation/advanced_conditions/advanced_condition_profile_catalog.py` | constantes dispersees dans runtime ou tests |
| Injection dans le theme natal | `backend/app/domain/astrology/natal_calculation.py` | API, services chart, DB |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-216. | Politique permanente sans exception. |

Validation rule:

- Toute exception requise doit bloquer l'implementation et exiger une decision
  utilisateur; aucune exception wildcard, dossier entier, fallback silencieux ou
  compatibilite transitoire ne doit etre ajoutee.

## 4f. Contract Shape

- Contract type:
  - enums `StrEnum` pour polarite et intensite;
  - dataclass immutable de profil interpretatif;
  - catalogue immutable de profils;
  - fonction pure retournant un tuple de profils.
- Fields:
  - `AdvancedConditionInterpretationProfile.condition_key`;
  - `AdvancedConditionInterpretationProfile.planet_key`;
  - `AdvancedConditionInterpretationProfile.tradition_key`;
  - `AdvancedConditionInterpretationProfile.polarity`;
  - `AdvancedConditionInterpretationProfile.intensity`;
  - `AdvancedConditionInterpretationProfile.keywords`;
  - `AdvancedConditionInterpretationProfile.themes`;
  - `AdvancedConditionInterpretationProfile.manifestations`;
  - `AdvancedConditionInterpretationProfile.psychological_axes`;
  - `AdvancedConditionInterpretationProfile.behavioral_axes`;
  - `AdvancedConditionInterpretationProfile.notes`.
- Required fields:
  - `condition_key: str`;
  - `polarity: InterpretationPolarity`;
  - `intensity: InterpretationIntensity`;
  - tuples immuables pour `keywords`, `themes`, `manifestations`,
    `psychological_axes`, `behavioral_axes` et `notes`;
  - `bundle: PlanetaryConditionsBundle`;
  - `moon_phase: MoonPhaseCondition | None`.
- Optional fields:
  - `planet_key: str | None`;
  - `tradition_key: str | None`;
  - `tradition_key` parametre de resolution;
  - les conditions partielles du bundle.
- Status codes:
  - aucun endpoint HTTP, methode ou status code n'est modifie.
- Serialization names:
  - aucun contrat JSON public dedie n'est ajoute volontairement;
  - si `NatalResult` est modifie, le champ doit rester interne ou exclu du
    schema public selon la convention deja utilisee pour
    `advanced_planetary_conditions`.
- Frontend type impact:
  - aucun type frontend ne change.
- Generated contract impact:
  - aucun OpenAPI, client genere, schema genere ou contrat API public n'est
    volontairement modifie.
- Public function shape:

```python
resolve_advanced_condition_profiles(
    *,
    bundle: PlanetaryConditionsBundle,
    moon_phase: MoonPhaseCondition | None,
    tradition_key: str | None = None,
) -> tuple
```

- Return type rule:
  - le tuple retourne doit etre type en implementation comme un tuple
    homogene de `AdvancedConditionInterpretationProfile`.

- Required enum values:
  - `InterpretationPolarity.POSITIVE`;
  - `InterpretationPolarity.NEGATIVE`;
  - `InterpretationPolarity.MIXED`;
  - `InterpretationPolarity.NEUTRAL`;
  - `InterpretationIntensity.LOW`;
  - `InterpretationIntensity.MODERATE`;
  - `InterpretationIntensity.HIGH`;
  - `InterpretationIntensity.EXTREME`.
- Required resolution priority:
  - planet + tradition;
  - planet generic;
  - tradition generic;
  - global generic.
- Polarity rule:
  - la polarite est portee par chaque profil via `InterpretationPolarity`;
  - elle ne devient pas un parametre de filtrage dans CS-216;
  - des entrees distinctes peuvent representer des lectures positives,
    negatives, mixtes ou neutres d'une meme condition.
- Resolution rule:
  - la resolution cherche uniquement dans le catalogue statique avec la priorite
    ci-dessus;
  - si aucune entree n'existe pour une priorite, le runtime teste la priorite
    suivante;
  - si aucune entree n'existe apres `global generic`, le runtime retourne aucun
    profil pour cette condition et ne genere jamais de profil dynamique.
- Required condition-key extraction:
  - `bundle.solar_proximity.condition_key.value` produit `cazimi`, `combust`
    ou `under_beams` quand la condition existe et qu'elle est active;
  - `bundle.motion.direction.value` produit `retrograde` ou `stationary` quand
    la direction vaut `RETROGRADE` ou `STATIONARY`;
  - `bundle.visibility.visibility_key.value` produit `invisible`, `emerging` ou
    `under_beams` quand la visibilite existe;
  - `bundle.solar_phase_relation.relation_key.value` produit `oriental` ou
    `occidental` quand la relation existe;
  - `moon_phase.phase_key.value` produit `full_moon` ou `new_moon` uniquement
    pour `bundle.planet_key == "moon"`;
  - les valeurs contractuelles `none`, `unknown`, `direct`, `visible`,
    `conjunct_solar` et les autres phases lunaires ne produisent aucun profil
    obligatoire dans CS-216.
- Condition-key order and deduplication:
  - l'ordre de collecte est proximite solaire, mouvement, visibilite, relation
    solaire, puis phase lunaire;
  - si deux familles produisent la meme cle, par exemple `under_beams`, le
    runtime ne resout cette cle qu'une seule fois pour eviter un profil duplique.
- Required minimal catalogue keys:
  - `combust`;
  - `cazimi`;
  - `retrograde`;
  - `stationary`;
  - `under_beams`;
  - `invisible`;
  - `emerging`;
  - `oriental`;
  - `occidental`;
  - `full_moon`;
  - `new_moon`.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-216 ne migre aucun consommateur par lots et ne remplace aucune
  surface publique.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans, lint, `RG-135` a `RG-143` et absence de scoring/texte final/API/DB/frontend/LLM. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher que les profils interpretatifs des conditions avancees deviennent
    un moteur narratif, un prompt, un score, une API, une DB, une projection
    publique, une duplication des calculateurs ou une derivation frontend.
- Forbidden examples in new `interpretation/advanced_conditions` modules:
  - `score`
  - `score_delta`
  - `strength_modifier`
  - `dignity_score`
  - `prompt`
  - `LLM`
  - `OpenAI`
  - `AIEngineAdapter`
  - `FastAPI`
  - `SQLAlchemy`
  - `Session`
  - `repository`
  - `json_builder`
  - `frontend`
  - `from app.api`
  - `from app.infra`
  - `from app.infrastructure`
  - `from app.services`
  - `sqlalchemy`
  - `fastapi`
  - `pydantic`
- Forbidden final-user text markers in new profile catalog:
  - `You are`
  - `This means`
  - `Votre`
  - `Vous`
  - `Cela signifie`
  - paragraph-shaped catalogue entries exceeding a bounded short-fragment
    length chosen by the implementation test.
- Forbidden duplication:
  - recalculer cazimi/combust/under beams depuis les longitudes;
  - recalculer retrogradation/stationnarite/vitesse depuis les vitesses;
  - recalculer oriental/occidental depuis les longitudes;
  - recalculer visibilite depuis proximite solaire;
  - recalculer phase lunaire depuis Soleil/Lune.
- Required guard evidence:
  - tests comportementaux;
  - scans cibles du Validation Plan;
  - diff des surfaces adjacentes obligatoire.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/stories/story-status.md` - `CS-215` est la derniere
  story numerotee et elle est enregistree comme `done`.
- Evidence 2: `_condamad/stories/CS-215-integrate-advanced-planetary-conditions-accidental-dignities/00-story.md`
  - la section follow-up annonce explicitement `CS-216 - Advanced Planetary
  Conditions Interpretation Profiles`.
- Evidence 3: `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `AdvancedPlanetaryConditionsResult`, `PlanetaryConditionsBundle` et
  `MoonPhaseCondition` existent comme contrats factuels.
- Evidence 4: `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
  - `calculate_advanced_planetary_conditions` assemble les bundles et la phase
  lunaire sans profils symboliques.
- Evidence 5: `backend/app/domain/astrology/dignities/advanced_condition_modifiers.py`
  - CS-215 a ajoute la conversion condition -> score accidentel dans le domaine
  `dignities`, qui ne doit pas devenir owner des profils symboliques.
- Evidence 6: `backend/app/domain/astrology/interpretation/` existe deja pour
  les couches semantiques astrologiques, mais aucun sous-package
  `advanced_conditions` n'existe encore.
- Evidence 7: `backend/app/domain/astrology/natal_calculation.py` expose deja
  `advanced_planetary_conditions` sur `NatalResult` en champ interne exclu du
  schema public.
- Evidence 8: `backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`
  - les tests CS-214 prouvent les bundles multiples et signaux techniques amont.
- Evidence 9: `_condamad/stories/regression-guardrails.md` - invariants
  `RG-135` a `RG-142` consultes avant cadrage; `RG-143` doit proteger la
  nouvelle couche symbolique.

## 6. Target State

After implementation:

- `AdvancedConditionInterpretationProfile`, `InterpretationPolarity` et
  `InterpretationIntensity` existent dans le sous-package canonique.
- Le catalogue contient les profils minimaux requis, au moins un profil
  specifique planete, un profil specifique tradition et des polarites explicites
  pour prouver les priorites et la structuration symbolique.
- `resolve_advanced_condition_profiles` retourne tous les profils applicables a
  une planete, avec resolution generique statique et deterministe.
- `NatalResult` expose les profils resolus par planete en runtime interne, sans
  projection publique volontaire.
- Les tests couvrent profils generiques, planete, tradition, resolution
  multiples profils, conditions absentes, profils manquants, combust,
  retrograde et phases lunaires.
- Les scans prouvent l'absence de scoring, texte final utilisateur, prompt/LLM,
  API, DB, migrations, services chart, frontend et recalcul des conditions.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-135` - les contrats factuels des conditions avancees ne doivent pas
    porter les profils symboliques ou de logique de resolution.
  - `RG-136` - la proximite solaire reste calculee uniquement par le
    calculateur existant.
  - `RG-137` - le mouvement planetaire reste calcule uniquement par le
    calculateur existant.
  - `RG-138` - la relation oriental/occidental reste calculee uniquement par le
    calculateur existant.
  - `RG-139` - la phase lunaire reste calculee uniquement par le calculateur
    existant.
  - `RG-140` - la visibilite reste calculee uniquement par le calculateur
    existant.
  - `RG-141` - l'orchestration runtime des conditions avancees reste factuelle
    et ne devient pas une couche d'interpretation.
  - `RG-142` - les modificateurs de dignite restent le seul owner du scoring
    issu des conditions avancees.
  - `RG-143` - les nouveaux profils symboliques restent pre-narratifs,
    deterministes et sans scoring ni prompt.
- Non-applicable invariants:
  - invariants hors surfaces astrology listees ci-dessus - la story ne touche
    pas routes historiques, API v1, DB, Stripe, prediction, frontend CSS ou
    prompts existants.
- Required regression evidence:
  - tests unitaires du runtime de profils;
  - test d'integration du champ natal interne si ajoute;
  - scans anti-scoring, anti-prompt/LLM, anti-API/DB/frontend, anti-texte final
    et anti-recalcul;
  - diff adjacent sur `planetary_conditions`, `dignities`, `json_builder.py`,
    API, infra, migrations et frontend.
- Allowed differences:
  - ajout du sous-package `interpretation/advanced_conditions`;
  - ajout d'un champ runtime interne pour profils par planete;
  - nouveaux tests, exports explicites et evidence.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Contrats interpretatifs immuables. | `pytest -q $profile_tests`. |
| AC2 | Catalogue avec les onze cles minimales. | `pytest -q $profile_tests`. |
| AC3 | Runtime extrait des profils depuis chaque famille contractuelle. | AST guard; `pytest -q $profile_tests`. |
| AC4 | L'ordre de priorite de resolution est respecte. | `pytest -q $profile_tests`. |
| AC5 | Resolution generique si aucun profil specifique. | `pytest -q $profile_tests`. |
| AC6 | Plusieurs profils par planete sont supportes. | `pytest -q $profile_tests`. |
| AC7 | Conditions absentes tolerees sans exception. | `pytest -q $profile_tests`. |
| AC8 | Profil specifique manquant sans blocage global. | `pytest -q $profile_tests`. |
| AC9 | `combust` inclut `hidden`, `burned`, `overpowered`. | `pytest -q $profile_tests`. |
| AC10 | `retrograde` inclut `internalized`, `revisiting`, `reprocessing`. | `pytest -q $profile_tests`. |
| AC11 | Les phases lunaires resolvent des profils dedies. | `pytest -q $profile_tests`. |
| AC12 | Runtime natal expose les profils par planete en champ interne. | AST guard; `pytest -q $natal_tests`. |
| AC13 | Aucun scoring dans les nouveaux modules. | `rg -n $forbidden_scoring $new_modules` zero hit. |
| AC14 | Les surfaces externes interdites sont absentes. | AST guard; `pytest -q $profile_tests`; scan zero hit. |
| AC15 | Aucun texte final utilisateur ni paragraphe narratif. | `pytest -q $profile_tests`; `rg -n $forbidden_final_text $new_modules`. |
| AC16 | Aucun recalcul des calculateurs CS-209 a CS-214. | `rg -n $forbidden_duplication $new_modules`; `git diff -- $adjacent_diff_paths`. |
| AC17 | `RG-143` existe dans le registre de guardrails. | `rg -n "RG-143" _condamad/stories/regression-guardrails.md`. |
| AC18 | Validation complete sous venv. | `ruff format backend`; `ruff check backend`; `pytest -q`; `evidence/validation.md`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le baseline et confirmer les owners (AC: AC1, AC12, AC13, AC14, AC16, AC17)
  - [x] Subtask 1.1 - Inspecter les fichiers listes en section 18.
  - [x] Subtask 1.2 - Documenter le baseline dans `evidence/validation.md`.
  - [x] Subtask 1.3 - Confirmer que le nouveau sous-package
    `interpretation/advanced_conditions` est absent avant creation.

- [x] Task 2 - Creer les contrats interpretatifs (AC: AC1, AC13, AC14, AC15)
  - [x] Subtask 2.1 - Creer `contracts.py` avec commentaire global en francais.
  - [x] Subtask 2.2 - Ajouter `InterpretationPolarity`,
    `InterpretationIntensity` et `AdvancedConditionInterpretationProfile`.
  - [x] Subtask 2.3 - Figer les tuples fournis et valider les cles essentielles
    sans accepter de mapping libre type `Any`.
  - [x] Subtask 2.4 - Verifier que la polarite est une propriete de profil et
    non un filtre runtime.

- [x] Task 3 - Creer le catalogue canonique (AC: AC2, AC4, AC5, AC9, AC10, AC11, AC15)
  - [x] Subtask 3.1 - Creer `advanced_condition_profile_catalog.py`.
  - [x] Subtask 3.2 - Ajouter les profils globaux minimaux requis.
  - [x] Subtask 3.3 - Ajouter au moins `Mercury combust` comme profil
    specifique planete.
  - [x] Subtask 3.4 - Ajouter au moins un profil `medieval` ou
    `hellenistic` pour prouver la resolution tradition.
  - [x] Subtask 3.5 - Utiliser des polarites explicites sur les profils du
    catalogue.
  - [x] Subtask 3.6 - Garder toutes les entrees sous forme de fragments courts,
    sans paragraphes narratifs.

- [x] Task 4 - Implementer le runtime pur de resolution (AC: AC3, AC4, AC5, AC6, AC7, AC8, AC11, AC13, AC14, AC15, AC16)
  - [x] Subtask 4.1 - Creer `profile_runtime.py`.
  - [x] Subtask 4.2 - Implementer `_build_condition_profiles`.
  - [x] Subtask 4.3 - Implementer `_resolve_planet_specific_profiles`.
  - [x] Subtask 4.4 - Implementer `_resolve_tradition_profiles`.
  - [x] Subtask 4.5 - Implementer `_resolve_generic_profiles`.
  - [x] Subtask 4.6 - Garantir la priorite de resolution et la tolerance aux
    conditions absentes.
  - [x] Subtask 4.7 - Exporter explicitement les symboles publics depuis
    `__init__.py`.

- [x] Task 5 - Integrer au runtime natal (AC: AC12, AC13, AC14, AC16)
  - [x] Subtask 5.1 - Ajouter le champ interne
    `interpretation_profiles_by_planet` a `NatalResult`.
  - [x] Subtask 5.2 - Appeler `resolve_advanced_condition_profiles` depuis le
    pipeline natal apres calcul des conditions avancees.
  - [x] Subtask 5.3 - Ne pas coder de logique detaillee de conditions dans
    `natal_calculation.py`; la resolution reste dans `profile_runtime.py`.
  - [x] Subtask 5.4 - Exclure le champ du schema public si la convention du
    runtime natal l'exige.

- [x] Task 6 - Ajouter les tests (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC15)
  - [x] Subtask 6.1 - Creer
    `backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py`.
  - [x] Subtask 6.2 - Couvrir generic profiles, planet profiles, tradition
    profiles, polarity fields, generic resolution, multiple profiles, missing
    profiles, combust, retrograde, stationary, visibility, solar phase, moon
    phases et deduplication `under_beams`.
  - [x] Subtask 6.3 - Ajouter ou etendre un test `NatalResult` pour le champ
    interne si le runtime natal est modifie.
  - [x] Subtask 6.4 - Ajouter une assertion anti-texte final sur les fragments
    du catalogue.

- [x] Task 7 - Ajouter les guardrails anti-drift et valider (AC: AC13, AC14, AC15, AC16, AC17, AC18)
  - [x] Subtask 7.1 - Verifier `RG-143` dans
    `_condamad/stories/regression-guardrails.md`.
  - [x] Subtask 7.2 - Executer les scans interdits du Validation Plan.
  - [x] Subtask 7.3 - Executer les tests cibles, `ruff format backend`,
    `ruff check backend` et `pytest -q` sous venv.
  - [x] Subtask 7.4 - Documenter commandes, resultats et risques residuels dans
    `evidence/validation.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetaryConditionsBundle`, `MoonPhaseCondition` et les enums depuis
    `planetary_conditions/contracts.py`;
  - `AdvancedPlanetaryConditionsResult` produit par CS-214;
  - le champ `NatalResult.advanced_planetary_conditions` comme source de faits
    deja calcules;
  - conventions d'exclusion schema deja utilisees dans `NatalResult` pour les
    champs internes;
  - conventions existantes du package `backend/app/domain/astrology/interpretation`.
- Do not recreate:
  - les contrats `planetary_conditions`;
  - les calculateurs de proximite solaire, mouvement, relation solaire,
    visibilite ou phase lunaire;
  - les modificateurs de score CS-215;
  - un moteur d'ephemerides;
  - une projection JSON publique des conditions avancees;
  - un moteur narratif, un prompt ou un renderer.
- Shared abstraction allowed only if:
  - elle reste dans `interpretation/advanced_conditions`;
  - elle supprime une duplication reelle dans la resolution de profils;
  - elle ne cree pas de second catalogue concurrent.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export
- second condition runtime
- second scoring engine
- broad allowlist
- `PASS with limitation`

Specific forbidden symbols / paths:

- `score`
- `score_delta`
- `strength_modifier`
- `dignity_score`
- `prompt`
- `LLM`
- `OpenAI`
- `AIEngineAdapter`
- `FastAPI`
- `SQLAlchemy`
- `Session`
- `repository`
- `json_builder`
- `frontend`
- `from app.api`
- `from app.infra`
- `from app.infrastructure`
- `from app.services`
- `sqlalchemy`
- `fastapi`
- `pydantic` dans les nouveaux modules `interpretation/advanced_conditions`
- `You are`
- `This means`
- `Votre`
- `Vous`
- `Cela signifie`

Specific forbidden production modifications unless explicitly justified by the
scope:

- `backend/app/domain/astrology/dignities/**` - aucun scoring ne change.
- `backend/app/domain/astrology/planetary_conditions/**` - aucun fait ou
  calculateur de condition ne change.
- `backend/app/domain/astrology/advanced_conditions/**` - ne pas reutiliser une
  surface historique si elle existe.
- `backend/app/domain/astrology/interpretation_adapters/**` - les adaptateurs
  narratifs restent hors scope.
- `backend/app/services/chart/json_builder.py` - pas de projection volontaire.
- `backend/app/api/**`
- `backend/app/infra/**`
- `backend/migrations/**`
- `frontend/src/**`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Conditions avancees factuelles | `backend/app/domain/astrology/planetary_conditions` | `interpretation/advanced_conditions` ne recalcule pas ces faits |
| Scoring accidentel | `backend/app/domain/astrology/dignities` | `interpretation/advanced_conditions` |
| Profils symboliques pre-narratifs | `backend/app/domain/astrology/interpretation/advanced_conditions` | `planetary_conditions`, `dignities`, API, services, frontend |
| Runtime de resolution des profils | `profile_runtime.py` | `natal_calculation.py`, `json_builder.py`, frontend |
| Injection runtime natal | `natal_calculation.py` | API, services chart, DB |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Artifact Check

- Generated artifact check: not applicable
- Reason: no generated file, generated schema, generated client or generated
  documentation is intentionally affected by CS-216.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, frontend
  type or generated client is intentionally affected. If an existing OpenAPI or
  public JSON snapshot changes because `NatalResult` serialization changes, the
  dev agent must stop and record the blocker rather than expanding CS-216.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
- `backend/app/domain/astrology/planetary_conditions/signal_factory.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/app/domain/astrology/dignities/advanced_condition_modifiers.py`
- `backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/interpretation/__init__.py`
- `backend/app/domain/astrology/interpretation/profile_fields.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`
- `backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py`
- `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py`
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md`
- `_condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md`
- `_condamad/stories/CS-212-moon-phase-calculator/00-story.md`
- `_condamad/stories/CS-213-planetary-visibility-conditions-calculator/00-story.md`
- `_condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/00-story.md`
- `_condamad/stories/CS-215-integrate-advanced-planetary-conditions-accidental-dignities/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/interpretation/advanced_conditions/contracts.py`
  - nouveaux contrats interpretatifs pre-narratifs.
- `backend/app/domain/astrology/interpretation/advanced_conditions/advanced_condition_profile_catalog.py`
  - catalogue canonique des profils symboliques.
- `backend/app/domain/astrology/interpretation/advanced_conditions/profile_runtime.py`
  - runtime pur de resolution.
- `backend/app/domain/astrology/interpretation/advanced_conditions/__init__.py`
  - exports publics explicites du sous-package.
- `backend/app/domain/astrology/natal_calculation.py` - enrichissement interne
  minimal avec profils par planete.
- `_condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/evidence/validation.md`
  - preuves de validation.

Likely tests:

- `backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py`
  - couverture du catalogue et du runtime.
- `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py`
  - extension pour le champ interne si `NatalResult` est modifie.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`
  - a maintenir pour prouver que le runtime factuel reste stable.

Files not expected to change:

- `backend/app/domain/astrology/planetary_conditions/**` - conditions factuelles
  deja calculees par CS-209 a CS-214.
- `backend/app/domain/astrology/dignities/**` - scoring CS-215 hors scope.
- `backend/app/domain/astrology/advanced_conditions/**` - ne pas utiliser de
  surface historique concurrente.
- `backend/app/domain/astrology/interpretation_adapters/**` - narration future
  hors scope.
- `backend/app/services/chart/json_builder.py` - projection publique hors scope.
- `backend/app/api/**` - aucune route/schema.
- `backend/app/infra/**` - aucune persistence.
- `backend/migrations/**` - aucune migration.
- `frontend/src/**` - aucun frontend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- Justification: les dataclasses, enums, contrats existants et pytest
  suffisent.

## 21. Validation Plan

All Python commands must be run after activating the venv from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

Targeted tests:

```powershell
$profile_tests = "backend/tests/unit/domain/astrology/interpretation/advanced_conditions/test_profile_runtime.py"
$natal_tests = "backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py"
$runtime_tests = "backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py"
$modifier_tests = "backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py"
pytest -q $profile_tests
pytest -q $natal_tests
pytest -q $runtime_tests
pytest -q $modifier_tests
```

Quality checks:

```powershell
ruff format backend
ruff check backend
pytest -q
```

Required scans from repository root:

```powershell
$contracts = "backend/app/domain/astrology/interpretation/advanced_conditions/contracts.py"
$catalog = "backend/app/domain/astrology/interpretation/advanced_conditions/advanced_condition_profile_catalog.py"
$runtime = "backend/app/domain/astrology/interpretation/advanced_conditions/profile_runtime.py"
$new_modules = @($contracts, $catalog, $runtime) | Where-Object { Test-Path $_ }
$forbidden_scoring = "\\bscore\\b|score_delta|strength_modifier|dignity_score"
$forbidden_surface_terms = (
  "prompt|LLM|OpenAI|AIEngineAdapter|from app\\.api|from app\\.infra|" +
  "from app\\.infrastructure|from app\\.services|sqlalchemy|fastapi|" +
  "pydantic|FastAPI|SQLAlchemy|Session|repository|json_builder|" +
  "frontend|migrations|router"
)
$forbidden_final_text = "You are|This means|Votre|Vous|Cela signifie"
$forbidden_duplication = (
  "calculate_solar_proximity|calculate_planetary_motion|" +
  "calculate_solar_phase|calculate_planet_visibility|calculate_moon_phase|" +
  "sun_longitude|moon_longitude|ephemeris|SwissEph|swe"
)
$adjacent_diff_paths = @(
  "backend/app/domain/astrology/planetary_conditions",
  "backend/app/domain/astrology/dignities",
  "backend/app/domain/astrology/advanced_conditions",
  "backend/app/domain/astrology/interpretation_adapters",
  "backend/app/services/chart/json_builder.py",
  "backend/app/api",
  "backend/app/infra",
  "backend/migrations",
  "frontend/src"
)
rg -n $forbidden_scoring $new_modules
rg -n $forbidden_surface_terms $new_modules
rg -n $forbidden_final_text $new_modules
rg -n $forbidden_duplication $new_modules
rg -n "AdvancedConditionInterpretationProfile|resolve_advanced_condition_profiles|interpretation_profiles_by_planet" backend/app/domain/astrology backend/tests -g "*.py"
Select-String "RG-143" _condamad/stories/regression-guardrails.md
git diff -- $adjacent_diff_paths
```

Expected scan result:

- scoring: zero hits;
- prompt/LLM/API/DB/frontend/json builder: zero hits;
- texte final utilisateur: zero hits;
- duplication de calculateurs amont: zero hits;
- symbols publics: hits limites aux nouveaux modules, exports, runtime natal et
  tests;
- diff adjacent: vide sauf blocker documente.

Story validation commands:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-216-advanced-planetary-conditions-interpretation-profiles/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Skipped-command rule:

- Any skipped command must be recorded in the final evidence with exact
  command, reason, risk and fallback evidence.

## 22. Regression Risks

- Risk: les profils deviennent un texte narratif final.
  - Guardrail: AC15, tests de fragments courts, scans anti-phrases finales et
    `RG-143`.
- Risk: la couche interpretation commence a porter du scoring accidentel.
  - Guardrail: AC13, `RG-142` et scans anti-scoring.
- Risk: les conditions avancees sont recalculees dans le runtime de profils.
  - Guardrail: AC16, ownership routing et scans anti-duplication.
- Risk: l'ajout au runtime natal fuit dans la projection publique ou OpenAPI.
  - Guardrail: AC12 et generated contract blocker.
- Risk: la resolution generique masque des profils manquants par generation
  dynamique.
  - Guardrail: AC5, AC8 et interdiction de texte invente a l'execution.

## 23. Dev Agent Instructions

- Implement only CS-216.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass constraints through wrapper, alias, fallback, re-export,
  broad allowlist, unresolved marker or hidden residual work.
- Keep `interpretation/advanced_conditions` pure and deterministic.
- Consume `PlanetaryConditionsBundle` and `MoonPhaseCondition`; do not
  recalculate condition facts.
- Keep condition scoring in `dignities`, not in `interpretation`.
- Keep narrative generation, final user text, prompts, LLM, API, DB,
  migrations and frontend out of scope.
- Use French top-of-file comments/docstrings for new applicative files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unresolved task markers or hidden residual in-domain work.

## 24. Follow-up Story

- Next planned story: not assigned.
- Expected future scope: brancher ces profils symboliques dans un moteur
  narratif astrologique avance ou une projection publique dediee, avec story
  separee et contrats propres.
- Boundary: CS-216 ne produit pas cette narration et ne cree aucun prompt; les
  profils structures restent toutefois exploitables par de futurs prompts dans
  une story separee.

## 25. References

- `backend/app/domain/astrology/planetary_conditions/contracts.py` - contrats
  factuels CS-208 a consommer.
- `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
  - runtime CS-214 qui assemble les bundles et la phase lunaire.
- `backend/app/domain/astrology/dignities/advanced_condition_modifiers.py` -
  owner CS-215 du scoring accidentel issu des conditions.
- `backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py`
  - profils de deltas CS-215 a ne pas confondre avec profils symboliques.
- `backend/app/domain/astrology/natal_calculation.py` - owner actuel de
  `NatalResult` et du branchement runtime natal.
- `backend/app/domain/astrology/interpretation/profile_fields.py` - precedent
  local de champs de profil dans le domaine interpretation.
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
  - source contractuelle des conditions avancees.
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
  - precedent proximite solaire.
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md`
  - precedent mouvement planetaire.
- `_condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md`
  - precedent relation solaire.
- `_condamad/stories/CS-212-moon-phase-calculator/00-story.md` - precedent
  phase lunaire.
- `_condamad/stories/CS-213-planetary-visibility-conditions-calculator/00-story.md`
  - precedent visibilite planetaire.
- `_condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/00-story.md`
  - precedent d'integration runtime natal.
- `_condamad/stories/CS-215-integrate-advanced-planetary-conditions-accidental-dignities/00-story.md`
  - precedent de scoring accidentel et follow-up CS-216.
- `_condamad/stories/regression-guardrails.md` - invariants applicables
  `RG-135` a `RG-143`.
