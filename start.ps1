# One click: make sure Docker is running, build and start the stack, wait until the desk answers, open the browser.
# Run by start.cmd (double-click). First run: ~10 minutes (image build + embedding 15,000 incidents). Later runs: seconds.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
function Say($m) { Write-Host ("[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m) }

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Say "Docker is not installed. Install Docker Desktop: https://www.docker.com/products/docker-desktop/ then run start.cmd again."
  Read-Host "Press Enter to close"; exit 1
}
docker info *> $null
if ($LASTEXITCODE -ne 0) {
  # machine-wide or per-user install, or wherever docker.exe lives (...\resources\bin\docker.exe -> ...\Docker Desktop.exe)
  $cli = (Get-Command docker).Source
  $dd = @("$env:ProgramFiles\Docker\Docker\Docker Desktop.exe", "$env:LOCALAPPDATA\Programs\DockerDesktop\Docker Desktop.exe",
          (Join-Path (Split-Path (Split-Path (Split-Path $cli))) "Docker Desktop.exe")) | Where-Object { Test-Path $_ } | Select-Object -First 1
  if ($dd) { Say "Starting Docker Desktop ($dd)..."; Start-Process $dd } else { Say "Start Docker Desktop, then run start.cmd again."; Read-Host "Press Enter"; exit 1 }
  $ok = $false
  foreach ($i in 1..60) { Start-Sleep 3; docker info *> $null; if ($LASTEXITCODE -eq 0) { $ok = $true; break } }
  if (-not $ok) { Say "Docker did not start within 3 minutes. Open Docker Desktop yourself, then run start.cmd again."; Read-Host "Press Enter"; exit 1 }
}
Say "Docker is running."
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env"; Say "Created .env (fixture model, no API key needed)." }

Say "Building and starting the stack (docker compose up -d --build)..."
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { Say "docker compose failed - see the messages above."; Read-Host "Press Enter"; exit 1 }

Say "Waiting for ingest (first run embeds 15,000 incidents; progress below)..."
$last = ""
foreach ($i in 1..360) {
  try { $r = Invoke-WebRequest -UseBasicParsing "http://localhost:8180/health" -TimeoutSec 4; if ($r.StatusCode -eq 200) { break } } catch { }
  $line = (docker compose logs --no-log-prefix --tail 1 ingest 2>$null | Select-Object -Last 1)
  if ($line -and $line -ne $last) { Say ("  ingest: " + $line.Substring(0, [Math]::Min(150, $line.Length))); $last = $line }
  $state = docker compose ps -a --format "{{.Service}} {{.State}} {{.ExitCode}}" 2>$null | Select-String "^ingest exited (\d+)"
  if ($state -and $state.Matches[0].Groups[1].Value -ne "0") { Say "ingest failed - run: docker compose logs ingest"; Read-Host "Press Enter"; exit 1 }
  Start-Sleep 5
}
Say "The Knowledge Desk is up: http://localhost:8180"
Start-Process "http://localhost:8180"
