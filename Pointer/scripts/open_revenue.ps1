#Requires -Version 5.1
# Open founder cash-path tabs. Does not start Pointer, does not email, does not
# set POINTER_ALLOW_REMOTE. Run on the Windows laptop in a browser the founder
# controls.

$ErrorActionPreference = "Stop"

Write-Host "Opening four cash-path tabs. This is not a $1M claim."
Write-Host "1. Google AI Studio key (store in OpenVault as GOOGLE_API_KEY, not git)"
Start-Process "https://aistudio.google.com/apikey"
Write-Host "2. All Things Agentic Devpost (deadline 31 Aug 2026 17:00 PDT; existing Devpost login)"
Start-Process "https://allthingsagentichackathon.devpost.com/"
Write-Host "3. YC Fall 2026 late apply (no promised decision date)"
Start-Process "https://www.ycombinator.com/apply"
Write-Host "4. Hacker101 authorized training (then H1 signup in the same browser)"
Start-Process "https://www.hacker101.com/"
Write-Host "Do not submit Pointer-as-is to Devpost. Do not write exploits. Do not blast Easyway/Hengxing."
