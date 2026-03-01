# Story 29-N5 — Eval Fixtures + Dashboard + Publish Gate

## Contexte & Périmètre

**Epic NATAL-7 / Story N5**
**Chapitre 29** — Interprétation natale via LLMGateway

Le harness d'évaluation (Epic 28.6) permet de tester les prompts LLM sur des fixtures YAML avant publication.
Cette story crée les fixtures spécifiques aux use cases nataux et active le publish gate.

**Dépend de :** Stories N1, N2, N3 (service + prompts fonctionnels)

---

## Architecture cible

```
backend/app/tests/eval_fixtures/
├── natal_interpretation/
│   ├── fixture_01_full_chart.yaml      # Thème complet (heure + lieu connus)
│   ├── fixture_02_no_time.yaml         # Mode dégradé no_time
│   ├── fixture_03_no_location.yaml     # Mode dégradé no_location
│   └── fixture_04_minimal_chart.yaml   # Thème avec peu d'aspects
└── natal_interpretation_short/
    ├── fixture_01_full_chart.yaml
    ├── fixture_02_no_time.yaml
    └── fixture_03_minimal_chart.yaml
```

---

## Hypothèses & Dépendances

- `eval_harness.run_eval()` charge des fichiers YAML depuis `eval_fixtures_path`
- Le format YAML attendu par le harness : `id`, `input`, `expected_schema_valid`, `expected_fields`
- Les fixtures `input.chart_json` doivent être des objets valides (dict), non des strings JSON
- `LlmUseCaseConfigModel.eval_fixtures_path` pointe vers le dossier de fixtures
- `LlmUseCaseConfigModel.eval_failure_threshold` : seuil de taux d'échec bloquant la publication (défaut 0.20)
- En mode offline (sans appel LLM réel), les fixtures utilisent des données représentatives
- L'harness est déclenché lors de `PATCH /v1/admin/llm/use-cases/{key}/prompts/{id}/publish`

---

## Structure des Fixtures YAML

### Format général

```yaml
- id: "identifiant_unique"
  description: "Description du cas de test"
  input:
    chart_json:
      meta:
        birth_date: "1985-04-15"
        birth_time: "14:30"
        birth_place: "Paris, France"
        birth_timezone: "Europe/Paris"
        degraded_mode: null
        engine: "swisseph"
        zodiac: "tropical"
        house_system: "placidus"
        reference_version: "v1.2"
        ruleset_version: "1.0.0"
      planets:
        - code: "sun"
          sign: "taurus"
          longitude: 25.4
          longitude_in_sign: 25.4
          house: 10
          is_retrograde: false
          speed: 0.98
        # ... autres planètes
      houses:
        - number: 1
          cusp_longitude: 284.5
          sign: "capricorn"
        # ... autres maisons
      aspects:
        - type: "trine"
          planet_a: "sun"
          planet_b: "moon"
          angle: 120.3
          orb: 0.3
          applying: false
      angles:
        ASC:
          longitude: 284.5
          sign: "capricorn"
        MC:
          longitude: 194.2
          sign: "libra"
        DSC:
          longitude: 104.5
          sign: "cancer"
        IC:
          longitude: 14.2
          sign: "aries"
    question: "Interprète mon thème natal"  # Pour natal_interpretation seulement
    locale: "fr-FR"
  expected_schema_valid: true
  expected_fields:
    title:
      min_length: 5
    summary:
      min_length: 50
    sections:
      min_items: 2
    highlights:
      min_items: 3
    advice:
      min_items: 3
    evidence:
      min_items: 2
```

---

## Acceptance Criteria

### AC1 — Fixtures `natal_interpretation_short` (3 cas)

**Fixture 01 — Thème complet :**
```yaml
id: "short_01_full_chart"
description: "Thème complet avec heure et lieu de naissance"
input:
  chart_json:
    meta: {birth_date: "1985-04-15", birth_time: "14:30", birth_place: "Paris, France", ...}
    planets: [10 planètes avec positions complètes]
    houses: [12 maisons]
    aspects: [5–8 aspects majeurs]
    angles: {ASC, MC, DSC, IC présents}
  locale: "fr-FR"
expected_schema_valid: true
expected_fields:
  title: {min_length: 5}
  summary: {min_length: 50}
  sections: {min_items: 2}
  highlights: {min_items: 3}
  advice: {min_items: 3}
  evidence: {min_items: 2}
```

**Fixture 02 — Mode dégradé no_time :**
```yaml
id: "short_02_no_time"
description: "Thème sans heure de naissance (pas de maisons ni d'ascendant)"
input:
  chart_json:
    meta: {birth_date: "1990-07-22", birth_time: null, degraded_mode: "no_time", ...}
    planets: [10 planètes, house: null pour toutes]
    houses: []
    aspects: [5 aspects]
    angles: {ASC: null, MC: null, DSC: null, IC: null}
  locale: "fr-FR"
expected_schema_valid: true
expected_fields:
  title: {min_length: 5}
  sections: {min_items: 2}
  highlights: {min_items: 3}
```

**Fixture 03 — Thème minimal (peu d'aspects) :**
```yaml
id: "short_03_minimal"
description: "Thème avec très peu d'aspects (edge case)"
input:
  chart_json:
    meta: {birth_date: "2000-01-01", birth_time: "12:00", ...}
    planets: [3 planètes seulement : soleil, lune, ascendant]
    houses: [12 maisons]
    aspects: [1 seul aspect]
    angles: {ASC et MC présents}
  locale: "fr-FR"
expected_schema_valid: true
expected_fields:
  sections: {min_items: 2}
  evidence: {min_items: 1}
```

### AC2 — Fixtures `natal_interpretation` (4 cas)

**Fixture 01 — Thème complet avec question :**
```yaml
id: "complete_01_full"
description: "Interprétation complète avec persona"
input:
  chart_json: [même structure que short_01 mais complet]
  question: "Interprète mon thème natal de façon approfondie"
  locale: "fr-FR"
expected_schema_valid: true
expected_fields:
  title: {min_length: 5}
  summary: {min_length: 100}
  sections: {min_items: 4}  # Plus de sections pour l'interprétation complète
  highlights: {min_items: 4}
  advice: {min_items: 4}
  evidence: {min_items: 3}
```

**Fixture 02 — Mode dégradé no_time :**
```yaml
id: "complete_02_no_time"
description: "Thème sans heure de naissance pour l'interprétation complète"
input:
  chart_json:
    meta: {birth_time: null, degraded_mode: "no_time", ...}
    ...
  question: "Interprète mon thème"
  locale: "fr-FR"
expected_schema_valid: true
expected_fields:
  sections: {min_items: 2}
```

**Fixture 03 — Mode dégradé no_location :**
```yaml
id: "complete_03_no_location"
description: "Thème sans lieu de naissance"
input:
  chart_json:
    meta: {birth_place: null, degraded_mode: "no_location", ...}
    angles: {ASC: null, MC: null, ...}
    ...
  question: "Interprète mon thème"
  locale: "fr-FR"
expected_schema_valid: true
expected_fields:
  sections: {min_items: 2}
```

**Fixture 04 — Thème minimal :**
```yaml
id: "complete_04_minimal"
description: "Thème minimal (edge case pour l'interprétation complète)"
input:
  chart_json:
    planets: [3 planètes]
    aspects: [1 aspect]
    ...
  question: "Interprète mon thème"
  locale: "fr-FR"
expected_schema_valid: true
expected_fields:
  sections: {min_items: 2}
  evidence: {min_items: 1}
```

### AC3 — `eval_fixtures_path` configuré dans la DB

Après la story N3 (prompts seedés), mettre à jour `LlmUseCaseConfigModel` :

```sql
UPDATE llm_use_case_configs SET
  eval_fixtures_path = 'backend/app/tests/eval_fixtures/natal_interpretation_short',
  eval_failure_threshold = 0.20
WHERE key = 'natal_interpretation_short';

UPDATE llm_use_case_configs SET
  eval_fixtures_path = 'backend/app/tests/eval_fixtures/natal_interpretation',
  eval_failure_threshold = 0.20
WHERE key = 'natal_interpretation';
```

Cela peut être fait via l'endpoint admin ou via le script `seed_29_prompts.py` (T2).

### AC4 — Publish gate actif

Quand `PATCH /v1/admin/llm/use-cases/natal_interpretation_short/prompts/{id}/publish` est appelé :
1. Le harness est déclenché sur les fixtures du use case
2. Si `failure_rate > eval_failure_threshold` → HTTP 409 avec `EvalReport` dans la réponse
3. Si `failure_rate <= eval_failure_threshold` → publication OK

> **Note :** Le harness fait des vrais appels LLM en mode intégration. Pour les tests offline, mocker `LLMGateway.execute`.

### AC5 — Tests offline du harness

**Fichier :** `backend/app/tests/unit/test_eval_harness_natal.py`

```python
@pytest.mark.asyncio
async def test_eval_harness_short_all_pass(mock_gateway):
    """Avec un mock qui retourne un AstroResponse_v1 valide, tous les fixtures passent."""
    mock_result = GatewayResult(
        structured_output={
            "title": "Test titre",
            "summary": "Résumé de test suffisamment long pour passer la validation",
            "sections": [
                {"key": "overall", "heading": "Vue d'ensemble", "content": "Contenu test..."},
                {"key": "career", "heading": "Carrière", "content": "Contenu test..."},
            ],
            "highlights": ["Point 1", "Point 2", "Point 3"],
            "advice": ["Conseil 1", "Conseil 2", "Conseil 3"],
            "evidence": ["SUN_TAURUS", "MOON_CANCER"],
        },
        meta=GatewayMeta(validation_status="valid", ...),
        ...
    )
    # mock gateway.execute → mock_result
    report = await run_eval("natal_interpretation_short", "test-version", fixtures_path, db)
    assert report.failure_rate == 0.0
    assert report.blocked_publication == False

@pytest.mark.asyncio
async def test_eval_harness_blocks_on_failures(mock_gateway_fail):
    """Si > 20% des fixtures échouent, blocked_publication = True."""
    # mock gateway.execute → résultat invalide ou exception
    report = await run_eval("natal_interpretation_short", "test-version", fixtures_path, db)
    assert report.failure_rate > 0.20
```

### AC6 — Dashboard monitoring natal

Via `GET /v1/admin/llm/dashboard` (déjà existant en Epic 28.6), les métriques suivantes sont visibles pour les use cases nataux :
- `request_count` par `use_case` (`natal_interpretation` et `natal_interpretation_short`)
- Taux de `fallback_triggered`
- Taux de `repair_attempted`
- `validation_status` distribution
- Latence moyenne

Pas de modification de l'endpoint nécessaire — juste confirmer que les données remontent correctement après les premiers appels.

### AC7 — Logging sans données personnelles

Chaque appel à `POST /v1/natal/interpretation` produit un `LlmCallLogModel` avec :
- `input_hash` : SHA-256 du `user_input` sanitisé (pas de données brutes)
- `use_case` : `natal_interpretation` ou `natal_interpretation_short`
- `validation_status`, `repair_attempted`, `fallback_triggered`
- `evidence_warnings_count` : compte les items `evidence` non conformes au pattern

---

## Tâches Techniques

### T1 — Créer les fichiers de fixtures YAML

**Dossiers :**
- `backend/app/tests/eval_fixtures/natal_interpretation_short/`
- `backend/app/tests/eval_fixtures/natal_interpretation/`

Créer les fichiers YAML avec des données de thème natal réalistes mais fictives.

**Données du thème de test canonique (à réutiliser dans toutes les fixtures full) :**
```yaml
# Thème canonique de test
birth_date: "1985-04-15"
birth_time: "14:30"
birth_place: "Paris, France"
birth_timezone: "Europe/Paris"
planets:
  - {code: sun, sign: taurus, longitude: 25.4, longitude_in_sign: 25.4, house: 10, is_retrograde: false, speed: 0.98}
  - {code: moon, sign: cancer, longitude: 94.7, longitude_in_sign: 4.7, house: 2, is_retrograde: false, speed: 13.1}
  - {code: mercury, sign: aries, longitude: 15.2, longitude_in_sign: 15.2, house: 9, is_retrograde: false, speed: 1.5}
  - {code: venus, sign: gemini, longitude: 70.3, longitude_in_sign: 10.3, house: 11, is_retrograde: false, speed: 1.2}
  - {code: mars, sign: capricorn, longitude: 284.8, longitude_in_sign: 14.8, house: 6, is_retrograde: false, speed: 0.7}
  - {code: jupiter, sign: aquarius, longitude: 318.5, longitude_in_sign: 18.5, house: 7, is_retrograde: false, speed: 0.1}
  - {code: saturn, sign: scorpio, longitude: 224.3, longitude_in_sign: 14.3, house: 4, is_retrograde: true, speed: -0.04}
  - {code: uranus, sign: sagittarius, longitude: 258.1, longitude_in_sign: 18.1, house: 5, is_retrograde: false, speed: 0.06}
  - {code: neptune, sign: capricorn, longitude: 272.4, longitude_in_sign: 2.4, house: 6, is_retrograde: false, speed: 0.02}
  - {code: pluto, sign: scorpio, longitude: 213.7, longitude_in_sign: 3.7, house: 4, is_retrograde: false, speed: 0.02}
houses:
  - {number: 1, cusp_longitude: 284.5, sign: capricorn}
  - {number: 2, cusp_longitude: 314.2, sign: aquarius}
  - {number: 3, cusp_longitude: 344.8, sign: pisces}
  - {number: 4, cusp_longitude: 14.2, sign: aries}
  - {number: 5, cusp_longitude: 44.6, sign: taurus}
  - {number: 6, cusp_longitude: 74.1, sign: gemini}
  - {number: 7, cusp_longitude: 104.5, sign: cancer}
  - {number: 8, cusp_longitude: 134.2, sign: leo}
  - {number: 9, cusp_longitude: 164.8, sign: virgo}
  - {number: 10, cusp_longitude: 194.2, sign: libra}
  - {number: 11, cusp_longitude: 224.6, sign: scorpio}
  - {number: 12, cusp_longitude: 254.1, sign: sagittarius}
aspects:
  - {type: trine, planet_a: sun, planet_b: moon, angle: 120.3, orb: 0.3, applying: false}
  - {type: square, planet_a: sun, planet_b: saturn, angle: 91.1, orb: 1.1, applying: true}
  - {type: conjunction, planet_a: neptune, planet_b: mars, angle: 1.4, orb: 1.4, applying: false}
  - {type: sextile, planet_a: moon, planet_b: venus, angle: 59.6, orb: 0.4, applying: true}
  - {type: opposition, planet_a: jupiter, planet_b: sun, angle: 176.9, orb: 3.1, applying: false}
angles:
  ASC: {longitude: 284.5, sign: capricorn}
  MC: {longitude: 194.2, sign: libra}
  DSC: {longitude: 104.5, sign: cancer}
  IC: {longitude: 14.2, sign: aries}
```

### T2 — Mettre à jour les use cases avec `eval_fixtures_path`

Dans le script `seed_29_prompts.py` (N3) ou dans un script dédié, ajouter la mise à jour :

```python
from sqlalchemy import update
from app.infra.db.models import LlmUseCaseConfigModel

# Ajouter dans seed()
updates = [
    {
        "key": "natal_interpretation_short",
        "eval_fixtures_path": "backend/app/tests/eval_fixtures/natal_interpretation_short",
        "eval_failure_threshold": 0.20,
    },
    {
        "key": "natal_interpretation",
        "eval_fixtures_path": "backend/app/tests/eval_fixtures/natal_interpretation",
        "eval_failure_threshold": 0.20,
    },
]
for upd in updates:
    uc = db.get(LlmUseCaseConfigModel, upd["key"])
    if uc:
        uc.eval_fixtures_path = upd["eval_fixtures_path"]
        uc.eval_failure_threshold = upd["eval_failure_threshold"]
db.commit()
```

### T3 — Tests du harness

**Fichier :** `backend/app/tests/unit/test_eval_harness_natal.py`

Utiliser `AsyncMock` pour mocker `LLMGateway.execute` et tester les cas :
- Tous les fixtures passent → `failure_rate = 0.0`
- Fichier de fixtures inexistant → rapport vide, pas d'erreur
- Un fixture sur trois échoue → `failure_rate ≈ 0.33`

### T4 — Vérifier la logique de publish gate dans `admin_llm.py`

Vérifier que `PATCH /v1/admin/llm/use-cases/{key}/prompts/{id}/publish` :
1. Récupère `eval_fixtures_path` et `eval_failure_threshold` depuis la DB
2. Si `eval_fixtures_path` est non null, appelle `run_eval()`
3. Si `failure_rate > threshold`, répond HTTP 409 avec l'EvalReport
4. Sinon, publie et répond HTTP 200

Si ce n'est pas encore le cas (possible lacune de l'Epic 28), compléter le handler.

---

## Fichiers à Créer / Modifier

| Action | Fichier |
|--------|---------|
| CRÉER | `backend/app/tests/eval_fixtures/natal_interpretation_short/fixture_01_full_chart.yaml` |
| CRÉER | `backend/app/tests/eval_fixtures/natal_interpretation_short/fixture_02_no_time.yaml` |
| CRÉER | `backend/app/tests/eval_fixtures/natal_interpretation_short/fixture_03_minimal.yaml` |
| CRÉER | `backend/app/tests/eval_fixtures/natal_interpretation/fixture_01_full.yaml` |
| CRÉER | `backend/app/tests/eval_fixtures/natal_interpretation/fixture_02_no_time.yaml` |
| CRÉER | `backend/app/tests/eval_fixtures/natal_interpretation/fixture_03_no_location.yaml` |
| CRÉER | `backend/app/tests/eval_fixtures/natal_interpretation/fixture_04_minimal.yaml` |
| CRÉER | `backend/app/tests/unit/test_eval_harness_natal.py` |
| MODIFIER | `backend/scripts/seed_29_prompts.py` — ajouter `eval_fixtures_path` |
| VÉRIFIER | `backend/app/api/v1/routers/admin_llm.py` — publish gate complet |

---

## Critères de "Done"

- [ ] 7 fichiers YAML de fixtures créés et valides (lisibles par PyYAML)
- [ ] `eval_fixtures_path` configuré dans la DB pour les deux use cases
- [ ] Harness offline : `run_eval()` sur les fixtures avec mock gateway → rapport sans erreur
- [ ] Tests `test_eval_harness_natal.py` passent
- [ ] Publish gate testé : publication bloquée si > 20% d'échecs (test avec mock)
- [ ] Dashboard `/v1/admin/llm/dashboard` montre les métriques natales après 1er appel réel
