#Requires -Version 5.1
# Fail-closed Cloud Run deploy for All Things Agentic (P-017).
# Does not set POINTER_ALLOW_REMOTE. Does not print the API key.
param()
$ErrorActionPreference = "Stop"
$bootstrap = Split-Path -Parent $PSScriptRoot
Set-Location $bootstrap

if ($env:POINTER_ALLOW_REMOTE -eq "1") {
    Write-Error "refusing: POINTER_ALLOW_REMOTE=1 (loopback Pointer only)"
    exit 1
}

$envName = "GEMINI_API_KEY"
$key = $env:GEMINI_API_KEY
if (-not $key) {
    $envName = "GOOGLE_API_KEY"
    $key = $env:GOOGLE_API_KEY
}
if (-not $key) {
    Write-Error "refusing: set GEMINI_API_KEY or GOOGLE_API_KEY (OpenVault provider google). Not in git."
    exit 1
}

$gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
if (-not $gcloud) {
    Write-Error "refusing: gcloud not on PATH. Install Google Cloud SDK, then gcloud auth login."
    exit 1
}

$region = if ($env:REGION) { $env:REGION } else { "asia-southeast1" }
$service = if ($env:SERVICE) { $env:SERVICE } else { "pointer-hackathon" }
$secret = if ($env:SECRET) { $env:SECRET } else { "pointer-gemini" }

Write-Host "preflight OK. root=$bootstrap region=$region service=$service env=$envName (value not printed)"
Write-Host "GCP service for Devpost: Cloud Run. Pointer daemon stays on 127.0.0.1:7420."
if ($env:DEPLOY -ne "1") {
    Write-Host "Dry run. On the founder machine with billing enabled:"
    Write-Host "  `$env:DEPLOY = '1'"
    Write-Host "  powershell -File scripts/deploy_hackathon.ps1"
    Write-Host "Not a `$1M claim. Individual/Hobbyist is USD 10k x2."
    exit 0
}

$tmp = Join-Path $env:TEMP "pointer-gemini.secret"
Set-Content -Path $tmp -Value $key -NoNewline
try {
    gcloud secrets describe $secret 2>$null
    if ($LASTEXITCODE -eq 0) {
        gcloud secrets versions add $secret --data-file=$tmp
    } else {
        gcloud secrets create $secret --data-file=$tmp
    }
    gcloud run deploy $service --source $bootstrap --dockerfile hackathon/Dockerfile --region $region --set-secrets "${envName}=${secret}:latest" --no-allow-unauthenticated
} finally {
    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
}
Write-Host "Next: GET /health on the .run.app URL must be 200, then submit https://allthingsagentichackathon.devpost.com/"
Write-Host "Do not set POINTER_ALLOW_REMOTE=1."
