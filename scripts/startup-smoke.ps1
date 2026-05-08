$ErrorActionPreference = "Stop"

$backendProcess = $null
$frontendProcess = $null

function Get-ShellExecutable {
  $pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
  if ($pwsh) {
    return "pwsh"
  }
  return "powershell.exe"
}

function Wait-HttpReady {
  param(
    [Parameter(Mandatory = $true)][string]$Uri,
    [Parameter(Mandatory = $true)][string]$Label,
    [int]$TimeoutSeconds = 60,
    [int]$IntervalSeconds = 2
  )

  $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
  while ((Get-Date) -lt $deadline) {
    try {
      $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 5
      if ($response.StatusCode -eq 200) {
        return
      }
    } catch {
      # Service not ready yet, keep retrying until deadline.
    }
    Start-Sleep -Seconds $IntervalSeconds
  }

  throw "$Label did not become ready before timeout (${TimeoutSeconds}s)."
}

function Stop-ProcessTree {
  param(
    [Parameter(Mandatory = $false)]
    [System.Diagnostics.Process]$Process
  )

  if ($null -eq $Process) {
    return
  }

  if ($Process.HasExited) {
    return
  }

  # Stoppe aussi les enfants npm/cmd/node afin d'eviter des serveurs Vite orphelins.
  $children = Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $Process.Id }
  foreach ($child in $children) {
    Stop-ProcessTree -Process (Get-Process -Id $child.ProcessId -ErrorAction SilentlyContinue)
  }

  Stop-Process -Id $Process.Id -Force -ErrorAction SilentlyContinue
}

try {
  $shellExecutable = Get-ShellExecutable
  $backendCmd = ".\.venv\Scripts\Activate.ps1; Set-Location backend; python -m uvicorn app.main:app --host 127.0.0.1 --port 8001"
  $backendProcess = Start-Process $shellExecutable -ArgumentList "-NoProfile", "-Command", $backendCmd -PassThru

  Set-Location frontend
  if (!(Test-Path node_modules)) {
    npm ci | Out-Null
  }
  $frontendProcess = Start-Process npm.cmd -ArgumentList "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173" -PassThru
  Set-Location ..

  $timeoutSeconds = 60
  if ($env:STARTUP_SMOKE_TIMEOUT_SECONDS) {
    $timeoutSeconds = [int]$env:STARTUP_SMOKE_TIMEOUT_SECONDS
  }

  Wait-HttpReady -Uri "http://127.0.0.1:8001/health" -Label "Backend health endpoint" -TimeoutSeconds $timeoutSeconds
  Wait-HttpReady -Uri "http://127.0.0.1:5173" -Label "Frontend root endpoint" -TimeoutSeconds $timeoutSeconds

  Write-Output "startup_smoke_ok"
} finally {
  if ($frontendProcess) { Stop-ProcessTree -Process $frontendProcess }
  if ($backendProcess) { Stop-ProcessTree -Process $backendProcess }
}
