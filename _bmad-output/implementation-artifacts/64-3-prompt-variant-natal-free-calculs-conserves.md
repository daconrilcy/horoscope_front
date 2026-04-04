# Story 64.3 — Prompt variant thème natal free : calculs conservés, texte restreint

Status: todo

## Story

En tant que système backend,
je veux que le thème natal d'un utilisateur free soit toujours calculé intégralement mais que la génération textuelle LLM soit restreinte au variant "free_short" (summary + ni-accordion-title uniquement),
afin que l'utilisateur free ait un thème natal fonctionnel et que les sections supplémentaires puissent être présentées comme teasers lockés côté frontend.

## Context

**Indépendante des stories 64.1 et 64.2** — peut être développée en parallèle.

La feature `natal_chart_long` est déjà enregistrée dans `FEATURE_SCOPE_REGISTRY` avec `FeatureScope.B2C`.  
`NatalChartLongEntitlementGate` existe déjà et retourne un `variant_code` (ex : `"single_astrologer"`, `"multi_astrologer"`).  
`NatalInterpretationServiceV2` utilise `MODULE_TO_USE_CASE_KEY` pour chaque section thématique (PSY_PROFILE, SHADOW_INTEGRATION, etc.) via `LLMGateway`.

**Comportement cible pour le plan free :**
- Tous les calculs astrologiques (`NatalResult`, positions planétaires, maisons, aspects) → **toujours exécutés**
- Génération textuelle LLM → restreinte au variant `"free_short"` :
  - Seul le `summary` global et le `ni-accordion-title` (titre court par section) sont générés
  - Les sections thématiques complètes (PSY_PROFILE, RELATIONSHIP_STYLE, etc.) ne sont pas générées

**Exceptions toujours visibles (aucune restriction) :** `ni-evidence-tags` et disclaimer.

## Acceptance Criteria

**AC1 — Nouveau variant "free_short" reconnu dans le gate natal**
**Given** `NatalChartLongEntitlementGate`  
**When** le plan actif de l'utilisateur est `free`  
**Then** `variant_code="free_short"` est retourné  
**And** le contrat existant (`single_astrologer`, `multi_astrologer`) est inchangé pour basic/premium

**AC2 — Nouveau PromptEntry dans le catalog**
**Given** `backend/app/prompts/catalog.py`  
**When** le fichier est inspecté  
**Then** la clé `"natal_long_free"` existe avec `engine_env_key="OPENAI_ENGINE_NATAL_LONG_FREE"`

**AC3 — Config .env.example mise à jour**
**Given** `backend/.env.example`  
**When** le fichier est inspecté  
**Then** `OPENAI_ENGINE_NATAL_LONG_FREE=gpt-4o-mini` est présent

**AC4 — NatalInterpretationServiceV2 respecte le variant free_short**
**Given** un utilisateur free demandant son thème natal  
**When** `NatalInterpretationServiceV2` est exécuté  
**Then** seuls `summary` et `ni-accordion-title` sont générés par le LLM  
**And** les modules thématiques (PSY_PROFILE, SHADOW_INTEGRATION, etc.) ne sont pas appelés

**AC5 — NatalResult est toujours calculé en free**
**Given** un utilisateur free demandant son thème natal  
**When** le calcul natal est exécuté  
**Then** `NatalResult` (positions, maisons, aspects) est complet — identique au comportement basic/premium  
**And** seule la couche de génération textuelle LLM est restreinte

**AC6 — ni-evidence-tags et disclaimer sont toujours inclus dans la réponse**
**Given** un utilisateur free  
**When** la réponse de l'interprétation natale est construite  
**Then** `ni-evidence-tags` est présent et non vide  
**And** le disclaimer est présent et inchangé

**AC7 — Tests unitaires**
**Given** `backend/app/tests/unit/test_natal_chart_long_entitlement_gate_v2.py` (existant) et un nouveau test  
**When** les tests unitaires sont exécutés  
**Then** le variant `"free_short"` est couvert pour le gate natal  
**And** `NatalInterpretationServiceV2` avec `variant_code="free_short"` est couvert dans un test dédié

**AC8 — Zéro régression**
**When** `pytest backend/` est exécuté  
**Then** 0 régression sur les tests nataux existants

## Tasks / Subtasks

- [ ] T1 — Ajouter le variant "free_short" dans `NatalChartLongEntitlementGate` (AC1)
  - [ ] T1.1 Lire entièrement `backend/app/services/natal_chart_long_entitlement_gate.py`
  - [ ] T1.2 Identifier comment `variant_code` est résolu depuis le snapshot
  - [ ] T1.3 S'assurer que le plan `free` mappe sur `variant_code="free_short"` via le catalog DB
  - [ ] T1.4 Vérifier que les variantes existantes (`single_astrologer`, `multi_astrologer`) restent inchangées

- [ ] T2 — Ajouter `natal_long_free` dans `PROMPT_CATALOG` (AC2)
  - [ ] T2.1 Définir le JSON Schema de sortie free_short :
    ```python
    NATAL_FREE_SHORT_SCHEMA = {
        "type": "object",
        "required": ["summary", "accordion_titles"],
        "properties": {
            "summary": {"type": "string"},
            "accordion_titles": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }
    ```
  - [ ] T2.2 Ajouter `"natal_long_free": PromptEntry(...)` dans `PROMPT_CATALOG`

- [ ] T3 — Mettre à jour `.env.example` (AC3)
  - [ ] T3.1 Ajouter `OPENAI_ENGINE_NATAL_LONG_FREE=gpt-4o-mini`

- [ ] T4 — Modifier `NatalInterpretationServiceV2` pour respecter le variant (AC4, AC5, AC6)
  - [ ] T4.1 Lire entièrement `backend/app/services/natal_interpretation_service_v2.py`
  - [ ] T4.2 Identifier le point d'entrée où les modules thématiques sont itérés
  - [ ] T4.3 Ajouter la logique de sélection :
    ```python
    if variant_code == "free_short":
        # Appel unique au prompt natal_long_free pour summary + accordion_titles
        return await self._generate_free_short(natal_result, ...)
    else:
        # Comportement existant : itération sur MODULE_TO_USE_CASE_KEY
        return await self._generate_full(natal_result, ...)
    ```
  - [ ] T4.4 Créer la méthode `_generate_free_short()` qui appelle `LLMGateway` avec `use_case="natal_long_free"`
  - [ ] T4.5 S'assurer que `ni-evidence-tags` et disclaimer sont toujours construits (depuis `build_enriched_evidence_catalog()` et `get_disclaimers()`)
  - [ ] T4.6 S'assurer que le `NatalResult` (calculs) est toujours entièrement produit avant la décision de variant

- [ ] T5 — Seeder le use_case `natal_long_free` (si applicable)
  - [ ] T5.1 Vérifier `backend/app/llm_orchestration/seeds/use_cases_seed.py`
  - [ ] T5.2 Ajouter `natal_long_free` avec le system prompt approprié

- [ ] T6 — Tests unitaires (AC7)
  - [ ] T6.1 Ajouter dans `test_natal_chart_long_entitlement_gate_v2.py` : test variant "free_short"
  - [ ] T6.2 Créer `backend/app/tests/unit/test_natal_interpretation_service_v2_free.py`
  - [ ] T6.3 Tester : avec `variant_code="free_short"`, `_generate_free_short()` est appelé (et non l'itération complète)
  - [ ] T6.4 Tester : `ni-evidence-tags` et disclaimer présents dans la réponse free

- [ ] T7 — Validation finale (AC8)
  - [ ] T7.1 `pytest backend/app/tests/ -k "natal"` → 0 régression
  - [ ] T7.2 `pytest backend/` → 0 erreur globale
  - [ ] T7.3 `ruff check backend/` → 0 erreur

## Dev Notes

### Distinction clé : calculs vs génération textuelle

```
NatalChartPage request (user free)
  ↓
NatalChartLongEntitlementGate.check_and_get_variant() → variant_code="free_short"
  ↓
NatalCalculationService.compute(birth_data)           ← TOUJOURS exécuté (inchangé)
  → NatalResult (positions, maisons, aspects)
  ↓
NatalInterpretationServiceV2.interpret(natal_result, variant_code="free_short")
  → si "free_short" : LLMGateway("natal_long_free") → {summary, accordion_titles}
  → si "full"       : itération MODULE_TO_USE_CASE_KEY → génération complète
  ↓
build_enriched_evidence_catalog(natal_result)         ← TOUJOURS (ni-evidence-tags)
get_disclaimers(...)                                  ← TOUJOURS (disclaimer)
```

### Format de réponse free_short attendu

La réponse pour le variant free doit structurellement inclure :
- `summary` : texte global du thème natal (paragraphe)
- `accordion_titles` : liste de titres courts pour les sections thématiques (sans le contenu)
- `evidence` : les evidence tags (toujours présents)
- `disclaimer` : toujours présent

Les sections thématiques complètes (PSY_PROFILE, etc.) sont absentes de la réponse — le frontend les détectera comme "nulles" et les affichera avec un LockedSection (Story 64.9).

### Prompt system pour natal_long_free

Le system prompt doit instruire le LLM de produire uniquement un résumé global du thème natal et des titres de sections courts pour chaque module thématique, sans développer le contenu de chaque module. La qualité éditoriale doit être maintenue — c'est un résumé premium, pas une sortie dégradée.
