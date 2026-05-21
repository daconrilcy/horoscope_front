# Story CS-213 planetary-visibility-conditions-calculator: Calculer les conditions de visibilite planetaire

Status: ready-to-dev

## 1. Objective

Creer un calculateur domaine pur qui determine la condition de visibilite
symbolique d'une planete depuis les resultats deja calcules de proximite
solaire CS-209 et de relation solaire CS-211. Le calculateur doit retourner
`PlanetVisibilityCondition`, gerer le Soleil, la conjonction solaire, le cazimi,
la combustion, les rayons solaires, l'emergence orientale et la visibilite
simple, sans recalculer la distance solaire ni l'orientation, sans scoring,
sans interpretation, sans heliacal astronomy reel, sans API, sans DB et sans
integration `NatalResult`.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-21 pour `CS-213 - Planetary
  Visibility Conditions Calculator`.
- Reason for change: CS-208 expose `PlanetVisibilityCondition` et
  `PlanetVisibilityKey`, CS-209 produit la proximite solaire, CS-211 produit la
  relation oriental/occidental, mais aucun calculateur pur ne compose encore ces
  faits pour produire la visibilite planetaire.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story reprend le brief comme un calculateur
  mono-domaine. Les AC couvrent creation du module, seuils, ajout minimal de
  `CONJUNCT_SOLAR` au contrat existant, priorite stricte, cas Soleil, cazimi,
  combustion, under beams, emergence seulement orientale, visible par defaut,
  batch optionnel implemente, interdits de scoring/interpretation/heliacal reel
  et validations. Les exclusions du brief restent hors scope.
- Brief-stakes alignment: la visibilite planetaire est traitee comme un fait
  astrologique expert qui qualifie la manifestation visible d'une planete sans
  encore produire force, score ou interpretation. La story preserve donc
  l'enjeu hellenistique, medieval, arabe, persan et renaissance du brief tout en
  limitant CS-213 a un contrat factuel reutilisable par les stories suivantes.
- Source ambiguity resolved: le brief mentionne les longitudes Soleil/planete,
  mais demande aussi de ne pas recalculer la distance solaire ni l'orientation.
  CS-213 consomme donc les faits deja derives par CS-209 et CS-211:
  `sun_distance_deg`, `condition_key` et `relation_key`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/planetary_conditions`
- In scope:
  - creer `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`;
  - ajouter `PlanetVisibilityThresholds` dans `contracts.py`;
  - ajouter la valeur contractuelle manquante
    `PlanetVisibilityKey.CONJUNCT_SOLAR = "conjunct_solar"`;
  - reutiliser `PlanetVisibilityCondition`, `PlanetVisibilityKey`,
    `SolarProximityCondition`, `SolarProximityConditionKey`,
    `PlanetarySolarPhaseRelation`, `SolarPhaseRelationKey` et
    `ConditionConfidence`;
  - calculer une seule visibilite par planete depuis
    `solar_proximity_condition.sun_distance_deg`,
    `solar_proximity_condition.condition_key` et
    `solar_phase_relation.relation_key`;
  - appliquer la priorite stricte `CONJUNCT_SOLAR > INVISIBLE > UNDER_BEAMS >
    EMERGING > VISIBLE`;
  - traiter `SolarProximityConditionKey.CAZIMI` comme `CONJUNCT_SOLAR` visible;
  - implementer la fonction de lot pure;
  - exporter seuils et fonctions publiques depuis `__init__.py`;
  - ajouter les tests unitaires cibles;
  - ajouter un commentaire global en francais et des docstrings francaises dans
    les fichiers applicatifs nouveaux ou significativement modifies.
- Out of scope:
  - heliacal rising complet;
  - heliacal setting complet;
  - magnitude astronomique reelle;
  - latitude ecliptique, altitude, horizon, topocentrisme, meteo ou atmosphere;
  - visibilite observee reelle;
  - recalcul de combustion, cazimi, under beams, distance solaire ou relation
    oriental/occidental;
  - scoring, force, dignites, dominance, profils ou signaux interpretatifs;
  - interpretation, narration, signification, description produit ou prompt;
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
- Archetype reason: la story cree un calculateur domaine pur et ajuste
  minimalement un contrat domaine existant; elle ne correspond pas aux
  archetypes API, suppression, migration, route, namespace ou service boundary.
- Additional validation rules:
  - `planetary_visibility_calculator.py` doit importer uniquement
    `collections.abc.Mapping` et les contrats du meme package;
  - le calculateur doit faire confiance a `SolarProximityCondition` et
    `PlanetarySolarPhaseRelation`; il ne recalcule pas la distance ni
    l'orientation;
  - le calculateur ne consomme pas `sun_longitude_deg` ou
    `planet_longitude_deg`: les longitudes brutes restent la responsabilite des
    calculateurs amont;
  - `PlanetVisibilityThresholds` doit valider des seuils finis et ordonnes:
    `0 <= conjunction_tolerance_deg <= under_beams_limit_deg <= emerging_limit_deg`;
  - `CONJUNCT_SOLAR` doit etre retourne si `sun_distance_deg <=
    conjunction_tolerance_deg` ou si `condition_key == CAZIMI`;
  - `COMBUST` doit retourner `INVISIBLE`;
  - `UNDER_BEAMS` doit retourner `UNDER_BEAMS` meme si la distance parait
    incoherente, car cette story ne corrige pas les calculateurs amont;
  - `EMERGING` est autorise seulement si `sun_distance_deg >
    under_beams_limit_deg`, `sun_distance_deg <= emerging_limit_deg` et
    `relation_key == ORIENTAL`;
  - `HELIACAL_RISING`, `HELIACAL_SETTING` et `UNKNOWN` restent des placeholders
    contractuels et ne doivent pas etre produits par le calculateur pour des
    entrees coherentes valides;
  - `score`, `score_delta`, `strength_modifier`, `interpretation`, `meaning`,
    `description`, `narrative`, `prompt`, `OpenAI`, `AIEngineAdapter`,
    `NatalResult`, `horizon`, `altitude`, `weather`, `topocentric`,
    `magnitude`, `latitude`, `ephemeris`, `FastAPI`, `SQLAlchemy` et
    `pydantic` sont interdits dans le calculateur.
- Behavior change allowed: constrained
- Behavior change constraints:
  - nouveau comportement autorise uniquement via les nouveaux contrats/fonctions
    domaine de visibilite planetaire;
  - le seul changement contractuel autorise est l'ajout de
    `PlanetVisibilityKey.CONJUNCT_SOLAR` et de `PlanetVisibilityThresholds`;
  - aucun endpoint, schema public, payload JSON, seed, migration, score,
    frontend ou comportement existant hors `planetary_conditions` ne change.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: l'ajout de `PlanetVisibilityKey.CONJUNCT_SOLAR`
  casse un contrat externe non visible dans le repository; le dev agent doit
  bloquer au lieu de representer la conjonction par une valeur ambigue.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les fonctions publiques importables et leurs tests comportementaux prouvent la verite runtime du calcul. |
| Baseline Snapshot | yes | Il faut capturer l'etat CS-208 a CS-212 et les guardrails `RG-135` a `RG-139`. |
| Ownership Routing | yes | Le calcul pur doit rester dans `planetary_conditions` et ne pas migrer vers API, services, infra, projections ou moteurs avances. |
| Allowlist Exception | yes | Les exceptions autorisees doivent rester un registre vide et testable: aucun fallback, alias, shim ou compatibilite n'est autorise. |
| Contract Shape | yes | `PlanetVisibilityThresholds`, `PlanetVisibilityKey.CONJUNCT_SOLAR` et les fonctions publiques ont une forme attendue. |
| Batch Migration | no | Aucun consommateur existant n'est migre. |
| Reintroduction Guard | yes | Les scans doivent bloquer scoring, interpretation, dependances interdites, heliacal reel et integration adjacente. |
| Persistent Evidence | yes | La validation et les scans doivent etre conserves dans l'artefact de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `calculate_planet_visibility_condition`;
  - `calculate_planet_visibility_conditions`;
  - les objets `PlanetVisibilityCondition` retournes par les tests unitaires;
  - `PlanetVisibilityThresholds` et `PlanetVisibilityKey` importes depuis le
    package public.
- Runtime artifacts:
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py`;
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`.
  - AST guard / importability guard:
    `pytest -q backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py`
    et les scans `rg` bornes listés dans le Validation Plan.
- Secondary evidence:
  - scans des imports interdits, scoring, interpretation, heliacal reel,
    astronomie observationnelle et integration adjacente;
  - `ruff check .`;
  - `pytest -q`.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas la priorite, le cazimi visible, l'emergence seulement
    orientale, les seuils personnalises, le batch ou le cas Soleil.
- Forbidden sources:
  - API, services, infra, DB, frontend, JSON builder, scoring, interpretation,
    heliacal astronomy reel et recalcul des calculateurs amont.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/planetary_conditions/contracts.py`;
  - `Get-Content backend/app/domain/astrology/planetary_conditions/__init__.py`;
  - `Test-Path backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`;
  - `Test-Path backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137|RG-138|RG-139|RG-140"`.
- Comparison after implementation:
  - `Test-Path backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`;
  - `Test-Path backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py`;
  - `rg -n $public_symbols $planetary_condition_paths`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137|RG-138|RG-139|RG-140"`.
- Expected invariant:
  - seuls `planetary_conditions`, ses tests, ses exports et les artefacts de
    story changent;
  - `RG-135` reste borne aux contrats, `RG-136` a la proximite solaire,
    `RG-137` au mouvement, `RG-138` a la relation solaire, `RG-139` a la phase
    lunaire et `RG-140` protege ce nouveau calculateur;
  - aucune integration adjacente n'est introduite.
- Allowed differences:
  - nouveau calculateur de visibilite planetaire;
  - ajout de `PlanetVisibilityThresholds`;
  - ajout de `PlanetVisibilityKey.CONJUNCT_SOLAR`;
  - export public explicite;
  - nouveau test unitaire;
  - evidence de validation et verification ou ajout de `RG-140`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrat de seuils de visibilite | `planetary_conditions/contracts.py` | settings, DB, API schema, calculateur local duplique |
| Valeurs de visibilite | `planetary_conditions/contracts.py` | enum locale, string libre, frontend |
| Calcul pur de visibilite | `planetary_conditions/planetary_visibility_calculator.py` | `advanced_conditions`, `dignities`, `services/chart`, frontend |
| Exports publics du package | `planetary_conditions/__init__.py` | re-export legacy ou alias de compatibilite |
| Tests du calculateur | `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py` | tests API, DB, frontend ou integration chart |
| Integration `NatalResult` | future story CS-214 | `natal_calculation.py`, `json_builder.py` dans CS-213 |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-213. | Politique permanente sans exception. |

Validation rule:

- Toute exception requise doit bloquer l'implementation et exiger une decision
  utilisateur; aucune exception wildcard ou dossier entier ne doit etre ajoutee.

## 4f. Contract Shape

- Contract type:
  - dataclass domaine immuable `PlanetVisibilityThresholds`;
  - valeur enum `PlanetVisibilityKey.CONJUNCT_SOLAR`;
  - fonctions pures importables.
- Fields:
  - `PlanetVisibilityThresholds.conjunction_tolerance_deg`;
  - `PlanetVisibilityThresholds.under_beams_limit_deg`;
  - `PlanetVisibilityThresholds.emerging_limit_deg`;
  - `PlanetVisibilityCondition.planet_key`;
  - `PlanetVisibilityCondition.visibility_key`;
  - `PlanetVisibilityCondition.is_visible`;
  - `PlanetVisibilityCondition.confidence`;
  - `PlanetVisibilityCondition.reason`.
- Required fields:
  - `conjunction_tolerance_deg: float = 0.5`;
  - `under_beams_limit_deg: float = 15.0`;
  - `emerging_limit_deg: float = 18.0`;
  - `visibility_key: PlanetVisibilityKey`;
  - `is_visible: bool | None`;
  - `confidence: ConditionConfidence`;
  - `reason: str | None`.
- Optional fields:
  - `thresholds: PlanetVisibilityThresholds | None = None` sur les fonctions
    publiques.
- Validation rules:
  - les seuils doivent etre finis;
  - `conjunction_tolerance_deg`, `under_beams_limit_deg` et
    `emerging_limit_deg` doivent etre positifs ou nuls;
  - l'ordre doit satisfaire `conjunction_tolerance_deg <=
    under_beams_limit_deg <= emerging_limit_deg`.
- Status codes:
  - aucun endpoint HTTP, methode ou status code n'est modifie.
- Serialization names:
  - aucune serialization JSON publique n'est ajoutee dans CS-213.
- Frontend type impact:
  - aucun type frontend ne change.
- Generated contract impact:
  - aucun contrat OpenAPI, client genere, schema genere ou contrat API public
    ne change.
- Public function shape:

```python
calculate_planet_visibility_condition(
    *,
    planet_key: str,
    solar_proximity_condition: SolarProximityCondition,
    solar_phase_relation: PlanetarySolarPhaseRelation,
    thresholds: PlanetVisibilityThresholds | None = None,
) -> PlanetVisibilityCondition
```

```python
calculate_planet_visibility_conditions(
    *,
    solar_proximity_conditions: Mapping[str, SolarProximityCondition],
    solar_phase_relations: Mapping[str, PlanetarySolarPhaseRelation],
    thresholds: PlanetVisibilityThresholds | None = None,
) -> Mapping[str, PlanetVisibilityCondition]
```

- Visibility mapping:
  - `planet_key == "sun"` -> `VISIBLE`, `is_visible=True`,
    `confidence=HIGH`, `reason="sun_visible"`;
  - distance inferieure ou egale a `conjunction_tolerance_deg` ou `CAZIMI` ->
    `CONJUNCT_SOLAR`,
    `is_visible=True`, `confidence=EXACT`, `reason="solar_conjunction"`;
  - `COMBUST` -> `INVISIBLE`, `is_visible=False`, `confidence=HIGH`,
    `reason="combust"`;
  - `UNDER_BEAMS` -> `UNDER_BEAMS`, `is_visible=False`, `confidence=HIGH`,
    `reason="under_beams"`;
  - relation orientale et distance strictement superieure a
    `under_beams_limit_deg`, puis inferieure ou egale a `emerging_limit_deg` ->
    `EMERGING`, `is_visible=True`, `confidence=MEDIUM`,
    `reason="planet_exiting_solar_beams"`;
  - sinon -> `VISIBLE`, `is_visible=True`, `confidence=HIGH`,
    `reason="outside_visibility_restrictions"`.
- Near-emergence handling:
  - le brief mentionne une planete "proche de l'emergence", mais CS-208 ne
    fournit pas de cle `NEAR_EMERGENCE`;
  - dans CS-213, cette intention est couverte par la fenetre simplifiee
    `EMERGING` (`under_beams_limit_deg < distance <= emerging_limit_deg`) et
    ne cree pas de nouvelle valeur enum locale.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-213 ne migre aucun consommateur et ne remplace aucun module
  existant.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans et statut `RG-135` a `RG-140`. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher que le calculateur de visibilite planetaire pur devienne une
    couche d'heliacal astronomy reel, scoring, interpretation, API,
    persistence, projection ou second moteur astrologique adjacent.
- Forbidden examples in `planetary_visibility_calculator.py`:
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
  - `horizon`
  - `altitude`
  - `weather`
  - `topocentric`
  - `magnitude`
  - `latitude`
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

- Evidence 1: `_condamad/stories/story-status.md` - `CS-212` est la derniere
  story numerotee avant cette creation et elle est enregistree comme `done`.
- Evidence 2: `_condamad/stories/CS-212-moon-phase-calculator/00-story.md` - la
  section `Follow-up Story` annonce `CS-213 - Planetary Visibility Conditions
  Calculator`.
- Evidence 3: `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `PlanetVisibilityCondition` et `PlanetVisibilityKey` existent deja, mais
  `PlanetVisibilityThresholds` et `PlanetVisibilityKey.CONJUNCT_SOLAR` sont
  absents dans l'etat courant.
- Evidence 4: `backend/app/domain/astrology/planetary_conditions/__init__.py`
  - les contrats et calculateurs CS-209 a CS-212 sont exportes, mais aucun
  calculateur de visibilite planetaire n'est exporte.
- Evidence 5: `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  - precedent local fournissant `SolarProximityCondition.sun_distance_deg` et
  `SolarProximityConditionKey`.
- Evidence 6: `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
  - precedent local fournissant `PlanetarySolarPhaseRelation.relation_key`.
- Evidence 7: `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - les valeurs de `PlanetVisibilityKey` sont testees et devront etre etendues.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - `RG-135` protege
  les contrats, `RG-136` la proximite solaire, `RG-137` le mouvement, `RG-138`
  la relation solaire et `RG-139` la phase lunaire.

Assumptions to verify during implementation:

- aucun calculateur canonique de visibilite planetaire n'existe deja dans
  `planetary_conditions`;
- les mappings fournis a la fonction batch ont les memes cles; une cle absente
  dans `solar_phase_relations` doit lever `KeyError` naturellement ou une
  erreur explicite, mais ne doit pas produire `UNKNOWN` silencieusement.

## 6. Target State

After implementation:

- `planetary_visibility_calculator.py` existe et reste pur;
- `PlanetVisibilityThresholds` est disponible, immuable et valide ses seuils;
- `PlanetVisibilityKey.CONJUNCT_SOLAR` existe et les tests de contrats sont
  mis a jour;
- `calculate_planet_visibility_condition` retourne toujours un
  `PlanetVisibilityCondition` pour des contrats d'entree valides;
- le Soleil retourne `VISIBLE`;
- le cazimi et la conjonction solaire retournent `CONJUNCT_SOLAR` visible;
- `COMBUST` retourne `INVISIBLE`;
- `UNDER_BEAMS` retourne `UNDER_BEAMS`;
- `EMERGING` est retourne uniquement pour une planete orientale dans la fenetre
  `15.0 < distance <= 18.0` par defaut;
- la notion de "proche de l'emergence" du brief est materialisee par cette
  meme fenetre `EMERGING`, sans etat contractuel supplementaire;
- une planete occidentale dans la meme fenetre retourne `VISIBLE`;
- les placeholders `HELIACAL_RISING`, `HELIACAL_SETTING` et `UNKNOWN` ne sont
  pas produits par le calculateur nominal;
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
    calculer la visibilite planetaire.
  - `RG-129` - le frontend reste display-only et hors scope.
  - `RG-135` - les contrats `contracts.py` restent immutables, sans scoring,
    interpretation ni dependance interdite.
  - `RG-136` - le calculateur de proximite solaire reste owner de cazimi,
    combustion et under beams.
  - `RG-138` - le calculateur de relation solaire reste owner de
    oriental/occidental/conjoint solaire.
  - `RG-139` - le calculateur de phase lunaire reste borne a la Lune et ne doit
    pas absorber la visibilite planetaire.
- New durable invariant:
  - verifier ou ajouter `RG-140` pour proteger
    `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
    comme surface pure, sans scoring, interpretation, heliacal astronomy reel,
    API, DB, services, frontend ou integration `NatalResult`.
- Non-applicable invariants:
  - guardrails de routes API, migrations DB, prompts LLM et CSS frontend; la
    story ne touche pas ces surfaces.
- Required regression evidence:
  - tests unitaires du calculateur;
  - tests de contrats CS-208 maintenus et etendus;
  - scans imports interdits, scoring, interpretation, heliacal reel et
    integration adjacente;
  - diff des surfaces adjacentes obligatoire;
  - `ruff format .`, `ruff check .`, `pytest -q`.
- Allowed differences:
  - nouveau calculateur;
  - ajout de `PlanetVisibilityThresholds`;
  - ajout de `PlanetVisibilityKey.CONJUNCT_SOLAR`;
  - export public;
  - nouveau test unitaire;
  - verification ou mise a jour de `RG-140`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le fichier `planetary_visibility_calculator.py` existe. | Evidence: `Test-Path $p`, `pytest -q $t`. |
| AC2 | `PlanetVisibilityThresholds` expose des seuils par defaut ordonnes. | Evidence: `pytest -q $t`; `pytest -q $contracts`. |
| AC3 | `PlanetVisibilityKey.CONJUNCT_SOLAR` existe avec la valeur `conjunct_solar`. | Evidence profile: `deterministic_test`; `pytest -q test_contracts.py`. |
| AC4 | `calculate_planet_visibility_condition` est importable depuis le package public. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC5 | Le Soleil retourne une visibilite solaire nominale. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC6 | Une conjonction solaire retourne `CONJUNCT_SOLAR`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC7 | Une planete `COMBUST` retourne `INVISIBLE`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC8 | Une planete `UNDER_BEAMS` retourne `UNDER_BEAMS`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC9 | Une planete orientale avec `15.0 < distance <= 18.0` retourne `EMERGING`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC10 | Une planete occidentale dans la fenetre d'emergence ne retourne pas `EMERGING`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC11 | Aucune condition restrictive retourne `VISIBLE`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC12 | La priorite `CONJUNCT_SOLAR > INVISIBLE > UNDER_BEAMS > EMERGING > VISIBLE` est respectee. | Evidence profile: `deterministic_test`; tests de collision; `pytest -q $t`. |
| AC13 | Les seuils personnalises modifient la classification. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC14 | La fonction de lot retourne une visibilite par cle de proximite fournie. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC15 | Le calculateur ne produit pas `UNKNOWN`, `HELIACAL_RISING` ou `HELIACAL_SETTING` pour les cas nominaux. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC16 | Le calculateur exclut les dependances interdites. | Evidence: `rg -n $forbidden_deps $p`; aucun hit attendu. |
| AC17 | Le calculateur exclut les symboles de scoring. | Evidence: `rg -n "score|score_delta|strength_modifier" $p`; aucun hit attendu. |
| AC18 | Le calculateur exclut le texte interpretatif. | Evidence: `rg -n "interpretation|meaning|description|narrative|prompt" $p`; aucun hit attendu. |
| AC19 | Le calculateur exclut l'astronomie observationnelle. | Evidence: `rg -n $forbidden_observation $p`; aucun hit attendu. |
| AC20 | Pas d'integration adjacente hors package. | Evidence: `rg -n $public_symbols $adjacent_roots`; `rg -n $forbidden_global_integration $p`. |
| AC21 | La qualite backend passe dans le venv. | Evidence profile: `deterministic_test`; `ruff format .`, `ruff check .`, `pytest -q`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer la baseline et confirmer l'ownership (AC: AC1, AC2, AC3, AC16, AC17, AC18, AC19, AC20)
  - [ ] Subtask 1.1 - Inspecter `contracts.py`, `__init__.py`,
    `solar_proximity_calculator.py`, `solar_phase_relation_calculator.py`,
    `moon_phase_calculator.py`, `test_contracts.py`, CS-208 a CS-212 et
    `regression-guardrails.md`.
  - [ ] Subtask 1.2 - Verifier l'absence preexistante de
    `planetary_visibility_calculator.py` et
    `test_planetary_visibility_calculator.py`.
  - [ ] Subtask 1.3 - Documenter dans l'evidence l'etat attendu de `RG-135` a
    `RG-140`.

- [ ] Task 2 - Ajuster les contrats de visibilite (AC: AC2, AC3, AC16, AC17, AC18)
  - [ ] Subtask 2.1 - Ajouter `PlanetVisibilityThresholds` dans `contracts.py`.
  - [ ] Subtask 2.2 - Ajouter `PlanetVisibilityKey.CONJUNCT_SOLAR` sans retirer
    les placeholders `HELIACAL_RISING` et `HELIACAL_SETTING`.
  - [ ] Subtask 2.3 - Etendre les exports publics dans `__init__.py`.
  - [ ] Subtask 2.4 - Etendre `test_contracts.py` pour les seuils et la valeur
    enum.

- [ ] Task 3 - Creer le calculateur de visibilite pur (AC: AC1, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18, AC19)
  - [ ] Subtask 3.1 - Creer `planetary_visibility_calculator.py`.
  - [ ] Subtask 3.2 - Implementer `_resolve_visibility_key`.
  - [ ] Subtask 3.3 - Implementer `_resolve_visibility_confidence`.
  - [ ] Subtask 3.4 - Implementer `_resolve_visibility_reason`.
  - [ ] Subtask 3.5 - Implementer `calculate_planet_visibility_condition`.
  - [ ] Subtask 3.6 - Implementer `calculate_planet_visibility_conditions`.
  - [ ] Subtask 3.7 - Exporter les fonctions publiques depuis `__init__.py`.

- [ ] Task 4 - Ajouter les tests unitaires (AC: AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15)
  - [ ] Subtask 4.1 - Creer
    `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py`.
  - [ ] Subtask 4.2 - Tester visible, invisible, under beams, emerging, cazimi,
    conjonction, Soleil, priorite, seuils personnalises et batch.
  - [ ] Subtask 4.3 - Tester qu'une planete occidentale n'est pas emerging.
  - [ ] Subtask 4.4 - Tester que les placeholders heliacaux et `UNKNOWN` ne
    sont pas produits par les cas nominaux.

- [ ] Task 5 - Ajouter et prouver les gardes anti-drift (AC: AC16, AC17, AC18, AC19, AC20)
  - [ ] Subtask 5.1 - Verifier que `RG-135` protege toujours les contrats purs.
  - [ ] Subtask 5.2 - Verifier que `RG-136`, `RG-138` et `RG-139` restent
    bornes a leurs calculateurs.
  - [ ] Subtask 5.3 - Verifier ou ajouter `RG-140` pour le calculateur de
    visibilite planetaire pur.
  - [ ] Subtask 5.4 - Executer les scans imports interdits, scoring,
    interpretation, heliacal reel et surfaces adjacentes.

- [ ] Task 6 - Valider la story (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17, AC18, AC19, AC20, AC21)
  - [ ] Subtask 6.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 6.2 - Executer le test cible.
  - [ ] Subtask 6.3 - Executer `ruff format .`, `ruff check .` et `pytest -q`.
  - [ ] Subtask 6.4 - Documenter les resultats dans `evidence/validation.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetVisibilityCondition`, `PlanetVisibilityKey` et
    `ConditionConfidence` depuis `contracts.py`;
  - `SolarProximityCondition` et `SolarProximityConditionKey` depuis
    `contracts.py`;
  - `PlanetarySolarPhaseRelation` et `SolarPhaseRelationKey` depuis
    `contracts.py`;
  - conventions des calculateurs purs `solar_proximity_calculator.py`,
    `solar_phase_relation_calculator.py` et `moon_phase_calculator.py`;
  - tests pytest sous `backend/tests/unit/domain/astrology/planetary_conditions`.
- Do not recreate:
  - contrats CS-208 sous un autre nom ou dans un autre package;
  - calculateur de proximite solaire;
  - calculateur de relation solaire oriental/occidental;
  - moteur heliacal ou observationnel;
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
- heliacal rising/setting reel
- horizon, altitude, meteo, magnitude ou latitude observationnelle
- integration `NatalResult`

Specific forbidden symbols / paths:

- `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
  importing `app.api`
- `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
  importing `app.infra`
- `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
  importing `app.infrastructure`
- `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
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
- `horizon`
- `altitude`
- `weather`
- `topocentric`
- `magnitude`
- `latitude`
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
| Seuils de visibilite planetaire | `planetary_conditions/contracts.py` | settings, DB, API schema |
| Valeur `CONJUNCT_SOLAR` de visibilite | `planetary_conditions/contracts.py` | string libre, enum locale |
| Composition proximite + relation solaire | `planetary_conditions/planetary_visibility_calculator.py` | calculateurs amont, services |
| Exports publics | `planetary_conditions/__init__.py` | alias ou re-export legacy |
| Integration future | future story CS-214 | CS-213 ne modifie pas `NatalResult` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Artifact Check

- Generated artifact check: not applicable
- Reason: no generated file, generated schema, generated client or generated
  documentation is affected by CS-213.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, frontend
  type or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
- `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_phase_relation_calculator.py`
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
- `_condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md`
- `_condamad/stories/CS-212-moon-phase-calculator/00-story.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/planetary_conditions/contracts.py` - ajouter
  `PlanetVisibilityThresholds` et `PlanetVisibilityKey.CONJUNCT_SOLAR`.
- `backend/app/domain/astrology/planetary_conditions/__init__.py` - exporter
  seuils et fonctions publiques.
- `backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py`
  - nouveau calculateur pur.
- `_condamad/stories/regression-guardrails.md` - verifier ou ajouter
  l'invariant `RG-140`.
- `_condamad/stories/CS-213-planetary-visibility-conditions-calculator/evidence/validation.md`
  - preuves de validation.

Likely tests:

- `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py`
  - couverture comportementale du calculateur.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - couverture du nouveau seuil et de la valeur enum.

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

- Next planned story: `CS-214 - Integrate Advanced Planetary Conditions Into
  NatalResult`
- Expected scope: integrer proximite solaire, mouvement, relation solaire,
  phase lunaire et visibilite dans le runtime natal global.
- Boundary: CS-213 ne cree aucune integration `NatalResult`, projection JSON,
  API, DB ou frontend.

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
$t = "backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_visibility_calculator.py"
$contracts = "backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py"
pytest -q $t
pytest -q $contracts
```

Quality checks:

```powershell
ruff format .
ruff check .
pytest -q
```

Required scans:

```powershell
$p = "backend/app/domain/astrology/planetary_conditions/planetary_visibility_calculator.py"
$planetary_condition_paths = "backend/app/domain/astrology/planetary_conditions", "backend/tests/unit/domain/astrology/planetary_conditions"
$forbidden_deps = "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services|sqlalchemy|fastapi|pydantic|OpenAI|AIEngineAdapter"
$forbidden_observation = "horizon|altitude|weather|topocentric|magnitude|latitude|ephemeris"
$forbidden_global_integration = "NatalResult|FastAPI|SQLAlchemy"
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
$public_symbols = "PlanetVisibilityThresholds|calculate_planet_visibility_condition|calculate_planet_visibility_conditions|CONJUNCT_SOLAR"
rg -n $forbidden_deps $p
rg -n "\\bscore\\b|score_delta|accidental_score_delta|essential_score_delta|strength_modifier" $p
rg -n "interpretation|meaning|description|narrative|prompt" $p
rg -n $forbidden_observation $p
rg -n $forbidden_global_integration $p
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
- heliacal reel / observationnel / integration: zero hits;
- symbols publics: hits limites aux nouveaux modules, exports et tests;
- symbols publics dans les surfaces adjacentes: zero hits;
- diff des surfaces adjacentes: vide.

Story validation commands:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-213-planetary-visibility-conditions-calculator/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Skipped-command rule:

- Any skipped command must be recorded in the final evidence with exact
  command, reason, risk and fallback evidence.

## 22. Regression Risks

- Risk: le calculateur de visibilite recalcule la proximite solaire ou la
  relation oriental/occidental.
  - Guardrail: AC12, reuse constraints, `RG-136` et `RG-138`.
- Risk: le cazimi est classe invisible par assimilation a la combustion.
  - Guardrail: AC6 impose `CONJUNCT_SOLAR` visible.
- Risk: l'emergence est appliquee aux planetes occidentales.
  - Guardrail: AC9 et AC10.
- Risk: les placeholders heliacaux deviennent une astronomie observationnelle
  non demandee.
  - Guardrail: AC15, AC19 et non-goals.
- Risk: une integration opportuniste modifie le JSON public ou `NatalResult`.
  - Guardrail: AC20 et diff des surfaces adjacentes obligatoire.

## 23. Dev Agent Instructions

- Implement only CS-213.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass constraints through wrapper, alias, fallback, re-export,
  broad allowlist, unresolved marker or hidden residual work.
- Keep the calculator pure and deterministic.
- Trust `SolarProximityCondition` and `PlanetarySolarPhaseRelation`; do not
  recalculate their facts.
- Do not integrate into `NatalResult`.
- Do not change JSON public output.
- Do not change frontend.
- Do not change DB, migrations or seeds.
- Do not add scoring, interpretation, prompts, LLM, API schemas, Pydantic
  models, heliacal rising/setting reel, horizon, altitude, weather, magnitude,
  latitude, topocentric or ephemeris logic.
- Use French top-of-file comments/docstrings for new applicative files.
- Run every Python command after activating `.venv`.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  unresolved task marker or hidden residual in-domain work.

## 24. References

- `backend/app/domain/astrology/planetary_conditions/contracts.py` - contrats
  CS-208 reutilises et ajustes minimalement.
- `backend/app/domain/astrology/planetary_conditions/__init__.py` - exports
  publics du package.
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  - source amont de proximite solaire.
- `backend/app/domain/astrology/planetary_conditions/solar_phase_relation_calculator.py`
  - source amont de relation oriental/occidental.
- `backend/app/domain/astrology/planetary_conditions/moon_phase_calculator.py`
  - precedent local recent de calculateur pur.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - tests de contrats a maintenir et etendre.
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
  - source contractuelle.
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
  - precedent proximite solaire.
- `_condamad/stories/CS-211-solar-phase-relation-calculator/00-story.md`
  - precedent relation solaire.
- `_condamad/stories/CS-212-moon-phase-calculator/00-story.md`
  - precedent et follow-up explicite CS-213.
- `_condamad/stories/regression-guardrails.md` - invariants applicables
  `RG-107`, `RG-119`, `RG-122`, `RG-128`, `RG-129`, `RG-135`, `RG-136`,
  `RG-138`, `RG-139` et nouvel invariant `RG-140`.
