param(
  [Parameter(Mandatory = $true)][string]$BackupFile,
  [ValidateSet("auto", "sqlite", "postgres")][string]$Mode = "auto",
  [string]$RepoRoot = "",
  [string]$SqliteRelativePath = "backend/horoscope.db",
  [switch]$Force,
  [string]$RuntimeBackupFile = "",
  [string]$PostRestoreHealthUrl = ""
)

$ErrorActionPreference = "Stop"

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

function Get-RepoRoot {
  if ($RepoRoot) {
    return (Resolve-Path $RepoRoot).Path
  }
  if ($env:BACKUP_REPO_ROOT) {
    return (Resolve-Path $env:BACKUP_REPO_ROOT).Path
  }
  return (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}

function Invoke-PostRestoreHealthCheck {
  param([string]$HealthUrl)
  if (-not $HealthUrl) {
    return
  }
  $response = Invoke-WebRequest -Uri $HealthUrl -Method GET -TimeoutSec 10
  if ($response.StatusCode -lt 200 -or $response.StatusCode -ge 300) {
    throw "Post-restore health check failed with status $($response.StatusCode)."
  }
}

function Restore-RuntimeAssets {
  param(
    [Parameter(Mandatory = $true)][string]$RuntimeBackupPath,
    [Parameter(Mandatory = $true)][string]$RootPath
  )

  $resolvedRuntimeBackup = (Resolve-Path $RuntimeBackupPath).Path
  & (Join-Path $PSScriptRoot "backup-validate.ps1") -BackupFile $resolvedRuntimeBackup | Out-Null

  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $zip = [System.IO.Compression.ZipFile]::OpenRead($resolvedRuntimeBackup)
  try {
    foreach ($entry in $zip.Entries) {
      if (-not $entry.Name) {
        continue
      }
      $destination = Join-Path $RootPath $entry.FullName
      $destinationDir = Split-Path -Parent $destination
      if (!(Test-Path $destinationDir)) {
        New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
      }
      [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $destination, $true)
    }
  } finally {
    $zip.Dispose()
  }
}

function Resolve-RestoreMode {
  param(
    [Parameter(Mandatory = $true)][string]$RequestedMode,
    [Parameter(Mandatory = $true)][string]$BackupFilePath
  )

  if ($RequestedMode -ne "auto") {
    return $RequestedMode
  }
  $extension = [System.IO.Path]::GetExtension($BackupFilePath).ToLowerInvariant()
  if ($extension -eq ".db" -or $extension -eq ".sqlite" -or $extension -eq ".sqlite3") {
    return "sqlite"
  }
  if ($extension -eq ".sql") {
    return "postgres"
  }
  throw "Unable to auto-detect restore mode from extension '$extension'. Use -Mode."
}

$resolvedBackup = (Resolve-Path $BackupFile).Path
$root = Get-RepoRoot
$restoreMode = Resolve-RestoreMode -RequestedMode $Mode -BackupFilePath $resolvedBackup

if (-not $Force) {
  $allowNonInteractive = $env:RESTORE_ALLOW_NONINTERACTIVE -eq "1"
  if ($allowNonInteractive) {
    Write-Host "RESTORE_ALLOW_NONINTERACTIVE=1 detected. Proceeding without prompt." -ForegroundColor Yellow
  } else {
    $confirmation = Read-Host "Type RESTORE to continue (destructive operation)"
    if ($confirmation -ne "RESTORE") {
      throw "Restore cancelled by user."
    }
  }
}

& (Join-Path $PSScriptRoot "backup-validate.ps1") -BackupFile $resolvedBackup | Out-Null

if ($restoreMode -eq "sqlite") {
  $targetDb = Join-Path $root $SqliteRelativePath
  $targetDir = Split-Path -Parent $targetDb
  if (!(Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
  }

  if (Test-Path $targetDb) {
    $timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
    $preRestore = "$targetDb.pre-restore-$timestamp.bak"
    Copy-Item -Path $targetDb -Destination $preRestore -Force
  }

  Copy-Item -Path $resolvedBackup -Destination $targetDb -Force
  if ($RuntimeBackupFile) {
    Restore-RuntimeAssets -RuntimeBackupPath $RuntimeBackupFile -RootPath $root
  }
  Invoke-PostRestoreHealthCheck -HealthUrl $PostRestoreHealthUrl
  Write-Output ("restore_ok mode=sqlite target={0}" -f $targetDb)
  exit 0
}

if ($restoreMode -eq "postgres") {
  $databaseUrl = $env:DATABASE_URL
  if (-not $databaseUrl) {
    throw "DATABASE_URL is required for postgres restore mode."
  }
  $psql = Get-Command psql -ErrorAction SilentlyContinue
  if (-not $psql) {
    throw "psql not found in PATH. Install PostgreSQL client tools."
  }
  $timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
  $preRestoreDir = Join-Path $root "backups/db/pre-restore"
  if (!(Test-Path $preRestoreDir)) {
    New-Item -ItemType Directory -Path $preRestoreDir -Force | Out-Null
  }
  $preRestoreFile = Join-Path $preRestoreDir "postgres-pre-restore-$timestamp.sql"
  $pgDump = Get-Command pg_dump -ErrorAction SilentlyContinue
  if (-not $pgDump) {
    throw "pg_dump not found in PATH. Install PostgreSQL client tools."
  }
  Invoke-ExternalChecked -Label "postgres pre-restore snapshot" -Command {
    pg_dump $databaseUrl --format=plain --clean --if-exists --no-owner --no-privileges --file $preRestoreFile
  }
  Invoke-ExternalChecked -Label "psql restore" -Command {
    psql $databaseUrl -v ON_ERROR_STOP=1 -f $resolvedBackup
  }
  if ($RuntimeBackupFile) {
    Restore-RuntimeAssets -RuntimeBackupPath $RuntimeBackupFile -RootPath $root
  }
  Invoke-PostRestoreHealthCheck -HealthUrl $PostRestoreHealthUrl
  Write-Output ("restore_ok mode=postgres source={0}" -f $resolvedBackup)
  exit 0
}

throw "Unsupported restore mode: $restoreMode"
