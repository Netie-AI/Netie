# Probe Netie Control. Do not start a second copy.
# Tree: E:\NetieControl (no hyphen). Port 8040. Not paperclip :3100.
# cite: E:\Netie-KB\findings\F-0029.md
$ErrorActionPreference = "Continue"
$Probe = "http://127.0.0.1:8040/healthz"
$Root = "E:\NetieControl"

try {
    $h = Invoke-WebRequest -Uri $Probe -UseBasicParsing -TimeoutSec 3
    if ($h.StatusCode -eq 200 -and $h.Content -match "netie-control") {
        Write-Host "Control already up: $Probe"
        Write-Host $h.Content
        exit 0
    }
} catch { }

Write-Host "Control not answering $Probe"
Write-Host "Working tree is $Root. Writer is netie-controlagent. EXTRA_STOP: do not start a second uvicorn."
Write-Host "Do not clone E:\Netie-Control. Do not start D:\Netie\paperclip :3100."
if (Test-Path $Root) {
    Write-Host "If you ARE that writer: cd $Root; python -m uvicorn netie_control.app:app --host 127.0.0.1 --port 8040"
} else {
    Write-Host "FAIL $Root missing - do not invent a hyphen path"
}
exit 2
