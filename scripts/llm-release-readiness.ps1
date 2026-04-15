param(
  [string]$CandidateVersion = "",
  [string]$OutputDir = "artifacts",
  [string]$ProgressiveBlocklist = "fb.use_case_first,fb.resolve_model",
  [switch]$SkipStartupSmoke
)

$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$backendRoot = Join-Path $root "backend"
$venvActivate = Join-Path $root ".venv\\Scripts\\Activate.ps1"

if (!(Test-Path $venvActivate)) {
  throw "Virtual environment not found at $venvActivate"
}

$resolvedOutputDir = Join-Path $root $OutputDir
$chaosDir = Join-Path $resolvedOutputDir "chaos"
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
  & $Action
  Write-Host "OK: $Name" -ForegroundColor Green
}

Push-Location $root
try {
  Invoke-Step -Name "Doc conformity" -Action {
    & $venvActivate
    python backend\scripts\check_doc_conformity.py --json | Set-Content -Path (Join-Path $resolvedOutputDir "llm-doc-conformity.json") -Encoding UTF8
  }

  Invoke-Step -Name "Release lifecycle targeted tests" -Action {
    & $venvActivate
    pytest -q backend\tests\integration\test_llm_release.py -o cache_dir=C:\dev\horoscope_front\.pytest_cache_runtime
  }

  Invoke-Step -Name "Golden regression and sensitive data targeted tests" -Action {
    & $venvActivate
    pytest -q backend\tests\integration\test_story_66_36_golden_regression.py backend\tests\unit\test_sensitive_data_non_leakage.py -o cache_dir=C:\dev\horoscope_front\.pytest_cache_runtime
  }

  Invoke-Step -Name "Chaos runtime targeted tests" -Action {
    & $venvActivate
    $env:CHAOS_REPORT_PATH = Join-Path $chaosDir "story-66-43-chaos-report.json"
    pytest -q backend\tests\integration\test_story_66_43_provider_runtime_chaos.py -o cache_dir=C:\dev\horoscope_front\.pytest_cache_runtime
  }

  Invoke-Step -Name "Legacy residual maintenance report" -Action {
    & $venvActivate
    python backend\scripts\legacy_residual_report.py | Set-Content -Path (Join-Path $resolvedOutputDir "llm-legacy-residual-report.md") -Encoding UTF8
  }

  Invoke-Step -Name "Build candidate snapshot" -Action {
    & $venvActivate
    python backend\scripts\build_llm_release_candidate.py --version $CandidateVersion --output (Join-Path $resolvedOutputDir "llm-release-candidate.json")
  }

  if (-not $SkipStartupSmoke) {
    Invoke-Step -Name "Startup smoke" -Action {
      & .\scripts\startup-smoke.ps1
    }
  }

  Invoke-Step -Name "Readiness aggregate report" -Action {
    & $venvActivate
    python backend\scripts\build_llm_release_readiness_report.py --output (Join-Path $resolvedOutputDir "llm-release-readiness.json")
  }

  Write-Host "llm_release_readiness_ok" -ForegroundColor Green
} finally {
  Pop-Location
}
