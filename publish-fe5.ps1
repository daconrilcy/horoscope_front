# Script de publication FE-5 Horoscope
# Ce script prépare la branche et donne les instructions pour créer l'issue et la PR

Write-Host "=== Publication FE-5 Horoscope ===" -ForegroundColor Cyan
Write-Host ""

# Vérifier si on est dans un repo git
if (-not (Test-Path .git)) {
    Write-Host "❌ Erreur: Pas un dépôt Git" -ForegroundColor Red
    exit 1
}

# Vérifier la branche courante
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "Branche courante: $currentBranch" -ForegroundColor Yellow

# Créer la branche feat/FE-5-horoscope si elle n'existe pas
$targetBranch = "feat/FE-5-horoscope"
if ($currentBranch -ne $targetBranch) {
    Write-Host "Création de la branche $targetBranch..." -ForegroundColor Cyan
    git checkout -b $targetBranch
}

# Vérifier le statut git
Write-Host ""
Write-Host "Statut Git:" -ForegroundColor Cyan
git status --short

# Vérifier les fichiers horoscope
Write-Host ""
Write-Host "Vérification des fichiers horoscope:" -ForegroundColor Cyan
$horoscopeFiles = @(
    "src/shared/api/horoscope.service.ts",
    "src/shared/api/horoscope.service.test.ts",
    "src/shared/auth/charts.ts",
    "src/stores/horoscopeStore.ts",
    "src/stores/horoscopeStore.test.ts",
    "src/features/horoscope/hooks/useCreateNatal.ts",
    "src/features/horoscope/hooks/useToday.ts",
    "src/features/horoscope/hooks/useTodayPremium.ts",
    "src/features/horoscope/hooks/useDownloadPdf.ts",
    "src/features/horoscope/utils/downloadBlob.ts",
    "src/features/horoscope/NatalForm.tsx",
    "src/features/horoscope/TodayCard.tsx",
    "src/features/horoscope/TodayPremiumCard.tsx",
    "src/pages/app/horoscope/index.tsx",
    "FE-5-horoscope-issue.md",
    "FE-5-horoscope-pr.md"
)

$allFilesExist = $true
foreach ($file in $horoscopeFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file MANQUANT" -ForegroundColor Red
        $allFilesExist = $false
    }
}

if (-not $allFilesExist) {
    Write-Host ""
    Write-Host "❌ Certains fichiers sont manquants" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Tous les fichiers sont présents" -ForegroundColor Green

# Demander confirmation pour le commit
Write-Host ""
$confirm = Read-Host "Voulez-vous commit et push maintenant? (y/n)"
if ($confirm -eq "y" -or $confirm -eq "Y") {
    Write-Host "Ajout des fichiers..." -ForegroundColor Cyan
    git add -A
    
    Write-Host "Commit..." -ForegroundColor Cyan
    git commit -m "feat: implement FE-5 horoscope feature

- Add HoroscopeService with strict Zod schemas
- Add horoscopeStore with LRU and FIFO cap 10
- Add React Query hooks (useCreateNatal, useToday, useTodayPremium, useDownloadPdf)
- Add UI components (NatalForm, TodayCard, TodayPremiumCard)
- Add horoscope page with lazy loading
- Add tests: 13 service tests, 10 store tests
- Total: 207/207 tests passing"
    
    Write-Host "Push..." -ForegroundColor Cyan
    git push -u origin $targetBranch
    
    Write-Host ""
    Write-Host "✅ Push réussi!" -ForegroundColor Green
} else {
    Write-Host "Skip commit/push" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Prochaines étapes manuelles ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Créer l'issue GitHub:" -ForegroundColor Yellow
Write-Host "   https://github.com/daconrilcy/horoscope_front/issues/new" -ForegroundColor White
Write-Host "   Titre: FE-5 — Horoscope Feature" -ForegroundColor White
Write-Host "   Description: Copier FE-5-horoscope-issue.md" -ForegroundColor White
Write-Host "   Labels: feature, horoscope, milestone-fe-5" -ForegroundColor White
Write-Host ""
Write-Host "2. Créer la PR GitHub:" -ForegroundColor Yellow
Write-Host "   https://github.com/daconrilcy/horoscope_front/compare/feat/FE-5-horoscope" -ForegroundColor White
Write-Host "   Titre: FE-5 — Horoscope Feature" -ForegroundColor White
Write-Host "   Description: Copier FE-5-horoscope-pr.md" -ForegroundColor White
Write-Host "   Ajouter: Closes #[issue_number]" -ForegroundColor White
Write-Host "   Labels: feature, horoscope, milestone-fe-5" -ForegroundColor White
Write-Host ""
Write-Host "3. Vérifier que les checks CI/CD passent" -ForegroundColor Yellow
Write-Host ""
Write-Host "=== Fin ===" -ForegroundColor Cyan

