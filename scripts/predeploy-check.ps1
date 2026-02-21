$ErrorActionPreference = "Stop"

function Invoke-Step {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][scriptblock]$Action
  )

  Write-Host "==> $Name" -ForegroundColor Cyan
  & $Action
  Write-Host "OK: $Name" -ForegroundColor Green
}

function Invoke-ExternalChecked {
  param(
    [Parameter(Mandatory = $true)][string]$Label,
    [Parameter(Mandatory = $true)][scriptblock]$Command
  )

  $global:LASTEXITCODE = 0
  & $Command
  if ($LASTEXITCODE -ne 0) {
    throw "$Label failed with exit code $LASTEXITCODE."
  }
}

$root = $null
if ($env:PREDEPLOY_ROOT) {
  $root = Resolve-Path $env:PREDEPLOY_ROOT
} else {
  $root = Resolve-Path (Join-Path $PSScriptRoot "..")
}

$qualityGateScript = $null
if ($env:PREDEPLOY_QUALITY_GATE_SCRIPT) {
  $qualityGateScript = Resolve-Path $env:PREDEPLOY_QUALITY_GATE_SCRIPT
} else {
  $qualityGateScript = Join-Path $PSScriptRoot "quality-gate.ps1"
}

$startupSmokeScript = $null
if ($env:PREDEPLOY_STARTUP_SMOKE_SCRIPT) {
  $startupSmokeScript = Resolve-Path $env:PREDEPLOY_STARTUP_SMOKE_SCRIPT
} else {
  $startupSmokeScript = Join-Path $PSScriptRoot "startup-smoke.ps1"
}

if (-not (Test-Path $qualityGateScript)) {
  throw "Missing script: $qualityGateScript"
}

Push-Location $root
try {
  Invoke-Step -Name "Run quality gate" -Action {
    & $qualityGateScript
  }

  Invoke-Step -Name "Validate Docker Compose configuration" -Action {
    Invoke-ExternalChecked -Label "docker compose config" -Command {
      docker compose config | Out-Null
    }
  }

  if ($env:PREDEPLOY_SKIP_STARTUP_SMOKE -eq "1") {
    Write-Host "Skip startup smoke check: PREDEPLOY_SKIP_STARTUP_SMOKE=1" -ForegroundColor Yellow
  } elseif (Test-Path $startupSmokeScript) {
    Invoke-Step -Name "Startup smoke check (backend + frontend)" -Action {
      & $startupSmokeScript
    }
  } else {
    Write-Host "Skip startup smoke check: script not found" -ForegroundColor Yellow
  }

  Write-Host "predeploy_check_ok" -ForegroundColor Green
} finally {
  Pop-Location
}
