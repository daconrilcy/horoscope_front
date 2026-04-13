param(
    [string]$InputPath = "artifacts/load-test-nominal.json",
    [string]$OutputPath = "artifacts/performance-qualification-report.md"
)

if (!(Test-Path $InputPath)) {
    Write-Error "Input file not found: $InputPath"
    exit 1
}

$data = Get-Content -Path $InputPath | ConvertFrom-Json
$quals = $data.performance_qualification

if ($null -eq $quals -or $quals.Count -eq 0) {
    Write-Warning "No performance qualification data found in $InputPath"
    exit 0
}

$md = "# Performance Qualification Report`n`n"
$md += "- **Generated at**: $($data.generated_at_utc)`n"
$md += "- **Base URL**: $($data.base_url)`n"
$md += "- **Profile**: $($data.profile)`n"
$md += "- **Concurrency**: $($data.concurrency)`n`n"

$md += "## LLM Gateway Qualification Summary`n`n"
$md += "| Family | Verdict | Success Rate | Protection Rate | Error Rate | p95 Latency | p99 Latency | Snapshot |`n"
$md += "|---|---|---|---|---|---|---|---|`n"

foreach ($q in $quals) {
    $successRate = "{0:P2}" -f ($q.success_count / $q.total_requests)
    $protRate = "{0:P2}" -f ($q.protection_count / $q.total_requests)
    $errRate = "{0:P2}" -f $q.error_rate
    $snapshot = if ($q.active_snapshot_version) { $q.active_snapshot_version } else { "N/A" }
    $md += "| $($q.family) | **$($q.verdict.ToUpper())** | $successRate | $protRate | $errRate | $($q.latency_p95_ms)ms | $($q.latency_p99_ms)ms | $snapshot |`n"
}

$md += "`n## Constraints & Warnings`n`n"
$hasIssues = $false
foreach ($q in $quals) {
    if ($null -ne $q.constraints -and $q.constraints.Count -gt 0) {
        $hasIssues = $true
        $md += "### $($q.family)`n"
        foreach ($c in $q.constraints) {
            $md += "- $c`n"
        }
        $md += "`n"
    }
}

if (-not $hasIssues) {
    $md += "No issues or warnings detected.`n"
}

$md += "`n## Detailed Scenarios`n`n"
$md += "| Scenario | Requests | Success | Protections | Errors | Throughput |`n"
$md += "|---|---|---|---|---|---|`n"
foreach ($s in $data.scenarios) {
    $md += "| $($s.name) | $($s.total_requests) | $($s.success_count) | $($s.protection_count) | $($s.error_count) | $($s.throughput_rps) RPS |`n"
}

$md | Set-Content -Path $OutputPath -Encoding UTF8
Write-Host "Performance qualification report generated at: $(Resolve-Path $OutputPath)" -ForegroundColor Green
