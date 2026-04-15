# Procédure Pas à Pas Avant Mise En Prod

Ce document est conçu pour un opérateur qui ne connaît pas l'application. Suivre les étapes dans l'ordre exact.

## 1. Préparer l'environnement

Ouvrir PowerShell à la racine du dépôt :

```powershell
cd C:\dev\horoscope_front
.\.venv\Scripts\Activate.ps1
```

Vérifier que le backend cible répond et que l'URL API est connue :

- local : `http://localhost:8000`
- préprod/prod : URL fournie par l'équipe plateforme

## 2. Construire ou vérifier le snapshot candidat

```powershell
python backend\scripts\build_llm_release_candidate.py --version release-candidate-YYYYMMDD-HHMMSS
Get-Content artifacts\llm-release-candidate.json
```

À noter :

- `candidate_snapshot.id`
- `candidate_snapshot.version`
- `candidate_snapshot.default_manifest_entry_id`

## 3. Vérifier la conformité doc ↔ code

```powershell
python backend\scripts\check_doc_conformity.py --json
Get-Content artifacts\llm-doc-conformity.json
```

Condition de passage :

- `status = ok`

## 4. Activer la blocklist legacy attendue

```powershell
$env:LLM_LEGACY_PROGRESSIVE_BLOCKLIST = "fb.use_case_first,fb.resolve_model"
python backend\scripts\legacy_residual_report.py
```

Condition de passage :

- le rapport ne doit pas indiquer de blocklist vide

## 5. Générer la qualification corrélée

```powershell
python backend\scripts\build_llm_qualification_evidence.py `
  --candidate artifacts\llm-release-candidate.json `
  --manifest-entry-id natal:interpretation:premium:fr-FR `
  --iterations 3 `
  --output artifacts\llm-qualification-evidence-premium.json
```

Vérifier :

```powershell
Get-Content artifacts\llm-qualification-evidence-premium.json
```

Condition de passage :

- `verdict = go` ou `go-with-constraints`

## 6. Générer la golden corrélée

```powershell
python backend\scripts\build_llm_golden_evidence.py `
  --candidate artifacts\llm-release-candidate.json `
  --manifest-entry-id natal:interpretation:premium:fr-FR `
  --output artifacts\llm-golden-evidence-premium.json
```

Vérifier :

```powershell
Get-Content artifacts\llm-golden-evidence-premium.json
```

Condition de passage :

- `verdict = pass`

## 7. Générer le smoke corrélé

```powershell
python backend\scripts\build_llm_smoke_evidence.py `
  --candidate artifacts\llm-release-candidate.json `
  --manifest-entry-id natal:interpretation:premium:fr-FR `
  --environment preprod `
  --output artifacts\llm-smoke-evidence-premium.json
```

## 8. Vérifier le chaos report

```powershell
$env:CHAOS_REPORT_PATH = "artifacts/chaos/story-66-43-chaos-report.json"
pytest -q backend\tests\integration\test_story_66_43_provider_runtime_chaos.py
```

Condition de passage :

- `all_passed = true`

## 9. Activer en préprod

```powershell
.\scripts\activate-llm-release.ps1 `
  -ApiBaseUrl "http://localhost:8000" `
  -CandidatePath artifacts\llm-release-candidate.json `
  -QualificationPath artifacts\llm-qualification-evidence-premium.json `
  -GoldenPath artifacts\llm-golden-evidence-premium.json `
  -SmokePath artifacts\llm-smoke-evidence-premium.json
```

Condition de passage :

- le script termine sans erreur
- le fichier `artifacts\llm-activation-response.json` est créé

Vérifier :

```powershell
Get-Content artifacts\llm-activation-response.json
```

Attendu :

- `status = active`

## 10. Contrôler l'état post-activation

Vérifier les dashboards ou endpoints de monitoring :

- snapshot actif
- provider demandé / résolu / exécuté
- `fallback_kind`
- `attempt_count`
- `provider_error_code`
- `breaker_state`
- `release_health`

## 11. Décider la production

Autoriser la production seulement si :

- qualification corrélée acceptable ;
- golden corrélée `pass` ;
- smoke corrélé présent ;
- activation préprod réussie ;
- point de latence accepté si `go-with-constraints`.

## 12. Rollback si nécessaire

En cas d'incident :

```powershell
Invoke-WebRequest `
  -Uri "http://localhost:8000/v1/admin/llm/releases/rollback" `
  -Method Post `
  -ContentType "application/json" `
  -Body "{}"
```

Puis vérifier :

- le snapshot précédent est redevenu actif ;
- les métriques redeviennent cohérentes ;
- les discriminants d'observabilité reflètent le rollback.

## 13. Ce qu'il ne faut pas faire

- ne jamais activer un snapshot sans qualification et golden corrélées ;
- ne jamais laisser `<preprod-url>` ou tout autre placeholder dans une commande PowerShell ;
- ne jamais pousser en prod sur un autre `manifest_entry_id` que celui qualifié ;
- ne jamais interpréter un artefact local ancien sans regarder son `generated_at`.

