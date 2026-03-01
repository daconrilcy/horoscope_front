# Story 29-N3 — Prompts DB + Lint Placeholders + Publish

## Contexte & Périmètre

**Epic NATAL-4 / Story N3**
**Chapitre 29** — Interprétation natale via LLMGateway

Le gateway (Epic 28) résout les prompts depuis la DB via `PromptRegistryV2`.
Les deux use cases `natal_interpretation` et `natal_interpretation_short` doivent avoir des prompts publiés en DB pour que le gateway puisse fonctionner.

Cette story crée :
1. Les prompts dans la DB pour les deux use cases (via script de seed)
2. Vérifie que le lint valide correctement les placeholders requis
3. Publie les prompts via l'endpoint admin

**Dépend de :** Epic 28.5 (use cases seédés), Epic 28.2 (PromptRegistryV2 + lint)

---

## Hypothèses & Dépendances

- `LlmUseCaseConfigModel` pour `natal_interpretation` a `required_prompt_placeholders = ["chart_json", "persona_name"]`
- `LlmUseCaseConfigModel` pour `natal_interpretation_short` a `required_prompt_placeholders = ["chart_json"]`
- Le lint valide que ces placeholders sont présents dans le `developer_prompt`
- Les placeholders `{{locale}}` et `{{use_case}}` sont toujours obligatoires (lint global)
- `PromptStatus.PUBLISHED` : un seul prompt publié par use_case_key à la fois
- L'endpoint admin `POST /v1/admin/llm/use-cases/{key}/prompts` crée un draft
- L'endpoint admin `PATCH /v1/admin/llm/use-cases/{key}/prompts/{id}/publish` publie

---

## Prompts à Créer

### Prompt SIMPLE (`natal_interpretation_short`)

**Caractéristiques :**
- Use case : `natal_interpretation_short`
- Output schema : `AstroResponse_v1`
- Persona strategy : `optional`
- Placeholders requis : `{{chart_json}}`
- Placeholders plateforme : `{{locale}}`, `{{use_case}}`
- Modèle : `gpt-4o-mini`
- Temperature : `0.7`
- Max tokens : `2048`

**Contenu du developer_prompt :**
```
Langue cible : {{locale}}. Contexte : use_case={{use_case}}.

Tu es un astrologue expérimenté. Tu interprètes le thème natal fourni de façon claire, moderne et non fataliste.

Tu travailles UNIQUEMENT à partir des données du thème natal suivantes :
{{chart_json}}

Règles absolues :
- N'invente aucun placement planétaire, aspect ou maison non présent dans les données
- Parle de tendances et de potentiels, jamais de certitudes
- Pas de diagnostic médical, légal ou financier ferme
- Si tu es incertain sur un point, reste général

Format de sortie (JSON strict AstroResponse_v1) :
- title : titre accrocheur, 5–10 mots
- summary : introduction du profil natal, 4–6 phrases
- sections : minimum 3 parmi [overall, career, relationships, inner_life, daily_life]
  - heading : titre de section percutant
  - content : 3–5 phrases par section, concret et actionnable
- highlights : 3–5 points forts ou traits marquants du thème
- advice : 3–5 conseils pratiques et positifs
- evidence : identifiants UPPER_SNAKE_CASE des placements réellement utilisés
  ex: SUN_TAURUS_H10, MOON_CANCER, ASPECT_SUN_MOON_TRINE, ASC_SCORPIO
- disclaimers : 1 note de prudence générale (astrologie = piste de réflexion)
```

### Prompt COMPLET (`natal_interpretation`)

**Caractéristiques :**
- Use case : `natal_interpretation`
- Output schema : `AstroResponse_v1`
- Persona strategy : `required`
- Placeholders requis : `{{chart_json}}`, `{{persona_name}}`
- Placeholders plateforme : `{{locale}}`, `{{use_case}}`
- Modèle : `gpt-4o-mini`
- Temperature : `0.7`
- Max tokens : `3000`

**Contenu du developer_prompt :**
```
Langue cible : {{locale}}. Contexte : use_case={{use_case}}.

Tu incarnes {{persona_name}}, astrologue expert. Adapte ton style et ton ton à cette persona tout en restant professionnel et bienveillant.

Tu réalises une interprétation approfondie et personnalisée du thème natal suivant :
{{chart_json}}

Règles absolues :
- Tu te bases UNIQUEMENT sur les données du thème natal fournies
- N'invente aucun placement, aspect ou maison non présent dans les données
- Parle de tendances, potentiels et dynamiques — jamais de prédictions certaines
- Pas de diagnostic médical, légal, financier ou psychologique ferme
- Si tu es incertain, reste nuancé et général

Niveau de détail : analyse complète et approfondie avec nuances

Format de sortie (JSON strict AstroResponse_v1) :
- title : titre personnalisé reflétant l'essentiel du thème, 5–12 mots
- summary : portrait astrologique complet, 6–10 phrases, ton de la persona
- sections : minimum 5 parmi [overall, career, relationships, inner_life, daily_life, strengths, challenges]
  - heading : titre de section évocateur (max 80 chars)
  - content : analyse détaillée, 4–7 phrases, concret et personnalisé (max 2500 chars)
- highlights : 5–8 points forts, traits dominants ou configurations remarquables
- advice : 5–8 conseils actionnables, positifs et spécifiques au thème
- evidence : identifiants UPPER_SNAKE_CASE de TOUS les placements et aspects utilisés
  Exemples : SUN_TAURUS_H10, MOON_CANCER_H8, ASC_SCORPIO, MC_LEO,
             ASPECT_SUN_MOON_TRINE_ORB0, ASPECT_SATURN_ASC_SQUARE_ORB2,
             SUN_RETROGRADE (si applicable)
- disclaimers : 1–2 notes sur la nature indicative de l'astrologie
```

---

## Acceptance Criteria

### AC1 — Prompts en DB après seed
Après exécution de `python backend/scripts/seed_29_prompts.py` :
- `LlmPromptVersionModel` avec `use_case_key="natal_interpretation_short"` et `status=PUBLISHED` existe en DB
- `LlmPromptVersionModel` avec `use_case_key="natal_interpretation"` et `status=PUBLISHED` existe en DB

### AC2 — Lint SHORT valide
Le prompt de `natal_interpretation_short` passe le lint :
- `{{chart_json}}` présent → OK
- `{{locale}}` présent → OK
- `{{use_case}}` présent → OK
- `{{persona_name}}` absent → OK (non requis pour ce use case)

### AC3 — Lint COMPLETE valide
Le prompt de `natal_interpretation` passe le lint :
- `{{chart_json}}` présent → OK
- `{{persona_name}}` présent → OK
- `{{locale}}` présent → OK
- `{{use_case}}` présent → OK

### AC4 — Lint bloque si placeholder manquant
Si un prompt pour `natal_interpretation` ne contient pas `{{persona_name}}` → le lint retourne une erreur, le draft n'est pas créé.
Test : `POST /v1/admin/llm/use-cases/natal_interpretation/prompts` avec un prompt sans `{{persona_name}}` → HTTP 422 avec `errors` contenant la mention du placeholder manquant.

### AC5 — Lint bloque si prompt trop long
Si le developer_prompt dépasse 8000 caractères → erreur de lint.
Si entre 4000 et 8000 → warning mais création autorisée.

### AC6 — Publish via endpoint admin
`PATCH /v1/admin/llm/use-cases/natal_interpretation_short/prompts/{id}/publish` → HTTP 200
La version précédente (si elle existait) passe en `ARCHIVED`.
Un seul prompt `PUBLISHED` par use_case_key.

### AC7 — Cache invalidé après publish
Après publish, `PromptRegistryV2._prompt_cache[use_case_key]` est invalidé.
Le prochain appel au gateway récupère le nouveau prompt depuis DB.

### AC8 — Rollback possible
`POST /v1/admin/llm/use-cases/natal_interpretation_short/rollback` → HTTP 200
Le dernier prompt `ARCHIVED` repasse en `PUBLISHED`.

### AC9 — `prompt_version_id` visible dans GatewayResult
Après un appel au gateway avec le prompt publié, `GatewayResult.meta.prompt_version_id` retourne l'UUID du prompt utilisé.

---

## Tâches Techniques

### T1 — Script de seed des prompts

**Fichier :** `backend/scripts/seed_29_prompts.py`

```python
"""
Seed des prompts nataux (Chapter 29) pour le LLMGateway.
Crée et publie les prompts pour natal_interpretation et natal_interpretation_short.
Idempotent : si un prompt PUBLISHED existe déjà, le script le signale et skip.
"""

from sqlalchemy import select
from app.infra.db.models import LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.session import SessionLocal
from app.llm_orchestration.services.prompt_lint import lint_prompt

NATAL_SHORT_PROMPT = """..."""  # contenu ci-dessus
NATAL_COMPLETE_PROMPT = """..."""  # contenu ci-dessus

PROMPTS_TO_SEED = [
    {
        "use_case_key": "natal_interpretation_short",
        "developer_prompt": NATAL_SHORT_PROMPT,
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_output_tokens": 2048,
    },
    {
        "use_case_key": "natal_interpretation",
        "developer_prompt": NATAL_COMPLETE_PROMPT,
        "model": "gpt-4o-mini",
        "temperature": 0.7,
        "max_output_tokens": 3000,
    },
]

def seed_prompts():
    with SessionLocal() as db:
        for config in PROMPTS_TO_SEED:
            # 1. Vérifier que le use_case existe
            # 2. Linter le prompt (lève exception si erreur)
            # 3. Vérifier si un PUBLISHED existe déjà (skip si oui)
            # 4. Créer LlmPromptVersionModel avec status=PUBLISHED
            # 5. Archiver l'éventuel PUBLISHED précédent
            # 6. Commit
```

**Important :** Le script utilise `lint_prompt()` pour valider avant d'insérer.
Si le lint échoue, lever une exception descriptive avec les erreurs de lint.

### T2 — Vérifier la fonction lint

**Fichier existant :** `backend/app/llm_orchestration/services/prompt_lint.py`

S'assurer que :
- La liste des placeholders requis est bien lue depuis `LlmUseCaseConfigModel.required_prompt_placeholders`
- Le lint vérifie `{{locale}}` et `{{use_case}}` systématiquement (placeholders plateforme)
- Le retour contient `errors` (liste) et `warnings` (liste)

Si ce n'est pas le cas, modifier `prompt_lint.py` en conséquence (sans casser les tests existants).

### T3 — Test du lint pour les prompts nataux

**Fichier :** `backend/app/tests/unit/test_prompt_lint_natal.py`

```python
def test_lint_short_valid():
    """Le prompt SHORT avec {{chart_json}}, {{locale}}, {{use_case}} passe."""

def test_lint_short_missing_chart_json():
    """Le prompt SHORT sans {{chart_json}} échoue avec erreur."""

def test_lint_complete_valid():
    """Le prompt COMPLETE avec tous les placeholders passe."""

def test_lint_complete_missing_persona_name():
    """Le prompt COMPLETE sans {{persona_name}} échoue avec erreur."""

def test_lint_prompt_too_long():
    """Un prompt > 8000 chars échoue au lint."""

def test_lint_prompt_warning_long():
    """Un prompt entre 4000 et 8000 chars passe avec warning."""
```

### T4 — Test d'intégration endpoint admin lint

**Fichier :** `backend/app/tests/integration/test_admin_llm_natal_prompts.py`

Test `POST /v1/admin/llm/use-cases/natal_interpretation/prompts` avec :
- Payload valide → 200 + `data.version_id`
- Payload sans `{{persona_name}}` → 422 + erreurs de lint

---

## Fichiers à Créer / Modifier

| Action | Fichier |
|--------|---------|
| CRÉER | `backend/scripts/seed_29_prompts.py` |
| CRÉER | `backend/app/tests/unit/test_prompt_lint_natal.py` |
| CRÉER | `backend/app/tests/integration/test_admin_llm_natal_prompts.py` |
| MODIFIER si besoin | `backend/app/llm_orchestration/services/prompt_lint.py` |

---

## Critères de "Done"

- [ ] `python backend/scripts/seed_29_prompts.py` s'exécute sans erreur
- [ ] Deux prompts PUBLISHED visibles via `GET /v1/admin/llm/use-cases` (dans `active_prompt_version`)
- [ ] Tests lint passent
- [ ] `GET /v1/admin/llm/use-cases/natal_interpretation_short/contract` montre le prompt actif
- [ ] `GET /v1/admin/llm/use-cases/natal_interpretation/contract` montre le prompt actif avec persona_strategy=required
- [ ] Appel gateway sur `natal_interpretation_short` → `GatewayResult.meta.prompt_version_id` non null
