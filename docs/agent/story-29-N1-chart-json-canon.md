# Story 29-N1 — Export `chart_json` canonique + `evidence_catalog`

## Contexte & Périmètre

**Epic NATAL-2 / Story N1**
**Chapitre 29** — Interprétation natale via LLMGateway (branchement sur Epic 28)

Le gateway (Epic 28) utilise des templates de prompt avec le placeholder `{{chart_json}}`.
Ce placeholder doit recevoir un **JSON sérialisé et stable** représentant le thème natal complet.
Actuellement, `NatalInterpretationService` produit un résumé textuel (`natal_chart_summary`) qui n'est pas compatible avec le contrat du gateway.

Cette story crée :
1. `build_chart_json(natal_result, birth_profile, degraded_mode)` → `dict` canonique
2. `build_evidence_catalog(chart_json)` → `list[str]` en UPPER_SNAKE_CASE

---

## Hypothèses & Dépendances

- `NatalResult` (depuis `app.domain.astrology.natal_calculation`) est disponible et stable
- `UserBirthProfileData` (depuis `app.services.user_birth_profile_service`) est disponible
- Le format `evidence` doit satisfaire le pattern regex `^[A-Z0-9_\.:-]{3,60}$` (AstroResponse_v1 schema)
- Le `chart_json` doit correspondre au champ `chart_json: {"type": "object"}` de l'`input_schema` de `natal_interpretation`
- La story ne modifie **aucun endpoint existant** — elle crée des utilitaires purs testables

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Produire un `chart_json` stable et lisible par le LLM
- Pré-calculer les `evidence_ids` pour ancrer l'interprétation LLM sur des faits
- Avoir du code 100 % testé unitairement (sans DB, sans LLM)

**Non-Objectifs :**
- Pas d'appel LLM dans cette story
- Pas de nouvel endpoint API
- Pas de modification du frontend

---

## Acceptance Criteria

### AC1 — Structure `chart_json`
La fonction `build_chart_json(natal_result, birth_profile, degraded_mode)` retourne un dict avec exactement ces clés :

```json
{
  "meta": {
    "birth_date": "1985-04-15",
    "birth_time": "14:30",
    "birth_place": "Paris, France",
    "birth_timezone": "Europe/Paris",
    "degraded_mode": null,
    "engine": "swisseph",
    "zodiac": "tropical",
    "house_system": "placidus",
    "reference_version": "v1.2",
    "ruleset_version": "1.0.0"
  },
  "planets": [
    {
      "code": "sun",
      "sign": "taurus",
      "longitude": 25.4,
      "longitude_in_sign": 25.4,
      "house": 10,
      "is_retrograde": false,
      "speed": 0.98
    }
  ],
  "houses": [
    {
      "number": 1,
      "cusp_longitude": 284.5,
      "sign": "capricorn"
    }
  ],
  "aspects": [
    {
      "type": "trine",
      "planet_a": "sun",
      "planet_b": "moon",
      "angle": 120.3,
      "orb": 0.3,
      "applying": false
    }
  ],
  "angles": {
    "ASC": { "longitude": 284.5, "sign": "capricorn" },
    "MC": { "longitude": 194.2, "sign": "libra" },
    "DSC": { "longitude": 104.5, "sign": "cancer" },
    "IC": { "longitude": 14.2, "sign": "aries" }
  }
}
```

### AC2 — Mode dégradé représenté
- Si `degraded_mode == "no_time"` : `meta.birth_time = null`, `meta.degraded_mode = "no_time"`, angles absents (ASC/MC = null)
- Si `degraded_mode == "no_location"` : `meta.birth_place = null`, angles ASC/MC = null
- Si `degraded_mode == "no_location_no_time"` : les deux

### AC3 — `longitude_in_sign` calculé correctement
`longitude_in_sign = longitude % 30` (position dans le signe, 0–30°)

### AC4 — `sign` calculé pour chaque corps
`sign = SIGNS[int(longitude / 30) % 12]` (même logique que l'existant dans `natal_interpretation_service.py`)

### AC5 — Aspects : uniquement les aspects majeurs
Seuls `conjunction`, `opposition`, `trine`, `square`, `sextile` sont inclus dans `chart_json.aspects`

### AC6 — Evidence catalog UPPER_SNAKE_CASE
`build_evidence_catalog(chart_json)` retourne une liste d'identifiants conformes au pattern `^[A-Z0-9_\.:-]{3,60}$`.

Exemples attendus pour Soleil Taureau Maison 10 :
- `SUN_TAURUS` → position planétaire
- `SUN_H10` → maison occupée
- `SUN_TAURUS_H10` → combiné

Pour un aspect Soleil trigone Lune orbe 0.3° :
- `ASPECT_SUN_MOON_TRINE` → type d'aspect
- `ASPECT_SUN_MOON_TRINE_ORB0` → orbe arrondi en degrés entiers

Pour les angles (si présents) :
- `ASC_CAPRICORN`
- `MC_LIBRA`

### AC7 — Tests unitaires ≥ 90 % de couverture
- `test_build_chart_json_full` : thème complet, vérification de chaque champ
- `test_build_chart_json_no_time` : mode dégradé no_time, angles null
- `test_build_chart_json_no_location` : mode dégradé no_location
- `test_build_evidence_catalog_basic` : vérifie les identifiants générés
- `test_evidence_catalog_pattern` : chaque item match `^[A-Z0-9_\.:-]{3,60}$`

---

## Tâches Techniques

### T1 — Créer le module `chart_json_builder.py`

**Fichier :** `backend/app/services/chart_json_builder.py`

```python
"""
Construit le payload chart_json canonique pour le LLMGateway.

Ce module produit un dictionnaire stable à partir d'un NatalResult,
compatible avec le placeholder {{chart_json}} des prompts du gateway.
"""
```

**Fonctions à implémenter :**

```python
SIGNS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
         "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
MAJOR_ASPECTS = {"conjunction", "opposition", "trine", "square", "sextile"}

def _longitude_to_sign(longitude: float) -> str: ...
def _longitude_in_sign(longitude: float) -> float: ...

def build_chart_json(
    natal_result: "NatalResult",
    birth_profile: "UserBirthProfileData",
    degraded_mode: str | None = None,
) -> dict: ...

def build_evidence_catalog(chart_json: dict) -> list[str]: ...
```

**Règles pour `build_chart_json` :**
- Importer `NatalResult` avec `TYPE_CHECKING` pour éviter les imports circulaires
- `meta.birth_timezone` vient de `natal_result.prepared_input.birth_timezone` si disponible, sinon `birth_profile.birth_timezone`
- `meta.engine` = `natal_result.engine`
- `meta.zodiac` = `natal_result.zodiac` (str ou `ZodiacType.value`)
- `meta.house_system` = `natal_result.house_system` (str ou `HouseSystemType.value`)
- Angles : House 1 = ASC, House 10 = MC, House 7 = DSC, House 4 = IC. Si `degraded_mode in {"no_time", "no_location", "no_location_no_time"}` : angles = null dict (toutes clés à None)

**Règles pour `build_evidence_catalog` :**
- Itérer sur `chart_json["planets"]` → pour chaque planète :
  - `{PLANET_CODE}_{SIGN_CODE}` : ex. `SUN_TAURUS`
  - `{PLANET_CODE}_H{house}` : ex. `SUN_H10`
  - `{PLANET_CODE}_{SIGN_CODE}_H{house}` : ex. `SUN_TAURUS_H10`
  - Si `is_retrograde == True` : ajouter `{PLANET_CODE}_RETROGRADE`
- Itérer sur `chart_json["aspects"]` → pour chaque aspect :
  - `ASPECT_{PA}_{PB}_{TYPE}` : ex. `ASPECT_SUN_MOON_TRINE`
  - `ASPECT_{PA}_{PB}_{TYPE}_ORB{orb_int}` : ex. `ASPECT_SUN_MOON_TRINE_ORB0`
- Itérer sur `chart_json["angles"]` (si non null) :
  - `{ANGLE}_{SIGN}` : ex. `ASC_CAPRICORN`, `MC_LIBRA`
- Déduplier, trier, et nettoyer : upcase, remplacer les caractères non autorisés
- Limiter à 40 items max (troncature des moins importants en priorité)

### T2 — Tests unitaires

**Fichier :** `backend/app/tests/unit/test_chart_json_builder.py`

Créer des fixtures `NatalResult` et `UserBirthProfileData` minimales (sans DB) :
- Utiliser `dataclasses` ou `SimpleNamespace` pour les fixtures de test
- 5 tests minimum (AC7)

### T3 — Export depuis le module services

Ajouter l'export dans `backend/app/services/__init__.py` si ce fichier existe, sinon documenter l'import direct.

---

## Fichiers à Créer / Modifier

| Action | Fichier |
|--------|---------|
| CRÉER | `backend/app/services/chart_json_builder.py` |
| CRÉER | `backend/app/tests/unit/test_chart_json_builder.py` |
| (optionnel) MODIFIER | `backend/app/services/__init__.py` — ajouter export |

---

## Critères de "Done"

- [ ] `build_chart_json()` implémentée et documentée
- [ ] `build_evidence_catalog()` implémentée et documentée
- [ ] Tests unitaires passent (`pytest backend/app/tests/unit/test_chart_json_builder.py`)
- [ ] Couverture de code ≥ 90 % sur le module
- [ ] Aucun import circulaire (vérifier avec `python -c "from app.services.chart_json_builder import build_chart_json"`)
- [ ] Le dict retourné par `build_chart_json` est sérialisable avec `json.dumps()` (pas de types non-JSON)
