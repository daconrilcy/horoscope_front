# Story CS-172 big-bang-reference-runtime-astrology: Basculer le runtime astrologique sur des contrats DB immutables

Status: ready-to-review

## 1. Objective

Basculer en big bang le flux natal astrologique vers un runtime DB complet, type et
immutable. Le domaine ne doit plus recevoir de `dict` metier non type, de constantes
astrologiques DB-backed ou de fallback silencieux pour le referentiel. L'infra charge et
mappe les tables DB, le service orchestre le use-case natal, le domaine calcule avec des
contrats explicites, et la serialization JSON/API ou preparation LLM reste hors domaine.

## 2. Trigger / Source

- Source type: audit
- Source reference: demande utilisateur du 2026-05-15 sur l'audit complet de
  `backend/app/domain/astrology`, DRY, legacy, bugs, constantes hardcodees et separation
  calcul astrologique / interpretation / preparation LLM.
- Reason for change: le flux actuel laisse circuler des `dict` metier, des constantes de
  referentiel et des fallbacks qui masquent les erreurs de donnees.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: backend astrology runtime reference and natal calculation vertical slice
- In scope:
  - `backend/app/domain/astrology/**` pour contrats runtime et calcul pur.
  - `backend/app/services/natal/**` pour l'orchestration natal.
  - `backend/app/infra/**` pour lecture DB, mapping et validation du referentiel.
  - Tests backend, factories, guardrails et preuves CONDAMAD.
- Out of scope:
  - Refonte frontend.
  - Refonte editoriale hors separation stricte avec le calcul.
  - Migration progressive, feature flag, double run, shim ou compatibilite.
- Explicit non-goals:
  - Ne pas utiliser `TypedDict` pour le coeur runtime.
  - Ne pas conserver `ReferenceDataService` dans le flux natal.
  - Ne pas dupliquer en constantes Python les donnees deja presentes en DB.
  - Ne pas deplacer la logique metier dans l'API ou l'infra.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story supprime les surfaces legacy du flux natal (`dict` metier,
  constantes DB-backed, fallbacks implicites) et impose le runtime DB type.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les erreurs de referentiel incomplet deviennent bloquantes.
  - `simplified` est autorise uniquement si l'option de calcul le demande explicitement.
  - La projection API conserve les noms publics sauf decision utilisateur.
  - Le calcul astrologique reste equivalent quand la DB est complete.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une surface OpenAPI publique ou table DB manquante impose un
  changement produit non couvert.

`Replacement allowed: no` interdit les wrappers, aliases, repointing et chemins de
compatibilite. La nouvelle implementation canonique `AstrologyRuntimeReference` reste
obligatoire.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le referentiel vient des tables DB chargees au runtime. |
| Baseline Snapshot | yes | La bascule doit distinguer changement structurel et derive de calcul. |
| Ownership Routing | yes | Les responsabilites infra/service/domain changent. |
| Allowlist Exception | yes | Registre actif pour prouver qu'aucune exception n'est admise. |
| Contract Shape | yes | Entrees et sorties domaine sont formalisees. |
| Batch Migration | yes | Bascule big bang par lots ordonnes sans coexistence legacy. |
| Reintroduction Guard | yes | Les anciennes surfaces doivent rester interdites. |
| Persistent Evidence | yes | Les preuves doivent etre conservees dans le dossier story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - DB schema and loaded DB rows exposed through SQLAlchemy metadata/models for
    `astral_planets`, `astral_signs`, `astral_house_systems`, `astral_angle_points`,
    `astral_house_modalities`, `astral_aspect_families`, `astral_aspect_profiles`,
    `astral_systems`, dignites, rulerships, maisons et references associees.
  - `AstrologyRuntimeReferenceRepository` retourne `AstrologyRuntimeReference`.
  - `AstrologyRuntimeReferenceMapper` convertit rows DB et JSON DB en dataclasses.
- Secondary evidence:
  - Tests repository/mapper.
  - Scans `rg` cibles.
  - Guard AST sur signatures publiques.
- Static scans alone are not sufficient for this story because:
  - La completude du referentiel doit etre prouvee par chargement runtime DB.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/evidence/baseline-natal-runtime-before.json`
- Comparison after implementation:
  - `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/evidence/baseline-natal-runtime-after.json`
- Expected invariant:
  - A DB complete produit des positions, maisons, aspects et dignites coherents.
  - Les cas anciennement masques par fallback ou `unknown` deviennent explicites.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Lecture SQLAlchemy et JSON DB | `backend/app/infra/**` | `backend/app/domain/**` |
| Mapping DB vers runtime | `backend/app/infra/**` | `backend/app/services/**` |
| Contrats runtime immutables | `backend/app/domain/astrology/**` | `backend/app/infra/**` |
| Calcul astrologique pur | `backend/app/domain/astrology/**` | `backend/app/services/**` |
| Orchestration natal | `backend/app/services/natal/**` | `backend/app/domain/**` |
| Serialization JSON/API | `backend/app/services/**` ou `backend/app/api/**` | `backend/app/domain/**` |
| Preparation LLM | service interpretation/prediction | `backend/app/domain/astrology/**` |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Empty register: any real allowlist row blocks closure. | permanent denial |

## 4f. Contract Shape

- Contract type:
  - Domain dataclasses immutables et frontiere service/API.
- Fields:
  - `AstrologyRuntimeReference.reference_version_id: int`
  - `AstrologyRuntimeReference.planets: PlanetReferenceSet`
  - `AstrologyRuntimeReference.signs: SignReferenceSet`
  - `AstrologyRuntimeReference.aspects: AspectReferenceSet`
  - `AstrologyRuntimeReference.houses: HouseReferenceSet`
  - `AstrologyRuntimeReference.dignities: DignityReferenceSet`
  - `AstrologyRuntimeReference.angle_points: AnglePointReferenceSet`
  - `AstrologyRuntimeReference.house_systems: HouseSystemReferenceSet`
  - `AstrologyRuntimeReference.systems: AstrologySystemReferenceSet`
  - `NatalResult`, `NatalPlanetPosition`, `NatalHouseRuntimeData`,
    `NatalAspectRuntimeData`, `NatalDignityRuntimeData`
- Required fields:
  - Tous les champs du runtime reference.
- Optional fields:
  - Metadonnees techniques hors coeur domaine.
- Status codes:
  - Pas de changement HTTP attendu si l'API reste stable.
- Serialization names:
  - La conversion JSON reste hors domaine.
- Frontend type impact:
  - Aucun impact attendu sans diff OpenAPI.
- Generated contract impact:
  - Produire une note OpenAPI ou bloquer si schema public modifie.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| A | `dict` et constantes | dataclasses domaine | domain + tests | contrats runtime | scan signatures | DB manquante |
| B | parsing JSON service | mapper infra | repos + service | tests mapper | no JSON domain | row ambigue |
| C | `ReferenceDataService` natal | repository runtime | service natal | tests repo | scan legacy | version ambigue |
| D | `unknown` / seeds | validation bloquante | calcul natal | tests negatifs | scan no unknown | DB incoherente |
| E | `reference_data=dict` | `runtime_reference` | services + tests | tests calcul | scan signatures | appel non migre |
| F | mutation reference | service repository | service natal | tests service | scan mutation | decision produit |
| G | fallbacks constantes | erreurs + DB | domain/services | guards | scan symboles | usage externe |
| H | fixtures partielles | factory runtime | tests backend | pytest cible | no dict fixture | dette test |

Closure map:

- Total affected surface: flux natal backend du chargement referentiel a la projection.
- Batches included in this story: A, B, C, D, E, F, G, H.
- Batches intentionally deferred: none.
- Stop condition for the source finding: consommateurs natal/domain sur runtime type,
  fallbacks implicites supprimes, constantes DB-backed absentes et guards PASS.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Baseline before | `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/evidence/baseline-natal-runtime-before.json` | Avant bascule. |
| Baseline after | `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/evidence/baseline-natal-runtime-after.json` | Apres bascule. |
| Runtime integrity | `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/evidence/runtime-reference-integrity.json` | Checks DB. |
| Removal audit | `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/removal-audit.md` | Surfaces legacy. |
| OpenAPI impact | `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/evidence/openapi-impact.md` | Diff ou non-impact. |
| Guard output | `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/evidence/architecture-guards.txt` | Anti-retour. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- forbidden symbols
- generated OpenAPI paths if affected
- importable python modules

Required forbidden examples:

- `ReferenceDataService.get_active_reference_data` dans le flux natal.
- `reference_data: dict` comme entree metier publique.
- `PLANET_KEYWORDS`, `SIGN_RULERS`, `DEFAULT_ORB`, `ASPECT_WEIGHTS`,
  `HOUSE_MEANINGS`, `UNKNOWN_SIGN`.
- `ZODIAC_SIGNS` comme source runtime canonique.
- `EXACT_ORB_DEG`, `TIGHT_RATIO`, `MODERATE_RATIO`.
- fallback implicite SwissEph vers `simplified`.
- valeurs sentinelles `unknown` dans les contrats runtime.

Guard evidence:

- Evidence profile: `reintroduction_guard`; command:
  `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py`.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: `user-audit-2026-05-15#backend-app-domain-astrology-dry-legacy-hardcoded-constants-boundary`
- Closure proof required: tests, scans, baseline, audit removal et integrity report.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

Full closure forbids `PASS with limitation`, broad allowlists, wildcard exceptions,
fallback, compatibility, legacy, migration-only, shim, alias, TODO and hidden residual work.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/astrology/zodiac.py` - contient `ZODIAC_SIGNS`.
- Evidence 2: `backend/app/domain/astrology/celestial_runtime_catalog.py` - contient des
  references runtime locales.
- Evidence 3: `backend/app/domain/astrology/house_system_codes.py` - contient des systems DB.
- Evidence 4: `backend/app/domain/astrology/interpretation/aspect_strength.py` - contient
  `EXACT_ORB_DEG`, `TIGHT_RATIO`, `MODERATE_RATIO`.
- Evidence 5: `backend/app/services/natal/calculation_service.py` - utilise le flux reference legacy.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - consulte.

## 6. Target State

- `AstrologyRuntimeReference` est la photographie runtime unique.
- Les contrats domaine sont des `dataclass(frozen=True, slots=True)`.
- Les JSON DB sont confines a l'infra.
- Les constantes astrologiques metier DB-backed quittent le flux runtime.
- Les constantes mathematiques restent autorisees.
- Le service natal orchestre; le domaine calcule; l'API/service serialise.
- La preparation LLM reste hors `domain/astrology`.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-091` a `RG-107` - invariants actifs astrology/prediction applicables.
- Non-applicable invariants:
  - none.
- Required regression evidence:
  - Tests architecture, repository, service, scans negatifs et OpenAPI non-impact.
- Allowed differences:
  - Les fallbacks implicites deviennent des erreurs explicites.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Immutable runtime dataclasses. | Evidence profile: `contract_shape` + `runtime_reference`; `pytest -q backend/tests/unit/domain/astrology/test_runtime_ref.py`. |
| AC2 | Infra repository loads DB runtime refs. | Evidence profile: `runtime_reference`; `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC3 | Runtime integrity is blocking. | Evidence profile: `negative_path`; `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_repository.py`. |
| AC4 | Public domain functions accept no business `dict`. | Evidence profile: `architecture_guard`; `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py`. |
| AC5 | Domain returns typed natal result contracts. | Evidence profile: `contract_shape`; `pytest -q backend/tests/unit/domain/astrology/test_natal_result_contract.py`. |
| AC6 | Natal service uses runtime ref. | Evidence profile: `integration` + `runtime_reference`; `pytest -q backend/app/tests/unit/test_natal_calculation_service.py`. |
| AC7 | Implicit engine fallback is removed. | Evidence profile: `negative_path`; `pytest -q backend/app/tests/unit/test_natal_calculation_service.py`. |
| AC8 | DB-backed constants leave runtime. | Evidence profile: `reintroduction_guard` + `runtime_reference`; `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py`. |
| AC9 | Legacy partial fixtures are migrated or deleted. | Evidence profile: `test_coverage`; `pytest -q backend/tests/unit/domain/astrology/test_runtime_ref.py`. |
| AC10 | LLM preparation stays outside astrology domain. | Evidence profile: `architecture_guard`; `pytest -q backend/app/tests/unit/test_scope_separation_imports.py`. |
| AC11 | Evidence files are persisted. | Evidence profile: `persistent_evidence` + `runtime_reference`; `pytest -q backend/app/tests/unit`. |
| AC12 | Big bang only: no migration flag. | Evidence profile: `no_legacy`; `pytest -q backend/app/tests/unit/test_astrology_runtime_reference_guard.py`. |

Acceptance details:

- AC1 covers `AstrologyRuntimeReference` and its reference sets.
- AC2 covers repository ownership, mapper delegation and JSON confinement in infra.
- AC3 covers 12 signs, houses, required planets/aspects, dignities, house systems,
  orphan references, active version ambiguity and `unknown`.
- AC4 covers exported/public domain functions called from services.
- AC5 covers typed `NatalResult` and subcontracts.
- AC6 covers removal of `ReferenceDataService` usage and reference mutation.
- AC7 covers SwissEph to `simplified`, active/latest and silent defaults.
- AC8 covers audited DB-backed constants while preserving math constants.
- AC9 covers official test factory and partial fixtures.
- AC10 covers imports and LLM prompt/payload absence in astrology.
- AC11 covers baseline, integrity report, removal audit, OpenAPI impact and guards.
- AC12 covers feature flag, double run, shim, alias and transitional fallback.

## 8. Implementation Tasks

- [ ] Task 1 - Capturer baseline et inventaire legacy (AC: AC8, AC11)
- [ ] Task 2 - Creer les contrats runtime immutables domaine (AC: AC1, AC5)
- [ ] Task 3 - Implementer mapper et repository infra (AC: AC2, AC3)
- [ ] Task 4 - Basculer les signatures du domaine (AC: AC4, AC5, AC8)
- [ ] Task 5 - Basculer `NatalCalculationService` en big bang (AC: AC6, AC7, AC12)
- [ ] Task 6 - Migrer ou supprimer les tests legacy (AC: AC9, AC12)
- [ ] Task 7 - Ajouter guardrails d'architecture et RG-107 (AC: AC4, AC8, AC10, AC12)
- [ ] Task 8 - Produire preuves finales et validation (AC: AC3, AC10, AC11)

## 9. Mandatory Reuse / DRY Constraints

- Reuse SQLAlchemy models, tables `astral_*`, session DB, repositories et conventions existantes.
- Do not recreate listes locales de signes, planetes, aspects, dignites ou systems.
- Do not parse JSON DB dans `domain/astrology`.
- Do not create two active natal pipelines.

## 10. No Legacy / Forbidden Paths

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- migration flag
- `ReferenceDataService.get_active_reference_data` dans le flux natal
- `reference_data: dict`
- `dict[str, Any]` pour donnees astrologiques metier
- `PLANET_KEYWORDS`, `SIGN_RULERS`, `DEFAULT_ORB`, `ASPECT_WEIGHTS`, `HOUSE_MEANINGS`
- `UNKNOWN_SIGN`, `ZODIAC_SIGNS`, `EXACT_ORB_DEG`, `TIGHT_RATIO`, `MODERATE_RATIO`

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: referenced by production code or canonical owner.
- `external-active`: referenced by public docs, generated links or clients.
- `historical-facade`: delegates only to preserve old surface.
- `dead`: zero references.
- `needs-user-decision`: ambiguity remains after scans.

## 12. Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path:

- `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/removal-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Structural references | DB `astral_*` + infra repository | Python constants |
| Runtime contracts | `backend/app/domain/astrology/**` | `TypedDict`, loose `dict` |
| JSON DB parsing | `backend/app/infra/**` | domain/services |
| Natal orchestration | `backend/app/services/natal/**` | domain DB loading |
| LLM preparation | interpretation/prediction service | `domain/astrology` |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is `external-active`, it must not be deleted. The dev agent must stop or
record explicit user decision with external evidence and deletion risk.

## 17. Generated Contract Check

- Generate or inspect FastAPI `app.openapi()` for natal schemas if affected.
- Record diff or non-impact in `evidence/openapi-impact.md`.

## 18. Files to Inspect First

- `backend/app/domain/astrology`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/infra`
- `backend/app/infra/db`
- `backend/tests`
- `backend/app/tests`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/astrology/**/*.py`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/infra/**/*.py`
- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/generated/*.md`

Likely tests:

- `backend/tests/unit/domain/astrology/**/*.py`
- `backend/app/tests/unit/**/*.py`

Files not expected to change:

- `frontend/**`
- `backend/pyproject.toml`
- `docs/recherches astro/*.json`

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
ruff format .
ruff check .
pytest -q
pytest -q tests/unit/domain/astrology app/tests/unit/test_natal_calculation_service.py
pytest -q app/tests/unit/test_reference_data_service.py app/tests/unit/test_scope_separation_imports.py
Pop-Location
python .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-172-big-bang-reference-runtime-astrology/00-story.md
```

Negative scans:

```powershell
.\.venv\Scripts\Activate.ps1
rg "ReferenceDataService\.get_active_reference_data|reference_data: dict" backend/app/domain/astrology backend/app/services/natal
rg "PLANET_KEYWORDS|SIGN_RULERS|DEFAULT_ORB|ASPECT_WEIGHTS|HOUSE_MEANINGS" backend/app/domain/astrology backend/app/services/natal
rg "UNKNOWN_SIGN|EXACT_ORB_DEG|TIGHT_RATIO|MODERATE_RATIO" backend/app/domain/astrology backend/app/services/natal
rg "SwissEph.*simplified|simplified.*SwissEph|calculation_engine.*simplified" backend/app/domain/astrology backend/app/services/natal
rg "domain\.prediction|app\.domain\.prediction" backend/app/domain/astrology
```

## 22. Regression Risks

- API natal modifiee silencieusement.
- DB incomplete maintenant bloquante.
- `dict` metier reintroduit par helper.
- JSON DB parse dans domain.
- preparation LLM dans `domain/astrology`.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not create progressive migration, feature flag, double run, shim, alias or fallback.
- Use `dataclass(frozen=True, slots=True)` for core runtime contracts.
- Keep `dict` only for JSON output, debug snapshots, validated HTTP payloads or metadata.
- Treat `360`, `180`, modulo normalization, epsilon and iteration caps as technical constants.

## 24. References

- `backend/app/domain/astrology`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/infra`
- `_condamad/stories/regression-guardrails.md`
- `.agents/skills/condamad-dev-review-fix-story/SKILL.md`
