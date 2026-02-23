# Story 15.4: Interprétation textuelle du thème natal via AI Engine

Status: done

## Story

As a utilisateur ayant généré son thème natal,
I want recevoir une interprétation textuelle riche et personnalisée de mon thème,
So that je comprenne la signification de mes positions planétaires, aspects et maisons.

## Contexte et Objectifs

Actuellement, le service `UserNatalChartService` génère un thème natal avec des **données brutes** :
- Positions planétaires (Soleil en Bélier à 15°, Lune en Cancer à 22°, etc.)
- Aspects (Soleil carré Mars, Lune trigone Vénus, etc.)
- Maisons (Ascendant Gémeaux, MC Poissons, etc.)

**Problème identifié :**
Ces données sont techniques et difficiles à comprendre pour un utilisateur lambda. Il manque une **interprétation textuelle** générée par l'IA qui explique la signification du thème.

**Solution :**
Utiliser le AI Engine avec le use_case `natal_chart_interpretation` (template existant) pour générer une interprétation riche et personnalisée.

**Pré-requis :**
- Story 15.1 (AI Engine + OpenAI gateway) ✅
- Story 15.2 (Rate limiting, cache) ✅  
- Story 15.3 (Migration chat/guidance) — peut être en parallèle

## Acceptance Criteria

### AC1: Service d'interprétation du thème natal
**Given** un utilisateur avec un thème natal calculé (`NatalResult`)
**When** il demande l'interprétation de son thème via le nouveau service
**Then** le AI Engine est appelé avec `use_case=natal_chart_interpretation`
**And** le contexte contient le résumé du thème (positions, aspects, maisons, ascendant)
**And** une interprétation textuelle structurée est retournée

### AC2: Conversion NatalResult vers résumé exploitable
**Given** un `NatalResult` contenant les données astronomiques brutes
**When** le service prépare le contexte pour le AI Engine
**Then** un `natal_chart_summary` lisible est généré avec :
- Signe solaire et position (depuis `planet_positions[planet_code="sun"].sign_code` + `longitude`)
- Signe lunaire et position (depuis `planet_positions[planet_code="moon"].sign_code` + `longitude`)
- Ascendant (signe dérivé de `houses[number=1].cusp_longitude` via `int(longitude / 30) % 12`)
- Aspects majeurs (conjonctions, carrés, oppositions, trigones) depuis `aspects[].aspect_code + planet_a + planet_b + orb`
- Placements des maisons principales (I, IV, VII, X) avec signe dérivé de `cusp_longitude`
- Lieu de naissance issu du **profil utilisateur** (nécessite un fetch séparé de `UserBirthProfileService`)

### AC3: Structure de l'interprétation
**Given** le template `natal_chart_interpretation_v1.jinja2` existant
**When** le AI Engine génère l'interprétation
**Then** le texte suit la structure définie :
1. Synthèse en 2-3 phrases
2. Points clés (Soleil, Lune, Ascendant, aspects majeurs)
3. Conseils actionnables et positifs
4. Note de prudence (disclaimer)
**And** le ton est bienveillant et non-alarmiste

### AC4: Endpoint REST pour l'interprétation
**Given** un utilisateur authentifié avec un thème natal existant
**When** il appelle `GET /v1/users/me/natal-chart/interpretation`
**Then** l'interprétation textuelle est retournée au format JSON
**And** les métadonnées incluent `chart_id`, `generated_at`, `cached`
**And** les codes d'erreur possibles sont : `401` (non authentifié), `404` (thème absent), `429` (rate limit AI Engine), `503` (AI Engine indisponible)

### AC5: Intégration optionnelle dans l'endpoint existant
**Given** l'endpoint existant `GET /v1/users/me/natal-chart/latest`
**When** l'utilisateur ajoute le paramètre `?include_interpretation=true`
**Then** la réponse inclut un champ `interpretation` avec le texte généré
**And** si le paramètre est absent ou false, le champ n'est pas inclus

### AC6: Gestion des données incomplètes
**Given** un thème natal avec des données incomplètes (heure ou lieu manquant)
**When** l'interprétation est demandée
**Then** le AI Engine adapte l'interprétation avec les limitations appropriées
**And** un avertissement est inclus concernant les données manquantes (mode dégradé)

### AC7: Cache de l'interprétation
**Given** un thème natal déjà interprété (même `chart_id`)
**When** l'interprétation est demandée à nouveau
**Then** l'interprétation est servie depuis le cache Redis (si activé)
**And** `meta.cached: true` est retourné

## Tasks / Subtasks

### Subtask 15.4.1: Service d'interprétation du thème natal
- [x] Créer `backend/app/services/natal_interpretation_service.py` (AC: #1)
  - [x] Classe `NatalInterpretationService`
  - [x] Méthode principale : `async interpret_chart(natal_chart: UserNatalChartReadData, birth_profile: UserBirthProfileData, user_id: int, request_id: str) -> NatalInterpretationData`
    - Reçoit le chart ET le profil déjà fetchés par l'endpoint (évite le double fetch DB)
    - Génère le summary, appelle le AI Engine, parse la réponse
  - [x] **Pas de** `interpret_for_user(db, user_id)` — le fetch est géré par l'endpoint appelant
- [x] Définir les modèles Pydantic pour l'interprétation (AC: #1)
  - [x] `NatalInterpretationData` avec `text` (texte brut AI complet), `summary`, `key_points`, `advice`, `disclaimer` (champs parsés depuis `text`), `metadata`
  - [x] `NatalInterpretationMetadata` avec `chart_id`, `generated_at`, `cached`, `degraded_mode`, `tokens_used`, `latency_ms`

### Subtask 15.4.2: Conversion NatalResult vers natal_chart_summary
- [x] Créer fonction `build_natal_chart_summary(natal_result: NatalResult, birth_place: str) -> str` (AC: #2)
  - [x] Extraire signe solaire : `next(p for p in natal_result.planet_positions if p.planet_code == "sun")` → `.sign_code + .longitude`
  - [x] Extraire signe lunaire : idem avec `planet_code == "moon"`
  - [x] Calculer le signe de l'Ascendant depuis `cusp_longitude` de la maison 1 :
    ```python
    SIGNS = ["aries","taurus","gemini","cancer","leo","virgo",
             "libra","scorpio","sagittarius","capricorn","aquarius","pisces"]
    sign = SIGNS[int(house1.cusp_longitude / 30) % 12]
    ```
  - [x] Lister les aspects majeurs (conjonction, carré, opposition, trigone, sextile) depuis `aspects[].aspect_code + planet_a + planet_b + orb`
  - [x] Résumer les maisons angulaires (I, IV, VII, X) avec signe dérivé de `cusp_longitude` (même formule)
  - [x] Inclure le `birth_place` dans l'en-tête du résumé (fourni par l'endpoint via `UserBirthProfileData`)
- [x] Formater le résumé de manière lisible pour le prompt
- [x] Tests de conversion (AC: #2) — inclure un test de dérivation signe depuis longitude

### Subtask 15.4.3: Intégration avec le AI Engine
- [x] Appeler `await generate_text(request, request_id=..., trace_id=..., user_id=...)` (AC: #1, #3)
  - **⚠️ `generate_text()` est `async` — le service et les endpoints appelants doivent être `async def`**
  - [x] use_case: `natal_chart_interpretation`
  - [x] context.natal_chart_summary: résumé généré par `build_natal_chart_summary()`
  - [x] context.birth_data: `{"date": str, "time": str, "place": str}` depuis le profil utilisateur
  - [x] input.tone: "warm" (par défaut)
  - [x] `request_id`: généré via `uuid.uuid4().hex` dans l'endpoint, propagé au service
  - [x] `trace_id`: identique à `request_id` (ou `request.headers.get("X-Trace-Id", request_id)`)
  - [x] `user_id`: `current_user.id` depuis l'endpoint, passé au service via paramètre
- [x] Parser la réponse structurée depuis `GenerateResponse.text` (AC: #3)
  - Le template impose 4 sections numérotées : synthèse → points clés → conseils → note de prudence
  - Stratégie : parser par section markdown (regex sur `^\d+\.` ou délimiteurs de ligne)
  - `summary` = premier paragraphe (avant section 2)
  - `key_points` = lignes de la section 2 (splitting par `\n-` ou `\n•`)
  - `advice` = lignes de la section 3
  - `disclaimer` = contenu de la section 4
  - `text` = `GenerateResponse.text` complet (brut, sans modification)
- [x] Gérer les erreurs AI Engine :
  - `UnknownUseCaseError` → 500 (ne devrait pas arriver si use_case est correct)
  - `asyncio.TimeoutError` / provider timeout → 503
  - Rate limit (429 du provider) → propager 429 vers l'appelant

### Subtask 15.4.4: Endpoint dédié `/v1/users/me/natal-chart/interpretation`
- [x] Créer route dans `backend/app/api/v1/routers/users.py` (AC: #4)
  - [x] **`async def get_me_natal_chart_interpretation(...)`** — `async def` obligatoire (appel `await` vers AI Engine)
  - [x] `GET /v1/users/me/natal-chart/interpretation`
  - [x] Authentification requise
  - [x] Séquence : fetch chart (`UserNatalChartService.get_latest_for_user`) → fetch profil (`UserBirthProfileService.get_for_user`) → `await NatalInterpretationService.interpret_chart(...)`
  - [x] Retourne `NatalInterpretationResponse`
  - [x] Codes d'erreur : `401`, `404` (chart absent), `429` (rate limit), `503` (AI Engine indisponible)
  - [x] `responses={401: ..., 404: ..., 429: ..., 503: ...}` dans le décorateur
- [x] Tests d'intégration de l'endpoint (AC: #4)

### Subtask 15.4.5: Paramètre optionnel dans l'endpoint existant
- [x] Modifier `GET /v1/users/me/natal-chart/latest` (AC: #5) — **c'est l'endpoint existant `get_me_latest_natal_chart`**
  - [x] Convertir le handler en **`async def`** (actuellement `def` synchrone)
  - [x] Ajouter query param `include_interpretation: bool = False`
  - [x] Si true : fetch profil + `await NatalInterpretationService.interpret_chart(...)` + ajouter champ `interpretation` dans la réponse
  - [x] Gérer le timeout gracieusement : `try/except asyncio.TimeoutError` → retourner le chart sans `interpretation` (pas une erreur 5xx)
  - [x] Ajouter `429: {"model": ErrorEnvelope}` dans les `responses` du décorateur
- [x] Tests avec et sans le paramètre (AC: #5)

### Subtask 15.4.6: Gestion des modes dégradés
- [x] Détecter les données manquantes via le **profil de naissance** `UserBirthProfileData` (AC: #6)
  - `NatalResult` ne porte pas d'information sur les données dégradées — la détection se fait sur le profil
  - [x] Heure par défaut : si `birth_profile.birth_time == "00:00"` → `degraded_mode: "no_time"`
  - [x] Lieu par défaut : si `birth_profile.birth_place` est vide ou valeur sentinelle → `degraded_mode: "no_location"`
  - [x] Vérifier avec story 14.2 quelle valeur sentinelle est utilisée pour le lieu absent
- [x] Adapter le contexte `birth_data` pour informer l'IA des limitations :
  - Si `no_time` : `birth_data.time = "Non connue (interprétation des maisons approximative)"`
  - Si `no_location` : `birth_data.place = "Non connu (Ascendant non disponible)"`
- [x] Ajouter `degraded_mode` dans `NatalInterpretationMetadata`
- [x] Tests modes dégradés (AC: #6)

### Subtask 15.4.7: Cache de l'interprétation
- [x] Le cache est géré automatiquement par le AI Engine via `CacheService` (story 15.2) — **aucun code de cache à écrire dans cette story** (AC: #7)
  - [x] La clé de cache est calculée par `CacheService` depuis `(use_case, input_dict, context_dict)` — transparent pour le service appelant
  - [x] Note : `temperature=0.7` pour `natal_chart_interpretation` → cache désactivé à cette température (seuil `CACHEABLE_TEMPERATURE_THRESHOLD = 0.0` dans `generate_service.py`)
  - [x] Documenté : le cache est désactivé pour ce use_case car temperature > 0
- [x] `meta.cached` dans la réponse = `GenerateResponse.meta.cached` (propagé automatiquement)
- [x] Tests cache hit/miss (AC: #7) — tester avec un mock de `CacheService`

## Dev Notes

### Architecture

```
┌─────────────────────────────────────┐
│        Frontend React               │
│  (NatalChartPage avec interprétation)│
└─────────────────┬───────────────────┘
                  │ GET /v1/users/me/natal-chart/latest?include_interpretation=true
                  │ ou GET /v1/users/me/natal-chart/interpretation
                  ▼
┌─────────────────────────────────────┐
│    UserNatalChartService            │
│    (génération thème natal)         │
└─────────────────┬───────────────────┘
                  │ NatalResult
                  ▼
┌─────────────────────────────────────┐
│  NatalInterpretationService         │
│  (interprétation textuelle)         │
│  ├─ build_natal_chart_summary()     │
│  └─ interpret_chart()               │
└─────────────────┬───────────────────┘
                  │ GenerateRequest (use_case: natal_chart_interpretation)
                  ▼
┌─────────────────────────────────────┐
│         AI Engine                   │
│  ├─ Prompt Registry                 │
│  ├─ OpenAI Client                   │
│  └─ Cache (Redis)                   │
└─────────────────────────────────────┘
```

### Format du natal_chart_summary

```
Thème natal de [Prénom] né(e) le [date] à [heure] à [lieu]:

SOLEIL: Bélier à 15°23' (Maison X)
- Identité, ego, vitalité
- Carré avec Mars en Cancer

LUNE: Cancer à 22°45' (Maison I)  
- Émotions, besoins fondamentaux
- Trigone avec Vénus en Poissons

ASCENDANT: Gémeaux à 8°12'
- Apparence, première impression

ASPECTS MAJEURS:
- Soleil carré Mars (orbe 3°) — tension action/volonté
- Lune trigone Vénus (orbe 4°) — harmonie émotionnelle
- Mercure conjonction Jupiter (orbe 2°) — expansion mentale

MAISONS ANGULAIRES:
- Maison I (Ascendant): Gémeaux — communication, adaptabilité
- Maison IV (Fond du Ciel): Vierge — foyer, racines
- Maison VII (Descendant): Sagittaire — partenariats, relations
- Maison X (Milieu du Ciel): Poissons — carrière, vocation
```

### Modèles Pydantic

```python
class NatalInterpretationData(BaseModel):
    """Données d'interprétation du thème natal."""

    chart_id: str
    text: str           # Texte brut complet retourné par le AI Engine (GenerateResponse.text)
    summary: str        # Parsé depuis text : section 1 (synthèse)
    key_points: list[str]  # Parsé depuis text : lignes de la section 2
    advice: list[str]   # Parsé depuis text : lignes de la section 3
    disclaimer: str     # Parsé depuis text : contenu de la section 4
    metadata: NatalInterpretationMetadata

class NatalInterpretationMetadata(BaseModel):
    """Métadonnées de l'interprétation."""

    generated_at: datetime
    cached: bool        # Depuis GenerateResponse.meta.cached
    degraded_mode: str | None  # "no_time", "no_location", "no_location_no_time" — détecté via profil
    tokens_used: int    # Depuis GenerateResponse.usage.total_tokens
    latency_ms: int     # Depuis GenerateResponse.meta.latency_ms
```

> ⚠️ Le parsing de `summary`, `key_points`, `advice`, `disclaimer` depuis le texte brut doit suivre la structure imposée par le template (4 sections numérotées). Voir Subtask 15.4.3 pour la stratégie de parsing.

### Mapping des données NatalResult

| Champ NatalResult (noms exacts) | Champ natal_chart_summary |
|--------------------------------|--------------------------|
| `planet_positions[planet_code="sun"].sign_code + longitude` | Signe solaire + degrés |
| `planet_positions[planet_code="moon"].sign_code + longitude` | Signe lunaire + degrés |
| `houses[number=1].cusp_longitude → SIGNS[int(lon/30)%12]` | Ascendant (signe dérivé de la longitude) |
| `aspects[].aspect_code + planet_a + planet_b + orb` | Aspects majeurs |
| `houses[number in {1,4,7,10}].cusp_longitude → sign dérivé` | Maisons angulaires |
| `birth_profile.birth_place` (fetch séparé via `UserBirthProfileService`) | Lieu de naissance dans l'en-tête |

> ⚠️ `HouseResult` n'a **pas** de champ `sign`. Le signe doit être calculé depuis `cusp_longitude` via `SIGNS[int(cusp_longitude / 30) % 12]` où `SIGNS` est la liste ordonnée des 12 signes depuis Bélier.

### Gestion des modes dégradés

| Mode | Impact sur l'interprétation |
|------|----------------------------|
| `no_time` | Positions de la Lune et maisons approximatives, avertissement inclus |
| `no_location` | Système de maisons égales, pas d'ascendant précis |
| `no_location_no_time` | Interprétation limitée aux positions planétaires |

### Cache

- **Mécanisme** : Le cache est géré nativement par le AI Engine (`CacheService` de story 15.2)
- **Clé de cache réelle** : calculée par `CacheService` depuis `(use_case, input_dict, context_dict)` — **pas depuis `chart_id`**
  - En pratique : si deux utilisateurs ont le même `natal_chart_summary`, ils partagent le cache (peu probable mais possible)
  - La `cached: true` dans les métadonnées vient de `GenerateResponse.meta.cached`
- **TTL** : configuré dans `CacheService` (story 15.2) — typiquement 1h pour `temperature > 0`
  - Note : `natal_chart_interpretation` a `temperature=0.7` → réponses non déterministes → le cache peut ne pas s'activer selon la config `CacheService`
- **Invalidation naturelle** : si le `natal_chart_summary` change (nouveau thème), la clé de cache diffère automatiquement

### Project Structure Notes

- `NatalInterpretationService` est dans `services/` car il orchestre l'appel au AI Engine
- La conversion `NatalResult` → `natal_chart_summary` peut être dans un helper dédié (`natal_chart_summary_builder.py`)
- L'endpoint dédié est `GET /v1/users/me/natal-chart/interpretation` (nouveau)
- Le paramètre optionnel est sur l'endpoint **existant** `GET /v1/users/me/natal-chart/latest` (pas `/natal-chart`)

### ⚠️ Note Async Critique

`generate_text()` dans `ai_engine/services/generate_service.py` est une **coroutine async**. Par conséquent :
- `NatalInterpretationService.interpret_chart()` doit être `async def`
- Les handlers FastAPI qui l'appellent doivent être convertis en **`async def`** :
  - `get_me_natal_chart_interpretation` (nouveau handler) → `async def`
  - `get_me_latest_natal_chart` (handler existant modifié) → convertir de `def` à `async def`
- FastAPI supporte nativement les handlers `async def` avec `await`

### References

- [Source: docs/agent/story-15-ai-text-engine-bmad.md] — Use case `natal_chart_interpretation`
- [Source: backend/app/ai_engine/prompts/natal_chart_interpretation_v1.jinja2] — Template existant
- [Source: backend/app/services/user_natal_chart_service.py] — Service de génération du thème
- [Source: backend/app/domain/astrology/natal_calculation.py] — Format NatalResult
- [Source: _bmad-output/implementation-artifacts/15-1-ai-text-engine-openai-gateway.md] — AI Engine

### Dépendances

**Stories pré-requises :**
- Story 15.1 (AI Engine - OpenAI Gateway) ✅
- Story 15.2 (Rate limiting, cache) ✅

**Peut être fait en parallèle de :**
- Story 15.3 (Migration chat/guidance)

### Tests DoD

- [x] Conversion NatalResult → summary : 7 tests (positions, aspects, maisons, modes dégradés)
- [x] Service interprétation : 5 tests (succès, erreurs AI Engine, cache, modes dégradés)
- [x] Fonctions utilitaires : 15 tests (_longitude_to_sign, _format_longitude, _detect_degraded_mode, _parse_interpretation_sections)
- [x] Endpoint dédié : 5 tests (200 OK, 404 sans chart, timeout 503, rate limit 429, 401 non authentifié)
- [x] Endpoint existant avec param : 4 tests (avec/sans include_interpretation, appel service, erreur gracieuse)
- [x] Lint : ruff check OK

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5

### Debug Log References

Aucun debug nécessaire.

### Completion Notes List

- ✅ Service `NatalInterpretationService` créé avec méthode async `interpret_chart()`
- ✅ Modèles Pydantic `NatalInterpretationData` et `NatalInterpretationMetadata` définis
- ✅ Fonction `build_natal_chart_summary()` pour conversion NatalResult → résumé textuel
- ✅ Parser `_parse_interpretation_sections()` pour extraire synthèse/points clés/conseils/disclaimer
- ✅ Endpoint dédié `GET /v1/users/me/natal-chart/interpretation` créé (async)
- ✅ Paramètre `include_interpretation` ajouté à `GET /v1/users/me/natal-chart/latest` (converti en async)
- ✅ Gestion des modes dégradés (no_time, no_location, no_location_no_time)
- ✅ Gestion gracieuse des erreurs (timeout retourne chart sans interprétation)
- ✅ 36 tests passent (27 tests unitaires + 9 tests d'intégration)
- ✅ Lint OK (ruff check)
- ⚠️ Cache désactivé pour ce use_case (temperature=0.7 > seuil 0.0)

### Change Log

- 2026-02-22: Implémentation complète de la story 15.4
- 2026-02-22: Code review fixes:
  - Ajout test 401 pour utilisateur non authentifié (HIGH-3)
  - Ajout test appel service pour include_interpretation=true (HIGH-2, MEDIUM-1)
  - Définition constantes UNKNOWN_BIRTH_TIME_SENTINEL et UNKNOWN_LOCATION_SENTINELS (MEDIUM-2)
  - Suppression gestion redondante asyncio.TimeoutError dans endpoint /interpretation (MEDIUM-3)
  - Ajout logs warning quand parsing interprétation < 4 sections (MEDIUM-4)
  - Documentation guidance_service.py dans File List (HIGH-1)

### File List

**Fichiers créés :**
- `backend/app/services/natal_interpretation_service.py`
- `backend/app/tests/unit/test_natal_interpretation_service.py`
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py`

**Fichiers modifiés :**
- `backend/app/api/v1/routers/users.py` — Ajout endpoint `GET /natal-chart/interpretation` (async def) + ajout param `include_interpretation` sur `GET /natal-chart/latest` (conversion en async def)
- `backend/app/services/guidance_service.py` — Refactoring: simplification gestion d'erreurs via `map_adapter_error_to_codes()` (DRY)
