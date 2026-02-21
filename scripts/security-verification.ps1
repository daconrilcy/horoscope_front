param(
  [string]$RootPath = "",
  [string]$OutputPath = "",
  [string]$RemediationPlanPath = "",
  [string]$AllowlistPath = "",
  [string[]]$FailOnSeverities = @("high", "critical"),
  [switch]$IncludeDevDependencies,
  [string]$BanditReportPath = "",
  [string]$PipAuditReportPath = "",
  [string]$NpmAuditReportPath = ""
)

$ErrorActionPreference = "Stop"

function Resolve-RootPath {
  param([string]$RequestedRoot)
  if ($RequestedRoot) {
    return (Resolve-Path $RequestedRoot).Path
  }
  return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Resolve-DefaultPath {
  param(
    [string]$RequestedPath,
    [string]$Root,
    [string]$LeafPath
  )
  if ($RequestedPath) {
    return $RequestedPath
  }
  return (Join-Path $Root $LeafPath)
}

function Ensure-ParentDirectory {
  param([string]$Path)
  $parent = Split-Path -Parent $Path
  if ($parent -and -not (Test-Path $parent)) {
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
  }
}

function Load-Allowlist {
  param([string]$Path)
  if (-not (Test-Path $Path)) {
    return @()
  }
  return @(
    Get-Content $Path |
      ForEach-Object { $_.Trim() } |
      Where-Object { $_ -and -not $_.StartsWith("#") }
  )
}

function Normalize-Severity {
  param([string]$Severity)
  if (-not $Severity) {
    return "unknown"
  }
  switch ($Severity.Trim().ToLower()) {
    "critical" { return "critical" }
    "high" { return "high" }
    "medium" { return "medium" }
    "moderate" { return "medium" }
    "low" { return "low" }
    "info" { return "info" }
    "informational" { return "info" }
    default { return "unknown" }
  }
}

function Resolve-CvssSeverityFromScore {
  param([double]$Score)
  if ($Score -ge 9.0) {
    return "critical"
  }
  if ($Score -ge 7.0) {
    return "high"
  }
  if ($Score -ge 4.0) {
    return "medium"
  }
  if ($Score -gt 0) {
    return "low"
  }
  return "unknown"
}

function Resolve-PipAuditSeverity {
  param([object]$Vuln)

  if ($null -ne $Vuln.severity) {
    if ($Vuln.severity -is [string]) {
      return Normalize-Severity -Severity $Vuln.severity
    }
    foreach ($entry in @($Vuln.severity)) {
      if ($entry -is [string]) {
        $normalized = Normalize-Severity -Severity $entry
        if ($normalized -ne "unknown") {
          return $normalized
        }
      }
      if ($entry -is [pscustomobject] -and $entry.score) {
        $scoreText = [string]$entry.score
        $scoreMatch = [regex]::Match($scoreText, "([0-9]+(\.[0-9]+)?)")
        if ($scoreMatch.Success) {
          $scoreValue = [double]$scoreMatch.Groups[1].Value
          return Resolve-CvssSeverityFromScore -Score $scoreValue
        }
      }
    }
  }
  return "high"
}

function Invoke-CommandToJson {
  param(
    [string]$Label,
    [scriptblock]$Command,
    [int[]]$AcceptedExitCodes = @(0)
  )
  $global:LASTEXITCODE = 0
  $output = & $Command
  if ($AcceptedExitCodes -notcontains $LASTEXITCODE) {
    throw "$Label failed with exit code $LASTEXITCODE."
  }
  return ($output | Out-String)
}

function Parse-BanditFindings {
  param([pscustomobject]$BanditJson)
  $findings = @()
  foreach ($item in @($BanditJson.results)) {
    $package = ""
    if ($item.filename) {
      $package = [string]$item.filename
    }
    $lineNumber = ""
    if ($null -ne $item.line_number) {
      $lineNumber = [string]$item.line_number
    }
    $id = [string]$item.test_id
    $severity = Normalize-Severity -Severity ([string]$item.issue_severity)
    $findingKey = "bandit:${id}:${package}:${lineNumber}"
    $findings += [pscustomobject]@{
      key = $findingKey
      tool = "bandit"
      category = "sast"
      id = $id
      title = [string]$item.test_name
      severity = $severity
      package = $package
      location = $package
      line = $lineNumber
      recommendation = "Review code pattern and apply secure alternative."
      raw = $item
    }
  }
  return $findings
}

function Parse-PipAuditFindings {
  param([object]$PipAuditJson)
  $findings = @()
  if ($null -eq $PipAuditJson) {
    return @()
  }

  $dependencies = @()
  if ($PipAuditJson -is [pscustomobject] -and $null -ne $PipAuditJson.dependencies) {
    $dependencies = @($PipAuditJson.dependencies)
  } else {
    $dependencies = @($PipAuditJson)
  }

  foreach ($dependency in $dependencies) {
    if ($null -eq $dependency) {
      continue
    }
    $packageName = [string]$dependency.name
    if (-not $packageName.Trim()) {
      continue
    }
    foreach ($vuln in @($dependency.vulns)) {
      if ($null -eq $vuln) {
        continue
      }
      $id = [string]$vuln.id
      if (-not $id.Trim()) {
        continue
      }
      $fixVersions = @($vuln.fix_versions | Where-Object { $_ -and ([string]$_).Trim() })
      $recommendation = "Upgrade dependency to a fixed version."
      if ($fixVersions.Count -gt 0) {
        $recommendation = "Upgrade dependency to one of: $($fixVersions -join ', ')."
      }
      $findingKey = "pip-audit:${id}:${packageName}"
      $severity = Resolve-PipAuditSeverity -Vuln $vuln
      $findings += [pscustomobject]@{
        key = $findingKey
        tool = "pip-audit"
        category = "dependency"
        id = $id
        title = ([string]$vuln.description)
        severity = $severity
        package = $packageName
        location = "python-env"
        line = ""
        recommendation = $recommendation
        raw = $vuln
      }
    }
  }
  return $findings
}

function Parse-NpmAuditFindings {
  param([pscustomobject]$NpmAuditJson)
  $findings = @()
  $vulnerabilityMap = $NpmAuditJson.vulnerabilities
  if ($null -eq $vulnerabilityMap) {
    return @()
  }
  foreach ($property in $vulnerabilityMap.PSObject.Properties) {
    $packageName = $property.Name
    $item = $property.Value
    $severity = Normalize-Severity -Severity ([string]$item.severity)
    $id = "npm:$packageName"
    $title = "npm audit finding for $packageName"
    $recommendation = "Run npm audit fix or update package version."
    $fixAvailable = $item.fixAvailable
    if ($fixAvailable -is [bool] -and $fixAvailable) {
      $recommendation = "Run npm audit fix for this package."
    }
    if ($fixAvailable -is [pscustomobject] -and $fixAvailable.name) {
      $recommendation = "Upgrade to $($fixAvailable.name)@$($fixAvailable.version)."
    }

    $findingKey = "npm-audit:$id"
    $findings += [pscustomobject]@{
      key = $findingKey
      tool = "npm-audit"
      category = "dependency"
      id = $id
      title = $title
      severity = $severity
      package = $packageName
      location = "frontend/package-lock.json"
      line = ""
      recommendation = $recommendation
      raw = $item
    }
  }
  return $findings
}

function Build-RemediationMarkdown {
  param(
    [pscustomobject]$Summary,
    [object[]]$Findings
  )
  $lines = @()
  $lines += "# Security Remediation Plan"
  $lines += ""
  $lines += "Generated at: $($Summary.generated_at)"
  $lines += ""
  $lines += "## Severity Summary"
  foreach ($severity in @("critical", "high", "medium", "low", "unknown", "info")) {
    $lines += "- ${severity}: $($Summary.findings_by_severity.$severity)"
  }
  $lines += ""
  $lines += "## Critical and High Findings"
  $criticalHigh = @($Findings | Where-Object { $_.severity -in @("critical", "high") })
  if ($criticalHigh.Count -eq 0) {
    $lines += "- No critical/high findings."
  } else {
    foreach ($finding in $criticalHigh) {
      $lines += "- [$($finding.severity)] $($finding.id) ($($finding.package)) - $($finding.recommendation)"
    }
  }
  $lines += ""
  $lines += "## Next Actions"
  $lines += "- Assign owner, ETA and verification plan for each critical/high finding."
  $lines += "- Re-run security verification after remediation."
  return ($lines -join "`r`n")
}

$root = Resolve-RootPath -RequestedRoot $RootPath
$outputFile = Resolve-DefaultPath -RequestedPath $OutputPath -Root $root -LeafPath "artifacts/security/security-verification-report.json"
$planFile = Resolve-DefaultPath -RequestedPath $RemediationPlanPath -Root $root -LeafPath "artifacts/security/security-remediation-plan.md"
$allowlistFile = Resolve-DefaultPath -RequestedPath $AllowlistPath -Root $root -LeafPath "scripts/security-findings-allowlist.txt"
$allowlist = Load-Allowlist -Path $allowlistFile

Ensure-ParentDirectory -Path $outputFile
Ensure-ParentDirectory -Path $planFile

Push-Location $root
try {
  $banditJsonText = ""
  if ($BanditReportPath) {
    $banditJsonText = Get-Content -Path $BanditReportPath -Raw
  } else {
    $banditJsonText = Invoke-CommandToJson -Label "bandit scan" -Command {
      bandit -r backend/app -x backend/app/tests -f json -q
    } -AcceptedExitCodes @(0, 1)
  }
  $banditJson = $banditJsonText | ConvertFrom-Json

  $pipAuditJsonText = ""
  if ($PipAuditReportPath) {
    $pipAuditJsonText = Get-Content -Path $PipAuditReportPath -Raw
  } else {
    $pipAuditJsonText = Invoke-CommandToJson -Label "pip-audit scan" -Command {
      pip-audit --format json
    } -AcceptedExitCodes @(0, 1)
  }
  $pipAuditJson = $pipAuditJsonText | ConvertFrom-Json

  $npmAuditJsonText = ""
  if ($NpmAuditReportPath) {
    $npmAuditJsonText = Get-Content -Path $NpmAuditReportPath -Raw
  } else {
    $npmAuditJsonText = Invoke-CommandToJson -Label "npm audit scan" -Command {
      if ($IncludeDevDependencies) {
        npm --prefix frontend audit --json
      } else {
        npm --prefix frontend audit --omit=dev --json
      }
    } -AcceptedExitCodes @(0, 1)
  }
  $npmAuditJson = $npmAuditJsonText | ConvertFrom-Json

  $findings = @()
  $findings += Parse-BanditFindings -BanditJson $banditJson
  $findings += Parse-PipAuditFindings -PipAuditJson $pipAuditJson
  $findings += Parse-NpmAuditFindings -NpmAuditJson $npmAuditJson

  $effectiveFindings = @()
  foreach ($finding in $findings) {
    if ($allowlist -contains $finding.key) {
      continue
    }
    $effectiveFindings += $finding
  }

  $severityBuckets = @{
    critical = @($effectiveFindings | Where-Object { $_.severity -eq "critical" }).Count
    high = @($effectiveFindings | Where-Object { $_.severity -eq "high" }).Count
    medium = @($effectiveFindings | Where-Object { $_.severity -eq "medium" }).Count
    low = @($effectiveFindings | Where-Object { $_.severity -eq "low" }).Count
    unknown = @($effectiveFindings | Where-Object { $_.severity -eq "unknown" }).Count
    info = @($effectiveFindings | Where-Object { $_.severity -eq "info" }).Count
  }

  $toolBuckets = @{
    bandit = @($effectiveFindings | Where-Object { $_.tool -eq "bandit" }).Count
    pip_audit = @($effectiveFindings | Where-Object { $_.tool -eq "pip-audit" }).Count
    npm_audit = @($effectiveFindings | Where-Object { $_.tool -eq "npm-audit" }).Count
  }

  $summary = [pscustomobject]@{
    generated_at = (Get-Date).ToString("s")
    root = $root
    findings_total = $effectiveFindings.Count
    findings_by_severity = [pscustomobject]$severityBuckets
    findings_by_tool = [pscustomobject]$toolBuckets
    fail_on_severities = @($FailOnSeverities | ForEach-Object { $_.Trim().ToLower() } | Where-Object { $_ })
    include_dev_dependencies = [bool]$IncludeDevDependencies
  }

  $report = [pscustomobject]@{
    summary = $summary
    findings = $effectiveFindings
  }

  $report | ConvertTo-Json -Depth 20 | Set-Content -Path $outputFile -Encoding UTF8
  Build-RemediationMarkdown -Summary $summary -Findings $effectiveFindings | Set-Content -Path $planFile -Encoding UTF8

  $violations = @($effectiveFindings | Where-Object {
      $summary.fail_on_severities -contains $_.severity
    })
  if ($violations.Count -gt 0) {
    Write-Host "security_pack_failed findings=$($violations.Count) output=$outputFile" -ForegroundColor Red
    foreach ($violation in $violations) {
      Write-Host "- [$($violation.severity)] $($violation.key) => $($violation.recommendation)"
    }
    exit 1
  }

  Write-Host "security_pack_ok output=$outputFile plan=$planFile" -ForegroundColor Green
} finally {
  Pop-Location
}
