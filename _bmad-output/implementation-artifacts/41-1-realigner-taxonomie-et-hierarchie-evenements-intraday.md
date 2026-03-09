# Story 41.1 : Réaligner la taxonomie et la hiérarchie des événements intraday

Status: done

## Story

En tant que mainteneur backend du moteur de prédiction,
je veux réaligner les `event_type`, les priorités et les poids entre le seed ruleset et le runtime,
afin que le moteur sache distinguer un vrai signal intraday d'un bruit technique et que les pivots forts reposent sur une hiérarchie cohérente.

## Acceptance Criteria

### AC1 — Le runtime et le seed parlent la même taxonomie d'événements

- [x] Les événements produits par `EventDetector._create_event()` utilisent des codes explicitement supportés par le ruleset actif, ou un mapping déterministe documenté entre codes runtime et codes seedés
- [x] Le moteur n'utilise plus par défaut `priority=50` / `base_weight=1.0` pour la majorité des aspects à cause d'un mismatch de nommage
- [x] Les tests couvrent au minimum les familles `exact`, `enter_orb`, `exit_orb`, `moon_sign_ingress`, `asc_sign_change`, `planetary_hour_change`

### AC2 — Les priorités reflètent la valeur produit du signal

- [x] Les événements structurants reçoivent une priorité supérieure au seuil de pivot uniquement quand ils ont une vraie valeur produit
- [x] `planetary_hour_change`, `enter_orb` et `exit_orb` restent en dessous du seuil de pivot critique par défaut
- [x] Les aspects exacts peuvent être différenciés selon la cible ou la famille (angle, luminaire, personnelle), mais sans ambiguïté entre seed et runtime

### AC3 — Un événement secondaire isolé ne devient plus un pivot critique

- [x] Le détecteur de pivots ne peut plus promouvoir un événement secondaire seul en "critique" sans changement significatif de signal
- [x] Les drivers secondaires peuvent enrichir un pivot existant, mais pas créer seuls un moment fort produit

### AC4 — Le seed V2 reste idempotent et cohérent

- [x] Le seed `seed_31_prediction_reference_v2.py` crée ou répare les types d'événements et paramètres sans divergence avec le runtime
- [x] Les priorités et `base_weight` seedés sont explicites et testés

### AC5 — La non-régression daily prediction est couverte

- [x] Les suites ciblées daily prediction restent vertes après réalignement de la taxonomie
- [x] Des tests unitaires verrouillent la cohérence `event_type -> priority/base_weight -> pivot behavior`

## Tasks / Subtasks

### T1 — Auditer et normaliser les codes d'événements

- [x] Choisir une stratégie unique (voir Dev Notes §Stratégies) et la documenter dans le code
- [x] Implémenter la stratégie choisie dans `EventDetector`
- [x] Documenter la taxonomie retenue dans un commentaire de classe ou docstring `EventDetector`

### T2 — Revoir la hiérarchie de priorité intraday

- [x] Mettre à jour les priorités dans `seed_31_prediction_reference_v2.py` (grille proposée en Dev Notes)
- [x] Vérifier la cohérence avec `TurningPointDetector.PRIORITY_PIVOT_THRESHOLD = 65`
- [x] S'assurer qu'aucun événement purement technique ne peut seul déclencher un pivot utilisateur fort

### T3 — Mettre à jour le seed V2

- [x] Modifier `backend/scripts/seed_31_prediction_reference_v2.py`
- [x] Mettre à jour `event_types_data` : codes, groupes, priorités et poids cohérents
- [x] Vérifier le compteur attendu `ruleset_event_types: 16` (ligne 44) — ajuster si le nombre de types change
- [x] Conserver l'idempotence et les chemins de réparation (`delete` + `add`) existants

### T4 — Durcir le runtime

- [x] Ajouter un log WARNING explicite (ou raise) quand `_create_event` tombe sur le fallback `priority=50`
- [x] Supprimer le recours silencieux au fallback générique quand il masque un problème de taxonomie
- [x] Si stratégie Normalisation : ajouter la table de mapping dans `EventDetector` (constante de classe)

### T5 — Tests

- [x] Mettre à jour `test_event_detector.py` : injecter des `event_types` non-vides dans `mock_ctx` pour couvrir le chemin nominal
- [x] Tester le mapping taxonomie (code runtime → code seedé, ou routing discriminé)
- [x] Tester priorité / `base_weight` par famille d'événements
- [x] Tester qu'un `planetary_hour_change` seul ne déclenche pas de pivot `high_priority_event`
- [x] Vérifier les tests d'intégration daily prediction ciblés après seed appliqué

## Dev Notes

### Cause racine — audit du code (2026-03-09)

**Mismatch de taxonomie confirmé dans le code :**

| Code émis par `EventDetector` | Code seedé dans `RulesetEventTypeModel` | Match ? |
|---|---|---|
| `exact` | `aspect_exact_to_angle`, `aspect_exact_to_luminary`, `aspect_exact_to_personal` | ✗ |
| `enter_orb` | `aspect_enter_orb` | ✗ |
| `exit_orb` | `aspect_exit_orb` | ✗ |
| `moon_sign_ingress` | `moon_sign_ingress` | ✓ |
| `asc_sign_change` | `asc_sign_change` | ✓ |
| `planetary_hour_change` | `planetary_hour_change` | ✓ |

**Lookup runtime** (`event_detector.py` ligne 402) :
```python
et_data = self.ctx.ruleset_context.event_types.get(event_type)
priority = et_data.priority if et_data else 50
base_weight = et_data.base_weight if et_data else 1.0
```
→ `exact`, `enter_orb`, `exit_orb` → toujours `priority=50` / `base_weight=1.0` (non trouvés dans le ruleset).

**Problème de priorités dans le seed** (`seed_31_prediction_reference_v2.py` ligne 148) :
```python
priority=0,  # ← TOUS les événements seedés ont priority=0 !
```
`TurningPointDetector.PRIORITY_PIVOT_THRESHOLD = 65` → aucun événement ne peut jamais déclencher un pivot `high_priority_event`. Le pivot via `delta_note` et `top3_change` fonctionne, mais pas via événement haute priorité.

**Test existant** (`test_event_detector.py` ligne 30) :
```python
ctx.ruleset_context.event_types = {}  # dict vide → toujours fallback
```
→ Les tests actuels ne couvrent jamais le chemin nominal taxonomy.

### Stratégies — choix à faire en T1

**Stratégie A — Aligner les codes runtime sur le seed (recommandée) :**
- `EventDetector._create_event()` reçoit déjà `target` (la planète natale). Discriminer :
  - `target in {"Asc", "MC"}` → émettre `aspect_exact_to_angle`
  - `target in {"Sun", "Moon"}` → émettre `aspect_exact_to_luminary`
  - autres planètes personnelles → émettre `aspect_exact_to_personal`
  - `enter_orb` → `aspect_enter_orb`
  - `exit_orb` → `aspect_exit_orb`
- Avantage : le seed reste maître, le runtime s'adapte. La granularité seed `angle/luminary/personal` permet des priorités différenciées.
- Points d'attention : mettre à jour toutes les comparaisons `event.event_type == "exact"` dans le reste du code (orchestrateur, tests, editorial).

**Stratégie B — Table de normalisation dans le runtime :**
- Conserver les codes courts dans le runtime, ajouter une méthode `_normalize_event_code(event_type, target)` → code long
- Lookup se fait sur le code normalisé. Moins de refactoring, mais double couche.

**Recommandation :** Stratégie A — plus propre, cohérente avec le design du seed.

### Grille de priorités proposée pour le seed V2

| Code | Groupe | Priorité proposée | base_weight | Commentaire |
|---|---|---|---|---|
| `aspect_exact_to_angle` | aspect | 80 | 2.0 | Au-dessus du seuil de pivot (65) |
| `aspect_exact_to_luminary` | aspect | 75 | 1.8 | Au-dessus du seuil |
| `aspect_exact_to_personal` | aspect | 68 | 1.5 | Légèrement au-dessus du seuil |
| `aspect_enter_orb` | aspect | 40 | 1.0 | En dessous du seuil — enrichit uniquement |
| `aspect_exit_orb` | aspect | 25 | 0.5 | En dessous du seuil |
| `moon_sign_ingress` | ingress | 72 | 1.5 | Au-dessus du seuil |
| `asc_sign_change` | ingress | 78 | 2.0 | Au-dessus du seuil — structurant |
| `planetary_hour_change` | timing | 20 | 0.8 | Bien en dessous du seuil |

> La grille est indicative — le dev peut l'ajuster, mais les seuils DOIVENT rester cohérents avec `PRIORITY_PIVOT_THRESHOLD = 65`.

### Fichiers à toucher

- `backend/app/prediction/event_detector.py` — méthode `_create_event()` + logique de discrimination (T1, T4)
- `backend/app/prediction/turning_point_detector.py` — vérification uniquement, pas de modification a priori (seuil déjà correct)
- `backend/scripts/seed_31_prediction_reference_v2.py` — `event_types_data` : codes, priorités, poids (T3)
- `backend/app/tests/unit/test_event_detector.py` — fixtures `mock_ctx` + nouveaux cas (T5)
- `backend/app/tests/unit/test_turning_point_detector.py` — cas no-pivot pour événement secondaire seul (T5)
- `backend/app/tests/integration/test_seed_31_prediction_v2.py` — vérifier compteur si nombre de types change (T3)

### Fichiers potentiellement impactés par Stratégie A (à vérifier)

Chercher `event_type == "exact"` ou `.event_type in ["exact",` dans :
- `backend/app/prediction/engine_orchestrator.py`
- `backend/app/prediction/editorial_builder.py`
- Tout test d'intégration utilisant des fixtures d'événements

### Contexte git récent

Dernier commit (`bfa03e2` — "Repair local prediction seed recovery") a modifié :
- `backend/app/services/daily_prediction_service.py` (+111 lignes) — robustesse seed recovery
- `backend/app/services/reference_data_service.py`
- `backend/app/tests/unit/test_daily_prediction_service.py` (+130 lignes)

Ne pas toucher à ces fichiers sauf nécessité absolue — ils viennent d'être stabilisés.

### Patterns de code à respecter

- **Logging** : utiliser `logger.warning(...)` avec `planet=%s aspect=%s` format (voir `_orb_max` ligne 373)
- **Constantes de classe** : les tables de mapping vont dans des `dict` de classe (`ASPECTS_V1`, `CHALDEAN_ORDER`, `V1_NATAL_TARGETS`)
- **Fallback explicite** : si un event_type n'est pas trouvé après normalisation, log WARNING + ne pas masquer silencieusement
- **Idempotence seed** : le pattern `delete + add` existant dans le seed garantit l'idempotence — le conserver

### Compteur attendu dans le seed

```python
"ruleset_event_types": 16,  # 8 par ruleset (1.0.0 et 2.0.0)
```
Si le nombre de types d'événements change (ex: on en ajoute ou retire), mettre à jour ce compteur et la vérification associée.

### Project Structure Notes

- Moteur de prédiction : `backend/app/prediction/`
- Scripts de seed : `backend/scripts/`
- Tests unitaires : `backend/app/tests/unit/`
- Tests d'intégration : `backend/app/tests/integration/`
- Schemas partagés : `backend/app/prediction/schemas.py` (AstroEvent, etc.)

### References

- [Source: backend/app/prediction/event_detector.py#L391-L417] — `_create_event()` fallback
- [Source: backend/app/prediction/event_detector.py#L384-L389] — `_lookup_mapping_value()`
- [Source: backend/app/prediction/turning_point_detector.py#L23] — `PRIORITY_PIVOT_THRESHOLD = 65`
- [Source: backend/app/prediction/turning_point_detector.py#L65-L74] — logique `high_priority_event`
- [Source: backend/scripts/seed_31_prediction_reference_v2.py#L131-L150] — `event_types_data` avec `priority=0`
- [Source: backend/app/tests/unit/test_event_detector.py#L30] — `event_types = {}` (dict vide, toujours fallback)
- [Source: _bmad-output/planning-artifacts/epics.md#Epic-41] — Epic 41 complet

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

Néant — implémentation directe sans blocages.

### Completion Notes List

- **Stratégie A retenue** : l'`EventDetector` émet désormais des codes discriminés (`aspect_exact_to_angle`, `aspect_exact_to_luminary`, `aspect_exact_to_personal`, `aspect_enter_orb`, `aspect_exit_orb`) alignés sur le seed, plutôt que les codes courts `exact`/`enter_orb`/`exit_orb`.
- **Constantes de classe ajoutées** : `ANGLE_TARGETS`, `LUMINARY_TARGETS`, `EXACT_EVENT_TYPES` — la logique de discrimination est encapsulée dans `_discriminate_exact_code(target)`.
- **Fallback explicite** : `_create_event()` loggue un WARNING quand l'`event_type` n'est pas trouvé dans le ruleset, au lieu de tomber silencieusement sur `priority=50`.
- **Seed V2 mis à jour** : les priorités sont maintenant explicites et calibrées autour de `PRIORITY_PIVOT_THRESHOLD = 65`. Les événements structurants (aspects exacts, ingresses) sont au-dessus du seuil, les événements techniques (`planetary_hour_change`, `enter_orb`, `exit_orb`) en dessous.
- **Orchestrateur mis à jour** : la vérification `event.event_type != "exact"` utilise désormais `EventDetector.EXACT_EVENT_TYPES` pour le tri des events à raffiner.
- **Tests** : 7 nouveaux tests ajoutés couvrant la discrimination par famille, les priorités nominales, et la garantie qu'un `planetary_hour_change` seul ne crée pas de pivot.
- **Non-régression** : 79 tests passent (les 2 échecs pré-existants ont été confirmés avant nos changements).

### File List

- `backend/app/prediction/event_detector.py`
- `backend/app/prediction/engine_orchestrator.py`
- `backend/scripts/seed_31_prediction_reference_v2.py`
- `backend/app/tests/unit/test_event_detector.py`
- `backend/app/tests/integration/test_intraday_refinement_integration.py`
- `backend/app/tests/unit/test_engine_orchestrator.py`
- `backend/app/tests/regression/fixtures/*.json`
- `backend/app/tests/regression/generate_fixtures.py`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-03-09 : Story créée à partir de l'audit intraday produit/backend.
- 2026-03-09 : Story enrichie via analyse exhaustive du code source — mismatch taxonomie confirmé, grille de priorités proposée, stratégies documentées.
- 2026-03-09 : Implémentation complète — Stratégie A (alignement runtime → seed), seed V2 avec priorités, tests de taxonomie, non-régression verte.
- 2026-03-09 : Revue de code (AI) — Correction des helpers de tests (`StubTemplateEngine`, `_loaded_context`), correction de la logique `required_event_types` dans `generate_fixtures.py` pour Mercury, régénération des fixtures de non-régression.
