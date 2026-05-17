# Story CS-182 remplacer-vocabulaire-public-astro-par-referentiels-db: Remplacer le vocabulaire public astro par les référentiels DB

Status: done

## 1. Objective

Supprimer l'exception laissée par CS-181 autour de `public_astro_vocabulary.py`.
Les étoiles fixes et tonalités d'aspects du thème astral daily doivent basculer
vers les référentiels DB déjà seedés. Après implémentation,
`backend/app/domain/prediction` ne doit plus employer `PublicAstroVocabulary`,
`_STAR_DATA` ni `_ASPECT_TONES`.

## 2. Trigger / Source

- Source type: refactor
- Source reference: demande utilisateur du 2026-05-17 après mise en oeuvre des
  tables `astral_fixed_*`, `astral_constellations`, `astral_reference_*`,
  `astral_zodiacal_reference_*` et des seeds aspects.
- Reason for change: CS-181 est `done`, mais `public_astro_vocabulary.py`
  conserve `_STAR_DATA` et `_ASPECT_TONES`, qui dupliquent des référentiels DB-backed.

## 3. Domain Boundary

Cette story appartient à un seul domaine :

- Domain: `backend/app/domain/prediction`
- In scope:
  - Remplacer les usages de `PublicAstroVocabulary` dans la projection/prompt daily par un contrat runtime injecté, compatible avec les labels astrologiques canoniques existants.
  - Charger les étoiles fixes actives depuis `AstralFixedStarModel` et
    `AstralFixedStarDefinitionModel`; les traductions de mots-clés sont incluses
    uniquement quand un consommateur public existant les lit déjà.
  - Remplacer `aspect_tone()` par des données issues de `PredictionContext.aspect_profiles` et `AspectProfileData`.
  - Supprimer `public_astro_vocabulary.py` ou le réduire à un contrat non propriétaire uniquement si aucun symbole DB-backed n'y reste.
  - Mettre à jour les tests et guards empêchant le retour de `_STAR_DATA`, `_ASPECT_TONES` et `PublicAstroVocabulary`.
- Out of scope:
  - Modifier le schéma DB ou créer une nouvelle table.
  - Refaire l'algorithme SwissEph ou les calculs astronomiques de positions planétaires.
  - Modifier le frontend ou le contrat OpenAPI public.
  - Réécrire les contenus éditoriaux LLM hors consommation des faits daily déjà projetés.
- Explicit non-goals:
  - Ne pas créer un nouveau JSON applicatif ou mapping local remplaçant `_STAR_DATA` / `_ASPECT_TONES`.
  - Ne pas contourner `RG-108`, `RG-110` ou `RG-112`.
  - Ne pas réintroduire une exception CS-181 sous forme d'allowlist large, shim, alias ou fallback silencieux.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: dead-code-removal
- Archetype reason: la story supprime un catalogue local DB-backed devenu legacy depuis la mise en place des tables fixed star et des profils d'aspects.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les libellés publics existants des planètes, signes, maisons et aspects doivent rester résolus par le resolver canonique déjà injecté.
  - Les noms d'étoiles fixes et les longitudes doivent changer uniquement pour refléter les lignes DB actives.
  - Les tonalités d'aspects peuvent devenir plus précises, mais doivent provenir des champs `AspectProfileData` et rester déterministes.
  - Un référentiel incomplet doit échouer explicitement; aucun fallback local ne doit masquer l'absence de ligne DB.
- Deletion allowed: yes
- Replacement allowed: no
  Les wrappers legacy, alias, shims et mappings locaux de remplacement sont interdits.
  La migration des consommateurs vers les contrats canoniques DB/runtime est obligatoire.
- User decision required if: une donnée encore consommée par le thème astral daily n'a aucune source dans les tables seedées ou dans `PredictionContext.aspect_profiles`.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les faits DB-backed doivent être prouvés depuis le contexte runtime/repository, pas par scan seul. |
| Baseline Snapshot | yes | L'exception CS-181 doit être capturée avant/après avec les symboles restants. |
| Ownership Routing | yes | `infra/db` charge les données, `domain/prediction` consomme des contrats, sans dépendance SQLAlchemy directe. |
| Allowlist Exception | yes | Le registre doit documenter explicitement `none/none` pour prouver qu'aucune exception résiduelle n'est conservée pour fermer CS-181. |
| Contract Shape | no | Aucun champ API/OpenAPI ou type frontend ne doit être modifié. |
| Batch Migration | yes | Les consommateurs sont distincts: détection étoiles fixes, projection publique, prompts et tests. |
| Reintroduction Guard | yes | Les symboles et imports legacy doivent être bloqués après suppression. |
| Persistent Evidence | yes | Les preuves avant/après de fermeture de l'exception CS-181 doivent être persistées. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - DB schema reflected through SQLAlchemy metadata for `astral_fixed_stars`, `astral_fixed_star_definitions`, `astral_aspects` and `astral_aspect_profiles`.
  - Objet runtime chargé par `PredictionReferenceRepository.load_prediction_context()` pour `aspect_profiles`.
  - Guard AST sur les imports et symboles runtime interdits.
- Secondary evidence:
  - Scans ciblés sur `PublicAstroVocabulary`, `_STAR_DATA`, `_ASPECT_TONES`, `fixed_star_longitudes`, `fixed_star_display_name`.
- Static scans alone are not sufficient for this story because:
  - un symbole peut disparaître tout en laissant une copie locale du référentiel ailleurs; le runtime doit prouver que les événements daily lisent les lignes DB.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/public-astro-vocabulary-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/public-astro-vocabulary-after.md`
- Expected invariant:
  - aucun vocabulaire astrologique DB-backed ne reste recréé dans `backend/app/domain/prediction`.

## 4d. Ownership Routing Rule

À utiliser pour les refactors de frontière, namespace, service, API, core, domain ou infra.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Application use case | `services/**` | `api/**` |
| HTTP-only adapter | `api/v1/**` | `services/**` |
| Pure cross-cutting helper | `core/**` | `api/**` |
| Persistence detail | `infra/**` | `api/**` |
| Domain invariant | `domain/**` | `api/**` |

Story-specific routing:

| Responsibility | Canonical owner | Forbidden destination |
|---|---|---|
| Requête SQL des étoiles fixes | `backend/app/infra/db/repositories/**` | `backend/app/domain/prediction/**` |
| Contrat runtime étoiles fixes | `backend/app/infra/db/repositories/prediction_schemas.py` ou contrat dédié existant à réutiliser | dict local dans projection/prompt |
| Détection des conjonctions d'étoiles fixes | `backend/app/domain/prediction/enriched_astro_events_builder.py` consommant un contrat injecté | `public_astro_vocabulary.py` |
| Tonalité/interprétation d'aspect daily | `PredictionContext.aspect_profiles` / `AspectProfileData` | `_ASPECT_TONES` ou mapping local équivalent |
| Libellés publics signes/planètes/maisons/aspects | Resolver canonique `PredictionAstroLabels` existant ou son successeur injecté | mapping FR local dans prediction |

## 4e. Allowlist / Exception Register

À utiliser quand une règle large autorise des exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| none | none | Aucune exception résiduelle n'est autorisée pour les symboles legacy. | permanent: toute exception demandée doit bloquer l'implémentation et exiger une décision utilisateur. |

Règles :

- aucun wildcard;
- aucune exception sur un dossier complet;
- aucune exception implicite;
- toute exception doit être validée par test ou scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: aucune API, erreur, payload, export, DTO, contrat OpenAPI, client généré ou type frontend n'est affecté.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| B1 fixed star runtime | `_STAR_DATA` et helpers d'étoiles | Contrat DB fixed star | `EnrichedAstroEventsBuilder` | tests enriched events | scan étoiles zéro hit | aucune source DB active |
| B2 aspect tone | `_ASPECT_TONES` | champ `AspectProfileData` | foundation policy | tests de projection | scan zéro hit | champ ambigu |
| B3 labels adapter | imports `PublicAstroVocabulary` | faits injectés | projection/prompt | tests publics | zéro import runtime | resolver indisponible |
| B4 guards/evidence | résidu CS-181 | `RG-113` + artefacts before/after | tests de guard | guards localization/catalog | guard AST + scan | faux positif inclassable |

## 4h. Persistent Evidence Artifacts

À utiliser quand la story exige une preuve d'audit, snapshot, baseline,
diff OpenAPI, mapping de migration, registre d'allowlist ou registre
d'exceptions.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Audit avant | `_condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/public-astro-vocabulary-before.md` | Inventaire initial. |
| Audit après | `_condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/public-astro-vocabulary-after.md` | Preuve de fermeture. |
| Preuve runtime | `_condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/runtime-reference-evidence.md` | Tests DB/runtime. |

## 4i. Reintroduction Guard

À utiliser quand la story supprime, interdit ou converge hors d'une route,
d'un champ, d'un import, d'un module, d'un préfixe, d'un chemin OpenAPI,
d'une route frontend ou d'un statut legacy.

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- forbidden symbols or states
- importable Python modules when `public_astro_vocabulary.py` is deleted

Required forbidden examples:

- `PublicAstroVocabulary`
- `_STAR_DATA`
- `_ASPECT_TONES`
- `fixed_star_longitudes`
- `fixed_star_display_name`

Guard evidence:

- Evidence profile: `reintroduction_guard`;
  `pytest -q app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_astrology_reference_catalog_guard.py`.

## 4j. Source Finding Closure

- Closure status: full-closure
- Source finding: exception résiduelle CS-181 dans `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/00-story.md` pour `public_astro_vocabulary.py`.
- Closure proof required: artefacts before/after, tests runtime, scans négatifs et mise à jour des guards.
- Known residual in-domain work: none
- Deferred non-domain concerns: none

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `backend/app/domain/prediction/public_astro_vocabulary.py` -
  `_STAR_DATA` contient 10 étoiles; `_ASPECT_TONES` contient six tonalités locales.
- Evidence 2: `backend/app/domain/prediction/enriched_astro_events_builder.py` -
  importe les helpers fixed star pour détecter et nommer les conjonctions.
- Evidence 3: `backend/app/domain/prediction/public_projection.py` - utilise `PublicAstroVocabulary.aspect_tone()` pour `astro_foundation.dominant_aspects[*].tonality`.
- Evidence 4: `backend/app/domain/prediction/public_astro_daily_events.py` - utilise `PublicAstroVocabulary.star()` pour construire les événements publics `fixed_stars`.
- Evidence 5: `backend/app/domain/prediction/astrologer_prompt_builder.py` - instancie `PublicAstroVocabulary` pour les libellés astro du prompt.
- Evidence 6: `backend/app/infra/db/models/reference.py` - expose `AstralFixedStarModel` et `AstralFixedStarDefinitionModel` avec `display_name` et `ecliptic_longitude_deg`.
- Evidence 7: `backend/app/infra/db/repositories/prediction_reference_repository.py` -
  charge déjà `AspectProfileData` depuis les tables d'aspects.
- Evidence 8: `_condamad/stories/regression-guardrails.md` - invariants `RG-108`, `RG-110`, `RG-112` consultés avant cadrage.

## 6. Target State

After implementation:

- Les événements fixed star sont calculés depuis les lignes actives `astral_fixed_star_definitions` et non depuis `_STAR_DATA`.
- Les noms d'étoiles affichés viennent de `AstralFixedStarModel.display_name`; les mots-clés/traductions sont disponibles dans le contrat runtime si le rendu public en a besoin.
- Les tonalités d'aspect de la projection publique viennent de `AspectProfileData` et non d'un mapping local.
- `PublicAstroVocabulary` n'est plus importé par le runtime prediction; si un contrat de labels reste nécessaire, il ne porte aucune donnée DB-backed.
- Les tests et guards échouent si l'ancienne exception CS-181 revient.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-108` - les étoiles fixes et aspects sont DB-backed et ne doivent plus être recréés localement.
  - `RG-110` - `domain/prediction` ne doit pas redevenir propriétaire de mappings de libellés ou effets astrologiques publics.
  - `RG-112` - CS-181 interdit explicitement `_STAR_DATA` et `_ASPECT_TONES`; cette story ferme l'exception résiduelle.
  - `RG-113` - le nouveau guard durable interdira le retour du vocabulaire public astro local DB-backed.
- Non-applicable invariants:
  - `RG-109` - la story ne traite pas les traductions de signes déjà fermées.
  - `RG-111` - la story ne modifie pas le registre global des modèles SQLAlchemy.
- Required regression evidence:
  - tests repository/runtime fixed stars;
  - tests publics prediction;
  - scans négatifs ciblés sur les symboles interdits;
  - artefacts before/after persistés.
- Allowed differences:
  - valeurs textuelles de `tonality` plus précises si elles proviennent explicitement de `AspectProfileData`.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les étoiles fixes daily viennent des tables fixed star actives. | `pytest -q app/tests/unit/test_prediction_reference_repository.py`. |
| AC2 | Le builder enriched détecte les conjonctions via contrat runtime. | `pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py`. |
| AC3 | `dominant_aspects[*].tonality` vient des profils d'aspects. | `pytest -q tests/unit/prediction/test_public_astro_foundation.py`. |
| AC4 | Le runtime prediction n'importe plus `PublicAstroVocabulary`. | `pytest -q app/tests/unit/test_astrology_localization_guardrails.py`. |
| AC5 | Les guards interdisent les symboles legacy fixed star/aspect tone. | `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py`. |
| AC6 | Les artefacts before/after prouvent la clôture de CS-181. | `rg -n "Closure status" _condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/public-astro-vocabulary-before.md _condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/public-astro-vocabulary-after.md _condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/runtime-reference-evidence.md`. |
| AC7 | La validation backend ciblée passe dans le venv. | Activer `.\.venv\Scripts\Activate.ps1` depuis la racine du repo, puis exécuter `ruff check .` et les commandes pytest du plan de validation depuis `backend`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le baseline et définir le contrat runtime (AC: AC1, AC6)
  - [x] Créer `public-astro-vocabulary-before.md` avec les imports, symboles, consommateurs et remplacement canonique.
  - [x] Identifier si le contrat fixed star doit vivre dans `prediction_schemas.py` ou dans un contrat runtime existant; ne pas créer de dépendance domain -> infra.

- [x] Task 2 - Charger les étoiles fixes depuis l'infra DB (AC: AC1)
  - [x] Ajouter une méthode repository qui retourne les étoiles fixes actives
    avec `key`, `display_name`, `ecliptic_longitude_deg`.
  - [x] Ajouter les mots-clés localisés seulement si un test de projection public
    existant prouve leur consommation.
  - [x] Brancher le chargement dans le contexte utilisé par le moteur daily sans requête SQL directe dans `domain/prediction`.
  - [x] Tester le tri, le filtrage `is_active` et la correspondance avec les seeds.

- [x] Task 3 - Migrer les consommateurs fixed star (AC: AC2, AC4)
  - [x] Remplacer les appels à `fixed_star_longitudes()` dans `EnrichedAstroEventsBuilder`.
  - [x] Remplacer `vocabulary.star()` dans `PublicAstroDailyEventsPolicy` et `PublicTimeWindowPolicy` par le nom déjà porté par l'événement ou par le contrat runtime.
  - [x] Supprimer les fonctions legacy si aucun consommateur ne reste.

- [x] Task 4 - Migrer les tonalités d'aspects (AC: AC3)
  - [x] Choisir explicitement le champ source `AspectProfileData` pour la tonalité publique et documenter la règle dans le test.
  - [x] Remplacer `vocabulary.aspect_tone(e.aspect)` par une résolution depuis le contexte/profil d'aspect.
  - [x] Vérifier que les aspects absents échouent ou produisent une absence contrôlée, jamais un fallback `"nuance"` local.

- [x] Task 5 - Supprimer l'adaptateur legacy et renforcer les tests (AC: AC4, AC5, AC7)
  - [x] Supprimer ou vider de toute donnée DB-backed `public_astro_vocabulary.py`.
  - [x] Adapter les helpers de tests pour injecter le nouveau contrat de labels/runtime facts.
  - [x] Mettre à jour les guards et scans négatifs.

- [x] Task 6 - Capturer l'état final et valider (AC: AC5, AC6, AC7)
  - [x] Créer `public-astro-vocabulary-after.md` et `runtime-reference-evidence.md`.
  - [x] Exécuter lint, tests ciblés et scans du plan de validation.
  - [x] Documenter toute décision de blocage plutôt que d'ajouter un fallback.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `PredictionReferenceRepository.get_aspect_profiles()` et `PredictionContext.aspect_profiles` pour les aspects.
  - `AstralFixedStarModel`, `AstralFixedStarDefinitionModel`, `AstralFixedStarKeywordModel` et `AstralFixedStarKeywordTranslationModel` pour les étoiles fixes.
  - `PredictionAstroLabels` ou son propriétaire canonique existant pour les libellés planète/signe/maison/aspect.
  - Les tests de seed/migration existants dans `backend/app/tests/unit/test_reference_data_service.py` et `backend/app/tests/integration/test_reference_data_migrations.py`.
- Ne pas recréer :
  - dictionnaire de longitudes d'étoiles fixes;
  - dictionnaire de tonalités d'aspects;
  - fallback local `"nuance"` pour aspect inconnu;
  - nouveau JSON applicatif de vocabulaire fixed star.
- Shared abstraction allowed only if:
  - elle a au moins deux consommateurs runtime immédiats;
  - elle transporte un contrat typé dérivé du repository;
  - elle ne dépend pas de SQLAlchemy dans `domain/prediction`.

## 10. No Legacy / Forbidden Paths

Interdit sans approbation explicite :

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Symboles / chemins spécifiquement interdits :

- `backend/app/domain/prediction/public_astro_vocabulary.py::_STAR_DATA`
- `backend/app/domain/prediction/public_astro_vocabulary.py::_ASPECT_TONES`
- `fixed_star_longitudes`
- `fixed_star_display_name`
- `PublicAstroVocabulary` as a runtime dependency
- any new `requirements.txt`

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

Décisions autorisées : `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path when applicable:

- `_condamad/stories/CS-182-remplacer-vocabulaire-public-astro-par-referentiels-db/public-astro-vocabulary-before.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Étoiles fixes actives | `AstralFixedStarDefinitionModel` + repository infra | `_STAR_DATA` |
| Nom public d'étoile fixe | `AstralFixedStarModel.display_name` | `PublicAstroVocabulary.star()` |
| Longitude d'étoile fixe | `AstralFixedStarDefinitionModel.ecliptic_longitude_deg` | `fixed_star_longitudes()` |
| Profil/tonalité d'aspect | `AspectProfileData` chargé depuis `astral_aspect_profiles` | `_ASPECT_TONES` |
| Libellés astrologiques publics | resolver canonique injecté | mappings locaux dans prediction |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Interdit :

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with the external proof and deletion risk.

## 16. Generated Contract Check

- Generated contract check: not applicable
- Reason: aucune API générée, manifest de routes, schéma, contrat public ou client généré n'est affecté.

## 17. Files to Inspect First

Codex doit inspecter avant toute édition :

- `backend/app/domain/prediction/public_astro_vocabulary.py`
- `backend/app/domain/prediction/enriched_astro_events_builder.py`
- `backend/app/domain/prediction/public_astro_daily_events.py`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/domain/prediction/astrologer_prompt_builder.py`
- `backend/app/domain/prediction/aspect_reference.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/translation_reference.py`
- `backend/app/tests/unit/test_astrology_localization_guardrails.py`
- `backend/app/tests/unit/test_astrology_reference_catalog_guard.py`
- `backend/tests/unit/prediction/test_public_astro_daily_events.py`

## 18. Expected Files to Modify

Likely files:

- `backend/app/infra/db/repositories/prediction_schemas.py` - ajouter un contrat typé fixed star si aucun contrat existant ne convient.
- `backend/app/infra/db/repositories/prediction_reference_repository.py` - charger les étoiles fixes actives dans le contexte prediction ou un contrat adjacent.
- `backend/app/domain/prediction/enriched_astro_events_builder.py` - consommer les étoiles fixes runtime.
- `backend/app/domain/prediction/public_astro_daily_events.py` - retirer `PublicAstroVocabulary`.
- `backend/app/domain/prediction/public_projection.py` - dériver la tonalité depuis `AspectProfileData`.
- `backend/app/domain/prediction/astrologer_prompt_builder.py` - consommer le contrat de labels sans adapter legacy.
- `backend/app/domain/prediction/public_astro_vocabulary.py` - supprimer ou réduire à un contrat sans données DB-backed.
- `backend/app/tests/unit/test_astrology_localization_guardrails.py` - bloquer les symboles legacy.

Likely tests:

- `backend/tests/unit/prediction/test_enriched_astro_events_builder.py`
- `backend/tests/unit/prediction/test_public_astro_daily_events.py`
- `backend/tests/unit/prediction/test_public_astro_foundation.py`
- `backend/tests/unit/prediction/test_public_projection.py`
- `backend/tests/unit/prediction/test_public_time_window.py`
- `backend/app/tests/unit/test_prediction_reference_repository.py`
- `backend/app/tests/unit/test_reference_data_service.py`
- `backend/app/tests/unit/test_astrology_localization_guardrails.py`
- `backend/app/tests/unit/test_astrology_reference_catalog_guard.py`

Files not expected to change:

- `frontend/**` - domaine backend uniquement.
- `backend/migrations/versions/**` - les tables existent déjà selon la demande utilisateur.
- `docs/db_seeder/astrology/*.json` - pas de modification de seed attendue.
- `backend/requirements.txt` - interdit par la règle repo.

## 19. Dependency Policy

- New dependencies: none
- Changements de dépendances autorisés uniquement s'ils sont listés ici avec justification.

## 20. Validation Plan

Exécuter ou justifier pourquoi c'est ignoré :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_prediction_reference_repository.py app/tests/unit/test_reference_data_service.py
pytest -q app/tests/unit/test_astrology_localization_guardrails.py app/tests/unit/test_astrology_reference_catalog_guard.py
pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py tests/unit/prediction/test_public_astro_daily_events.py
pytest -q tests/unit/prediction/test_public_astro_foundation.py tests/unit/prediction/test_public_projection.py tests/unit/prediction/test_public_time_window.py
rg -n "PublicAstroVocabulary|_STAR_DATA|_ASPECT_TONES|fixed_star_longitudes|fixed_star_display_name" app/domain/prediction app/tests tests -g "*.py"
rg -n "\"nuance\"|\"fluidité\"|\"ajustement\"|\"intensification\"|\"adaptation\"" app/domain/prediction -g "*.py"
```

Résultat de scan attendu : aucun hit runtime pour les symboles interdits, hors artefacts historiques `_condamad` et tests de guard intentionnellement mis à jour.

## 21. Regression Risks

- Risk: les événements fixed star disparaissent si le contexte daily ne transporte pas les lignes DB.
  - Guardrail: test runtime avec seed Regulus et vérification de l'événement public.
- Risk: la tonalité publique change de vocabulaire et casse des assertions de snapshot.
  - Guardrail: tests ciblés documentant le champ `AspectProfileData` choisi et les différences autorisées.
- Risk: le domaine prediction reçoit une session SQLAlchemy pour lire les étoiles fixes.
  - Guardrail: ownership routing et scan des imports `sqlalchemy`, `Session`, `app.infra` dans `domain/prediction`.
- Risk: un helper de test conserve `PublicAstroVocabulary` et normalise l'ancien contrat.
  - Guardrail: scan négatif sur `backend/app/tests` et `backend/tests`.

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
  TODO, or hidden residual in-domain work when this story is marked `full-closure`.
- Toutes les commandes Python doivent être exécutées après `.\.venv\Scripts\Activate.ps1`.

## 23. References

- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/00-story.md` - source de l'exception à fermer.
- `_condamad/stories/regression-guardrails.md` - invariants `RG-108`, `RG-110`, `RG-112`, `RG-113`.
- `backend/app/domain/prediction/public_astro_vocabulary.py` - surface legacy à supprimer.
- `backend/app/domain/prediction/enriched_astro_events_builder.py` - consommateur des longitudes/noms fixed star.
- `backend/app/domain/prediction/public_projection.py` - consommateur de tonalité d'aspect.
- `backend/app/infra/db/models/reference.py` - modèles DB fixed star et aspects.
- `backend/app/infra/db/repositories/prediction_reference_repository.py` - chargement existant des profils d'aspects.
