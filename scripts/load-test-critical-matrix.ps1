param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [string]$OutputDir = "artifacts/load-test-matrix",
  [string]$B2BApiKey = "",
  [switch]$RequireB2B
)

$ErrorActionPreference = "Stop"

if (!(Test-Path $OutputDir)) {
  New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$profiles = @("smoke", "nominal", "stress")
foreach ($profile in $profiles) {
  $reportPath = Join-Path $OutputDir ("load-test-{0}.json" -f $profile)
  $args = @{
    BaseUrl    = $BaseUrl
    Profile    = $profile
    OutputPath = $reportPath
  }
  if ($B2BApiKey) {
    $args["B2BApiKey"] = $B2BApiKey
  }
  if ($RequireB2B) {
    $args["RequireB2B"] = $true
  }

  & (Join-Path $PSScriptRoot "load-test-critical.ps1") @args
}

Write-Output ("load_test_matrix_ok output_dir={0}" -f (Resolve-Path $OutputDir).Path)
