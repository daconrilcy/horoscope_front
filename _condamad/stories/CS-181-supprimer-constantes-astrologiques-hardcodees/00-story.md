# Story CS-181 supprimer-constantes-astrologiques-hardcodees: Supprimer les constantes astrologiques codées en dur et les fallbacks legacy

Status: done

## 1. Objective

Supprimer les constantes métier astrologiques encore codées en dur dans le runtime backend :
maîtrises de signes, aspects majeurs, orbes, classifications et fallbacks legacy.
Après implémentation, les calculs et projections astrologiques consomment les
référentiels canoniques DB/JSON déjà chargés en contrats runtime.

## 2. Trigger / Source

- Type de source : audit
- Référence source : demande utilisateur du 2026-05-16 et inventaire Codex du même tour sur `backend/app`.
- Raison du changement : `backend/app/services/natal/calculation_service.py` contient encore un fallback
  legacy `sign_rulerships`, et le scan backend a identifié d'autres constantes métier actives.

## 3. Domain Boundary

Cette story appartient à un seul domaine :

- Domaine : `backend/app/domain/astrology`
- Domain: `backend/app/domain/astrology`
- In scope:
- Périmètre inclus :
  - Supprimer les fallbacks legacy du flux natal qui reconstituent des référentiels métier.
  - Centraliser ou dériver les constantes astrologiques depuis les contrats runtime existants.
  - Corriger les consommateurs `backend/app/domain/prediction` uniquement quand ils dupliquent un référentiel astrologique DB-backed nécessaire au flux daily.
  - Ajouter des tests et guards empêchant la réintroduction de mappings astrologiques locaux.
- Hors périmètre :
- Out of scope:
  - Modifier les migrations DB existantes ou ajouter de nouvelles tables sans preuve de manque de référentiel.
  - Refaire les algorithmes astronomiques SwissEph, Delta T ou maisons simplifiées.
  - Modifier le frontend.
  - Réécrire les contenus éditoriaux ou les traductions i18n.
- Non-objectifs explicites :
- Explicit non-goals:
  - Ne pas changer la stack ni les contrats API publics sauf preuve de champ legacy supprimé côté payload.
  - Ne pas introduire un nouveau fichier JSON applicatif concurrent aux sources `docs/db_seeder/astrology` et aux tables canoniques.
  - Ne pas contourner `RG-106`, `RG-107`, `RG-108`, `RG-110`.
  - Ne pas créer de fallback de compatibilité pour remplacer les fallbacks supprimés.

## 4. Operation Contract

- Operation type: remove
- Type d'opération : remove
- Primary archetype: dead-code-removal
- Archétype principal : dead-code-removal
- Archetype reason: la story supprime des chemins legacy/fallbacks et des constantes métier locales dont la source canonique existe déjà dans les référentiels runtime.
- Raison de l'archétype : la story supprime des chemins legacy/fallbacks et des constantes métier locales dont la source canonique existe déjà dans les référentiels runtime.
- Behavior change allowed: constrained
- Changement de comportement autorisé : constrained
- Behavior change constraints:
  - Les appels avec référentiel valide doivent produire des résultats équivalents ou plus strictement validés.
  - Les anciens doubles de tests ou payloads incomplets ne doivent plus passer par fallback silencieux.
- Contraintes de changement de comportement :
  - Les appels avec référentiel valide doivent produire des résultats équivalents ou plus strictement validés.
  - Les anciens doubles de tests ou payloads incomplets ne doivent plus passer par fallback silencieux; ils doivent être mis à jour ou échouer explicitement.
  - Les erreurs utilisateur/API existantes doivent rester stables quand l'entrée est invalide.
- Deletion allowed: yes
- Suppression autorisée : yes
- Replacement allowed: no
- Remplacement autorisé : no
- User decision required if: une constante métier auditée n'a aucune source canonique DB, seed JSON, contrat runtime ou décision produit existante permettant de la dériver.
- Décision utilisateur requise si : une constante métier auditée n'a aucune source canonique DB, seed JSON, contrat runtime ou décision produit existante permettant de la dériver.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les données astrologiques métier doivent provenir des référentiels runtime observables, pas de scans statiques seuls. |
| Baseline Snapshot | yes | Le scan actuel doit être capturé avant/après pour prouver la fermeture. |
| Ownership Routing | yes | Les responsabilités entre `domain/astrology`, `domain/prediction`, `services/natal` et `infra/db` doivent rester explicites. |
| Allowlist Exception | yes | Les constantes techniques non DB-backed conservées doivent être classées avec justification exacte. |
| Contract Shape | no | Not applicable: la story ne vise pas une modification de payload public ou OpenAPI; tout impact découvert doit bloquer ou être documenté. |
| Batch Migration | yes | Les surfaces concernées sont divisées entre natal runtime, daily prediction et guards/tests. |
| Reintroduction Guard | yes | Les mappings et fallbacks supprimés doivent être bloqués contre retour. |
| Persistent Evidence | yes | L'audit avant/après et le registre d'exceptions doivent être persistés dans le dossier de story. |

## 4b. Runtime Source of Truth

- Primary source of truth: schéma DB/référentiel runtime chargé via
- Source de vérité principale : schéma DB/référentiel runtime chargé via
  `AstrologyRuntimeReferenceRepository.load()`, `AstrologyRuntimeReference`, AST guard tests,
  seeds `docs/db_seeder/astrology/*.json`, tables astrology et rulesets déjà utilisés.
- Secondary evidence: scans ciblés des constantes interdites dans `backend/app`.
- Preuve secondaire : scans ciblés des constantes interdites dans `backend/app`.
- Static scans alone are not sufficient: un mapping peut disparaître tout en laissant un fallback runtime équivalent ailleurs.
- Les scans statiques seuls ne suffisent pas : un mapping peut disparaître tout en laissant un fallback runtime équivalent ailleurs.
- Preuve runtime obligatoire : tests chargeant un référentiel valide et vérifiant que `NatalCalculationService`,
  `EventDetector` et les builders concernés consomment les définitions runtime.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/hardcoded-astrology-before.md`
- Artefact de baseline avant implémentation : `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/hardcoded-astrology-before.md`
- Artefact de baseline après implémentation : `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/hardcoded-astrology-after.md`
- Comparison after implementation: reproduire le même script ou les mêmes commandes `rg` ciblées avant/après et documenter chaque différence.
- Comparaison après implémentation : reproduire le même script ou les mêmes commandes `rg` ciblées avant/après et documenter chaque différence.
- Expected invariant: aucun référentiel métier DB-backed ne reste recréé localement dans le code applicatif.
- Invariant attendu : aucun référentiel métier DB-backed ne reste recréé localement dans le code applicatif.
- Différences autorisées : constantes géométriques nommées (`360`, `30`, `12`) et flags SwissEph uniquement s'ils sont classés dans le registre d'exceptions.

## 4d. Ownership Routing Rule

Table de routage des responsabilités :

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Référentiel signes, maisons, planètes, maîtrises, systèmes | `backend/app/infra/db/repositories` + `backend/app/domain/astrology/runtime` | `services/natal` |
| Calcul natal pur et validation runtime | `backend/app/domain/astrology` | `api/**`, `services/**` hors orchestration |
| Orbes et aspects de calcul | `backend/app/domain/astrology/calculators` via contrats runtime | constantes dans `domain/prediction` |
| Projection daily consommant des faits astro | `backend/app/domain/prediction` | propriétaire de référentiels astrology DB-backed |

Les preuves de validation doivent inclure des guards d'architecture qui prouvent que ces propriétaires sont respectés.

## 4e. Allowlist / Exception Register

Les exceptions sont autorisées uniquement pour les constantes qui ne sont pas DB-backed et ne peuvent pas raisonnablement être chargées depuis un référentiel runtime.

Chemin obligatoire de la table :

- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/astrology-constant-exceptions.md`

Colonnes obligatoires :

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|

Interdit :

- exception wildcard;
- exception sur un dossier complet;
- échéance vide;
- `temporary` sans date, condition ou décision tracée.

## 4f. Contract Shape

- Not applicable: no API route, DTO, OpenAPI schema, generated client or frontend type is intentionally modified.
- Reason: aucune route API, aucun DTO, schéma OpenAPI, client généré ou type frontend n'est intentionnellement modifié.
- Forme du contrat : non applicable
- Raison : aucune route API, aucun DTO, schéma OpenAPI, client généré ou type frontend n'est intentionnellement modifié.
  Si un champ public doit être supprimé, arrêter l'implémentation et créer une story API/contrat séparée.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| B1 Fallbacks natal | fallbacks natal legacy | Référentiel runtime | service natal/tests | tests runtime natal | scan zéro | mock legacy requis |
| B2 Constantes d'aspect | mappings et orbes fixes | rulesets runtime | daily prediction | tests d'événements | scan zéro | contexte daily incomplet |
| B3 Vocabulaire astro public | `_STAR_DATA`, `_ASPECT_TONES` | canonique ou exception | projection daily | tests astro publics | registre exact | source absente |
| B4 Guards | scans manuels | tests AST/guard | tests | guard du catalogue de références | mapping bloqué | allowlist wildcard |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit avant | `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/hardcoded-astrology-before.md` | Inventaire initial des constantes et fallbacks. |
| Audit après | `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/hardcoded-astrology-after.md` | Preuve de suppression ou classification. |
| Registre d'exceptions | `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/astrology-constant-exceptions.md` | Constantes techniques conservées. |
| Preuve des guards | `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/guard-evidence.md` | Commandes exécutées et résultats attendus. |

## 4i. Reintroduction Guard

L'implémentation doit ajouter ou mettre à jour un guard d'architecture afin que ces symboles interdits ne puissent pas être réintroduits :
Architecture guard against reintroduced forbidden symbols:

- mappings de maîtrises de signes codés en dur dans `backend/app/services/natal`;
- mappings degré-vers-code d'aspect hors chargement de référence canonique;
- création en fallback de `aspect_orb_rules`, `house_axes`, `planet_definitions` dans l'orchestration de service;
- mappings locaux de vocabulaire astrologique DB-backed sous `backend/app/domain/prediction`.

Commande/test de guard obligatoire :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_runtime_reference_guard.py
```

## 4j. Source Finding Closure

- Statut de clôture : full-closure
- Finding source : demande utilisateur du 2026-05-16 + inventaire Codex des constantes codées en dur backend astrology
- Preuve de clôture obligatoire : artefacts avant/après, tests runtime, scans négatifs et guard anti-réintroduction
- Travail résiduel in-domain connu : aucun
- Préoccupations hors domaine différées : constantes purement produit non astrology dans `domain/prediction` si elles ne dupliquent pas un référentiel astrologique DB-backed

## 5. Current State Evidence

Le code actuel ou l'audit indique :

- Evidence 1: `backend/app/services/natal/calculation_service.py` -
  `_legacy_payload_for_mock_db` reconstruit localement des référentiels astrology.
- Preuve 1 : `backend/app/services/natal/calculation_service.py` -
  `_legacy_payload_for_mock_db` reconstruit localement des référentiels astrology.
- Preuve 2 : `backend/app/domain/prediction/event_detector.py` - `ASPECTS_V1`, `CHALDEAN_ORDER`, `DAY_RULERS`, `ANGLE_TARGETS` et fallback `orb_max=2.0` sont codés localement.
- Preuve 3 : `backend/app/domain/prediction/enriched_astro_events_builder.py` - mapping aspects majeurs, orbes et priorités d'événements enrichis sont en dur.
- Preuve 4 : `backend/app/domain/prediction/public_astro_vocabulary.py` - étoiles fixes et tonalités d'aspects sont en dur.
- Preuve 5 : `backend/app/domain/astrology/interpretation/aspect_strength.py`,
  `house_strength.py`, `builders/sign_runtime_builder.py` - seuils et pondérations locales.
- Preuve 6 : `_condamad/stories/regression-guardrails.md` - invariants consultés avant cadrage, notamment `RG-106`, `RG-107`, `RG-108`, `RG-110`.

## 6. Target State

Après implémentation :

- `NatalCalculationService` ne contient plus de fallback legacy recréant un référentiel astrologique.
- Les tests qui dépendaient de payloads mockés incomplets fournissent des fixtures runtime complètes ou utilisent la factory canonique.
- Les aspects, orbes, systèmes et classifications DB-backed sont lus depuis les contrats runtime/rulesets disponibles.
- Toute constante technique conservée est nommée et documentée dans `astrology-constant-exceptions.md`.
- Un guard échoue si un mapping de référentiel astrologique DB-backed est réintroduit dans `backend/app`.

## 6a. Regression Guardrails

- Source des guardrails : `_condamad/stories/regression-guardrails.md`
- Invariants applicables :
  - `RG-106` - les calculateurs astrology ne doivent pas revenir à des tuples ou constantes métier legacy.
  - `RG-107` - le flux natal ne doit pas transporter de payload libre ou fallback implicite de référence.
  - `RG-108` - tout vocabulaire métier DB-backed doit rester lu depuis sa source canonique.
  - `RG-110` - `domain/prediction` ne doit pas redevenir propriétaire de mappings astrologiques affichables DB-backed.
- Invariants non applicables :
  - `RG-109` - la story ne traite pas directement les libellés i18n de signes déjà fermés par CS-174/CS-177.
- Preuves de régression obligatoires :
  - tests runtime et guards listés dans le plan de validation;
  - scans négatifs sur les symboles interdits;
  - artefacts avant/après persistés.
- Différences autorisées :
  - constantes mathématiques/astronomiques non DB-backed classées explicitement;
  - flags SwissEph de fallback si justifiés comme constantes d'API externe.

## 7. Acceptance Criteria

| AC | Requirement | Evidence |
|---|---|---|
| AC1 | L'inventaire avant/après classe chaque constante auditée. | `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py`; artefacts before/after. |
| AC2 | Les fallbacks legacy de `_legacy_payload_for_mock_db` sont supprimés. | `pytest -q app/tests/unit/test_natal_calculation_service.py`; scan natal zéro. |
| AC3 | Les mappings d'aspects daily ne sont plus dupliqués localement. | `pytest -q tests/unit/prediction/test_enriched_astro_events_builder.py`; scan des aspects. |
| AC4 | Les constantes conservées sont classées sans wildcard ni exception de dossier. | `pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py`; registre exact. |
| AC5 | Le domaine astrology reste séparé de prediction. | `pytest -q app/tests/unit/test_astrology_prediction_boundary.py`; scan imports interdits. |
| AC6 | Les guards échouent si les mappings DB-backed reviennent. | `pytest -q app/tests/unit/test_astrology_runtime_reference_guard.py`; runtime evidence + guard. |
| AC7 | La validation standard backend passe dans le venv. | `ruff check .`; commandes pytest ciblées du plan de validation. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer et classer l'état initial (AC: AC1, AC4)
  - [ ] Créer `hardcoded-astrology-before.md` avec les fichiers, symboles, source canonique attendue et décision.
  - [ ] Créer `astrology-constant-exceptions.md` uniquement pour les constantes non DB-backed.

- [ ] Task 2 - Supprimer les fallbacks legacy natal (AC: AC2, AC6)
  - [ ] Retirer la reconstruction locale des maîtrises, axes, règles d'orbes et définitions planétaires.
  - [ ] Adapter les tests mockés pour fournir un `AstrologyRuntimeReference` complet ou passer par une factory canonique.
  - [ ] Ajouter un test négatif prouvant qu'un référentiel incomplet échoue explicitement.

- [ ] Task 3 - Dériver les constantes daily depuis les référentiels (AC: AC3, AC4)
  - [ ] Remplacer les mappings d'aspects locaux par les définitions/rulesets chargés.
  - [ ] Remplacer les fallbacks d'orbe par une erreur contrôlée ou une règle runtime explicite.
  - [ ] Classer les étoiles fixes et règles de progression si aucune source canonique n'existe.

- [ ] Task 4 - Renforcer les guards (AC: AC5, AC6)
  - [ ] Étendre `test_astrology_reference_catalog_guard.py` ou créer un test AST dédié.
  - [ ] Vérifier que la garde exclut les fixtures/tests de données sans masquer le code applicatif.
  - [ ] Ajouter les scans négatifs exacts au plan de validation.

- [ ] Task 5 - Capturer l'état final et valider (AC: AC1, AC7)
  - [ ] Créer `hardcoded-astrology-after.md`.
  - [ ] Exécuter lint, tests ciblés et scans négatifs.
  - [ ] Documenter les résultats dans `guard-evidence.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `AstrologyRuntimeReferenceRepository` et `AstrologyRuntimeReferenceMapper` pour le référentiel runtime natal.
  - `PredictionReferenceRepository` et le contexte prediction chargé pour les règles daily.
  - `planet_catalog.py`, `zodiac.py`, `house_system_codes.py` quand une constante géométrique ou catalogue seed-backed existe déjà.
  - Tests/factories existants sous `backend/tests/factories/astrology_runtime_reference_factory.py`.
- Ne pas recréer :
  - listes de signes, planètes, aspects, maisons, maîtrises ou systèmes astrologiques;
  - règles d'orbes ou valences d'aspects en dict local;
  - fallback `modern/natal/any` synthétique.
- Abstraction partagée autorisée uniquement si :
  - au moins deux consommateurs runtime l'utilisent immédiatement;
  - elle lit une source canonique existante;
  - elle ne devient pas un second référentiel local.

## 10. No Legacy / Forbidden Paths

Interdit sauf approbation explicite :

- wrappers de compatibilité / compatibility wrappers
- alias transitoires
- imports legacy
- implémentations actives dupliquées
- fallback silencieux
- service au niveau racine quand un namespace canonique existe
- préservation d'un ancien chemin via ré-export

Symboles et chemins spécifiquement interdits :

- `backend/app/services/natal/calculation_service.py::sign_rulerships = {`
- `payload.setdefault("sign_rulerships", sign_rulerships)`
- `payload["house_axes"] = [` dans le service natal
- `payload["aspect_orb_rules"] = [` dans le service natal
- `EventDetector.ASPECTS_V1` comme source active d'aspects si les définitions runtime sont disponibles
- `EnrichedAstroEventsBuilder.ASPECTS` comme mapping actif dupliqué
- `_ASPECT_TONES` pour des aspects DB-backed sans classification
- nouveau fichier `requirements.txt`

## 11. Removal Classification Rules

La classification doit être déterministe :

- `canonical-active`: l'élément est référencé par le code de production first-party ou il est le propriétaire canonique.
- `external-active`: l'élément est référencé par la documentation publique, les templates d'e-mails, des liens générés, des clients ou une preuve d'audit.
- `historical-facade`: l'élément délègue à une implémentation canonique uniquement pour préserver une ancienne surface.
- `dead`: l'élément n'a aucune référence dans le code de production, les tests, la documentation, les contrats générés et les surfaces externes connues.
- `needs-user-decision`: une ambiguïté persiste après les scans obligatoires et doit bloquer la suppression.

Matrice de décision de classification :

| Classification | Décisions autorisées | Règle |
|---|---|---|
| `canonical-active` | `keep` | Ne doit pas être supprimé. |
| `external-active` | `keep`, `needs-user-decision` | Ne doit pas être supprimé sans décision utilisateur explicite. |
| `historical-facade` | `delete`, `needs-user-decision` | Doit être supprimé quand aucun blocage externe ne subsiste. Ne doit pas être repointé. |
| `dead` | `delete` | Doit être supprimé. |
| `needs-user-decision` | `needs-user-decision` | Doit bloquer l'implémentation jusqu'à décision. |

## 12. Removal Audit Format

Chemin obligatoire de la table d'audit :

- `_condamad/stories/CS-181-supprimer-constantes-astrologiques-hardcodees/hardcoded-astrology-before.md`

Table d'audit obligatoire :

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Décisions autorisées : `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Chaque élément supprimé doit avoir une preuve issue de scans de références de code et de tests ciblés.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Maîtrises signes | `PredictionReferenceRepository.get_sign_rulerships_from_dignities` + `DignityReferenceSet.sign_rulerships` | `services/natal` fallback dict |
| Axes maisons | `AstrologyRuntimeReference.house_axes` | listes synthétiques dans services |
| Aspects et orbes | `AspectDefinitionRuntimeData`, `AspectOrbRuleRuntimeData`, rulesets prediction | `ASPECTS_V1`, `ASPECTS`, fallback orbe `2.0` |
| Planètes et IDs SwissEph | `planet_catalog.py` et seed `astral_planets.json` | dicts locaux de corps majeurs |

## 14. Delete-Only Rule

Les éléments classés comme supprimables doivent être supprimés, pas repointés.
They must be deleted, not repointed.

Interdit :

- rediriger vers l'endpoint canonique
- préserver un wrapper
- ajouter un alias de compatibilité
- garder une route dépréciée active
- préserver l'ancien chemin via un ré-export
- preserve the old path through a re-export
- remplacer la suppression par un comportement soft-disable

## 15. External Usage Blocker

Si un élément est classé `external-active`, il ne doit pas être supprimé.
L'agent dev doit s'arrêter ou enregistrer une décision utilisateur explicite.
If an item is `external-active`, it must not be deleted without a user decision.

## 16. Generated Contract Check

- Vérification des contrats générés : non applicable
- Raison : aucune API générée, aucun manifeste de routes, schéma, contrat public ou client généré n'est intentionnellement affecté.
  OpenAPI and generated artifact absence are explicit: no generated API/client/schema artifact is modified by this story.

## 17. Files to Inspect First

Codex doit inspecter avant d'éditer :

- `backend/app/services/natal/calculation_service.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/prediction/event_detector.py`
- `backend/app/domain/prediction/enriched_astro_events_builder.py`
- `backend/app/domain/prediction/public_astro_vocabulary.py`
- `backend/app/tests/unit/test_astrology_reference_catalog_guard.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/tests/factories/astrology_runtime_reference_factory.py`

## 18. Expected Files to Modify

Likely files:
Fichiers probables :

- `backend/app/services/natal/calculation_service.py` - suppression du fallback legacy et erreurs explicites.
- `backend/app/domain/prediction/event_detector.py` - dérivation des aspects/orbes depuis contexte runtime ou suppression des duplications.
- `backend/app/domain/prediction/enriched_astro_events_builder.py` - suppression/classification des mappings d'aspects et orbes fixes.
- `backend/app/domain/prediction/public_astro_vocabulary.py` - suppression ou classification des étoiles/tonalités non DB-backed.
- `backend/app/tests/unit/test_astrology_reference_catalog_guard.py` - guard anti-réintroduction.
- `backend/app/tests/unit/test_natal_calculation_service.py` - fixtures runtime complètes.

Likely tests:
Tests probables :

- `backend/app/tests/unit/test_natal_calculation_service.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_repository.py`
- `backend/app/tests/unit/test_astrology_reference_catalog_guard.py`
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`
- `backend/tests/unit/prediction/test_public_astro_daily_events.py`
- `backend/tests/unit/prediction/test_enriched_astro_events_builder.py`
- `backend/app/tests/unit/test_transit_signal_v3.py`

Files not expected to change:
Fichiers qui ne devraient pas changer :

- `frontend/**` - story backend uniquement.
- `backend/requirements.txt` - interdit par les règles du dépôt.
- `backend/migrations/versions/**` - aucun changement de schéma attendu sauf si une source canonique manquante est prouvée et approuvée.

## 19. Dependency Policy

- New dependencies: none
- Nouvelles dépendances : aucune
- Changements de dépendances autorisés uniquement s'ils sont listés ici avec justification.

## 20. Validation Plan

Exécuter ou justifier chaque commande ignorée :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q app/tests/unit/test_natal_calculation_service.py app/tests/unit/test_astrology_runtime_reference_repository.py
pytest -q app/tests/unit/test_astrology_reference_catalog_guard.py app/tests/unit/test_astrology_runtime_reference_guard.py
pytest -q app/tests/unit/test_astrology_prediction_boundary.py
pytest -q tests/unit/prediction/test_public_astro_daily_events.py tests/unit/prediction/test_enriched_astro_events_builder.py app/tests/unit/test_transit_signal_v3.py
rg -n "sign_rulerships\s*=\s*\{|payload\.setdefault\(\"sign_rulerships\"|payload\[\"house_axes\"\]\s*=|payload\[\"aspect_orb_rules\"\]\s*=" app/services/natal -g "*.py"
rg -n "ASPECTS_V1|ASPECTS\s*=\s*\{|orb_max_fallback.*2\.0|_ASPECT_TONES|_STAR_DATA" app/domain/astrology app/domain/prediction -g "*.py"
rg -n "app\.domain\.prediction|app\.services\.prediction" app/domain/astrology -g "*.py"
```

Résultat attendu des scans : aucun résultat pour les constantes DB-backed supprimées, hors tests et entrées documentées dans le registre d'exceptions.

## 21. Regression Risks

- Risque : les tests mockés passaient grâce au fallback legacy et deviennent instables.
  - Guardrail : remplacer les mocks par des factories runtime complètes et ajouter un test d'erreur explicite.
- Risque : `domain/prediction` perd des événements daily faute de référentiel chargé.
  - Guardrail : tests daily ciblés et blocage si le contexte runtime n'expose pas encore l'information.
- Risque : une constante technique est supprimée alors qu'elle représente une contrainte astronomique non DB-backed.
  - Guardrail : registre d'exceptions exact avec décision de permanence.
- Risque : le scan anti-retour devient trop large et bloque des fixtures légitimes.
  - Guardrail : guard AST borné au code applicatif, exclusion explicite des tests/fixtures historiques.

## 22. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Implémenter uniquement cette story.
- Ne pas élargir le domaine.
- Ne pas introduire de nouvelles dépendances sauf si elles sont explicitement listées.
- Ne pas marquer une tâche comme terminée sans preuve de validation.
- Si un AC ne peut pas être satisfait, arrêter et enregistrer le blocage.
- Ne pas préserver un comportement legacy par facilité.
- Ne pas contourner la suppression via repointing, soft-disable, wrapper, alias, fallback ou ré-export.
- Ne pas accepter `PASS with limitation`, broad allowlists, wildcard exceptions, unclassified fallback,
  compatibility, legacy, migration-only, shim, alias, placeholder task, or hidden residual work.
- Toutes les commandes Python doivent être exécutées après `.\.venv\Scripts\Activate.ps1`.

## 23. References

- `_condamad/stories/regression-guardrails.md` - invariants backend astrology et DB-backed.
- `_condamad/stories/CS-171-converger-referentiels-astrologie-db-json/00-story.md` - convergence référentiels DB/JSON.
- `_condamad/stories/CS-172-big-bang-reference-runtime-astrology/00-story.md` - contrats runtime immutables.
- `_condamad/stories/CS-179-fermer-i18n-prediction-astrologique/00-story.md` - fermeture des mappings astrologiques côté prediction.
- `backend/app/services/natal/calculation_service.py` - fallback legacy explicitement signalé par l'utilisateur.
