# Story CS-162 heriter-regles-orbes-systemes-astrologiques: Heriter les regles d'orbes des systemes astrologiques

Status: ready-to-dev

## 1. Objective

Mettre en oeuvre l'heritage explicite des systemes astrologiques pour les regles d'orbes.
`hellenistic` et `medieval` heritent de `traditional` sans copie physique complete, et les overrides locaux restent prioritaires.

## 2. Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-14 sur l'heritage `astral_systems` pour `astral_aspect_orb_rules`.
- Reason for change: le modele `astral_aspect_orb_rules` est correct, mais le seed actuel deploie `copy_rules_from` en lignes dupliquees pour les systemes enfants.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: referentiels astrologiques backend + resolution `domain/astrology` des orbes.
- In scope:
  - ajouter `astral_systems.inherits_from_system_id` nullable FK vers `astral_systems.id`;
  - seed `modern -> null`, `traditional -> null`, `hellenistic -> traditional`, `medieval -> traditional`;
  - reduire `docs/recherches astro/astral_aspect_orb_rules.json` pour ne plus copier les regles `hellenistic` et `medieval`;
  - adapter le resolver d'orbes pour charger la chaine locale puis parente;
  - ajouter un guard anti-cycle d'heritage;
  - mettre a jour `tables-aspects-et-roles.md`, `tables-maisons-et-roles.md` et `tables-planetes-et-roles.md`.
- Out of scope:
  - changer les colonnes de `astral_aspect_orb_rules`;
  - ajouter des planetes, points, aspects ou maisons;
  - modifier les dignites planetaires ou profils editoriaux de maisons hors documentation de l'heritage;
  - changer le scoring daily, `orb_multiplier` ou les categories produit.
- Explicit non-goals:
  - ne pas recopier les regles `traditional` dans `hellenistic` ou `medieval`;
  - ne pas creer de fallback silencieux vers `modern`;
  - ne pas utiliser `copy_rules_from` comme mecanisme runtime acceptable;
  - preserver `RG-091`, `RG-092`, `RG-093`, `RG-094`, `RG-095` et `RG-096`.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: registry-catalog-refactor
- Archetype reason: la story modifie un referentiel stable (`astral_systems`), son seed, ses regles derivees et les guards documentaires associes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - `modern` et `traditional` gardent leurs orbes resolus actuels;
  - `hellenistic` et `medieval` resolvent les memes orbes que `traditional` quand aucune regle locale ne matche;
  - une regle locale enfant gagne toujours contre une regle parente;
  - le tri logique est `inheritance_depth` ascendant, `priority` descendant, `specificity` descendant;
  - un cycle d'heritage doit echouer explicitement.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: une regle existante `hellenistic` ou `medieval` diverge intentionnellement de `traditional` et doit etre conservee comme override local.
- Deletion constraints:
  - autorise uniquement la suppression des copies physiques heritees et du depliage `copy_rules_from`;
  - interdit la suppression de colonnes existantes dans `astral_aspect_orb_rules`;
  - interdit la suppression des regles sources `modern` et `traditional`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le comportement depend du schema migre, du seed DB et du resolver runtime. |
| Baseline Snapshot | yes | Les comptages et orbes resolus doivent etre compares avant/apres. |
| Ownership Routing | yes | L'heritage referentiel reste dans les modeles/seeds/repositories, la resolution metier reste dans `domain/astrology`. |
| Allowlist Exception | yes | Les seuls ecarts admis sont des overrides locaux exacts, audites et testes. |
| Contract Shape | yes | La forme SQL de `astral_systems` et du payload de reference doit etre explicite. |
| Batch Migration | yes | Le changement traverse migration, seed JSON, repository/payload, resolver et documentation. |
| Reintroduction Guard | yes | Le retour de copies completes `hellenistic` ou `medieval` doit echouer. |
| Persistent Evidence | yes | Les preuves de comptage et d'orbes avant/apres doivent etre conservees. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - schema reflechi Alembic head pour `astral_systems.inherits_from_system_id`;
  - seed DB et payload `ReferenceRepository.get_reference_data`;
  - tests du resolver `resolve_orb` et `calculate_major_aspects`.
- Secondary evidence:
  - scans cibles sur `copy_rules_from`, comptage des groupes JSON et docs.
- Static scans alone are not sufficient for this story because:
  - un JSON non duplique peut encore produire des lignes dupliquees si le seed deploie l'heritage au lieu de le stocker dans `astral_systems`.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/CS-162-heriter-regles-orbes-systemes-astrologiques/orb-rules-baseline-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-162-heriter-regles-orbes-systemes-astrologiques/orb-rules-baseline-after.md`
- Expected invariant:
  - `modern` et `traditional` conservent leurs resolutions;
  - `hellenistic` et `medieval` obtiennent les orbes `traditional` par heritage;
  - sans override enfant, la cible physique est 79 regles par `reference_version`;
  - le detail attendu est `modern = 39`, `traditional = 40`, enfants = `0`.

## 4d. Ownership Routing Rule

Use when the story moves or protects responsibilities across API, services, domain, infra, or core owners.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Colonne et relation `inherits_from_system_id` | `backend/app/infra/db/models/reference.py` + migration Alembic | `domain/astrology` |
| Seed des systemes et des regles physiques | `backend/app/services/prediction/reference_seed_service.py` + JSON documentaire | resolver runtime |
| Resolution locale puis heritee des orbes | `backend/app/domain/astrology/calculators/aspects.py` | repository SQL ou API |
| Exposition des regles et metadonnees de systeme | `backend/app/infra/db/repositories/reference_repository.py` | composants UI ou calculateur |
| Doctrine documentaire | `docs/recherches astro/*.md` | commentaires de code seuls |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `docs/recherches astro/astral_aspect_orb_rules.json` | overrides locaux enfants | Divergence explicite au parent `traditional`. | Permanente si testee et documentee. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

Use when the story touches an API, HTTP error, payload, export, DTO, OpenAPI contract, generated client, or frontend type.

- Contract type:
  - SQL reference catalog and reference payload.
- Fields:
  - `astral_systems.id`: integer primary key.
  - `astral_systems.name`: stable system code.
  - `astral_systems.inherits_from_system_id`: nullable self-FK.
  - `aspect_orb_rules[*].reference_version_id`: reference version owner.
  - `aspect_orb_rules[*].astral_system_id`: physical rule owner system.
  - `aspect_orb_rules[*].aspect_id`: referenced aspect.
  - `aspect_orb_rules[*].system_code`: owner system for a physical rule.
  - `aspect_orb_rules[*].aspect_code`: aspect code.
  - `aspect_orb_rules[*].calculation_context`: context selector.
  - `aspect_orb_rules[*].source_body_type`: source body category.
  - `aspect_orb_rules[*].source_planet_id`: optional source planet FK.
  - `aspect_orb_rules[*].source_point_code`: optional source point code.
  - `aspect_orb_rules[*].target_body_type`: target body category.
  - `aspect_orb_rules[*].target_planet_id`: optional target planet FK.
  - `aspect_orb_rules[*].target_point_code`: optional target point code.
  - `aspect_orb_rules[*].orb_deg`: resolved override value.
  - `aspect_orb_rules[*].priority`: matching priority.
  - `aspect_orb_rules[*].is_enabled`: rule activation flag.
  - `aspect_orb_rules[*].micro_note`: optional note.
- Required fields:
  - `id`, `name`, and all existing physical `aspect_orb_rules` fields.
- Optional fields:
  - `inherits_from_system_id`, `inherits_from_system_code`, point codes, planet codes, and `micro_note`.
- Status codes:
  - none; no HTTP route or response status changes.
- Serialization names:
  - `system_code` remains unchanged; optional inheritance metadata uses `inherits_from_system_code` if exposed.
- Frontend type impact:
  - none expected.
- Generated contract impact:
  - none expected; if an existing schema covers reference data, add nullable inheritance metadata without removing existing fields.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | `astral_systems(id, name)` | self-FK d'heritage | modeles/migration | migration tests | FK reflechie | SQLite incompatible |
| 2 | `copy_rules_from` deplié | `inherits_from` + `rules: []` | seed + JSON | seed tests | scan zero-hit | divergence enfant |
| 3 | filtre systeme courant | chaine `[local, parent]` | resolver | tests orbes | local > parent | chaine absente |
| 4 | docs aspects seules | doctrine dans 3 docs | docs | scans docs | section presente | conflit actif |

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Baseline avant | `_condamad/stories/CS-162-heriter-regles-orbes-systemes-astrologiques/orb-rules-baseline-before.md` | Comptages et orbes avant. |
| Baseline apres | `_condamad/stories/CS-162-heriter-regles-orbes-systemes-astrologiques/orb-rules-baseline-after.md` | Comptages et orbes apres. |
| Guard anti-duplication | `_condamad/stories/CS-162-heriter-regles-orbes-systemes-astrologiques/no-duplicated-inherited-orb-rules.md` | Preuve anti-copie. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route, field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- `copy_rules_from` dans `docs/recherches astro/astral_aspect_orb_rules.json`;
- 40 regles physiques `hellenistic` identiques a `traditional`;
- 40 regles physiques `medieval` identiques a `traditional`;
- cycle `astral_systems` A -> B -> A.

Guard evidence:

- Evidence profile: `reintroduction_guard`;
  `pytest -q app/tests/unit/test_aspect_orb_overrides.py app/tests/integration/test_seed_31_prediction_v2.py`.

## 4j. Source Finding Closure

- Closure status: not applicable
- Reason: story is not sourced from an audit finding.

## 5. Current State Evidence

- Evidence 1: `backend/app/infra/db/models/reference.py` - `AstralSystemModel` expose seulement `id` et `name`.
- Evidence 2: `backend/app/services/prediction/reference_seed_service.py` - `_resolve_aspect_orb_rule_groups` deploie `copy_rules_from` en regles physiques.
- Evidence 3: `backend/app/domain/astrology/calculators/aspects.py` - `resolve_orb` filtre uniquement `system_code == normalized_system_code`.
- Evidence 4: `backend/app/tests/unit/test_reference_data_service.py` - le payload attend encore `159` regles par version.
- Evidence 5: `docs/recherches astro/tables-aspects-et-roles.md` - les exceptions sont documentees, pas l'heritage.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage; `RG-091` a `RG-096` touchent les referentiels astrologiques voisins.

## 6. Target State

After implementation:

- `astral_systems` porte une FK nullable `inherits_from_system_id` vers lui-meme.
- `hellenistic` et `medieval` heritent de `traditional`; `modern` et `traditional` sont racines.
- `astral_aspect_orb_rules` contient les regles physiques `modern` et `traditional`, plus seulement d'eventuels overrides locaux enfants.
- Le resolver charge les regles locales puis les regles heritees, sans cycle possible.
- Les trois documents de recherche expliquent l'heritage et interdisent la recopie physique complete des regles heritees.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-091` - `astro_characteristics` ne doit pas redevenir une source d'overrides d'orbes.
  - `RG-092` - les referentiels structurels astrologiques restent stables; la nouvelle colonne n'ajoute pas `reference_version_id`.
  - `RG-093` - les profils et maitrises des signes ne sont pas touches par l'heritage d'orbes.
  - `RG-094` - la projection runtime des maitres de maisons ne doit pas etre changee.
  - `RG-095` - `domain/astrology` ne doit pas importer `domain/prediction` pour resoudre l'heritage.
  - `RG-096` - les contrats de force maison restent hors scope.
  - `RG-097` - cette story etablit l'invariant anti-duplication des regles d'orbes heritees.
- Non-applicable invariants:
  - `RG-001` a `RG-090` - surfaces API/frontend/LLM/prediction non modifiees.
- Required regression evidence:
  - tests Alembic/modeles;
  - tests unitaires du resolver;
  - tests seed/reference data;
  - scans cibles sur `copy_rules_from`, `astro_characteristics`, imports prediction depuis astrology.
- Allowed differences:
  - nombre physique de lignes `astral_aspect_orb_rules` reduit a environ `79 * reference_version_count`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `astral_systems` ajoute une self-FK nullable. | `pytest -q app/tests/integration/test_reference_data_migrations.py`. |
| AC2 | Le seed cree la carte d'heritage systeme exacte. | `pytest -q app/tests/integration/test_seed_31_prediction_v2.py`. |
| AC3 | Le JSON actif d'orbes n'a plus `copy_rules_from`. | `rg -n "copy_rules_from" "../docs/recherches astro/astral_aspect_orb_rules.json"`. |
| AC4 | Le seed produit exactement 79 regles physiques sans override enfant. | `pytest -q app/tests/integration/test_seed_31_prediction_v2.py`. |
| AC5 | `modern` garde ses regles propres. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC6 | `traditional` garde ses regles propres. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC7 | `hellenistic` herite de `traditional`. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC8 | `medieval` herite de `traditional`. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC9 | Une regle locale enfant gagne contre une regle parente. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC10 | Une priorite plus elevee gagne a profondeur egale. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC11 | Une regle plus specifique gagne a priorite egale. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC12 | Un cycle d'heritage leve une erreur explicite. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC13 | Le fallback `default_orb_deg` reste actif. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC14 | Une regle desactivee ne matche pas. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC15 | `natal` reste symetrique. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC16 | `transit_to_natal` reste directionnel. | `pytest -q app/tests/unit/test_aspect_orb_overrides.py`. |
| AC17 | Le seed refuse une copie complete des regles heritees dans les enfants. | `pytest -q app/tests/integration/test_seed_31_prediction_v2.py`. |
| AC18 | Le doc aspects contient le titre d'heritage. | `rg -n "Héritage des systèmes astrologiques" "../docs/recherches astro/tables-aspects-et-roles.md"`. |
| AC19 | Le doc maisons contient le titre d'heritage. | `rg -n "Héritage des systèmes astrologiques" "../docs/recherches astro/tables-maisons-et-roles.md"`. |
| AC20 | Le doc planetes contient le titre d'heritage. | `rg -n "Héritage des systèmes astrologiques" "../docs/recherches astro/tables-planetes-et-roles.md"`. |
| AC21 | Le doc aspects mappe `hellenistic` vers `traditional`. | `rg -n "hellenistic.*traditional" "../docs/recherches astro/tables-aspects-et-roles.md"`. |
| AC22 | Le doc aspects mappe `medieval` vers `traditional`. | `rg -n "medieval.*traditional" "../docs/recherches astro/tables-aspects-et-roles.md"`. |
| AC23 | Le doc maisons mappe `hellenistic` vers `traditional`. | `rg -n "hellenistic.*traditional" "../docs/recherches astro/tables-maisons-et-roles.md"`. |
| AC24 | Le doc maisons mappe `medieval` vers `traditional`. | `rg -n "medieval.*traditional" "../docs/recherches astro/tables-maisons-et-roles.md"`. |
| AC25 | Le doc planetes mappe `hellenistic` vers `traditional`. | `rg -n "hellenistic.*traditional" "../docs/recherches astro/tables-planetes-et-roles.md"`. |
| AC26 | Le doc planetes mappe `medieval` vers `traditional`. | `rg -n "medieval.*traditional" "../docs/recherches astro/tables-planetes-et-roles.md"`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer le baseline courant des regles d'orbes (AC: AC2, AC4, AC5, AC6, AC7, AC8, AC17)
  - [ ] Ecrire `orb-rules-baseline-before.md` avec comptages par systeme et exemples d'orbes modern/traditional/hellenistic/medieval.
  - [ ] Noter le nombre actuel attendu `159` par version et la presence de `copy_rules_from`.

- [ ] Task 2 - Migrer `astral_systems` et le modele (AC: AC1, AC2)
  - [ ] Ajouter une migration Alembic nullable self-FK `inherits_from_system_id`.
  - [ ] Mettre a jour `AstralSystemModel` avec relation parent/enfants et docstring francaise.
  - [ ] Adapter `_ensure_astral_systems` pour renseigner les parents sans changer les ids existants.

- [ ] Task 3 - Reduire et synchroniser les rules d'orbes (AC: AC2, AC3, AC4, AC17)
  - [ ] Remplacer `copy_rules_from` par `inherits_from` dans le JSON documentaire.
  - [ ] Supprimer le depliage `_resolve_aspect_orb_rule_groups` comme source de duplication physique.
  - [ ] Adapter les compteurs vers `modern = 39`, `traditional = 40`, enfants = `0` sans override.
  - [ ] Ajouter un guard qui refuse une copie complete des regles `traditional` dans les enfants.

- [ ] Task 4 - Adapter l'exposition reference data et le resolver (AC: AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16)
  - [ ] Fournir au resolver la chaine d'heritage systeme depuis le payload ou une structure derivee deterministe.
  - [ ] Trier comme `(-inheritance_depth, priority, specificity)` avec local a profondeur `0`.
  - [ ] Ajouter le guard anti-cycle avec erreur explicite.
  - [ ] Preserver la symetrie `natal` et la directionnalite `transit_to_natal`.

- [ ] Task 5 - Mettre a jour les tests et preuves persistantes (AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10, AC11, AC12, AC13, AC14, AC15, AC16, AC17)
  - [ ] Ajouter ou adapter les tests listés dans les AC.
  - [ ] Ecrire `orb-rules-baseline-after.md` et `no-duplicated-inherited-orb-rules.md`.
  - [ ] Verifier les scans anti-retour.

- [ ] Task 6 - Mettre a jour la documentation de recherche (AC: AC18, AC19, AC20, AC21, AC22, AC23, AC24, AC25, AC26)
  - [ ] Ajouter `Héritage des systèmes astrologiques` dans `tables-aspects-et-roles.md`.
  - [ ] Ajouter la meme doctrine resumee dans `tables-maisons-et-roles.md`.
  - [ ] Ajouter la meme doctrine resumee dans `tables-planetes-et-roles.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AstralSystemModel` pour porter l'heritage, pas une nouvelle table;
  - `AstralAspectOrbRuleModel` pour les exceptions physiques, sans changer ses colonnes metier;
  - `_rule_matches_bodies`, `_rule_effective_priority` et `_rule_specificity_score` pour la resolution;
  - les fixtures DB canoniques de tests, sans import statique direct de `SessionLocal`.
- Do not recreate:
  - une table d'heritage separee;
  - une copie `hellenistic` ou `medieval` des regles `traditional`;
  - un resolver d'orbes concurrent dans un autre package.
- Shared abstraction allowed only if:
  - elle evite une duplication effective entre seed, repository et resolver, et reste bornee au domaine astrologique.

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

- `copy_rules_from` dans `docs/recherches astro/astral_aspect_orb_rules.json`;
- `astro_characteristics` comme source d'orbes;
- import `app.domain.prediction` ou `app.services.prediction` depuis `backend/app/domain/astrology`;
- nouvelle colonne `reference_version_id` sur `astral_systems`;
- copie complete des regles `traditional` dans les systemes enfants.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Taxonomie des systemes astrologiques | `astral_systems` / `AstralSystemModel` | JSON runtime local, enums dupliques |
| Exceptions d'orbes physiques | `astral_aspect_orb_rules` | `astral_aspects`, `astral_aspect_profiles`, `astro_characteristics` |
| Resolution des orbes | `backend/app/domain/astrology/calculators/aspects.py` | API, repository, scoring prediction |
| Documentation de doctrine | `docs/recherches astro/tables-*-et-roles.md` | commentaires isoles ou story seule |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/tests/unit/test_aspect_orb_overrides.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/unit/test_reference_data_service.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `docs/recherches astro/astral_aspect_orb_rules.json`
- `docs/recherches astro/tables-aspects-et-roles.md`
- `docs/recherches astro/tables-maisons-et-roles.md`
- `docs/recherches astro/tables-planetes-et-roles.md`

## 19. Expected Files to Modify

Likely files:

- `backend/app/infra/db/models/reference.py` - ajouter la self-FK et les relations.
- `backend/migrations/versions/*.py` - ajouter une revision Alembic pour l'heritage des systemes.
- `backend/app/services/prediction/reference_seed_service.py` - seed systemes, comptages, suppression du depliage de copies.
- `backend/app/infra/db/repositories/reference_repository.py` - exposer les donnees d'heritage utiles au resolver.
- `backend/app/domain/astrology/calculators/aspects.py` - resolution par chaine d'heritage et guard anti-cycle.
- `docs/recherches astro/astral_aspect_orb_rules.json` - remplacer copies par `inherits_from` et `rules: []`.
- `docs/recherches astro/tables-aspects-et-roles.md` - section d'heritage et nouveau comptage.
- `docs/recherches astro/tables-maisons-et-roles.md` - rappel du referentiel commun `astral_systems`.
- `docs/recherches astro/tables-planetes-et-roles.md` - rappel du referentiel commun `astral_systems`.

Likely tests:

- `backend/app/tests/unit/test_aspect_orb_overrides.py` - resolver, override, cycle, symetrie/direction.
- `backend/app/tests/unit/test_prediction_reference_repository.py` - forme modele `astral_systems`.
- `backend/app/tests/unit/test_reference_data_service.py` - taille payload et absence de duplication.
- `backend/app/tests/integration/test_seed_31_prediction_v2.py` - seed et comptages.
- `backend/app/tests/integration/test_reference_data_migrations.py` - schema Alembic head et FK.

Files not expected to change:

- `frontend/` - aucun impact UI.
- `backend/app/domain/prediction/**` - aucun changement de scoring produit.
- `backend/app/services/chart/json_builder.py` - aucune modification attendue du JSON chart.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_aspect_orb_overrides.py app/tests/unit/test_prediction_reference_repository.py
pytest -q app/tests/unit/test_reference_data_service.py app/tests/integration/test_seed_31_prediction_v2.py
pytest -q app/tests/integration/test_reference_data_migrations.py
rg -n "copy_rules_from" "..\docs\recherches astro\astral_aspect_orb_rules.json"
rg -n "Héritage des systèmes astrologiques" "..\docs\recherches astro\tables-aspects-et-roles.md"
rg -n "Héritage des systèmes astrologiques" "..\docs\recherches astro\tables-maisons-et-roles.md"
rg -n "Héritage des systèmes astrologiques" "..\docs\recherches astro\tables-planetes-et-roles.md"
rg -n "hellenistic.*traditional" "..\docs\recherches astro\tables-aspects-et-roles.md"
rg -n "medieval.*traditional" "..\docs\recherches astro\tables-aspects-et-roles.md"
rg -n "hellenistic.*traditional" "..\docs\recherches astro\tables-maisons-et-roles.md"
rg -n "medieval.*traditional" "..\docs\recherches astro\tables-maisons-et-roles.md"
rg -n "hellenistic.*traditional" "..\docs\recherches astro\tables-planetes-et-roles.md"
rg -n "medieval.*traditional" "..\docs\recherches astro\tables-planetes-et-roles.md"
rg -n "astro_characteristics|AstroCharacteristicModel" app tests
rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"
```

Expected scan results:

- `copy_rules_from` scan: zero hits.
- `app.domain.prediction|app.services.prediction` under `app/domain/astrology`: zero hits.
- `astro_characteristics` scan: only existing guard/test references allowed by `RG-091`.

## 22. Regression Risks

- Risk: les systemes enfants perdent leurs orbes si la chaine d'heritage n'est pas exposee au calculateur.
  - Guardrail: tests `hellenistic` et `medieval` resolvent une regle presente seulement en `traditional`.
- Risk: le seed continue a redupliquer physiquement les regles malgre un JSON plus propre.
  - Guardrail: test DB par systeme et guard anti-copie complete.
- Risk: une regle locale enfant est ignoree au profit du parent.
  - Guardrail: test `test_child_rule_overrides_parent_rule`.
- Risk: cycle de reference bloquant ou boucle infinie.
  - Guardrail: test cycle rejected avec erreur explicite.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  compatibility, legacy, migration-only, shim, alias, TODO, or hidden residual work.
- Respecter l'AGENTS.md: toute commande Python doit etre executee apres `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `backend/app/infra/db/models/reference.py` - proprietaire SQLAlchemy de `astral_systems`.
- `backend/app/services/prediction/reference_seed_service.py` - seed actuel et comptages.
- `backend/app/domain/astrology/calculators/aspects.py` - resolver d'orbes a adapter.
- `docs/recherches astro/astral_aspect_orb_rules.json` - source documentaire des exceptions d'orbes.
- `docs/recherches astro/tables-aspects-et-roles.md` - documentation principale des aspects et orbes.
- `docs/recherches astro/tables-maisons-et-roles.md` - documentation des maisons utilisant `astral_systems`.
- `docs/recherches astro/tables-planetes-et-roles.md` - documentation des planetes et dignites utilisant `astral_systems`.
