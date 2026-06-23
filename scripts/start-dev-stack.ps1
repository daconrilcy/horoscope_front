#!/usr/bin/env pwsh
<#
.SYNOPSIS
Lance la pile de developpement locale dans Windows Terminal.

.DESCRIPTION
Demarre backend et frontend par defaut. Le listener Stripe local est lance
uniquement lorsque le parametre -WithStripe est fourni.

.PARAMETER WithStripe
Ajoute un onglet Stripe qui execute scripts/stripe-listen-webhook.ps1. La CLI
Stripe doit etre installee et disponible dans le PATH lorsque ce mode est demande.

.PARAMETER NoCleanStart
Desactive l'arret automatique des anciens services detectes pour ce depot avant
le lancement. Par defaut, le script fait un demarrage propre.

.PARAMETER Help
Affiche l'aide du script sans lancer la stack locale.
#>

[CmdletBinding()]
param(
  [string] $BackendHost = "127.0.0.1",
  [int] $BackendPort = 8001,
  [string] $FrontendHost = "127.0.0.1",
  [int] $FrontendPort = 5173,
  [switch] $WithStripe,
  [switch] $NoCleanStart,
  [switch] $Help
)

$ErrorActionPreference = "Stop"

if ($Help) {
  Get-Help -Detailed $PSCommandPath
  return
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $repoRoot "backend"
$frontendPath = Join-Path $repoRoot "frontend"
$stripeScriptPath = Join-Path $PSScriptRoot "stripe-listen-webhook.ps1"
$stopScriptPath = Join-Path $PSScriptRoot "stop-dev-services.ps1"
$venvActivatePath = Join-Path $repoRoot ".venv\Scripts\Activate.ps1"

function Assert-PathExists {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Path,

    [Parameter(Mandatory = $true)]
    [string] $Label
  )

  if (-not (Test-Path -LiteralPath $Path)) {
    throw "$Label introuvable: $Path"
  }
}

function Resolve-ShellCommand {
  $pwshCommand = Get-Command "pwsh" -ErrorAction SilentlyContinue
  if ($null -ne $pwshCommand) {
    return $pwshCommand.Source
  }

  $powershellCommand = Get-Command "powershell" -ErrorAction SilentlyContinue
  if ($null -ne $powershellCommand) {
    return $powershellCommand.Source
  }

  throw "PowerShell est introuvable dans le PATH."
}

function Assert-CommandExists {
  param(
    [Parameter(Mandatory = $true)]
    [string] $Name,

    [Parameter(Mandatory = $true)]
    [string] $InstallHint
  )

  if ($null -eq (Get-Command $Name -ErrorAction SilentlyContinue)) {
    throw "$Name est introuvable. $InstallHint"
  }
}

function Assert-LocalPortAvailable {
  <#
  .SYNOPSIS
  Verifie qu'un port local n'est pas deja occupe avant de lancer un onglet dev.
  #>
  param(
    [Parameter(Mandatory = $true)]
    [int] $Port,

    [Parameter(Mandatory = $true)]
    [string] $ServiceName
  )

  $listeners = @(
    Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  )
  if (-not $listeners) {
    return
  }

  $ownerIds = @($listeners | Select-Object -ExpandProperty OwningProcess -Unique)
  $ownerSummary = @(
    foreach ($ownerId in $ownerIds) {
      $process = Get-CimInstance Win32_Process -Filter "ProcessId = $ownerId" -ErrorAction SilentlyContinue
      if ($null -eq $process) {
        "PID $ownerId"
      } else {
        "PID $ownerId $($process.Name)"
      }
    }
  ) -join ", "

  throw "$ServiceName ne peut pas demarrer: le port $Port est deja occupe ($ownerSummary). Arretez l'ancienne stack avec scripts\stop-dev-services.ps1 puis relancez."
}

Assert-PathExists -Path $backendPath -Label "Dossier backend"
Assert-PathExists -Path $frontendPath -Label "Dossier frontend"
Assert-CommandExists -Name "npm" -InstallHint "Installez Node.js ou ajoutez npm au PATH."

if (-not $NoCleanStart) {
  Assert-PathExists -Path $stopScriptPath -Label "Script d'arret"
  Write-Host "Arret preventif des anciens services de developpement..."
  & $stopScriptPath -Ports @($BackendPort, $FrontendPort, 5174, 4173, 4174)
}

Assert-LocalPortAvailable -Port $BackendPort -ServiceName "Backend"
Assert-LocalPortAvailable -Port $FrontendPort -ServiceName "Frontend"

if ($WithStripe) {
  Assert-PathExists -Path $stripeScriptPath -Label "Script Stripe"
  Assert-CommandExists -Name "stripe" -InstallHint "Installez Stripe CLI ou relancez sans -WithStripe."
}

if (-not (Test-Path -LiteralPath $venvActivatePath)) {
  Assert-CommandExists -Name "py" -InstallHint "Installez Python 3.13 avec le lanceur py.exe."
}

$wtCommand = Get-Command "wt" -ErrorAction SilentlyContinue
if ($null -eq $wtCommand) {
  throw "Windows Terminal est introuvable. Installez Windows Terminal ou ajoutez 'wt' au PATH."
}

$shellCommand = Resolve-ShellCommand

$backendCommand = @"
Set-Location -LiteralPath '$repoRoot'
if (-not (Test-Path -LiteralPath '$venvActivatePath')) {
  py -3.13 -m venv .venv
  . '$venvActivatePath'
  Set-Location -LiteralPath '$backendPath'
  python -m pip install -e '.[dev]'
} else {
  . '$venvActivatePath'
  Set-Location -LiteralPath '$backendPath'
}
python -m uvicorn app.main:app --host $BackendHost --port $BackendPort --reload
"@

$frontendCommand = @"
Set-Location -LiteralPath '$frontendPath'
if (-not (Test-Path -LiteralPath 'node_modules')) {
  npm ci
}
npm run dev -- --host $FrontendHost --port $FrontendPort --strictPort
"@

$stripeCommand = @"
Set-Location -LiteralPath '$repoRoot'
& '$stripeScriptPath'
"@

$wtArguments = @(
  "new-tab", "--title", "Backend", $shellCommand, "-NoExit", "-Command", $backendCommand,
  ";",
  "new-tab", "--title", "Frontend", $shellCommand, "-NoExit", "-Command", $frontendCommand
)

if ($WithStripe) {
  $wtArguments += @(
    ";",
    "new-tab", "--title", "Stripe", $shellCommand, "-NoExit", "-Command", $stripeCommand
  )
}

& $wtCommand.Source @wtArguments
