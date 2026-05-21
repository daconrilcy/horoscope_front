# Story CS-209 solar-proximity-conditions-calculator: Calculer les conditions de proximite solaire

Status: ready-to-dev

## 1. Objective

Creer un calculateur domaine pur qui determine, pour chaque planete, la
condition de proximite solaire `cazimi`, `combust`, `under_beams` ou `none`
(`free of beams` dans le vocabulaire du brief) a partir des contrats CS-208. Le
calculateur doit rester deterministe, configurable par seuils, sans scoring,
interpretation, API, persistance, projection publique ou integration dans
`NatalResult`.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-21 pour `CS-209 - Solar
  Proximity Conditions Calculator`.
- Reason for change: CS-208 a cree `SolarProximityCondition`,
  `SolarProximityConditionKey` et `ConditionSeverity`, mais aucun calculateur ne
  produit encore l'etat solaire reel d'une planete.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story reprend le brief comme un calculateur
  mono-domaine. Les AC couvrent creation du module, seuils configurables,
  priorite stricte, distance angulaire minimale, normalisation, bornes
  inclusives, traitement du Soleil, absence de scoring/interpretation,
  fonction de lot et validations. Les exclusions du brief restent explicitement
  hors scope.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/planetary_conditions`
- In scope:
  - creer `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`;
  - ajouter `SolarProximityThresholds` dans `contracts.py`;
  - exporter le calculateur et les seuils depuis
    `planetary_conditions/__init__.py`;
  - calculer une seule condition solaire par planete selon la priorite
    `CAZIMI > COMBUST > UNDER_BEAMS > NONE`;
  - normaliser les longitudes dans `[0, 360)`;
  - calculer la distance angulaire minimale, y compris aux passages `358/2` et
    `1/359`;
  - retourner `NONE` inactif pour `planet_key="sun"`;
  - ajouter les tests unitaires cibles du calculateur;
  - ajouter un commentaire global en francais et des docstrings francaises dans
    les fichiers applicatifs nouveaux ou modifies.
- Out of scope:
  - scoring de dignite accidentelle, essentielle, dominance ou force;
  - interpretation textuelle, narration, signification ou prompt;
  - visibilite planetaire avancee, heliacal rising/setting, oriental/occidental;
  - vitesse planetaire, retrogradation, stationnarite, phase lunaire;
  - DB, migrations, seeders, SQLAlchemy, API, FastAPI, Pydantic;
  - integration dans `NatalResult`, JSON public, frontend ou services chart.
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
  contrat de seuils; elle ne correspond pas aux archetypes API, suppression,
  migration, route, namespace ou service boundary.
- Additional validation rules:
  - `solar_proximity_calculator.py` doit importer uniquement la bibliotheque
    standard et `app.domain.astrology.planetary_conditions.contracts`;
  - les conditions doivent etre mutuellement exclusives par branchement de
    priorite strict;
  - `NONE` represente explicitement l'etat `free of beams` du brief dans les
    contrats CS-208;
  - `SolarProximityThresholds` doit valider `0 <= cazimi <= combust <= under_beams`;
  - `score`, `score_delta`, `accidental_score_delta`,
    `essential_score_delta`, `strength_modifier`, `interpretation`, `meaning`,
    `description` et `narrative` sont interdits dans le calculateur;
  - les garde-fous `RG-135` et `RG-136` doivent rester alignes: `RG-135`
    protege `contracts.py` comme module contractuel, et `RG-136` protege le
    calculateur solaire pur.
- Behavior change allowed: constrained
- Behavior change constraints:
  - nouveau comportement autorise uniquement via les nouvelles fonctions domaine
    de proximite solaire;
  - aucun comportement existant, endpoint, schema public, payload JSON, seed,
    migration, score ou frontend ne change.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: un contrat CS-208 existant rend impossible
  l'ajout de `SolarProximityThresholds` sans casser les tests de contrats; le
  dev agent doit bloquer au lieu de creer un second contrat concurrent.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les fonctions publiques importables et leurs tests comportementaux prouvent la verite runtime du calcul. |
| Baseline Snapshot | yes | Il faut capturer l'etat CS-208 et l'etat explicite des guardrails `RG-135`/`RG-136`. |
| Ownership Routing | yes | Le calcul pur doit rester dans le domaine et ne pas migrer vers API, services, infra ou projections. |
| Allowlist Exception | yes | Les exceptions autorisees doivent rester un registre vide et testable: aucun fallback, alias, shim ou compatibilite n'est autorise. |
| Contract Shape | yes | `SolarProximityThresholds` et les fonctions publiques ont une forme attendue. |
| Batch Migration | no | Aucun consommateur existant n'est migre. |
| Reintroduction Guard | yes | Les scans doivent bloquer scoring, interpretation et dependances interdites. |
| Persistent Evidence | yes | La validation et les scans doivent etre conserves dans l'artefact de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `calculate_solar_proximity_condition`;
  - `calculate_solar_proximity_conditions`;
  - les objets `SolarProximityCondition` retournes par les tests unitaires;
  - AST guard implicite par tests et scans bornes sur les imports du module
    calculateur.
- Runtime artifact:
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`.
  - AST guard evidence:

```powershell
rg -n $forbidden_imports $p
```

  - `$forbidden_imports` and `$p` are defined with exact values in the
    Validation Plan.
- Secondary evidence:
  - scans des imports interdits et symboles interdits;
  - `ruff check .`;
  - `pytest -q`.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas la priorite des seuils, les bornes inclusives, la
    normalisation des longitudes ou le traitement du Soleil.
- Forbidden sources:
  - API, services, infra, DB, frontend, JSON builder, scoring et interpretation.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/planetary_conditions/contracts.py`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136"`;
  - `Test-Path backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`.
- Comparison after implementation:
  - `Test-Path backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`;
  - `rg -n $public_symbols $planetary_condition_paths`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136"`.
- Expected invariant:
  - seuls `planetary_conditions`, ses tests, ses exports et les artefacts de
    story changent;
  - `RG-135` reste borne a `contracts.py` et `RG-136` protege le calculateur
    pur;
  - aucune integration adjacente n'est introduite.
- Allowed differences:
  - nouveau calculateur solaire;
  - ajout `SolarProximityThresholds`;
  - export public explicite;
  - tests unitaires cibles;
  - evidence de validation et verification du garde-fou `RG-136`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrat de seuils solaires | `planetary_conditions/contracts.py` | calculateur local duplique, API schema, service |
| Calcul pur de proximite solaire | `planetary_conditions/solar_proximity_calculator.py` | `advanced_conditions`, `dignities`, `services/chart`, frontend |
| Exports publics du package | `planetary_conditions/__init__.py` | re-export legacy ou alias de compatibilite |
| Tests du calculateur | `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py` | tests API, DB, frontend ou integration chart |
| Integration `NatalResult` | out of scope for CS-209 | `natal_calculation.py`, `json_builder.py` |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | No exception is authorized for CS-209. | Permanent zero-exception policy. |

Validation rule:

- Any required exception must block implementation and require a user decision;
  no wildcard or folder-wide exception may be added.

## 4f. Contract Shape

- Contract type:
  - dataclass domaine immuable `SolarProximityThresholds`;
  - fonctions pures importables.
- Fields:
  - `SolarProximityThresholds.cazimi_max_distance_deg`;
  - `SolarProximityThresholds.combust_max_distance_deg`;
  - `SolarProximityThresholds.under_beams_max_distance_deg`.
- Required fields:
  - `cazimi_max_distance_deg: float = 17.0 / 60.0`;
  - `combust_max_distance_deg: float = 8.5`;
  - `under_beams_max_distance_deg: float = 15.0`.
- Default value note:
  - `17.0 / 60.0` est le choix d'implementation recommande pour representer
    `0.2833333333` (`0 deg 17'`) sans dupliquer une constante arrondie.
- Optional fields:
  - `thresholds: SolarProximityThresholds | None = None` sur les fonctions
    publiques.
- Status codes:
  - no HTTP endpoint, method or status code is modified.
- Serialization names:
  - no public JSON serialization is added in CS-209.
- Frontend type impact:
  - no frontend type change.
- Generated contract impact:
  - no OpenAPI, generated client, generated schema or public API contract
    change.
- Public function shape:

```python
calculate_solar_proximity_condition(
    *,
    planet_key: str,
    planet_longitude_deg: float,
    sun_longitude_deg: float,
    thresholds: SolarProximityThresholds | None = None,
) -> SolarProximityCondition
```

```python
calculate_solar_proximity_conditions(
    *,
    planet_longitudes_deg: Mapping[str, float],
    sun_longitude_deg: float,
    thresholds: SolarProximityThresholds | None = None,
) -> Mapping[str, SolarProximityCondition]
```

  - la fonction de lot doit etre implementee et testee.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-209 ne migre aucun consommateur et ne remplace aucun module
  existant.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans et statut `RG-135`/`RG-136`. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher que le calculateur solaire pur devienne une couche de scoring,
    interpretation, API, persistence, projection ou second moteur astrologique
    adjacent.
- Forbidden examples in `solar_proximity_calculator.py`:
  - `score`
  - `score_delta`
  - `accidental_score_delta`
  - `essential_score_delta`
  - `strength_modifier`
  - `interpretation`
  - `meaning`
  - `description`
  - `narrative`
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
  - diff adjacent vide hors surfaces explicitement autorisees.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/stories/story-status.md` - `CS-209` est enregistree
  avec le statut `ready-to-dev` et le chemin canonique de cette story.
- Evidence 2: `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
  - la section `Follow-up Story` annonce `CS-209 - Solar Proximity Conditions
  Calculator`.
- Evidence 3: `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `SolarProximityCondition`, `SolarProximityConditionKey` et
  `ConditionSeverity` existent deja, mais `SolarProximityThresholds` est absent.
- Evidence 4: `backend/app/domain/astrology/planetary_conditions/__init__.py`
  - les exports publics existent pour les contrats CS-208.
- Evidence 5: `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - les tests de contrats purs existent et doivent rester valides.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - `RG-135` protege
  `contracts.py` comme module contractuel pur et `RG-136` protege le
  calculateur solaire pur sans ouvrir les autres calculateurs.

Assumptions to verify during implementation:

- aucune fonction canonique de distance angulaire minimale n'existe deja dans
  `planetary_conditions`; le calculateur peut creer une fonction privee locale.
- la fonction de lot fait partie de CS-209 et doit etre testee et exportee.

## 6. Target State

After implementation:

- `solar_proximity_calculator.py` existe et reste pur;
- `SolarProximityThresholds` est disponible, immuable et valide ses bornes;
- `calculate_solar_proximity_condition` retourne toujours un
  `SolarProximityCondition`;
- le Soleil retourne `NONE` inactif sans exception;
- les longitudes sont normalisees et la distance minimale traverse `0/360`;
- les seuils exacts sont inclusifs;
- aucune integration, scoring, interpretation, DB, API ou frontend n'est ajoute;
- les tests unitaires et scans anti-drift passent dans le venv.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-107` - les faits astrologiques doivent traverser les frontieres sous
    contrats types, pas en dictionnaires libres.
  - `RG-119` - les profils conditionnels ne doivent pas devenir un second moteur
    astrologique ou une source de scoring local.
  - `RG-122` - le moteur avance existant ne doit pas etre modifie par ce
    calculateur solaire pur.
  - `RG-128` - `json_builder.py` reste une projection stricte et ne doit pas
    calculer la proximite solaire.
  - `RG-129` - le frontend reste display-only et hors scope.
  - `RG-135` - les contrats `contracts.py` restent immutables, sans scoring,
    interpretation ni dependance interdite; CS-209 doit verifier que le
    registre ne confond plus le contrat et le calculateur.
- New durable invariant:
  - verifier la presence de `RG-136` pour proteger
    `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
    comme calculateur solaire pur, sans scoring, interpretation, API, DB,
    services, frontend ou integration `NatalResult`.
- Non-applicable invariants:
  - guardrails de routes API, migrations DB, prompts LLM et CSS frontend; la
    story ne touche pas ces surfaces.
- Required regression evidence:
  - tests unitaires du calculateur;
  - tests de contrats CS-208 maintenus;
  - scans imports interdits, scoring, interpretation;
  - diff adjacent obligatoire;
  - `ruff format .`, `ruff check .`, `pytest -q`.
- Allowed differences:
  - nouveau calculateur;
  - ajout de seuils contractuels;
  - export public;
  - nouveau test unitaire;
  - verification ou mise a jour de `RG-135`/`RG-136` si le registre derive.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La fonction principale est disponible dans le fichier calculateur. | Evidence: `Test-Path $p`, import test, `pytest -q $t`. |
| AC2 | `SolarProximityThresholds` expose les trois seuils par defaut du brief. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC3 | La priorite `CAZIMI > COMBUST > UNDER_BEAMS > NONE` retourne une seule condition. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC4 | La distance minimale gere les passages autour de zero du brief. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC5 | La normalisation des longitudes suit les exemples du brief. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC6 | Les bornes `0.2833333333`, `8.5`, `15.0` sont inclusives; `15.0001` retourne `NONE`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC7 | `planet_key="sun"` retourne la condition inactive attendue. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC8 | Le mapping est `CAZIMI=EXTREME`, `COMBUST=MAJOR`, `UNDER_BEAMS=MODERATE`, `NONE=NONE`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC9 | Les seuils personnalises modifient le classement sans changer les contrats. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC10 | La fonction de lot retourne un mapping pur incluant le Soleil. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC11 | Le calculateur exclut les interdits du brief. | Evidence: AST guard `rg -n $forbidden_imports $p` plus scans P2-P4. |
| AC12 | Aucune integration adjacente n'est ajoutee hors package. | Evidence: AST guard `rg -n $public_symbols $adjacent_roots` zero-hit. |
| AC13 | La qualite backend passe dans le venv. | Evidence profile: `deterministic_test`; `ruff format .`, `ruff check .`, `pytest -q`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer la baseline et confirmer l'ownership (AC: AC1, AC2, AC11, AC12)
  - [ ] Subtask 1.1 - Inspecter `contracts.py`, `__init__.py`,
    `test_contracts.py`, CS-208 et `regression-guardrails.md`.
  - [ ] Subtask 1.2 - Verifier l'absence preexistante de
    `solar_proximity_calculator.py`.
  - [ ] Subtask 1.3 - Documenter dans l'evidence l'etat attendu de `RG-135` et
    `RG-136`.

- [ ] Task 2 - Ajouter les seuils contractuels (AC: AC2, AC9, AC11)
  - [ ] Subtask 2.1 - Ajouter `SolarProximityThresholds` dans `contracts.py`.
  - [ ] Subtask 2.2 - Utiliser `dataclass(frozen=True, slots=True)`.
  - [ ] Subtask 2.3 - Ajouter une validation simple de l'ordre des seuils.
  - [ ] Subtask 2.4 - Exporter le contrat depuis `__init__.py`.

- [ ] Task 3 - Creer le calculateur solaire pur (AC: AC1, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11)
  - [ ] Subtask 3.1 - Creer `solar_proximity_calculator.py`.
  - [ ] Subtask 3.2 - Ajouter `_normalize_longitude_deg` et
    `_angular_distance_deg` comme fonctions privees locales.
  - [ ] Subtask 3.3 - Implementer `calculate_solar_proximity_condition`.
  - [ ] Subtask 3.4 - Implementer la fonction de lot pure.
  - [ ] Subtask 3.5 - Exporter les fonctions publiques depuis `__init__.py`.

- [ ] Task 4 - Ajouter les tests unitaires (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10)
  - [ ] Subtask 4.1 - Creer
    `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`.
  - [ ] Subtask 4.2 - Tester cazimi, combust, under beams et none.
  - [ ] Subtask 4.3 - Tester priorite, bornes exactes, passages `358/2` et
    `1/359`, normalisation, Soleil et seuils personnalises.
  - [ ] Subtask 4.4 - Tester la fonction de lot.
  - [ ] Subtask 4.5 - Maintenir les tests CS-208 de contrats.

- [ ] Task 5 - Ajouter et prouver les gardes anti-drift (AC: AC11, AC12)
  - [ ] Subtask 5.1 - Verifier que `RG-135` protege les contrats purs de
    `contracts.py`.
  - [ ] Subtask 5.2 - Verifier ou mettre a jour `RG-136` pour le calculateur
    solaire pur.
  - [ ] Subtask 5.3 - Executer les scans imports interdits, scoring,
    interpretation et surfaces adjacentes.

- [ ] Task 6 - Valider la story (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13)
  - [ ] Subtask 6.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 6.2 - Executer le test cible.
  - [ ] Subtask 6.3 - Executer `ruff format .`, `ruff check .` et `pytest -q`.
  - [ ] Subtask 6.4 - Documenter les resultats dans
    `evidence/validation.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `SolarProximityCondition`, `SolarProximityConditionKey` et
    `ConditionSeverity` depuis `contracts.py`;
  - conventions `dataclass(frozen=True, slots=True)` existantes;
  - tests pytest sous `backend/tests/unit/domain/astrology/planetary_conditions`.
- Do not recreate:
  - contrats CS-208 sous un autre nom ou dans un autre package;
  - calculateurs `advanced_conditions`;
  - scoring de dignites, dominance, profils ou signaux;
  - schemas API/Pydantic pour les memes concepts;
  - utilitaire global d'angles pour cette story.
- Shared abstraction allowed only if:
  - une fonction pure canonique de distance angulaire existe deja dans le
    domaine astrologique et son import ne viole pas l'ownership.

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

Specific forbidden symbols / paths:

- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  importing `app.api`
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  importing `app.infra`
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  importing `app.infrastructure`
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
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
| Seuils de proximite solaire | `planetary_conditions/contracts.py` | calculateur local duplique, settings, DB |
| Calcul cazimi/combust/under beams/none | `planetary_conditions/solar_proximity_calculator.py` | `advanced_conditions`, `dignities`, `json_builder.py`, frontend |
| Exports publics | `planetary_conditions/__init__.py` | alias ou re-export legacy |
| Integration future | future story | CS-209 ne modifie pas `NatalResult` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Artifact Check

- Generated artifact check: not applicable
- Reason: no generated file, generated schema, generated client or generated
  documentation is affected by CS-209.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, frontend
  type or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/astrology/advanced_conditions/contracts.py` only for
  style comparison, not modification.

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/planetary_conditions/contracts.py` - ajouter
  `SolarProximityThresholds`.
- `backend/app/domain/astrology/planetary_conditions/__init__.py` - exporter
  seuils et fonctions publiques.
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
  - nouveau calculateur pur.
- `_condamad/stories/regression-guardrails.md` - verifier ou mettre a jour
  `RG-135` et `RG-136` si le registre derive.
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/evidence/validation.md`
  - preuves de validation.

Likely tests:

- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
  - couverture comportementale du calculateur.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - couverture du nouveau contrat de seuils.

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

- Next planned story: `CS-210 - Planetary Motion Conditions Calculator`
- Expected scope: calculer direction directe/retrograde, vitesse lente,
  normale ou rapide et stationnarite a partir de seuils par planete.
- Boundary: CS-209 ne cree aucun calculateur de mouvement planetaire et ne
  prepare pas d'integration opportuniste pour CS-210.

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
$t = "backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py"
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
$p = "backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py"
rg -n "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services" $p
rg -n "sqlalchemy|fastapi|pydantic|OpenAI|AIEngineAdapter" $p
rg -n "\\bscore\\b|score_delta|accidental_score_delta|essential_score_delta|strength_modifier" $p
rg -n "interpretation|meaning|description|narrative|prompt" $p
rg -n "SolarProximityThresholds|calculate_solar_proximity_condition" backend/app/domain/astrology/planetary_conditions backend/tests/unit/domain/astrology/planetary_conditions
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
- symbols publics: hits limites au nouveau module, exports et tests;
- diff adjacent: vide.

Story validation commands:

```powershell
$story = "_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Skipped-command rule:

- Any skipped command must be recorded in the final evidence with exact
  command, reason, risk and fallback evidence.

## 22. Regression Risks

- Risk: le calculateur solaire devient une source de scoring avant la story
  dediee.
  - Guardrail: AC11, scans scoring et `RG-136`.
- Risk: une integration opportuniste modifie le JSON public ou `NatalResult`.
  - Guardrail: AC12 et diff adjacent obligatoire.
- Risk: les seuils sont dupliques localement dans le calculateur.
  - Guardrail: AC2, DRY constraints et export `SolarProximityThresholds`.
- Risk: `RG-135` ou `RG-136` derive et bloque le follow-up CS-209.
  - Guardrail: AC12 et evidence explicite de verification `RG-135`/`RG-136`.
- Risk: le calculateur se trompe aux bornes ou au passage `0/360`.
  - Guardrail: AC4, AC5 et AC6.

## 23. Dev Agent Instructions

- Implement only CS-209.
- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass constraints through wrapper, alias, fallback, re-export,
  broad allowlist, TODO or hidden residual work.
- Keep the calculator pure and deterministic.
- Do not integrate into `NatalResult`.
- Do not change JSON public output.
- Do not change frontend.
- Do not change DB, migrations or seeds.
- Do not add scoring, interpretation, prompts, LLM, API schemas or Pydantic
  models.
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
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - tests de contrats a maintenir.
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
  - source contractuelle et follow-up explicite CS-209.
- `_condamad/stories/regression-guardrails.md` - invariants applicables
  `RG-107`, `RG-119`, `RG-122`, `RG-128`, `RG-129`, `RG-135` et `RG-136`.
