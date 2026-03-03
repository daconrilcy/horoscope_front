# Story 30-3 — Gateway GPT-5 : Orchestration Responses API avec reasoning & verbosity

## Contexte & Périmètre

**Epic ASTRO-30 / Story 30-3**
**Chapitre 30** — AstroResponse_v2 & Orchestration GPT-5

**Dépend de :** Story 30-2 (AstroResponse_v2 en DB, use case natal_interpretation pointant sur v2)

La Responses API de GPT-5 expose deux paramètres absents de gpt-4o-mini :
- **`verbosity`** (`"low"` | `"medium"` | `"high"`) : densité du texte produit
- **`reasoning`** (`{"effort": "minimal"` | `"low"` | `"medium"` | `"high"}`) : profondeur de raisonnement interne avant réponse

Ces paramètres remplacent avantageusement les instructions de longueur dans le prompt
(`"10–18 phrases"`, `"max 4000 chars"`), qui créent des contradictions avec les limites du JSON schema
et incitent le modèle à compter les phrases plutôt qu'à construire du sens.

De plus, GPT-5 via la Responses API recommande des **typed content blocks** pour les messages :
```json
{"role": "developer", "content": [{"type": "input_text", "text": "..."}]}
```
au lieu de la syntaxe string plate :
```json
{"role": "developer", "content": "..."}
```

**Cette story :**
1. Ajoute les colonnes `reasoning_effort` et `verbosity` à `llm_prompt_versions` (Alembic)
2. Expose ces champs dans `LlmPromptVersionModel` (ORM) et `UseCaseConfig` (Pydantic)
3. Passe ces paramètres du gateway au `ResponsesClient`
4. Adapte `ResponsesClient` : typed content blocks pour GPT-5, `reasoning` + `verbosity` dans le payload
5. Crée un script de seed qui publie un nouveau prompt `natal_interpretation` optimisé GPT-5
   (sans contraintes de longueur, avec auto-check evidence, reasoning_effort="low", verbosity="high")

**Stratégie de déploiement safe :**
- `natal_interpretation_short` reste sur `gpt-4o-mini` sans `reasoning_effort` ni `verbosity`
- `natal_interpretation` (complet, payant) passe sur `gpt-5` avec les nouveaux paramètres
- Le mécanisme d'override via env var `LLM_MODEL_OVERRIDE_NATAL_INTERPRETATION` (Story 30-1) reste fonctionnel

---

## Hypothèses & Dépendances

- Story 30-2 exécutée : `AstroResponse_v2` en DB, `natal_interpretation` y pointe
- `LlmPromptVersionModel` est dans `backend/app/infra/db/models/llm_prompt.py`
- Alembic est configuré (`backend/alembic.ini`, `backend/migrations/`)
- Convention de nommage migrations : `YYYYMMDD_NNNN_description.py` (ex: `20260226_0027_...`)
- `ResponsesClient.execute()` reçoit déjà `model` et gère l'exclusion de `temperature` pour les modèles reasoning (prefixe `gpt-5-`)
- `LLMGateway.execute()` lit `config.model` (depuis `UseCaseConfig`) et le passe au client
- La détection "reasoning model" dans `gateway.py` (ligne 226) couvre déjà `_REASONING_PREFIXES = ("o1-", "o3-", "o4-", "gpt-5-")` — vérifier que `"gpt-5"` exact (sans tiret) est aussi couvert
- `PromptRegistryV2` lit `LlmPromptVersionModel` et construit `UseCaseConfig` via le gateway (`gateway.py:181-198`)

---

## Objectifs / Non-Objectifs

**Objectifs :**
- Migration Alembic : ajouter `reasoning_effort VARCHAR(20) NULL` et `verbosity VARCHAR(20) NULL` à `llm_prompt_versions`
- ORM `LlmPromptVersionModel` : refléter les nouveaux champs
- Pydantic `UseCaseConfig` : ajouter `reasoning_effort: Optional[str] = None` et `verbosity: Optional[str] = None`
- `LLMGateway.execute()` : transmettre `reasoning_effort` et `verbosity` de `config` au client
- `ResponsesClient.execute()` : appliquer les typed content blocks pour GPT-5, passer `reasoning` et `verbosity`
- Script de seed `seed_30_3_gpt5_prompts.py` : publier un nouveau prompt `natal_interpretation` optimisé GPT-5 sans contraintes de longueur dans le texte, avec `model="gpt-5"`, `reasoning_effort="low"`, `verbosity="high"`, `max_output_tokens=32000`
- Tests : gateway passe bien les paramètres au client, client les inclut dans le payload

**Non-Objectifs :**
- Modifier le prompt `natal_interpretation_short` (reste sur v1 + gpt-4o-mini)
- Implémenter le caching de la Responses API GPT-5
- Refactorer la structure 3-rôles (system/developer/user avec chart_json en user msg) : le `chart_json` reste dans le developer prompt via `{{chart_json}}`, la séparation 3-rôles est reportée
- Modifier le frontend
- Ajouter de nouveaux fields au JSON schema (objet de Story 30-2)

---

## Acceptance Criteria

### AC1 — Migration Alembic appliquée

Après `alembic upgrade head` :
- La table `llm_prompt_versions` a deux nouvelles colonnes :
  - `reasoning_effort VARCHAR(20) NULL DEFAULT NULL`
  - `verbosity VARCHAR(20) NULL DEFAULT NULL`
- Les lignes existantes ont `reasoning_effort=NULL`, `verbosity=NULL`
- `alembic downgrade -1` supprime proprement les deux colonnes

### AC2 — `LlmPromptVersionModel` reflète les nouveaux champs

```python
# backend/app/infra/db/models/llm_prompt.py

class LlmPromptVersionModel(Base):
    # ... champs existants ...
    reasoning_effort: Mapped[str | None] = mapped_column(
        String(20), nullable=True, default=None
    )  # "low", "medium", "minimal", "none", None
    verbosity: Mapped[str | None] = mapped_column(
        String(20), nullable=True, default=None
    )  # "high", "medium", "low", None
```

### AC3 — `UseCaseConfig` expose `reasoning_effort` et `verbosity`

```python
# backend/app/llm_orchestration/models.py

class UseCaseConfig(BaseModel):
    # ... champs existants ...
    reasoning_effort: Optional[str] = None  # None = non supporté par le modèle
    verbosity: Optional[str] = None         # None = non supporté par le modèle
```

Le gateway construit `UseCaseConfig` depuis `LlmPromptVersionModel` (bloc lignes 181-198 de `gateway.py`).
Ajouter la transmission des deux champs :

```python
config = UseCaseConfig(
    model=db_prompt.model,
    # ... champs existants ...
    reasoning_effort=db_prompt.reasoning_effort,  # AJOUT
    verbosity=db_prompt.verbosity,                # AJOUT
)
```

### AC4 — `ResponsesClient.execute()` accepte et transmet `reasoning_effort` et `verbosity`

**Signature étendue :**

```python
async def execute(
    self,
    messages: List[Dict[str, str]],
    model: str,
    temperature: float = 0.7,
    max_output_tokens: int = 1000,
    timeout_seconds: int = 30,
    request_id: str = "",
    trace_id: str = "",
    use_case: str = "",
    response_format: Optional[Dict[str, Any]] = None,
    reasoning_effort: Optional[str] = None,   # NOUVEAU
    verbosity: Optional[str] = None,           # NOUVEAU
) -> GatewayResult:
```

**Payload de l'API pour GPT-5 :**

Si `reasoning_effort` est fourni et non `None` :
```python
params["reasoning"] = {"effort": reasoning_effort}
```

Si `verbosity` est fourni et non `None` :
```python
params["verbosity"] = verbosity
```

### AC5 — Typed content blocks pour les modèles GPT-5

Pour les modèles dont le nom commence par `"gpt-5"` (ex: `"gpt-5"`, `"gpt-5.2"`), les messages
sont convertis en typed content blocks avant d'être envoyés à l'API :

```python
# Entrée (format actuel, string content) :
[
    {"role": "system", "content": "Texte de politique..."},
    {"role": "developer", "content": "Texte du prompt développeur..."},
    {"role": "user", "content": "Données du thème natal..."},
]

# Sortie (typed content blocks pour GPT-5) :
[
    {"role": "system", "content": [{"type": "input_text", "text": "Texte de politique..."}]},
    {"role": "developer", "content": [{"type": "input_text", "text": "Texte du prompt développeur..."}]},
    {"role": "user", "content": [{"type": "input_text", "text": "Données du thème natal..."}]},
]
```

La conversion ne s'applique que si le content du message est une string. Si c'est déjà une liste
(typed blocks), ne pas convertir (idempotence).

```python
def _to_typed_content_blocks(
    messages: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Convert string content to typed content blocks for GPT-5 Responses API."""
    result = []
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            converted = {**msg, "content": [{"type": "input_text", "text": content}]}
        else:
            converted = msg  # Already typed blocks
        result.append(converted)
    return result

# Dans do_create(), avant d'assigner params["input"] :
is_gpt5 = model.startswith("gpt-5")
input_messages = _to_typed_content_blocks(messages) if is_gpt5 else messages
params["input"] = input_messages
```

### AC6 — Détection reasoning models étendue dans `gateway.py`

La détection actuelle (ligne 226) couvre `_REASONING_PREFIXES = ("o1-", "o3-", "o4-", "gpt-5-")`.
Étendre pour couvrir `"gpt-5"` exact (sans suffixe) :

```python
_REASONING_PREFIXES = ("o1-", "o3-", "o4-", "gpt-5-", "gpt-5")
_REASONING_EXACT = {"o1", "o3", "o4", "gpt-5"}
```

Attention : `"gpt-5"` dans `_REASONING_PREFIXES` capturait aussi `"gpt-5.2"`, `"gpt-5-turbo"` etc.
Utiliser `startswith("gpt-5")` (sans tiret final) couvre tous les variants GPT-5.

### AC7 — `LLMGateway.execute()` transmet `reasoning_effort` et `verbosity` au client

Dans l'appel à `self.client.execute()` (autour de la ligne 451 de `gateway.py`) :

```python
result = await self.client.execute(
    messages=messages,
    model=config.model,
    temperature=config.temperature,
    max_output_tokens=config.max_output_tokens,
    timeout_seconds=config.timeout_seconds,
    request_id=request_id,
    trace_id=trace_id,
    use_case=use_case,
    response_format={...} if schema_dict else None,
    reasoning_effort=config.reasoning_effort,  # AJOUT
    verbosity=config.verbosity,                 # AJOUT
)
```

### AC8 — Script de seed `seed_30_3_gpt5_prompts.py`

Après exécution de `python backend/scripts/seed_30_3_gpt5_prompts.py` :
- `LlmPromptVersionModel(use_case_key="natal_interpretation", status=PUBLISHED)` a :
  - `model = "gpt-5"` (ou valeur configurée)
  - `temperature = 0.5` (GPT-5 : valeur basse ou ignorée selon le modèle)
  - `max_output_tokens = 32000`
  - `reasoning_effort = "low"`
  - `verbosity = "high"`
  - Prompt sans contraintes de longueur dans le texte (pas de "max 4000 chars")
  - Prompt avec section auto-check evidence
- Le prompt passe le lint (`PromptLint.lint_prompt`)
- L'ancien prompt `natal_interpretation` PUBLISHED passe en ARCHIVED
- `natal_interpretation_short` reste **inchangé** (gpt-4o-mini, v1)

**Contenu du nouveau prompt `NATAL_COMPLETE_PROMPT_V2` :**

Points clés de la réécriture vs le prompt actuel (`NATAL_COMPLETE_PROMPT` dans `seed_29_prompts.py`) :

1. **Supprimer** toutes les contraintes "max N chars" et "N–M phrases" → c'est le schema JSON v2 et `verbosity` qui gouvernent la densité
2. **Conserver** les règles de vérité (ne pas inventer de données), le style non-fataliste, le persona
3. **Renforcer** l'auto-check evidence (rendre la règle mécanique, pas rhétorique)
4. **Ajouter** explicitement : "Aucun UPPER_SNAKE_CASE dans le texte libre (réservé à evidence)"
5. **Remplacer** "7–12 phrases par section" par des exigences de contenu (constat + manifestation + tension + levier)

```
Langue de réponse : français ({{locale}}). Contexte : use_case={{use_case}}.

Tu incarnes {{persona_name}}, astrologue expert. Adapte ton style à cette persona tout en restant
professionnel, bienveillant, moderne et non fataliste. Tu écris en prose fluide avec des
transitions naturelles entre les idées. Interdiction de lister des placements sans les relier.

Données (source unique et exclusive) :
{{chart_json}}

═══ RÈGLES DE VÉRITÉ (inviolables) ═══
- Base-toi UNIQUEMENT sur les données présentes dans chart_json.
- N'invente aucun placement, aspect, maison, dominante, maître, dignité, rétrogradation, nœud,
  astéroïde ou point qui n'apparaît pas explicitement dans chart_json.
- Si une donnée nécessaire (ex : ascendant/maisons/heure) est absente, signale-le et adapte
  l'analyse (plus générale, sans combler le vide par de l'invention).
- Tu parles de tendances, potentiels et dynamiques, jamais de certitudes ni de prédictions datées.
- Aucun diagnostic médical, légal, financier ou psychologique.

═══ EXIGENCE PREMIUM ═══
- HIÉRARCHISÉ : identifie les 3 dominantes du thème (éléments récurrents, stelliums, angles,
  maisons chargées) et fais-les vivre dans toutes les sections.
- INTÉGRATIF : montre au moins une tension interne (deux besoins contradictoires) et une voie
  d'intégration concrète.
- CONCRET : pour chaque grande idée, donne une manifestation observable dans la vie réelle et un
  levier d'ajustement. Formule au moins un "si… alors…" pratico-pratique par section.
- ANTI-GÉNÉRIQUE : chaque section relie au moins 2 éléments du thème entre eux si les données
  le permettent. Pas de formules creuses qui s'appliqueraient à n'importe quel thème.

═══ EVIDENCE / TRAÇABILITÉ ═══
Avant de finaliser ta réponse, effectue ce contrôle en trois étapes :
1. Liste tous les éléments astrologiques que tu as mentionnés (planètes, signes, maisons, aspects,
   angles, maîtres, dignités, rétrogradations).
2. Pour chacun, vérifie qu'il est explicitement présent dans chart_json.
3. Produis le champ "evidence" avec UNIQUEMENT les identifiants UPPER_SNAKE_CASE correspondant
   aux éléments réellement utilisés dans l'interprétation.
- Si chart_json ne fournit aucun identifiant exploitable → evidence = []
- Ne cite dans le texte AUCUN élément qui ne figure pas dans evidence.

═══ FORMAT DE SORTIE : JSON strict AstroResponse_v2 ═══
- title : reflète le fil rouge du thème.
- summary : narratif, cohérent. Doit annoncer les dominantes + le fil rouge + une tension + une
  promesse d'intégration.
- sections : couvrir idéalement [overall, inner_life, relationships, career, daily_life,
  strengths, challenges]. Minimum 6 sections.
  Chaque section doit inclure : un constat dynamique, une manifestation concrète, un risque
  typique (réflexe), un levier d'intégration (ressource), et un micro "si… alors…".
- highlights : phrases complètes ancrées dans des éléments du thème. Chacune doit être
  auto-suffisante et spécifique.
- advice : conseils actionnables et nuancés, spécifiques au thème. Éviter les banalités
  universelles ("prends soin de toi", "fais confiance au processus").
- disclaimers : 1–2 notes prudentes (astrologie = piste de réflexion, libre arbitre).

⚠️ FORMATAGE (impératif) :
- Pas de numérotation ("1.", "2."...) dans les strings. Pas de tirets "-" ni puces dans les
  chaînes. Le rendu est géré par l'application.
- Dans TOUT le texte libre (title, summary, sections/content, highlights, advice) : emploie
  UNIQUEMENT les noms naturels en français (Soleil, Lune, Vénus, Taureau, Maison 10, Milieu
  du Ciel, Ascendant, trigone, carré, opposition, conjonction, rétrograde…).
- Les codes UPPER_SNAKE_CASE sont STRICTEMENT réservés au champ evidence.
- Pas de redondance entre summary et sections. Chaque section apporte un angle nouveau.

⚠️ GESTION D'ERREUR :
Si l'entrée est malformée ou trop incomplète (ex : planets absent) → retourne un JSON
AstroResponse_v2 avec title="Erreur : Données insuffisantes", summary expliquant la cause,
sections/highlights/advice vides, evidence=[].
```

### AC9 — Lint passe pour le nouveau prompt

`PromptLint.lint_prompt(NATAL_COMPLETE_PROMPT_V2, use_case_required_placeholders=["chart_json", "persona_name", "locale", "use_case"])` retourne `passed=True`.

### AC10 — Compatibilité avec le mécanisme d'override de modèle (Story 30-1)

Si `LLM_MODEL_OVERRIDE_NATAL_INTERPRETATION=gpt-5.2` est défini :
- Le gateway remplace `config.model = "gpt-5.2"` (Story 30-1, gateway.py:216-247)
- La détection reasoning model s'applique (`gpt-5.2` commence par `gpt-5`) → `max_output_tokens` minimum 16384 si inférieur
- `reasoning_effort` et `verbosity` sont toujours lus depuis `config` (DB) et passés au client
- Le typed content blocks s'applique car `gpt-5.2`.startswith(`"gpt-5"`) est True

---

## Tâches Techniques

### T1 — Migration Alembic

**Fichier à créer :** `backend/migrations/versions/20260302_0030_add_reasoning_effort_verbosity_to_prompts.py`

```python
"""add_reasoning_effort_verbosity_to_prompts

Revision ID: <généré par alembic>
Revises: <dernière révision>
Create Date: 2026-03-02 ...
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "<à générer>"
down_revision: Union[str, Sequence[str], None] = "<dernière revision>"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "llm_prompt_versions",
        sa.Column("reasoning_effort", sa.String(20), nullable=True, server_default=None),
    )
    op.add_column(
        "llm_prompt_versions",
        sa.Column("verbosity", sa.String(20), nullable=True, server_default=None),
    )


def downgrade() -> None:
    op.drop_column("llm_prompt_versions", "verbosity")
    op.drop_column("llm_prompt_versions", "reasoning_effort")
```

**Générer avec Alembic (recommandé) :**

```bash
cd backend
alembic revision --autogenerate -m "add_reasoning_effort_verbosity_to_prompts"
# Ajuster le fichier généré pour supprimer les colonnes de migration auto non désirées
alembic upgrade head
```

### T2 — ORM `LlmPromptVersionModel`

**Fichier :** `backend/app/infra/db/models/llm_prompt.py`

Ajouter deux champs après `fallback_use_case_key` :

```python
class LlmPromptVersionModel(Base):
    __tablename__ = "llm_prompt_versions"
    # ... champs existants ...
    fallback_use_case_key: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # AJOUT Story 30-3
    reasoning_effort: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default=None,
        comment="GPT-5 reasoning effort: 'minimal', 'low', 'medium', 'high'. NULL = non applicable.",
    )
    verbosity: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        default=None,
        comment="GPT-5 verbosity: 'low', 'medium', 'high'. NULL = non applicable.",
    )
    # ... reste inchangé ...
```

### T3 — Pydantic `UseCaseConfig`

**Fichier :** `backend/app/llm_orchestration/models.py`

```python
class UseCaseConfig(BaseModel):
    """Configuration for a specific LLM use case."""
    model: str
    temperature: float = 0.7
    max_output_tokens: int = 1000
    timeout_seconds: int = 30
    system_core_key: str = "default_v1"
    developer_prompt: str
    prompt_version_id: str = "hardcoded-v1"
    persona_strategy: str = "optional"
    safety_profile: str = "astrology"
    input_schema: Optional[Dict[str, Any]] = None
    output_schema_id: Optional[str] = None
    required_prompt_placeholders: List[str] = Field(default_factory=list)
    fallback_use_case: Optional[str] = None
    # AJOUT Story 30-3
    reasoning_effort: Optional[str] = None
    verbosity: Optional[str] = None
```

### T4 — `LLMGateway.execute()` : transmission des paramètres GPT-5

**Fichier :** `backend/app/llm_orchestration/gateway.py`

**4a. Construction de `UseCaseConfig` depuis DB (bloc lignes 181-198) :**

```python
config = UseCaseConfig(
    model=db_prompt.model,
    temperature=db_prompt.temperature,
    max_output_tokens=db_prompt.max_output_tokens,
    system_core_key="default_v1",
    developer_prompt=db_prompt.developer_prompt,
    prompt_version_id=str(db_prompt.id),
    required_prompt_placeholders=required,
    fallback_use_case=resolved_fallback,
    persona_strategy=db_use_case.persona_strategy if db_use_case else "optional",
    safety_profile=db_use_case.safety_profile if db_use_case else "astrology",
    output_schema_id=db_use_case.output_schema_id if db_use_case else None,
    input_schema=db_use_case.input_schema if db_use_case else None,
    reasoning_effort=db_prompt.reasoning_effort,  # AJOUT
    verbosity=db_prompt.verbosity,                 # AJOUT
)
```

**4b. Appel à `self.client.execute()` (ligne ~451) :**

```python
result = await self.client.execute(
    messages=messages,
    model=config.model,
    temperature=config.temperature,
    max_output_tokens=config.max_output_tokens,
    timeout_seconds=config.timeout_seconds,
    request_id=request_id,
    trace_id=trace_id,
    use_case=use_case,
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": use_case,
            "schema": schema_dict,
            "strict": True,
        },
    } if schema_dict else None,
    reasoning_effort=config.reasoning_effort,  # AJOUT
    verbosity=config.verbosity,                 # AJOUT
)
```

**4c. Extension de la détection reasoning models (ligne ~226) :**

```python
# Remplacer :
_REASONING_PREFIXES = ("o1-", "o3-", "o4-", "gpt-5-")
_REASONING_EXACT = {"o1", "o3", "o4"}

# Par :
_REASONING_PREFIXES = ("o1-", "o3-", "o4-", "gpt-5",)  # "gpt-5" comme prefix couvre gpt-5, gpt-5.2, gpt-5-turbo
_REASONING_EXACT = {"o1", "o3", "o4"}
```

Attention : la détection s'applique déjà pour les overrides via env. Elle doit aussi s'appliquer
pour les modèles DB-loaded. Ajouter une vérification similaire sur `config.model` (après résolution DB) :

```python
# Après résolution de config (ligne ~248, après model override)
_REASONING_PREFIXES = ("o1-", "o3-", "o4-", "gpt-5")
_is_db_reasoning = config.model.startswith(_REASONING_PREFIXES) or config.model in {"o1", "o3", "o4"}
if _is_db_reasoning:
    updates = {}
    if config.max_output_tokens < 16384:
        updates["max_output_tokens"] = 16384
    if config.timeout_seconds < 180:
        updates["timeout_seconds"] = 180
    if updates:
        config = config.model_copy(update=updates)
        logger.info("gateway_db_model_is_reasoning model=%s updates=%s", config.model, updates)
```

### T5 — `ResponsesClient.execute()` : typed content blocks + params GPT-5

**Fichier :** `backend/app/llm_orchestration/providers/responses_client.py`

**5a. Ajouter la méthode de conversion :**

```python
@staticmethod
def _to_typed_content_blocks(
    messages: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Convert string message content to typed content blocks for GPT-5 Responses API.
    GPT-5 recommends: {"role": "developer", "content": [{"type": "input_text", "text": "..."}]}
    instead of: {"role": "developer", "content": "..."}
    Idempotent: if content is already a list, returns as-is.
    """
    result = []
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            converted = {**msg, "content": [{"type": "input_text", "text": content}]}
        else:
            converted = msg
        result.append(converted)
    return result
```

**5b. Modifier la signature de `execute()` :**

```python
async def execute(
    self,
    messages: List[Dict[str, str]],
    model: str,
    temperature: float = 0.7,
    max_output_tokens: int = 1000,
    timeout_seconds: int = 30,
    request_id: str = "",
    trace_id: str = "",
    use_case: str = "",
    response_format: Optional[Dict[str, Any]] = None,
    reasoning_effort: Optional[str] = None,  # NOUVEAU
    verbosity: Optional[str] = None,           # NOUVEAU
) -> GatewayResult:
```

**5c. Modifier `do_create()` :**

```python
async def do_create() -> "Response":
    # Conversion typed content blocks pour GPT-5
    is_gpt5 = model.startswith("gpt-5")
    input_messages = self._to_typed_content_blocks(messages) if is_gpt5 else messages

    params: Dict[str, Any] = {
        "model": model,
        "input": input_messages,  # type: ignore
        "max_output_tokens": max_output_tokens,
    }

    # Temperature : exclue pour les reasoning models
    supports_temperature = not (
        model.startswith(("o1-", "o3-", "gpt-5-", "gpt-5"))
        or model in ["o1", "o3"]
    )
    if supports_temperature:
        params["temperature"] = temperature

    # Paramètres GPT-5 : reasoning effort
    if reasoning_effort is not None:
        params["reasoning"] = {"effort": reasoning_effort}
        logger.debug(
            "responses_client_gpt5_reasoning model=%s effort=%s use_case=%s",
            model, reasoning_effort, use_case
        )

    # Paramètres GPT-5 : verbosity
    if verbosity is not None:
        params["verbosity"] = verbosity
        logger.debug(
            "responses_client_gpt5_verbosity model=%s verbosity=%s use_case=%s",
            model, verbosity, use_case
        )

    if response_format:
        fmt = dict(response_format)
        if fmt.get("type") == "json_schema" and "json_schema" in fmt:
            nested = fmt.pop("json_schema")
            fmt.update(nested)
        params["text"] = {"format": fmt}

    return await client.responses.create(**params)
```

### T6 — Script de seed `seed_30_3_gpt5_prompts.py`

**Fichier :** `backend/scripts/seed_30_3_gpt5_prompts.py`

```python
"""
Seed : prompts nataux optimisés GPT-5 pour le use case natal_interpretation.

Ce script :
- Met à jour uniquement natal_interpretation (payant, complete)
- Publie un nouveau prompt avec model="gpt-5", reasoning_effort="low", verbosity="high"
- NE modifie PAS natal_interpretation_short (reste gpt-4o-mini, v1)

Dépend de : seed_30_2_astroresponse_v2.py (natal_interpretation pointe sur AstroResponse_v2)

Run with:
    python -m scripts.seed_30_3_gpt5_prompts
"""
import logging
from sqlalchemy import select
from app.infra.db.models import LlmOutputSchemaModel, LlmPromptVersionModel, LlmUseCaseConfigModel
from app.infra.db.models.llm_prompt import PromptStatus
from app.infra.db.session import SessionLocal
from app.llm_orchestration.services.prompt_lint import PromptLint
from app.llm_orchestration.services.prompt_registry_v2 import PromptRegistryV2, utc_now

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

NATAL_COMPLETE_PROMPT_V2 = """..."""  # Voir AC8 pour le contenu complet

GPT5_CONFIG = {
    "use_case_key": "natal_interpretation",
    "developer_prompt": NATAL_COMPLETE_PROMPT_V2,
    "model": "gpt-5",
    "temperature": 0.5,        # Ignoré par GPT-5 si reasoning actif, mais stocké
    "max_output_tokens": 32000,
    "reasoning_effort": "low",
    "verbosity": "high",
}


def seed():
    db = SessionLocal()
    try:
        key = GPT5_CONFIG["use_case_key"]

        # 1. Vérifier que use case existe
        uc = db.execute(
            select(LlmUseCaseConfigModel).where(LlmUseCaseConfigModel.key == key)
        ).scalar_one_or_none()
        if not uc:
            logger.error("Use case '%s' not found. Run seed_29_prompts.py first.", key)
            return

        # 2. Vérifier que AstroResponse_v2 est le schema pointé
        schema = db.get(LlmOutputSchemaModel, uc.output_schema_id) if uc.output_schema_id else None
        if not schema or schema.name != "AstroResponse_v2":
            logger.warning(
                "use case '%s' ne pointe pas sur AstroResponse_v2 (actuel: %s). "
                "Exécuter seed_30_2_astroresponse_v2.py d'abord.",
                key, schema.name if schema else "None"
            )

        # 3. Linter le prompt
        lint_res = PromptLint.lint_prompt(
            GPT5_CONFIG["developer_prompt"],
            use_case_required_placeholders=["chart_json", "persona_name", "locale", "use_case"],
        )
        if not lint_res.passed:
            raise RuntimeError(f"Lint FAILED for {key}: {lint_res.errors}")
        if lint_res.warnings:
            logger.warning("Lint warnings for %s: %s", key, lint_res.warnings)

        # 4. Archiver le PUBLISHED actuel si contenu différent
        current_p = db.execute(
            select(LlmPromptVersionModel).where(
                LlmPromptVersionModel.use_case_key == key,
                LlmPromptVersionModel.status == PromptStatus.PUBLISHED,
            )
        ).scalar_one_or_none()

        if (
            current_p
            and current_p.developer_prompt == GPT5_CONFIG["developer_prompt"]
            and current_p.model == GPT5_CONFIG["model"]
            and current_p.reasoning_effort == GPT5_CONFIG["reasoning_effort"]
            and current_p.verbosity == GPT5_CONFIG["verbosity"]
        ):
            logger.info("Prompt for %s already published and identical. Skipping.", key)
            return

        if current_p:
            current_p.status = PromptStatus.ARCHIVED
            logger.info("Archived previous prompt version for %s", key)

        # 5. Créer et publier la nouvelle version
        new_v = LlmPromptVersionModel(
            use_case_key=key,
            status=PromptStatus.PUBLISHED,
            developer_prompt=GPT5_CONFIG["developer_prompt"],
            model=GPT5_CONFIG["model"],
            temperature=GPT5_CONFIG["temperature"],
            max_output_tokens=GPT5_CONFIG["max_output_tokens"],
            reasoning_effort=GPT5_CONFIG["reasoning_effort"],  # NOUVEAU champ
            verbosity=GPT5_CONFIG["verbosity"],                 # NOUVEAU champ
            created_by="system",
            published_at=utc_now(),
        )
        db.add(new_v)
        db.commit()

        PromptRegistryV2.invalidate_cache(key)
        logger.info(
            "Published GPT-5 prompt for %s (model=%s, reasoning_effort=%s, verbosity=%s)",
            key, GPT5_CONFIG["model"], GPT5_CONFIG["reasoning_effort"], GPT5_CONFIG["verbosity"]
        )
    except Exception:
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
```

### T7 — Tests unitaires `ResponsesClient` GPT-5

**Fichier :** `backend/app/tests/unit/test_responses_client_gpt5.py`

```python
import pytest
from app.llm_orchestration.providers.responses_client import ResponsesClient


MESSAGES_STRING = [
    {"role": "system", "content": "Hard policy text."},
    {"role": "developer", "content": "Developer prompt text."},
    {"role": "user", "content": "Chart JSON here."},
]


def test_to_typed_content_blocks_converts_strings():
    """Les messages avec content string sont convertis en typed blocks."""
    result = ResponsesClient._to_typed_content_blocks(MESSAGES_STRING)
    for msg in result:
        assert isinstance(msg["content"], list)
        assert msg["content"][0]["type"] == "input_text"
        assert isinstance(msg["content"][0]["text"], str)


def test_to_typed_content_blocks_idempotent():
    """Les messages déjà en typed blocks ne sont pas re-convertis."""
    already_typed = [
        {"role": "developer", "content": [{"type": "input_text", "text": "Hello"}]}
    ]
    result = ResponsesClient._to_typed_content_blocks(already_typed)
    assert result[0]["content"] == [{"type": "input_text", "text": "Hello"}]


def test_to_typed_content_blocks_preserves_roles():
    """Le rôle et les autres champs du message sont préservés."""
    result = ResponsesClient._to_typed_content_blocks(MESSAGES_STRING)
    roles = [m["role"] for m in result]
    assert roles == ["system", "developer", "user"]


class TestResponsesClientPayload:
    """Tests sur la construction du payload params dans do_create()."""

    @pytest.mark.asyncio
    async def test_reasoning_effort_included_for_gpt5(self, mocker):
        """reasoning_effort est inclus dans params pour gpt-5."""
        client = ResponsesClient()
        mock_create = mocker.AsyncMock(return_value=mocker.Mock(
            output_text="{}",
            usage=mocker.Mock(input_tokens=10, output_tokens=10, total_tokens=20),
            model="gpt-5",
        ))
        mocker.patch.object(
            client, "_get_async_client",
            return_value=mocker.AsyncMock(
                responses=mocker.Mock(create=mock_create)
            )
        )

        await client.execute(
            messages=MESSAGES_STRING,
            model="gpt-5",
            reasoning_effort="low",
            verbosity="high",
        )

        call_kwargs = mock_create.call_args[1]
        assert call_kwargs.get("reasoning") == {"effort": "low"}
        assert call_kwargs.get("verbosity") == "high"

    @pytest.mark.asyncio
    async def test_no_reasoning_for_gpt4o(self, mocker):
        """reasoning et verbosity ne sont pas inclus pour gpt-4o-mini."""
        client = ResponsesClient()
        mock_create = mocker.AsyncMock(return_value=mocker.Mock(
            output_text="{}",
            usage=mocker.Mock(input_tokens=5, output_tokens=5, total_tokens=10),
            model="gpt-4o-mini",
        ))
        mocker.patch.object(
            client, "_get_async_client",
            return_value=mocker.AsyncMock(
                responses=mocker.Mock(create=mock_create)
            )
        )

        await client.execute(
            messages=MESSAGES_STRING,
            model="gpt-4o-mini",
            reasoning_effort=None,
            verbosity=None,
        )

        call_kwargs = mock_create.call_args[1]
        assert "reasoning" not in call_kwargs
        assert "verbosity" not in call_kwargs

    @pytest.mark.asyncio
    async def test_typed_content_blocks_used_for_gpt5(self, mocker):
        """Les typed content blocks sont utilisés dans input pour gpt-5."""
        client = ResponsesClient()
        mock_create = mocker.AsyncMock(return_value=mocker.Mock(
            output_text="{}",
            usage=mocker.Mock(input_tokens=5, output_tokens=5, total_tokens=10),
            model="gpt-5",
        ))
        mocker.patch.object(
            client, "_get_async_client",
            return_value=mocker.AsyncMock(
                responses=mocker.Mock(create=mock_create)
            )
        )

        await client.execute(messages=MESSAGES_STRING, model="gpt-5")

        call_kwargs = mock_create.call_args[1]
        for msg in call_kwargs["input"]:
            assert isinstance(msg["content"], list), f"Expected list for role={msg['role']}"
```

### T8 — Test d'intégration gateway → client GPT-5

**Fichier :** `backend/app/tests/integration/test_gateway_gpt5_params.py`

```python
"""
Vérifie que LLMGateway transmet correctement reasoning_effort et verbosity
au ResponsesClient quand le use case est configuré pour GPT-5.
"""

def test_gateway_reads_reasoning_effort_from_use_case_config():
    """
    Fixture : use case avec reasoning_effort="low", verbosity="high".
    Assertion : ResponsesClient.execute() est appelé avec ces valeurs.
    """

def test_gateway_does_not_pass_reasoning_for_gpt4o():
    """
    Fixture : use case sans reasoning_effort (gpt-4o-mini).
    Assertion : ResponsesClient.execute() est appelé sans reasoning_effort ni verbosity.
    """
```

---

## Ordre d'implémentation recommandé

```
T1 (migration Alembic + alembic upgrade head)
    ↓
T2 (ORM llm_prompt.py)
    ↓
T3 (Pydantic UseCaseConfig)
    ↓
T4 (gateway.py : 3 sous-tâches)
    ↓
T5 (responses_client.py : typed blocks + reasoning/verbosity)
    ↓
T7 + T8 (tests unitaires + intégration)
    ↓
T6 (seed_30_3_gpt5_prompts.py)
```

---

## Fichiers à Créer / Modifier

| Action | Fichier |
|--------|---------|
| CRÉER | `backend/migrations/versions/20260302_0030_add_reasoning_effort_verbosity_to_prompts.py` |
| MODIFIER | `backend/app/infra/db/models/llm_prompt.py` (ajouter `reasoning_effort`, `verbosity`) |
| MODIFIER | `backend/app/llm_orchestration/models.py` (`UseCaseConfig` : deux champs Optional) |
| MODIFIER | `backend/app/llm_orchestration/gateway.py` (3 points : construction config, appel client, détection reasoning) |
| MODIFIER | `backend/app/llm_orchestration/providers/responses_client.py` (signature + typed blocks + params GPT-5) |
| CRÉER | `backend/scripts/seed_30_3_gpt5_prompts.py` |
| CRÉER | `backend/app/tests/unit/test_responses_client_gpt5.py` |
| CRÉER | `backend/app/tests/integration/test_gateway_gpt5_params.py` |

---

## Critères de "Done"

- [ ] `alembic upgrade head` s'exécute sans erreur
- [ ] `alembic downgrade -1` supprime proprement les deux colonnes
- [ ] `LlmPromptVersionModel` a les attributs `reasoning_effort` et `verbosity` sans erreur SQLAlchemy
- [ ] `UseCaseConfig` accepte `reasoning_effort="low"` et `verbosity="high"` sans erreur Pydantic
- [ ] `ResponsesClient._to_typed_content_blocks()` est statique et importable
- [ ] Pour `model="gpt-5"`, le payload envoyé à l'API inclut `reasoning` et `verbosity`
- [ ] Pour `model="gpt-4o-mini"`, le payload n'inclut PAS `reasoning` ni `verbosity`
- [ ] Pour `model="gpt-5"`, `params["input"]` contient des typed content blocks (pas des strings)
- [ ] `python backend/scripts/seed_30_3_gpt5_prompts.py` s'exécute sans erreur
- [ ] Prompt lint passe pour le nouveau `NATAL_COMPLETE_PROMPT_V2`
- [ ] `LlmPromptVersionModel(use_case_key="natal_interpretation", status=PUBLISHED)` a `model="gpt-5"`, `reasoning_effort="low"`, `verbosity="high"`
- [ ] `natal_interpretation_short` reste INCHANGÉ (gpt-4o-mini, AstroResponse_v1)
- [ ] Tests unitaires `test_responses_client_gpt5.py` passent à 100%
- [ ] Aucun test existant cassé (en particulier les tests du `ResponsesClient` existants)
- [ ] L'override via env var `LLM_MODEL_OVERRIDE_NATAL_INTERPRETATION=gpt-5.2` reste fonctionnel (Story 30-1 non cassé)
