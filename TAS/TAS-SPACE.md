# TAS-SPACE - Netie Space technical architecture

**Plane:** 4 (application) · **Repo:** `Netie-AI/Space` · `D:\Space`
**Measured:** 2026-08-02. Every claim below was verified against code, not documentation.

---

## 1. What it is

A C#/WPF Windows desktop app that turns the Space key - in File Explorer or on the
Desktop - into a Quick Look style preview, with PDF/video/image editing, format
conversion, OCR, and an optional AI chat over the previewed file.

**It is not "DMS Spaces".** DMS Spaces are ACL-scoped sandboxes over warehouse data.
These two share a word and nothing else, and the collision already causes confusion in
cross-repo docs. Renaming one of them is worth doing before a third person joins.

---

## 2. Entry points

| Path | Role |
|---|---|
| `NetieSpace.sln` -> `src/NetieSpace/NetieSpace.csproj` | net8.0-windows, WinExe, UseWPF |
| `src/NetieSpace/App.xaml.cs` | WPF Application, tray icon, global keyboard hook, OpenVault key sync at `:865` |
| `src/NetieSpace/Views/PreviewWindow.xaml.cs` | the preview surface |
| `NetieSpace.exe --preview "<path>"` | CLI, used by the AirGPT plugin manifest |
| `scripts/publish.ps1` -> `installer/NetieSpace.iss` | Inno Setup installer build |
| `license-api/` | a separate Cloudflare Worker for register/activate/device-bind |

Shipped artifact: `dist/NetieSpace/NetieSpace.exe`, **194,269,001 bytes**, self-contained
single-file win-x64.

---

## 3. What is genuinely shipped

This is the most product-complete surface in the estate, and that deserves saying plainly.

- **Preview engine** - PDF via bundled pdf.js in WebView2; Word via mammoth HTML with an
  OpenXML fallback carrying KaTeX/OMML math; PowerPoint via `PptxSlideImageService`.
- **Explorer and Desktop selection resolution** - `ExplorerFileService.cs` (46 KB):
  ShellWindows coclass, `IShellFolderView`, UI Automation for the desktop, with an
  explicit refusal to fall through from a desktop context to an Explorer window.
- **PDF operations** - `PdfEditService.cs` (30 KB) on PdfSharpCore + PdfPig: merge,
  split, extract, organize, rotate, reverse, signature stamp with drag placement.
- **OCR** - local Tesseract first, cloud second.
- **Video** - `FfmpegService.cs` (29 KB), background export, Whisper auto-captions with
  SRT burn-in.
- **Chat** - per-document threads that survive reopen, `DitchContext` history tiering
  (12,000 char default budget), and a conversation cache so an identical question on the
  same excerpt costs zero tokens.
- **Distribution** - Inno Setup with `PrivilegesRequired=lowest`, optional startup key.

---

## 4. Trust boundaries - the section that matters

| Boundary | Enforced by |
|---|---|
| Embedding consent | **ENFORCED** - UI gate (`EmbeddingConsentWindow`), and `LocalEmbeddingBrain` never uploads |
| Leave-machine gate on the AI path | **NOTHING ENFORCES IT** |
| Baidu cloud OCR | **NOTHING ENFORCES IT** |
| Key custody | **PARTIAL** - see below |
| License gate | **DISABLED IN SHIPPED CONFIG** (`appsettings.json`, `License.SkipGate = true`) |
| Repo invariants | **NONE** - `CLAUDE.md` Hard rules reads "None recorded yet". No CI, no test project |

### The constitution conflict

`NETIE.md` tells a customer: *"Your data does not leave your machine unless you say it
can."* Three paths in this app contradict that today.

**1. The primary AI path has no gate.** `AiService.ChatAsync` / `SummarizeAsync` build
messages containing the previewed document's text and POST them directly to Groq,
Gemini, SEA-LION or OpenRouter. OpenVault - which owns the leave-machine decision for the
whole estate - is not consulted. Cortex escalation exists at `AiService.cs:167-172` but
is *conditional and soft-fail*: four conditions must all hold, and failure falls back to
the direct provider call.

**2. Baidu OCR uploads the image.** `ImageOcrService.cs:113-163` base64-encodes the whole
image file and POSTs it to `aip.baidubce.com` whenever Baidu env keys exist and local
Tesseract returned fewer than 20 characters (`:26-29`). The trigger is *poor local OCR
quality* - so the worse the local read, the more likely the document leaves the machine,
with no prompt.

**3. Keys are stored in plaintext.** `EnvLoader.cs:58` writes `GOOGLE_AISTUDIO_FREE`,
`GROQ_API_KEY`, `OPENROUTER_API_KEY` and `SEA_LION_API_KEY` to
`%LOCALAPPDATA%\NetieSpace\user.env` in cleartext. `OpenVaultKeySync` treats OpenVault as
the source of truth in its docstring but reveals each secret in cleartext at `:100`,
`:315-325` and persists all four locally.

**4. Credential harvesting.** `OpenVaultKeySync.ResolveLoginCredentialsAsync` (`:220-294`)
reads `NETIE_SPACE_EMAIL` / `NETIE_SPACE_PASSWORD` from OpenVault, and **if that fails,
scans the local `PasswordVaultService` for any matching entry.** A fallback that searches
a local credential store is a different security posture from one that fails closed, and
it is not documented anywhere.

None of these is necessarily wrong as an engineering decision. All four are wrong as
*undisclosed* decisions, given what the constitution promises. Each needs either a gate,
or a visible disclosure, or a correction to `NETIE.md`.

---

## 5. Data stores

| Store | Location | Note |
|---|---|---|
| `user.env` | `%LOCALAPPDATA%\NetieSpace\` | **plaintext API keys** |
| `.netie-brain` | `%LOCALAPPDATA%\NetieSpace\` | local embeddings, consent-gated, never uploaded |
| `DocumentChatStore` | per-document threads keyed on a path fingerprint | survives reopen |
| `PasswordVaultService` | DPAPI-backed (`ProtectedData`) | the one store done properly |
| `LicenseStore` | on-device token sealed with a device fingerprint | gate currently skipped |

Plus `SummaryCache`, `ConversationMemoryCache`, `PreviewConversionCache`,
`LocalRedisStore`, `UsageFootprintStore`, `SignatureLibrary`.

---

## 6. Dependencies

- **OpenVault** (`:5000`) via `OpenVaultKeySync.cs` - key sync and login credentials
- **Cortex** (`:8010`) via `CortexClient.cs` - conditional escalation only
- **AirGPT** via `AirGptChatSync.cs` and the plugin manifest
- External model providers **directly**: Groq, Gemini, SEA-LION, OpenRouter
- External OCR: Baidu
- Local binaries: Tesseract, FFmpeg, LibreOffice (PowerPoint), Whisper

---

## 7. Structure problems

1. **No CI and no tests.** No `.github` directory. `tests/` holds only preview fixtures.
   A 194 MB shipped binary with no automated check on it.
2. **`CLAUDE.md` Hard rules is empty** - so an agent working here has no invariant to
   respect. The leave-machine posture is the obvious first entry.
3. **The name collision with DMS Spaces.**
4. **License gate disabled in the shipped config**, which is either intentional
   pre-launch or an accident that ships the product for free. It is not written down
   which.

---

## 8. Verify

```powershell
dotnet build D:\Space\NetieSpace.sln -c Release
powershell -File D:\Space\scripts\publish.ps1
```

There is no test command, because there are no tests. That is the single most useful
thing to change about this repo.

Portable contract in this Netie repo (Space remote still 404): `scripts/space_leave.py`.
AI/OCR leave without OpenVault `allowed=true` is denied. `user.env` / `.env` / `env.local` key writes are denied even when not marked plaintext. Local credential-store scan is denied. `python3 scripts/test_space_leave.py`.

---

## 9. Honest summary

Space is the most finished *product* in the estate and the least governed *repo*. It has
a real installer, a real feature set, and a real user experience - and no CI, no tests, no
recorded invariants, and four undisclosed data-egress paths that contradict the
constitution's central promise.

The gap is not capability. It is that nothing here is checkable, so nothing here can be
claimed.
