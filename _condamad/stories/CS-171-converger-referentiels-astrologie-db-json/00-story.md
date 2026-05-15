# Story CS-171 converger-referentiels-astrologie-db-json: Converger les referentiels astrologiques DB et JSON

Status: ready-to-review

## 1. Objective

Supprimer les doublons actifs de referentiels astrologiques backend.
Les sources canoniques sont `docs/recherches astro/*.json` et les tables `astral_*` migrees.
La correction repare `astral_aspect_families`, supprime les constantes redondantes,
et adapte les tests sans chemin legacy, alias, fallback ou compatibilite.

## 2. Trigger / Source

- Source type: audit
- Source reference: audits Codex utilisateur du 2026-05-14 sur `backend/app/domain/astrology` et comparaison avec `backend/horoscope.db`.
- Reason for change: `astral_aspect_families` est vide en base active alors que `astral_aspects.family` contient `1/2/3`.
  `ReferenceRepository.get_reference_data` ne retourne donc aucun aspect via son join.
  `reference_seed_service.py` cherche aussi `astral_aspect_family.json` au lieu du fichier pluriel canonique.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend` referentiels astrologiques persistants et chargement de reference.
- In scope:
  - Corriger le seed de `astral_aspect_families` depuis `docs/recherches astro/astral_aspect_families.json`.
  - Supprimer les constantes applicatives redondantes portant des valeurs de referentiel astrologique quand la source canonique existe en JSON/DB.
  - Converger les helpers calculatoires dupliques du domaine astrology vers un owner unique quand ils ne sont pas des referentiels persistants.
  - Adapter les tests backend pour verifier la DB, les loaders JSON et le payload `ReferenceDataService`.
  - Ajouter des gardes anti-retour pour le fichier singulier `astral_aspect_family.json`, les tuples hardcodes de referentiels et les helpers dupliques audites.
- Out of scope:
  - Changer les regles astrologiques metier, les valeurs contenues dans les JSON, ou les schemas publics du theme natal.
  - Modifier le frontend.
  - Reconcevoir le moteur SwissEph ou les calculs mathematiques purs.
  - Ajouter de nouveaux referentiels astrologiques.
- Explicit non-goals:
  - Ne pas creer de shim, alias, fallback de fichier, support transitoire du nom singulier, ou re-export.
  - Ne pas garder des constantes redondantes "pour compatibilite".
  - Ne pas contourner `RG-092`: les referentiels structurels restent non versionnes.
  - Ne pas contourner `RG-095`: `backend/app/domain/astrology/**` ne doit pas importer prediction.
  - Ne pas contourner `RG-097`: l'heritage des regles d'orbes reste via `astral_systems.inherits_from_system_id`.
  - Ne pas contourner `RG-098` a `RG-105`: le runtime et l'interpretation des aspects restent proprietaires de leurs contrats, sans logique prediction.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: dead-code-removal
- Archetype reason: la story supprime des constantes, tuples, imports et chemins de fichiers non canoniques qui dupliquent les referentiels JSON/DB.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le payload de reference doit passer de "0 aspect via join casse" a "20 aspects avec famille et `default_orb_deg`".
  - Les valeurs astrologiques canoniques ne changent pas; seule leur source active change.
  - Les tests doivent etre modifies pour exiger la source canonique actuelle, pas pour accepter l'ancien doublon.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une constante candidate est un algorithme pur non derivable de JSON/DB,
  ou si une surface externe consomme `astral_aspect_family.json`.
- Consumer migration rule:
  - Les items legacy/removables sont supprimes sans wrapper, alias, fallback ou re-export.
  - Les consommateurs actifs doivent etre migres vers l'owner canonique existant ou vers un helper unique classe `canonical-active`.

## 4a. Required Contracts

Every story must persist the contracts selected from the archetype and story scope.

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La correction touche le comportement de persistence et le payload charge depuis DB. |
| Baseline Snapshot | yes | Le bug doit etre prouve par un etat avant/apres de la DB et du payload reference. |
| Ownership Routing | yes | Les responsabilites JSON source, seed service, repository SQL et domaine runtime doivent rester separees. |
| Allowlist Exception | no | Aucune exception, alias, shim ou fallback n'est autorise. |
| Contract Shape | no | Aucun contrat API/DTO/frontend n'est modifie; le payload reference interne conserve ses champs. |
| Batch Migration | yes | La convergence touche plusieurs surfaces independantes: familles d'aspects, valeurs de reference, tests/gardes. |
| Reintroduction Guard | yes | Les anciens doublons et le nom de fichier singulier ne doivent pas revenir. |
| Persistent Evidence | yes | Les preuves DB/payload et la classification des suppressions doivent etre conservees dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - DB schema after alembic migration: `sqlite3 backend/horoscope.db ".schema astral_aspect_families"` and `sqlite3 backend/horoscope.db "PRAGMA foreign_key_check;"`.
  - DB runtime query result: `sqlite3 backend/horoscope.db "SELECT COUNT(*) FROM astral_aspects a JOIN astral_aspect_families f ON f.id = a.family;"`.
  - Loaded runtime repository payload: pytest assertion around `ReferenceDataService.get_active_reference_data`.
  - AST guard: `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py`.
- Secondary evidence:
  - Scans cibles `rg` sur les noms de fichiers legacy, tuples hardcodes et constantes supprimees.
  - Garde AST owner-aware sur les helpers conserves: une seule definition owner autorisee par helper.
  - Tests unitaires/integration de repository et migrations.
- Static scans alone are not sufficient for this story because:
  - Le bug observe existe au runtime DB: la table `astral_aspect_families` vide casse le join meme si le code contient les bonnes strings.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `reference-runtime-before.md` avec les sorties `sqlite3` prouvant familles vides,
    references invalides et payload aspects vide.
- Comparison after implementation:
  - `reference-runtime-after.md` avec familles `3`, references invalides `0`,
    join aspects `20` et payload aspects `20`.
- Expected invariant:
  - Les codes des 20 aspects, les 12 signes, les 10 planetes, les 4 systemes de maisons et les 4 systemes astrologiques restent identiques aux JSON/DB canoniques.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Source documentaire des familles d'aspects | `docs/recherches astro/astral_aspect_families.json` | tuple hardcode dans repository/service/test |
| Seed applicatif des referentiels prediction | `backend/app/services/prediction/reference_seed_service.py` | `backend/app/domain/astrology/**` |
| Lecture SQL des donnees de reference | `backend/app/infra/db/repositories/reference_repository.py` | `backend/app/domain/astrology/**` |
| Invariants astrologiques runtime purs | `backend/app/domain/astrology/**` | `backend/app/services/prediction/**` |
| Migrations Alembic | `backend/migrations/versions/**` | scripts ad hoc non migres |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Aspect families | fichier singulier + tuples | JSON pluriel + DB | seed/migrations/tests | integration | scan zero-hit | usage externe |
| Stable catalogs | tuples aspects/signes/planetes | JSON ou DB | repository/seeds | tests repository | scan zero-hit | algorithme pur |
| Domain constants | taxonomies locales redondantes | DB/JSON ou helper derive unique | `domain/astrology` | tests astrology | scan symboles supprimes | stop si RG casse |
| Calculation helpers | normalisation angle, signe, SwissEph | owner unique `domain/astrology` | providers/calculators | tests calcul | guard owner-aware | changement numerique |
| Interpretation helpers | listes profils | owner interpretation | builders/facts | tests interpretation | guard owner-aware | contrat RG casse |

Closure map:

- Total affected surface: referentiels astrologiques backend dupliques entre docs JSON, DB `astral_*`, repositories, services de seed, domaine astrology et tests.
- Batches included in this story: tous les batches ci-dessus.
- Batches intentionally deferred: aucune dans ce domaine.
- Stop condition for the source finding: aucun doublon actif de valeur/helper de referentiel astrologique
  ne reste hors owner canonique. Toute valeur ou helper conserve est classe comme algorithme pur ou owner unique.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Baseline runtime DB/payload | `_condamad/stories/CS-171-converger-referentiels-astrologie-db-json/reference-runtime-before.md` | Prouver le bug et l'etat initial. |
| Resultat runtime DB/payload | `_condamad/stories/CS-171-converger-referentiels-astrologie-db-json/reference-runtime-after.md` | Prouver la correction DB et payload. |
| Classification des suppressions | `astrology-duplication-audit.md` | Lister chaque constante, tuple, fichier ou helper supprime, garde, ou bloque. |

## 4i. Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- `docs/recherches astro/astral_aspect_family.json`
- string/import/path `astral_aspect_family.json`
- tuples actifs `ASPECT_FAMILY_ROWS`, `ASPECT_ROWS`, `DEFAULT_ASPECT_ORBS` comme source seed/repository
- constantes redondantes `MAJOR_ASPECTS`, `LUMINARIES`, `PLANET_CLASS_BY_CODE`,
  `ANGLE_CODES`, `ANGULAR_HOUSES`, `SUCCEDENT_HOUSES`,
  `DEFAULT_TRADITIONAL_SIGN_RULERSHIPS`, `_HOUSE_SYSTEM_CODES`
- helpers dupliques de calcul `normalize_360`, `_norm360`, `_normalize_longitude`,
  `_sign_from_longitude`, `_get_swe_module`, `_profile_list`, `_require_list`

Deterministic guard sources:

- importable Python modules and AST guard test over backend Python modules.
- Targeted forbidden symbol scan over `backend/app`, `backend/tests`, `docs/recherches astro`.

Guard evidence:

- Evidence profile: `reintroduction_guard`;
  `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py`
  checks file name, forbidden duplicate catalog constants and helper owner uniqueness.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: audits Codex du 2026-05-14 sur DRY `backend/app/domain/astrology` + comparaison DB `backend/horoscope.db`
- Closure proof required: artefacts before/after, tests repository/seed/migration,
  scans zero-hit pour surfaces supprimees, garde owner-aware pour helpers conserves.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

Full closure forbids `PASS with limitation`, broad allowlists, wildcard exceptions,
unclassified fallback, compatibility, legacy, migration-only, shim, alias, TODO,
and hidden residual in-domain work.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `docs/recherches astro/astral_aspect_families.json` - fichier canonique present avec `{"family": ["major", "minor", "advanced"]}`.
- Evidence 2: `backend/app/services/prediction/reference_seed_service.py` - le service cherche encore `astral_aspect_family.json` au singulier.
- Evidence 3: `backend/horoscope.db` - `astral_aspect_families` contient 0 ligne, `astral_aspects` contient 20 lignes avec `family=1/2/3`, et `invalid_aspect_family_refs=20`.
- Evidence 4: `backend/app/infra/db/repositories/reference_repository.py` - contient des tuples
  qui dupliquent les catalogues DB/JSON.
- Evidence 5: plusieurs fichiers `backend/app/domain/astrology/**` redifinissent des taxonomies
  deja presentes ailleurs.
- Evidence 6: plusieurs fichiers `backend/app/domain/astrology/**` redifinissent des helpers
  de calcul ou d'adaptation deja presents ailleurs: normalisation 360, signe depuis longitude,
  loader SwissEph et helpers de listes d'interpretation.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage;
  `RG-092`, `RG-095`, `RG-097`, `RG-098`, `RG-100` a `RG-105` s'appliquent.

## 6. Target State

After implementation:

- `astral_aspect_families` est seedee depuis `docs/recherches astro/astral_aspect_families.json`.
- `ReferenceDataService.get_active_reference_data` retourne 20 aspects avec `family` et `default_orb_deg`.
- Les valeurs de catalogues astrologiques ne sont plus recopiees dans les repositories, services, domaine ou tests comme sources actives.
- Les helpers non persistants audites ont un owner unique; aucune variante locale active ne reste dans providers, calculators ou interpretation.
- Les dernieres structures issues des migrations/stories recentes priment sur tout ancien catalogue local ou test historique:
  `astral_aspect_definitions`, `astral_aspect_orb_rules`, runtime aspects RG-097 a RG-105.
- Les tests ne valident plus l'ancien chemin singulier ni les constantes supprimees.
- Une garde deterministe bloque la reintroduction des doublons de catalogue et de helpers.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-092` - les referentiels structurels astrologiques restent stables et non versionnes.
  - `RG-095` - le domaine astrology ne doit pas importer prediction pendant la convergence.
  - `RG-097` - l'heritage des regles d'orbes ne doit pas redevenir une copie physique.
  - `RG-098` - les contrats runtime des aspects restent dans `domain/astrology`.
  - `RG-100` - l'interpretation editoriale des aspects ne doit pas introduire de fallback texte.
  - `RG-101` - les aspects dominants/inter-chart reutilisent les referentiels existants.
  - `RG-102` - la semantique des aspects reste pure.
  - `RG-103` - les modifiers et poids restent separes par owner.
  - `RG-104` - les patterns restent sous runtime astrology.
  - `RG-105` - prediction ne choisit pas la semantique des aspects.
  - `RG-106` - les calculateurs astrology consomment des contrats types sans anciens tuples, champs legacy d'orbes, constantes recopiees ni fallback silencieux.
- Non-applicable invariants:
  - `RG-001` a `RG-090` - ces invariants protegent API, frontend, LLM, Stripe ou prediction hors referentiels astrology touches par cette story.
  - `RG-094` - la projection publique des maitres de maisons n'est pas modifiee.
- Required regression evidence:
  - Tests repository/seed/migration, scans zero-hit des surfaces supprimees,
    garde owner-aware helpers, artefacts before/after DB/payload.
- Allowed differences:
  - Le payload reference passe de 0 aspect a 20 aspects; aucune autre difference de valeur catalogue n'est autorisee.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le JSON pluriel seed les familles; le nom singulier disparait. | `pytest -q app/tests/integration/test_seed_31_prediction_v2.py` + `rg` zero-hit. |
| AC2 | L'integrite DB aspect-famille est valide. | `alembic` evidence + `pytest -q app/tests/integration/test_reference_data_migrations.py`. |
| AC3 | `ReferenceDataService` expose le set canonique des aspects. | `pytest -q app/tests/unit/test_prediction_reference_repository.py`. |
| AC4 | Les tuples catalogues redondants audites sont supprimes du code actif. | Evidence profile: `repo_wide_negative_scan`; AST guard pytest + scan. |
| AC5 | Toute constante ou helper conserve est classe comme owner canonique ou algorithme pur. | Guard pytest + audit persistant. |
| AC6 | Une garde bloque la reintroduction des surfaces catalogue/helper supprimees. | Evidence profile: `reintroduction_guard`; guard pytest + scan cible. |
| AC7 | Les invariants `RG-092`, `RG-095`, `RG-097`, `RG-098`, `RG-100` a `RG-105` restent satisfaits. | `pytest -q app/tests/unit/test_astrology_prediction_boundary.py`. |
| AC8 | La validation standard backend passe dans le venv. | `.\.venv\Scripts\Activate.ps1; cd backend; ruff format .; ruff check .; pytest -q`. |
| AC9 | Les helpers dupliques audites sont converges vers un owner unique. | Guard pytest + tests astrology cibles + scan. |
| AC10 | Les constantes catalogues redondantes auditees sont supprimees du code actif. | Guard pytest + scan. |
| AC11 | Les contrats de calcul d'aspects sont types et bloquent les anciennes formes legacy. | `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_aspects_calculator.py app/tests/unit/test_aspect_orb_overrides.py`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'etat initial et classifier les doublons (AC: AC2, AC4, AC5, AC9)
  - [ ] Subtask 1.1 - Creer `reference-runtime-before.md` avec comptes DB, join aspects/familles, payload reference avant correction.
  - [ ] Subtask 1.2 - Creer `astrology-duplication-audit.md` avec la classification des fichiers, constantes, tuples, helpers et tests.

- [ ] Task 2 - Corriger le seed des familles d'aspects (AC: AC1, AC2, AC3)
  - [ ] Subtask 2.1 - Modifier `reference_seed_service.py` pour charger uniquement `astral_aspect_families.json` et la cle `family`.
  - [ ] Subtask 2.2 - Ajouter une migration Alembic idempotente qui repare `astral_aspect_families` et les references `astral_aspects.family`.
  - [ ] Subtask 2.3 - Supprimer toute route de compatibilite vers `astral_aspect_family.json`.

- [ ] Task 3 - Supprimer les constantes, tuples et helpers redondants (AC: AC4, AC5, AC6, AC9, AC10)
  - [ ] Subtask 3.1 - Supprimer les tuples catalogues actifs de `ReferenceRepository` quand le loader JSON ou la DB est l'owner canonique.
  - [ ] Subtask 3.2 - Supprimer les constantes redondantes dans `domain/astrology` et remplacer leurs consommateurs par l'owner canonique ou par un helper derive unique.
  - [ ] Subtask 3.3 - Refuser tout fallback silencieux; si une valeur ne peut pas etre chargee depuis la source canonique, lever une erreur explicite.
  - [ ] Subtask 3.4 - Converger les helpers dupliques de normalisation d'angle, signe depuis longitude, SwissEph et listes d'interpretation vers un owner unique.

- [ ] Task 4 - Adapter les tests et gardes (AC: AC1, AC2, AC3, AC6, AC7)
  - [ ] Subtask 4.1 - Mettre a jour les tests de migrations/reference data pour exiger 3 familles et 20 aspects joints.
  - [ ] Subtask 4.2 - Mettre a jour les tests unitaires qui attendaient les anciennes constantes.
  - [ ] Subtask 4.3 - Ajouter ou durcir une garde anti-reintroduction pour le fichier singulier et les symboles catalogues supprimes.
  - [ ] Subtask 4.4 - Ajouter des scans/gardes sur les helpers dupliques audites et les fichiers astrology concernes.

- [ ] Task 5 - Produire l'evidence finale et valider (AC: AC2, AC7, AC8)
  - [ ] Subtask 5.1 - Creer `reference-runtime-after.md` avec les commandes et resultats.
  - [ ] Subtask 5.2 - Executer format, lint, tests dans le venv.
  - [ ] Subtask 5.3 - Documenter tout blocage comme `needs-user-decision`; ne pas marquer la story complete avec une limitation.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `docs/recherches astro/astral_aspect_families.json` pour les familles d'aspects.
  - `docs/recherches astro/astral_aspect_definitions.json`, `astral_aspect_profiles.json`, `astral_aspect_orb_rules.json` pour les donnees d'aspects deja externalisees.
  - `backend/app/services/prediction/reference_seed_service.py` comme owner applicatif du seed prediction/reference.
  - `backend/app/infra/db/repositories/reference_repository.py` comme owner de lecture SQL du payload reference.
  - `backend/app/domain/astrology/zodiac.py` ou un helper derive unique pour les calculs purs de signes, pas de nouvelle liste locale.
- Do not recreate:
  - listes locales des 20 aspects, 12 signes, 10 planetes, familles d'aspects, systemes astrologiques ou systemes de maisons.
  - `DEFAULT_ASPECT_ORBS` comme source de seed ou de payload reference.
  - taxonomies locales divergentes `personal` / `personal_planet` sans mapping canonique documente.
  - variantes locales de normalisation 360, signe depuis longitude, loader SwissEph ou helpers de listes d'interpretation.
- Shared abstraction allowed only if:
  - elle remplace au moins deux duplications prouvees dans `astrology-duplication-audit.md`;
  - elle a un owner unique;
  - elle n'introduit pas de dependance `domain/astrology -> services/prediction`.

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

- `docs/recherches astro/astral_aspect_family.json`
- `astral_aspect_family.json`
- `ASPECT_FAMILY_ROWS` comme tuple actif de repository/seed
- `ASPECT_ROWS` comme tuple actif de repository/seed
- `DEFAULT_ASPECT_ORBS` comme source de seed/reference payload
- `MAJOR_ASPECTS` duplique hors owner canonique
- `LUMINARIES` duplique hors owner canonique
- `PLANET_CLASS_BY_CODE` duplique hors owner canonique
- `ANGLE_CODES` duplique hors owner canonique
- `ANGULAR_HOUSES` et `SUCCEDENT_HOUSES` dupliques hors owner canonique
- `DEFAULT_TRADITIONAL_SIGN_RULERSHIPS` et `_HOUSE_SYSTEM_CODES` dupliques hors owner canonique
- `normalize_360`, `_norm360`, `_normalize_longitude`, `_sign_from_longitude`, `_get_swe_module`,
  `_profile_list`, `_require_list` dupliques hors owner canonique

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path when applicable:

- `_condamad/stories/CS-171-converger-referentiels-astrologie-db-json/astrology-duplication-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Familles d'aspects | `docs/recherches astro/astral_aspect_families.json` + `astral_aspect_families` | fichier singulier, tuples `ASPECT_FAMILY_ROWS` / `ASPECT_FAMILIES` |
| Aspects stables | JSON aspect canonique + `astral_aspects` | tuples `ASPECT_ROWS`, listes locales de 20 aspects |
| Orbes et definitions par systeme | `astral_aspect_definitions`, `astral_aspect_orb_rules` | `DEFAULT_ASPECT_ORBS` comme source runtime/seed |
| Signes, planetes, maisons structurels | `astral_signs`, `astral_planets`, `astral_houses` | listes locales dans repositories/services/tests |
| Calcul pur de signe depuis longitude | `backend/app/domain/astrology/zodiac.py` | duplications `_sign_from_longitude`, `_norm360`, listes locales |
| Normalisation d'angles | helper unique `domain/astrology` existant ou cree dans namespace astrology | variantes locales `normalize_360`, `_normalize_longitude`, `_norm360` |
| Acces SwissEph | provider owner unique dans `domain/astrology` | duplications `_get_swe_module` dans providers |
| Helpers interpretation | owner unique dans `domain/astrology/interpretation` | duplications `_profile_list`, `_require_list` |

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

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

For this story, suspected external surface is limited to repository docs or scripts
referencing `astral_aspect_family.json`. If found outside historical `_condamad`
evidence, implementation must stop for user decision.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `docs/recherches astro/astral_aspect_families.json`
- `docs/recherches astro/astral_aspect_definitions.json`
- `docs/recherches astro/astral_aspect_profiles.json`
- `docs/recherches astro/astral_aspect_orb_rules.json`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/domain/astrology/angle_utils.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/natal_preparation.py`
- `backend/app/domain/astrology/house_system_codes.py`
- `backend/app/domain/astrology/house_ruler_resolver.py`
- `backend/app/domain/astrology/ephemeris_provider.py`
- `backend/app/domain/astrology/houses_provider.py`
- `backend/app/domain/astrology/calculators/natal.py`
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/astrology/interpretation/aspect_strength.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py`
- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py`
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py`
- `backend/app/domain/astrology/interpretation/house_strength.py`
- `backend/app/domain/astrology/zodiac.py`
- `backend/migrations/versions/20260514_0102_normalize_astral_aspects.py`
- `backend/migrations/versions/20260514_0103_rename_astral_aspect_families.py`
- `backend/migrations/versions/20260514_0104_add_astral_aspect_orb_rules.py`
- `backend/app/tests/integration/test_reference_data_migrations.py`
- `backend/app/tests/integration/test_seed_31_prediction_v2.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/services/prediction/reference_seed_service.py` - charger le JSON pluriel canonique et supprimer le chemin singulier.
- `backend/app/infra/db/repositories/reference_repository.py` - supprimer les tuples catalogues redondants et lire les sources canoniques.
- `backend/app/domain/astrology/interpretation/aspect_strength.py` - supprimer taxonomies redondantes ou consommer l'owner unique.
- `backend/app/domain/astrology/builders/aspect_runtime_builder.py` - supprimer `MAJOR_ASPECTS` local si redondant.
- `backend/app/domain/astrology/interpretation/house_strength.py` - supprimer sets maisons/luminaires redondants si source canonique existe.
- `backend/app/domain/astrology/angle_utils.py` - devenir l'owner unique de normalisation d'angles ou deleguer a l'owner existant retenu.
- `backend/app/domain/astrology/ephemeris_provider.py` - supprimer les helpers SwissEph/normalisation dupliques.
- `backend/app/domain/astrology/houses_provider.py` - supprimer les helpers SwissEph/normalisation dupliques.
- `backend/app/domain/astrology/calculators/natal.py` - supprimer les helpers de signes/normalisation dupliques.
- `backend/app/domain/astrology/calculators/aspects.py` - converger la normalisation et validation d'orbes avec l'owner runtime recent.
- `backend/app/domain/astrology/house_system_codes.py` - supprimer mappings redondants si DB/JSON est owner.
- `backend/app/domain/astrology/house_ruler_resolver.py` - supprimer les rulerships redondants si source canonique existe.
- `backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py` - supprimer helpers de listes dupliques.
- `backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py` - supprimer helpers de listes dupliques.
- `backend/migrations/versions/20260514_0107_repair_astral_aspect_families_seed.py`
  - migration idempotente de reparation.
- `_condamad/stories/CS-171-converger-referentiels-astrologie-db-json/reference-runtime-before.md` - evidence initiale.
- `_condamad/stories/CS-171-converger-referentiels-astrologie-db-json/reference-runtime-after.md` - evidence finale.
- `_condamad/stories/CS-171-converger-referentiels-astrologie-db-json/astrology-duplication-audit.md` - classification des suppressions.

Likely tests:

- `backend/app/tests/integration/test_reference_data_migrations.py` - verifier familles, FK et joins.
- `backend/app/tests/integration/test_seed_31_prediction_v2.py` - verifier counts et seed depuis JSON.
- `backend/app/tests/unit/test_prediction_reference_repository.py` - verifier payload reference.
- `backend/app/tests/unit/test_astrology_reference_catalog_guard.py` - nouveau ou equivalent pour bloquer la reintroduction.
- `backend/tests/unit/domain/astrology/test_aspect_strength.py` - adapter aux owners canoniques.
- `backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py` - adapter aux owners canoniques.
- `backend/tests/unit/domain/astrology/test_natal_calculation.py` ou equivalent - verifier invariants numeriques apres convergence des helpers.
- `backend/tests/unit/domain/astrology/test_aspect_interpretation_builder.py` ou equivalent - verifier helpers interpretation apres convergence.

Files not expected to change:

- `frontend/**` - hors domaine.
- `backend/app/api/**` - aucun contrat HTTP n'est modifie.
- `backend/app/domain/prediction/**` - cette story ne change pas le moteur prediction.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
sqlite3 horoscope.db "SELECT COUNT(*) FROM astral_aspect_families;"
sqlite3 horoscope.db "SELECT COUNT(*) FROM astral_aspects a JOIN astral_aspect_families f ON f.id = a.family;"
sqlite3 horoscope.db "PRAGMA foreign_key_check;"
pytest -q app/tests/integration/test_reference_data_migrations.py app/tests/integration/test_seed_31_prediction_v2.py app/tests/unit/test_prediction_reference_repository.py
pytest -q tests/unit/domain/astrology/test_aspect_strength.py tests/unit/domain/astrology/test_aspect_runtime_builder.py
pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py
$catalogPattern = "astral_aspect_family\.json|ASPECT_FAMILY_ROWS|ASPECT_ROWS|DEFAULT_ASPECT_ORBS"
$constantPattern = "MAJOR_ASPECTS|PLANET_CLASS_BY_CODE|ANGLE_CODES|ANGULAR_HOUSES|SUCCEDENT_HOUSES|DEFAULT_TRADITIONAL_SIGN_RULERSHIPS|_HOUSE_SYSTEM_CODES"
$helperPattern = "normalize_360|_norm360|_normalize_longitude|_sign_from_longitude|_get_swe_module|_profile_list|_require_list"
rg -n $catalogPattern app tests ../docs -g "*.py" -g "*.md" -g "*.json"
rg -n $constantPattern app tests ../docs -g "*.py" -g "*.md" -g "*.json"
rg -n $helperPattern app tests ../docs -g "*.py" -g "*.md" -g "*.json"
pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py
# Le scan helper n'est pas zero-hit: ses resultats doivent correspondre aux owners autorises par la garde.
ruff format .
ruff check .
pytest -q
```

Story validation before implementation handoff:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-171-converger-referentiels-astrologie-db-json/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-171-converger-referentiels-astrologie-db-json/00-story.md
```

## 22. Regression Risks

- Risk: une constante supprimee etait en fait un invariant de calcul pur.
  - Guardrail: classification obligatoire dans `astrology-duplication-audit.md`; si non derivable d'une source canonique, stop user decision.
- Risk: la migration repare SQLite local mais pas PostgreSQL.
  - Guardrail: migration Alembic idempotente via SQLAlchemy/Alembic compatible dialectes, avec test migration.
- Risk: les tests conservent l'ancien comportement en dur.
  - Guardrail: tests modifies pour verifier JSON/DB; scan anti-retour sur tuples et fichier singulier.
- Risk: la suppression des constantes casse les invariants runtime des aspects.
  - Guardrail: executer les tests `RG-098` a `RG-105` applicables.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Do not accept `PASS with limitation`, broad allowlists, wildcard exceptions,
  unclassified fallback, compatibility, legacy, migration-only, shim, alias, TODO,
  or hidden residual in-domain work when this story is marked `full-closure`.
- Supprimer les constantes redondantes: la conservation est interdite sauf classification `canonical-active` comme algorithme pur non referentiel avec preuve.
- Pour les helpers, ne pas exiger un scan zero-hit global: exiger une seule definition owner autorisee et des consommateurs migres.
- Modifier les tests en consequence; ne pas ajouter de tests qui encodent un ancien doublon comme comportement nominal.
- Toutes les commandes Python doivent etre lancees apres `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `docs/recherches astro/astral_aspect_families.json` - source canonique des familles d'aspects.
- `backend/app/services/prediction/reference_seed_service.py` - owner du seed applicatif.
- `backend/app/infra/db/repositories/reference_repository.py` - owner de lecture du payload reference.
- `backend/horoscope.db` - evidence runtime locale du bug `astral_aspect_families` vide.
- `_condamad/stories/regression-guardrails.md` - invariants applicables aux referentiels astrologiques et runtime aspects.
