# Story 30.15: Chat — Naturalité conversationnelle : thème natal comme contexte silencieux

Status: done

## Story

As an utilisateur du chat astrologue,
I want que l'astrologue me réponde naturellement sans me redumper mes transits et aspects à chaque message,
so that la conversation est fluide, engageante et centrée sur mes questions, pas sur une récitation du thème natal.

## Contexte du problème

Le LLM ouvre chaque réponse par une liste de transits/aspects (Jupiter sextile Mercure, Jupiter carré Vénus, etc.) même quand l'utilisateur n'a rien demandé sur ces transits spécifiques. Deux causes :

1. **`chat_system.jinja2`** (path v1 AI engine) : injecte `natal_chart_summary` sans instruction sur son mode d'utilisation → le LLM l'interprète comme "informations à transmettre"
2. **`seed_30_14_chat_prompt.py`** (path v2 orchestration) : prompt v2 a des règles de style générales mais **aucune instruction explicite** sur "ne pas exposer le natal tel quel"
3. **Sur un message d'ouverture vague** ("bonjour", "j'ai une question") : le LLM n'a pas de sujet précis → il remplit l'espace avec le natal disponible dans son contexte

## Acceptance Criteria

1. [x] **AC1 — Prompt v2 : natal silencieux** : Le prompt publié pour `chat_astrologer` (v2 orchestration) contient une section explicite indiquant que `natal_chart_summary` est un contexte de fond privé, à ne **jamais** paraphraser ou lister comme introduction, sauf demande explicite de l'utilisateur.
2. [x] **AC2 — Template Jinja2 : natal silencieux** : Le template `chat_system.jinja2` (v1 AI engine) est enrichi d'une instruction après l'injection du natal indiquant qu'il s'agit d'un contexte de fond silencieux, à intégrer de façon transparente dans les réponses.
3. [x] **AC3 — Message d'ouverture naturel** : Quand le premier message de la conversation est une salutation ou une question ouverte sans sujet précis (< 20 mots, pas d'aspect ou transit mentionné), l'astrologue répond par une phrase de bienvenue courte + une question de clarification ciblée — **sans lister des éléments du thème natal**.
4. [x] **AC4 — Utilisation transparente du natal** : Quand l'utilisateur pose une question sur un thème précis (finances, amour, carrière), l'astrologue utilise le natal pour enrichir sa réponse mais l'intègre de façon fluide ("votre Jupiter en maison 2 favorise...") plutôt que de lister tous les aspects dans un bloc markdown.
5. [x] **AC5 — Test de non-régression** : Un test unitaire/intégration vérifie que la réponse pour un message "bonjour" ne contient pas de marqueurs de liste d'aspects (`###`, `**Jupiter`, `**Mars`, `- **`).
6. [x] **AC6 — Seed script idempotent** : Le nouveau seed script pour le prompt v2 est idempotent et publie une nouvelle version archivant l'ancienne.

## Tasks / Subtasks

- [x] **T1 — Améliorer le template Jinja2** (AC2, AC3, AC4)
  - [x] Modifier `backend/app/ai_engine/prompts/chat_system.jinja2`
  - [x] Après le bloc `{% if context.natal_chart_summary %}`, ajouter une instruction explicite :
    "Ce contexte natal est ton référentiel privé. NE le récite pas, NE le liste pas. Utilise-le de façon transparente pour enrichir tes réponses uniquement quand c'est pertinent."
  - [x] Ajouter une instruction pour les messages d'ouverture : si la question est courte/générale, demander une clarification ciblée

- [x] **T2 — Améliorer le prompt v2** (AC1, AC3, AC4)
  - [x] Créer `backend/scripts/seed_30_15_chat_naturalite.py` (nouveau seed script)
  - [x] Publier une nouvelle version du prompt `chat_astrologer` avec :
    - Section "Utilisation du contexte natal" : thème natal = fond silencieux, pas d'introduction récapitulative
    - Interdiction explicite des blocs `###`, listes `- **Aspect**` dans les réponses sauf si l'utilisateur les demande
    - Instruction d'ouverture : sur message vague, poser une question de clarification ciblée
    - Conserver toutes les règles de sécurité et méta-instructions existantes

- [x] **T3 — Tests non-régression** (AC5)
  - [x] Ajouter un test dans `backend/app/tests/unit/` ou `backend/app/tests/integration/`
  - [x] Mock du LLM : vérifier que le *prompt rendu* (system message) contient bien l'instruction "contexte silencieux"
  - [x] Test comportemental (si faisable avec mock) : réponse pour "bonjour" ne contient pas de patterns de liste (`###`, `- **`)

- [x] **T4 — Validation manuelle** (AC3, AC4)
  - [x] Appliquer le seed script en staging : `python backend/scripts/seed_30_15_chat_naturalite.py`
  - [x] Tester manuellement avec un utilisateur ayant un thème natal complet :
    - Message "bonjour" → réponse naturelle sans liste d'aspects
    - Message "j'ai une question sur mes finances" → réponse enrichie du natal sans dump brut
    - Message "quels sont mes transits actuels ?" → liste autorisée (demande explicite)

## Dev Notes

### Analyse de la cause racine

**Path v1** (`ai_engine_settings.llm_orchestration_v2 = False`) :
- Fichier : `backend/app/ai_engine/prompts/chat_system.jinja2`
- Le bloc `{% if context.natal_chart_summary %}` injecte le natal avec label "Contexte du thème natal de l'utilisateur:" sans instruction comportementale → le LLM l'interprète comme "informations à présenter"

**Path v2** (`ai_engine_settings.llm_orchestration_v2 = True`) :
- Fichier seed actuel : `backend/scripts/seed_30_14_chat_prompt.py`
- `CHAT_ASTROLOGER_PROMPT_V2` contient "Utilise les éléments du thème natal seulement si pertinents pour la question posée" mais **cette instruction arrive après** et n'est pas suffisamment explicite sur le fait de ne pas lister/récapituler
- Le `natal_chart_summary` est injecté via `context` dans le gateway, mais la façon dont le gateway le transmet au LLM (probablement comme partie du developer prompt ou user_input) doit être vérifiée

### Fichiers à modifier

| Fichier | Type | Action |
|---------|------|---------|
| `backend/app/ai_engine/prompts/chat_system.jinja2` | Template | Ajouter instruction "natal silencieux" |
| `backend/scripts/seed_30_15_chat_naturalite.py` | Script | CRÉER — nouveau prompt v2 |
| `backend/app/tests/unit/test_chat_naturalite_prompt.py` | Tests | CRÉER — vérifications AC5 |

**Ne pas modifier** :
- `backend/app/services/chat_guidance_service.py` — la logique d'injection du natal est correcte, c'est le prompt que doit guider l'usage
- `backend/app/services/ai_engine_adapter.py` — pas de changement d'architecture nécessaire
- Le schema `ChatResponse_v1` — pas d'impact

### Prompt v2 cible (section à ajouter/remplacer)

```
Règles d'utilisation du thème natal :
- Le natal_chart_summary est ton CONTEXTE DE FOND PRIVÉ — ne le récite jamais, ne le liste jamais en introduction.
- Intègre les éléments astrologiques de façon fluide dans tes réponses ("votre Soleil en Bélier vous pousse à..."), pas en bloc de liste.
- N'utilise JAMAIS les formats "### Titre" ou "- **Aspect** :" dans une réponse conversationnelle sauf si l'utilisateur demande explicitement une liste ou une analyse structurée.
- Sur un message d'ouverture court ("bonjour", "j'ai une question") : accueille chaleureusement et pose UNE seule question de clarification ciblée. Ne présente pas le thème natal.
- Sur une question précise (finances, amour, carrière, etc.) : réponds directement à la question, enrichis avec 1-2 éléments du natal pertinents, maximum.
- Si l'utilisateur demande explicitement "quels sont mes transits / aspects" : tu peux alors les lister.
```

### Template Jinja2 cible (section à modifier)

```jinja2
{% if context.natal_chart_summary %}
[CONTEXTE INTERNE — NE PAS RÉCITER]
Thème natal de l'utilisateur (utilise de façon transparente et silencieuse, uniquement quand pertinent) :
{{ context.natal_chart_summary }}
[FIN CONTEXTE INTERNE]
{% endif %}
```

### Seed script v2 — structure minimale

Le seed doit :
1. Trouver le use case `chat_astrologer` en DB
2. Archiver la version publiée actuelle
3. Publier une nouvelle `LlmPromptVersionModel` avec le prompt enrichi
4. Appeler `PromptRegistryV2.invalidate_cache("chat_astrologer")`
5. Être idempotent (vérifier si le prompt est déjà identique avant d'agir)

Modèle : `backend/scripts/seed_30_14_chat_prompt.py` (à copier/adapter)

### Gateway v2 — comment natal_chart_summary est transmis

Dans `ai_engine_adapter.py:402-413`, le gateway reçoit :
```python
context={
    **context,          # contient natal_chart_summary
    "history": messages[:-1],
}
```
Le gateway passe ce contexte au prompt template via le moteur de rendu Jinja2/prompt registry. Vérifier dans `backend/app/llm_orchestration/gateway.py` comment `context["natal_chart_summary"]` est injecté dans le prompt rendu — c'est là que l'instruction "silencieuse" doit être ancrée.

### Testing standards

- Tests unitaires : mock `AIEngineAdapter.generate_chat_reply`, vérifier le `context` passé
- Tests de prompt rendering : utiliser `PromptRegistryV2` en mode test pour vérifier le prompt rendu
- Pattern de tests existant : `backend/app/tests/integration/test_chat_persona_prompting.py` (story 30-14)

### Project Structure Notes

- L'architecture à deux chemins (v1 jinja2 / v2 gateway) doit être prise en compte : les deux doivent être améliorés
- Prioriser le **path v2** (orchestration) car c'est le chemin de production cible
- Le **path v1** (jinja2) est le fallback legacy — améliorer aussi pour la cohérence

### References

- [Source: backend/app/ai_engine/prompts/chat_system.jinja2] — template v1
- [Source: backend/scripts/seed_30_14_chat_prompt.py] — prompt v2 actuel à améliorer
- [Source: backend/app/services/chat_guidance_service.py:669-693] — injection du natal_summary dans le context
- [Source: backend/app/services/ai_engine_adapter.py:385-413] — transmission au gateway v2
- [Source: backend/app/tests/integration/test_chat_persona_prompting.py] — pattern de tests à suivre
- [Source: docs/chat/plan_implementation_chat_memoire.md#8] — section "Prompts/use cases — `chat_astrologer` doit lire la mémoire" (contexte futur compatible)

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-thinking-exp

### Debug Log References

- Fixed `test_persona_injection.py` which was failing due to missing `app_env` in `MockSettings`.

### Completion Notes List

- Updated `backend/app/ai_engine/prompts/chat_system.jinja2` (v1 path) with silent natal instructions and opening message handling.
- Created `backend/scripts/seed_30_15_chat_naturalite.py` (v2 path) with Prompt V3 including explicit restrictions on natal dump and opening strategy.
- Added `backend/app/tests/unit/test_chat_naturalite_prompt.py` to verify prompt rendering for both paths.
- Executed seed script to update the database with the new prompt version.

### Code Review Fixes (claude-sonnet-4-6)

- **H1 fixed** : Ajout de 3 tests comportementaux dans `test_chat_naturalite_prompt.py` : `test_response_bonjour_no_forbidden_patterns`, `test_response_with_forbidden_patterns_is_detected`, `test_response_explicit_request_allows_listing` — valident AC5 au niveau réponse LLM et non seulement au niveau du prompt.
- **M1 fixed** : `chat_system.jinja2` enrichi avec interdiction explicite des formats `### Titre` et `- **Aspect** :` (alignement v1 sur v2).
- **M2 fixed** : `chat_system.jinja2` enrichi avec la règle "demande explicite → liste autorisée" et l'instruction pour questions précises (finances, amour, carrière).
- **L1 fixed** : `seed_30_15_chat_naturalite.py` — ajout de `sys.exit(1)` dans le bloc `except` pour propager les erreurs en CI/CD.
- **L2 fixed** : `test_persona_injection.py` — ajout de `database_url` dans `MockSettings` des tests `test_persona_injection_disabled` et `test_persona_required_but_missing`.
- **L3 fixed** : `seed_30_15_chat_naturalite.py` — `temperature=0.5` documenté comme choix intentionnel (cohérence, réduction verbosité).

### File List

- `backend/app/ai_engine/prompts/chat_system.jinja2`
- `backend/scripts/seed_30_15_chat_naturalite.py`
- `backend/app/tests/unit/test_chat_naturalite_prompt.py`
- `backend/app/tests/unit/test_persona_injection.py`
