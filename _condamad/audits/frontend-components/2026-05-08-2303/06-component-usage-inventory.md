<!-- Inventaire reproductible des usages runtime des composants frontend. -->

# Component Usage Inventory - frontend-components

## Purpose

This artifact supports `F-005`. It records a reproducible static inventory for component files under `frontend/src/components/**`, excluding tests and each component's own file.

The inventory is conservative. It is meant to identify files requiring classification before deletion, not to authorize automatic removal.

## Command

Run from repository root:

```powershell
$componentFiles = Get-ChildItem -Recurse -File -LiteralPath 'frontend\src\components' -Include *.tsx | Where-Object { $_.Name -notlike '*.test.tsx' }
$rows = foreach ($file in $componentFiles) {
  $repo = (Get-Location).Path
  $rel = $file.FullName.Replace($repo + '\', '').Replace('\','/')
  $srcRel = $rel.Replace('frontend/src/','')
  $source = Get-Content -Raw -LiteralPath $file.FullName
  $symbols = @()
  $symbols += [regex]::Matches($source, 'export\s+function\s+([A-Za-z0-9_]+)') | ForEach-Object { $_.Groups[1].Value }
  $symbols += [regex]::Matches($source, 'export\s+(?:const|class)\s+([A-Za-z0-9_]+)') | ForEach-Object { $_.Groups[1].Value }
  if ($source -match 'export\s+default') { $symbols += [IO.Path]::GetFileNameWithoutExtension($file.Name) }
  $symbols = @($symbols | Sort-Object -Unique)
  if ($symbols.Count -eq 0) { $symbols = @([IO.Path]::GetFileNameWithoutExtension($file.Name)) }
  $pathStem = $srcRel -replace '\.tsx$',''
  $pathHits = @(rg -n --fixed-strings $pathStem frontend/src -g '*.ts' -g '*.tsx' -g '!**/*.test.ts' -g '!**/*.test.tsx' 2>$null | Where-Object { (($_ -split ':',2)[0].Replace('\','/')) -ne $rel })
  $symbolHits = @()
  foreach ($symbol in $symbols) {
    $symbolHits += @(rg -n --fixed-strings $symbol frontend/src -g '*.ts' -g '*.tsx' -g '!**/*.test.ts' -g '!**/*.test.tsx' 2>$null | Where-Object { (($_ -split ':',2)[0].Replace('\','/')) -ne $rel })
  }
  $external = @($pathHits + $symbolHits | Sort-Object -Unique)
  $barrelOnly = $external.Count -gt 0 -and (@($external | Where-Object { (($_ -split ':',2)[0].Replace('\','/')) -notmatch '/index\.ts$' }).Count -eq 0)
  if ($external.Count -eq 0 -or $barrelOnly) {
    [PSCustomObject]@{
      Path = $rel
      Exports = ($symbols -join ', ')
      Classification = $(if ($external.Count -eq 0) { 'no-runtime-reference' } else { 'barrel-only' })
      Evidence = ($external -join ' || ')
    }
  }
}
$rows | Sort-Object Classification, Path | Format-Table -AutoSize
```

## Result

| Path | Exports | Classification | Evidence |
|---|---|---|---|
| `frontend/src/components/ui/Form/FormField.tsx` | `FormField` | `barrel-only` | `frontend/src/components/ui/Form/index.ts:2:export * from './FormField';` |
| `frontend/src/components/B2BAstrologyPanel.tsx` | `B2BAstrologyPanel` | `no-runtime-reference` | none |
| `frontend/src/components/B2BBillingPanel.tsx` | `B2BBillingPanel` | `no-runtime-reference` | none |
| `frontend/src/components/B2BEditorialPanel.tsx` | `B2BEditorialPanel` | `no-runtime-reference` | none |
| `frontend/src/components/B2BUsagePanel.tsx` | `B2BUsagePanel` | `no-runtime-reference` | none |
| `frontend/src/components/DailyInsightsSection.tsx` | `DailyInsightsSection`, `DailyInsightsSectionPresenter` | `no-runtime-reference` | none |
| `frontend/src/components/HeroHoroscopeCard.tsx` | `HeroHoroscopeCard` | `no-runtime-reference` | none |
| `frontend/src/components/OpsMonitoringPanel.tsx` | `OpsMonitoringPanel` | `no-runtime-reference` | none |
| `frontend/src/components/OpsPersonaPanel.tsx` | `OpsPersonaPanel` | `no-runtime-reference` | none |
| `frontend/src/components/prediction/CategoryGrid.tsx` | `CategoryGrid` | `no-runtime-reference` | none |
| `frontend/src/components/prediction/DayPredictionCardContainer.tsx` | `DayPredictionCardContainer` | `no-runtime-reference` | none |
| `frontend/src/components/prediction/DecisionWindowsSection.tsx` | `DecisionWindowsSection` | `no-runtime-reference` | none |
| `frontend/src/components/prediction/TurningPointsList.tsx` | `TurningPointsList` | `no-runtime-reference` | none |
| `frontend/src/components/PrivacyPanel.tsx` | `PrivacyPanel` | `no-runtime-reference` | none |
| `frontend/src/components/TodayHeader.tsx` | `TodayHeader` | `no-runtime-reference` | none |

## Export-Aware Manual Notes

`frontend/src/components/icons/DashboardIcons.tsx` exports named symbols rather than a `DashboardIcons` component. The basename scan flagged the file as barrel-only, but the export-aware review must check named exports:

- `StarIcon`
- `ChatIcon`
- `CrystalBallIcon`
- `UserIcon`
- `SettingsIcon`

Current static scan found the exported symbols only in `DashboardIcons.tsx`, `components/icons/index.ts`, and a name collision in `pages/AdminPage.tsx` where `SettingsIcon` is a local function, not an import from `DashboardIcons.tsx`. This file is therefore a `manual-review-required` candidate for `SC-004`, not an automatic removal candidate.

## Limitations

- This is a static text inventory, not a TypeScript import graph.
- Same-name local declarations can create false positives and must be resolved before deletion.
- Dynamic imports and generated code are not detected by this scan.

