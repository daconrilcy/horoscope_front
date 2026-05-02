# Orchestration locale des controles de readiness release LLM.
param(
  [string]$CandidateVersion = "",
  [string]$OutputDir = "artifacts",
  [string]$ProgressiveBlocklist = "fb.use_case_first,fb.resolve_model",
  [string]$PytestCachePath = "",
  [switch]$SkipStartupSmoke
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendRoot = Join-Path $root "backend"
$venvActivate = Join-Path $root ".venv\\Scripts\\Activate.ps1"
$resolvedPytestCachePath = Join-Path $root ".pytest_cache_runtime"

if (-not [string]::IsNullOrWhiteSpace($PytestCachePath)) {
  if ([System.IO.Path]::IsPathRooted($PytestCachePath)) {
    $resolvedPytestCachePath = $PytestCachePath
  } else {
    $resolvedPytestCachePath = Join-Path $root $PytestCachePath
  }
}

if (!(Test-Path $venvActivate)) {
  throw "Virtual environment not found at $venvActivate"
}

$resolvedOutputDir = Join-Path $root $OutputDir
$chaosDir = Join-Path $resolvedOutputDir "chaos"
$readinessReportPath = Join-Path $resolvedOutputDir "llm-release-readiness.json"
New-Item -ItemType Directory -Force -Path $resolvedOutputDir | Out-Null
New-Item -ItemType Directory -Force -Path $chaosDir | Out-Null

if (-not [string]::IsNullOrWhiteSpace($ProgressiveBlocklist)) {
  $env:LLM_LEGACY_PROGRESSIVE_BLOCKLIST = $ProgressiveBlocklist
}

if ([string]::IsNullOrWhiteSpace($CandidateVersion)) {
  $CandidateVersion = "release-candidate-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
}

function Invoke-Step {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][scriptblock]$Action
  )

  Write-Host "==> $Name" -ForegroundColor Cyan
  $global:LASTEXITCODE = 0
  & $Action
  if ($LASTEXITCODE -ne 0) {
    throw "Step '$Name' failed with exit code $LASTEXITCODE"
  }
  Write-Host "OK: $Name" -ForegroundColor Green
}

function Invoke-BackendStep {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][scriptblock]$Action
  )

  $backendAction = $Action
  Invoke-Step -Name $Name -Action {
    Push-Location $backendRoot
    try {
      & $venvActivate
      & $backendAction
    } finally {
      Pop-Location
    }
  }
}

function Assert-ReadinessReportGo {
  param(
    [Parameter(Mandatory = $true)][string]$ReportPath
  )

  $report = Get-Content -Raw -Path $ReportPath | ConvertFrom-Json
  if ($report.decision -ne "go") {
    $blockerSummary = "no blocker details"
    if ($null -ne $report.blockers -and $report.blockers.Count -gt 0) {
      $blockerSummary = $report.blockers -join "; "
    }
    throw "LLM release readiness decision is '$($report.decision)': $blockerSummary"
  }
}

Push-Location $root
try {
  Invoke-BackendStep -Name "Doc conformity" -Action {
    python scripts\check_doc_conformity.py --json | Set-Content -Path (Join-Path $resolvedOutputDir "llm-doc-conformity.json") -Encoding UTF8
  }

  Invoke-BackendStep -Name "Release lifecycle targeted tests" -Action {
    pytest -q tests\integration\test_llm_release.py -o "cache_dir=$resolvedPytestCachePath"
  }

  Invoke-BackendStep -Name "Golden regression and sensitive data targeted tests" -Action {
    pytest -q tests\integration\test_llm_golden_regression.py tests\unit\test_sensitive_data_non_leakage.py -o "cache_dir=$resolvedPytestCachePath"
  }

  Invoke-BackendStep -Name "Chaos runtime targeted tests" -Action {
    $env:CHAOS_REPORT_PATH = Join-Path $chaosDir "story-66-43-chaos-report.json"
    pytest -q tests\integration\test_llm_provider_runtime_chaos.py -o "cache_dir=$resolvedPytestCachePath"
  }

  Invoke-BackendStep -Name "Legacy residual maintenance report" -Action {
    python scripts\legacy_residual_report.py | Set-Content -Path (Join-Path $resolvedOutputDir "llm-legacy-residual-report.md") -Encoding UTF8
  }

  Invoke-BackendStep -Name "Build candidate snapshot" -Action {
    python scripts\build_llm_release_candidate.py --version $CandidateVersion --output (Join-Path $resolvedOutputDir "llm-release-candidate.json")
  }

  if (-not $SkipStartupSmoke) {
    Invoke-Step -Name "Startup smoke" -Action {
      & .\scripts\startup-smoke.ps1
    }
  }

  Invoke-BackendStep -Name "Readiness aggregate report" -Action {
    python scripts\build_llm_release_readiness_report.py --output $readinessReportPath
  }

  Invoke-Step -Name "Readiness decision" -Action {
    Assert-ReadinessReportGo -ReportPath $readinessReportPath
  }

  Write-Host "llm_release_readiness_ok" -ForegroundColor Green
} finally {
  Pop-Location
}
