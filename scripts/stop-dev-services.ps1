#!/usr/bin/env pwsh
<#
.SYNOPSIS
Arrete les services locaux de developpement du projet.

.DESCRIPTION
Tue en une commande les processus backend, frontend et Stripe CLI lances pour
ce depot. La detection cible les commandes connues du projet et leurs enfants
afin d'eviter d'arreter des processus generiques comme VS Code, Adobe ou un
autre service Node/Python sans lien avec la stack locale.

.PARAMETER Ports
Ports locaux a inspecter en plus des lignes de commande. Un processus trouve
par port n'est arrete que s'il ressemble a un serveur backend, frontend ou
Stripe CLI.

.PARAMETER Help
Affiche l'aide du script sans arreter de processus.

.EXAMPLE
.\scripts\stop-dev-services.ps1

.EXAMPLE
.\scripts\stop-dev-services.ps1 -WhatIf
#>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
  [int[]] $Ports = @(8001, 5173, 5174, 4173, 4174),
  [switch] $Help
)

$ErrorActionPreference = "Stop"

if ($Help) {
  Get-Help -Detailed $PSCommandPath
  return
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backendPath = Join-Path $repoRoot "backend"
$frontendPath = Join-Path $repoRoot "frontend"
$currentProcessId = $PID

function ConvertTo-RegexLiteral {
  <#
  .SYNOPSIS
  Prepare un chemin Windows pour les comparaisons par expression reguliere.
  #>
  param(
    [Parameter(Mandatory = $true)]
    [string] $Value
  )

  return [regex]::Escape($Value)
}

function Get-ProjectProcesses {
  <#
  .SYNOPSIS
  Recupere les processus backend, frontend et Stripe CLI detectes localement.
  #>
  $backendPattern = ConvertTo-RegexLiteral -Value $backendPath
  $frontendPattern = ConvertTo-RegexLiteral -Value $frontendPath

  return @(
    Get-CimInstance Win32_Process |
      Where-Object {
        $_.ProcessId -ne $currentProcessId -and
        $_.CommandLine -and
        (
          (
            $_.CommandLine -match $backendPattern -and
            $_.CommandLine -match "(?i)\b(python|uvicorn|fastapi|pytest)\b"
          ) -or
          (
            $_.CommandLine -match "(?i)\buvicorn\b" -and
            $_.CommandLine -match "(?i)\bapp\.main:app\b"
          ) -or
          (
            $_.CommandLine -match $frontendPattern -and
            $_.CommandLine -match "(?i)\b(node|npm|pnpm|yarn|vite|esbuild)\b"
          ) -or
          (
            $_.CommandLine -match "(?i)\bstripe(\.exe)?\b" -and
            $_.CommandLine -match "(?i)\blisten\b"
          )
        )
      }
  )
}

function Get-PortOwnerProcesses {
  <#
  .SYNOPSIS
  Ajoute les proprietaires des ports de dev quand leur commande est connue.
  #>
  param(
    [Parameter(Mandatory = $true)]
    [int[]] $LocalPorts
  )

  $ownerIds = @(
    Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
      Where-Object { $_.LocalPort -in $LocalPorts } |
      Select-Object -ExpandProperty OwningProcess -Unique
  )

  if (-not $ownerIds) {
    return @()
  }

  return @(
    foreach ($ownerId in $ownerIds) {
      Get-CimInstance Win32_Process -Filter "ProcessId = $ownerId" -ErrorAction SilentlyContinue |
        Where-Object {
          $_.CommandLine -and
          (
            $_.CommandLine -match "(?i)\b(uvicorn|fastapi|vite|esbuild|pnpm|npm|yarn)\b" -or
            ($_.CommandLine -match "(?i)\bstripe(\.exe)?\b" -and $_.CommandLine -match "(?i)\blisten\b")
          )
        }
    }
  )
}

function Get-DescendantProcesses {
  <#
  .SYNOPSIS
  Recupere recursivement les enfants des processus detectes.
  #>
  param(
    [Parameter(Mandatory = $true)]
    [object[]] $RootProcesses
  )

  $allProcesses = @(Get-CimInstance Win32_Process)
  $knownById = @{}
  foreach ($process in $RootProcesses) {
    $knownById[[int] $process.ProcessId] = $process
  }

  $queue = [System.Collections.Queue]::new()
  foreach ($process in $RootProcesses) {
    $queue.Enqueue([int] $process.ProcessId)
  }

  while ($queue.Count -gt 0) {
    $parentId = $queue.Dequeue()
    foreach ($child in @($allProcesses | Where-Object { $_.ParentProcessId -eq $parentId })) {
      if (-not $knownById.ContainsKey([int] $child.ProcessId)) {
        $knownById[[int] $child.ProcessId] = $child
        $queue.Enqueue([int] $child.ProcessId)
      }
    }
  }

  return @($knownById.Values)
}

$rootMatches = @(Get-ProjectProcesses) + @(Get-PortOwnerProcesses -LocalPorts $Ports)
$uniqueRoots = @(
  $rootMatches |
    Where-Object { $null -ne $_ } |
    Sort-Object ProcessId -Unique
)

if (-not $uniqueRoots) {
  Write-Host "Aucun service backend, frontend ou Stripe CLI detecte."
  return
}

$targets = @(
  Get-DescendantProcesses -RootProcesses $uniqueRoots |
    Where-Object { $_.ProcessId -ne $currentProcessId } |
    Sort-Object ProcessId -Unique |
    Sort-Object { $_.ParentProcessId -in @($uniqueRoots.ProcessId) }, ProcessId -Descending
)

Write-Host "Processus detectes:"
foreach ($target in $targets) {
  Write-Host ("- {0} {1}: {2}" -f $target.ProcessId, $target.Name, $target.CommandLine)
}

foreach ($target in $targets) {
  $label = "{0} {1}" -f $target.ProcessId, $target.Name
  if ($PSCmdlet.ShouldProcess($label, "Stop-Process -Force")) {
    Stop-Process -Id $target.ProcessId -Force -ErrorAction SilentlyContinue
  }
}

Start-Sleep -Milliseconds 300

$remaining = @(
  foreach ($target in $targets) {
    Get-Process -Id $target.ProcessId -ErrorAction SilentlyContinue
  }
)

if ($remaining) {
  Write-Warning "Certains processus sont encore actifs:"
  foreach ($process in $remaining) {
    Write-Warning ("- {0} {1}" -f $process.Id, $process.ProcessName)
  }
  exit 1
}

Write-Host "Services backend, frontend et Stripe CLI arretes."
