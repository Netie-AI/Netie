#Requires -Version 5.1
# Verify Pointer on the founder laptop. Does NOT install OpenClaw as a third orchestrator
# unless -FallbackAssistants is passed AND the Pointer daemon cannot start.

param(
    [switch]$FallbackAssistants
)

$ErrorActionPreference = "Stop"
Write-Host "1. Looking for product Pointer at D:\Pointer"
$product = "D:\Pointer"
$bootstrap = Split-Path -Parent $PSScriptRoot
if (Test-Path $product) {
    Write-Host "HIT $product"
} else {
    Write-Host "MISS $product - using Netie bootstrap at $bootstrap"
}

Write-Host "2. Python"
python --version

Write-Host "3. Start daemon on 127.0.0.1:7420 in a new window if not listening"
try {
    $r = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:7420/health -TimeoutSec 2
    Write-Host "daemon already up: $($r.StatusCode)"
} catch {
    Write-Host "daemon down - start with: python -m pointer serve"
    Write-Host "from $bootstrap"
}

Write-Host "4. OpenClaw / Hermes / Ollama (informational)"
foreach ($b in @("ollama", "openclaw", "hermes")) {
    $cmd = Get-Command $b -ErrorAction SilentlyContinue
    if ($cmd) { Write-Host "HIT $b -> $($cmd.Source)" } else { Write-Host "MISS $b" }
}

Write-Host "5. Pair tokens (laptop only, do not commit, do not paste into chat unless pairing a cloud agent)"
Write-Host "   python -m pointer pair --show"

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
