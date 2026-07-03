#!/usr/bin/env pwsh
<#
.SYNOPSIS
Supprime le theme natal enregistre d'un utilisateur et remet son compteur natal long a zero.

.DESCRIPTION
Active le venv Python du depot, puis execute le script Python local correspondant.
Par defaut, cible daconrilcy@hotmail.com.

.PARAMETER Email
Email de l'utilisateur a purger.
#>

[CmdletBinding()]
param(
  [string] $Email = "daconrilcy@hotmail.com"
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$backendPath = Join-Path $projectRoot "backend"
$venvActivatePath = Join-Path $projectRoot ".venv\Scripts\Activate.ps1"
$pythonScriptPath = Join-Path $PSScriptRoot "reset_user_natal_theme.py"

if (-not (Test-Path -LiteralPath $venvActivatePath)) {
  throw "Venv introuvable: $venvActivatePath"
}

if (-not (Test-Path -LiteralPath $pythonScriptPath)) {
  throw "Script Python introuvable: $pythonScriptPath"
}

. $venvActivatePath
Set-Location -LiteralPath $backendPath
python -B $pythonScriptPath --email $Email
