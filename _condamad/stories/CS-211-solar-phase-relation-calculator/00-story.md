# Story CS-211 solar-phase-relation-calculator: Calculer la relation solaire oriental occidental

Status: ready-to-dev

## 1. Objective

Creer un calculateur domaine pur qui determine la relation solaire
oriental/occidental d'une planete depuis sa longitude zodiacale et celle du
Soleil. Le calculateur doit retourner le contrat CS-208
`PlanetarySolarPhaseRelation`, normaliser les longitudes, appliquer une
tolerance de conjonction configurable, traiter explicitement le Soleil et rester
deterministe, sans IO, sans scoring, sans interpretation, sans visibilite
avancee, sans API, sans DB, sans projection publique et sans integration
`NatalResult`.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-21 pour `CS-211 - Oriental /
  Occidental Solar Phase Relation Calculator`.
- Reason for change: CS-208 expose `PlanetarySolarPhaseRelation` et
  `SolarPhaseRelationKey`, mais aucun calculateur pur ne produit encore la
  relation geometrique du Soleil vers la planete.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story reprend le brief comme un calculateur
  mono-domaine. Les AC couvrent fonction principale, contrat de seuil,
  normalisation, angle relatif `(planet - sun) % 360`, tolerance de conjonction,
  opposition exacte conventionnellement occidentale, Soleil, fonction de lot,
  interdits de scoring/interpretation et validations. Les exclusions du brief
  restent hors scope.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/planetary_conditions`
- In scope:
  - creer `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`;
  - ajouter `SolarPhaseRelationThresholds` dans `contracts.py` si ce contrat
    n'existe pas encore;
  - exporter les seuils et fonctions publiques depuis
    `planetary_conditions/__init__.py`;
  - calculer `CONJUNCT_SOLAR`, `OCCIDENTAL` ou `ORIENTAL` depuis la distance
    zodiacale relative du Soleil vers la planete;
  - appliquer la convention angle strictement positif jusqu'a `180` inclus pour
    `OCCIDENTAL`;
  - appliquer la convention angle strictement superieur a `180` et inferieur a
    `360` pour `ORIENTAL`;
  - appliquer `CONJUNCT_SOLAR` si l'angle est inferieur ou egal a la tolerance
    ou si `360 - angle` est inferieur ou egal a la tolerance;
  - traiter `planet_key == "sun"` comme conjoint solaire avec distance `0.0`;
  - implementer la fonction batch optionnelle si elle reste dans le meme module
    pur;
  - ajouter les tests unitaires cibles du calculateur;
  - ajouter un commentaire global en francais et des docstrings francaises dans
    les fichiers applicatifs nouveaux ou modifies.
- Out of scope:
  - visibilite planetaire avancee;
  - heliacal rising ou heliacal setting;
  - combustion, cazimi, under beams ou proximite solaire;
  - scoring de dignite, dominance, force ou conditions accidentelles;
  - interpretation, narration, signification, prompt ou LLM;
  - integration dans `NatalResult`, JSON public, frontend ou services chart;
  - DB, migrations, seeders, SQLAlchemy, API, FastAPI, Pydantic;
  - logique traditionnelle specifique par planete;
  - phases mercuriennes, venusiennes ou lunaires complexes.
- Explicit non-goals:
  - ne pas modifier `backend/app/domain/astrology/advanced_conditions/**`;
  - ne pas modifier `backend/app/domain/astrology/dignities/**`;
  - ne pas modifier `backend/app/domain/astrology/condition/**`;
  - ne pas modifier `backend/app/domain/astrology/dominance/**`;
  - ne pas modifier `backend/app/domain/astrology/interpretation_adapters/**`;
  - ne pas modifier `backend/app/domain/astrology/natal_calculation.py`;
  - ne pas modifier `backend/app/services/chart/json_builder.py`;
  - ne pas ajouter de dossier de base sous `backend/`;
  - ne pas ajouter de shim, alias, fallback, compatibilite ou second owner.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story cree un calculateur domaine pur et un petit
  contrat de seuil; elle ne correspond pas aux archetypes API, suppression,
  migration, route, namespace ou service boundary.
- Additional validation rules:
  - `solar_phase_relation_calculator.py` doit importer uniquement la
    bibliotheque standard et les contrats du meme package;
  - `SolarPhaseRelationThresholds` doit etre une dataclass immuable et slotted;
  - le calcul de l'angle relatif doit etre exactement equivalent a
    `(planet_longitude_deg - sun_longitude_deg) % 360.0` apres normalisation;
  - l'opposition exacte `180.0` doit retourner `OCCIDENTAL` et cette convention
    doit etre documentee dans le code ou la docstring;
  - les comparaisons de conjonction doivent etre basees sur la tolerance et
    ne pas dependre d'une egalite flottante brute;
  - `UNKNOWN` reste reserve au contrat CS-208 et ne doit pas etre produit par
    ce calculateur quand des longitudes numeriques sont fournies;
  - `score`, `score_delta`, `strength_modifier`, `interpretation`, `meaning`,
    `description`, `narrative`, `prompt`, `OpenAI`, `AIEngineAdapter`,
    `heliacal` et `visibility` sont interdits dans le calculateur.
- Behavior change allowed: constrained
- Behavior change constraints:
  - nouveau comportement autorise uniquement via les nouvelles fonctions
    domaine de relation solaire;
  - aucun comportement existant, endpoint, schema public, payload JSON, seed,
    migration, score ou frontend ne change.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: un contrat CS-208 existant rend impossible l'ajout
  de `SolarPhaseRelationThresholds` sans casser les tests de contrats; le dev
  agent doit bloquer au lieu de creer un second contrat concurrent.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les fonctions publiques importables et leurs tests comportementaux prouvent la verite runtime du calcul. |
| Baseline Snapshot | yes | Il faut capturer l'etat CS-208/CS-209/CS-210 et l'etat explicite des guardrails `RG-135`, `RG-136`, `RG-137` et `RG-138`. |
| Ownership Routing | yes | Le calcul pur doit rester dans `planetary_conditions` et ne pas migrer vers API, services, infra ou projections. |
| Allowlist Exception | yes | Les exceptions autorisees doivent rester un registre vide et testable: aucun fallback, alias, shim ou compatibilite n'est autorise. |
| Contract Shape | yes | `SolarPhaseRelationThresholds` et les fonctions publiques ont une forme attendue. |
| Batch Migration | no | Aucun consommateur existant n'est migre. |
| Reintroduction Guard | yes | Les scans doivent bloquer scoring, interpretation, dependances interdites, visibilite avancee et integration adjacente. |
| Persistent Evidence | yes | La validation et les scans doivent etre conserves dans l'artefact de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `calculate_solar_phase_relation`;
  - `calculate_solar_phase_relations`, si implementee;
  - `SolarPhaseRelationThresholds`;
  - les objets `PlanetarySolarPhaseRelation` retournes par les tests unitaires.
- Runtime artifacts:
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py`.
  - AST guard / importability guard:
    `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py`.
  - scans statiques des imports bornes et des symboles interdits definis dans
    le Validation Plan.
- Secondary evidence:
  - tests de contrats CS-208 maintenus;
  - scans des imports interdits, scoring, interpretation et visibilite avancee;
  - `ruff check .`;
  - `pytest -q`.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas l'angle relatif, la tolerance de conjonction, le
    passage 359/0, l'opposition exacte ou le traitement du Soleil.
- Forbidden sources:
  - API, services, infra, DB, frontend, JSON builder, scoring, interpretation,
    visibilite heliacale et proximite solaire.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/planetary_conditions/contracts.py`;
  - `Get-Content backend/app/domain/astrology/planetary_conditions/__init__.py`;
  - `Test-Path backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137|RG-138"`.
- Comparison after implementation:
  - `Test-Path backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`;
  - `rg -n $public_symbols $planetary_condition_paths`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137|RG-138"`.
- Expected invariant:
  - seuls `planetary_conditions`, ses tests, ses exports et les artefacts de
    story changent;
  - `RG-135` reste borne aux contrats, `RG-136` protege le calculateur de
    proximite solaire, `RG-137` protege le calculateur de mouvement, et
    `RG-138` protege le calculateur de relation solaire;
  - aucune integration adjacente n'est introduite.
- Allowed differences:
  - nouveau calculateur de relation solaire;
  - ajout de `SolarPhaseRelationThresholds` si absent;
  - export public explicite;
  - nouveau test unitaire;
  - evidence de validation et verification du garde-fou `RG-138`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrat de seuil de relation solaire | `planetary_conditions/contracts.py` | calculateur local duplique, settings, DB, API schema |
| Calcul pur oriental/occidental | `planetary_conditions/solar_phase_relation_calculator.py` | `advanced_conditions`, `dignities`, `services/chart`, frontend |
| Exports publics du package | `planetary_conditions/__init__.py` | re-export legacy ou alias de compatibilite |
| Tests du calculateur | `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py` | tests API, DB, frontend ou integration chart |
| Integration `NatalResult` | out of scope for CS-211 | `natal_calculation.py`, `json_builder.py` |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-211. | Politique permanente sans exception. |

Validation rule:

- Any required exception must block implementation and require a user decision;
  no wildcard or folder-wide exception may be added.

## 4f. Contract Shape

- Contract type:
  - dataclass domaine immuable `SolarPhaseRelationThresholds`;
  - fonctions pures importables.
- Fields:
  - `SolarPhaseRelationThresholds.conjunction_tolerance_deg`.
- Required fields:
  - `conjunction_tolerance_deg: float = 0.5`.
- Optional fields:
  - none on `SolarPhaseRelationThresholds`.
- Validation rules:
  - `conjunction_tolerance_deg` doit etre fini;
  - `conjunction_tolerance_deg` doit etre superieur ou egal a `0.0`;
  - une tolerance superieure a `180.0` doit lever `ValueError` pour eviter une
    classification qui absorbe tout le cercle zodiacal.
- Result contract:
  - `PlanetarySolarPhaseRelation.planet_key` conserve la cle d'entree;
  - `PlanetarySolarPhaseRelation.relation_key` vaut `CONJUNCT_SOLAR`,
    `OCCIDENTAL` ou `ORIENTAL`;
  - `PlanetarySolarPhaseRelation.angular_distance_deg` vaut l'angle relatif
    normalise dans `[0, 360)`, sauf pour `planet_key == "sun"` ou il vaut
    `0.0`;
  - `is_oriental` vaut `True` uniquement pour `ORIENTAL`;
  - `is_occidental` vaut `True` uniquement pour `OCCIDENTAL`;
  - les deux booleens valent `False` pour `CONJUNCT_SOLAR`.
- Status codes:
  - no HTTP endpoint, method or status code is modified.
- Serialization names:
  - no public JSON serialization is added in CS-211.
- Frontend type impact:
  - no frontend type change.
- Generated contract impact:
  - no OpenAPI, generated client, generated schema or public API contract
    change.
- Public function shape:

```python
calculate_solar_phase_relation(
    *,
    planet_key: str,
    planet_longitude_deg: float,
    sun_longitude_deg: float,
    thresholds: SolarPhaseRelationThresholds | None = None,
) returns PlanetarySolarPhaseRelation
```

```python
calculate_solar_phase_relations(
    *,
    planet_longitudes_deg: Mapping[str, float],
    sun_longitude_deg: float,
    thresholds: SolarPhaseRelationThresholds | None = None,
) returns Mapping[str, PlanetarySolarPhaseRelation]
```

  - la fonction de lot est optionnelle dans le brief; si elle est implementee,
    elle doit rester dans le meme module pur, etre testee et etre exportee.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-211 ne migre aucun consommateur et ne remplace aucun module
  existant.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans et statut `RG-135`/`RG-136`/`RG-137`/`RG-138`. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher que le calculateur de relation solaire pur devienne une couche de
    scoring, interpretation, visibilite avancee, API, persistence, projection
    ou second moteur astrologique adjacent.
- Forbidden examples in `solar_phase_relation_calculator.py`:
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
  - `heliacal`
  - `visibility`
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

- Evidence 1: `_condamad/stories/story-status.md` - `CS-210` est la derniere
  story numerotee avant cette creation et elle est enregistree comme `done`.
- Evidence 2: `_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md`
  - la section `Follow-up Story` annonce `CS-211 - Oriental / Occidental Solar
  Phase Relation Calculator`.
- Evidence 3: `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `PlanetarySolarPhaseRelation` et `SolarPhaseRelationKey` existent deja;
  `SolarPhaseRelationThresholds` n'est pas encore expose dans le fichier lu
  avant la story.
- Evidence 4: `backend/app/domain/astrology/planetary_conditions/__init__.py`
  - les exports publics existent pour les contrats CS-208, le calculateur de
  proximite solaire CS-209 et le calculateur de mouvement CS-210; aucun export
  de relation solaire n'existe encore.
- Evidence 5: `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  - precedent local de calculateur pur a reutiliser comme style, pas comme
  responsabilite.
- Evidence 6: `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - les tests de contrats purs existent et doivent etre maintenus ou etendus
  pour le seuil.
- Evidence 7: `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
  et `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py`
  - precedents de tests calculateurs purs dans le meme package.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - `RG-135` protege
  `contracts.py`, `RG-136` protege le calculateur solaire de proximite,
  `RG-137` protege le mouvement planetaire et cette story ajoute `RG-138` pour
  la relation solaire oriental/occidental.

Assumptions to verify during implementation:

- aucun calculateur canonique de relation solaire n'existe deja dans
  `planetary_conditions`;
- les longitudes fournies sont des nombres finis; si le code existant a une
  politique standard pour les flottants non finis, la story doit la suivre sans
  ajouter de fallback silencieux.

## 6. Target State

After implementation:

- `solar_phase_relation_calculator.py` existe et reste pur;
- `SolarPhaseRelationThresholds` est disponible, immuable et valide sa
  tolerance;
- `_normalize_longitude_deg(value)` normalise les longitudes dans `[0, 360)`;
- `calculate_solar_phase_relation` retourne toujours un
  `PlanetarySolarPhaseRelation` pour des longitudes numeriques valides;
- `relative_angle` est calcule par `(planet - sun) % 360.0`;
- `CONJUNCT_SOLAR` est retourne pour le Soleil et pour les angles dans la
  tolerance autour de `0/360`;
- `OCCIDENTAL` est retourne pour un angle strictement positif jusqu'a `180`
  inclus, avec opposition exacte documentee comme occidentale;
- `ORIENTAL` est retourne pour un angle strictement superieur a `180` et
  inferieur a `360`;
- la fonction de lot, si implementee, retourne un mapping de relations par
  planete;
- aucune integration, scoring, interpretation, visibilite avancee, DB, API ou
  frontend n'est ajoute;
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
    calculer la relation solaire.
  - `RG-129` - le frontend reste display-only et hors scope.
  - `RG-135` - les contrats `contracts.py` restent immutables, sans scoring,
    interpretation ni dependance interdite.
  - `RG-136` - le calculateur de proximite solaire reste borne a cazimi,
    combustion, under beams ou none et ne doit pas absorber oriental/occidental.
  - `RG-137` - le calculateur de mouvement planetaire reste borne au mouvement
    apparent et ne doit pas absorber la relation solaire.
- New durable invariant:
  - verifier la presence de `RG-138` pour proteger
    `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
    comme surface pure, sans scoring, interpretation, visibilite avancee, API,
    DB, services, frontend ou integration `NatalResult`.
- Non-applicable invariants:
  - guardrails de routes API, migrations DB, prompts LLM et CSS frontend; la
    story ne touche pas ces surfaces.
- Required regression evidence:
  - tests unitaires du calculateur;
  - tests de contrats CS-208 maintenus;
  - scans imports interdits, scoring, interpretation, visibilite avancee;
  - diff des surfaces adjacentes obligatoire;
  - `ruff format .`, `ruff check .`, `pytest -q`.
- Allowed differences:
  - nouveau calculateur;
  - ajout de `SolarPhaseRelationThresholds` si absent;
  - export public;
  - nouveau test unitaire;
  - verification ou mise a jour de `RG-138` si le registre derive.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le fichier `solar_phase_relation_calculator.py` existe. | Evidence: `Test-Path $p`, `pytest -q $t`. |
| AC2 | `calculate_solar_phase_relation` est importable. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC3 | `SolarPhaseRelationThresholds` expose la tolerance par defaut. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC4 | `SolarPhaseRelationThresholds` rejette les tolerances invalides. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC5 | Les longitudes sont normalisees dans le cercle zodiacal. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC6 | L'angle relatif applique `(planet - sun) % 360.0`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC7 | `CONJUNCT_SOLAR` est retourne pour angle `0`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC8 | `CONJUNCT_SOLAR` respecte la tolerance autour de `0/360`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC9 | `OCCIDENTAL` est retourne pour l'hemicycle occidental. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC10 | L'opposition exacte est `OCCIDENTAL`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC11 | `ORIENTAL` est retourne pour l'hemicycle oriental. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC12 | `planet_key == "sun"` retourne `CONJUNCT_SOLAR`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC13 | Le resultat utilise `PlanetarySolarPhaseRelation`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC14 | Le calculateur ne produit pas `UNKNOWN` pour des longitudes valides. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC15 | La fonction batch retourne une relation par entree si elle est implementee. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC16 | Le calculateur exclut les dependances interdites. | Evidence: `rg -n "from app\\.api|from app\\.infra|sqlalchemy|fastapi|pydantic" $p`. |
| AC17 | Le calculateur exclut le scoring. | Evidence: `rg -n "\\bscore\\b|score_delta|strength_modifier" $p`. |
| AC18 | Le calculateur exclut l'interpretation. | Evidence: `rg -n "interpretation|meaning|description|narrative|prompt" $p`. |
| AC19 | Le calculateur exclut la visibilite avancee. | Evidence: `rg -n "heliacal|visibility" $p`. |
| AC20 | Aucune integration adjacente n'est ajoutee hors package. | Evidence: `rg -n $public_symbols $adjacent_roots` expected zero hits. |
| AC21 | La qualite backend passe dans le venv. | Evidence profile: `deterministic_test`; `ruff format .`, `ruff check .`, `pytest -q`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer la baseline et confirmer l'ownership (AC: AC1, AC3, AC16, AC17, AC18, AC19, AC20)
  - [ ] Subtask 1.1 - Inspecter `contracts.py`, `__init__.py`,
    `solar_proximity_calculator.py`, `planetary_motion_calculator.py`,
    `test_contracts.py`, CS-208, CS-209, CS-210 et
    `regression-guardrails.md`.
  - [ ] Subtask 1.2 - Verifier l'absence preexistante de
    `solar_phase_relation_calculator.py`.
  - [ ] Subtask 1.3 - Documenter dans l'evidence l'etat attendu de `RG-135`,
    `RG-136`, `RG-137` et `RG-138`.

- [ ] Task 2 - Ajouter le contrat de seuil (AC: AC3, AC4, AC16, AC17, AC18)
  - [ ] Subtask 2.1 - Ajouter `SolarPhaseRelationThresholds` dans
    `contracts.py` si absent.
  - [ ] Subtask 2.2 - Utiliser `dataclass(frozen=True, slots=True)`.
  - [ ] Subtask 2.3 - Valider que la tolerance est finie, positive ou nulle, et
    inferieure ou egale a `180.0`.
  - [ ] Subtask 2.4 - Exporter le contrat depuis `__init__.py`.

- [ ] Task 3 - Creer le calculateur de relation solaire pur (AC: AC1, AC2, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18, AC19)
  - [ ] Subtask 3.1 - Creer `solar_phase_relation_calculator.py`.
  - [ ] Subtask 3.2 - Implementer `_normalize_longitude_deg(value: float)`.
  - [ ] Subtask 3.3 - Implementer l'angle relatif `(planet - sun) % 360.0`.
  - [ ] Subtask 3.4 - Implementer la tolerance de conjonction autour de `0/360`.
  - [ ] Subtask 3.5 - Implementer la convention d'opposition exacte occidentale
    et la documenter.
  - [ ] Subtask 3.6 - Implementer le cas `planet_key == "sun"`.
  - [ ] Subtask 3.7 - Implementer la fonction batch si elle est retenue dans le
    meme module pur.
  - [ ] Subtask 3.8 - Exporter les fonctions publiques depuis `__init__.py`.

- [ ] Task 4 - Ajouter les tests unitaires (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15)
  - [ ] Subtask 4.1 - Creer
    `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py`.
  - [ ] Subtask 4.2 - Tester occidental, oriental, conjonction exacte et
    tolerance par defaut.
  - [ ] Subtask 4.3 - Tester opposition exacte `180.0` comme occidentale.
  - [ ] Subtask 4.4 - Tester passage `359/0` et normalisation `361`, `-1`,
    `720`.
  - [ ] Subtask 4.5 - Tester le Soleil.
  - [ ] Subtask 4.6 - Tester seuil personnalise et seuil invalide.
  - [ ] Subtask 4.7 - Tester la fonction batch si elle est implementee.
  - [ ] Subtask 4.8 - Etendre `test_contracts.py` pour
    `SolarPhaseRelationThresholds` si le contrat est ajoute.

- [ ] Task 5 - Ajouter et prouver les gardes anti-drift (AC: AC16, AC17, AC18, AC19, AC20)
  - [ ] Subtask 5.1 - Verifier que `RG-135` protege toujours les contrats purs.
  - [ ] Subtask 5.2 - Verifier que `RG-136` reste borne a la proximite solaire.
  - [ ] Subtask 5.3 - Verifier que `RG-137` reste borne au mouvement
    planetaire.
  - [ ] Subtask 5.4 - Verifier ou mettre a jour `RG-138` pour le calculateur de
    relation solaire pur.
  - [ ] Subtask 5.5 - Executer les scans imports interdits, scoring,
    interpretation, visibilite avancee et surfaces adjacentes.

- [ ] Task 6 - Valider la story (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18, AC19, AC20, AC21)
  - [ ] Subtask 6.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 6.2 - Executer le test cible.
  - [ ] Subtask 6.3 - Executer `ruff format .`, `ruff check .` et `pytest -q`.
  - [ ] Subtask 6.4 - Documenter les resultats dans `evidence/validation.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetarySolarPhaseRelation` et `SolarPhaseRelationKey` depuis
    `contracts.py`;
  - conventions `dataclass(frozen=True, slots=True)` existantes;
  - style local de `solar_proximity_calculator.py` et
    `planetary_motion_calculator.py`;
  - tests pytest sous `backend/tests/unit/domain/astrology/planetary_conditions`.
- Do not recreate:
  - contrats CS-208 sous un autre nom ou dans un autre package;
  - calculateur de proximite solaire;
  - calculateur de mouvement planetaire;
  - visibilite heliacale ou phases planetaires avancees;
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
- visibilite avancee, heliacal rising, heliacal setting
- combustion, cazimi, under beams

Specific forbidden symbols / paths:

- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
  importing `app.api`
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
  importing `app.infra`
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
  importing `app.infrastructure`
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
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
- `heliacal`
- `visibility`
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
| Seuil de conjonction solaire | `planetary_conditions/contracts.py` | settings, DB, API schema |
| Calcul angle relatif Soleil-planete | `planetary_conditions/solar_phase_relation_calculator.py` | `solar_proximity_calculator.py`, `advanced_conditions`, `dignities`, frontend |
| Classification oriental/occidental/conjoint | `planetary_conditions/solar_phase_relation_calculator.py` | scoring, dominance, interpretation adapters |
| Exports publics | `planetary_conditions/__init__.py` | alias ou re-export legacy |
| Integration future | future story | CS-211 ne modifie pas `NatalResult` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Artifact Check

- Generated artifact check: not applicable
- Reason: no generated file, generated schema, generated client or generated
  documentation is affected by CS-211.

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
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py`
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/astrology/advanced_conditions/contracts.py` only for
  style comparison, not modification.

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/planetary_conditions/contracts.py` - ajouter
  `SolarPhaseRelationThresholds` si absent.
- `backend/app/domain/astrology/planetary_conditions/__init__.py` - exporter
  seuils et fonctions publiques.
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
  - nouveau calculateur pur.
- `_condamad/stories/regression-guardrails.md` - verifier ou mettre a jour
  `RG-138`.
- `_condamad/stories/CS-211-solar-phase-relation-calculator/evidence/validation.md`
  - preuves de validation.

Likely tests:

- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py`
  - couverture comportementale du calculateur.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - couverture du nouveau seuil si ajoute.

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

- Next planned story: `CS-212 - Moon Phase Calculator`
- Expected scope: calculer les phases lunaires, waxing/waning, illumination et
  segmentation angulaire Soleil-Lune depuis les contrats CS-208.
- Boundary: CS-211 ne cree aucun calculateur de phase lunaire et ne prepare pas
  d'integration opportuniste pour CS-212.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.
- Justification: la bibliotheque standard et les contrats CS-208 suffisent.

## 21. Validation Plan

All Python commands must be run after activating the venv from repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

Targeted tests:

```powershell
$t = "backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py"
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
$p = "backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py"
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
$public_symbols = "SolarPhaseRelationThresholds|calculate_solar_phase_relation|calculate_solar_phase_relations"
rg -n "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services" $p
rg -n "sqlalchemy|fastapi|pydantic|OpenAI|AIEngineAdapter" $p
rg -n "\\bscore\\b|score_delta|accidental_score_delta|essential_score_delta|strength_modifier" $p
rg -n "interpretation|meaning|description|narrative|prompt|heliacal|visibility" $p
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
- interpretation/narration/prompt/heliacal/visibility: zero hits;
- symbols publics: hits limites aux nouveaux modules, exports et tests;
- symbols publics dans les surfaces adjacentes: zero hits;
- diff des surfaces adjacentes: vide.

Story validation commands:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Skipped-command rule:

- Any skipped command must be recorded in the final evidence with exact
  command, reason, risk and fallback evidence.

## 22. Regression Risks

- Risk: le calculateur de relation solaire devient une source de scoring avant
  une story dediee.
  - Guardrail: AC17, scans scoring et `RG-138`.
- Risk: le calculateur absorbe la proximite solaire ou les phases heliacales.
  - Guardrail: AC19, interdits `heliacal`/`visibility`, non-goals et
    comparaison avec `RG-136`.
- Risk: l'opposition exacte est classee differemment selon les tests.
  - Guardrail: AC10 impose `180.0` comme `OCCIDENTAL` et une documentation dans le
    code.
- Risk: les longitudes hors cercle produisent une relation fausse autour de
  `0/360`.
  - Guardrail: AC3, AC4 et tests de normalisation.
- Risk: une integration opportuniste modifie le JSON public ou `NatalResult`.
  - Guardrail: AC20 et diff des surfaces adjacentes obligatoire.

## 23. Dev Agent Instructions

- Implement only CS-211.
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
  models, heliacal phases, visibility engine, combustion, cazimi or under beams.
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
  - precedent local de calculateur pur recent.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - tests de contrats a maintenir.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
  - precedent de tests calculateur.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py`
  - precedent de tests calculateur avec fonction de lot.
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
  - source contractuelle.
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
  - precedent proximite solaire.
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md`
  - precedent et follow-up explicite CS-211.
- `_condamad/stories/regression-guardrails.md` - invariants applicables
  `RG-107`, `RG-119`, `RG-122`, `RG-128`, `RG-129`, `RG-135`, `RG-136`,
  `RG-137` et nouvel invariant `RG-138`.
