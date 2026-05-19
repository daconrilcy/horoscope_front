# Story CS-191 advanced-planet-dignity-engine: Construire le moteur avance de dignites planetaires

Status: done

## 1. Objective

Mettre en oeuvre un moteur backend de dignites planetaires avance qui consomme
exclusivement les referentiels astraux exposes dans le runtime. Le moteur
calcule des scores factuels et explicables par planete puis les expose dans `NatalResult`, sans
melanger referentiel, calcul et interpretation.

## 2. Trigger / Source

- Source type: architecture-decision
- Source reference: demande utilisateur du 2026-05-19 apres creation des referentiels de dignites astrales.
- Reason for change: les tables de dignites existent mais ne sont pas encore
  consommees par un moteur de calcul explicable, integre au resultat natal et
  fonde sur des contrats explicites.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/astrology/dignities`
- In scope:
  - etendre le runtime astrologique pour transporter les referentiels de dignites essentiels et accidentels sous contrats immutables;
  - creer les contrats domaine de resultat et de breakdown des dignites;
  - creer `SectCalculator`, `EssentialDignityCalculator`, `AccidentalDignityCalculator` et `PlanetDignityScoringService`;
  - exposer les dignites calculees dans le payload natal via les adaptateurs existants;
  - ajouter les tests unitaires, snapshots et gardes d'architecture necessaires.
- Out of scope:
  - interpretation editoriale des dignites;
  - appel LLM, prompt, narration ou enrichissement prediction;
  - persistance independante dans `astral_chart_planet_dignity_results`;
  - changement des seeds JSON ou des migrations deja livrees par CS-190;
  - frontend et affichage UI.
- Explicit non-goals:
  - ne pas introduire de scoring ou de regle astrologique codee en dur quand la donnee existe en table;
  - ne pas faire lire la DB directement par les calculateurs;
  - ne pas produire de texte interpretatif dans les calculateurs;
  - ne pas utiliser une polarite positive ou negative comme verite metier de scoring;
  - ne pas contourner `RG-095`, `RG-107`, `RG-108`, `RG-112`, `RG-114`, `RG-115` et `RG-116`.

## 4. Operation Contract

- Operation type: create
- Primary archetype: custom
- Archetype reason: la story cree un sous-domaine de calcul pur, etend le
  runtime reference, puis ajoute une projection payload.
- Behavior change allowed: constrained
- Behavior change constraints:
  - le payload natal peut gagner un bloc `dignities`;
  - les champs natals existants et leur semantique ne doivent pas changer;
  - les calculateurs doivent rester deterministes et sans interpretation;
  - le profil de scoring par defaut doit etre `traditional_standard` tant qu'aucun autre choix explicite n'est transmis.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: le resultat natal courant ne contient pas les
  donnees minimales requises aux dignites accidentelles et que les ajouter
  impose de modifier le contrat d'ephemeride au-dela du payload dignites.
- Additional validation rules:
  - prouver par test runtime que `AstrologyRuntimeReference.dignity_reference` est charge avant tout calcul de dignites;
  - prouver par scans cibles que les calculateurs n'importent ni DB, ni services, ni API, ni prediction, ni LLM;
  - prouver par snapshot que le payload natal existant reste stable hors ajout `dignities`.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story
scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | les calculateurs doivent prouver que leur source de verite est `AstrologyRuntimeReference` enrichi, pas la DB directe ni des constantes locales. |
| Baseline Snapshot | yes | le payload natal gagne un bloc; un avant/apres est requis pour prouver que l'existant reste stable. |
| Ownership Routing | yes | la story traverse infra, domaine et services chart; les responsabilites doivent rester separees. |
| Allowlist Exception | no | aucune exception, alias, fallback ou shim n'est autorise. |
| Contract Shape | yes | `NatalResult.dignities` et les dataclasses de breakdown ont une forme publique explicite. |
| Batch Migration | yes | l'implementation doit etre livree par lots independants: runtime, domaine, calculateurs, integration payload. |
| Reintroduction Guard | yes | les futures regressions DB directes, hardcoding et interpretation doivent echouer. |
| Persistent Evidence | yes | les snapshots et scans doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - loaded config: inventaire runtime de `AstrologyRuntimeReference.dignity_reference` charge depuis les modeles DB et seeds canoniques.
- Secondary evidence:
  - tests repository/runtime reference, snapshots de payload natal et scans `rg` anti-import DB dans les calculateurs.
- Static scans alone are not sufficient for this story because:
  - le risque principal est une mauvaise composition runtime ou un payload
    incomplet; il faut donc des tests executant le chargement reference.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-191-advanced-planet-dignity-engine/evidence/natal-payload-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-191-advanced-planet-dignity-engine/evidence/natal-payload-after.json`
- Expected invariant:
  - tous les champs natals existants restent presents et inchanges; seul le bloc `dignities` est ajoute.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Chargement SQLAlchemy des referentiels dignites | `backend/app/infra/db/repositories/**` | `backend/app/domain/**` |
| Contrats runtime immutables | `backend/app/domain/astrology/runtime/runtime_reference.py` | `backend/app/services/**` |
| Calcul pur des dignites | `backend/app/domain/astrology/dignities/**` | `backend/app/infra/**`, `backend/app/api/**` |
| Orchestration applicative du resultat natal | `backend/app/services/natal/**` ou service existant equivalent | `backend/app/api/**` |
| Projection JSON publique | `backend/app/services/chart/json_builder.py` | calculateurs domaine |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract type:
  - DTO domaine et payload `NatalResult.dignities`
- Fields:
  - `score_profile: string` identifiant du profil de scoring utilise.
  - `tradition: string` systeme astrologique de reference.
  - `reference_version: string` version reference affichee dans le payload.
  - `sect: string` valeur `day` ou `night`.
  - `planets: object` mapping par code planete.
  - `essential_score: number` total des dignites essentielles.
  - `accidental_score: number` total des dignites accidentelles.
  - `total_score: number` somme de `essential_score` et `accidental_score`.
  - `functional_strength_score: number` agregat des poids fonctionnels.
  - `expression_quality_score: number` agregat des poids d'expression.
  - `intensity_score: number` agregat des poids d'intensite.
  - `essential_breakdown: array` liste des dignites essentielles detectees.
  - `accidental_breakdown: array` liste des dignites accidentelles detectees.
- Required fields:
  - tous les champs listes ci-dessus sont requis dans chaque resultat planete.
- Optional fields:
  - aucun champ optionnel dans le payload dignites de cette story.
- Status codes:
  - aucune route API nouvelle n'est creee et aucun status code n'est modifie.
- Serialization names:
  - `PlanetDignityResult.essential_breakdown` devient `essential_breakdown`.
  - `EssentialDignityMatch.dignity_type_code` devient `type`.
  - `EssentialDignityMatch.score_value` devient `score`.
  - `AccidentalDignityMatch.dignity_type_code` devient `type`.
  - `AccidentalDignityMatch.score_value` devient `score`.
- Frontend type impact:
  - le payload backend peut etre consomme plus tard par le front, mais cette story ne modifie pas les types frontend.
- Generated contract impact:
  - OpenAPI ne doit pas changer sauf si le payload natal est deja modelise par schema genere; dans ce cas le snapshot doit documenter uniquement l'ajout `dignities`.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Runtime reference | runtime sans dignites | `AstrologyRuntimeReference.dignity_reference` | repo runtime | repo test | preuve zero DB lookup | modele manquant |
| Domain calculators | pas de moteur dignites | `domain/astrology/dignities/**` | tests domaine | dignity unit tests | preuve zero score constant | donnees natales insuffisantes |
| Natal integration | payload sans dignites | `NatalResult.dignities` | service natal, json builder | chart payload tests | preuve snapshot stable | rupture payload |

Closure map:

- Total affected surface: runtime reference astrologique, domaine astrology dignities, payload natal.
- Batches included in this story: les trois lots listes ci-dessus.
- Batches intentionally deferred: persistance audit dans `astral_chart_planet_dignity_results` et UI frontend.
- Stop condition for this story: `NatalResult` expose des dignites scorees, testees et derivees du runtime a contrats explicites.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Snapshot payload natal avant | `_condamad/stories/CS-191-advanced-planet-dignity-engine/evidence/natal-payload-before.json` | prouver la stabilite du payload existant. |
| Snapshot payload natal apres | `_condamad/stories/CS-191-advanced-planet-dignity-engine/evidence/natal-payload-after.json` | prouver l'ajout exact du bloc `dignities`. |
| Rapport runtime dignites | `evidence/dignity-runtime-reference.md` | lister les tables chargees. |
| Rapport gardes | `evidence/dignity-guard-evidence.md` | conserver les scans et resultats. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- importable Python modules
- forbidden symbols or states
- runtime reference inventory

Required forbidden examples:

- `from app.infra` dans `backend/app/domain/astrology/dignities/**`
- `Session`, `select(` ou modeles SQLAlchemy dans les calculateurs
- mappings locaux de score par dignite comme `DOMICILE_SCORE`, `DIGNITY_SCORES` ou equivalent
- imports ou symboles `AIEngineAdapter`, `OpenAI`, `prompt`, `interpretation` dans les calculateurs

Guard evidence:

- Evidence profile: `reintroduction_guard`;
  `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` et les
  scans du plan de validation verifient les symboles interdits.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/astrology/runtime/runtime_reference.py` -
  le runtime expose deja `AstrologyRuntimeReference`.
- Evidence 2: `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` -
  `_load_dignities()` charge seulement les dignites signe-planete historiques.
- Evidence 3: `backend/app/infra/db/repositories/dignity_reference_repository.py` -
  un repository dedie aux nouveaux referentiels existe.
- Evidence 4: `backend/app/infra/db/models/dignity_reference.py` - les modeles SQLAlchemy des nouvelles tables de dignites et resultats audit existent.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - shared regression invariants consulted before story scope was finalized.

## 6. Target State

After implementation:

- `AstrologyRuntimeReference` contient un referentiel de dignites complet, explicite et immuable.
- Les calculateurs de dignites consomment uniquement ce runtime et les donnees natales deja calculees.
- Les dignites essentielles detectent domicile, exaltation, detriment, fall, triplicity, term, face/decan et peregrine.
- Les dignites accidentelles detectent maisons, mouvement direct ou retrograde, conditions solaires exclusives et joies planetaires.
- `PlanetDignityScoringService` retourne un `PlanetDignityResult` par planete, sans interpretation.
- Le payload natal expose `dignities` avec breakdown explicable et scores agreges.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-095` - le nouveau domaine astrology ne doit pas dependre de prediction.
  - `RG-107` - les donnees astrologiques runtime doivent rester typees et les JSON DB confines a l'infra.
  - `RG-108` - les referentiels DB-backed de dignites ne doivent pas etre recrees sous forme de constantes locales.
  - `RG-112` - les constantes metier astrologiques et fallbacks legacy ne doivent pas revenir.
  - `RG-114` - les attributs element, modalite et polarite des signes utilises par triplicite ou secte restent DB-backed.
  - `RG-115` - le runtime natal reste objectif et fonde sur des contrats explicites.
  - `RG-116` - les calculateurs ne doivent pas importer de services ou modeles d'interpretation.
  - `RG-118` - cette story etablit le moteur de dignites comme calcul pur sur runtime a contrats explicites.
- Non-applicable invariants:
  - `RG-117` - cette story ne touche pas le scoring des etoiles fixes daily.
- Required regression evidence:
  - tests unitaires calculateurs, tests runtime repository, snapshot payload avant/apres, scan anti-import DB, scan anti-LLM et scan anti-hardcoding.
- Allowed differences:
  - ajout du bloc `dignities` dans le payload natal uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le runtime expose `dignity_reference`. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py` |
| AC2 | Les contrats resultats n'exposent aucun dict libre. | Evidence profile: `contract_shape`; test `pytest backend/tests/unit/domain/astrology/test_dignity_contracts.py`. |
| AC3 | `SectCalculator` retourne une secte explicite. | Evidence profile: `unit`; test `pytest backend/tests/unit/domain/astrology/test_sect_calculator.py`. |
| AC4 | `EssentialDignityCalculator` calcule depuis le runtime. | `pytest -q backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py` |
| AC5 | `AccidentalDignityCalculator` calcule les dignites accidentelles demandees. | `pytest -q backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py` |
| AC6 | Le scoring service orchestre sans interpretation ni LLM. | `pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` |
| AC7 | `NatalResult` expose `dignities` sans casser l'existant. | Evidence profile: `baseline_snapshot`; test `pytest backend/app/tests/unit/test_chart_json_builder.py`. |
| AC8 | Les calculateurs ne lisent jamais la DB. | `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py` + scans RG-118 |

## 8. Implementation Tasks

- [ ] Task 1 - Inspecter les surfaces runtime et payload avant modification (AC: AC1, AC7)
  - [ ] Subtask 1.1 - Lire les contrats runtime, repository runtime reference et repository dignity existants.
  - [ ] Subtask 1.2 - Capturer `_condamad/stories/CS-191-advanced-planet-dignity-engine/evidence/natal-payload-before.json`.
  - [ ] Subtask 1.3 - Documenter les donnees natales disponibles pour les dignites accidentelles.

- [ ] Task 2 - Etendre le runtime reference dignites (AC: AC1)
  - [ ] Subtask 2.1 - Ajouter les dataclasses immutables pour les types, regles, systems, bounds, decans, profiles et weights.
  - [ ] Subtask 2.2 - Brancher le chargement via les repositories infra existants sans exposer de JSON libre.
  - [ ] Subtask 2.3 - Ajouter les tests de chargement et de completude des referentiels.

- [ ] Task 3 - Creer les contrats domaine des resultats (AC: AC2)
  - [ ] Subtask 3.1 - Creer `backend/app/domain/astrology/dignities/contracts.py`.
  - [ ] Subtask 3.2 - Ajouter les tests d'immutabilite, de tuples et de serialisation en bordure.
  - [ ] Subtask 3.3 - Verifier qu'aucun dict libre ne traverse le domaine dignites.

- [ ] Task 4 - Implementer le calcul de secte et les dignites essentielles (AC: AC3, AC4)
  - [ ] Subtask 4.1 - Implementer `SectCalculator`.
  - [ ] Subtask 4.2 - Implementer `EssentialDignityCalculator` avec breakdown explicable.
  - [ ] Subtask 4.3 - Couvrir chaque dignite essentielle par tests unitaires.

- [ ] Task 5 - Implementer les dignites accidentelles (AC: AC5)
  - [ ] Subtask 5.1 - Implementer maison angulaire, succedente, cadente et joie planetaire.
  - [ ] Subtask 5.2 - Implementer mouvement direct, retrograde et conditions solaires.
  - [ ] Subtask 5.3 - Tester la priorite cazimi, combust, under sunbeams.

- [ ] Task 6 - Ajouter l'orchestrateur et l'integration natal (AC: AC6, AC7)
  - [ ] Subtask 6.1 - Implementer `PlanetDignityScoringService`.
  - [ ] Subtask 6.2 - Brancher le service dans le flux natal existant au point le plus proche du calcul objectif.
  - [ ] Subtask 6.3 - Adapter la projection JSON pour le bloc `dignities`.
  - [ ] Subtask 6.4 - Capturer `_condamad/stories/CS-191-advanced-planet-dignity-engine/evidence/natal-payload-after.json`.

- [ ] Task 7 - Ajouter les gardes et preuves finales (AC: AC8)
  - [ ] Subtask 7.1 - Ajouter ou etendre une garde d'architecture pour imports interdits, hardcoding et interpretation.
  - [ ] Subtask 7.2 - Produire `dignity-runtime-reference.md` et `dignity-guard-evidence.md`.
  - [ ] Subtask 7.3 - Executer lint, tests cibles et scans du plan de validation.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AstrologyRuntimeReference` pour transporter les referentiels astrologiques.
  - `DignityReferenceRepository` pour les tables deja creees par CS-190.
  - `backend/app/infra/db/models/dignity_reference.py` pour les modeles SQLAlchemy existants.
  - les contrats de signes, planetes, maisons, elements, systems et reference versions deja charges dans le runtime.
- Do not recreate:
  - listes locales de signes, planetes, elements, maisons ou systems;
  - mappings locaux des scores par type de dignite;
  - conditions de termes, decans ou triplicites sous constantes Python;
  - interpretation textuelle ou micro-notes comme sortie calculateur.
- Shared abstraction allowed only if:
  - elle remplace une duplication reelle entre essential et accidental, reste dans `domain/astrology/dignities`, et ne masque pas les proprietaires infra ou service.

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

- `backend/app/domain/astrology/dignities/**` important `app.infra`, `sqlalchemy`, `Session` ou modeles DB.
- `backend/app/domain/astrology/dignities/**` important `AIEngineAdapter`, `OpenAI`, services LLM ou services prediction.
- `DIGNITY_SCORES`, `DOMICILE_SCORE`, `ACCIDENTAL_DIGNITY_SCORES` ou mapping equivalent de scores locaux.
- lecture directe de `astral_chart_planet_dignity_results` pendant le calcul natal.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chargement des referentiels dignites | `backend/app/infra/db/repositories/dignity_reference_repository.py` et repository runtime reference | calculateurs domaine |
| Contrats de runtime astrology | `backend/app/domain/astrology/runtime/runtime_reference.py` | services chart, routeurs API |
| Calcul de dignites | `backend/app/domain/astrology/dignities/**` | infra DB, LLM, prediction, API |
| Projection payload natal | `backend/app/services/chart/json_builder.py` | calculateurs domaine |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 16. Generated Contract Check

- Generated contract check: applicable if the natal payload schema is generated by FastAPI/OpenAPI.
- Required generated-contract evidence:
  - compare OpenAPI or schema snapshot when a generated schema includes `NatalResult`.
  - document that no route path or status code changed.
  - generated client/schema absence is acceptable only if no generated client exists for this payload.

## 17. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/infra/db/repositories/dignity_reference_repository.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/chart/result_service.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/app/tests/unit/test_chart_json_builder.py`
- `backend/app/tests/unit/test_chart_result_service.py`

## 18. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/runtime/runtime_reference.py` - ajouter les contrats runtime dignites.
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` - charger les nouveaux referentiels dans le runtime.
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` - mapper les lignes DB vers contrats immutables si ce mapper est l'owner local.
- `backend/app/domain/astrology/dignities/contracts.py` - nouveaux contrats domaine.
- `backend/app/domain/astrology/dignities/sect_calculator.py` - calcul de secte.
- `backend/app/domain/astrology/dignities/essential_dignity_calculator.py` - calcul essential.
- `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` - calcul accidental.
- `backend/app/domain/astrology/dignities/planet_dignity_scoring_service.py` - orchestration par planete.
- `backend/app/domain/astrology/natal_calculation.py` - porter les resultats objectifs dans `NatalResult`.
- `backend/app/services/natal/calculation_service.py` - brancher le service de scoring si ce flux est l'owner du calcul natal.
- `backend/app/services/chart/json_builder.py` - serialiser le bloc `dignities`.
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py` - ajouter les gardes anti-reintroduction.

Likely tests:

- `backend/tests/unit/domain/astrology/test_dignity_contracts.py` - contrats immutables et absence de dict libre.
- `backend/tests/unit/domain/astrology/test_sect_calculator.py` - secte jour/nuit.
- `backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py` - dignites essentielles.
- `backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py` - dignites accidentelles.
- `backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py` - orchestration scores.
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py` - chargement runtime.
- `backend/app/tests/unit/test_chart_json_builder.py` - projection JSON.
- `backend/app/tests/unit/test_chart_result_service.py` - persistance payload existante.

Files not expected to change:

- `frontend/**` - aucune UI dans cette story.
- `docs/db_seeder/astrology/**` - les seeds sont hors scope et ont ete traites avant cette story.
- `backend/app/api/**` - aucune route nouvelle.

## 19. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 20. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q backend/tests/unit/domain/astrology/test_sect_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_dignity_contracts.py
pytest -q backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_accidental_dignity_calculator.py
pytest -q backend/tests/unit/domain/astrology/test_planet_dignity_scoring_service.py
pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py
pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py
pytest -q backend/app/tests/unit/test_chart_json_builder.py
pytest -q backend/app/tests/unit/test_chart_result_service.py
Set-Location backend
ruff check .
ruff format --check .
Set-Location ..
rg -n "Session|select\\(|from app\\.infra|from app\\.services|from app\\.api" backend/app/domain/astrology/dignities -g "*.py"
rg -n "DIGNITY_SCORES|DOMICILE_SCORE|ACCIDENTAL_DIGNITY_SCORES|score_value\\s*=\\s*[-0-9]" backend/app/domain/astrology/dignities -g "*.py"
rg -n "OpenAI|AIEngineAdapter|chat\\.completions|prompt|interpretation|micro_note" backend/app/domain/astrology/dignities -g "*.py"
```

Expected scan result: zero production hit for forbidden imports, local score
mappings, LLM or interpretation symbols. Any hit must be removed or documented
as a false positive in `dignity-guard-evidence.md` with exact file and reason.

## 21. Regression Risks

- Risk: les calculateurs recreent les referentiels DB-backed en constantes Python.
  - Guardrail: `RG-108`, `RG-112`, tests runtime reference et scans anti-hardcoding.
- Risk: le domaine astrology importe infra, services ou prediction.
  - Guardrail: `RG-095`, `RG-107`, scan imports interdits.
- Risk: le payload natal existant est modifie involontairement.
  - Guardrail: snapshot avant/apres et tests `json_builder` / `result_service`.
- Risk: les conditions solaires accidentelles scorent plusieurs etats incompatibles.
  - Guardrail: tests unitaires de priorite cazimi, combust, under sunbeams.
- Risk: le calcul se transforme en interpretation.
  - Guardrail: `RG-116`, scan anti-LLM et anti-interpretation.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias,
  TODO, or hidden residual in-domain work when this story is marked
  `full-closure`.
- Keep comments and docstrings in French for every new or materially modified backend file.
- Run all Python commands only after `.\.venv\Scripts\Activate.ps1`.

## 23. References

- `backend/app/domain/astrology/runtime/runtime_reference.py` - owner du runtime reference.
- `backend/app/infra/db/repositories/dignity_reference_repository.py` - acces DB existant aux referentiels de dignites.
- `backend/app/infra/db/models/dignity_reference.py` - modeles SQLAlchemy des tables seeds par CS-190.
- `_condamad/stories/CS-190-seed-astral-dignity-reference-runtime/00-story.md` - story precedente qui cree les tables et repositories.
- `_condamad/stories/regression-guardrails.md` - invariants a respecter et enrichir.
