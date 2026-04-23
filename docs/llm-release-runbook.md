# LLM Release Runbook

Ce document décrit la chaîne de promotion opérationnelle du runtime LLM prompt generation par snapshot corrélé.

## But

Autoriser une mise en production uniquement si le snapshot candidat est traçable, qualifié, régressé, activable et réversible.

## Cible validée

Les travaux opérés dans ce dépôt ont été menés sur le manifest cible :

- `natal:interpretation:premium:fr-FR`

Le snapshot candidat utilisé pendant la stabilisation est :

- `active_snapshot_id`: `e2e7191a-b403-42b9-911a-43c6f442420e`
- `active_snapshot_version`: `release-candidate-ready`

## Modifications opérées pour rendre la promotion exploitable

- génération d'un snapshot candidat et d'un rapport readiness agrégé ;
- génération de preuves corrélées qualification / golden / smoke ;
- wrapper d'activation corrélé ;
- correction du runtime pour exécuter les campagnes golden et qualification via le chemin canonique `execute_request()` ;
- correction de la compatibilité reasoning model pour les assemblies `gpt-5` ;
- correction du fallback `persona_name` pour les prompts assembly ;
- ajout d'une fixture golden premium alignée sur le contrat enrichi `AstroResponse_v3`.

## Pré-requis

- backend démarré sur l'environnement visé ;
- venv Python actif via `.\.venv\Scripts\Activate.ps1` ;
- credentials provider valides sur l'environnement d'exécution ;
- connectivité sortante vers le provider LLM ;
- accès aux endpoints admin et monitoring.

## Artefacts source

Les scripts suivants sont désormais la source de vérité pour construire le dossier de release :

- [build_llm_release_candidate.py](/C:/dev/horoscope_front/backend/scripts/build_llm_release_candidate.py)
- [build_llm_release_readiness_report.py](/C:/dev/horoscope_front/backend/scripts/build_llm_release_readiness_report.py)
- [build_llm_qualification_evidence.py](/C:/dev/horoscope_front/backend/scripts/build_llm_qualification_evidence.py)
- [build_llm_golden_evidence.py](/C:/dev/horoscope_front/backend/scripts/build_llm_golden_evidence.py)
- [build_llm_smoke_evidence.py](/C:/dev/horoscope_front/backend/scripts/build_llm_smoke_evidence.py)
- [activate-llm-release.ps1](/C:/dev/horoscope_front/scripts/activate-llm-release.ps1)
- [llm-release-readiness.ps1](/C:/dev/horoscope_front/scripts/llm-release-readiness.ps1)

## Artefacts produits

Le dossier de preuve standard est constitué de :

- `artifacts/llm-release-candidate.json`
- `artifacts/llm-doc-conformity.json`
- `artifacts/chaos/story-66-43-chaos-report.json`
- `artifacts/llm-qualification-evidence-premium.json`
- `artifacts/llm-golden-evidence-premium.json`
- `artifacts/llm-smoke-evidence-premium.json`
- `artifacts/llm-release-readiness-premium.json`
- `artifacts/llm-activation-response.json`

Ces fichiers sont des preuves d'environnement. Ils ne doivent pas être utilisés comme référence de configuration dans le code source.

## Commandes de construction du dossier de preuve

### 1. Snapshot candidat

```powershell
.\.venv\Scripts\Activate.ps1
python backend\scripts\build_llm_release_candidate.py --version release-candidate-YYYYMMDD-HHMMSS
```

### 2. Doc ↔ code

```powershell
.\.venv\Scripts\Activate.ps1
python backend\scripts\check_doc_conformity.py --json
```

### 3. Legacy blocklist

```powershell
$env:LLM_LEGACY_PROGRESSIVE_BLOCKLIST = "fb.use_case_first,fb.resolve_model"
.\.venv\Scripts\Activate.ps1
python backend\scripts\legacy_residual_report.py
```

### 4. Qualification corrélée

```powershell
.\.venv\Scripts\Activate.ps1
python backend\scripts\build_llm_qualification_evidence.py `
  --candidate artifacts\llm-release-candidate.json `
  --manifest-entry-id natal:interpretation:premium:fr-FR `
  --iterations 3 `
  --output artifacts\llm-qualification-evidence-premium.json
```

Acceptation :

- `active_snapshot_id` corrélé ;
- `active_snapshot_version` corrélé ;
- `manifest_entry_id` corrélé ;
- verdict `go` ou `go-with-constraints`.

### 5. Golden corrélée

```powershell
.\.venv\Scripts\Activate.ps1
python backend\scripts\build_llm_golden_evidence.py `
  --candidate artifacts\llm-release-candidate.json `
  --manifest-entry-id natal:interpretation:premium:fr-FR `
  --output artifacts\llm-golden-evidence-premium.json
```

Acceptation :

- verdict global `pass` ;
- aucune dérive structurelle blocking ;
- aucun fallback legacy interdit ;
- mêmes discriminants snapshot que la qualification.

### 6. Chaos runtime 66.43

```powershell
.\.venv\Scripts\Activate.ps1
$env:CHAOS_REPORT_PATH = "artifacts/chaos/story-66-43-chaos-report.json"
pytest -q backend\tests\integration\test_story_66_43_provider_runtime_chaos.py
```

Acceptation :

- `report_kind = provider_runtime_chaos_invariants`
- `all_passed = true`

### 7. Smoke corrélé

```powershell
.\.venv\Scripts\Activate.ps1
python backend\scripts\build_llm_smoke_evidence.py `
  --candidate artifacts\llm-release-candidate.json `
  --manifest-entry-id natal:interpretation:premium:fr-FR `
  --environment preprod `
  --output artifacts\llm-smoke-evidence-premium.json
```

### 8. Activation

```powershell
.\scripts\activate-llm-release.ps1 `
  -ApiBaseUrl "http://localhost:8000" `
  -CandidatePath artifacts\llm-release-candidate.json `
  -QualificationPath artifacts\llm-qualification-evidence-premium.json `
  -GoldenPath artifacts\llm-golden-evidence-premium.json `
  -SmokePath artifacts\llm-smoke-evidence-premium.json
```

Succès attendu :

- création de `artifacts/llm-activation-response.json`
- `status = active`

## Lecture minimale post-activation

Vérifier au minimum :

- snapshot actif ;
- `requested_provider`, `resolved_provider`, `executed_provider` ;
- `attempt_count` ;
- `provider_error_code` ;
- `breaker_state` ;
- `fallback_kind` ;
- `release_health`.

Endpoints utiles :

- `GET /v1/ops/monitoring/llm/dashboard`
- `POST /v1/admin/llm/releases/{snapshot_id}/release-health`
- `POST /v1/admin/llm/releases/rollback`

## Semantique snapshot et pointeur actif

Un `llm_release_snapshots` est un artefact versionne immuable apres creation. Les
etats `draft`, `validated`, `active` et `archived` decrivent la promotion de cet
artefact, pas une pile de pointeurs actifs.

La table `llm_active_releases` est un pointeur singleton vers le snapshot actif.
Une activation ou un rollback remplace ce pointeur unique ; elle ne cree pas une
nouvelle ligne logique a conserver comme historique. L historique de promotion
reste porte par les snapshots eux-memes (`status`, `activated_at`, `activated_by`)
et par `release_health.history` dans le manifest.

Une release `draft` ou `validated` ne doit jamais etre lue comme configuration
runtime active tant que `llm_active_releases.release_snapshot_id` ne pointe pas
dessus. Les lectures runtime et les preuves d observabilite doivent donc
correler `active_snapshot_id`, `active_snapshot_version` et `manifest_entry_id`
avec le pointeur actif courant.

## Point de vigilance connu

Le dernier run validé affiche une qualification `go-with-constraints` à cause d'une latence `p95` supérieure au seuil SLO. Ce point ne bloque pas mécaniquement l'activation mais doit être assumé explicitement avant production.

## Décision formelle

La promotion n'est autorisée que si cette phrase est vraie :

> Nous activons le snapshot X, validé par qualification Y, golden Z, chaos report W, avec seuils de release health S et procédure de rollback R.
