param(
  [string]$RootPath = "",
  [string]$AllowlistPath = "",
  [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"

function Get-RootPathResolved {
  param([string]$RequestedRoot)
  if ($RequestedRoot) {
    return (Resolve-Path $RequestedRoot).Path
  }
  if ($env:SECRETS_SCAN_ROOT) {
    return (Resolve-Path $env:SECRETS_SCAN_ROOT).Path
  }
  return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Get-EffectiveAllowlistPath {
  param([string]$RequestedAllowlist)
  if ($RequestedAllowlist) {
    return $RequestedAllowlist
  }
  if ($env:SECRETS_SCAN_ALLOWLIST) {
    return $env:SECRETS_SCAN_ALLOWLIST
  }
  return (Join-Path $PSScriptRoot "secrets-scan-allowlist.txt")
}

function Load-Allowlist {
  param([string]$Path)
  if (!(Test-Path $Path)) {
    return @()
  }
  $entries = @(
    Get-Content $Path |
      ForEach-Object { $_.Trim() } |
      Where-Object { $_ -and -not $_.StartsWith("#") }
  )
  foreach ($entry in $entries) {
    if ($entry -match '[\*\?\[\]]') {
      throw "Wildcard entry '$entry' is forbidden in secrets scan allowlist."
    }
  }
  return $entries
}

$root = Get-RootPathResolved -RequestedRoot $RootPath
$allowlist = Load-Allowlist -Path (Get-EffectiveAllowlistPath -RequestedAllowlist $AllowlistPath)

$excludedDirNames = @(".git", ".venv", "node_modules", "__pycache__", "dist", "build", "artifacts", "_bmad-output")
$includedExtensions = @(".py", ".ps1", ".ts", ".tsx", ".js", ".json", ".yml", ".yaml", ".md", ".env")

$patterns = @(
  [pscustomobject]@{ Name = "jwt_literal"; Regex = 'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}' },
  [pscustomobject]@{ Name = "openai_key"; Regex = 'sk-(proj-)?[A-Za-z0-9_-]{20,}' },
  [pscustomobject]@{ Name = "hardcoded_secret_assignment"; Regex = '(?i)\b(jwt_secret_key|api_credentials_secret_key|reference_seed_admin_token|llm_anonymization_salt|postgres_password|api[_-]?key|secret)\b\s*[:=]\s*["''][^"'']{12,}["'']' }
)

$files = Get-ChildItem -Path $root -Recurse -File | Where-Object {
  $extension = $_.Extension.ToLowerInvariant()
  if ($includedExtensions -notcontains $extension) {
    return $false
  }
  foreach ($excluded in $excludedDirNames) {
    if ($_.FullName -match [regex]::Escape([System.IO.Path]::DirectorySeparatorChar + $excluded + [System.IO.Path]::DirectorySeparatorChar)) {
      return $false
    }
  }
  return $true
}

$findings = @()
foreach ($file in $files) {
  $relativePath = [System.IO.Path]::GetRelativePath($root, $file.FullName)
  $relativePathNormalized = $relativePath.Replace("\", "/")
  $lines = @(Get-Content -Path $file.FullName)
  for ($index = 0; $index -lt $lines.Count; $index++) {
    $line = $lines[$index]
    foreach ($pattern in $patterns) {
      if ($line -match $pattern.Regex) {
        $entry = "${relativePathNormalized}:$($index + 1)"
        $isAllowed = $false
        foreach ($allow in $allowlist) {
          if ($entry -eq $allow) {
            $isAllowed = $true
            break
          }
        }
        if (-not $isAllowed) {
          $snippet = $line.Trim()
          if ($snippet.Length -gt 140) {
            $snippet = $snippet.Substring(0, 140) + "..."
          }
          $findings += [pscustomobject]@{
            file    = $relativePath
            line    = $index + 1
            pattern = $pattern.Name
            snippet = $snippet
          }
        }
      }
    }
  }
}

if ($findings.Count -gt 0) {
  Write-Host "secrets_scan_failed findings=$($findings.Count)" -ForegroundColor Red
  foreach ($finding in $findings) {
    Write-Host ("- {0}:{1} [{2}] {3}" -f $finding.file, $finding.line, $finding.pattern, $finding.snippet)
  }
  exit 1
}

if ($VerboseOutput) {
  Write-Host ("Scanned {0} files under {1}" -f $files.Count, $root) -ForegroundColor DarkGray
}
Write-Host "secrets_scan_ok" -ForegroundColor Green
