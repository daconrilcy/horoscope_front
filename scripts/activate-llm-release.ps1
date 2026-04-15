param(
  [string]$BaseUrl = "http://127.0.0.1:8001",
  [string]$CandidatePath = "artifacts/llm-release-candidate.json",
  [string]$QualificationPath = "artifacts/llm-qualification-evidence.json",
  [string]$GoldenPath = "artifacts/llm-golden-evidence.json",
  [string]$SmokePath = "artifacts/llm-smoke-evidence.json",
  [string]$OutputPath = "artifacts/llm-activation-response.json"
)

$ErrorActionPreference = "Stop"

$candidate = Get-Content $CandidatePath | ConvertFrom-Json
$qualification = Get-Content $QualificationPath | ConvertFrom-Json
$golden = Get-Content $GoldenPath | ConvertFrom-Json
$smoke = Get-Content $SmokePath | ConvertFrom-Json

$snapshotId = $candidate.candidate_snapshot.id
$payload = @{
  qualification_report = @{
    active_snapshot_id = $qualification.active_snapshot_id
    active_snapshot_version = $qualification.active_snapshot_version
    manifest_entry_id = $qualification.manifest_entry_id
    verdict = $qualification.verdict
    generated_at = $qualification.generated_at
  }
  golden_report = @{
    active_snapshot_id = $golden.active_snapshot_id
    active_snapshot_version = $golden.active_snapshot_version
    manifest_entry_id = $golden.manifest_entry_id
    verdict = $golden.verdict
    generated_at = $golden.generated_at
  }
  smoke_result = @{
    status = $smoke.status
    active_snapshot_id = $smoke.active_snapshot_id
    active_snapshot_version = $smoke.active_snapshot_version
    manifest_entry_id = $smoke.manifest_entry_id
    forbidden_fallback_detected = $smoke.forbidden_fallback_detected
    details = $smoke.details
  }
  monitoring_thresholds = @{
    error_rate = 0.02
    p95_latency_ms = 1500.0
    fallback_rate = 0.01
  }
  rollback_policy = "recommend-only"
  max_evidence_age_minutes = 60
}

$body = $payload | ConvertTo-Json -Depth 10
$uri = "$BaseUrl/v1/admin/llm/releases/$snapshotId/activate"
$response = Invoke-WebRequest -Uri $uri -Method Post -ContentType "application/json" -Body $body -UseBasicParsing
$response.Content | Set-Content -Path $OutputPath -Encoding UTF8
Write-Host "Activation response written to $OutputPath" -ForegroundColor Green
