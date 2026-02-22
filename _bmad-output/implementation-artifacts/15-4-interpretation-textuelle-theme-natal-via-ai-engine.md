# Story 15.4: Interprétation textuelle du thème natal via AI Engine

Status: ready-for-dev

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
- Signe solaire et position
- Signe lunaire et position
- Ascendant
- Aspects majeurs (conjonctions, carrés, oppositions, trigones)
- Placements des maisons principales (I, IV, VII, X)

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

### AC5: Intégration optionnelle dans l'endpoint existant
**Given** l'endpoint existant `GET /v1/users/me/natal-chart`
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
- [ ] Créer `backend/app/services/natal_interpretation_service.py` (AC: #1)
  - [ ] Classe `NatalInterpretationService`
  - [ ] Méthode `interpret_for_user(db, user_id) -> NatalInterpretationData`
  - [ ] Méthode `interpret_chart(natal_result) -> str`
- [ ] Définir les modèles Pydantic pour l'interprétation (AC: #1)
  - [ ] `NatalInterpretationData` avec `text`, `summary`, `key_points`, `advice`, `disclaimer`
  - [ ] `NatalInterpretationMetadata` avec `chart_id`, `generated_at`, `cached`, `degraded_mode`

### Subtask 15.4.2: Conversion NatalResult vers natal_chart_summary
- [ ] Créer fonction `build_natal_chart_summary(natal_result: NatalResult) -> str` (AC: #2)
  - [ ] Extraire signe solaire et position en degrés
  - [ ] Extraire signe lunaire et position
  - [ ] Extraire ascendant
  - [ ] Lister les aspects majeurs (conjonction, carré, opposition, trigone, sextile)
  - [ ] Résumer les placements des maisons angulaires (I, IV, VII, X)
- [ ] Formater le résumé de manière lisible pour le prompt
- [ ] Tests de conversion (AC: #2)

### Subtask 15.4.3: Intégration avec le AI Engine
- [ ] Appeler `ai_engine.services.generate_service.generate_text()` (AC: #1, #3)
  - [ ] use_case: `natal_chart_interpretation`
  - [ ] context.natal_chart_summary: résumé généré
  - [ ] context.birth_data: date, heure, lieu
  - [ ] input.tone: "warm" (par défaut)
- [ ] Parser la réponse et structurer l'interprétation (AC: #3)
- [ ] Gérer les erreurs AI Engine (timeout, rate limit, etc.)

### Subtask 15.4.4: Endpoint dédié `/v1/users/me/natal-chart/interpretation`
- [ ] Créer route dans `backend/app/api/v1/routers/users.py` (AC: #4)
  - [ ] `GET /v1/users/me/natal-chart/interpretation`
  - [ ] Authentification requise
  - [ ] Retourne `NatalInterpretationResponse`
- [ ] Tests d'intégration de l'endpoint (AC: #4)

### Subtask 15.4.5: Paramètre optionnel dans l'endpoint existant
- [ ] Modifier `GET /v1/users/me/natal-chart` (AC: #5)
  - [ ] Ajouter query param `include_interpretation: bool = False`
  - [ ] Si true, appeler le service d'interprétation et ajouter le champ
  - [ ] Gérer le timeout gracieusement (retourner le chart sans interprétation si timeout)
- [ ] Tests avec et sans le paramètre (AC: #5)

### Subtask 15.4.6: Gestion des modes dégradés
- [ ] Détecter les données manquantes dans `NatalResult` (AC: #6)
  - [ ] Heure absente (`metadata.degraded_mode: "no_time"`)
  - [ ] Lieu absent (`metadata.degraded_mode: "no_location"`)
- [ ] Adapter le prompt/contexte pour informer l'IA des limitations
- [ ] Ajouter un avertissement dans la réponse
- [ ] Tests modes dégradés (AC: #6)

### Subtask 15.4.7: Cache de l'interprétation
- [ ] Utiliser le cache du AI Engine (story 15.2) (AC: #7)
  - [ ] Clé de cache basée sur `chart_id` ou `input_hash`
  - [ ] TTL configurable (par défaut: 24h pour les interprétations)
- [ ] Retourner `cached: true` dans les métadonnées
- [ ] Tests cache hit/miss (AC: #7)

## Dev Notes

### Architecture

```
┌─────────────────────────────────────┐
│        Frontend React               │
│  (NatalChartPage avec interprétation)│
└─────────────────┬───────────────────┘
                  │ GET /v1/users/me/natal-chart?include_interpretation=true
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
    text: str  # Interprétation complète
    summary: str  # Synthèse 2-3 phrases
    key_points: list[str]  # Points clés
    advice: list[str]  # Conseils actionnables
    disclaimer: str  # Note de prudence
    metadata: NatalInterpretationMetadata
    
class NatalInterpretationMetadata(BaseModel):
    """Métadonnées de l'interprétation."""
    
    generated_at: datetime
    cached: bool
    degraded_mode: str | None  # "no_time", "no_location", "no_location_no_time"
    tokens_used: int
    latency_ms: int
```

### Mapping des données NatalResult

| Champ NatalResult | Champ natal_chart_summary |
|------------------|--------------------------|
| `positions[planet="sun"]` | Signe solaire + degrés |
| `positions[planet="moon"]` | Signe lunaire + degrés |
| `houses[house=1].sign` | Ascendant |
| `aspects[]` | Liste des aspects majeurs |
| `houses[1,4,7,10]` | Maisons angulaires |

### Gestion des modes dégradés

| Mode | Impact sur l'interprétation |
|------|----------------------------|
| `no_time` | Positions de la Lune et maisons approximatives, avertissement inclus |
| `no_location` | Système de maisons égales, pas d'ascendant précis |
| `no_location_no_time` | Interprétation limitée aux positions planétaires |

### Cache

- **Clé de cache** : `natal_interpretation:{chart_id}` ou `natal_interpretation:{input_hash}`
- **TTL** : 24 heures (les interprétations pour un même thème ne changent pas)
- **Invalidation** : Si le thème est regénéré (nouveau `chart_id`), nouvelle interprétation

### Project Structure Notes

- `NatalInterpretationService` est dans `services/` car il orchestre l'appel au AI Engine
- La conversion `NatalResult` → `natal_chart_summary` peut être dans un helper dédié
- L'endpoint utilise l'existant `/v1/users/me/natal-chart` avec un paramètre optionnel

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

- [ ] Conversion NatalResult → summary : 6 tests (positions, aspects, maisons, modes dégradés)
- [ ] Service interprétation : 8 tests (succès, erreurs AI Engine, cache, modes dégradés)
- [ ] Endpoint dédié : 4 tests (200 OK, 401 sans auth, 404 sans chart, timeout)
- [ ] Endpoint existant avec param : 4 tests (avec/sans include_interpretation)
- [ ] Cache : 2 tests (hit, miss)
- [ ] Lint : ruff check backend/app/services/natal_interpretation_service.py

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

**Fichiers à créer :**
- `backend/app/services/natal_interpretation_service.py`
- `backend/app/services/natal_chart_summary_builder.py` (optionnel, peut être dans le service)
- `backend/app/tests/test_natal_interpretation_service.py`

**Fichiers à modifier :**
- `backend/app/api/v1/routers/users.py` — Ajout endpoint `/natal-chart/interpretation` et param `include_interpretation`
- `backend/app/services/user_natal_chart_service.py` — Optionnel, si intégration directe
