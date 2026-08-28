# TAS-POINTER - Pointer technical architecture

**Plane:** 4 (computer control) · **Repo:** `Netie-AI/Pointer` (this token: not found)
**Measured:** 2026-08-27 from `NETIE.md` and founder inventory, **not** from a Pointer checkout. Tool-for-tool vs UACC is UNVERIFIABLE.

---

## 1. What it is

The hands and eyes: an Electron tray client that sees a screen region, takes an instruction, and executes clicks/types as a coworker rather than a macro. Holds no keys. Trusts nothing on screen. Sends intents to Cortex and executes what comes back, fail-closed.

**Is not:** a second orchestrator, UACC itself, Perplexity Computer, or a billing bypass into Cursor/Claude Code.

---

## 2. Entry points (founder inventory)

| Claim | Status |
|---|---|
| Electron tray, Ctrl+Space, crop a region, instruct | founder table; not cloned |
| ~216 files, 120 JS/TS | founder table |
| Was NetieClicks / `jian-hong/NetieClicks` | `NETIE.md` |
| Founder: "not working as expected" | treat as broken until HEAD is green |

---

## 3. vs Perplexity Computer and UACC

| Analogue | License | Job | Pointer |
|---|---|---|---|
| Perplexity Computer | closed | hosted computer-use agent | not a host; local tray |
| `uacc` (PyPI, MCP, ~68 tools) | open MCP server | pixel/a11y desktop tools for any agent | should be *optional hands* behind Cortex `tool_runner`, not a second brain |
| `e2b-dev/open-computer-use` | Apache-2.0 | sandboxed desktop | different threat model (cloud VM vs operator laptop) |

Fail-closed click contract in this repo (Pointer still 404): `scripts/pointer_click.py`. Unlabeled or unknown-role elements do not click. Password / OTP / cookie fields do not click even when labeled. No Cortex intent, no click. The file does not mention API keys or `os.environ`.

MCP wrap of UACC 1.1.0's **68** public tool names: `scripts/pointer_hands.py`. Cortex must allow the name. Planner / workflow / memory / `get_action_history` / clipboard / `browser_execute_js` / ungated `open_url` refuse. Screenshot / snapshot / screen-diff / `detect_elements_visual` / `get_screen_info_enhanced` / `vlm_locate_element` need a labeled non-secret crop (`screenshot_uncropped` otherwise). `browser_get_page_info`, `list_processes`, and `get_system_info` refuse. Hover/drag/`wait_for_element` reuse fail-closed click. `hotkey` / `scroll` / `paint_image` / `paint_preset` on a password/OTP field refuse (uncropped paint refuses). We do not import `uacc`. `python3 scripts/test_pointer_click.py` and `python3 scripts/test_pointer_hands.py`. Not a UACC clone.

---

## 4. Trust boundaries (constitution)

| Boundary | Required | Verified on HEAD |
|---|---|---|
| No keys in the tray | yes | UNVERIFIABLE |
| Cortex decides the intent | yes | UNVERIFIABLE |
| Fail closed on ambiguous UI | yes | UNVERIFIABLE |
| Leave-machine via OpenVault | yes | UNVERIFIABLE |

---

## 5. Verify

```
NEEDS-YOU TAS-POINTER  add Netie-AI/Pointer to this environment
```

Then: a tool-for-tool matrix against UACC, a fail-closed test (refuse to click unlabeled), and a proof the tray never reads `env.local`.
