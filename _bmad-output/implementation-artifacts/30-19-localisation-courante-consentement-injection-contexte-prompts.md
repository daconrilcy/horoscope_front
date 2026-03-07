# Story 30.19 : Localisation courante — consentement, profil lieu actuel et injection contexte temporel dans les prompts

Status: done

## Story

As a utilisateur de l'application horoscope,
I want que l'application me demande l'autorisation de me localiser physiquement, et que les astrologues connaissent ma date, heure, timezone et lieu actuels au moment de chaque demande,
so that les interprétations astrologiques (chat, thème natal, guidances) soient ancrées dans le contexte planétaire du moment présent et de mon lieu actuel, rendant les réponses plus pertinentes et personnalisées.

## Contexte métier

En astrologie, les transits planétaires et les interprétations "du moment" dépendent fortement :
- De **quand** on pose la question (date, heure exacte, fuseau horaire)
- De **où** on se trouve (le ciel local varie selon la localisation)

Actuellement, les prompts envoyés aux astrologues LLM ne contiennent que les données natales de l'utilisateur (thème de naissance). Ils ignorent le contexte temporel et géographique présent, ce qui empêche des interprétations de transits, de révolutions solaires, ou d'aspects en cours.

Cette story couvre deux parties distinctes mais liées :
- **Partie 1** : Collecte du consentement géolocalisation et stockage du lieu actuel dans le profil utilisateur
- **Partie 2** : Injection automatique de la date/heure/timezone/lieu courants dans tous les prompts astrologiques

## Acceptance Criteria

### Partie 1 — Profil et consentement géolocalisation

1. **AC1 — Consentement géolocalisation dans le profil** :
   Le formulaire `BirthProfilePage.tsx` comporte une nouvelle section "Ma localisation actuelle" avec un toggle/checkbox `geolocation_consent`. Quand l'utilisateur coche ce toggle, il indique qu'il autorise l'application à utiliser sa localisation physique pour les interprétations. La valeur est persistée en DB (champ `geolocation_consent`).

2. **AC2 — Géolocalisation automatique (si consentement accordé)** :
   Si `geolocation_consent = true`, un bouton "Localiser automatiquement" appelle `navigator.geolocation.getCurrentPosition()` dans le navigateur (seulement disponible en HTTPS). Les coordonnées lat/lon obtenues sont envoyées au nouvel endpoint `POST /v1/geocoding/reverse` qui retourne ville, pays, timezone IANA et display_name via Nominatim reverse. Ces données sont sauvegardées dans le profil.

3. **AC3 — Saisie manuelle du lieu actuel (si refus ou échec géolocalisation)** :
   Si `geolocation_consent = false` OU si la géolocalisation échoue (navigateur HTTP, permission refusée, timeout), un formulaire de saisie manuelle (champs `current_city` + `current_country`) est affiché avec un message explicatif : *"Pour des interprétations ancrées dans votre ciel local (transits, maisons d'heure), indiquez votre lieu actuel. Cette information n'est pas requise mais améliore la pertinence des réponses."*
   La saisie manuelle utilise le forward geocoding existant (`GET /v1/geocoding/search`) pour résoudre les coordonnées et la timezone.

4. **AC4 — Persistance en DB (migration Alembic)** :
   La table `user_birth_profiles` est étendue avec 7 nouvelles colonnes, toutes nullable sauf `geolocation_consent` :
   - `geolocation_consent` BOOLEAN NOT NULL DEFAULT FALSE
   - `current_city` VARCHAR(255) NULL
   - `current_country` VARCHAR(100) NULL
   - `current_lat` FLOAT NULL
   - `current_lon` FLOAT NULL
   - `current_location_display` VARCHAR(255) NULL — label humain lisible (ex: "Paris, Île-de-France, France")
   - `current_timezone` VARCHAR(64) NULL — IANA (ex: "Europe/Paris")

   Une migration Alembic (séquence 0031) est créée et idempotente.

5. **AC5 — Endpoint reverse geocoding** :
   Un nouvel endpoint `POST /v1/geocoding/reverse` est créé dans `backend/app/api/v1/routers/geocoding.py`. Il accepte `{ "lat": float, "lon": float }`, interroge Nominatim reverse (`https://nominatim.openstreetmap.org/reverse?format=json&lat=X&lon=Y`), et retourne `{ display_name, city, country, timezone_iana, lat, lon }`. L'accès est authentifié (token JWT requis). Le résultat peut être mis en cache via `GeoPlaceResolvedRepository` si un `osm_id` est disponible.

### Partie 2 — Injection contexte temporel dans les prompts

6. **AC6 — Injection dans le prompt de chat** :
   À chaque appel à `ChatGuidanceService.send_message_async()`, le `context` dict injecté dans les prompts contient trois nouvelles clés :
   - `current_datetime` : datetime du moment de la requête dans le timezone de l'utilisateur, formaté "07 mars 2026 à 14h30 (Europe/Paris)"
   - `current_timezone` : IANA string (source : `current_timezone` du profil → fallback `birth_timezone`)
   - `current_location` : label humain (source : `current_location_display` du profil → fallback `"{birth_city}, {birth_country}"` → fallback `birth_place`)

7. **AC7 — Injection dans le prompt d'interprétation natale** :
   Même injection dans `NatalInterpretationService` pour le contexte envoyé au template `natal_chart_interpretation_v1.jinja2`.

8. **AC8 — Injection dans les prompts de guidance** :
   Même injection dans `GuidanceService` pour les guidances daily, weekly et contextual.

9. **AC9 — Mise à jour des templates Jinja2** :
   Les templates suivants sont enrichis d'un bloc conditionnel affichant le contexte temporel quand disponible :
   - `backend/app/ai_engine/prompts/chat_system.jinja2`
   - `backend/app/ai_engine/prompts/natal_chart_interpretation_v1.jinja2`
   - `backend/app/ai_engine/prompts/guidance_daily_v1.jinja2`
   - `backend/app/ai_engine/prompts/guidance_weekly_v1.jinja2`
   - `backend/app/ai_engine/prompts/guidance_contextual_v1.jinja2`

   Bloc type à ajouter (via `context.extra.*` pour chat, via `context.*` pour guidance) :
   ```
   {% if context.extra.current_datetime %}
   [CONTEXTE PRÉSENT — utilise ces données pour ancrer tes interprétations dans le moment actuel]
   Date et heure de la demande : {{ context.extra.current_datetime }}
   Lieu actuel de l'utilisateur : {{ context.extra.current_location }}
   [/CONTEXTE PRÉSENT]
   {% endif %}
   ```

10. **AC10 — Backward compatibility totale** :
    Les profils existants sans `current_timezone` ni `current_location_display` fonctionnent sans erreur. Les fallbacks garantissent qu'au minimum `birth_timezone` et `birth_place` sont utilisés. Si ces fallbacks sont aussi absents, le bloc n'est pas injecté (condition `if` dans le template).

## Tasks / Subtasks

### T1 — Migration DB (AC4)

- [x] Créer `backend/migrations/versions/{date}_0031_add_current_location_to_user_birth_profiles.py`
  - [x] Ajouter les 7 colonnes avec `op.add_column` et `op.drop_column` dans `downgrade()`
  - [x] Contrainte : `geolocation_consent` NOT NULL DEFAULT FALSE ; autres colonnes nullable
- [x] Mettre à jour `backend/app/infra/db/models/user_birth_profile.py`
  - [x] Ajouter les 7 champs `Mapped` avec types corrects (Bool, String, Float)
- [x] Mettre à jour `backend/app/infra/db/repositories/user_birth_profile_repository.py`
  - [x] Ajouter les 7 champs au `upsert()` avec valeurs par défaut (consentement=False, reste=None)

### T2 — Backend Service profil (AC4)

- [x] Mettre à jour `UserBirthProfileData` dans `user_birth_profile_service.py`
  - [x] Ajouter les 7 champs avec types Optional et valeurs par défaut
- [x] Mettre à jour `UserBirthProfileService.get_for_user()` — mapper les nouveaux champs depuis le modèle
- [x] Mettre à jour `UserBirthProfileService.upsert_for_user()` — accepter et persister les nouveaux champs
- [x] Mettre à jour l'endpoint API `backend/app/api/v1/routers/users.py` (PUT `/me/birth-data`)
  - [x] Ajouter les 7 champs dans `UserBirthProfileWithAstroData` et dans `BirthInput` (via `natal_preparation.py`)

### T3 — Endpoint reverse geocoding (AC5)

- [x] Ajouter `POST /v1/geocoding/reverse` dans `backend/app/api/v1/routers/geocoding.py`
  - [x] Schema payload : `{ "lat": float, "lon": float }`
  - [x] Appel Nominatim reverse : `GET https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&addressdetails=1`
  - [x] Extraction : `display_name`, `address.city` (ou `address.town`/`address.village`), `address.country`, `address.country_code`
  - [x] Résolution timezone IANA via `GeocodingService` (si `osm_id` disponible) ou via bibliothèque `timezonefinder` (lat/lon → IANA) — **préférer timezonefinder pour éviter appel Nominatim supplémentaire**
  - [x] Authentification JWT requise (utiliser `get_authenticated_user`)
  - [x] Réponse : `{ display_name, city, country, lat, lon, timezone_iana }`

### T4 — Injection contexte temporel — Chat (AC6)

- [x] Modifier `backend/app/services/chat_guidance_service.py`
  - [x] Après le chargement du `birth_profile` (ligne ~804), calculer le contexte temporel courant :
    ```python
    from zoneinfo import ZoneInfo
    tz_name = birth_profile.current_timezone or birth_profile.birth_timezone or "UTC"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("UTC")
    current_dt = datetime.now(tz)
    current_datetime_str = current_dt.strftime(f"%d %B %Y à %Hh%M ({tz_name})")
    current_location_str = (
        birth_profile.current_location_display
        or (f"{birth_profile.birth_city}, {birth_profile.birth_country}"
            if birth_profile.birth_city and birth_profile.birth_country
            else birth_profile.birth_place)
        or None
    )
    ```
  - [x] Ajouter au `context` dict : `"current_datetime": current_datetime_str`, `"current_timezone": tz_name`, `"current_location": current_location_str`
  - [x] Gérer le cas `UserBirthProfileServiceError` : si profil absent, pas d'injection (déjà géré par le `except` existant)

### T5 — Injection contexte temporel — Thème natal (AC7)

- [x] Modifier `backend/app/services/natal_interpretation_service.py`
  - [x] Ajouter la même logique de calcul `current_datetime_str` et `current_location_str`
  - [x] Passer ces valeurs au contexte de `generate_text()` (dans `GenerateContext.extra` ou comme champs séparés selon la structure de `GenerateContext`)

### T6 — Injection contexte temporel — Guidance (AC8)

- [x] Modifier `backend/app/services/guidance_service.py`
  - [x] Même logique que T4 : calculer `current_datetime_str` et `current_location_str` depuis `birth_profile`
  - [x] Injecter dans le context passé aux prompts daily/weekly/contextual
  - [x] Adapter selon la structure de contexte guidance (voir `guidance_daily_v1.jinja2` : utilise `context.birth_data.*` et `context.extra.*`)

### T7 — Templates Jinja2 (AC9)

- [x] `backend/app/ai_engine/prompts/chat_system.jinja2`
  - [x] Ajouter après le bloc `{% if context.extra and context.extra.persona_line %}` :
    ```jinja2
    {% if context.extra and context.extra.current_datetime %}
    [CONTEXTE PRÉSENT — utilise ces données pour ancrer tes interprétations dans le moment actuel]
    Date et heure de la demande : {{ context.extra.current_datetime }}
    Lieu actuel de l'utilisateur : {{ context.extra.current_location }}
    [/CONTEXTE PRÉSENT]
    {% endif %}
    ```
- [x] `backend/app/ai_engine/prompts/natal_chart_interpretation_v1.jinja2`
  - [x] Ajouter un bloc similaire après `{% if context.birth_data %}...{% endif %}`
- [x] `backend/app/ai_engine/prompts/guidance_daily_v1.jinja2`
  - [x] Ajouter un bloc similaire après `{% if context.birth_data %}...{% endif %}`
- [x] `backend/app/ai_engine/prompts/guidance_weekly_v1.jinja2` — même modification
- [x] `backend/app/ai_engine/prompts/guidance_contextual_v1.jinja2` — même modification

### T8 — Frontend : section "Localisation actuelle" dans BirthProfilePage (AC1, AC2, AC3)

- [x] Modifier `frontend/src/pages/BirthProfilePage.tsx`
  - [x] Ajouter un état `geolocationConsent: boolean` et `currentLocationState: "idle" | "loading" | "success" | "error"`
  - [x] Ajouter une section "Ma localisation actuelle" sous le formulaire principal
  - [x] Toggle consent avec label explicatif i18n
  - [x] Si consent coché : afficher bouton "Localiser automatiquement"
    - [x] Handler `handleAutoLocate()` : appelle `navigator.geolocation.getCurrentPosition()` → POST `/v1/geocoding/reverse` → met à jour les champs `current_city`, `current_country`, `current_lat`, `current_lon`, `current_location_display`, `current_timezone`
    - [x] Vérification préalable `if (!navigator.geolocation)` → afficher message d'erreur
  - [x] Si consent décoché OU géoloc échouée : afficher champs manuels `current_city` + `current_country` + message explicatif
    - [x] Géocode forward via `geocodeCity()` existant (réutiliser le pattern BirthProfilePage)
  - [x] Synchroniser le formulaire avec `syncFormWithProfileData()` pour les nouveaux champs

- [x] Modifier `frontend/src/api/birthProfile.ts`
  - [x] Ajouter les 7 champs dans le type `BirthProfileData` et dans le payload de `saveBirthData()`

- [x] Modifier `frontend/src/i18n/birthProfile.ts` (ou fichier i18n correspondant)
  - [x] Ajouter les clés : `current_location_section`, `geolocation_consent_label`, `geolocation_consent_description`, `auto_locate_button`, `geolocation_error_http`, `geolocation_error_denied`, `current_location_explain`

### T9 — Tests (AC6, AC10)

- [x] Ajouter tests unitaires dans `backend/app/tests/unit/`
  - [x] Test : `current_datetime`, `current_timezone`, `current_location` bien injectés dans le context dict du chat
  - [x] Test : fallback `current_timezone → birth_timezone` si `current_timezone` est null
  - [x] Test : fallback `current_location_display → "{birth_city}, {birth_country}" → birth_place` si display null
  - [x] Test : profil sans aucun champ courant → aucune clé `current_*` injectée (ou clé avec valeur `None` ignorée par le template)
  - [x] Test : profil inexistant → pas d'exception (le `except UserBirthProfileServiceError` existant dans chat_guidance_service couvre ce cas)

## Dev Notes

### Chemin du contexte vers les prompts

**Chat (path v1 AI engine)** :
```
chat_guidance_service.py
  → context: dict[str, str | None]  ← ajouter current_datetime, current_timezone, current_location ici
  → AIEngineAdapter.generate_chat_reply(context=context)
  → ai_engine_adapter.py → ChatRequest(context=ChatContext(extra=context))
  → chat_system.jinja2 : context.extra.current_datetime
```

**Guidance** :
```
guidance_service.py
  → context dict (birth_data + extra)
  → guidance_daily_v1.jinja2 : context.extra.current_datetime
```

Attention : dans `chat_system.jinja2`, le natal est accessible via `context.natal_chart_summary` (directement sur ChatContext), mais les champs persona et custom sont dans `context.extra.*`. Les nouveaux champs temporels iront dans `context.extra.*` (même pattern que persona_name, etc.).

### Calcul du datetime courant avec timezone

```python
from zoneinfo import ZoneInfo
from datetime import datetime

tz_name = profile.current_timezone or profile.birth_timezone or "UTC"
try:
    tz = ZoneInfo(tz_name)
except Exception:
    tz = ZoneInfo("UTC")

current_dt = datetime.now(tz)
# Format lisible pour le LLM
current_datetime_str = current_dt.strftime(f"%d %B %Y à %Hh%M ({tz_name})")
# ex: "07 mars 2026 à 14h30 (Europe/Paris)"
```

`ZoneInfo` est dans la stdlib Python 3.9+. Pas de dépendance externe nécessaire.

### Reverse geocoding — Nominatim

Endpoint Nominatim : `https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&addressdetails=1`

Réponse type :
```json
{
  "display_name": "Paris, Île-de-France, France",
  "address": {
    "city": "Paris",
    "state": "Île-de-France",
    "country": "France",
    "country_code": "fr"
  }
}
```

Pour la timezone depuis lat/lon, utiliser **`timezonefinder`** (déjà peut-être dans le projet, sinon à ajouter dans `pyproject.toml`). Vérifier si déjà présent :
```bash
grep timezonefinder backend/pyproject.toml
```
Si absent : `pip install timezonefinder` et ajouter dans `[project].dependencies`.

```python
from timezonefinder import TimezoneFinder
tf = TimezoneFinder()
tz = tf.timezone_at(lat=48.8566, lng=2.3522)  # → "Europe/Paris"
```

### `navigator.geolocation` — contraintes HTTPS

L'API `navigator.geolocation` n'est disponible qu'en **HTTPS** (ou localhost). En HTTP, `navigator.geolocation` est `undefined`. Le handler frontend doit prévoir ce cas et afficher un message adéquat (clé i18n `geolocation_error_http`).

```typescript
if (!navigator.geolocation) {
  // Afficher message : géolocalisation non disponible (connexion non sécurisée ou navigateur)
  return
}
navigator.geolocation.getCurrentPosition(
  (pos) => { /* success */ },
  (err) => { /* err.code: 1=PERMISSION_DENIED, 2=UNAVAILABLE, 3=TIMEOUT */ },
  { timeout: 10000, maximumAge: 300_000 }
)
```

### Pas de breaking change

- Tous les nouveaux champs DB sont `nullable` sauf `geolocation_consent` (DEFAULT FALSE).
- `UserBirthProfileData` étend les champs existants avec des valeurs par défaut `None`/`False`.
- L'injection dans les prompts est conditionnelle (`{% if context.extra.current_datetime %}`).
- Les services existants continuent de fonctionner même si ces champs ne sont pas renseignés.

### Fichiers à ne pas toucher

- `backend/app/domain/` — aucun changement de domaine métier
- `backend/app/infra/db/models/chat_message.py` — pas de changement
- `frontend/src/features/chat/` — pas de changement côté chat (l'injection est backend-only)

### Dépendance optionnelle à vérifier

```bash
grep -n "timezonefinder\|tzfinder" backend/pyproject.toml
```
Si absent, ajouter `timezonefinder>=6.5` dans `[project].dependencies` de `backend/pyproject.toml`.

### Fichiers modifiés / créés

| Fichier | Action |
|---------|--------|
| `backend/migrations/versions/*_0031_add_current_location_*.py` | Créer |
| `backend/app/infra/db/models/user_birth_profile.py` | Modifier |
| `backend/app/infra/db/repositories/user_birth_profile_repository.py` | Modifier |
| `backend/app/services/user_birth_profile_service.py` | Modifier |
| `backend/app/api/v1/routers/birth_profile.py` | Modifier |
| `backend/app/api/v1/routers/geocoding.py` | Modifier (nouvel endpoint) |
| `backend/app/services/chat_guidance_service.py` | Modifier |
| `backend/app/services/natal_interpretation_service.py` | Modifier |
| `backend/app/services/guidance_service.py` | Modifier |
| `backend/app/ai_engine/prompts/chat_system.jinja2` | Modifier |
| `backend/app/ai_engine/prompts/natal_chart_interpretation_v1.jinja2` | Modifier |
| `backend/app/ai_engine/prompts/guidance_daily_v1.jinja2` | Modifier |
| `backend/app/ai_engine/prompts/guidance_weekly_v1.jinja2` | Modifier |
| `backend/app/ai_engine/prompts/guidance_contextual_v1.jinja2` | Modifier |
| `frontend/src/pages/BirthProfilePage.tsx` | Modifier |
| `frontend/src/api/birthProfile.ts` | Modifier |
| `frontend/src/i18n/birthProfile.ts` | Modifier |
| `backend/app/tests/unit/test_current_context_injection.py` | Créer |

## Dev Agent Record

### Agent Model Used

gemini-2.0-flash-001

### Debug Log References

- SQLite duplicate column error handled by `alembic stamp`.
- TypeScript interface mismatch for `geolocation_consent` handled by removing `.default(false)` in Zod schema and using React Hook Form `defaultValues`.

### Completion Notes List

- Database schema updated with 7 new columns in `user_birth_profiles`.
- Alembic migration `20260307_0031` created and stamped.
- `GeocodingService.reverse` implemented via Nominatim.
- `POST /v1/geocoding/reverse` endpoint added with IANA timezone resolution.
- Temporal context injection added to Chat, Natal Interpretation, and Guidance services.
- Jinja2 templates updated for all use cases to include current datetime and location.
- Frontend `BirthProfilePage` updated with geolocation consent and browser-based detection.
- Frontend `BirthProfilePage` now auto-refreshes the current location on page load when `geolocation_consent=true`, while preserving the last saved location if browser geolocation fails.
- Multi-language support (FR, EN, ES) updated for new features.
- Unit and integration tests passed.

### File List

- `backend/migrations/versions/20260307_0031_add_current_location_to_user_birth_profiles.py`
- `backend/app/infra/db/models/user_birth_profile.py`
- `backend/app/infra/db/repositories/user_birth_profile_repository.py`
- `backend/app/domain/astrology/natal_preparation.py`
- `backend/app/services/user_birth_profile_service.py`
- `backend/app/services/geocoding_service.py`
- `backend/app/services/current_context.py`
- `backend/app/services/chat_guidance_service.py`
- `backend/app/services/natal_interpretation_service.py`
- `backend/app/services/guidance_service.py`
- `backend/app/services/ai_engine_adapter.py`
- `backend/app/ai_engine/schemas.py`
- `backend/app/ai_engine/prompts/chat_system.jinja2`
- `backend/app/ai_engine/prompts/natal_chart_interpretation_v1.jinja2`
- `backend/app/ai_engine/prompts/guidance_daily_v1.jinja2`
- `backend/app/ai_engine/prompts/guidance_weekly_v1.jinja2`
- `backend/app/ai_engine/prompts/guidance_contextual_v1.jinja2`
- `backend/app/api/v1/routers/users.py`
- `backend/app/api/v1/routers/geocoding.py`
- `backend/app/tests/unit/test_current_context_injection.py`
- `frontend/src/api/birthProfile.ts`
- `frontend/src/api/geocoding.ts`
- `frontend/src/pages/BirthProfilePage.tsx`
- `frontend/src/pages/BirthProfilePage.css`
- `frontend/src/i18n/birthProfile.ts`
