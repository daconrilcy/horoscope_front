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
if ($env:QUALITY_GATE_ROOT) {
  $root = Resolve-Path $env:QUALITY_GATE_ROOT
} else {
  $root = Resolve-Path (Join-Path $PSScriptRoot "..")
}
$venvActivate = Join-Path $root ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvActivate)) {
  throw "Virtual environment not found at '$venvActivate'. Create it before running quality gates."
}
$secretsScanScript = Join-Path $PSScriptRoot "scan-secrets.ps1"
if (-not (Test-Path $secretsScanScript)) {
  throw "Secrets scan script not found at '$secretsScanScript'."
}
$securityVerificationScript = Join-Path $PSScriptRoot "security-verification.ps1"
if (-not (Test-Path $securityVerificationScript)) {
  throw "Security verification script not found at '$securityVerificationScript'."
}

Push-Location $root
try {
  $ciRaw = ""
  if ($null -ne $env:CI) {
    $ciRaw = $env:CI
  }
  $isCi = ($ciRaw.Trim().ToLower() -in @("1", "true", "yes"))
  $rotationPgUrl = ""
  if ($null -ne $env:ROTATION_RESTART_POSTGRES_DATABASE_URL) {
    $rotationPgUrl = $env:ROTATION_RESTART_POSTGRES_DATABASE_URL
  }

  Invoke-Step -Name "Activate Python virtual environment" -Action {
    . $venvActivate
  }

  Invoke-Step -Name "CI PostgreSQL restart-test guardrail" -Action {
    if ($isCi -and -not $rotationPgUrl.Trim()) {
      throw "ROTATION_RESTART_POSTGRES_DATABASE_URL must be set in CI to run restart-rotation PostgreSQL coverage."
    }
  }

  Invoke-Step -Name "Repository secrets scan" -Action {
    & $secretsScanScript -RootPath $root
    if (-not $?) {
      throw "secrets scan failed."
    }
  }

  Invoke-Step -Name "Security verification pack (SAST/deps/pentest-ready)" -Action {
    & $securityVerificationScript -RootPath $root -IncludeDevDependencies
    if (-not $?) {
      throw "security verification pack failed."
    }
  }

  Invoke-Step -Name "Backend lint (ruff)" -Action {
    Set-Location $root
    Invoke-ExternalChecked -Label "ruff check backend" -Command { ruff check backend }
  }

  Invoke-Step -Name "Backend tests (pytest)" -Action {
    Set-Location $root
    Invoke-ExternalChecked -Label "pytest backend/app/tests" -Command { pytest -q backend/app/tests }
  }

  Invoke-Step -Name "PostgreSQL restart-rotation test" -Action {
    if ($isCi -or $rotationPgUrl.Trim()) {
      Set-Location $root
      $env:ROTATION_RESTART_POSTGRES_DATABASE_URL = $rotationPgUrl
      Invoke-ExternalChecked -Label "pytest restart-rotation postgres" -Command {
        pytest -q backend/app/tests/integration/test_secret_rotation_process_restart.py::test_rotation_survives_real_python_process_restart_with_http_flows_postgres
      }
    } else {
      Write-Host "Skipped: ROTATION_RESTART_POSTGRES_DATABASE_URL not set and not running in CI." -ForegroundColor Yellow
    }
  }

  Invoke-Step -Name "Alembic migration check (single head + history available)" -Action {
    Set-Location (Join-Path $root "backend")
    $headsOutput = (& alembic heads) | Out-String
    if ($LASTEXITCODE -ne 0) {
      throw "alembic heads failed with exit code $LASTEXITCODE."
    }
    $headLines = @($headsOutput -split "`r?`n" | Where-Object { $_.Trim() -ne "" })
    if ($headLines.Count -ne 1) {
      throw "Expected exactly one Alembic head, got $($headLines.Count)."
    }
    & alembic history | Out-Null
    if ($LASTEXITCODE -ne 0) {
      throw "alembic history failed with exit code $LASTEXITCODE."
    }
  }

  Invoke-Step -Name "Frontend lint" -Action {
    Set-Location $root
    Invoke-ExternalChecked -Label "frontend lint" -Command { npm --prefix frontend run lint }
  }

  Invoke-Step -Name "Frontend tests" -Action {
    Set-Location $root
    Invoke-ExternalChecked -Label "frontend tests" -Command { npm --prefix frontend run test -- --run }
  }

  Invoke-Step -Name "Frontend build" -Action {
    Set-Location $root
    Invoke-ExternalChecked -Label "frontend build" -Command { npm --prefix frontend run build }
  }

  Write-Host "quality_gate_ok" -ForegroundColor Green
} finally {
  Pop-Location
}
