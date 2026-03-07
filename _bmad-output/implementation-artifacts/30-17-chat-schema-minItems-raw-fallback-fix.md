# Story 30.17: Chat — Fix ChatResponse_v1 suggested_replies.minItems causing raw_fallback

Status: done

## Story

As a utilisateur du chat,
I want que le chat réponde toujours en style conversationnel naturel (sans titres markdown ni liste d'aspects),
so that les messages d'ouverture courts ("bonjour", "j'ai une question") ne déclenchent plus un rendu "rapport natal" mal formaté.

## Contexte du problème

Le schéma JSON `ChatResponse_v1` définissait `suggested_replies.minItems: 1`, ce qui imposait au LLM de toujours fournir au moins une suggestion de réponse.

Comportement observé :
1. L'utilisateur envoie un message d'ouverture court ("bonjour").
2. Le LLM, respectant les règles conversationnelles du prompt 30-15, retourne `suggested_replies: []` (aucune suggestion pertinente sur une simple salutation).
3. Le gateway structured-output déclenche une `ValidationError` (minItems constraint violated).
4. Le gateway tombe en `raw_fallback` : retourne `raw_output` (texte brut non parsé).
5. `ai_engine_adapter.py` détecte l'absence de `structured_output["message"]` → utilise `raw_output`.
6. Le `raw_output` contient le style "rapport natal" (titres `### Titre`, listes `- **Aspect** :`) car les règles du prompt ne s'appliquent plus.

## Root Cause

```
ChatResponse_v1.suggested_replies.minItems = 1
    ↓
LLM retourne [] (valide sémantiquement pour "bonjour")
    ↓
ValidationError → raw_fallback
    ↓
Style conversationnel perdu
```

## Fix

Supprimer `minItems` sur `suggested_replies` dans `CHAT_RESPONSE_V1` → `[]` devient valide → structured_output quasi-systématique → style naturel garanti par le prompt.

## Acceptance Criteria

1. [x] **AC1 — Schema fix** : `ChatResponse_v1.suggested_replies` n'a plus de contrainte `minItems`. `[]` est un tableau valide.
2. [x] **AC2 — Prompt aligné** : Le prompt `chat_astrologer` précise explicitement "tableau vide [] autorisé si aucune suggestion pertinente" (0 à 3 suggestions).
3. [x] **AC3 — Seed idempotent** : Un script de migration `seed_30_17_fix_schema_minItems.py` met à jour le schéma en base si `minItems` est encore présent.

## Tasks / Subtasks

- [x] **T1 — Fix use_cases_seed.py** (AC1)
  - [x] Supprimer `"minItems": 1` dans `CHAT_RESPONSE_V1["properties"]["suggested_replies"]`

- [x] **T2 — Mise à jour prompt** (AC2)
  - [x] Modifier `CHAT_ASTROLOGER_PROMPT_V3` dans `seed_30_15_chat_naturalite.py` : "0 à 3 suggestions courtes et actionnables (tableau vide [] autorisé si aucune suggestion pertinente)"

- [x] **T3 — Seed DB** (AC3)
  - [x] Créer `backend/scripts/seed_30_17_fix_schema_minItems.py`
  - [x] Vérifie si `minItems` est présent avant de patcher (idempotent)
  - [x] Met à jour `schema.json_schema = CHAT_RESPONSE_V1` et commit

## Dev Notes

### Schéma avant/après

```python
# Avant
"suggested_replies": {
    "type": "array",
    "minItems": 1,        # ← root cause
    "maxItems": 5,
    "items": {"type": "string", "minLength": 1, "maxLength": 80},
},

# Après
"suggested_replies": {
    "type": "array",
    "maxItems": 5,
    "items": {"type": "string", "minLength": 1, "maxLength": 80},
},
```

### Commande de migration

```bash
cd backend && python scripts/seed_30_17_fix_schema_minItems.py
```

### Fichiers modifiés

| Fichier | Type | Action |
|---------|------|--------|
| `backend/app/llm_orchestration/seeds/use_cases_seed.py` | Seed | Suppression `minItems: 1` |
| `backend/scripts/seed_30_15_chat_naturalite.py` | Seed | Alignement prompt ([] autorisé) |
| `backend/scripts/seed_30_17_fix_schema_minItems.py` | Seed | CRÉÉ — migration DB idempotente |
| `backend/app/services/ai_engine_adapter.py` | Service | Amélioration observabilité (logs validation error/raw fallback) |

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Completion Notes List

- Suppression `minItems: 1` dans `CHAT_RESPONSE_V1` (`use_cases_seed.py`).
- Prompt `CHAT_ASTROLOGER_PROMPT_V3` mis à jour pour indiquer "tableau vide [] autorisé".
- Script `seed_30_17_fix_schema_minItems.py` créé : vérifie la présence de `minItems`, patche si nécessaire, idempotent.
- Observabilité améliorée dans `ai_engine_adapter.py` : logs détaillés sur les échecs de validation pour faciliter le diagnostic futur.
- Tests unitaires `test_use_cases_seed_chat_schema.py` mis à jour pour vérifier l'absence de `minItems`.

### File List

- `backend/app/llm_orchestration/seeds/use_cases_seed.py`
- `backend/scripts/seed_30_15_chat_naturalite.py`
- `backend/scripts/seed_30_17_fix_schema_minItems.py`
- `backend/app/services/ai_engine_adapter.py`
- `backend/app/tests/unit/test_use_cases_seed_chat_schema.py`
