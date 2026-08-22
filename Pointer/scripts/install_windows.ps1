#Requires -Version 5.1
# Start Pointer on the founder laptop. Does NOT install OpenClaw as a third orchestrator
# unless -FallbackAssistants is passed AND the Pointer daemon cannot start.

param(
    [switch]$FallbackAssistants
)

$ErrorActionPreference = "Stop"
$bootstrap = Split-Path -Parent $PSScriptRoot
Set-Location $bootstrap
$env:PYTHONPATH = $bootstrap
$env:POINTER_BIND = "127.0.0.1"

Write-Host "1. Looking for product Pointer at D:\Pointer"
$product = "D:\Pointer"
if (Test-Path $product) {
    Write-Host "HIT $product"
} else {
    Write-Host "MISS $product - using Netie bootstrap at $bootstrap"
}

Write-Host "2. Python"
python --version

Write-Host "3. Daemon on 127.0.0.1:7420"
$up = $false
try {
    $r = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:7420/health -TimeoutSec 2
    if ($r.StatusCode -eq 200) { $up = $true }
} catch {
    $up = $false
}
if ($up) {
    Write-Host "daemon already up"
} else {
    Write-Host "starting python -m pointer serve (loopback only)"
    Start-Process -FilePath "python" -WorkingDirectory $bootstrap -ArgumentList "-m","pointer","serve"
    for ($i = 0; $i -lt 20; $i++) {
        Start-Sleep -Milliseconds 400
        try {
            $r = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:7420/health -TimeoutSec 2
            if ($r.StatusCode -eq 200) { $up = $true; break }
        } catch {
            $up = $false
        }
    }
}
if (-not $up) {
    throw "daemon did not become healthy on http://127.0.0.1:7420/health"
}

Write-Host "4. Prove hardware then write pair card (no tokens in this window)"
python -m pointer prove
if ($LASTEXITCODE -ne 0) {
    Write-Host "prove failed; still writing pair card. This is P-002 unproven."
}
python -m pointer pair --card
$desktop = [Environment]::GetFolderPath("Desktop")
if ($desktop) {
    Copy-Item (Join-Path $bootstrap ".pointer-state\PAIR_CARD.txt") (Join-Path $desktop "POINTER_CARD.txt") -Force
    $prove = Join-Path $bootstrap ".pointer-state\PROVE.json"
    if (Test-Path $prove) {
        Copy-Item $prove (Join-Path $desktop "POINTER_PROVE.json") -Force
    }
    $qr = Join-Path $bootstrap "pay\pointer-rm300.png"
    if (Test-Path $qr) {
        Copy-Item $qr (Join-Path $desktop "POINTER_RM300.png") -Force
    }
    Write-Host "desktop copies: POINTER_CARD.txt (no tokens), POINTER_PROVE.json, POINTER_RM300.png if present"
}
Write-Host "card: $bootstrap\.pointer-state\PAIR_CARD.txt (gitignored). Do not email tokens."
Write-Host "open http://127.0.0.1:7420/ for the same 5 steps"

Write-Host "5. OpenClaw / Hermes / Ollama (informational; not Cortex)"
foreach ($b in @("ollama", "openclaw", "hermes")) {
    $cmd = Get-Command $b -ErrorAction SilentlyContinue
    if ($cmd) { Write-Host "HIT $b -> $($cmd.Source)" } else { Write-Host "MISS $b" }
}

if ($FallbackAssistants) {
    Write-Host "Fallback requested. NETIE.md: these are assistants, not Cortex."
    if (Get-Command ollama -ErrorAction SilentlyContinue) {
        Write-Host "Run on the laptop, interactively:"
        Write-Host "  ollama launch openclaw"
        Write-Host "  ollama launch hermes"
    } else {
        Write-Host "Install Ollama from https://ollama.com then re-run."
    }
}
