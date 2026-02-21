param(
  [string]$RootPath = "",
  [string]$BaseUrl = "http://127.0.0.1:8000",
  [string]$AccessToken = "",
  [int]$TargetUserId = 0,
  [string]$OutputPath = "",
  [string]$MarkdownPath = ""
)

$ErrorActionPreference = "Stop"

function Resolve-RootPath {
  param([string]$RequestedRoot)
  if ($RequestedRoot) {
    return (Resolve-Path $RequestedRoot).Path
  }
  return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Ensure-ParentDirectory {
  param([string]$Path)
  $parent = Split-Path -Parent $Path
  if ($parent -and -not (Test-Path $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
  }
}

function Resolve-OutputPath {
  param(
    [string]$Root,
    [string]$RequestedPath,
    [int]$UserId
  )
  if ($RequestedPath) {
    return $RequestedPath
  }
  return (Join-Path $Root "artifacts/privacy/rgpd-evidence-user-$UserId.json")
}

function Resolve-MarkdownPath {
  param(
    [string]$Root,
    [string]$RequestedPath,
    [int]$UserId
  )
  if ($RequestedPath) {
    return $RequestedPath
  }
  return (Join-Path $Root "artifacts/privacy/rgpd-evidence-user-$UserId.md")
}

if (-not $AccessToken.Trim()) {
  throw "AccessToken is required."
}
if ($TargetUserId -le 0) {
  throw "TargetUserId must be > 0."
}

$root = Resolve-RootPath -RequestedRoot $RootPath
$jsonPath = Resolve-OutputPath -Root $root -RequestedPath $OutputPath -UserId $TargetUserId
$mdPath = Resolve-MarkdownPath -Root $root -RequestedPath $MarkdownPath -UserId $TargetUserId

Ensure-ParentDirectory -Path $jsonPath
Ensure-ParentDirectory -Path $mdPath

$headers = @{
  Authorization = "Bearer $AccessToken"
}

$url = "$BaseUrl/v1/privacy/evidence/$TargetUserId"
try {
  $response = Invoke-RestMethod -Method Get -Uri $url -Headers $headers -ContentType "application/json"
} catch {
  $errorBody = ""
  if ($null -ne $_.ErrorDetails -and $null -ne $_.ErrorDetails.Message) {
    $errorBody = $_.ErrorDetails.Message
  }
  if (-not $errorBody) {
    $errorBody = $_.Exception.Message
  }
  throw "RGPD evidence retrieval failed: $errorBody"
}

$response | ConvertTo-Json -Depth 20 | Set-Content -Path $jsonPath -Encoding UTF8

$data = $response.data
$lines = @()
$lines += "# RGPD Operational Evidence"
$lines += ""
$lines += "- schema_version: $($data.schema_version)"
$lines += "- user_id: $($data.user_id)"
$lines += "- collected_at: $($data.collected_at)"
$lines += ""
$lines += "## Export Evidence"
$lines += "- request_id: $($data.export_request.request_id)"
$lines += "- status: $($data.export_request.status)"
$lines += "- requested_at: $($data.export_request.requested_at)"
$lines += "- completed_at: $($data.export_request.completed_at)"
$lines += ""
$lines += "## Delete Evidence"
$lines += "- request_id: $($data.delete_request.request_id)"
$lines += "- status: $($data.delete_request.status)"
$lines += "- requested_at: $($data.delete_request.requested_at)"
$lines += "- completed_at: $($data.delete_request.completed_at)"
$lines += ""
$lines += "## Audit Trace Evidence"
$lines += "- audit_events_count: $(@($data.audit_events).Count)"
foreach ($event in @($data.audit_events | Select-Object -First 10)) {
  $lines += "- [event#$($event.event_id)] action=$($event.action) status=$($event.status) request_id=$($event.request_id)"
}
$lines += ""
$lines += "## Reproducibility"
$lines += "- Command: .\\scripts\\generate-rgpd-evidence.ps1 -BaseUrl $BaseUrl -AccessToken *** -TargetUserId $TargetUserId"
$lines += "- Output JSON: $jsonPath"
$lines += "- Output Markdown: $mdPath"

$lines -join "`r`n" | Set-Content -Path $mdPath -Encoding UTF8

Write-Host "rgpd_evidence_ok json=$jsonPath markdown=$mdPath" -ForegroundColor Green
