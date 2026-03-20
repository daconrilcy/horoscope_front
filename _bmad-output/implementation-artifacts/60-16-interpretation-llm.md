# Story 60.16 : Interprétation LLM des sections horoscope — textes narratifs enrichis par profil astrologue

Status: done

## Story

En tant qu'utilisateur de la page Horoscope du jour,
je veux que chaque section (synthèse, créneaux, turning points) contienne un texte narratif personnalisé généré par un LLM,
afin d'obtenir une lecture astrologique compréhensible, fluide et cohérente plutôt que des libellés statiques génériques.

## Acceptance Criteria

### AC1 — Colonne `astrologer_profile` sur le modèle User (backend)
- Ajouter `astrologer_profile: Mapped[str]` (valeur par défaut `"standard"`) au modèle ORM `UserModel` dans `backend/app/infra/db/models/user.py`
- Créer une migration Alembic `backend/migrations/versions/YYYYMMDD_XXXX_add_astrologer_profile_to_users.py` qui ajoute la colonne `astrologer_profile VARCHAR(32) DEFAULT 'standard' NOT NULL`
- Valeurs valides : `standard`, `vedique`, `humaniste`, `karmique`, `psychologique`

### AC2 — Endpoint utilisateur GET/PATCH paramètres (backend)
- Ajouter `GET /v1/users/me/settings` → retourne `{ "astrologer_profile": str }`
- Ajouter `PATCH /v1/users/me/settings` avec body `{ "astrologer_profile": str }` → valide la valeur, persiste, retourne le profil mis à jour
- Validation : valeur inconnue → 422 avec code `invalid_astrologer_profile`

### AC3 — Sélecteur "Style d'astrologue" (frontend)
- Ajouter une section "Style d'astrologue" dans `frontend/src/pages/settings/AccountSettings.tsx`
- Afficher les 5 options sous forme de boutons radio ou select avec description courte de chaque style
- Au chargement : `GET /v1/users/me/settings` pour afficher la valeur courante
- À la sauvegarde : `PATCH /v1/users/me/settings`
- Style inline CSS + variables CSS du projet (pas Tailwind)

### AC4 — Service `LLMNarrator` (backend)
- Créer `backend/app/prediction/llm_narrator.py` avec la classe `LLMNarrator`
- Utiliser le SDK **OpenAI** (`openai.AsyncOpenAI`) — **NE PAS utiliser l'Anthropic SDK** (non installé)
- Modèle : `settings.openai_model_default` (défaut `gpt-4o-mini`)
- Méthode principale : `async def narrate(snapshot, events, time_windows, common_context, astrologer_profile_key, lang) -> NarratorResult | None`
  - `common_context: PromptCommonContext` — fourni par `CommonContextBuilder.build()` (Story 59.5) ; contient natal_interpretation/natal_data, persona global, date du jour
  - `astrologer_profile_key: str` — style par utilisateur (défaut `"standard"`)
- `NarratorResult` (dataclass) : `daily_synthesis: str`, `astro_events_intro: str`, `time_window_narratives: dict[str, str]`, `turning_point_narratives: list[str]`
- Timeout : 10 secondes — si dépassé ou erreur OpenAI → retourner `None` (fallback silencieux)
- Construire le prompt via un module séparé `backend/app/prediction/astrologer_prompt_builder.py`

### AC5 — Module `AstrologerPromptBuilder` (backend)
- Créer `backend/app/prediction/astrologer_prompt_builder.py` avec la classe `AstrologerPromptBuilder`
- Méthode `build(common_context, time_windows, events, astrologer_profile_key, lang) -> str`
  - `common_context: PromptCommonContext` — **socle fourni par `CommonContextBuilder.build()`** (Story 59.5), qui contient déjà :
    - `natal_interpretation` (texte d'interprétation existant) ou `natal_data` (thème natal brut)
    - `astrologer_profile` (persona global configuré par admin via `PersonaConfigService`)
    - `today_date` (date formatée en français)
    - `precision_level` (heure/lieu manquant)
  - `astrologer_profile_key: str` — clé du style **par utilisateur** (`standard`/`vedique`/`humaniste`/`karmique`/`psychologique`), complémentaire du persona global
- Le prompt inclut :
  - Profil natal : utiliser `common_context.natal_interpretation` s'il existe, sinon formater `common_context.natal_data` (Soleil, Lune, Ascendant, planètes lentes — voir Dev Notes)
  - Date du jour : `common_context.today_date`
  - Événements astrologiques du jour (ingresses, sky aspects, aspects transit-natal, progressions, nœuds, étoiles fixes, retours)
  - Les 4 créneaux avec leur régime et leurs `astro_events`
  - Les turning points détectés (heure, domaine, type de changement)
  - Instruction de style selon `astrologer_profile_key` (voir section Dev Notes)
- System prompt : ton selon `common_context.astrologer_profile["tonality"]`, langue fr/en selon `lang`, max 800 tokens total
- Format de sortie demandé : JSON strict avec clés `daily_synthesis`, `astro_events_intro`, `time_window_narratives` (objet avec clés nuit/matin/apres_midi/soiree), `turning_point_narratives` (liste de strings)

### AC6 — Feature flag et intégration pipeline (backend)
- Ajouter `llm_narrator_enabled: bool` à `Settings.__init__()` via `self._parse_bool_env("LLM_NARRATOR_ENABLED", default=False)`
- Appeler `LLMNarrator.narrate()` depuis `PublicProjection.build()` (ou depuis `DailyPredictionService`) **après** l'assemblage complet du DTO
- Si `settings.llm_narrator_enabled` est `False` → ne pas appeler LLMNarrator (retour immédiat sans narratives)
- Si résultat non-None → enrichir les champs narratifs du DTO final
- L'appel est asynchrone — si le endpoint `/v1/predictions/daily` est synchrone, utiliser `asyncio.run()` ou un wrapper avec `concurrent.futures`

### AC7 — Mise à jour DTO backend
- Dans `DailyPredictionResponse` (fichier `backend/app/api/v1/routers/predictions.py`) ajouter :
  - `daily_synthesis: str | None = None`
  - `astro_events_intro: str | None = None`
  - `has_llm_narrative: bool = False`
- Dans `DailyPredictionTimeWindow` ajouter :
  - `narrative: str | None = None`
- Dans `DailyPredictionTurningPointPublic` ajouter (si ce modèle existe dans predictions.py) :
  - `narrative: str | None = None`
- Passer `astrologer_profile` (récupéré depuis la DB) à `PublicProjection.build()` ou au service de narration

### AC8 — Mise à jour types TypeScript
- Dans `frontend/src/types/dailyPrediction.ts` ajouter sur `DailyPredictionResponse` :
  - `daily_synthesis?: string`
  - `astro_events_intro?: string`
  - `has_llm_narrative?: boolean`
- Sur `DailyPredictionTimeWindow` : `narrative?: string`
- Créer ou enrichir `frontend/src/types/user.ts` avec `UserSettings { astrologer_profile: string }`

### AC9 — Intégration frontend
- Dans `DailyHoroscopePage.tsx` : afficher `prediction.daily_synthesis` en texte introductif sous `DayClimateHero` si présent (conditionnel sur `has_llm_narrative`)
- Dans `DayTimelineSectionV4.tsx` : afficher `window.narrative` si présent en remplacement de `window.label` (ou en complément — italique, couleur `var(--text-2)`)
- Dans `AstroDailyEvents.tsx` : afficher `prediction.astro_events_intro` comme sous-titre si présent
- Dans `TurningPointCard.tsx` : afficher `turning_point.narrative` si présent
- Tous ces affichages sont conditionnels : si le champ est null/undefined → affichage actuel inchangé

### AC10 — Tests
- Tests unitaires `TestLLMNarrator` avec mock OpenAI : `backend/tests/unit/prediction/test_llm_narrator.py`
  - Test que `narrate()` retourne None si timeout
  - Test que `narrate()` retourne None si erreur OpenAI
  - Test que `narrate()` parse correctement le JSON de réponse
- Tests unitaires `TestAstrologerPromptBuilder` : `backend/tests/unit/prediction/test_astrologer_prompt_builder.py`
  - Test que le prompt contient les éléments natals (Soleil, Lune, Ascendant) quand `natal_chart` est fourni
  - Test que le prompt contient "non disponible" quand `natal_chart=None`
  - Test que le style varie selon `astrologer_profile`
- Test que `has_llm_narrative=False` quand `settings.llm_narrator_enabled=False`

## Tasks / Subtasks

- [x] T1 — Migration Alembic + modèle User (AC: 1)
  - [x] T1.1 — Ajouter `astrologer_profile: Mapped[str]` avec `mapped_column(String(32), default="standard")` dans `UserModel`
  - [x] T1.2 — Créer `backend/migrations/versions/20260320_0050_add_astrologer_profile_to_users.py` avec `op.add_column("users", sa.Column("astrologer_profile", sa.String(32), nullable=False, server_default="standard"))`

- [x] T2 — Endpoints utilisateur (AC: 2)
  - [x] T2.1 — Ajouter `GET /v1/users/me/settings` dans `backend/app/api/v1/routers/users.py`
  - [x] T2.2 — Ajouter `PATCH /v1/users/me/settings` avec validation et persistance

- [x] T3 — Sélecteur frontend (AC: 3)
  - [x] T3.1 — Ajouter section "Style d'astrologue" dans `AccountSettings.tsx`
  - [x] T3.2 — Ajouter hook `useUserSettings` ou calls directs via fetch/axios dans le composant
  - [x] T3.3 — Ajouter traductions dans `frontend/src/i18n/settings.ts` (ou équivalent)

- [x] T4 — AstrologerPromptBuilder (AC: 5)
  - [x] T4.1 — Créer `backend/app/prediction/astrologer_prompt_builder.py`
  - [x] T4.2 — Implémenter les 5 styles de prompt (standard, védique, humaniste, karmique, psychologique)
  - [x] T4.3 — Intégrer `PromptCommonContext` comme source du profil natal et de la date (via `common_context.natal_interpretation` ou `common_context.natal_data`)
  - [x] T4.4 — Formatter les événements, les créneaux et turning points

- [x] T5 — LLMNarrator (AC: 4)
  - [x] T5.1 — Créer `backend/app/prediction/llm_narrator.py` avec `LLMNarrator` + `NarratorResult`
  - [x] T5.2 — Appel `openai.AsyncOpenAI` avec timeout 10s et fallback `None`
  - [x] T5.3 — Parser le JSON de réponse avec gestion d'erreur

- [x] T6 — Feature flag + intégration pipeline (AC: 6)
  - [x] T6.1 — Ajouter `llm_narrator_enabled` dans `Settings` (`backend/app/core/config.py`)
  - [x] T6.2 — Appeler `LLMNarrator` depuis `PublicProjection.build()` après assemblage
  - [x] T6.3 — Appeler `CommonContextBuilder.build()` dans le router et passer le résultat au service/projection
  - [x] T6.4 — Récupérer `astrologer_profile_key` depuis `UserModel.astrologer_profile` et le passer en complément

- [x] T7 — DTO backend + types TypeScript (AC: 7, 8)
  - [x] T7.1 — Étendre `DailyPredictionResponse`, `DailyPredictionTimeWindow`, `DailyPredictionTurningPointPublic`
  - [x] T7.2 — Mettre à jour `frontend/src/types/dailyPrediction.ts`
  - [x] T7.3 — Créer/étendre `frontend/src/types/user.ts`

- [x] T8 — Intégration frontend (AC: 9)
  - [x] T8.1 — `DailyHoroscopePage.tsx` : afficher `daily_synthesis`
  - [x] T8.2 — `DayTimelineSectionV4.tsx` : afficher `window.narrative`
  - [x] T8.3 — `AstroDailyEvents.tsx` : afficher `astro_events_intro`
  - [x] T8.4 — `TurningPointCard.tsx` : afficher `narrative`

- [x] T9 — Tests (AC: 10)
  - [x] T9.1 — `test_llm_narrator.py` avec mock OpenAI
  - [x] T9.2 — `test_astrologer_prompt_builder.py`
  - [x] T9.3 — Test feature flag désactivé

- [x] T10 — Vérification finale
  - [x] T10.1 — `ruff check backend/` passe
  - [x] T10.2 — `pytest backend/` passe
  - [x] T10.3 — Avec `LLM_NARRATOR_ENABLED=false` → comportement actuel inchangé (zéro régression)
  - [x] T10.4 — Avec `LLM_NARRATOR_ENABLED=true` et clé OpenAI valide → narratives affichées

## Dev Notes

### ⚠️ CRITIQUE : Provider LLM = OpenAI, PAS Anthropic

Le projet utilise exclusivement **OpenAI** via `openai>=2.0.0` dans `pyproject.toml`.
Le SDK `anthropic` n'est **pas installé** et **ne doit pas être ajouté**.

```python
# ✅ CORRECT
import openai
client = openai.AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = await client.chat.completions.create(
    model=settings.openai_model_default,  # "gpt-4o-mini"
    messages=[...],
    response_format={"type": "json_object"},
    timeout=10.0,
)

# ❌ FAUX - ne pas utiliser
import anthropic
```

### Migration Alembic — Pattern du projet

```python
# Fichier : backend/migrations/versions/20260320_0050_add_astrologer_profile_to_users.py
"""add astrologer_profile to users"""
from alembic import op
import sqlalchemy as sa

revision = "20260320_0050"
down_revision = "a63994cb990f"  # dernière migration connue
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("astrologer_profile", sa.String(32), nullable=False, server_default="standard"),
    )

def downgrade() -> None:
    op.drop_column("users", "astrologer_profile")
```

**IMPORTANT :** Vérifier le `down_revision` réel en exécutant `alembic heads` ou en lisant la dernière migration. Le dernier fichier observé est `a63994cb990f_add_granularity_to_user_baselines.py`.

### Modèle User — pattern SQLAlchemy

```python
# backend/app/infra/db/models/user.py
class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(16), index=True)
    astrologer_profile: Mapped[str] = mapped_column(String(32), default="standard")  # NOUVEAU
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
```

### Endpoint utilisateur — pattern du projet

Le router `users.py` utilise le pattern `AuthenticatedUser = Depends(require_authenticated_user)`. Voir `GET /v1/users/me/birth-data` pour le pattern exact. Ajouter dans le même fichier :

```python
VALID_ASTROLOGER_PROFILES = {"standard", "vedique", "humaniste", "karmique", "psychologique"}

class UserSettingsResponse(BaseModel):
    astrologer_profile: str

class UserSettingsPatchRequest(BaseModel):
    astrologer_profile: str

@router.get("/me/settings", response_model=UserSettingsResponse)
def get_me_settings(current_user: AuthenticatedUser = Depends(require_authenticated_user), db: Session = Depends(get_db_session)):
    user = db.get(UserModel, current_user.id)
    return {"astrologer_profile": getattr(user, "astrologer_profile", "standard")}

@router.patch("/me/settings", response_model=UserSettingsResponse)
def patch_me_settings(payload: UserSettingsPatchRequest, current_user: ..., db: ...):
    if payload.astrologer_profile not in VALID_ASTROLOGER_PROFILES:
        return JSONResponse(status_code=422, content={"error": {"code": "invalid_astrologer_profile", ...}})
    user = db.get(UserModel, current_user.id)
    user.astrologer_profile = payload.astrologer_profile
    db.commit()
    return {"astrologer_profile": user.astrologer_profile}
```

### Feature Flag — pattern du projet

```python
# backend/app/core/config.py — dans __init__
self.llm_narrator_enabled = self._parse_bool_env("LLM_NARRATOR_ENABLED", default=False)
```

Variable d'environnement : `LLM_NARRATOR_ENABLED=true` pour activer.

### LLMNarrator — implémentation

```python
# backend/app/prediction/llm_narrator.py
from __future__ import annotations
import asyncio, json, logging
from dataclasses import dataclass
from typing import Any
import openai
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class NarratorResult:
    daily_synthesis: str
    astro_events_intro: str
    time_window_narratives: dict[str, str]   # {"nuit": ..., "matin": ..., "apres_midi": ..., "soiree": ...}
    turning_point_narratives: list[str]      # une entrée par TP

class LLMNarrator:
    TIMEOUT_SECONDS = 10.0

    async def narrate(
        self,
        snapshot: Any,
        events: list[Any],
        time_windows: list[dict],
        common_context: Any,              # PromptCommonContext (natal, date, persona global)
        astrologer_profile_key: str = "standard",  # style par utilisateur
        lang: str = "fr",
    ) -> NarratorResult | None:
        from app.prediction.astrologer_prompt_builder import AstrologerPromptBuilder
        try:
            prompt = AstrologerPromptBuilder().build(
                snapshot=snapshot,
                events=events,
                time_windows=time_windows,
                common_context=common_context,
                astrologer_profile_key=astrologer_profile_key,
                lang=lang,
            )
            client = openai.AsyncOpenAI()  # utilise OPENAI_API_KEY de l'env
            response = await asyncio.wait_for(
                client.chat.completions.create(
                    model=settings.openai_model_default,
                    messages=[
                        {"role": "system", "content": self._system_prompt(lang)},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    max_tokens=600,
                ),
                timeout=self.TIMEOUT_SECONDS,
            )
            raw = response.choices[0].message.content or ""
            data = json.loads(raw)
            return NarratorResult(
                daily_synthesis=data.get("daily_synthesis", ""),
                astro_events_intro=data.get("astro_events_intro", ""),
                time_window_narratives=data.get("time_window_narratives", {}),
                turning_point_narratives=data.get("turning_point_narratives", []),
            )
        except Exception as e:
            logger.warning("llm_narrator.failed error=%s", str(e))
            return None

    def _system_prompt(self, lang: str) -> str:
        lang_instruction = "Réponds en français." if lang == "fr" else "Answer in English."
        return (
            "Tu es un astrologue expert, bienveillant et précis. "
            f"{lang_instruction} "
            "Génère uniquement du JSON valide avec les clés : "
            "daily_synthesis (string), astro_events_intro (string), "
            "time_window_narratives (objet avec clés nuit/matin/apres_midi/soiree), "
            "turning_point_narratives (liste de strings). "
            "Sois concis : 1-2 phrases par champ. Pas de markdown."
        )
```

### AstrologerPromptBuilder — styles de prompt

```python
# backend/app/prediction/astrologer_prompt_builder.py
STYLE_INSTRUCTIONS = {
    "standard": "Utilise le vocabulaire astrologique occidental classique, ton positif et accessible.",
    "vedique":  "Utilise des références védiques : nakshatra, maisons védiques, dharma, karma.",
    "humaniste": "Adopte l'approche humaniste : archétypes jungiens, croissance personnelle, symbolisme.",
    "karmique":  "Insiste sur les leçons de vie, les nœuds lunaires, les cycles karmiques.",
    "psychologique": "Utilise un vocabulaire psychologique moderne : patterns, intégration, comportements.",
}
```

### Intégration dans PublicProjection.build()

`PublicProjection.build()` est dans `backend/app/prediction/public_projection.py`. Il est appelé de façon synchrone. Pour l'appel async, utiliser :

```python
import asyncio

if settings.llm_narrator_enabled:
    try:
        narrator_result = asyncio.run(
            LLMNarrator().narrate(
                snapshot=snapshot,
                events=events,
                time_windows=time_windows,
                common_context=common_context,           # PromptCommonContext via CommonContextBuilder
                astrologer_profile_key=astrologer_profile_key,  # style par utilisateur
                lang=lang,
            )
        )
    except Exception:
        narrator_result = None
```

**Attention** : si le contexte d'exécution a déjà une boucle asyncio active (ex: FastAPI async endpoint), `asyncio.run()` lèvera une exception. Dans ce cas, utiliser `asyncio.get_event_loop().run_until_complete()` ou exécuter dans un `ThreadPoolExecutor`. Vérifier si `/v1/predictions/daily` est `def` ou `async def` — si `def` → `asyncio.run()` fonctionne directement.

L'`astrologer_profile` doit être récupéré depuis la DB au niveau du service ou du router et passé à `PublicProjection.build()`. Ajouter un paramètre optionnel `astrologer_profile: str = "standard"` à la méthode `build()`.

### Frontend — AccountSettings pattern

`AccountSettings.tsx` utilise :
- `useAccessTokenSnapshot()` pour le token
- `useAuthMe(token)` pour les données user
- Styles avec classes CSS existantes (`.panel`, `.account-info-grid`, etc.)
- Aucune dépendance Tailwind — utiliser inline styles ou classes CSS existantes

Pour le sélecteur astrologue :
```tsx
// Appel fetch direct — pas de React Query pour PATCH simples
const [profile, setProfile] = useState("standard")
const [saving, setSaving] = useState(false)

const save = async (value: string) => {
  setSaving(true)
  await fetch("/api/v1/users/me/settings", {
    method: "PATCH",
    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
    body: JSON.stringify({ astrologer_profile: value }),
  })
  setProfile(value)
  setSaving(false)
}
```

Descriptions des styles pour l'UI (fr) :
- `standard` : "Astrologie occidentale classique, ton accessible"
- `vedique` : "Tradition védique, nakshatra, karma"
- `humaniste` : "Archétypes jungiens, croissance personnelle"
- `karmique` : "Leçons de vie, nœuds lunaires, cycles"
- `psychologique` : "Patterns comportementaux, intégration"

### Socle `CommonContextBuilder` — source unique des données natales et de la date

⚠️ **Ne pas re-fetcher le thème natal manuellement.** Le module `backend/app/prompts/common_context.py` (Story 59.5) fait déjà tout :

```python
from app.prompts.common_context import CommonContextBuilder

# Dans le router predictions.py (a accès à db et current_user.id)
common_context = CommonContextBuilder.build(
    user_id=current_user.id,
    use_case_key="daily_horoscope",  # nouvelle entrée à ajouter au PROMPT_CATALOG
    period="daily",
    db=db,
)
```

`PromptCommonContext` contient :
- `natal_interpretation: str | None` — texte d'interprétation pré-généré si disponible (priorité haute)
- `natal_data: dict | None` — thème natal brut (`NatalResult.model_dump()`) en fallback
- `astrologer_profile: dict` — persona global (`{"name", "style", "tonality", "limits", "description"}`) via `PersonaConfigService`
- `today_date: str` — ex: `"vendredi 20 mars 2026"`
- `precision_level: str` — `"précision complète"` ou dégradée

**Si `natal_data` est fourni** (fallback brut), les clés utiles pour le prompt :
- `natal_data["planet_positions"]` → liste de `{planet_code, sign_code, house_number, is_retrograde}`
  - Codes planètes : `"SO"` Soleil, `"LU"` Lune, `"ME"` Mercure, `"VE"` Vénus, `"MA"` Mars, `"JU"` Jupiter, `"SA"` Saturne
- `natal_data["houses"]` → liste de `{number, cusp_longitude}` — Ascendant = maison 1
  - Pour le signe de l'Ascendant : `sign_from_longitude(houses[0]["cusp_longitude"])` (fonction dans `natal_calculation.py`)

**Profil utilisateur `astrologer_profile_key`** (védique/humaniste/etc.) — distinct du persona global :
- Récupéré séparément depuis `UserModel.astrologer_profile` (colonne ajoutée par AC1)
- Passé à `AstrologerPromptBuilder` comme paramètre complémentaire

### Récupération dans le pipeline de prédiction

Dans `backend/app/api/v1/routers/predictions.py` :
```python
from app.prompts.common_context import CommonContextBuilder

# 1. Socle commun (natal, date, persona global)
common_context = CommonContextBuilder.build(
    user_id=current_user.id, use_case_key="daily_horoscope", period="daily", db=db
)

# 2. Style par utilisateur
user_model = db.get(UserModel, current_user.id)
astrologer_profile_key = getattr(user_model, "astrologer_profile", "standard")

# 3. Passer au service/projection
```

### TurningPointCard — structure actuelle

Vérifier dans `frontend/src/components/TurningPointCard.tsx` comment le composant affiche les données actuelles, puis ajouter `narrative` de façon conditionnelle. Le type TypeScript `DailyPredictionTurningPointPublic` est dans `frontend/src/types/dailyPrediction.ts`.

### Project Structure Notes

- Migration dans `backend/migrations/versions/` (pas `backend/alembic/versions/`)
- Pattern de nommage migrations : `YYYYMMDD_XXXX_description.py`
- UserModel dans `backend/app/infra/db/models/user.py` (pas de sous-module `auth`)
- Router users dans `backend/app/api/v1/routers/users.py`
- Settings frontend dans `frontend/src/pages/settings/AccountSettings.tsx` (pas de ProfilePage)
- Composants prédiction dans `frontend/src/components/prediction/` et `frontend/src/components/`
- Page principale dans `frontend/src/pages/DailyHoroscopePage.tsx`

### Ordre de passage des tests

```bash
# Tests unitaires ciblés
pytest backend/tests/unit/prediction/test_llm_narrator.py -v
pytest backend/tests/unit/prediction/test_astrologer_prompt_builder.py -v

# Régression prédiction
pytest backend/tests/ -k "daily_prediction or time_window or public_projection" -v

# Lint
cd backend && ruff check app/
```

### References

- `backend/app/infra/db/models/user.py` — UserModel actuel (id, email, password_hash, role, created_at, updated_at)
- `backend/app/core/config.py:Settings.__init__()` — pattern `_parse_bool_env`
- `backend/app/api/v1/routers/users.py` — router utilisateur existant (GET /me/birth-data comme référence pattern)
- `backend/app/prediction/public_projection.py:PublicProjection.build()` — point d'intégration narrateur
- `backend/app/prediction/public_projection.py:PublicTimeWindowPolicy.build()` — génère time_windows avec astro_events
- `backend/app/api/v1/routers/predictions.py:DailyPredictionResponse` — DTO à enrichir
- `frontend/src/pages/DailyHoroscopePage.tsx` — page principale V4
- `frontend/src/pages/settings/AccountSettings.tsx` — page paramètres utilisateur
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx` — affichage créneaux
- `frontend/src/components/AstroDailyEvents.tsx` — affichage événements astro
- `frontend/src/types/dailyPrediction.ts` — types TypeScript à enrichir
- `backend/migrations/versions/20260218_0003_add_users_table.py` — référence migration users

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `backend/app/infra/db/models/user.py`
- `backend/migrations/versions/20260320_0050_add_astrologer_profile_to_users.py`
- `backend/app/api/v1/routers/users.py`
- `backend/app/api/v1/routers/predictions.py`
- `backend/app/prediction/astrologer_prompt_builder.py`
- `backend/app/prediction/llm_narrator.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/core/config.py`
- `backend/tests/unit/prediction/test_llm_narrator.py`
- `backend/tests/unit/prediction/test_astrologer_prompt_builder.py`
- `frontend/src/types/user.ts`
- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/pages/settings/AccountSettings.tsx`
- `frontend/src/i18n/settings.ts`
- `frontend/src/components/DayClimateHero.tsx`
- `frontend/src/components/AstroDailyEvents.tsx`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/TurningPointCard.tsx`
- `frontend/src/pages/DailyHoroscopePage.tsx`

- `backend/app/infra/db/models/user.py`
- `backend/migrations/versions/20260320_0050_add_astrologer_profile_to_users.py`
- `backend/app/api/v1/routers/users.py`
- `backend/app/prediction/astrologer_prompt_builder.py`
- `backend/app/prediction/llm_narrator.py`
- `backend/app/core/config.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/api/v1/routers/predictions.py`
- `frontend/src/types/dailyPrediction.ts`
- `frontend/src/types/user.ts`
- `frontend/src/pages/settings/AccountSettings.tsx`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/AstroDailyEvents.tsx`
- `frontend/src/pages/DailyHoroscopePage.tsx`
- `backend/tests/unit/prediction/test_llm_narrator.py`
- `backend/tests/unit/prediction/test_astrologer_prompt_builder.py`
