# Script pour créer toutes les issues GitHub
$issuesDir = "issues\0_5_1"
$files = @(
    @{file="FE-13.md"; title="FE-13 — Billing config awareness & dev debug panel"},
    @{file="FE-14.md"; title="FE-14 — Checkout form: AB + trial + coupons + tax address/ids"},
    @{file="FE-15.md"; title="FE-15 — Billing success/cancel hardening with session correlation"},
    @{file="FE-16.md"; title="FE-16 — Portal session with whitelist UX & fallback"},
    @{file="FE-17.md"; title="FE-17 — Stripe Terminal dev console (simulator flow)"},
    @{file="FE-18.md"; title="FE-18 — Admin dev: clear price_lookup cache"},
    @{file="FE-19.md"; title="FE-19 — Billing front observability correlation (request_id breadcrumbs)"},
    @{file="FE-20.md"; title="FE-20 — Docs: billing/terminal quickstart & env"}
)

foreach ($item in $files) {
    $filePath = Join-Path $issuesDir $item.file
    $tempBodyFile = Join-Path $issuesDir "$($item.file.Replace('.md', '-body.md'))"
    
    # Extraire le body (tout après les 8 premières lignes qui contiennent le frontmatter)
    Get-Content $filePath | Select-Object -Skip 8 | Out-File -FilePath $tempBodyFile -Encoding utf8
    
    Write-Host "Création de l'issue: $($item.title)"
    
    # Créer l'issue sans labels pour l'instant (les labels n'existent pas encore)
    $result = gh issue create --title $item.title --body-file $tempBodyFile 2>&1
    
    if ($LASTEXCODE -eq 0) {
        Write-Host "✓ Issue créée avec succès: $($item.title)" -ForegroundColor Green
    } else {
        Write-Host "✗ Erreur: $($item.title)" -ForegroundColor Red
        Write-Host $result
    }
    
    # Nettoyer
    Remove-Item $tempBodyFile -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
}

Write-Host "`nTerminé!"



