# Estate watchdog -- launch only, not an orchestrator.
# Keeps Plane + Cortex-crew :8020 alive. Does not auto-start Grok Bot.
# Refreshes RUNTIME.md from live gh. Does not implement tickets.
$ErrorActionPreference = "Continue"
$Netie = "D:\Netie"
$Runtime = Join-Path $Netie "Internal\Agents\RUNTIME.md"
$PlaneRoot = "D:\plane-selfhost"
$PlaneApp = Join-Path $PlaneRoot "plane-app"
$Stamp = Get-Date -Format "yyyy-MM-dd HH:mm"

function PlaneUp {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8099/api/instances/" -UseBasicParsing -TimeoutSec 4
        return $r.StatusCode -eq 200
    } catch { return $false }
}

$notes = @()

$nw = "D:\Cortex-crew\scripts\night_watch.ps1"
if (Test-Path $nw) {
    try {
        & $nw -SkipEstate
        $notes += "night_watch -SkipEstate"
    } catch {
        $notes += "night_watch failed: $($_.Exception.Message)"
    }
}

docker info 1>$null 2>$null
if ($LASTEXITCODE -ne 0) {
    $dd = "$env:ProgramFiles\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dd) { Start-Process $dd; $notes += "started Docker Desktop" }
}

if (-not (PlaneUp)) {
    if (Test-Path (Join-Path $PlaneApp "docker-compose.yaml")) {
        Push-Location $PlaneApp
        docker compose --env-file plane.env -f docker-compose.yaml up -d 1>$null 2>$null
        Pop-Location
        $notes += "compose up Plane"
    }
    $until = (Get-Date).AddMinutes(2)
    while (-not (PlaneUp) -and (Get-Date) -lt $until) { Start-Sleep 5 }
}

$plane = if (PlaneUp) { "up" } else { "DOWN" }
$notes += "Plane $plane"

# Grok Bot is offloaded to Cortex-crew. Watchdog must not relaunch the xAI app.
$grok = Get-Process -Name "Grok Bot" -ErrorAction SilentlyContinue
$grokState = if ($grok) {
    "manual pids=$($grok.Id -join ',') (watchdog will not restart it)"
} else {
    "OFFLOADED -> http://127.0.0.1:8020/ (Cortex-crew)"
}
$notes += "Grok Bot auto-start off"

$ncState = "DOWN"
try {
    $nc = Invoke-WebRequest -Uri "http://localhost:3100/api/health" -UseBasicParsing -TimeoutSec 2
    if ($nc.StatusCode -eq 200) { $ncState = "up GET /api/health" }
} catch { }

if ($ncState -notmatch "^up") {
    if ($env:NETIE_CONTROL -eq "1") {
        $paperclip = "D:\Netie\paperclip"
        if (Test-Path (Join-Path $paperclip "package.json")) {
            $pnpm = "npx pnpm"
            if (Get-Command pnpm -ErrorAction SilentlyContinue) { $pnpm = "pnpm" }
            if (-not (Test-Path (Join-Path $paperclip "node_modules"))) {
                $notes += "Control needs pnpm install in paperclip (run once)"
            } else {
                Start-Process -FilePath "cmd.exe" -ArgumentList @(
                    "/c", "cd /d `"$paperclip`" && $pnpm dev"
                ) -WorkingDirectory $paperclip -WindowStyle Minimized
                $notes += "started Netie Control $pnpm dev :3100"
                Start-Sleep 12
                try {
                    $nc2 = Invoke-WebRequest -Uri "http://localhost:3100/api/health" -UseBasicParsing -TimeoutSec 4
                    if ($nc2.StatusCode -eq 200) { $ncState = "up GET /api/health" }
                } catch { }
            }
        }
    } else {
        $notes += "Control GATED (set NETIE_CONTROL=1 to boot)"
    }
}

$freeMB = 0
try {
    $os = Get-CimInstance Win32_OperatingSystem
    $freeMB = [int]($os.FreePhysicalMemory / 1024)
} catch { }
$lowRam = ($freeMB -gt 0 -and $freeMB -lt 512)
if ($lowRam) { $notes += "RAM ${freeMB}MB; skip gh/gate this tick (keep-alive only)" }

$ghLines = @()
if ($lowRam) {
    $ghLines = @("- skipped (paging file / RAM ${freeMB}MB)")
} else {
    try {
        $dms = gh issue list --repo Netie-AI/dms --state open --limit 5 --json number,title,state 2>$null | ConvertFrom-Json
        $crx = gh issue list --repo Netie-AI/Cortex --state open --limit 5 --json number,title,state 2>$null | ConvertFrom-Json
        foreach ($i in @($dms)) { $ghLines += "- dms#$($i.number) $($i.title)" }
        foreach ($i in @($crx)) { $ghLines += "- Cortex#$($i.number) $($i.title)" }
    } catch {
        $ghLines = @("- gh list failed (not SoT; retry next tick)")
    }
}
if (-not $ghLines) { $ghLines = @("- no open issues returned") }

$claude = if (Get-Command claude -ErrorAction SilentlyContinue) { "claude.exe on PATH" } else { "claude.exe MISSING" }
$cursorAgent = if (Get-Command cursor-agent -ErrorAction SilentlyContinue) { "cursor-agent on PATH" } else { "cursor-agent MISSING (Cursor chat / Cortex-crew :8020)" }

$padLines = @()
try {
    $pads = claude agents --json 2>$null | ConvertFrom-Json
    foreach ($p in @($pads)) {
        $padLines += "- $($p.name) pid=$($p.pid) $($p.kind) cwd=$($p.cwd)"
    }
} catch { $padLines = @("- claude agents --json failed") }
if (-not $padLines) { $padLines = @("- no live Claude pads") }

$prLines = @()
if ($lowRam) {
    $prLines = @("- skipped (low RAM)")
} else {
    try {
        foreach ($repo in @("Netie-AI/dms", "Netie-AI/Cortex")) {
            $prs = gh pr list --repo $repo --state open --limit 6 --json number,title,headRefName 2>$null | ConvertFrom-Json
            foreach ($pr in @($prs)) {
                $who = if ($pr.headRefName -like "cursor/*") { "Cursor-cloud" } elseif ($pr.headRefName -like "worktree-*") { "Claude-worktree" } else { "mixed" }
                $prLines += "- $repo #$($pr.number) [$who] ``$($pr.headRefName)`` $($pr.title)"
            }
        }
    } catch { $prLines = @("- gh pr list failed") }
}
if (-not $prLines) { $prLines = @("- no open PRs returned") }

function HttpOk([string]$Url) {
    try {
        $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 4
        return ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300)
    } catch { return $false }
}
$crewState = if (HttpOk "http://127.0.0.1:8020/crew/health") { "up" } else { "DOWN (night_watch launches)" }
$ovState = if (HttpOk "http://127.0.0.1:5000/api/healthz") { "up" } else { "DOWN (night_watch launches)" }
$engineState = if (HttpOk "http://127.0.0.1:8010/api/engine/activity") { "up" } else { "DOWN (ANS checkout owns :8010)" }

# Netie-KB skill registry :8030 - keep alive + pull (R-0016). Estate service, not a desktop app (R-0015).
$env:GIT_TERMINAL_PROMPT = "0"
git -C "D:\Netie-KB" pull --ff-only --quiet 2>$null
if ($LASTEXITCODE -eq 0) { $notes += "KB pulled" } else { $notes += "KB pull skipped (offline or diverged)" }
$ssUp = HttpOk "http://127.0.0.1:8030/healthz"
if (-not $ssUp) {
    Start-Process -FilePath "python" -ArgumentList @("D:\Netie-KB\scripts\skill_server.py", "--host", "127.0.0.1", "--port", "8030") -WindowStyle Hidden
    Start-Sleep 3
    $ssUp = HttpOk "http://127.0.0.1:8030/healthz"
    $notes += "started skill server :8030"
}
$ssState = if ($ssUp) { "up" } else { "DOWN" }

$pointerProc = Get-Process -Name "Pointer","NetieClicks","electron" -ErrorAction SilentlyContinue | Where-Object { $_.Path -match "Pointer|NetieClicks" }
$pointerState = if ($pointerProc) { "up pids=$($pointerProc.Id -join ',')" } else { "DOWN (no unattended laptop control)" }

$prd = if (Test-Path "$env:USERPROFILE\.claude\agents\prd-agent.md") { "deployed" } else { "MISSING" }
$epic = if (Test-Path "$env:USERPROFILE\.claude\agents\epic-agent.md") { "deployed" } else { "MISSING" }
$tr = if (Test-Path "$env:USERPROFILE\.claude\agents\ticket-runner.md") { "deployed" } else { "MISSING" }
$guaca = if (Test-Path "D:\Cortex\guaca") { "cloned, not the loop" } else { "missing" }
$rakazo = if (Test-Path "D:\Cortex\rakazo") { "cloned, not the loop" } else { "missing" }

$sync = Join-Path $PlaneRoot "sync_holds_view.py"
if (Test-Path $sync) {
    try {
        $syncOut = python $sync 2>&1 | Out-String
        $notes += $syncOut.Trim()
    } catch { $notes += "plane-view failed" }
}

$gate = Join-Path $Netie "Internal\Agents\estate_gate.py"
$gateLine = "gate not run"
if ($lowRam) {
    $gateLine = "GATE skipped this tick (RAM ${freeMB}MB / paging file). Keep-alive still ran."
    $notes += $gateLine
} elseif (Test-Path $gate) {
    $gateOut = python $gate check 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        $gateLine = ($gateOut -split "`n" | Where-Object { $_ -match "GATE|SNAPSHOT|CLAIMS|PANEL|COMPARE" }) -join " | "
    } else {
        $tail = ($gateOut -split "`n" | Select-Object -Last 4) -join " "
        $gateLine = "GATE retry next tick (gh/plane flake). $tail"
    }
    $notes += $gateLine.Trim()
}

$body = @"
# RUNTIME (generated $Stamp) -- not ticket law

**SoT:** GitHub Issues. **Loop:** AGENT_SYSTEM.md + CURSOR_CLAUDE_GROK_RULES.md
**Watchdog:** launch only. One writer per branch.
**Locks:** ``Internal/Agents/FLEET.md`` (roster) + CLAUDE_SYNC.md (pads) + GROK_SYNC.md (Grok).
**Coordinator:** this file + Plane view. Do not triple-ping CI in chat.

## Gate

$gateLine

## Alive

- Plane: $plane  http://localhost:8099/netie/
- Grok Bot: $grokState
- Crew offload: http://127.0.0.1:8020/  (golden D:\Cortex-crew)
- Crew: $crewState  http://127.0.0.1:8020/
- OpenVault API: $ovState  http://127.0.0.1:5000/api/healthz
- Cortex engine: $engineState  http://127.0.0.1:8010/
- Skill registry: $ssState  http://127.0.0.1:8030/  (Netie-KB R-0016; MCP /mcp + REST; kb_search before re-deriving)
- Netie Control: $ncState  http://localhost:3100/api/health (GATED unless NETIE_CONTROL=1)
- Claude Code CLI: $claude
- Cursor agent CLI: $cursorAgent
- Pointer app: $pointerState
- PRD / Epic / Ticket Runner: $prd / $epic / $tr
- Gating: estate_gate.py. PR Bot + Decision: FLEET.md. Marketing: MARKETING.md. Money: MONEY_LANE.md
- Guaca: $guaca. Rakazo: $rakazo. Do not pnpm-app them as the loop.

## Live Claude pads (``claude agents --json``)

$($padLines -join "`n")

## Open (live gh, may lag STATUS.md)

$($ghLines -join "`n")

## Open PRs (writer guess from branch name)

$($prLines -join "`n")

## Who does what this tick

- Locks: read ``D:\Netie\Internal\Agents\CLAIMS.json`` then FLEET.md. EXTRA_STOP/HELD = different ticket. Panel: snapshots/panel.html
- Grok Bot: OFFLOADED to Cortex-crew. Do not auto-start. Judgement / verify = this Cursor session or Crew Manager. dms #61 HELD. Cortex#42 skipped. Cortex#45 same writer only. Do not clone onto the Grok box.
- Claude Code: pad locks in CLAUDE_SYNC.md. ``/ticket-runner`` is manager. Extra Cortex pads do not write.
- Cursor: this laptop for Internal. Cloud Cortex only on a new unused branch. Do not dual-write.

## Next human

Do not auto-start Grok Bot. Use Cortex Crew http://127.0.0.1:8020/ . Desktop **Plane Netie** for the board. Password in ``D:\plane-selfhost\ADMIN.local.txt``.
Pointer laptop control stays human-confirmed. Do not ask it to drain Claude unattended.

## Watchdog notes

$($notes -join "; ")
"@

New-Item -ItemType Directory -Force -Path (Split-Path $Runtime) | Out-Null
Set-Content -Path $Runtime -Value $body.TrimEnd() -Encoding utf8
Write-Host "RUNTIME $Runtime Plane=$plane Grok=$grokState Crew=http://127.0.0.1:8020/"
