# Runbook QA LLM Interne

## Objectif

Ce document décrit la recette backend post-70.15 pour :

- créer ou converger l utilisateur canonique `cyril-test@test.com` ;
- vérifier les flux `guidance`, `chat`, `natal` et `horoscope_daily` ;
- prouver que le chemin exécuté reste le pipeline canonique.

## Pré-requis d environnement

- backend lancé depuis le venv Python ;
- variables d environnement explicites :
  - `LLM_QA_ROUTES_ENABLED=true`
  - `LLM_QA_SEED_USER_ENABLED=true` si le seed doit aussi s exécuter au démarrage
- en production, ces deux capacités restent désactivées par défaut ;
  - les routes QA ne sont pas montées tant que `LLM_QA_ROUTES_ALLOW_PRODUCTION=true` n est pas posé explicitement ;
  - le seed canonique est refusé tant que `LLM_QA_SEED_USER_ALLOW_PRODUCTION=true` n est pas posé explicitement.

## Démarrage local

Depuis `c:\dev\horoscope_front` :

```powershell
.\.venv\Scripts\Activate.ps1
Set-Location backend
$env:LLM_QA_ROUTES_ENABLED = "true"
$env:LLM_QA_SEED_USER_ENABLED = "true"
python -m uvicorn app.main:app --reload
```

## Seed canonique

L utilisateur convergé est :

- email : `cyril-test@test.com`
- mot de passe : `admin123`
- date : `1973-04-24`
- heure : `11:00`
- lieu : `Paris, France`

Le seed :

- crée ou remet en conformité le user ;
- résout `Paris, France` via `GeocodingService.search_with_cache()` puis `GeoPlaceResolvedRepository.find_or_create()` ;
- dérive la timezone depuis les coordonnées ;
- met à jour le profil via `UserBirthProfileService.upsert_for_user()` ;
- ne régénère le thème natal que si le `input_hash` attendu ne correspond pas déjà au dernier chart persisté.

Appel HTTP :

```powershell
$login = Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/v1/auth/login `
  -ContentType "application/json" `
  -Body '{"email":"admin@test.com","password":"admin123"}'

$token = $login.data.tokens.access_token

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/v1/internal/llm/qa/seed-user `
  -Headers @{ Authorization = "Bearer $token" }
```

## Recette QA

Toutes les routes suivantes ciblent par défaut `cyril-test@test.com`. Le champ `target_email` permet de viser explicitement un autre utilisateur existant.

### Guidance

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/v1/internal/llm/qa/guidance `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"period":"daily"}'
```

### Chat

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/v1/internal/llm/qa/chat `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"message":"Donne-moi une lecture synthétique du jour."}'
```

### Natal

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/v1/internal/llm/qa/natal `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{"use_case_level":"complete","locale":"fr"}'
```

### Horoscope daily

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/v1/internal/llm/qa/horoscope-daily `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body '{}'
```

## Ce qui prouve le pipeline canonique

- `guidance` passe par `GuidanceService -> AIEngineAdapter.generate_guidance() -> LLMGateway`
- `chat` passe par `ChatGuidanceService -> AIEngineAdapter.generate_chat_reply() -> LLMGateway`
- `natal` passe par `NatalInterpretationServiceV2 -> AIEngineAdapter.generate_natal_interpretation() -> LLMGateway`
- `horoscope_daily` passe par `DailyPredictionService` et `PublicPredictionAssembler`, puis la narration LLM nominale si activée

Les réponses QA retournent la sortie normalisée utile à la recette runtime. Aucun endpoint QA ne doit exposer des secrets provider ni de télémétrie brute excessive.
