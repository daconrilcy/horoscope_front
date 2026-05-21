# Story CS-212 moon-phase-calculator: Calculer la phase lunaire natale

Status: done

## 1. Objective

Creer un calculateur domaine pur qui determine la phase lunaire natale depuis
la longitude du Soleil et la longitude de la Lune. Le calculateur doit retourner
`MoonPhaseCondition`, normaliser les longitudes, calculer l'angle Soleil-Lune,
classifier waxing/waning/exact, estimer le ratio d'illumination, produire un
`phase_index` stable et rester deterministe, sans IO, sans DB, sans API, sans
scoring, sans interpretation et sans integration `NatalResult`.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-21 pour `CS-212 - Moon Phase
  Calculator`.
- Reason for change: CS-208 expose `MoonPhaseCondition`, `MoonPhaseKey` et
  `WaxingWaningState`, mais aucun calculateur pur ne produit encore la phase
  lunaire globale du theme natal.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story reprend le brief comme un calculateur
  mono-domaine. Les AC couvrent fonction publique, contrat de retour, angle
  `(moon - sun) % 360`, normalisation, waxing/waning/exact, segmentation,
  priorite `NEW_MOON`/`FULL_MOON`/`BALSAMIC`, illumination, index stable,
  bornes, interdits de scoring/interpretation et validations. Les exclusions du
  brief restent hors scope.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/planetary_conditions`
- In scope:
  - creer `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`;
  - reutiliser `MoonPhaseCondition`, `MoonPhaseKey` et `WaxingWaningState`
    depuis `contracts.py`;
  - exporter la fonction publique depuis
    `backend/app/domain/astrology/planetary_conditions/__init__.py`;
  - calculer `sun_moon_angle_deg = (moon_longitude_deg - sun_longitude_deg) %
    360.0`;
  - normaliser les longitudes dans `[0, 360)`;
  - calculer l'illumination approximative avec `(1 - cos(angle_rad)) / 2`;
  - classifier les phases `NEW_MOON`, `WAXING_CRESCENT`, `FIRST_QUARTER`,
    `WAXING_GIBBOUS`, `FULL_MOON`, `WANING_GIBBOUS`, `LAST_QUARTER`,
    `WANING_CRESCENT` et `BALSAMIC`;
  - appliquer la priorite explicite `NEW_MOON`, `FULL_MOON`, `BALSAMIC`, puis
    autres phases;
  - produire un `phase_index` stable de `0` a `8`;
  - ajouter les tests unitaires cibles du calculateur;
  - ajouter un commentaire global en francais et des docstrings francaises dans
    les fichiers applicatifs nouveaux ou significativement modifies.
- Out of scope:
  - interpretation des phases;
  - scoring, dignites, dominance, profils ou signaux interpretatifs;
  - lunaisons collectives;
  - ephemerides avancees;
  - eclipses;
  - visibilite lunaire reelle;
  - calcul astronomique exact d'illumination;
  - progression secondaire;
  - transits lunaires;
  - integration dans `NatalResult`, JSON public, frontend ou services chart;
  - DB, migrations, seeders, SQLAlchemy, API, FastAPI, Pydantic.
- Explicit non-goals:
  - ne pas modifier `backend/app/domain/astrology/advanced_conditions/**`;
  - ne pas modifier `backend/app/domain/astrology/dignities/**`;
  - ne pas modifier `backend/app/domain/astrology/condition/**`;
  - ne pas modifier `backend/app/domain/astrology/dominance/**`;
  - ne pas modifier `backend/app/domain/astrology/interpretation_adapters/**`;
  - ne pas modifier `backend/app/domain/astrology/natal_calculation.py`;
  - ne pas modifier `backend/app/services/chart/json_builder.py`;
  - ne pas modifier `backend/app/api/**`, `backend/app/infra/**`,
    `backend/migrations/**` ou `frontend/src/**`;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas ajouter de shim, alias, fallback, compatibilite ou second owner.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story cree un calculateur domaine pur dans un package
  deja contractuel; elle ne correspond pas aux archetypes API, suppression,
  migration, route, namespace ou service boundary.
- Additional validation rules:
  - `moon_phase_calculator.py` doit importer uniquement la bibliotheque
    standard et les contrats du meme package;
  - l'angle Soleil-Lune doit etre exactement equivalent a `(moon - sun) %
    360.0` apres normalisation;
  - les longitudes non finies doivent lever `ValueError` au lieu de produire un
    etat `UNKNOWN`;
  - `UNKNOWN` reste reserve au contrat CS-208 et ne doit pas etre produit par ce
    calculateur quand des longitudes numeriques valides sont fournies;
  - la nouvelle lune exacte `0.0` et la pleine lune exacte `180.0` doivent
    retourner `WaxingWaningState.EXACT`;
  - le balsamique de `315.0` inclus a `337.5` exclu doit etre prioritaire sur
    `WANING_CRESCENT`, mais pas sur `NEW_MOON` pour `angle >= 337.5`;
  - `score`, `score_delta`, `strength_modifier`, `interpretation`, `meaning`,
    `description`, `narrative`, `prompt`, `OpenAI`, `AIEngineAdapter`,
    `NatalResult`, `sqlalchemy`, `fastapi` et `pydantic` sont interdits dans le
    calculateur.
- Behavior change allowed: constrained
- Behavior change constraints:
  - nouveau comportement autorise uniquement via la nouvelle fonction domaine de
    phase lunaire;
  - aucun comportement existant, endpoint, schema public, payload JSON, seed,
    migration, score ou frontend ne change.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: les contrats CS-208 existants ne correspondent plus
  a `MoonPhaseCondition`, `MoonPhaseKey` ou `WaxingWaningState`; le dev agent
  doit bloquer au lieu de creer un second contrat concurrent.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les fonctions publiques importables et leurs tests comportementaux prouvent la verite runtime du calcul. |
| Baseline Snapshot | yes | Il faut capturer l'etat CS-208/CS-209/CS-210/CS-211 et l'etat explicite des guardrails `RG-135` a `RG-139`. |
| Ownership Routing | yes | Le calcul pur doit rester dans `planetary_conditions` et ne pas migrer vers API, services, infra ou projections. |
| Allowlist Exception | yes | Les exceptions autorisees doivent rester un registre vide et testable: aucun fallback, alias, shim ou compatibilite n'est autorise. |
| Contract Shape | yes | La forme de `MoonPhaseCondition` et de la fonction publique est le coeur de la story. |
| Batch Migration | no | Aucun consommateur existant n'est migre. |
| Reintroduction Guard | yes | Les scans doivent bloquer scoring, interpretation, dependances interdites et integration adjacente. |
| Persistent Evidence | yes | La validation et les scans doivent etre conserves dans l'artefact de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `calculate_moon_phase_condition`;
  - les objets `MoonPhaseCondition` retournes par les tests unitaires.
- Runtime artifacts:
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py`;
  - tests d'import depuis `app.domain.astrology.planetary_conditions`.
  - AST guard / importability guard:
    `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py`.
- Secondary evidence:
  - tests de contrats CS-208 maintenus;
  - scans des imports interdits, scoring, interpretation et integrations
    adjacentes;
  - `ruff check .`;
  - `pytest -q`.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas l'angle Soleil-Lune, les bornes de segmentation,
    l'illumination, le passage `359/0`, la priorite balsamique ou les cas
    exacts `0/180`.
- Forbidden sources:
  - API, services, infra, DB, frontend, JSON builder, scoring, interpretation,
    ephemerides avancees, transits, progressions et integration `NatalResult`.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/planetary_conditions/contracts.py`;
  - `Get-Content backend/app/domain/astrology/planetary_conditions/__init__.py`;
  - `Test-Path backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`;
  - `Test-Path backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137|RG-138|RG-139"`.
- Comparison after implementation:
  - `Test-Path backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`;
  - `Test-Path backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py`;
  - `rg -n $public_symbols $planetary_condition_paths`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137|RG-138|RG-139"`.
- Expected invariant:
  - seuls `planetary_conditions`, ses tests, ses exports et les artefacts de
    story changent;
  - `RG-135` reste borne aux contrats, `RG-136` protege la proximite solaire,
    `RG-137` protege le mouvement, `RG-138` protege la relation solaire et
    `RG-139` protege la phase lunaire;
  - aucune integration adjacente n'est introduite.
- Allowed differences:
  - nouveau calculateur de phase lunaire;
  - export public explicite;
  - nouveau test unitaire;
  - evidence de validation et ajout ou verification du garde-fou `RG-139`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrat de phase lunaire | `planetary_conditions/contracts.py` | calculateur local duplique, settings, DB, API schema |
| Calcul pur de phase lunaire | `planetary_conditions/moon_phase_calculator.py` | `advanced_conditions`, `dignities`, `services/chart`, frontend |
| Exports publics du package | `planetary_conditions/__init__.py` | re-export legacy ou alias de compatibilite |
| Tests du calculateur | `backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py` | tests API, DB, frontend ou integration chart |
| Integration `NatalResult` | out of scope for CS-212 | `natal_calculation.py`, `json_builder.py` |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-212. | Politique permanente sans exception. |

Validation rule:

- Any required exception must block implementation and require a user decision;
  no wildcard or folder-wide exception may be added.

## 4f. Contract Shape

- Contract type:
  - fonction pure importable qui retourne une dataclass domaine immuable
    `MoonPhaseCondition`.
- Fields:
  - `MoonPhaseCondition.phase_key`;
  - `MoonPhaseCondition.sun_moon_angle_deg`;
  - `MoonPhaseCondition.illumination_ratio`;
  - `MoonPhaseCondition.waxing_or_waning`;
  - `MoonPhaseCondition.phase_index`.
- Required fields:
  - `phase_key: MoonPhaseKey`;
  - `sun_moon_angle_deg: float`;
  - `illumination_ratio: float | None`;
  - `waxing_or_waning: WaxingWaningState`;
  - `phase_index: int | None`.
- Optional fields:
  - none for valid inputs; `illumination_ratio` and `phase_index` are nullable
    only because the CS-208 contract allows unknown states, not because this
    calculateur may emit null for valid longitudes.
- Status codes:
  - no HTTP endpoint, method or status code is modified.
- Serialization names:
  - no public JSON serialization is added in CS-212.
- Frontend type impact:
  - no frontend type change.
- Generated contract impact:
  - no OpenAPI, generated client, generated schema or public API contract
    change.
- Public function shape:

```python
calculate_moon_phase_condition(
    *,
    moon_longitude_deg: float,
    sun_longitude_deg: float,
) -> MoonPhaseCondition
```

- Phase index shape:
  - `0`: `NEW_MOON`;
  - `1`: `WAXING_CRESCENT`;
  - `2`: `FIRST_QUARTER`;
  - `3`: `WAXING_GIBBOUS`;
  - `4`: `FULL_MOON`;
  - `5`: `WANING_GIBBOUS`;
  - `6`: `LAST_QUARTER`;
  - `7`: `WANING_CRESCENT`;
  - `8`: `BALSAMIC`.
- Base phase segmentation:
  - `NEW_MOON`: `337.5 <= angle < 360.0` ou `0.0 <= angle < 22.5`;
  - `WAXING_CRESCENT`: `22.5 <= angle < 67.5`;
  - `FIRST_QUARTER`: `67.5 <= angle < 112.5`;
  - `WAXING_GIBBOUS`: `112.5 <= angle < 157.5`;
  - `FULL_MOON`: `157.5 <= angle < 202.5`;
  - `WANING_GIBBOUS`: `202.5 <= angle < 247.5`;
  - `LAST_QUARTER`: `247.5 <= angle < 292.5`;
  - `WANING_CRESCENT`: `292.5 <= angle < 337.5`.
- Phase priority rule:
  - appliquer les bornes explicites dans cet ordre: `NEW_MOON`, `FULL_MOON`,
    `BALSAMIC`, puis les autres intervalles non chevauchants.
- Effective balsamic override:
  - `BALSAMIC`: `315.0 <= angle < 337.5`;
  - dans cette plage, retourner `BALSAMIC` et non `WANING_CRESCENT`;
  - pour `angle >= 337.5`, retourner `NEW_MOON` et non `BALSAMIC`.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-212 ne migre aucun consommateur et ne remplace aucun module
  existant.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans et statut `RG-135`/`RG-136`/`RG-137`/`RG-138`/`RG-139`. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher que le calculateur de phase lunaire pur devienne une couche de
    scoring, interpretation, API, persistence, projection, ephemerides avancees
    ou second moteur astrologique adjacent.
- Forbidden examples in `moon_phase_calculator.py`:
  - `score`
  - `score_delta`
  - `accidental_score_delta`
  - `essential_score_delta`
  - `strength_modifier`
  - `interpretation`
  - `meaning`
  - `description`
  - `narrative`
  - `prompt`
  - `NatalResult`
  - `transit`
  - `progression`
  - `eclipse`
  - `ephemeris`
  - `from app.api`
  - `from app.infra`
  - `from app.infrastructure`
  - `from app.services`
  - `sqlalchemy`
  - `fastapi`
  - `pydantic`
  - `OpenAI`
  - `AIEngineAdapter`
- Required guard evidence:
  - tests unitaires comportementaux;
  - scans cibles du Validation Plan;
  - diff des surfaces adjacentes obligatoire.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/stories/story-status.md` - `CS-211` est la derniere
  story numerotee avant cette creation et elle est enregistree comme `done`.
- Evidence 2: `_condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md`
  - la section `Follow-up Story` annonce `CS-212 - Moon Phase Calculator`.
- Evidence 3: `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `MoonPhaseCondition`, `MoonPhaseKey` et `WaxingWaningState` existent deja.
- Evidence 4: `backend/app/domain/astrology/planetary_conditions/__init__.py`
  - les contrats lunaires sont exportes, mais aucun export de
    `calculate_moon_phase_condition` n'existe encore.
- Evidence 5: `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`,
  `planetary_motion_calculator.py` et `solar_phase_relation_calculator.py` -
  precedents locaux de calculateurs purs a reutiliser comme style.
- Evidence 6: `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - les tests de contrats prouvent deja l'importabilite et l'immutabilite de
    `MoonPhaseCondition`.
- Evidence 7: `Test-Path` local - `moon_phase_calculator.py` et
  `test_moon_phase_calculator.py` n'existent pas avant cette story.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - `RG-135` protege
  `contracts.py`, `RG-136` protege la proximite solaire, `RG-137` protege le
  mouvement planetaire, `RG-138` protege la relation solaire et cette story
  ajoute `RG-139` pour la phase lunaire.

Assumptions to verify during implementation:

- aucun calculateur canonique de phase lunaire n'existe deja dans
  `planetary_conditions`;
- les longitudes fournies sont des nombres finis; si le code existant a une
  politique standard pour les flottants non finis, la story doit la suivre sans
  ajouter de fallback silencieux.

## 6. Target State

After implementation:

- `moon_phase_calculator.py` existe et reste pur;
- `calculate_moon_phase_condition` retourne toujours un `MoonPhaseCondition`
  pour des longitudes numeriques valides;
- `_normalize_longitude_deg(value)` normalise les longitudes dans `[0, 360)`;
- `sun_moon_angle_deg` est calcule par `(moon - sun) % 360.0`;
- `WaxingWaningState.EXACT` est retourne pour `0.0` et `180.0`;
- un angle brut equivalent a `360.0` est normalise a `0.0` et retourne
  `WaxingWaningState.EXACT`;
- `WaxingWaningState.WAXING` est retourne pour les angles strictement entre
  `0.0` et `180.0`;
- `WaxingWaningState.WANING` est retourne pour les angles strictement entre
  `180.0` et `360.0`;
- les phases et `phase_index` suivent la segmentation et l'index de la section
  4f;
- `BALSAMIC` couvre `315.0` inclus a `337.5` exclu et ne remplace jamais
  `NEW_MOON` pour `angle >= 337.5`;
- le ratio d'illumination reste compris dans `[0.0, 1.0]`;
- aucune integration, scoring, interpretation, DB, API ou frontend n'est ajoute;
- les tests unitaires et scans anti-drift passent dans le venv.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-107` - les faits astrologiques doivent traverser les frontieres sous
    contrats types, pas en dictionnaires libres.
  - `RG-119` - les profils conditionnels ne doivent pas devenir un second
    moteur astrologique ou une source de scoring local.
  - `RG-122` - le moteur avance existant ne doit pas etre modifie par ce
    calculateur pur.
  - `RG-128` - `json_builder.py` reste une projection stricte et ne doit pas
    calculer la phase lunaire.
  - `RG-129` - le frontend reste display-only et hors scope.
  - `RG-135` - les contrats `contracts.py` restent immutables, sans scoring,
    interpretation ni dependance interdite.
  - `RG-136` - le calculateur de proximite solaire reste borne a cazimi,
    combustion, under beams ou none.
  - `RG-137` - le calculateur de mouvement planetaire reste borne au mouvement
    apparent.
  - `RG-138` - le calculateur de relation solaire reste borne a
    oriental/occidental/conjoint solaire.
- New durable invariant:
  - verifier la presence de `RG-139` pour proteger
    `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
    comme surface pure, sans scoring, interpretation, API, DB, services,
    frontend, ephemerides avancees ou integration `NatalResult`.
- Non-applicable invariants:
  - guardrails de routes API, migrations DB, prompts LLM et CSS frontend; la
    story ne touche pas ces surfaces.
- Required regression evidence:
  - tests unitaires du calculateur;
  - tests de contrats CS-208 maintenus;
  - scans imports interdits, scoring, interpretation, ephemerides avancees et
    integration adjacente;
  - diff des surfaces adjacentes obligatoire;
  - `ruff format .`, `ruff check .`, `pytest -q`.
- Allowed differences:
  - nouveau calculateur;
  - export public;
  - nouveau test unitaire;
  - verification ou mise a jour de `RG-139`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le fichier `moon_phase_calculator.py` existe. | Evidence: `Test-Path $p`, `pytest -q $t`. |
| AC2 | `calculate_moon_phase_condition` est importable depuis le package public. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC3 | La fonction retourne toujours un `MoonPhaseCondition` pour des longitudes finies. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC4 | La normalisation retourne une longitude canonique. | Evidence profile: `deterministic_test`; cas `361`, `-1`, `720`; `pytest -q $t`. |
| AC5 | L'angle Soleil-Lune applique `(moon - sun) % 360.0`. | Evidence profile: `deterministic_test`; `pytest -q $t` avec tests `sun=350, moon=10` et `sun=358, moon=2`. |
| AC6 | Les angles exacts majeurs retournent `WaxingWaningState.EXACT`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC7 | L'hemicycle croissant retourne `WaxingWaningState.WAXING`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC8 | L'hemicycle decroissant retourne `WaxingWaningState.WANING`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC9 | `NEW_MOON` respecte les bornes de la section 4f. | Evidence profile: `deterministic_test`; tests de bornes; `pytest -q $t`. |
| AC10 | `FULL_MOON` respecte les bornes de la section 4f. | Evidence profile: `deterministic_test`; tests de bornes; `pytest -q $t`. |
| AC11 | Les phases intermediaires respectent la section 4f. | Evidence profile: `deterministic_test`; parametrisation des bornes; `pytest -q $t`. |
| AC12 | `BALSAMIC` respecte la plage prioritaire de la section 4f. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC13 | L'ordre de priorite des phases est applique. | Evidence profile: `deterministic_test`; tests `angle=350`, `180`, `330`; `pytest -q $t`. |
| AC14 | `illumination_ratio` applique la formule de la section 3. | Evidence profile: `deterministic_test`; `pytest.approx`; `pytest -q $t`. |
| AC15 | `phase_index` suit le mapping stable `0..8`. | Evidence profile: `deterministic_test`; test parametrise; `pytest -q $t`. |
| AC16 | Les longitudes non finies levent `ValueError`. | Evidence profile: `deterministic_test`; tests `nan` et `inf`; `pytest -q $t`. |
| AC17 | Le calculateur exclut les dependances interdites. | Evidence: `rg -n "from app\\.api|from app\\.infra|sqlalchemy|fastapi|pydantic" $p` expected zero hits. |
| AC18 | Le calculateur exclut le scoring. | Evidence: `rg -n "\\bscore\\b|score_delta|accidental_score_delta|essential_score_delta|strength_modifier" $p` expected zero hits. |
| AC19 | Le calculateur exclut l'interpretation. | Evidence: `rg -n "interpretation|meaning|description|narrative|prompt" $p` expected zero hits. |
| AC20 | Le calculateur exclut les domaines hors scope. | Evidence: `rg -n "NatalResult|transit|progression|eclipse|ephemeris|FastAPI|SQLAlchemy" $p` expected zero hits. |
| AC21 | Aucune integration adjacente n'est ajoutee hors package. | Evidence: `rg -n $public_symbols $adjacent_roots` expected zero hits. |
| AC22 | La qualite backend passe dans le venv. | Evidence profile: `deterministic_test`; `ruff format .`, `ruff check .`, `pytest -q`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer la baseline et confirmer l'ownership (AC: AC1, AC2, AC17, AC18, AC19, AC20, AC21)
  - [ ] Subtask 1.1 - Inspecter `contracts.py`, `__init__.py`,
    `solar_proximity_calculator.py`, `planetary_motion_calculator.py`,
    `solar_phase_relation_calculator.py`, `test_contracts.py`, CS-208 a
    CS-211 et `regression-guardrails.md`.
  - [ ] Subtask 1.2 - Verifier l'absence preexistante de
    `moon_phase_calculator.py` et `test_moon_phase_calculator.py`.
  - [ ] Subtask 1.3 - Documenter dans l'evidence l'etat attendu de `RG-135`,
    `RG-136`, `RG-137`, `RG-138` et `RG-139`.

- [ ] Task 2 - Creer le calculateur de phase lunaire pur (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18, AC19, AC20)
  - [ ] Subtask 2.1 - Creer `moon_phase_calculator.py`.
  - [ ] Subtask 2.2 - Importer uniquement `math` et les contrats
    `MoonPhaseCondition`, `MoonPhaseKey`, `WaxingWaningState`.
  - [ ] Subtask 2.3 - Implementer `_normalize_longitude_deg(value: float)`.
  - [ ] Subtask 2.4 - Implementer `_compute_sun_moon_angle_deg`.
  - [ ] Subtask 2.5 - Implementer `_compute_illumination_ratio`.
  - [ ] Subtask 2.6 - Implementer `_resolve_waxing_waning`.
  - [ ] Subtask 2.7 - Implementer `_resolve_phase_key` avec priorites
    explicites.
  - [ ] Subtask 2.8 - Implementer `_resolve_phase_index`.
  - [ ] Subtask 2.9 - Exporter `calculate_moon_phase_condition` depuis
    `__init__.py`.

- [ ] Task 3 - Ajouter les tests unitaires (AC: AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16)
  - [ ] Subtask 3.1 - Creer
    `backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py`.
  - [ ] Subtask 3.2 - Tester nouvelle lune, pleine lune, premier quartier,
    dernier quartier et balsamique.
  - [ ] Subtask 3.3 - Tester waxing, waning, exact et l'equivalence
    `360.0 -> 0.0`.
  - [ ] Subtask 3.4 - Tester illumination `0.0`, `1.0` et une valeur
    intermediaire avec `pytest.approx`.
  - [ ] Subtask 3.5 - Tester passage `359/0` et normalisation `361`, `-1`,
    `720`.
  - [ ] Subtask 3.6 - Tester les bornes `22.5`, `67.5`, `112.5`, `157.5`,
    `202.5`, `247.5`, `292.5`, `315.0`, `337.5`.
  - [ ] Subtask 3.7 - Tester le mapping `phase_index`.
  - [ ] Subtask 3.8 - Tester le rejet des longitudes non finies.

- [ ] Task 4 - Ajouter et prouver les gardes anti-drift (AC: AC17, AC18, AC19, AC20, AC21)
  - [ ] Subtask 4.1 - Verifier que `RG-135` protege toujours les contrats purs.
  - [ ] Subtask 4.2 - Verifier que `RG-136`, `RG-137` et `RG-138` restent
    bornes a leurs calculateurs.
  - [ ] Subtask 4.3 - Verifier ou mettre a jour `RG-139` pour le calculateur de
    phase lunaire pur.
  - [ ] Subtask 4.4 - Executer les scans imports interdits, scoring,
    interpretation, domaines hors scope et surfaces adjacentes.

- [ ] Task 5 - Valider la story (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18, AC19, AC20, AC21, AC22)
  - [ ] Subtask 5.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 5.2 - Executer le test cible.
  - [ ] Subtask 5.3 - Executer `ruff format .`, `ruff check .` et `pytest -q`.
  - [ ] Subtask 5.4 - Documenter les resultats dans `evidence/validation.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `MoonPhaseCondition`, `MoonPhaseKey` et `WaxingWaningState` depuis
    `contracts.py`;
  - conventions des calculateurs purs `solar_proximity_calculator.py`,
    `planetary_motion_calculator.py` et `solar_phase_relation_calculator.py`;
  - tests pytest sous `backend/tests/unit/domain/astrology/planetary_conditions`.
- Do not recreate:
  - contrats CS-208 sous un autre nom ou dans un autre package;
  - calculateur de proximite solaire;
  - calculateur de mouvement planetaire;
  - calculateur de relation solaire oriental/occidental;
  - moteur d'ephemerides, visibilite, transit ou progression;
  - scoring de dignites, dominance, profils ou signaux;
  - schemas API/Pydantic pour les memes concepts.
- Shared abstraction allowed only if:
  - une fonction pure canonique existe deja dans le meme package et son import
    ne viole pas l'ownership.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export
- scoring
- interpretation textuelle
- narration
- prompts ou LLM
- API schemas
- migrations, seeders, repositories, DB models
- ephemerides avancees
- visibilite lunaire reelle
- eclipses
- transits
- progressions
- integration `NatalResult`

Specific forbidden symbols / paths:

- `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
  importing `app.api`
- `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
  importing `app.infra`
- `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
  importing `app.infrastructure`
- `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
  importing `app.services`
- `sqlalchemy`
- `fastapi`
- `pydantic`
- `score`
- `score_delta`
- `accidental_score_delta`
- `essential_score_delta`
- `strength_modifier`
- `interpretation`
- `meaning`
- `description`
- `narrative`
- `prompt`
- `NatalResult`
- `transit`
- `progression`
- `eclipse`
- `ephemeris`
- `OpenAI`
- `AIEngineAdapter`

Specific forbidden production modifications unless explicitly justified by an
export convention:

- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/dignities/**`
- `backend/app/domain/astrology/condition/**`
- `backend/app/domain/astrology/dominance/**`
- `backend/app/domain/astrology/interpretation_adapters/**`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
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
| Contrat de phase lunaire | `planetary_conditions/contracts.py` | API schema, frontend type, JSON builder |
| Calcul angle Soleil-Lune | `planetary_conditions/moon_phase_calculator.py` | `natal_calculation.py`, `json_builder.py`, frontend |
| Classification phase et waxing/waning | `planetary_conditions/moon_phase_calculator.py` | scoring, dominance, interpretation adapters |
| Exports publics | `planetary_conditions/__init__.py` | alias ou re-export legacy |
| Integration future | future story | CS-212 ne modifie pas `NatalResult` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Artifact Check

- Generated artifact check: not applicable
- Reason: no generated file, generated schema, generated client or generated
  documentation is affected by CS-212.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, frontend
  type or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py`
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md`
- `_condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/planetary_conditions/__init__.py` - exporter la
  fonction publique.
- `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
  - nouveau calculateur pur.
- `_condamad/stories/regression-guardrails.md` - verifier ou ajouter
  l'invariant `RG-139`.
- `_condamad/stories/CS-212-moon-phase-calculator/evidence/validation.md` -
  preuves de validation.

Likely tests:

- `backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py`
  - couverture comportementale du calculateur.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - a maintenir sans changement sauf convention d'export ou contrat decouvert
  pendant l'implementation.

Files not expected to change:

- `backend/app/domain/astrology/advanced_conditions/**` - aucun moteur avance
  existant ne change.
- `backend/app/domain/astrology/dignities/**` - aucune dignite ou scoring ne
  change.
- `backend/app/domain/astrology/condition/**` - aucun profil/signal existant ne
  change.
- `backend/app/domain/astrology/dominance/**` - aucune dominance ne change.
- `backend/app/domain/astrology/natal_calculation.py` - pas d'integration
  `NatalResult`.
- `backend/app/services/chart/json_builder.py` - pas de projection JSON.
- `backend/app/api/**` - aucune route/schema.
- `backend/app/infra/**` - aucune persistence.
- `backend/migrations/**` - aucune migration.
- `frontend/src/**` - aucun frontend.

## 19a. Follow-up Story

- Next planned story: `CS-213 - Planetary Visibility Conditions Calculator`
- Expected scope: calculer la visibilite planetaire, emergence, invisibilite et
  visibilite solaire relative depuis les contrats CS-208.
- Boundary: CS-212 ne cree aucun calculateur de visibilite planetaire et ne
  prepare pas d'integration opportuniste pour CS-213.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- Justification: la bibliotheque standard `math` et les contrats CS-208
  suffisent.

## 21. Validation Plan

All Python commands must be run after activating the venv from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

Targeted tests:

```powershell
$t = "backend/tests/unit/domain/astrology/planetary_conditions/test_moon_phase_calculator.py"
pytest -q $t
pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py
```

Quality checks:

```powershell
ruff format .
ruff check .
pytest -q
```

Required scans:

```powershell
$p = "backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py"
$planetary_condition_paths = "backend/app/domain/astrology/planetary_conditions", "backend/tests/unit/domain/astrology/planetary_conditions"
$adjacent_roots = @(
  "backend/app/domain/astrology/advanced_conditions",
  "backend/app/domain/astrology/dignities",
  "backend/app/domain/astrology/condition",
  "backend/app/domain/astrology/dominance",
  "backend/app/domain/astrology/interpretation_adapters",
  "backend/app/domain/astrology/natal_calculation.py",
  "backend/app/services/chart/json_builder.py",
  "backend/app/api",
  "backend/app/infra",
  "backend/migrations",
  "frontend/src"
)
$public_symbols = "calculate_moon_phase_condition|MoonPhaseCondition|MoonPhaseKey|WaxingWaningState"
rg -n "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services" $p
rg -n "sqlalchemy|fastapi|pydantic|OpenAI|AIEngineAdapter" $p
rg -n "\\bscore\\b|score_delta|accidental_score_delta|essential_score_delta|strength_modifier" $p
rg -n "interpretation|meaning|description|narrative|prompt" $p
rg -n "NatalResult|transit|progression|eclipse|ephemeris|FastAPI|SQLAlchemy" $p
rg -n $public_symbols $planetary_condition_paths
rg -n $public_symbols $adjacent_roots
git diff -- `
  backend/app/domain/astrology/advanced_conditions `
  backend/app/domain/astrology/dignities `
  backend/app/domain/astrology/condition `
  backend/app/domain/astrology/dominance `
  backend/app/domain/astrology/interpretation_adapters `
  backend/app/domain/astrology/natal_calculation.py `
  backend/app/services/chart/json_builder.py `
  backend/app/api backend/app/infra backend/migrations frontend/src
```

Expected scan result:

- imports interdits: zero hits;
- scoring: zero hits;
- interpretation/narration/prompt: zero hits;
- domaines hors scope dans le calculateur: zero hits;
- symbols publics: hits limites aux nouveaux modules, exports et tests;
- symbols publics dans les surfaces adjacentes: zero hits;
- diff des surfaces adjacentes: vide.

Story validation commands:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-212-moon-phase-calculator/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Skipped-command rule:

- Any skipped command must be recorded in the final evidence with exact
  command, reason, risk and fallback evidence.

## 22. Regression Risks

- Risk: le calculateur de phase lunaire devient une source de scoring ou
  d'interpretation avant une story dediee.
  - Guardrail: AC18, AC19, scans scoring/interpretation et `RG-139`.
- Risk: les bornes `315.0`/`337.5` classent mal le balsamique ou la nouvelle
  lune.
  - Guardrail: AC9, AC12, AC13 et tests de bornes.
- Risk: la normalisation autour de `359/0` produit un angle negatif ou une
  phase fausse.
  - Guardrail: AC4, AC5 et tests de passage zero.
- Risk: l'illumination est traitee comme astronomiquement exacte alors qu'elle
  est seulement approximative.
  - Guardrail: non-goals, AC14 et docstring francaise du calculateur.
- Risk: une integration opportuniste modifie le JSON public ou `NatalResult`.
  - Guardrail: AC20, AC21 et diff des surfaces adjacentes obligatoire.

## 23. Dev Agent Instructions

- Implement only CS-212.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass constraints through wrapper, alias, fallback, re-export,
  broad allowlist, unresolved marker or hidden residual work.
- Keep the calculator pure and deterministic.
- Do not integrate into `NatalResult`.
- Do not change JSON public output.
- Do not change frontend.
- Do not change DB, migrations or seeds.
- Do not add scoring, interpretation, prompts, LLM, API schemas, Pydantic
  models, ephemerides avancees, transits, progressions, eclipses or lunar
  visibility engine.
- Use French top-of-file comments/docstrings for new applicative files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unresolved task marker or hidden residual in-domain work.

## 24. References

- `backend/app/domain/astrology/planetary_conditions/contracts.py` - contrats
  CS-208 reutilises par le calculateur.
- `backend/app/domain/astrology/planetary_conditions/__init__.py` - exports
  publics du package.
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  - precedent local de calculateur pur.
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
  - precedent local de calculateur pur.
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
  - precedent local recent de calculateur pur avec normalisation.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - tests de contrats a maintenir.
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
  - source contractuelle.
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
  - precedent proximite solaire.
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md`
  - precedent mouvement planetaire.
- `_condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md`
  - precedent relation solaire et follow-up explicite CS-212.
- `_condamad/stories/regression-guardrails.md` - invariants applicables
  `RG-107`, `RG-119`, `RG-122`, `RG-128`, `RG-129`, `RG-135`, `RG-136`,
  `RG-137`, `RG-138` et nouvel invariant `RG-139`.
