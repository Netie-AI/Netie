# Cited-answer prototype deployment finding

- Date: 2026-08-23 UTC
- Model: computer-use agent
- Scope: Spaceship deployment of the synthetic cited-answer prototype
- Keywords: cited answer, fixed synthetic corpus, no-answer state, Spaceship File Manager, source verification, browser-only
- Main idea: The File Manager upload path reliably published the synthetic cited-answer proof; the live artifact demonstrates both a cited response and a no-answer state without presenting itself as a retrieval backend.

## Verified result

- Created `/hire/knowledge/` through File Manager.
- Uploaded only `/hire/index.html` and `/hire/knowledge/index.html`.
- Tested a cited response for "What blocks closure?" with the synthetic dispatch note.
- Tested an unknown question and saw the explicit no-answer state.
- Left `/hire/ops/`, `/hire/trace/`, and `/hire/assets/` intact.
- Production download of `/hire/knowledge/` matched `docs/knowledge/index.html` byte-for-byte.

## Public boundary

The page uses a fixed local synthetic set and has no file upload, model call, embedding, public retrieval backend, customer data, login, analytics, or network request. It proves a citation and no-answer interaction pattern only.
