param(
  [Parameter(Mandatory = $true)][string]$BackupFile
)

$ErrorActionPreference = "Stop"

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

if (!(Test-Path $BackupFile)) {
  throw "Backup file not found: $BackupFile"
}

$metadataPath = "$BackupFile.meta.json"
if (!(Test-Path $metadataPath)) {
  throw "Metadata file not found: $metadataPath"
}

$metadata = Get-Content -Raw $metadataPath | ConvertFrom-Json
$currentHash = (Get-FileHash -Algorithm SHA256 -Path $BackupFile).Hash

if ($currentHash -ne $metadata.sha256) {
  throw "Backup hash mismatch. Expected $($metadata.sha256), got $currentHash."
}

$sizeBytes = (Get-Item $BackupFile).Length
if ([int64]$sizeBytes -ne [int64]$metadata.size_bytes) {
  throw "Backup size mismatch. Expected $($metadata.size_bytes), got $sizeBytes."
}

$integrityKey = $env:BACKUP_METADATA_HMAC_KEY
if (-not $integrityKey) {
  throw "BACKUP_METADATA_HMAC_KEY is required for backup metadata validation."
}
if (-not $metadata.hmac_sha256) {
  throw "Backup metadata missing hmac_sha256."
}
$modeValue = if ($metadata.mode) { [string]$metadata.mode } else { "unknown" }
$backupFileName = [System.IO.Path]::GetFileName($BackupFile)
$signaturePayload = "{0}|{1}|{2}|{3}" -f $currentHash, $sizeBytes, $modeValue, $backupFileName
$expectedHmac = Get-HmacSha256 -Key $integrityKey -Message $signaturePayload
if ($expectedHmac -ne [string]$metadata.hmac_sha256) {
  throw "Backup metadata HMAC mismatch."
}

Write-Output ("backup_validate_ok file={0}" -f (Resolve-Path $BackupFile).Path)
