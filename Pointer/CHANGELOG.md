# CHANGELOG

Append-only. Newest first.

## 2026-08-22

- OpenVault org-clone aligned: `pointer/mesh.py` probes TAS Cortex `:8010`, OpenVault mesh Cortex `:8000`, and OpenVault `:5000` independently. Gate still uses `CORTEX_URL` (default 8010). No silent port remap. Gemini planner also accepts OpenVault `GOOGLE_API_KEY`. YC Fall 2026 late-apply pack `docs/YC_FALL_2026.md` (P-018).
- verify.sh now live-probes the hackathon planner HTTP on an ephemeral loopback port. Without GEMINI_API_KEY it must be HTTP 503 + `missing_gemini_key`. `/pay` points at `hackathon/README.md`.
- Hackathon scaffold: `pointer/gemini_planner.py` (google-genai, fail-closed without `GEMINI_API_KEY`, refuses `shell`) plus `hackathon/` Cloud Run wrapper. Still not a submitted Devpost entry. P-017.
- Public pay copy refreshed on litterbox `k99m4f.html` (~72h from 12:52 UTC) so it includes Agentic + Bugcrowd + payouts + r/forhire. QR still `5hdpx8.png`. P-013 still open.
- All Things Agentic hackathon pack: `docs/AGENTIC_HACK.md` plus Drive `1P3E2rf1NSnNUrf454YB6dL5P34ObNv3PmICVu1yb59Y`. Deadline 31 Aug 2026 17:00 PDT. Pointer-as-is is not a valid Gemini/ADK/GCP entry. P-017.
- install_windows.ps1 now opens loopback `/` and `/pay` in the default browser and selects Desktop POINTER_PROVE.json in Explorer. Still no Windows prove file. P-002.
- Wayback save of litterbox pay returned HTTP 523; archive.ph returned 429. P-013 still open.
- Bugcrowd signup pack: `docs/BUGCROWD.md` plus Drive `1k0aHSZTRYeilXjc4CK4AbiyA7sXor2qTusYhg-oRLc4`. Tesla + Mastercard briefs measured HTTP 200. Agent still will not write exploits/PoCs. P-007.
- paste.rs accepted the pay HTML but served `text/plain` (not a buyer host). P-013 still open.
- Reddit r/forhire Pointer paste: `docs/FORHIRE.md` plus Drive `1hP52Fun6L1LQEsxdgU-1E-f60yhXJ45He69tt7WrT4o`. Agent will not post. One post / 7 days; sibling Excel paste already mailed today. P-015.
- MDEC MDAG-AI measured closed (2025-07-18). Not an apply-now path. P-016.
- Stripe payouts phone pack: `docs/STRIPE_PAYOUTS.md` plus Drive `175ocCJoFFaXbbKkHKNyvw0w6AkwEiaix1D527Qf-8Oo`. Linked from `/pay`. Dashboard-only; NRIC stays out of git. P-014.
- Windows prove: SetProcessDpiAwareness so SetCursorPos matches GetCursorPos; `ok` requires screenshot >=100 bytes; targets clamped to screen size. Linux prove still ok=true.
- Laptop phone pack Drive `1by_5VEBbQpD86So-q6K8F2T2MpcHWNkd4BKb4UlARI0` (5 steps, no tokens, branch zip + py -3). Still no POINTER_PROVE.json.
- install_windows.ps1 accepts `python` or `py -3`. `pair --card` writes token-free POINTER_NEXT.txt for Desktop. Product Pointer PRs #26/#27 in Gmail still have no cloneable payloads.
- Cradle CIP Spark phone pack Drive `16kmarL_ZW48KYA0uvQW51-JvwnB7yyKB9ZabmTNoSoA`. GMS register only until a second teammate is named. Do not paste deck 100K traction.
- Public pay copy refreshed on litterbox `q727wl.html` (~72h from 12:41 UTC) so it includes payouts + r/forhire. QR still `5hdpx8.png`. P-013 durable host still open.
- HackerOne signup pack `docs/HACKERONE.md` + Drive `1n5htCeuadHZsU7udormJGiAh-EmigBj3izXWR4NUMD4`. Directory measured public bounties (Vercel Sandbox, Agoda Public, Anthropic). No H1 username yet. Agent still will not write exploits/PoCs.
- Pointer Fiverr phone-paste Drive doc `1CIfusgZvh8yXwucboi1iYpdMhgFHEyFlWEqjY4U_fIs` (USD 70). Wired on `/pay`. Still not a live gig URL. Stripe charges remain 0.
- `python -m pointer prove` writes `.pointer-state/PROVE.json` (no tokens). install_windows.ps1 copies it to Desktop as POINTER_PROVE.json. Linux prove ok on this VM; Windows still unproven.
- Fiverr paste pack `docs/FIVERR_GIG.md` (USD 70 Pointer install). Google sign-in to Fiverr measured; no gig URL yet. Forbids 100K-download claims.
- Drive QR `12HUn5z1C62HwMp144kB_-wvnBom4XIke` (bytes match local PNG). install_windows.ps1 copies card+QR to Desktop.
- Restored `_html` after QR `_png` replace-bug (GET /pay and GET / were empty replies). Vercel `ruma-houser` flags netie.ai/www as misconfigured while apex still LiteSpeed.
- Pointer RM 300 QR at `GET /pay/pointer-rm300.png` (`plink_1U7DHhFV5wcFod2f1pf2kUEs` still active). Drive pay sheet still owner-only.
- Drive pay sheet `1h7H6thuUqyD71MlDyQd0Vbey5ucO30JGM1sSZ_mN4nI` plus HackerOne/Outlier/Bugcrowd links on `/pay`. H1 pays the researcher; Stripe payouts block is NETIE SKUs only. crash.netie.ai still autoindex.
- Laptop pair card: `GET /` + `python -m pointer pair --card`. `live-click` writes `.pointer-state/shots` (Windows-safe; was `/tmp`). install_windows.ps1 now starts serve + live-click. Tokens still not emailed.
- Live SKU `prod_V7SBesawobyQ3x` Pointer laptop install RM 300: https://buy.stripe.com/dRmaEXchg7Wr7nS8D29ws08. Verify now proves gated sandbox write through the daemon.
- Loop tick: verify still 12/12 + live mouse; Stripe MYR 0; no buyer replies; crash.netie.ai still autoindex. Next money path that is actually open: Cradle CIP Spark (gms.cradle.com.my), founder submit only.
- Windows type/hotkey/screenshot wired through `windows_input.py` (SendInput + CopyFromScreen). Unit-tested on Linux; hardware proof still requires the founder laptop.
- Daemon started on this VM at `127.0.0.1:7420`. Stripe live balance remains MYR 0 / 0 charges.
- Bootstrap Pointer daemon in this meta repo: localhost HTTP API, fail-closed gate, hash-chained ledger, Linux live mouse/screenshot via xdotool+ffmpeg.
- Recorded that product `Netie-AI/Pointer` is private and unreachable to this cloud token, while Gmail shows PRs #26 and #27 landing the same day.
- OpenClaw/Hermes checked: not installed here; not installed on this VM on purpose.
