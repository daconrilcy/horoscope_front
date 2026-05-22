# Story CS-215 integrate-advanced-planetary-conditions-accidental-dignities: Integrer les conditions planetaires avancees dans les dignites accidentelles

Status: done

## 1. Objective

Integrer les conditions planetaires avancees deja produites par le runtime natal
dans le calcul des dignites accidentelles, afin que combustion, cazimi,
under beams, retrogradation, stationnarite, vitesse, visibilite, relation
oriental/occidental et phase lunaire modifient le score accidentel par des
modificateurs configurables, explicables et non narratifs.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-22 pour `CS-215 - Integrate
  Advanced Planetary Conditions Into Accidental Dignities`.
- Reason for change: CS-214 expose les conditions planetaires avancees dans le
  runtime natal, mais les dignites accidentelles restent encore principalement
  structurelles et ne consomment pas ce bloc comme source de score accidentel.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story couvre le probleme du brief sans
  interpretation textuelle, UI, API, DB, LLM, nouveau calculateur de conditions
  ou dignites essentielles. Les AC exigent le moteur de modificateurs, les
  profils configurables, l'integration au score accidentel, les breakdowns, les
  cas cazimi prioritaire, stationnaire+retrograde, conditions partielles et
  Soleil sans penalite de combustion. Le brief autorise deux noms de profil;
  la story retient `advanced_condition_modifier_profiles.py` comme choix
  canonique unique pour eviter deux chemins concurrents.
- Brief pipeline alignment:
  - pipeline cible couvert:
    `positions -> aspects -> advanced planetary conditions -> accidental dignity modifiers -> accidental dignity score`;
  - CS-215 consomme le resultat CS-214 `AdvancedPlanetaryConditionsResult` et
    ne recalcule pas les positions, aspects ou conditions avancees;
  - l'enjeu "etat vivant de la planete" est traduit en modificateurs
    accidentels factuels, configurables et non narratifs.
- Brief dignity-signals resolution:
  - le brief demande d'enrichir les signaux de dignite;
  - dans le code actuel, `PlanetDignityResult` expose des scores et
    breakdowns, pas un champ `signals` dedie aux dignites;
  - CS-215 resout donc cet enjeu par des `AccidentalDignityModifier` visibles
    dans `accidental_breakdown` ou dans un champ dedie minimal de
    `PlanetDignityResult`, sans utiliser `interpretation_adapters` ni produire
    de signal narratif.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/dignities`
- In scope:
  - creer
    `backend/app/domain/astrology/dignities/advanced_condition_modifiers.py`;
  - creer
    `backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py`
    comme source unique des deltas V1;
  - creer si absent le contrat immutable `AccidentalDignityModifier`;
  - calculer les modificateurs accidentels depuis `PlanetaryConditionsBundle`
    et `MoonPhaseCondition`;
  - integrer ces modificateurs au calcul accidentel et au score final;
  - exposer les modificateurs dans les breakdowns accidentels ou dans un champ
    dedie du contrat `PlanetDignityResult`, selon la plus petite adaptation
    coherente avec le code existant;
  - garder les modificateurs additifs, independants, deterministes,
    configurables et explicables;
  - ajouter les tests unitaires du moteur et de l'integration;
  - ajouter un commentaire global en francais et des docstrings francaises dans
    les fichiers applicatifs nouveaux ou significativement modifies.
- Out of scope:
  - interpretation textuelle, signification editoriale ou narration;
  - rendering, UI, frontend, TypeScript ou composants React;
  - endpoint API dedie, schema FastAPI volontaire, OpenAPI volontaire ou client
    genere;
  - DB, migrations, seeders, repositories ou persistance;
  - dignites essentielles;
  - scoring psychologique, karmique ou LLM;
  - nouveaux calculateurs de conditions planetaires;
  - visibilite astronomique reelle;
  - modification des calculateurs CS-209 a CS-214 sauf correction bloquante
    strictement necessaire et documentee.
- Explicit non-goals:
  - ne pas modifier `backend/app/domain/astrology/planetary_conditions/**`
    comme source de scoring;
  - ne pas ajouter de texte interpretatif, `meaning`, `interpretation`,
    `narrative`, `prompt`, `LLM`, `OpenAI` ou appel IA;
  - ne pas modifier `backend/app/services/chart/json_builder.py` sauf si le
    contrat interne `PlanetDignityResult` rend une adaptation minimale
    inevitable; dans ce cas, la projection publique ne doit pas ajouter de
    nouveau bloc narratif;
  - ne pas modifier `backend/app/api/**`, `backend/app/infra/**`,
    `backend/migrations/**` ou `frontend/src/**`;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas creer shim, alias, fallback silencieux, second moteur de dignites ou
    second contrat concurrent des conditions avancees.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story cree un moteur pur de modificateurs dans le
  domaine `dignities` et branche un contrat runtime existant au scoring
  accidentel; aucun archetype API, migration, suppression, route ou namespace
  ne couvre exactement ce cas.
- Additional validation rules:
  - `advanced_condition_modifiers.py` doit rester pur, deterministe, sans IO,
    sans DB, sans API, sans settings, sans logging et sans appel ephemeride;
  - le moteur de modificateurs consomme uniquement
    `PlanetaryConditionsBundle` et `MoonPhaseCondition`;
  - les valeurs de score doivent venir d'un profil explicite, pas de branches
    magiques dispersees;
  - les raisons doivent rester factuelles et techniques, sans interpretation
    astrologique narrative;
  - un cazimi exclut tout `combust_penalty`;
  - le Soleil ne recoit pas de penalite de combustion;
  - `motion=None`, `visibility=None`, `solar_proximity=None`,
    `solar_phase_relation=None` et `moon_phase=None` sont acceptes sans
    exception.
- Behavior change allowed: constrained
- Behavior change constraints:
  - nouveau comportement autorise: les conditions avancees modifient
    `accidental_score` et `total_score` quand elles existent;
  - les dignites essentielles et les calculateurs de conditions existants ne
    changent pas;
  - les scores structurels existants restent calcules avant ajout des
    modificateurs avances.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: le branchement des conditions avancees ne peut pas
  etre fait sans changer volontairement API, DB, migration, frontend ou contrat
  public JSON; le dev agent doit bloquer au lieu d'elargir le scope.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le score final doit prouver que les modificateurs avances sont consommes par le runtime de dignites. |
| Baseline Snapshot | yes | Les scores et breakdowns accidentels existants doivent etre compares avant/apres. |
| Ownership Routing | yes | Les conditions avancees restent dans `planetary_conditions`, leur scoring accidentel appartient a `dignities`. |
| Allowlist Exception | yes | Aucune exception shim/fallback/compatibilite n'est autorisee; toute exception doit bloquer. |
| Contract Shape | yes | La forme de `AccidentalDignityModifier`, des profils et de l'integration resultat est le coeur de la story. |
| Batch Migration | no | Aucun consommateur ou surface publique n'est migre par lots. |
| Reintroduction Guard | yes | Les scans doivent bloquer interpretation, LLM, API, DB, frontend et duplication des calculateurs de conditions. |
| Persistent Evidence | yes | Les tests, scans et snapshots doivent etre conserves dans l'evidence de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `calculate_advanced_condition_modifiers`;
  - `PlanetDignityScoringService.calculate` ou l'orchestrateur equivalent qui
    agrege le score accidentel;
  - `PlanetDignityResult.accidental_score`, `total_score` et breakdowns.
- Pipeline source of truth:
  - `AdvancedPlanetaryConditionsResult.conditions_by_planet` fournit les
    bundles par planete;
  - `AdvancedPlanetaryConditionsResult.moon_phase` fournit la phase lunaire
    globale;
  - les modificateurs avances sont ajoutes apres les matches accidentels
    structurels existants.
- Runtime artifacts:
  - tests unitaires du moteur de modificateurs;
  - tests d'integration du calcul de dignite prouvant que les modificateurs
    modifient le score final.
  - AST guard evidence:
    `pytest -q backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py`
    et
    `pytest -q backend/tests/unit/domain/astrology/dignities/test_accidental_dignity_conditions_integration.py`.
- Secondary evidence:
  - scans anti-interpretation, anti-LLM, anti-API, anti-DB et anti-frontend;
  - tests existants des calculateurs CS-209 a CS-214 maintenus;
  - `ruff check .` et `pytest -q`.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas l'addition au score, la priorite cazimi, la tolerance
    aux conditions partielles ou l'enrichissement des breakdowns.
- Forbidden sources:
  - API, infra, DB, migrations, services chart, frontend, LLM, ephemerides,
    nouveaux calculateurs de conditions et interpretation.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/dignities/contracts.py`;
  - `Get-Content backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`;
  - `Get-Content backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`;
  - `Get-Content backend/app/domain/astrology/planetary_conditions/contracts.py`;
  - `Get-Content backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`;
  - `rg -n "advanced_planetary_conditions|PlanetaryConditionsBundle|MoonPhaseCondition|AccidentalDignityModifier" backend/app/domain/astrology backend/tests -g "*.py"`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137|RG-138|RG-139|RG-140|RG-141|RG-142"`.
- Comparison after implementation:
  - `Test-Path backend/app/domain/astrology/dignities/advanced_condition_modifiers.py`;
  - `Test-Path backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py`;
  - `rg -n "calculate_advanced_condition_modifiers|AccidentalDignityModifier|advanced_condition" backend/app/domain/astrology/dignities backend/tests -g "*.py"`;
  - targeted pytest commands listed in the Validation Plan;
  - diff adjacent sur `planetary_conditions`, `json_builder.py`, API, infra,
    migrations et frontend.
- Expected invariant:
  - les calculateurs de conditions restent factuels;
  - le domaine `dignities` convertit les faits en modificateurs accidentels;
  - aucun texte interpretatif ni surface publique volontaire n'est ajoute.
- Allowed differences:
  - nouveaux modules de modificateurs et profils;
  - contrat `AccidentalDignityModifier` si absent;
  - signature ou orchestration minimale necessaire pour transmettre les
    conditions avancees au scoring;
  - breakdowns enrichis et scores accidentels differents quand des conditions
    avancees sont presentes;
  - tests et evidence.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrats factuels des conditions avancees | `planetary_conditions/contracts.py` | contrats dupliques dans `dignities` |
| Calcul des conditions avancees | `planetary_conditions/*_calculator.py` et `advanced_planetary_conditions_runtime.py` | `advanced_condition_modifiers.py` |
| Conversion condition -> score accidentel | `dignities/advanced_condition_modifiers.py` | `planetary_conditions`, API, services, frontend |
| Profils de score des modificateurs | `dignities/advanced_condition_modifier_profiles.py` | constantes dispersees dans le calculateur |
| Agregation des scores de dignite | `dignities/planet_dignity_scoring_service.py` ou owner equivalent existant | `natal_calculation.py`, services chart, API |
| Projection publique JSON | out of scope | ne pas etendre volontairement dans CS-215 |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-215. | Politique permanente sans exception. |

Validation rule:

- Toute exception requise doit bloquer l'implementation et exiger une decision
  utilisateur; aucune exception wildcard, dossier entier, fallback silencieux ou
  compatibilite transitoire ne doit etre ajoutee.

## 4f. Contract Shape

- Contract type:
  - dataclass immutable de modificateur accidentel;
  - dataclass immutable de profil de modificateur;
  - fonction pure retournant un tuple de modificateurs.
- Fields:
  - `AccidentalDignityModifier.key`;
  - `AccidentalDignityModifier.category`;
  - `AccidentalDignityModifier.score_delta`;
  - `AccidentalDignityModifier.reason`;
  - `AccidentalDignityModifier.source`;
  - `AdvancedConditionModifierProfile.condition_key`;
  - `AdvancedConditionModifierProfile.score_delta`;
  - `AdvancedConditionModifierProfile.category`.
- Required fields:
  - `bundle: PlanetaryConditionsBundle`;
  - `moon_phase: MoonPhaseCondition | None`;
  - retour: tuple immuable de `AccidentalDignityModifier`.
- Optional fields:
  - `PlanetaryConditionsBundle.solar_proximity`;
  - `PlanetaryConditionsBundle.motion`;
  - `PlanetaryConditionsBundle.visibility`;
  - `PlanetaryConditionsBundle.solar_phase_relation`;
  - `moon_phase`.
- Status codes:
  - aucun endpoint HTTP, methode ou status code n'est modifie.
- Serialization names:
  - aucun contrat JSON public dedie n'est ajoute volontairement.
- Frontend type impact:
  - aucun type frontend ne change.
- Generated contract impact:
  - aucun OpenAPI, client genere, schema genere ou contrat API public n'est
    volontairement modifie.
- Public function shape:

```python
calculate_advanced_condition_modifiers(
    *,
    bundle: PlanetaryConditionsBundle,
    moon_phase: MoonPhaseCondition | None,
) -> tuple
```

Le tuple retourne uniquement des instances immuables de
`AccidentalDignityModifier`.

- Required categories:
  - `solar_condition`;
  - `motion_condition`;
  - `visibility_condition`;
  - `solar_phase_condition`;
  - `lunar_condition`.
- Required modifier keys and default deltas:
  - `cazimi_bonus`: `+5`;
  - `combust_penalty`: `-5`;
  - `under_beams_penalty`: `-2`;
  - `retrograde_penalty`: `-3`;
  - `stationary_bonus`: `+2`;
  - `very_fast_bonus`: `+1`;
  - `very_slow_penalty`: `-1`;
  - `invisible_penalty`: `-4`;
  - `emerging_bonus`: `+2`;
  - `oriental_superior_bonus`: `+1`;
  - `occidental_superior_penalty`: `-1`;
  - `full_moon_bonus`: `+2`;
  - `new_moon_penalty`: `-2`.
- Solar proximity rule:
  - `solar_proximity=None`, `is_active=False` ou `condition_key=NONE` ne
    produit aucun modificateur;
  - `CAZIMI` produit seulement `cazimi_bonus`;
  - `COMBUST` produit `combust_penalty` sauf pour `bundle.planet_key == "sun"`;
  - `UNDER_BEAMS` produit `under_beams_penalty`.
- Visibility V1 rule:
  - `INVISIBLE` produit `invisible_penalty`;
  - `EMERGING` produit `emerging_bonus`;
  - `VISIBLE`, `UNKNOWN`, `UNDER_BEAMS`, `CONJUNCT_SOLAR`, `HELIACAL_RISING`
    et `HELIACAL_SETTING` ne produisent aucun modificateur de visibilite V1;
  - `UNDER_BEAMS` et `CONJUNCT_SOLAR` restent couverts par la proximite solaire
    afin d'eviter un double comptage.
- Simplified V1 solar phase rule:
  - planetes superieures V1: `mars`, `jupiter`, `saturn`;
  - planete superieure: oriental produit `oriental_superior_bonus`,
    occidental produit `occidental_superior_penalty`;
  - planetes inferieures V1: `mercury`, `venus`;
  - planete inferieure, Soleil, Lune, relation `UNKNOWN` ou
    `CONJUNCT_SOLAR`: aucun effet V1;
  - cette heuristique doit etre documentee comme simplification traditionnelle,
    sans texte interpretatif.
- Stationary V1 note:
  - `stationary_bonus` vaut `+2` dans CS-215;
  - ce delta est une convention de scoring configurable V1, pas une verite
    astrologique absolue;
  - les nuances interpretatives de stationnarite restent reservees a une story
    ulterieure.
- Lunar rule:
  - phase lunaire appliquee uniquement quand `bundle.planet_key == "moon"`;
  - `FULL_MOON` produit `full_moon_bonus`;
  - `NEW_MOON` produit `new_moon_penalty`.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-215 ne migre aucun consommateur par lots et ne remplace aucune
  surface publique.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans, lint, `RG-135` a `RG-142` et absence d'interpretation/API/DB/frontend/LLM. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher que l'integration des conditions avancees dans les dignites
    accidentelles devienne une couche d'interpretation, un nouveau calculateur
    de conditions, une projection publique, une API, une DB ou une duplication
    des contrats `planetary_conditions`.
- Forbidden examples in new `dignities` modules:
  - `interpretation`
  - `meaning`
  - `description`
  - `narrative`
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

- Evidence 1: `_condamad/stories/story-status.md` - `CS-215` est enregistree
  comme `ready-to-dev`, apres `CS-214` enregistree comme `done`.
- Evidence 2: `_condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/00-story.md`
  - la section follow-up annonce explicitement `CS-215 - Integrate Advanced
  Planetary Conditions Into Accidental Dignities`.
- Evidence 3: `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `PlanetaryConditionsBundle`, `MoonPhaseCondition`, les enums de
  proximite, mouvement, visibilite, relation solaire et phase lunaire existent.
- Evidence 4: `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
  - `calculate_advanced_planetary_conditions` produit les bundles par planete
  et la phase lunaire globale.
- Evidence 5: `backend/app/domain/astrology/dignities/contracts.py` -
  `AccidentalDignityMatch`, `PlanetDignityInput` et `PlanetDignityResult`
  existent, mais aucun `AccidentalDignityModifier` n'existe encore.
- Evidence 6: `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`
  - le calculateur detecte deja maisons, mouvement, distance solaire et
  relation heliacale depuis les regles runtime, mais ne consomme pas
  `PlanetaryConditionsBundle`.
- Evidence 7: `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
  - l'agregation additionne `essential`, `accidental`, `essential_score`,
  `accidental_score` et `total_score` sans modificateurs avances.
- Evidence 8: `backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py`
  - les tests actuels couvrent les dignites accidentelles structurelles et les
  sources historiques, pas le bloc CS-214.
- Evidence 9: `backend/pyproject.toml` - pytest collecte `tests/unit`, donc les
  tests peuvent rester sous `backend/tests/unit/domain/astrology` ou utiliser
  un sous-dossier `dignities` si cree par la story.
- Evidence 10: `_condamad/stories/regression-guardrails.md` - invariants
  `RG-135` a `RG-141` consultes avant cadrage; `RG-142` est ajoute par cette
  story pour proteger l'integration accidentelle.

## 6. Target State

After implementation:

- `calculate_advanced_condition_modifiers` convertit un bundle de conditions
  avancees et la phase lunaire globale en modificateurs accidentels explicites.
- Les deltas par defaut sont concentres dans un profil configurable, pas
  disperses dans le calculateur.
- Les modificateurs sont additionnes au score accidentel et visibles dans le
  breakdown du resultat.
- Les "signaux de dignite" du brief sont representes par ces modificateurs
  accidentels factuels et explicables, sans ajouter de couche narrative.
- Cazimi prime sur combust, le Soleil ne recoit pas de penalite de combustion,
  stationnaire et retrograde peuvent coexister, et les conditions partielles ne
  cassent pas le calcul.
- Aucune interpretation, API, DB, migration, frontend, LLM ou projection
  publique volontaire n'est ajoutee.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-135` - les contrats `planetary_conditions` doivent rester factuels et
    sans scoring.
  - `RG-136` - le calcul de proximite solaire ne doit pas etre duplique dans
    les dignites.
  - `RG-137` - le calcul de mouvement ne doit pas etre duplique dans les
    dignites.
  - `RG-138` - le calcul oriental/occidental ne doit pas etre duplique dans
    les dignites.
  - `RG-139` - le calcul de phase lunaire ne doit pas etre duplique dans les
    dignites.
  - `RG-140` - le calcul de visibilite ne doit pas etre duplique dans les
    dignites.
  - `RG-141` - l'orchestration CS-214 reste la source runtime des conditions
    avancees.
  - `RG-142` - les modificateurs accidentels avances restent purs,
    configurables et non narratifs.
- Non-applicable invariants:
  - `RG-129` - la story ne modifie pas le frontend expert panel.
  - `RG-130` - la story ne modifie pas volontairement la persistance d'audit.
  - `RG-134` - la story ne remplace pas la validation transverse CS-207.
- Required regression evidence:
  - tests unitaires et integration dignity;
  - scans anti-duplication des calculateurs de conditions;
  - scans anti-interpretation, anti-LLM, anti-API, anti-DB et anti-frontend;
  - diff adjacent sur `planetary_conditions`, services chart, API, infra,
    migrations et frontend.
- Allowed differences:
  - nouveaux modificateurs et scores accidentels modifies seulement quand le
    runtime fournit des conditions avancees.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le module expose la fonction publique attendue. | Evidence profile: `runtime source of truth`; `pytest -q $modifiers_tests`. |
| AC2 | `AccidentalDignityModifier` est immutable avec les cinq champs requis. | Evidence profile: `contract shape`; `pytest -q $contracts_tests`; `pytest -q $modifiers_tests`. |
| AC3 | Les profils de deltas sont centralises avec les categories attendues. | Evidence profile: `contract shape`; `Test-Path $profiles`; `pytest -q $modifiers_tests`. |
| AC4 | Cazimi prioritaire exclut `combust_penalty`. | Evidence profile: `deterministic test`; `pytest -q $modifiers_tests`. |
| AC5 | Combust produit `combust_penalty` `-5` pour une planete non solaire. | Evidence profile: `deterministic test`; `pytest -q $modifiers_tests`. |
| AC6 | Under beams produit `under_beams_penalty` `-2`. | Evidence profile: `deterministic test`; `pytest -q $modifiers_tests`. |
| AC7 | Stationary+retrograde cohabitent dans les modificateurs. | Evidence profile: `deterministic test`; `pytest -q $modifiers_tests`. |
| AC8 | Les vitesses extremes generent leurs deltas. | Evidence profile: `deterministic test`; `pytest -q $modifiers_tests`. |
| AC9 | Visibilite V1 couvre `INVISIBLE`/`EMERGING` sans double compter `UNDER_BEAMS`. | Evidence profile: `deterministic test`; `pytest -q $modifiers_tests`. |
| AC10 | Oriental/occidental applique les deltas V1 seulement aux planetes superieures. | Evidence profile: `deterministic test`; `pytest -q $modifiers_tests`. |
| AC11 | La phase lunaire affecte uniquement `bundle.planet_key == "moon"`. | Evidence profile: `deterministic test`; `pytest -q $modifiers_tests`. |
| AC12 | Les conditions partielles `None` sont tolerees sans crash. | Evidence profile: `deterministic test`; `pytest -q $modifiers_tests`. |
| AC13 | Le score accidentel inclut les modificateurs. | Evidence profile: `runtime source of truth`; `pytest -q $integration_tests`. |
| AC14 | Les breakdowns exposent les modificateurs. | Evidence profile: `json_contract_shape`; `pytest -q $integration_tests`; `pytest -q $contracts_tests`. |
| AC15 | Le Soleil ne recoit aucune penalite de combustion. | Evidence profile: `deterministic test`; `pytest -q $modifiers_tests`; `pytest -q $integration_tests`. |
| AC16 | Les surfaces interdites restent absentes. | Evidence profile: `scan`; `rg -n $forbidden_surface_terms $new_modules`. |
| AC17 | Les surfaces adjacentes restent sans diff. | Evidence profile: `scan`; Manual check: `git diff -- $adjacent_diff_paths` expected empty diff. |
| AC18 | Les calculateurs CS-209 a CS-214 ne sont pas dupliques. | Evidence profile: `reintroduction_guard`; `rg -n $forbidden_duplication $new_modules`. |
| AC19 | La validation complete passe sous venv. | Evidence profile: `persistent evidence`; `ruff check .`; `pytest -q`; `evidence/validation.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline et confirmer les owners (AC: AC1, AC2, AC3, AC16, AC17, AC18)
  - [ ] Subtask 1.1 - Inspecter les fichiers listes en section 18.
  - [ ] Subtask 1.2 - Documenter le baseline dans `evidence/validation.md`.
  - [ ] Subtask 1.3 - Confirmer si les tests seront places dans le sous-dossier
    `backend/tests/unit/domain/astrology/dignities/` ou dans la racine
    existante `backend/tests/unit/domain/astrology/`.

- [ ] Task 2 - Creer les contrats et profils de modificateurs (AC: AC1, AC2, AC3)
  - [ ] Subtask 2.1 - Ajouter `AccidentalDignityModifier` dans `contracts.py` ou
    dans le nouveau module si cela evite un couplage inutile.
  - [ ] Subtask 2.2 - Ajouter `AdvancedConditionModifierProfile` et le profil V1.
  - [ ] Subtask 2.3 - Centraliser les deltas et categories attendus.

- [ ] Task 3 - Implementer le moteur pur de modificateurs (AC: AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC15)
  - [ ] Subtask 3.1 - Creer `advanced_condition_modifiers.py`.
  - [ ] Subtask 3.2 - Implementer `_build_solar_condition_modifiers`.
  - [ ] Subtask 3.3 - Implementer `_build_motion_modifiers`.
  - [ ] Subtask 3.4 - Implementer `_build_visibility_modifiers`.
  - [ ] Subtask 3.5 - Implementer `_build_solar_phase_modifiers`.
  - [ ] Subtask 3.6 - Implementer `_build_moon_phase_modifiers`.
  - [ ] Subtask 3.7 - Garantir cazimi prioritaire, Soleil sans penalite et
    tolerance aux `None`.
  - [ ] Subtask 3.8 - Garantir que `UNDER_BEAMS` et `CONJUNCT_SOLAR` de
    visibilite ne creent pas un second modificateur V1.

- [ ] Task 4 - Brancher les modificateurs au scoring accidentel (AC: AC13, AC14, AC15, AC18)
  - [ ] Subtask 4.1 - Etendre la signature de l'owner de scoring pour recevoir
    le resultat CS-214 ou les bundles par planete, sans importer API/DB/service.
  - [ ] Subtask 4.2 - Additionner les modificateurs aux scores accidentels
    apres les matches structurels existants.
  - [ ] Subtask 4.3 - Enrichir les breakdowns avec une forme explicite et
    stable.
  - [ ] Subtask 4.4 - Ne pas mettre de logique detaillee de conditions dans
    `natal_calculation.py` au-dela du passage du runtime deja calcule.

- [ ] Task 5 - Ajouter les tests (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15)
  - [ ] Subtask 5.1 - Creer
    `backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py`
    si le sous-dossier est retenu, sinon le fichier equivalent dans la racine
    pytest existante.
  - [ ] Subtask 5.2 - Couvrir combust, cazimi, under beams, retrograde,
    stationnaire, vitesse, visibilite invisible/emerging, absence de double
    comptage under beams, oriental/occidental, phase lunaire, Soleil et
    conditions partielles.
  - [ ] Subtask 5.3 - Creer
    `backend/tests/unit/domain/astrology/dignities/test_accidental_dignity_conditions_integration.py`
    ou le fichier equivalent adapte a la topologie existante.
  - [ ] Subtask 5.4 - Couvrir score final et breakdowns.

- [ ] Task 6 - Ajouter les guardrails anti-drift (AC: AC16, AC17, AC18)
  - [ ] Subtask 6.1 - Verifier `RG-142` dans
    `_condamad/stories/regression-guardrails.md`.
  - [ ] Subtask 6.2 - Executer les scans imports interdits, interpretation,
    LLM, API, DB, frontend et duplication.
  - [ ] Subtask 6.3 - Documenter les resultats dans l'evidence.

- [ ] Task 7 - Valider la story (AC: AC19)
  - [ ] Subtask 7.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 7.2 - Executer les tests cibles.
  - [ ] Subtask 7.3 - Executer `ruff format .`, `ruff check .` et `pytest -q`.
  - [ ] Subtask 7.4 - Documenter commandes, resultats et risques residuels dans
    `evidence/validation.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetaryConditionsBundle`, `MoonPhaseCondition` et les enums depuis
    `planetary_conditions/contracts.py`;
  - `AdvancedPlanetaryConditionsResult` produit par CS-214;
  - `PlanetDignityScoringService`, `AccidentalDignityCalculator`,
    `PlanetDignityResult` et `AccidentalDignityMatch` existants;
  - les tests existants de `planetary_conditions` pour prouver que les
    calculateurs amont restent stables.
- Do not recreate:
  - les contrats `planetary_conditions`;
  - les calculateurs de proximite solaire, mouvement, relation solaire,
    visibilite ou phase lunaire;
  - un second moteur de dignites accidentelles;
  - un moteur d'ephemerides;
  - une projection JSON publique des conditions avancees;
  - un moteur d'interpretation ou de narration.
- Shared abstraction allowed only if:
  - elle reste dans `dignities`;
  - elle supprime une duplication reelle entre modificateurs;
  - elle ne cree pas de registre concurrent aux profils V1.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export
- second scoring engine
- broad allowlist
- `PASS with limitation`

Specific forbidden symbols / paths:

- `interpretation`
- `meaning`
- `description`
- `narrative`
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
- `pydantic` dans les nouveaux modules `dignities`

Specific forbidden production modifications unless explicitly justified by the
scope:

- `backend/app/domain/astrology/planetary_conditions/**` - pas de scoring dans
  les calculateurs de conditions.
- `backend/app/domain/astrology/advanced_conditions/**` - pas d'interpretation
  ou reutilisation historique.
- `backend/app/domain/astrology/interpretation_adapters/**` - CS-216 portera
  les profils interpretatifs; CS-215 reste limite au scoring accidentel.
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
| Conditions avancees factuelles | `backend/app/domain/astrology/planetary_conditions` | `dignities` ne recalcule pas ces faits |
| Modificateurs accidentels issus des conditions | `backend/app/domain/astrology/dignities/advanced_condition_modifiers.py` | `planetary_conditions`, API, services, frontend |
| Profils de deltas | `backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py` | constantes dispersees dans scoring service |
| Agregation scores de dignite | `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` | `natal_calculation.py`, services chart |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Artifact Check

- Generated artifact check: not applicable
- Reason: no generated file, generated schema, generated client or generated
  documentation is intentionally affected by CS-215.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, frontend
  type or generated client is intentionally affected. If an existing OpenAPI or
  public JSON snapshot changes because the result contract is serialized
  elsewhere, the dev agent must stop and record the blocker rather than
  expanding CS-215.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/dignities/contracts.py`
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py`
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py`
- `backend/app/domain/astrology/dignities/__init__.py`
- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py`
- `backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py`
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py`
- `backend/tests/unit/domain/astrology/test_natal_result_conditions_integration.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py`
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md`
- `_condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md`
- `_condamad/stories/CS-212-moon-phase-calculator/00-story.md`
- `_condamad/stories/CS-213-planetary-visibility-conditions-calculator/00-story.md`
- `_condamad/stories/CS-214-integrate-advanced-planetary-conditions-natal-result/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/dignities/advanced_condition_modifiers.py` -
  nouveau moteur pur de modificateurs.
- `backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py`
  - profils V1 configurables des deltas.
- `backend/app/domain/astrology/dignities/contracts.py` - ajout eventuel de
  `AccidentalDignityModifier` ou champ de breakdown.
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` -
  integration minimale si l'owner de breakdown accidentel reste ce calculateur.
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` -
  ajout des modificateurs au score final.
- `backend/app/domain/astrology/dignities/__init__.py` - exports publics si
  necessaire.
- `_condamad/stories/CS-215-integrate-advanced-planetary-conditions-accidental-dignities/evidence/validation.md`
  - preuves de validation.

Likely tests:

- `backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py`
  - couverture du moteur de modificateurs si le sous-dossier est cree.
- `backend/tests/unit/domain/astrology/dignities/test_accidental_dignity_conditions_integration.py`
  - couverture integration score/breakdowns si le sous-dossier est cree.
- `backend/tests/unit/domain/astrology/test_dignity_contracts.py` - a etendre si
  le contrat `PlanetDignityResult` ou un nouveau contrat y est ajoute.
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` -
  a etendre si l'integration reste dans ce fichier existant.

Files not expected to change:

- `backend/app/domain/astrology/planetary_conditions/**` - conditions deja
  calculees par CS-209 a CS-214.
- `backend/app/domain/astrology/advanced_conditions/**` - interpretation et
  conditions traditionnelles hors scope.
- `backend/app/domain/astrology/interpretation_adapters/**` - profils
  interpretatifs hors scope.
- `backend/app/services/chart/json_builder.py` - projection publique hors scope
  sauf blocker de serialization interne.
- `backend/app/api/**` - aucune route/schema.
- `backend/app/infra/**` - aucune persistence.
- `backend/migrations/**` - aucune migration.
- `frontend/src/**` - aucun frontend.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- Justification: les dataclasses, contrats existants et pytest suffisent.

## 21. Validation Plan

All Python commands must be run after activating the venv from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

Targeted tests:

```powershell
$modifiers_tests = "backend/tests/unit/domain/astrology/dignities/test_advanced_condition_modifiers.py"
$integration_tests = "backend/tests/unit/domain/astrology/dignities/test_accidental_dignity_conditions_integration.py"
$contracts_tests = "backend/tests/unit/domain/astrology/test_dignity_contracts.py"
$scoring_tests = "backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py"
$runtime_tests = "backend/tests/unit/domain/astrology/planetary_conditions/test_advanced_planetary_conditions_runtime.py"
pytest -q $modifiers_tests
pytest -q $integration_tests
pytest -q $contracts_tests
pytest -q backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py
pytest -q $scoring_tests
pytest -q $runtime_tests
```

If the dev agent keeps the existing flat topology instead of creating
`backend/tests/unit/domain/astrology/dignities/`, replace `$modifiers_tests` and
`$integration_tests` with the exact created paths and document the reason in
`evidence/validation.md`.

Quality checks:

```powershell
ruff format backend
ruff check backend
pytest -q
```

Required scans from repository root:

```powershell
$modifier = "backend/app/domain/astrology/dignities/advanced_condition_modifiers.py"
$profiles = "backend/app/domain/astrology/dignities/advanced_condition_modifier_profiles.py"
$new_modules = @($modifier, $profiles) | Where-Object { Test-Path $_ }
$forbidden_deps = "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services|sqlalchemy|fastapi|pydantic|FastAPI|SQLAlchemy|Session|repository"
$forbidden_interpretation = "interpretation|meaning|description|narrative|prompt|LLM|OpenAI|AIEngineAdapter"
$forbidden_surface_terms = (
  $forbidden_deps + "|" + $forbidden_interpretation +
  "|json_builder|frontend|migrations|router"
)
$forbidden_duplication = (
  "calculate_solar_proximity|calculate_planetary_motion|calculate_solar_phase|" +
  "calculate_planet_visibility|calculate_moon_phase|sun_longitude|moon_longitude|" +
  "ephemeris|SwissEph|swe"
)
$adjacent_diff_paths = @(
  "backend/app/domain/astrology/planetary_conditions",
  "backend/app/domain/astrology/advanced_conditions",
  "backend/app/domain/astrology/interpretation_adapters",
  "backend/app/services/chart/json_builder.py",
  "backend/app/api",
  "backend/app/infra",
  "backend/migrations",
  "frontend/src"
)
rg -n $forbidden_deps $new_modules
rg -n $forbidden_interpretation $new_modules
rg -n $forbidden_surface_terms $new_modules
rg -n "json_builder|frontend|migrations|router|FastAPI" $new_modules
rg -n $forbidden_duplication $new_modules
rg -n "calculate_advanced_condition_modifiers|AccidentalDignityModifier|advanced_condition_modifier" backend/app/domain/astrology/dignities backend/tests -g "*.py"
Select-String "RG-142" _condamad/stories/regression-guardrails.md
git diff -- $adjacent_diff_paths
```

Expected scan result:

- imports interdits dans les nouveaux modules: zero hits;
- interpretation/narration/prompt/LLM: zero hits;
- API/DB/frontend/json builder dans les nouveaux modules: zero hits;
- duplication de calculateurs amont: zero hits;
- symbols publics: hits limites aux nouveaux modules, exports, scoring et
  tests;
- diff adjacent: vide sauf blocker documente.

Story validation commands:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-215-integrate-advanced-planetary-conditions-accidental-dignities/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Skipped-command rule:

- Any skipped command must be recorded in the final evidence with exact
  command, reason, risk and fallback evidence.

## 22. Regression Risks

- Risk: le domaine `planetary_conditions` commence a porter du scoring.
  - Guardrail: `RG-135` a `RG-141`, ownership routing et scans anti-scoring.
- Risk: les modificateurs dupliquent les calculateurs de conditions.
  - Guardrail: scans anti-duplication et tests CS-209 a CS-214.
- Risk: les breakdowns deviennent narratifs ou interpretatifs.
  - Guardrail: AC16, scans interdits et `RG-142`.
- Risk: l'integration modifie indirectement une projection publique, une DB ou
  une API.
  - Guardrail: generated contract blocker et diff adjacent obligatoire.
- Risk: cazimi et combust s'additionnent ou le Soleil recoit une penalite
  solaire.
  - Guardrail: AC4, AC15 et tests cibles.

## 23. Dev Agent Instructions

- Implement only CS-215.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass constraints through wrapper, alias, fallback, re-export,
  broad allowlist, unresolved marker or hidden residual work.
- Keep `advanced_condition_modifiers.py` pure and deterministic.
- Consume `PlanetaryConditionsBundle`; do not recalculate condition facts.
- Keep condition scoring in `dignities`, not in `planetary_conditions`.
- Keep interpretation, narration, prompts, LLM, API, DB, migrations and
  frontend out of scope.
- Use French top-of-file comments/docstrings for new applicative files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unresolved task markers or hidden residual in-domain work.

## 24a. Follow-up Story

- Next planned story: `CS-216 - Advanced Planetary Conditions Interpretation Profiles`.
- Boundary: CS-216 pourra introduire profils interpretatifs, vocabulaire
  astrologique, variations traditionnelles, nuances par planete et exploitation
  narrative future.
- CS-215 ne doit pas anticiper CS-216: les modificateurs restent du scoring
  accidentel factuel et non narratif.

## 24. References

- `backend/app/domain/astrology/dignities/contracts.py` - contrats de resultat
  et breakdowns de dignite.
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` -
  calcul actuel des dignites accidentelles.
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` -
  owner actuel de l'agregation des scores.
- `backend/app/domain/astrology/planetary_conditions/contracts.py` - contrats
  CS-208 a consommer sans duplication.
- `backend/app/domain/astrology/planetary_conditions/advanced_planetary_conditions_runtime.py`
  - runtime CS-214 qui assemble les bundles et la phase lunaire.
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
- `_condamad/stories/regression-guardrails.md` - invariants applicables
  `RG-135` a `RG-142`.
