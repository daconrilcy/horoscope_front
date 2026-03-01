# Chapitre 29 — Interprétation Natale via LLMGateway

## Vue d'ensemble

Le chapitre 29 branche le parcours d'interprétation natale (frontend → backend → LLM) sur l'infrastructure du chapitre 28 (LLMGateway, contrats de use cases, prompts DB, personas, validation, observabilité).

**Produit :** 2 niveaux d'interprétation
- **SIMPLE** (`natal_interpretation_short`) — gratuite, persona optionnelle, fallback none
- **COMPLETE** (`natal_interpretation`) — payante, persona required, fallback → short

---

## Dépendances avec Epic 28

| Composant 28 | Rôle dans le Chapitre 29 |
|---|---|
| `LLMGateway.execute()` | Orchestration centrale des appels LLM |
| `PromptRegistryV2` | Chargement des prompts DB avec cache 60s |
| Use case catalog (`use_cases_seed.py`) | Contrats `natal_interpretation` + `natal_interpretation_short` déjà seédés |
| `AstroResponse_v1` schema (seed_28_4.py) | Format de sortie structuré (title, summary, sections, highlights, advice, evidence) |
| `LlmPersonaModel` + `persona_composer.py` | Bloc persona injecté pour COMPLETE |
| `hard_policy.py` (profil `astrology`) | Garde-fous : non-fatalisme, pas de diagnostic |
| Repair + Fallback (gateway) | Si COMPLETE échoue → automatiquement SHORT |
| `observability_service.py` | Logging + métriques sans données perso |
| `eval_harness.py` | Publish gate sur fixtures YAML |
| `admin_llm.py` | Endpoints admin pour gérer prompts + contrats |

---

## Stories — Ordre d'implémentation

```
N1 → N2 → N3 → N4 → N5
 │     │     │
 │     │     └─ Prompts seédés avant tests endpoint
 │     └─ Service branchable après N1 (chart_json)
 └─ Foundation : chart_json + evidence_catalog
```

| Story | Epic | Fichier | Priorité | Effort |
|-------|------|---------|----------|--------|
| [N1 — chart_json canonique](./story-29-N1-chart-json-canon.md) | NATAL-2 | Backend utility | P0 — bloquant | Moyen |
| [N2 — NatalInterpretationServiceV2](./story-29-N2-natal-interpretation-gateway.md) | NATAL-3 | Backend service + endpoint | P0 — bloquant | Élevé |
| [N3 — Prompts DB + lint + publish](./story-29-N3-prompts-db-publish.md) | NATAL-4 | Backend scripts + admin | P0 — bloquant | Moyen |
| [N4 — UI AstroResponse_v1 + upsell](./story-29-N4-ui-rendu-upsell.md) | NATAL-6 | Frontend | P1 — user-visible | Élevé |
| [N5 — Eval fixtures + publish gate](./story-29-N5-eval-fixtures-gate.md) | NATAL-7 | Backend tests + config | P1 — qualité | Moyen |

---

## Décisions d'Architecture Clés

### 1. `chart_json` : dict en input, string en context

Le gateway valide `user_input` avec JSON Schema (type: object).
Le template `{{chart_json}}` attend une string JSON sérialisée.

**Solution (N2) :**
```python
user_input = {"chart_json": chart_json_dict}        # Validation schéma : dict OK
context = {"chart_json": json.dumps(chart_json_dict)}  # Rendu template : string JSON
# context["chart_json"] overwrite user_input["chart_json"] dans template_vars
```

### 2. `persona_name` : résolution dans le service, pas le gateway

Le prompt COMPLETE utilise `{{persona_name}}` comme variable de rendu.
Le gateway ne résout pas automatiquement le nom depuis `persona_id`.

**Solution (N2) :**
Le service charge `LlmPersonaModel` depuis la DB avant d'appeler le gateway :
```python
persona = db.get(LlmPersonaModel, persona_id)
context["persona_name"] = persona.name
```

### 3. Fallback COMPLETE → SHORT : automatique par le gateway

La configuration `fallback_use_case_key = "natal_interpretation_short"` sur le use case COMPLETE garantit qu'une défaillance de validation ou de réparation déclenche automatiquement un appel SHORT.
Le service N2 n'a pas besoin de gérer ce cas manuellement.

### 4. `NatalInterpretationService` existant : non modifié

Le service v1 (`natal_interpretation_service.py`) reste intact pour compatibilité.
Le service v2 (`natal_interpretation_service_v2.py`) est une nouvelle classe.
Le feature flag `llm_orchestration_v2` contrôle lequel est utilisé.

### 5. Frontend : chargement non bloquant

L'interprétation est chargée après le chart via un hook séparé (`useNatalInterpretation`).
Si l'interprétation échoue, les données brutes du chart restent affichées.

---

## Contrats API (nouveaux)

### `POST /v1/natal/interpretation`

**Request :**
```json
{
  "use_case_level": "short" | "complete",
  "persona_id": "uuid | null",
  "locale": "fr-FR",
  "question": "Interprète mon thème natal"
}
```

**Response 200 :**
```json
{
  "data": {
    "chart_id": "uuid",
    "use_case": "natal_interpretation_short",
    "interpretation": {
      "title": "string",
      "summary": "string",
      "sections": [{"key": "string", "heading": "string", "content": "string"}],
      "highlights": ["string"],
      "advice": ["string"],
      "evidence": ["UPPER_SNAKE_CASE"],
      "disclaimers": ["string"]
    },
    "meta": {
      "prompt_version_id": "uuid | null",
      "persona_id": "uuid | null",
      "model": "string",
      "latency_ms": 1234,
      "validation_status": "valid | repair_success | fallback",
      "repair_attempted": false,
      "fallback_triggered": false
    },
    "degraded_mode": "null | no_time | no_location | no_location_no_time"
  }
}
```

---

## Nouveaux Fichiers par Story

### N1 (Backend — Utilitaires)
- `backend/app/services/chart_json_builder.py` ← CRÉER
- `backend/app/tests/unit/test_chart_json_builder.py` ← CRÉER

### N2 (Backend — Service + Endpoint)
- `backend/app/services/natal_interpretation_service_v2.py` ← CRÉER
- `backend/app/api/v1/routers/natal_interpretation.py` ← CRÉER
- `backend/app/api/v1/schemas/natal_interpretation.py` ← CRÉER
- `backend/app/tests/integration/test_natal_interpretation_endpoint.py` ← CRÉER
- `backend/app/api/v1/router.py` ← MODIFIER (inclure le router)

### N3 (Backend — Prompts + Config)
- `backend/scripts/seed_29_prompts.py` ← CRÉER
- `backend/app/tests/unit/test_prompt_lint_natal.py` ← CRÉER
- `backend/app/tests/integration/test_admin_llm_natal_prompts.py` ← CRÉER
- `backend/app/llm_orchestration/services/prompt_lint.py` ← VÉRIFIER/MODIFIER si besoin

### N4 (Frontend)
- `frontend/src/api/natalChart.ts` ← MODIFIER (types + hook)
- `frontend/src/components/NatalInterpretation.tsx` ← CRÉER
- `frontend/src/i18n/natalChart.ts` ← MODIFIER (clés `interpretation`)
- `frontend/src/pages/NatalChartPage.tsx` ← MODIFIER (intégrer le composant)
- `frontend/src/tests/natalInterpretation.test.ts` ← CRÉER

### N5 (Backend — Tests + Config)
- `backend/app/tests/eval_fixtures/natal_interpretation_short/fixture_01_full_chart.yaml` ← CRÉER
- `backend/app/tests/eval_fixtures/natal_interpretation_short/fixture_02_no_time.yaml` ← CRÉER
- `backend/app/tests/eval_fixtures/natal_interpretation_short/fixture_03_minimal.yaml` ← CRÉER
- `backend/app/tests/eval_fixtures/natal_interpretation/fixture_01_full.yaml` ← CRÉER
- `backend/app/tests/eval_fixtures/natal_interpretation/fixture_02_no_time.yaml` ← CRÉER
- `backend/app/tests/eval_fixtures/natal_interpretation/fixture_03_no_location.yaml` ← CRÉER
- `backend/app/tests/eval_fixtures/natal_interpretation/fixture_04_minimal.yaml` ← CRÉER
- `backend/app/tests/unit/test_eval_harness_natal.py` ← CRÉER
- `backend/scripts/seed_29_prompts.py` ← MODIFIER (ajouter eval_fixtures_path)

---

## Checklist de Validation Finale

**Backend :**
- [ ] `python backend/scripts/seed_29_prompts.py` sans erreur
- [ ] `GET /v1/admin/llm/use-cases/natal_interpretation_short/contract` → contrat OK
- [ ] `GET /v1/admin/llm/use-cases/natal_interpretation/contract` → persona_strategy=required, fallback=short
- [ ] `POST /v1/natal/interpretation` avec `use_case_level=short` → 200 + AstroResponse_v1
- [ ] `POST /v1/natal/interpretation` avec `use_case_level=complete` + persona_id → 200
- [ ] `POST /v1/natal/interpretation` sans chart → 404
- [ ] `LlmCallLogModel` créé en DB après chaque appel
- [ ] Publish gate : bloque si > 20% échecs (test offline)

**Frontend :**
- [ ] Section interprétation visible dans `/natal` après chargement du chart
- [ ] Skeleton pendant le chargement
- [ ] CTA upsell visible après interprétation SHORT
- [ ] PersonaSelector → appel COMPLETE avec persona
- [ ] Erreur d'interprétation → ne casse pas les données brutes du chart

**Observabilité :**
- [ ] Dashboard `/v1/admin/llm/dashboard` montre les métriques natales
- [ ] `validation_status` visible par use_case
