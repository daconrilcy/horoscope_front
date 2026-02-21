param(
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [ValidateSet("smoke", "nominal", "stress")][string]$Profile = "smoke",
  [int]$Iterations = -1,
  [int]$Concurrency = -1,
  [string]$OutputPath = "artifacts/load-test-report.json",
  [string]$B2BApiKey = "",
  [switch]$RequireB2B,
  [string]$OpsAccessToken = "",
  [string]$OpsWindow = "24h"
)

$ErrorActionPreference = "Stop"

function Invoke-ApiCall {
  param(
    [Parameter(Mandatory = $true)][ValidateSet("GET", "POST")][string]$Method,
    [Parameter(Mandatory = $true)][string]$Url,
    [hashtable]$Headers = @{},
    [object]$Body = $null
  )

  $start = [System.Diagnostics.Stopwatch]::StartNew()
  try {
    if ($Method -eq "GET") {
      $response = Invoke-WebRequest -Uri $Url -Method Get -Headers $Headers
    } else {
      $jsonBody = if ($Body -eq $null) { "{}" } else { $Body | ConvertTo-Json -Depth 10 }
      $response = Invoke-WebRequest -Uri $Url -Method Post -Headers $Headers -ContentType "application/json" -Body $jsonBody
    }
    $start.Stop()
    return [pscustomobject]@{
      status_code = [int]$response.StatusCode
      duration_ms = [math]::Round($start.Elapsed.TotalMilliseconds, 2)
      ok          = $true
      error       = $null
    }
  } catch {
    $start.Stop()
    $statusCode = 0
    if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
      $statusCode = [int]$_.Exception.Response.StatusCode
    }
    return [pscustomobject]@{
      status_code = $statusCode
      duration_ms = [math]::Round($start.Elapsed.TotalMilliseconds, 2)
      ok          = $false
      error       = $_.Exception.Message
    }
  }
}

function Invoke-ScenarioLoad {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][ValidateSet("GET", "POST")][string]$Method,
    [Parameter(Mandatory = $true)][string]$Url,
    [hashtable]$Headers = @{},
    [object]$Body = $null,
    [Parameter(Mandatory = $true)][int]$TotalRequests,
    [Parameter(Mandatory = $true)][int]$WorkerCount,
    [int[]]$AllowedStatusCodes = @()
  )

  if ($TotalRequests -le 0) {
    throw "TotalRequests must be > 0 for scenario '$Name'."
  }
  if ($WorkerCount -le 0) {
    throw "WorkerCount must be > 0 for scenario '$Name'."
  }
  $requestsPerWorker = [math]::Ceiling($TotalRequests / [double]$WorkerCount)
  $jobs = @()
  $scenarioStopwatch = [System.Diagnostics.Stopwatch]::StartNew()

  for ($worker = 0; $worker -lt $WorkerCount; $worker++) {
    $jobs += Start-Job -ScriptBlock {
      param($methodParam, $urlParam, $headersParam, $bodyParam, $countParam)
      $rows = @()
      for ($i = 0; $i -lt $countParam; $i++) {
        $start = [System.Diagnostics.Stopwatch]::StartNew()
        try {
          if ($methodParam -eq "GET") {
            $resp = Invoke-WebRequest -Uri $urlParam -Method Get -Headers $headersParam
            $status = [int]$resp.StatusCode
            $ok = $true
            $err = $null
          } else {
            $json = if ($bodyParam -eq $null) { "{}" } else { $bodyParam | ConvertTo-Json -Depth 10 }
            $resp = Invoke-WebRequest -Uri $urlParam -Method Post -Headers $headersParam -ContentType "application/json" -Body $json
            $status = [int]$resp.StatusCode
            $ok = $true
            $err = $null
          }
        } catch {
          $status = 0
          if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $status = [int]$_.Exception.Response.StatusCode
          }
          $ok = $false
          $err = $_.Exception.Message
        }
        $start.Stop()
        $rows += [pscustomobject]@{
          status_code = $status
          duration_ms = [math]::Round($start.Elapsed.TotalMilliseconds, 2)
          ok          = $ok
          error       = $err
        }
      }
      return $rows
    } -ArgumentList $Method, $Url, $Headers, $Body, $requestsPerWorker
  }

  $raw = @()
  foreach ($job in $jobs) {
    $raw += Receive-Job -Job $job -Wait -AutoRemoveJob
  }
  $scenarioStopwatch.Stop()

  $records = $raw | Select-Object -First $TotalRequests
  $latencies = @($records | ForEach-Object { [double]$_.duration_ms } | Sort-Object)
  if ($latencies.Count -eq 0) {
    throw "Scenario '$Name' returned no records."
  }
  $p50Index = [math]::Floor(0.5 * ($latencies.Count - 1))
  $p95Index = [math]::Floor(0.95 * ($latencies.Count - 1))
  $p99Index = [math]::Floor(0.99 * ($latencies.Count - 1))

  $statusMap = @{}
  foreach ($item in $records) {
    $key = [string]$item.status_code
    if (-not $statusMap.ContainsKey($key)) {
      $statusMap[$key] = 0
    }
    $statusMap[$key]++
  }

  $hasAllowedOverrides = $AllowedStatusCodes.Count -gt 0
  $successCount = if ($hasAllowedOverrides) {
    (@($records | Where-Object { $AllowedStatusCodes -contains [int]$_.status_code })).Count
  } else {
    (@($records | Where-Object { $_.status_code -ge 200 -and $_.status_code -lt 300 })).Count
  }
  $protectionCount = (@($records | Where-Object { $_.status_code -eq 429 })).Count
  $errorCount = if ($hasAllowedOverrides) {
    (@($records | Where-Object { ($AllowedStatusCodes -notcontains [int]$_.status_code) -and $_.status_code -ne 429 })).Count
  } else {
    (@($records | Where-Object { $_.status_code -ge 500 -or ($_.status_code -ge 400 -and $_.status_code -ne 429) -or $_.status_code -eq 0 })).Count
  }
  $elapsedSeconds = [math]::Max($scenarioStopwatch.Elapsed.TotalSeconds, 0.001)
  $throughputRps = [math]::Round($records.Count / $elapsedSeconds, 2)

  return [pscustomobject]@{
    name           = $Name
    total_requests = $records.Count
    concurrency    = $WorkerCount
    success_count  = $successCount
    protection_count = $protectionCount
    error_count    = $errorCount
    error_rate     = [math]::Round(($errorCount / [double]$records.Count) * 100, 2)
    latency_ms     = [pscustomobject]@{
      p50 = $latencies[$p50Index]
      p95 = $latencies[$p95Index]
      p99 = $latencies[$p99Index]
    }
    elapsed_seconds = [math]::Round($elapsedSeconds, 3)
    throughput_rps = $throughputRps
    status_codes = $statusMap
    records = $records
    phase_name = "single"
  }
}

function Get-ProfilePhases {
  param(
    [Parameter(Mandatory = $true)][ValidateSet("smoke", "nominal", "stress")][string]$ProfileName,
    [Parameter(Mandatory = $true)][int]$BaseIterations,
    [Parameter(Mandatory = $true)][int]$BaseConcurrency
  )

  $base = [math]::Max($BaseIterations, 1)
  $concurrency = [math]::Max($BaseConcurrency, 1)
  switch ($ProfileName) {
    "smoke" {
      $ramp = [math]::Max([int][math]::Floor($base * 0.3), 1)
      $plateau = [math]::Max([int][math]::Floor($base * 0.5), 1)
      $spike = [math]::Max($base - $ramp - $plateau, 1)
      return @(
        [pscustomobject]@{ name = "ramp_up"; requests = $ramp; concurrency = [math]::Max([int][math]::Floor($concurrency * 0.6), 1) },
        [pscustomobject]@{ name = "plateau"; requests = $plateau; concurrency = $concurrency },
        [pscustomobject]@{ name = "spike"; requests = $spike; concurrency = [math]::Max([int][math]::Ceiling($concurrency * 1.4), 1) }
      )
    }
    "nominal" {
      $ramp = [math]::Max([int][math]::Floor($base * 0.2), 1)
      $plateau = [math]::Max([int][math]::Floor($base * 0.6), 1)
      $spike = [math]::Max($base - $ramp - $plateau, 1)
      return @(
        [pscustomobject]@{ name = "ramp_up"; requests = $ramp; concurrency = [math]::Max([int][math]::Floor($concurrency * 0.7), 1) },
        [pscustomobject]@{ name = "plateau"; requests = $plateau; concurrency = $concurrency },
        [pscustomobject]@{ name = "spike"; requests = $spike; concurrency = [math]::Max([int][math]::Ceiling($concurrency * 1.6), 1) }
      )
    }
    default {
      $ramp = [math]::Max([int][math]::Floor($base * 0.15), 1)
      $plateau = [math]::Max([int][math]::Floor($base * 0.55), 1)
      $spike = [math]::Max($base - $ramp - $plateau, 1)
      return @(
        [pscustomobject]@{ name = "ramp_up"; requests = $ramp; concurrency = [math]::Max([int][math]::Floor($concurrency * 0.8), 1) },
        [pscustomobject]@{ name = "plateau"; requests = $plateau; concurrency = [math]::Max([int][math]::Ceiling($concurrency * 1.2), 1) },
        [pscustomobject]@{ name = "spike"; requests = $spike; concurrency = [math]::Max([int][math]::Ceiling($concurrency * 1.8), 1) }
      )
    }
  }
}

function Merge-PhaseScenarioResults {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][array]$PhaseResults
  )

  $allRecords = @()
  $totalSeconds = 0.0
  foreach ($phase in $PhaseResults) {
    $allRecords += @($phase.records)
    $totalSeconds += [double]$phase.elapsed_seconds
  }
  $latencies = @($allRecords | ForEach-Object { [double]$_.duration_ms } | Sort-Object)
  if ($latencies.Count -eq 0) {
    throw "Scenario '$Name' produced no records."
  }
  $p50Index = [math]::Floor(0.5 * ($latencies.Count - 1))
  $p95Index = [math]::Floor(0.95 * ($latencies.Count - 1))
  $p99Index = [math]::Floor(0.99 * ($latencies.Count - 1))

  $statusMap = @{}
  foreach ($item in $allRecords) {
    $key = [string]$item.status_code
    if (-not $statusMap.ContainsKey($key)) {
      $statusMap[$key] = 0
    }
    $statusMap[$key]++
  }
  $successCount = (@($allRecords | Where-Object { $_.status_code -ge 200 -and $_.status_code -lt 300 })).Count
  $protectionCount = (@($allRecords | Where-Object { $_.status_code -eq 429 })).Count
  $errorCount = (@($allRecords | Where-Object { $_.status_code -ge 500 -or ($_.status_code -ge 400 -and $_.status_code -ne 429) -or $_.status_code -eq 0 })).Count
  $elapsedSeconds = [math]::Max($totalSeconds, 0.001)
  $throughputRps = [math]::Round($allRecords.Count / $elapsedSeconds, 2)

  $phaseSummaries = @()
  foreach ($phase in $PhaseResults) {
    $phaseSummaries += [pscustomobject]@{
      name = $phase.phase_name
      requests = $phase.total_requests
      concurrency = $phase.concurrency
      elapsed_seconds = $phase.elapsed_seconds
      throughput_rps = $phase.throughput_rps
      error_rate = $phase.error_rate
      latency_ms = $phase.latency_ms
    }
  }

  return [pscustomobject]@{
    name            = $Name
    total_requests  = $allRecords.Count
    concurrency     = ($phaseSummaries | Measure-Object -Property concurrency -Maximum).Maximum
    success_count   = $successCount
    protection_count = $protectionCount
    error_count     = $errorCount
    error_rate      = [math]::Round(($errorCount / [double]$allRecords.Count) * 100, 2)
    latency_ms      = [pscustomobject]@{
      p50 = $latencies[$p50Index]
      p95 = $latencies[$p95Index]
      p99 = $latencies[$p99Index]
    }
    elapsed_seconds = [math]::Round($elapsedSeconds, 3)
    throughput_rps  = $throughputRps
    status_codes    = $statusMap
    phases          = $phaseSummaries
  }
}

function Invoke-ScenarioByProfile {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][ValidateSet("GET", "POST")][string]$Method,
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)][array]$PhaseDefinitions,
    [hashtable]$Headers = @{},
    [object]$Body = $null,
    [int[]]$AllowedStatusCodes = @()
  )

  $phaseResults = @()
  foreach ($phase in $PhaseDefinitions) {
    $phaseResult = Invoke-ScenarioLoad -Name $Name -Method $Method -Url $Url -Headers $Headers -Body $Body -TotalRequests $phase.requests -WorkerCount $phase.concurrency -AllowedStatusCodes $AllowedStatusCodes
    $phaseResult | Add-Member -NotePropertyName phase_name -NotePropertyValue $phase.name -Force
    $phaseResults += $phaseResult
  }

  return Merge-PhaseScenarioResults -Name $Name -PhaseResults $phaseResults
}

function New-Recommendations {
  param([Parameter(Mandatory = $true)][array]$ScenarioResults)

  $recommendations = @()
  foreach ($result in $ScenarioResults) {
    if ($result.error_rate -gt 0) {
      $recommendations += [pscustomobject]@{
        priority = "high"
        scenario = $result.name
        action   = "Investigate unexpected errors (5xx/other failures); review logs/request_id and resilience settings."
      }
    }
    if ($result.protection_count -gt 0) {
      $recommendations += [pscustomobject]@{
        priority = "medium"
        scenario = $result.name
        action   = "Observe 429 protection hits and validate rate-limit/quota thresholds versus expected traffic profile."
      }
    }
    if ($result.latency_ms.p95 -gt 1000) {
      $recommendations += [pscustomobject]@{
        priority = "medium"
        scenario = $result.name
        action   = "Reduce p95 latency (cache/read path, DB indexes, rate-limit store tuning)."
      }
    }
    if ($result.latency_ms.p99 -gt 1500) {
      $recommendations += [pscustomobject]@{
        priority = "low"
        scenario = $result.name
        action   = "Profile tail latency and remove slow-path hotspots."
      }
    }
    if ($result.throughput_rps -lt 5) {
      $recommendations += [pscustomobject]@{
        priority = "medium"
        scenario = $result.name
        action   = "Increase sustained throughput capacity (optimize endpoint hot path and worker sizing)."
      }
    }
  }
  return $recommendations
}

if ($Iterations -le 0 -or $Concurrency -le 0) {
  switch ($Profile) {
    "smoke" {
      if ($Iterations -le 0) { $Iterations = 20 }
      if ($Concurrency -le 0) { $Concurrency = 5 }
    }
    "nominal" {
      if ($Iterations -le 0) { $Iterations = 80 }
      if ($Concurrency -le 0) { $Concurrency = 10 }
    }
    "stress" {
      if ($Iterations -le 0) { $Iterations = 160 }
      if ($Concurrency -le 0) { $Concurrency = 20 }
    }
  }
}

if ($Iterations -le 0) {
  throw "Iterations must be > 0 after profile/default resolution."
}
if ($Concurrency -le 0) {
  throw "Concurrency must be > 0 after profile/default resolution."
}

$runId = [guid]::NewGuid().ToString("N")
$email = "loadtest-$runId@example.com"
$password = "Passw0rd!"

$registerPayload = @{
  email    = $email
  password = $password
}
$register = Invoke-ApiCall -Method POST -Url "$BaseUrl/v1/auth/register" -Body $registerPayload
if (-not $register.ok -or $register.status_code -ne 200) {
  throw "Failed to register load user. status=$($register.status_code) error=$($register.error)"
}

$login = Invoke-RestMethod -Method Post -Uri "$BaseUrl/v1/auth/login" -ContentType "application/json" -Body ($registerPayload | ConvertTo-Json)
$accessToken = $login.data.tokens.access_token
if (-not $accessToken) {
  throw "Unable to extract access token from login response."
}
$authHeaders = @{ Authorization = "Bearer $accessToken" }
$opsToken = if ($OpsAccessToken) { $OpsAccessToken } else { $env:OPS_ACCESS_TOKEN }
$opsHeaders = if ($opsToken) { @{ Authorization = "Bearer $opsToken" } } else { @{} }

$opsMonitoring = [ordered]@{
  enabled = [bool]($opsToken)
  pre_run = $null
  post_run = $null
  skipped_reason = $null
}
if ($opsToken) {
  $opsMonitoring.pre_run = Invoke-ApiCall -Method GET -Url "$BaseUrl/v1/ops/monitoring/operational-summary?window=$OpsWindow" -Headers $opsHeaders
} else {
  $opsMonitoring.skipped_reason = "no_ops_access_token"
}

$checkoutPayload = @{
  plan_code             = "basic-entry"
  payment_method_token  = "pm_card_ok"
  idempotency_key       = "loadtest-checkout-$runId"
}
$checkout = Invoke-ApiCall -Method POST -Url "$BaseUrl/v1/billing/checkout" -Headers $authHeaders -Body $checkoutPayload
if (-not $checkout.ok -or $checkout.status_code -ne 200) {
  throw "Failed to checkout test subscription. status=$($checkout.status_code)"
}

# Prime privacy status endpoints.
$null = Invoke-ApiCall -Method POST -Url "$BaseUrl/v1/privacy/export" -Headers $authHeaders

$scenarioResults = @()
$phaseDefinitions = Get-ProfilePhases -ProfileName $Profile -BaseIterations $Iterations -BaseConcurrency $Concurrency
$scenarioResults += Invoke-ScenarioByProfile -Name "billing_quota" -Method GET -Url "$BaseUrl/v1/billing/quota" -Headers $authHeaders -PhaseDefinitions $phaseDefinitions
$scenarioResults += Invoke-ScenarioByProfile -Name "privacy_export_status" -Method GET -Url "$BaseUrl/v1/privacy/export" -Headers $authHeaders -PhaseDefinitions $phaseDefinitions
$scenarioResults += Invoke-ScenarioByProfile -Name "privacy_delete_request" -Method POST -Url "$BaseUrl/v1/privacy/delete" -Headers $authHeaders -Body @{ confirmation = "DELETE" } -PhaseDefinitions $phaseDefinitions -AllowedStatusCodes @(200, 409)
$scenarioResults += Invoke-ScenarioByProfile -Name "chat_conversations" -Method GET -Url "$BaseUrl/v1/chat/conversations?limit=20&offset=0" -Headers $authHeaders -PhaseDefinitions $phaseDefinitions

$effectiveB2BKey = if ($B2BApiKey) { $B2BApiKey } else { $env:B2B_API_KEY }
$skippedScenarios = @()
if ($effectiveB2BKey) {
  $b2bHeaders = @{ "X-API-Key" = $effectiveB2BKey }
  $scenarioResults += Invoke-ScenarioByProfile -Name "b2b_weekly_by_sign" -Method GET -Url "$BaseUrl/v1/b2b/astrology/weekly-by-sign" -Headers $b2bHeaders -PhaseDefinitions $phaseDefinitions
} else {
  $skippedScenarios += "b2b_weekly_by_sign"
  if ($RequireB2B) {
    throw "B2B scenario required but no B2BApiKey parameter and no B2B_API_KEY env var."
  }
  Write-Host "Skipping b2b scenario: no B2BApiKey parameter and no B2B_API_KEY env var." -ForegroundColor Yellow
}
if ($opsToken) {
  $opsMonitoring.post_run = Invoke-ApiCall -Method GET -Url "$BaseUrl/v1/ops/monitoring/operational-summary?window=$OpsWindow" -Headers $opsHeaders
}

$recommendations = @(New-Recommendations -ScenarioResults $scenarioResults)
$report = [ordered]@{
  generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
  base_url         = $BaseUrl
  profile          = $Profile
  profile_phases   = $phaseDefinitions
  iterations       = $Iterations
  concurrency      = $Concurrency
  require_b2b      = [bool]$RequireB2B
  scenarios        = $scenarioResults
  skipped_scenarios = $skippedScenarios
  ops_monitoring_correlation = $opsMonitoring
  recommendations  = $recommendations
}

$outputDir = Split-Path -Parent $OutputPath
if ($outputDir -and !(Test-Path $outputDir)) {
  New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

($report | ConvertTo-Json -Depth 8) | Set-Content -Path $OutputPath -Encoding UTF8
Write-Output ("load_test_ok report={0}" -f (Resolve-Path $OutputPath).Path)
