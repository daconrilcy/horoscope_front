# Story 59.5 : Socle commun des prompts — PromptCommonContext

Status: done

## Story

En tant que système LLM,
je veux recevoir systématiquement dans chaque prompt le contexte astrologique de base de l'utilisateur (interprétation ou données natales, niveau de précision, profil de l'astrologue, période couverte, date du jour),
afin que chaque réponse soit ancrée dans un référentiel cohérent et complet, sans que chaque service ait à assembler manuellement ces informations.

## Acceptance Criteria

1. `backend/app/prompts/common_context.py` existe avec `PromptCommonContext` (Pydantic) et `CommonContextBuilder`.
2. `PromptCommonContext` contient les champs :
   - `natal_interpretation: str | None` — texte interprété du thème natal (si disponible en DB)
   - `natal_data: dict | None` — données brutes calculées du thème natal (si pas d'interprétation)
   - `precision_level: str` — `"complete"` ou `"degradée — heure de naissance manquante"` (ou variante lieu)
   - `astrologer_profile: dict` — profil persona actif complet (nom, style, tonalité, limites)
   - `period_covered: str` — période en format long localisé (ex: `"journée du 18 mars 2026"`)
   - `today_date: str` — date du jour en format long français (ex: `"mercredi 18 mars 2026"`)
   - `use_case_name: str` — nom unique du prompt tel que défini dans `PROMPT_CATALOG`
3. `CommonContextBuilder.build(user_id, use_case_key, period, db)` retourne un `PromptCommonContext`.
4. Si l'interprétation du thème natal existe en DB pour l'utilisateur → `natal_interpretation` est renseigné, `natal_data=None`.
5. Si aucune interprétation n'existe → `natal_interpretation=None`, `natal_data` est renseigné avec les données calculées du thème natal.
6. Le `precision_level` reflète la disponibilité de l'heure et du lieu de naissance :
   - Heure + lieu présents → `"précision complète"`
   - Heure absente → `"précision dégradée — heure de naissance manquante"`
   - Lieu absent → `"précision dégradée — lieu de naissance manquant"`
7. `LLMGateway.execute()` appelle `CommonContextBuilder.build()` et fusionne `PromptCommonContext.model_dump()` dans le dict `context` avant le rendu du prompt.
8. Le prompt `natal_interpretation` reçoit `natal_interpretation=None` (il la produit) mais reçoit `natal_data`, `precision_level`, `astrologer_profile`, `today_date`, `use_case_name`.
9. Tous les templates de prompts en DB incluent un bloc `## Contexte de base` en tête utilisant les variables du socle commun.
10. Le champ `use_case_name` est toujours présent dans le contexte pour tous les appels.
11. Tests unitaires : 3 scénarios couverts (natal interprété, natal non interprété précis, natal non interprété dégradé).
12. `pytest backend/` passe. `ruff check backend/` passe.

## Tasks / Subtasks

- [ ] T1 — Créer `PromptCommonContext` (AC: 2)
  - [ ] T1.1 Créer `backend/app/prompts/common_context.py`
  - [ ] T1.2 Définir `PromptCommonContext(BaseModel)` avec les 7 champs requis
  - [ ] T1.3 Ajouter un `@model_validator(mode='after')` : si `natal_interpretation` est None alors `natal_data` doit être non-None (sauf pour `natal_interpretation` use_case)

- [ ] T2 — Implémenter `CommonContextBuilder.build()` (AC: 3, 4, 5, 6)
  - [ ] T2.1 Identifier le modèle DB d'interprétation natale existante (probablement `NatalInterpretationModel` ou similaire, lié à l'utilisateur)
  - [ ] T2.2 Requête DB : `SELECT interpretation_text FROM natal_interpretations WHERE user_id=? ORDER BY created_at DESC LIMIT 1`
  - [ ] T2.3 Si interprétation trouvée : `natal_interpretation=text`, `natal_data=None`
  - [ ] T2.4 Si pas d'interprétation : appeler `UserNatalChartService.get_natal_data(user_id, db)` pour récupérer les données brutes calculées → `natal_data=chart_json`
  - [ ] T2.5 Calculer `precision_level` depuis le profil utilisateur (birth_time, birth_place)
  - [ ] T2.6 Récupérer `astrologer_profile` via `PersonaConfigService.get_active_persona(db)` → serialiser en dict
  - [ ] T2.7 Formater `today_date` en français : `"mercredi 18 mars 2026"` (utiliser `babel` ou la logique déjà présente dans `current_context.py`)
  - [ ] T2.8 Construire `period_covered` depuis le paramètre `period` (ex: `"daily"` → `"journée du 18 mars 2026"`)
  - [ ] T2.9 Récupérer `use_case_name` depuis `PROMPT_CATALOG[use_case_key].name`

- [ ] T3 — Cas spécial `natal_interpretation` use_case (AC: 8)
  - [ ] T3.1 Détecter `use_case_key == "natal_interpretation"` dans `CommonContextBuilder.build()`
  - [ ] T3.2 Dans ce cas, forcer `natal_interpretation=None` (le prompt va la produire, pas la consommer)
  - [ ] T3.3 Fournir `natal_data`, `precision_level`, `astrologer_profile`, `today_date` normalement

- [ ] T4 — Intégrer dans `LLMGateway.execute()` (AC: 7, 10)
  - [ ] T4.1 Lire entièrement `backend/app/llm_orchestration/gateway.py`
  - [ ] T4.2 Au début de `execute()`, après validation de l'input, appeler `CommonContextBuilder.build(user_id, use_case, period, db)`
  - [ ] T4.3 Fusionner avec `context` existant : `context = {**context, **common_ctx.model_dump()}`
  - [ ] T4.4 S'assurer que les clefs du `common_context` ne peuvent pas écraser des clefs spécifiques au use_case (priorité aux données use_case si conflit de clef)
  - [ ] T4.5 Vérifier que `use_case_name` est toujours présent après fusion

- [ ] T5 — Mettre à jour tous les templates de prompts en DB (AC: 9)
  - [ ] T5.1 Lire les prompts publiés pour chaque use_case via le registre
  - [ ] T5.2 Ajouter en tête de chaque prompt un bloc `## Contexte de base` :
    ```
    ## Contexte de base — {{ use_case_name }}
    Date du jour : {{ today_date }}
    Période couverte : {{ period_covered }}
    Astrologue : {{ astrologer_profile.name }} — {{ astrologer_profile.style }}
    Précision du thème natal : {{ precision_level }}

    {% if natal_interpretation %}
    ### Thème natal interprété
    {{ natal_interpretation }}
    {% elif natal_data %}
    ### Données natales (non encore interprétées)
    Soleil : {{ natal_data.planets.sun.sign }} maison {{ natal_data.planets.sun.house }}
    {# ... autres planètes principales ... #}
    {% endif %}
    ```
  - [ ] T5.3 Publier les nouvelles versions de chaque prompt (incrémenter version, archiver précédentes)
  - [ ] T5.4 Pour `natal_interpretation` : bloc adapté sans la section `natal_interpretation` (remplacé par instruction de production)

- [ ] T6 — Tests unitaires (AC: 11)
  - [ ] T6.1 Test scénario A — natal interprété :
    - Mock DB retourne un texte d'interprétation
    - `CommonContextBuilder.build()` → `natal_interpretation` renseigné, `natal_data=None`
  - [ ] T6.2 Test scénario B — natal non interprété, précision complète :
    - Mock DB sans interprétation, profil avec birth_time + birth_place
    - `natal_interpretation=None`, `natal_data` non None, `precision_level="précision complète"`
  - [ ] T6.3 Test scénario C — natal non interprété, précision dégradée :
    - Mock profil sans birth_time
    - `precision_level="précision dégradée — heure de naissance manquante"`
  - [ ] T6.4 Test scénario D — use_case `natal_interpretation` :
    - `natal_interpretation=None` forcé même si interprétation existe en DB
  - [ ] T6.5 Test intégration : le gateway fusionne correctement `common_context` dans le `context` final

- [ ] T7 — Validation finale (AC: 12)
  - [ ] T7.1 `ruff check backend/` → 0 erreur
  - [ ] T7.2 `pytest backend/` → tous les tests passent

## Dev Notes

### Modèle DB de l'interprétation natale

Rechercher dans `backend/app/infra/db/models/` le modèle qui stocke les interprétations natales générées. D'après l'Epic 29, c'est probablement `NatalInterpretation` ou `AstroResponse`. La jointure est `user_id` + `status=published` ou dernière version.

### Format du `natal_data` dans le contexte

Utiliser `build_chart_json()` d'Epic 29 (Story 29-N1) si disponible :
```python
from app.services.natal_chart_service import build_chart_json
natal_data = build_chart_json(natal_result, birth_profile, degraded_mode)
```
Ce JSON est canonique et connu du LLM depuis Epic 29.

### `astrologer_profile` — structure attendue

D'après `PersonaConfigService` et Epic 28 (personas paramétriques), le profil contient au moins :
- `name: str` — nom de l'astrologue
- `style: str` — style rédactionnel
- `tone: str` — tonalité
- `limits: list[str]` — domaines exclus/limites

Sérialiser via `.model_dump()` ou `.dict()`.

### Fusion dans le gateway — ordre de priorité

Si une clef existe à la fois dans `common_context` et dans `context` spécifique au use_case, **le contexte use_case a priorité** :
```python
merged_context = {**common_ctx.model_dump(), **context}
```
(Le contexte use_case écrase le contexte commun en cas de conflit.)

### Formatage de la date en français

La logique de formatage en français est probablement déjà dans `backend/app/services/current_context.py`. Réutiliser :
```python
MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin",
           "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
JOURS_FR = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

def format_date_fr(d: date) -> str:
    jour = JOURS_FR[d.weekday()]
    mois = MOIS_FR[d.month - 1]
    return f"{jour} {d.day} {mois} {d.year}"
```

### Project Structure Notes

```
backend/app/prompts/
  __init__.py          (59.2)
  catalog.py           (59.2)
  validators.py        (59.2)
  common_context.py    ← NOUVEAU (59.5)
```

### References
- [Source: backend/app/infra/db/models/] — modèles DB (natal interpretation, persona)
- [Source: backend/app/services/current_context.py] — formatage date française
- [Source: backend/app/services/persona_config_service.py] — persona active
- [Source: backend/app/llm_orchestration/gateway.py] — point d'injection
- [Source: docs/agent/story-29-N1-chart-json-canon.md] — format `chart_json` canonique
- [Source: _bmad-output/planning-artifacts/epic-59-refacto-moteur-ia-v2.md] — epic parent

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Completion Notes List

- Implémentation complète : `PromptCommonContext` Pydantic, `CommonContextBuilder.build()`, fusion dans `LLMGateway.execute()` pour tous les use_cases.
- **Code review (post-implémentation) :**
  - ISSUE-10 (Info) : double appel à `_validate_period()` dans `guidance_service.py` (déjà appelé ligne 559, rappelé inutilement ligne 616 dans le bloc astro_context) — appel redondant supprimé.
  - ISSUE-11 (Bug critique) : `validate_natal_source()` dans `PromptCommonContext` vérifiait `use_case_name` (le nom lisible du catalogue, qui tombe back sur `use_case_key` string si l'entrée catalogue est absente) — comparaison fragile. Correction : ajout du champ `use_case_key: str` dans `PromptCommonContext` pour le branchement logique stable, validator migré sur `self.use_case_key.startswith("natal_interpretation")`. Le `CommonContextBuilder.build()` passe maintenant `use_case_key=use_case_key` en plus.
  - ISSUE-12 (Bug critique) : `authorized_vars` dans `gateway.py` ne contenait pas les variables du socle commun ni `astro_context` — les templates de prompts ne pouvaient donc pas les utiliser comme variables de rendu. Ajout des 9 variables manquantes : `astro_context`, `natal_interpretation`, `natal_data`, `precision_level`, `astrologer_profile`, `period_covered`, `today_date`, `use_case_name`, `use_case_key`.
- Tests : 1342 passed, ruff clean.

### File List

- `backend/app/prompts/common_context.py` — PromptCommonContext (+ champ use_case_key), CommonContextBuilder
- `backend/app/llm_orchestration/gateway.py` — authorized_vars étendu (9 variables), appel CommonContextBuilder.build()
- `backend/app/services/guidance_service.py` — suppression appel _validate_period() dupliqué
