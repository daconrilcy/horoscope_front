param(
  [ValidateSet("auto", "sqlite", "postgres")][string]$Mode = "auto",
  [string]$OutputDir = "",
  [string]$RepoRoot = "",
  [string]$SqliteRelativePath = "backend/horoscope.db",
  [bool]$IncludeRuntimeAssets = $true
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

function Resolve-BackupMode {
  param(
    [Parameter(Mandatory = $true)][string]$RequestedMode,
    [Parameter(Mandatory = $true)][string]$SqlitePath
  )

  if ($RequestedMode -ne "auto") {
    return $RequestedMode
  }

  $databaseUrl = $env:DATABASE_URL
  if ($databaseUrl -and $databaseUrl.ToLowerInvariant().StartsWith("postgres")) {
    return "postgres"
  }
  if (Test-Path $SqlitePath) {
    return "sqlite"
  }
  throw "Unable to auto-detect backup mode. Provide -Mode sqlite|postgres."
}

function Write-MetadataFile {
  param(
    [Parameter(Mandatory = $true)][string]$BackupFilePath,
    [Parameter(Mandatory = $true)][string]$ModeValue,
    [Parameter(Mandatory = $true)][string]$IntegrityKey
  )

  $hash = Get-FileHash -Algorithm SHA256 -Path $BackupFilePath
  $fileInfo = Get-Item $BackupFilePath
  $signaturePayload = "{0}|{1}|{2}|{3}" -f $hash.Hash, $fileInfo.Length, $ModeValue, [System.IO.Path]::GetFileName($BackupFilePath)
  $hmac = Get-HmacSha256 -Key $IntegrityKey -Message $signaturePayload
  $metadata = [ordered]@{
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    mode             = $ModeValue
    backup_file      = [System.IO.Path]::GetFileName($BackupFilePath)
    backup_path      = $BackupFilePath
    size_bytes       = $fileInfo.Length
    sha256           = $hash.Hash
    hmac_sha256      = $hmac
  }
  $metadataPath = "$BackupFilePath.meta.json"
  ($metadata | ConvertTo-Json -Depth 4) | Set-Content -Path $metadataPath -Encoding UTF8
  return $metadataPath
}

function Get-IntegrityKey {
  $key = $env:BACKUP_METADATA_HMAC_KEY
  if (-not $key) {
    throw "BACKUP_METADATA_HMAC_KEY is required for backup metadata integrity."
  }
  return $key
}

function Get-HmacSha256 {
  param(
    [Parameter(Mandatory = $true)][string]$Key,
    [Parameter(Mandatory = $true)][string]$Message
  )

  $keyBytes = [System.Text.Encoding]::UTF8.GetBytes($Key)
  $messageBytes = [System.Text.Encoding]::UTF8.GetBytes($Message)
  $hmac = [System.Security.Cryptography.HMACSHA256]::new($keyBytes)
  try {
    $hashBytes = $hmac.ComputeHash($messageBytes)
    return [Convert]::ToHexString($hashBytes)
  } finally {
    $hmac.Dispose()
  }
}

function Backup-RuntimeAssets {
  param(
    [Parameter(Mandatory = $true)][string]$RootPath,
    [Parameter(Mandatory = $true)][string]$TimestampValue,
    [Parameter(Mandatory = $true)][string]$IntegrityKey
  )

  $runtimeSources = @(
    "backend/.env",
    "docker-compose.yml",
    "backend/alembic.ini"
  )
  $existingSources = @()
  foreach ($source in $runtimeSources) {
    $sourcePath = Join-Path $RootPath $source
    if (Test-Path $sourcePath) {
      $existingSources += $sourcePath
    }
  }
  if ($existingSources.Count -eq 0) {
    Write-Output "runtime_backup_skipped reason=no_runtime_sources_found"
    return
  }

  $runtimeBackupDir = Join-Path $RootPath "backups/runtime"
  if (!(Test-Path $runtimeBackupDir)) {
    New-Item -ItemType Directory -Path $runtimeBackupDir -Force | Out-Null
  }
  $runtimeBackupFile = Join-Path $runtimeBackupDir "runtime-backup-$TimestampValue.zip"

  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $zip = [System.IO.Compression.ZipFile]::Open($runtimeBackupFile, [System.IO.Compression.ZipArchiveMode]::Create)
  try {
    foreach ($sourcePath in $existingSources) {
      $relative = [System.IO.Path]::GetRelativePath($RootPath, $sourcePath)
      [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $sourcePath, $relative) | Out-Null
    }
  } finally {
    $zip.Dispose()
  }

  $runtimeMeta = Write-MetadataFile -BackupFilePath $runtimeBackupFile -ModeValue "runtime-assets" -IntegrityKey $IntegrityKey
  Write-Output ("runtime_backup_ok file={0} metadata={1}" -f $runtimeBackupFile, $runtimeMeta)
}

$root = Get-RepoRoot
$timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMdd-HHmmss")
$sqlitePath = Join-Path $root $SqliteRelativePath
$resolvedOutputDir = if ($OutputDir) { $OutputDir } else { "backups/db" }
$backupDir = Join-Path $root $resolvedOutputDir
$integrityKey = Get-IntegrityKey
if (!(Test-Path $backupDir)) {
  New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}

$resolvedMode = Resolve-BackupMode -RequestedMode $Mode -SqlitePath $sqlitePath

if ($resolvedMode -eq "sqlite") {
  if (!(Test-Path $sqlitePath)) {
    throw "SQLite database file not found: $sqlitePath"
  }
  $backupFile = Join-Path $backupDir "sqlite-backup-$timestamp.db"
  Copy-Item -Path $sqlitePath -Destination $backupFile -Force
  $metadataFile = Write-MetadataFile -BackupFilePath $backupFile -ModeValue "sqlite" -IntegrityKey $integrityKey
  if ($IncludeRuntimeAssets) {
    Backup-RuntimeAssets -RootPath $root -TimestampValue $timestamp -IntegrityKey $integrityKey
  }
  Write-Output ("backup_ok mode=sqlite file={0} metadata={1}" -f $backupFile, $metadataFile)
  exit 0
}

if ($resolvedMode -eq "postgres") {
  $databaseUrl = $env:DATABASE_URL
  if (-not $databaseUrl) {
    throw "DATABASE_URL is required for postgres backup mode."
  }
  $pgDump = Get-Command pg_dump -ErrorAction SilentlyContinue
  if (-not $pgDump) {
    throw "pg_dump not found in PATH. Install PostgreSQL client tools."
  }
  $backupFile = Join-Path $backupDir "postgres-backup-$timestamp.sql"
  Invoke-ExternalChecked -Label "pg_dump backup" -Command {
    pg_dump $databaseUrl --format=plain --clean --if-exists --no-owner --no-privileges --file $backupFile
  }
  $metadataFile = Write-MetadataFile -BackupFilePath $backupFile -ModeValue "postgres" -IntegrityKey $integrityKey
  if ($IncludeRuntimeAssets) {
    Backup-RuntimeAssets -RootPath $root -TimestampValue $timestamp -IntegrityKey $integrityKey
  }
  Write-Output ("backup_ok mode=postgres file={0} metadata={1}" -f $backupFile, $metadataFile)
  exit 0
}

throw "Unsupported mode: $resolvedMode"
