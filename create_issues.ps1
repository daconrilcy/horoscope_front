# Script pour créer les issues GitHub à partir des fichiers markdown
$issuesDir = "issues\0_5_1"
$files = @("FE-13.md", "FE-14.md", "FE-15.md", "FE-16.md", "FE-17.md", "FE-18.md", "FE-19.md", "FE-20.md")

foreach ($file in $files) {
    $filePath = Join-Path $issuesDir $file
    $content = Get-Content $filePath -Raw
    
    # Extraire le titre depuis le frontmatter
    if ($content -match 'title:\s*(.+?)\n') {
        $title = $matches[1].Trim()
    }
    
    # Extraire les labels depuis le frontmatter
    $labels = @()
    if ($content -match 'labels:\s*(.+?)\n') {
        $labelsStr = $matches[1].Trim()
        $labels = $labelsStr -split '\s*,\s*'
    }
    
    # Extraire le body (tout après le frontmatter)
    $bodyStart = $content.IndexOf("---`n`n", 0)
    if ($bodyStart -eq -1) {
        $bodyStart = $content.IndexOf("---", 0)
        if ($bodyStart -ne -1) {
            $bodyStart = $content.IndexOf("---", $bodyStart + 3)
            if ($bodyStart -ne -1) {
                $bodyStart += 3
            }
        }
    } else {
        $bodyStart += 5
    }
    
    if ($bodyStart -eq -1) {
        $bodyStart = 0
    }
    
    # Chercher le début réel du body (après le deuxième ---)
    $lines = Get-Content $filePath
    $bodyLines = @()
    $skipFrontmatter = $false
    $foundSecondDash = $false
    
    foreach ($line in $lines) {
        if ($line -eq "---") {
            if (-not $skipFrontmatter) {
                $skipFrontmatter = $true
            } elseif (-not $foundSecondDash) {
                $foundSecondDash = $true
                continue
            }
        }
        if ($foundSecondDash) {
            $bodyLines += $line
        }
    }
    
    $body = $bodyLines -join "`n"
    
    # Créer un fichier temporaire pour le body
    $tempBodyFile = Join-Path $issuesDir "$($file.Replace('.md', '-body.md'))"
    $body | Out-File -FilePath $tempBodyFile -Encoding utf8 -NoNewline
    
    Write-Host "Création de l'issue: $title"
    
    # Créer l'issue avec gh
    if ($labels.Count -gt 0) {
        $labelStr = $labels -join ","
        $result = gh issue create --title $title --label $labelStr --body-file $tempBodyFile 2>&1
    } else {
        $result = gh issue create --title $title --body-file $tempBodyFile 2>&1
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Issue créée avec succès: $title" -ForegroundColor Green
    } else {
        Write-Host "✗ Erreur lors de la création de l'issue: $title" -ForegroundColor Red
        Write-Host $result
    }
    
    # Nettoyer le fichier temporaire
    Remove-Item $tempBodyFile -ErrorAction SilentlyContinue
}

Write-Host "`nTerminé!"



