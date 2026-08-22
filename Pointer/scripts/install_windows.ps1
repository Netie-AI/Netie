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

function Get-PointerPython {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return @{ File = $python.Source; Prefix = @() }
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return @{ File = $py.Source; Prefix = @("-3") }
    }
    throw "Python not found. Install CPython from https://www.python.org/downloads/windows/ then re-run."
}

Write-Host "1. Looking for product Pointer at D:\Pointer"
$product = "D:\Pointer"
if (Test-Path $product) {
    Write-Host "HIT $product (informational). This script still runs the Netie bootstrap at $bootstrap unless you cloned product Pointer here."
} else {
    Write-Host "MISS $product - using Netie bootstrap at $bootstrap"
}

Write-Host "2. Python"
$Py = Get-PointerPython
$pyArgs = @($Py.Prefix)
& $Py.File @pyArgs --version
if ($LASTEXITCODE -ne 0) {
    throw "Python --version failed"
}

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
    $serveArgs = @($Py.Prefix + @("-m", "pointer", "serve"))
    Start-Process -FilePath $Py.File -WorkingDirectory $bootstrap -ArgumentList $serveArgs
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
& $Py.File @($Py.Prefix + @("-m", "pointer", "prove"))
if ($LASTEXITCODE -ne 0) {
    Write-Host "prove failed; still writing pair card. This is P-002 unproven."
}
& $Py.File @($Py.Prefix + @("-m", "pointer", "pair", "--card"))
$desktop = [Environment]::GetFolderPath("Desktop")
if ($desktop) {
    Copy-Item (Join-Path $bootstrap ".pointer-state\PAIR_CARD.txt") (Join-Path $desktop "POINTER_CARD.txt") -Force
    $next = Join-Path $bootstrap ".pointer-state\POINTER_NEXT.txt"
    if (Test-Path $next) {
        Copy-Item $next (Join-Path $desktop "POINTER_NEXT.txt") -Force
    }
    $prove = Join-Path $bootstrap ".pointer-state\PROVE.json"
    if (Test-Path $prove) {
        Copy-Item $prove (Join-Path $desktop "POINTER_PROVE.json") -Force
    }
    $qr = Join-Path $bootstrap "pay\pointer-rm300.png"
    if (Test-Path $qr) {
        Copy-Item $qr (Join-Path $desktop "POINTER_RM300.png") -Force
    }
    Write-Host "desktop copies: POINTER_CARD.txt (no tokens), POINTER_NEXT.txt, POINTER_PROVE.json, POINTER_RM300.png if present"
    Write-Host "Drive-upload Desktop POINTER_PROVE.json only. Do not email tokens."
    $proveDesk = Join-Path $desktop "POINTER_PROVE.json"
    if (Test-Path $proveDesk) {
        Start-Process explorer.exe -ArgumentList "/select,$proveDesk"
    }
}
Write-Host "card: $bootstrap\.pointer-state\PAIR_CARD.txt (gitignored). Do not email tokens."
Write-Host "opening http://127.0.0.1:7420/ (steps) and /pay (Stripe) in the default browser"
Start-Process "http://127.0.0.1:7420/"
Start-Process "http://127.0.0.1:7420/pay"

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
