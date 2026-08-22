#Requires -Version 5.1
# Open founder cash-path tabs. Does not start Pointer, does not email, does not
# set POINTER_ALLOW_REMOTE. Run on the Windows laptop in a browser the founder
# controls.

$ErrorActionPreference = "Stop"

Write-Host "Opening cash-path tabs. This is not a $1M claim. A hackathon win is not confirmed."
Write-Host "1. Google AI Studio key (store in OpenVault as GOOGLE_API_KEY, not git)"
Start-Process "https://aistudio.google.com/apikey"
Write-Host "2. All Things Agentic Devpost (deadline 31 Aug 2026 17:00 PDT; existing Devpost login)"
Start-Process "https://allthingsagentichackathon.devpost.com/"
Write-Host "3. Google Cloud $150 hackathon credits (request by 28 Aug 2026 12:00 PT; not guaranteed)"
Start-Process "https://forms.gle/riGhgDSHkHeMx8Ca6"
Write-Host "4. Agentic Cinema Devpost (deadline 9 Sep 2026 14:00 PDT; NEW project, not Pointer-as-is)"
Start-Process "https://agentic-cinema.devpost.com/"
Write-Host "5. YC Fall 2026 late apply (no promised decision date)"
Start-Process "https://www.ycombinator.com/apply"
Write-Host "6. Hacker101 authorized training (then H1 signup in the same browser)"
Start-Process "https://www.hacker101.com/"
Write-Host "After the AI Studio key: store it in OpenVault as GOOGLE_API_KEY, then powershell -File scripts/deploy_hackathon.ps1 with `$env:DEPLOY='1' on a billed GCP project. Dry-run first. Do not set POINTER_ALLOW_REMOTE."
Write-Host "This agent does not auto-join or auto-win. No math/research exam. Do not submit Pointer-as-is. Do not write exploits. Do not blast Easyway/Hengxing."
