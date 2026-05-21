# Story CS-210 planetary-motion-conditions-calculator: Calculer les conditions de mouvement planetaire

Status: ready-to-dev

## 1. Objective

Creer un calculateur domaine pur qui determine, pour chaque planete, la
direction apparente, la retrogradation, la stationnarite, le ratio de vitesse
normalise et l'etat de vitesse relatif a partir des contrats CS-208 et d'un
profil planetaire configurable. Le calculateur doit rester deterministe, sans
IO, sans scoring, sans interpretation, sans API, sans DB, sans projection
publique et sans integration `NatalResult`.

## 2. Trigger / Source

- Source type: brief
- Source reference: brief utilisateur du 2026-05-21 pour `CS-210 - Planetary
  Motion Conditions Calculator`.
- Reason for change: CS-208 expose `PlanetaryMotionCondition`,
  `PlanetaryMotionDirection` et `PlanetarySpeedState`, mais aucun calculateur
  pur ne produit encore ces conditions dynamiques a partir d'une vitesse
  instantanee et de seuils configurables.
- Selected story writer mode: Repo-informed story.
- Source-alignment review: la story reprend le brief comme un calculateur
  mono-domaine. Les AC couvrent direction, priorite stationnaire, ratio, etats
  de vitesse, mean speed invalide, profils configurables, catalogue par defaut,
  profil manquant dans la fonction de lot, absence de scoring/interpretation et
  validations. Les exclusions du brief restent hors scope.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/planetary_conditions`
- In scope:
  - creer `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`;
  - ajouter `PlanetaryMotionProfile` dans `contracts.py`;
  - creer `backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py`
    pour le catalogue runtime minimal `DEFAULT_PLANETARY_MOTION_PROFILES`;
  - exporter le profil, le catalogue et les fonctions publiques depuis
    `planetary_conditions/__init__.py`;
  - calculer `DIRECT`, `RETROGRADE` ou `STATIONARY` avec priorite stricte a la
    stationnarite; `UNKNOWN` reste reserve au contrat CS-208 et ne doit pas
    etre produit quand une vitesse numerique et un profil sont fournis;
  - calculer `VERY_SLOW`, `SLOW`, `NORMAL`, `FAST`, `VERY_FAST` ou `UNKNOWN`
    depuis `abs(speed) / mean_speed`;
  - implementer la fonction de lot avec erreur explicite si un profil manque;
  - ajouter les tests unitaires cibles du calculateur;
  - ajouter un commentaire global en francais et des docstrings francaises dans
    les fichiers applicatifs nouveaux ou modifies.
- Out of scope:
  - scoring de dignite accidentelle, essentielle, dominance ou force;
  - interpretation textuelle, narration, signification, prompt ou LLM;
  - proximite solaire, combustion, cazimi, under beams;
  - relation oriental/occidental, phases solaires, phases lunaires, visibilite;
  - calcul astronomique des vitesses, ephemerides ou derivees temporelles;
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
- Archetype reason: la story cree un calculateur domaine pur, un contrat de
  profil et un petit catalogue runtime; elle ne correspond pas aux archetypes
  API, suppression, migration, route, namespace ou service boundary.
- Additional validation rules:
  - `planetary_motion_calculator.py` doit importer uniquement la bibliotheque
    standard, `contracts.py` et le catalogue de profils du meme package;
  - `PlanetaryMotionProfile` doit etre une dataclass immuable et slotted;
  - le calcul de direction doit appliquer `STATIONARY` avant direct/retrograde;
  - `normalized_speed_ratio` doit etre `None` si le mean speed est nul ou negatif;
  - la fonction de lot doit lever `ValueError` si `profiles_by_planet` ne
    contient pas la cle requise;
  - `score`, `score_delta`, `strength_modifier`, `interpretation`, `meaning`,
    `description`, `narrative`, `prompt`, `OpenAI` et `AIEngineAdapter` sont
    interdits dans le calculateur et le catalogue.
- Behavior change allowed: constrained
- Behavior change constraints:
  - nouveau comportement autorise uniquement via les nouvelles fonctions
    domaine de mouvement planetaire;
  - aucun comportement existant, endpoint, schema public, payload JSON, seed,
    migration, score ou frontend ne change.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: un contrat CS-208 existant rend impossible
  l'ajout de `PlanetaryMotionProfile` sans casser les tests de contrats; le dev
  agent doit bloquer au lieu de creer un second contrat concurrent.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les fonctions publiques importables et leurs tests comportementaux prouvent la verite runtime du calcul. |
| Baseline Snapshot | yes | Il faut capturer l'etat CS-208/CS-209 et l'etat explicite des guardrails `RG-135`, `RG-136` et `RG-137`. |
| Ownership Routing | yes | Le calcul pur doit rester dans le domaine et ne pas migrer vers API, services, infra ou projections. |
| Allowlist Exception | yes | Les exceptions autorisees doivent rester un registre vide et testable: aucun fallback, alias, shim ou compatibilite n'est autorise. |
| Contract Shape | yes | `PlanetaryMotionProfile`, le catalogue et les fonctions publiques ont une forme attendue. |
| Batch Migration | no | Aucun consommateur existant n'est migre. |
| Reintroduction Guard | yes | Les scans doivent bloquer scoring, interpretation, dependances interdites et integration adjacente. |
| Persistent Evidence | yes | La validation et les scans doivent etre conserves dans l'artefact de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - `calculate_planetary_motion_condition`;
  - `calculate_planetary_motion_conditions`;
  - `PlanetaryMotionProfile`;
  - `DEFAULT_PLANETARY_MOTION_PROFILES`;
  - les objets `PlanetaryMotionCondition` retournes par les tests unitaires.
- Runtime artifacts:
  - `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py`.
  - AST guard / scan statique des imports bornes et des symboles interdits:

```powershell
rg -n $forbidden_imports $p
```

  - `$forbidden_imports` et `$p` sont definis avec leurs valeurs exactes dans
    le Validation Plan.
- Secondary evidence:
  - scans des imports interdits et symboles interdits;
  - tests de contrats CS-208 maintenus;
  - `ruff check .`;
  - `pytest -q`.
- Static scans alone are not sufficient because:
  - ils ne prouvent pas la priorite stationnaire, le ratio, les bornes
    strictes/inclusives des seuils ou les erreurs de profils manquants.
- Forbidden sources:
  - API, services, infra, DB, frontend, JSON builder, scoring et interpretation.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `Get-Content backend/app/domain/astrology/planetary_conditions/contracts.py`;
  - `Test-Path backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`;
  - `Test-Path backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137"`.
- Comparison after implementation:
  - `Test-Path backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`;
  - `Test-Path backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py`;
  - `rg -n $public_symbols $planetary_condition_paths`;
  - `Get-Content _condamad/stories/regression-guardrails.md | Select-String "RG-135|RG-136|RG-137"`.
- Expected invariant:
  - seuls `planetary_conditions`, ses tests, ses exports et les artefacts de
    story changent;
  - `RG-135` reste borne aux contrats, `RG-136` protege le calculateur solaire
    et `RG-137` protege le calculateur de mouvement;
  - aucune integration adjacente n'est introduite.
- Allowed differences:
  - nouveau calculateur de mouvement;
  - nouveau profil contractuel;
  - nouveau catalogue de profils;
  - export public explicite;
  - nouveau test unitaire;
  - evidence de validation et verification du garde-fou `RG-137`.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Contrat de profil de mouvement | `planetary_conditions/contracts.py` | calculateur local duplique, settings, DB, API schema |
| Profils de mouvement par defaut | `planetary_conditions/planetary_motion_profiles.py` | settings, seeders, migrations, frontend |
| Calcul pur direction/vitesse | `planetary_conditions/planetary_motion_calculator.py` | `advanced_conditions`, `dignities`, `services/chart`, frontend |
| Exports publics du package | `planetary_conditions/__init__.py` | re-export legacy ou alias de compatibilite |
| Tests du calculateur | `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py` | tests API, DB, frontend ou integration chart |
| Integration `NatalResult` | out of scope for CS-210 | `natal_calculation.py`, `json_builder.py` |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception n'est autorisee pour CS-210. | Politique permanente sans exception. |

Validation rule:

- Any required exception must block implementation and require a user decision;
  no wildcard or folder-wide exception may be added.

## 4f. Contract Shape

- Contract type:
  - dataclass domaine immuable `PlanetaryMotionProfile`;
  - mapping runtime expose sous forme non mutable
    `DEFAULT_PLANETARY_MOTION_PROFILES`;
  - fonctions pures importables.
- Fields:
  - `PlanetaryMotionProfile.planet_key`;
  - `PlanetaryMotionProfile.mean_speed_deg_per_day`;
  - `PlanetaryMotionProfile.stationary_threshold_abs`;
  - `PlanetaryMotionProfile.very_slow_ratio_threshold`;
  - `PlanetaryMotionProfile.slow_ratio_threshold`;
  - `PlanetaryMotionProfile.fast_ratio_threshold`;
  - `PlanetaryMotionProfile.very_fast_ratio_threshold`.
- Required fields:
  - `planet_key: str`;
  - `mean_speed_deg_per_day: float`;
  - `stationary_threshold_abs: float`;
  - `very_slow_ratio_threshold: float = 0.4`;
  - `slow_ratio_threshold: float = 0.8`;
  - `fast_ratio_threshold: float = 1.2`;
  - `very_fast_ratio_threshold: float = 1.6`.
- Optional fields:
  - none on `PlanetaryMotionProfile`.
- Validation rules:
  - ratio thresholds must satisfy
    `0 <= very_slow <= slow <= fast <= very_fast`;
  - `stationary_threshold_abs` must be zero or positive;
  - a zero or negative `mean_speed_deg_per_day` is allowed so the calculator can return
    `UNKNOWN` speed state while still calculating direction.
- Speed state thresholds:
  - `ratio < very_slow_ratio_threshold` retourne `VERY_SLOW`;
  - `very_slow_ratio_threshold <= ratio < slow_ratio_threshold` retourne
    `SLOW`;
  - `slow_ratio_threshold <= ratio <= fast_ratio_threshold` retourne `NORMAL`;
  - `fast_ratio_threshold < ratio <= very_fast_ratio_threshold` retourne
    `FAST`;
  - `ratio > very_fast_ratio_threshold` retourne `VERY_FAST`.
- Default mean speeds:
  - `moon: 13.176`;
  - `mercury: 1.2`;
  - `venus: 1.18`;
  - `sun: 0.9856`;
  - `mars: 0.524`;
  - `jupiter: 0.083`;
  - `saturn: 0.033`;
  - `uranus: 0.0117`;
  - `neptune: 0.006`;
  - `pluto: 0.004`.
- Status codes:
  - no HTTP endpoint, method or status code is modified.
- Serialization names:
  - no public JSON serialization is added in CS-210.
- Frontend type impact:
  - no frontend type change.
- Generated contract impact:
  - no OpenAPI, generated client, generated schema or public API contract
    change.
- Public function shape:

```python
calculate_planetary_motion_condition(
    *,
    planet_key: str,
    speed_deg_per_day: float,
    profile: PlanetaryMotionProfile,
) -> PlanetaryMotionCondition
```

```python
calculate_planetary_motion_conditions(
    *,
    speeds_by_planet: Mapping[str, float],
    profiles_by_planet: Mapping[str, PlanetaryMotionProfile],
) -> Mapping[str, PlanetaryMotionCondition]
```

  - la fonction de lot doit etre implementee et testee.

## 4g. Batch Migration Plan

- Batch migration: not applicable
- Reason: CS-210 ne migre aucun consommateur et ne remplace aucun module
  existant.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation | `evidence/validation.md` | Baseline, tests, scans et statut `RG-135`/`RG-136`/`RG-137`. |

## 4i. Reintroduction Guard

- Guard target:
  - empecher que le calculateur de mouvement pur devienne une couche de scoring,
    interpretation, API, persistence, projection ou second moteur astrologique
    adjacent.
- Forbidden examples in `planetary_motion_calculator.py` and
  `planetary_motion_profiles.py`:
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
  - diff des surfaces adjacentes vide hors surfaces explicitement autorisees.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/stories/story-status.md` - `CS-209` est la derniere
  story numerotee avant cette creation et elle est enregistree comme `done`.
- Evidence 2: `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
  - la section `Follow-up Story` annonce `CS-210 - Planetary Motion Conditions
  Calculator`.
- Evidence 3: `backend/app/domain/astrology/planetary_conditions/contracts.py`
  - `PlanetaryMotionCondition`, `PlanetaryMotionDirection` et
  `PlanetarySpeedState` existent; `PlanetaryMotionProfile` est absent.
- Evidence 4: `backend/app/domain/astrology/planetary_conditions/__init__.py`
  - les exports publics existent pour les contrats CS-208 et le calculateur
  solaire CS-209.
- Evidence 5: `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - les tests de contrats purs existent et doivent etre etendus pour le profil.
- Evidence 6: `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
  - precedent de calculateur pur dans le meme package et meme style de tests.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - `RG-135` protege
  `contracts.py`, `RG-136` protege le calculateur solaire pur, et cette story
  ajoute `RG-137` pour le calculateur de mouvement pur.

Assumptions to verify during implementation:

- aucun calculateur canonique de mouvement planetaire n'existe deja dans
  `planetary_conditions`;
- les valeurs de profils par defaut sont des references de classification
  suffisantes pour tests et runtime minimal, pas des ephemerides astronomiques.

## 6. Target State

After implementation:

- `planetary_motion_calculator.py` existe et reste pur;
- `PlanetaryMotionProfile` est disponible, immuable et valide ses seuils;
- `DEFAULT_PLANETARY_MOTION_PROFILES` expose les profils `moon`, `mercury`,
  `venus`, `sun`, `mars`, `jupiter`, `saturn`, `uranus`, `neptune`, `pluto`;
- les profils par defaut utilisent les vitesses moyennes recommandees du brief
  et `stationary_threshold_abs = mean_speed_deg_per_day * 0.05`;
- `calculate_planetary_motion_condition` retourne toujours un
  `PlanetaryMotionCondition` quand un profil est fourni;
- `STATIONARY` prime toujours sur direct/retrograde;
- `normalized_speed_ratio` vaut `abs(speed) / mean_speed` ou `None` si le mean
  speed est invalide;
- la fonction de lot leve `ValueError` pour un profil manquant;
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
    calculateur de mouvement pur.
  - `RG-128` - `json_builder.py` reste une projection stricte et ne doit pas
    calculer le mouvement planetaire.
  - `RG-129` - le frontend reste display-only et hors scope.
  - `RG-135` - les contrats `contracts.py` restent immutables, sans scoring,
    interpretation ni dependance interdite.
  - `RG-136` - le calculateur solaire reste borne a la proximite solaire et ne
    doit pas absorber le calcul de mouvement.
- New durable invariant:
  - verifier la presence de `RG-137` pour proteger
    `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
    et `planetary_motion_profiles.py` comme surfaces pures, sans scoring,
    interpretation, API, DB, services, frontend ou integration `NatalResult`.
- Non-applicable invariants:
  - guardrails de routes API, migrations DB, prompts LLM et CSS frontend; la
    story ne touche pas ces surfaces.
- Required regression evidence:
  - tests unitaires du calculateur;
  - tests de contrats CS-208 maintenus;
  - scans imports interdits, scoring, interpretation;
  - diff des surfaces adjacentes obligatoire;
  - `ruff format .`, `ruff check .`, `pytest -q`.
- Allowed differences:
  - nouveau calculateur;
  - ajout de `PlanetaryMotionProfile`;
  - nouveau catalogue de profils;
  - export public;
  - nouveau test unitaire;
  - verification ou mise a jour de `RG-137` si le registre derive.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | La fonction principale est importable depuis le module calculateur. | Evidence: `Test-Path $p`, import test, `pytest -q $t`. |
| AC2 | `PlanetaryMotionProfile` expose le contrat du brief. | Evidence profile: `deterministic_test`; tests contrats + `pytest -q $t`. |
| AC3 | La direction respecte les seuils du brief. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC4 | La stationnarite a priorite sur toute autre direction. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC5 | La vitesse exactement zero produit `STATIONARY`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC6 | Le ratio `absolute_speed / mean_speed` est calcule pour mean speed valide. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC7 | Les etats `VERY_SLOW`, `SLOW`, `NORMAL`, `FAST`, `VERY_FAST` suivent les seuils configurables. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC8 | Mean speed invalide produit `UNKNOWN`. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC9 | Le catalogue par defaut correspond au tableau de profils du brief. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC10 | La fonction de lot leve `ValueError` lorsqu'un profil manque. | Evidence profile: `deterministic_test`; `pytest -q $t`. |
| AC11 | Le calculateur exclut les interdits du brief. | Evidence: `rg -n "from app|score_delta|prompt" $motion_paths`. |
| AC12 | Aucune integration adjacente n'est ajoutee hors package. | Evidence: `rg -n "PlanetaryMotionProfile" $adjacent_roots`. |
| AC13 | La qualite backend passe dans le venv. | Evidence profile: `deterministic_test`; `ruff format .`, `ruff check .`, `pytest -q`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer la baseline et confirmer l'ownership (AC: AC1, AC2, AC11, AC12)
  - [ ] Subtask 1.1 - Inspecter `contracts.py`, `__init__.py`,
    `test_contracts.py`, CS-208, CS-209 et `regression-guardrails.md`.
  - [ ] Subtask 1.2 - Verifier l'absence preexistante de
    `planetary_motion_calculator.py` et `planetary_motion_profiles.py`.
  - [ ] Subtask 1.3 - Documenter dans l'evidence l'etat attendu de `RG-135`,
    `RG-136` et `RG-137`.

- [ ] Task 2 - Ajouter le profil contractuel (AC: AC2, AC8, AC11)
  - [ ] Subtask 2.1 - Ajouter `PlanetaryMotionProfile` dans `contracts.py`.
  - [ ] Subtask 2.2 - Utiliser `dataclass(frozen=True, slots=True)`.
  - [ ] Subtask 2.3 - Valider l'ordre des seuils de ratio et le seuil
    stationnaire non negatif.
  - [ ] Subtask 2.4 - Autoriser explicitement un mean speed nul ou negatif
    pour couvrir `UNKNOWN`.
  - [ ] Subtask 2.5 - Exporter le contrat depuis `__init__.py`.

- [ ] Task 3 - Creer le catalogue de profils par defaut (AC: AC2, AC9, AC11)
  - [ ] Subtask 3.1 - Creer `planetary_motion_profiles.py`.
  - [ ] Subtask 3.2 - Construire les dix profils recommandes.
  - [ ] Subtask 3.3 - Utiliser les vitesses moyennes recommandees par le brief.
  - [ ] Subtask 3.4 - Calculer chaque `stationary_threshold_abs` comme
    `mean_speed * 0.05`.
  - [ ] Subtask 3.5 - Exposer le catalogue sans mutation accidentelle.

- [ ] Task 4 - Creer le calculateur de mouvement pur (AC: AC1, AC3, AC4, AC5, AC6, AC7, AC8, AC10, AC11)
  - [ ] Subtask 4.1 - Creer `planetary_motion_calculator.py`.
  - [ ] Subtask 4.2 - Implementer la direction avec priorite `STATIONARY`.
  - [ ] Subtask 4.3 - Implementer le ratio normalise et les etats de vitesse.
  - [ ] Subtask 4.4 - Implementer la fonction de lot avec erreur explicite pour
    profil manquant.
  - [ ] Subtask 4.5 - Exporter les fonctions publiques depuis `__init__.py`.

- [ ] Task 5 - Ajouter les tests unitaires (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10)
  - [ ] Subtask 5.1 - Creer
    `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py`.
  - [ ] Subtask 5.2 - Tester direct, retrograde, stationnaire et vitesse zero.
  - [ ] Subtask 5.3 - Tester tous les etats de vitesse et les seuils
    personnalises.
  - [ ] Subtask 5.4 - Tester mean speed invalide.
  - [ ] Subtask 5.5 - Tester que `UNKNOWN` n'est pas produit pour la direction
    quand une vitesse numerique et un profil sont fournis.
  - [ ] Subtask 5.6 - Tester le catalogue par defaut, ses vitesses moyennes, la
    fonction de lot et le profil manquant.
  - [ ] Subtask 5.7 - Etendre `test_contracts.py` pour `PlanetaryMotionProfile`.

- [ ] Task 6 - Ajouter et prouver les gardes anti-drift (AC: AC11, AC12)
  - [ ] Subtask 6.1 - Verifier que `RG-135` protege toujours les contrats purs.
  - [ ] Subtask 6.2 - Verifier que `RG-136` reste borne au calculateur solaire.
  - [ ] Subtask 6.3 - Verifier ou mettre a jour `RG-137` pour le calculateur de
    mouvement pur.
  - [ ] Subtask 6.4 - Executer les scans imports interdits, scoring,
    interpretation et surfaces adjacentes.

- [ ] Task 7 - Valider la story (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13)
  - [ ] Subtask 7.1 - Activer `.venv` avant toute commande Python.
  - [ ] Subtask 7.2 - Executer le test cible.
  - [ ] Subtask 7.3 - Executer `ruff format .`, `ruff check .` et `pytest -q`.
  - [ ] Subtask 7.4 - Documenter les resultats dans `evidence/validation.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PlanetaryMotionCondition`, `PlanetaryMotionDirection` et
    `PlanetarySpeedState` depuis `contracts.py`;
  - conventions `dataclass(frozen=True, slots=True)` existantes;
  - tests pytest sous `backend/tests/unit/domain/astrology/planetary_conditions`.
- Do not recreate:
  - contrats CS-208 sous un autre nom ou dans un autre package;
  - calculateurs `advanced_conditions`;
  - scoring de dignites, dominance, profils ou signaux;
  - schemas API/Pydantic pour les memes concepts;
  - moteur astronomique de calcul des vitesses.
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
- calcul astronomique des vitesses

Specific forbidden symbols / paths:

- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
  importing `app.api`
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
  importing `app.infra`
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
  importing `app.infrastructure`
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
  importing `app.services`
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py`
  importing `app.api`, `app.infra`, `app.infrastructure` or `app.services`
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
| Profil de mouvement planetaire | `planetary_conditions/contracts.py` | calculateur local duplique, settings, DB |
| Catalogue de profils par defaut | `planetary_conditions/planetary_motion_profiles.py` | seeders, migrations, frontend |
| Calcul direct/retrograde/stationnaire | `planetary_conditions/planetary_motion_calculator.py` | `advanced_conditions`, `dignities`, `json_builder.py`, frontend |
| Calcul etat de vitesse relatif | `planetary_conditions/planetary_motion_calculator.py` | scoring, dominance, interpretation adapters |
| Exports publics | `planetary_conditions/__init__.py` | alias ou re-export legacy |
| Integration future | future story | CS-210 ne modifie pas `NatalResult` |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Artifact Check

- Generated artifact check: not applicable
- Reason: no generated file, generated schema, generated client or generated
  documentation is affected by CS-210.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, frontend
  type or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/planetary_conditions/contracts.py`
- `backend/app/domain/astrology/planetary_conditions/__init__.py`
- `backend/app/domain/astrology/planetary_conditions/solar_proximity_calculator.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/app/domain/astrology/advanced_conditions/contracts.py` only for
  style comparison, not modification.

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/planetary_conditions/contracts.py` - ajouter
  `PlanetaryMotionProfile`.
- `backend/app/domain/astrology/planetary_conditions/__init__.py` - exporter
  profil, catalogue et fonctions publiques.
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py`
  - nouveau catalogue pur.
- `backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py`
  - nouveau calculateur pur.
- `_condamad/stories/regression-guardrails.md` - verifier ou mettre a jour
  `RG-137`.
- `_condamad/stories/CS-210-planetary-motion-conditions-calculator/evidence/validation.md`
  - preuves de validation.

Likely tests:

- `backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py`
  - couverture comportementale du calculateur.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - couverture du nouveau profil.

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

- Next planned story: `CS-211 - Oriental / Occidental Solar Phase Relation Calculator`
- Expected scope: calculer la relation oriental/occidental au Soleil et les
  phases solaires planetaires depuis les contrats CS-208.
- Boundary: CS-210 ne cree aucun calculateur de relation solaire et ne prepare
  pas d'integration opportuniste pour CS-211.

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
$t = "backend/tests/unit/domain/astrology/planetary_conditions/test_planetary_motion_calculator.py"
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
$p = "backend/app/domain/astrology/planetary_conditions/planetary_motion_calculator.py"
$profiles = "backend/app/domain/astrology/planetary_conditions/planetary_motion_profiles.py"
$motion_paths = "$p", "$profiles"
rg -n "from app\\.api|from app\\.infra|from app\\.infrastructure|from app\\.services" $motion_paths
rg -n "sqlalchemy|fastapi|pydantic|OpenAI|AIEngineAdapter" $motion_paths
rg -n "\\bscore\\b|score_delta|accidental_score_delta|essential_score_delta|strength_modifier" $motion_paths
rg -n "interpretation|meaning|description|narrative|prompt" $motion_paths
rg -n "PlanetaryMotionProfile|calculate_planetary_motion_condition|DEFAULT_PLANETARY_MOTION_PROFILES" `
  backend/app/domain/astrology/planetary_conditions `
  backend/tests/unit/domain/astrology/planetary_conditions
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
- symbols publics: hits limites aux nouveaux modules, exports et tests;
- diff des surfaces adjacentes: vide.

Story validation commands:

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-210-planetary-motion-conditions-calculator/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py --explain-contracts $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

Skipped-command rule:

- Any skipped command must be recorded in the final evidence with exact
  command, reason, risk and fallback evidence.

## 22. Regression Risks

- Risk: le calculateur de mouvement devient une source de scoring avant une
  story dediee.
  - Guardrail: AC11, scans scoring et `RG-137`.
- Risk: une integration opportuniste modifie le JSON public ou `NatalResult`.
  - Guardrail: AC12 et diff des surfaces adjacentes obligatoire.
- Risk: la stationnarite est calculee apres retrograde et produit un etat
  incoherent.
  - Guardrail: AC3, AC4 et tests stationnaire/zero.
- Risk: les seuils de vitesse sont hardcodes dans le calculateur au lieu du
  profil.
  - Guardrail: AC2, AC7 et seuils personnalises.
- Risk: le catalogue par defaut est confondu avec une verite astronomique
  d'ephemerides.
  - Guardrail: scope limite a la classification relative et non-goal sur le
    calcul astronomique des vitesses; les valeurs du brief sont reprises comme
    references de classification, pas comme ephemerides exactes.

## 23. Dev Agent Instructions

- Implement only CS-210.
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
- Do not add scoring, interpretation, prompts, LLM, API schemas or Pydantic
  models.
- Do not hardcode a no-retrograde rule for the Sun.
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
- `backend/tests/unit/domain/astrology/planetary_conditions/test_contracts.py`
  - tests de contrats a maintenir.
- `backend/tests/unit/domain/astrology/planetary_conditions/test_solar_proximity_calculator.py`
  - precedent de tests calculateur.
- `_condamad/stories/CS-208-advanced-planetary-conditions-contracts/00-story.md`
  - source contractuelle.
- `_condamad/stories/CS-209-solar-proximity-conditions-calculator/00-story.md`
  - precedent et follow-up explicite CS-210.
- `_condamad/stories/regression-guardrails.md` - invariants applicables
  `RG-107`, `RG-119`, `RG-122`, `RG-128`, `RG-129`, `RG-135`, `RG-136` et
  nouvel invariant `RG-137`.
