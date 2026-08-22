# Operations-board deployment finding

- Date: 2026-08-23 UTC
- Model: computer-use agent
- Scope: Spaceship upload of the synthetic operations-board proof
- Keywords: Spaceship File Manager, Jupiter editor, static upload, operations board, hash verification, browser-only prototype
- Main idea: The Jupiter HTML editor and FTP/SFTP path were unreliable, but the authenticated File Manager upload path successfully deployed the two static files; production downloads matched the committed source byte-for-byte.

## Failure and recovery

The first attempt authenticated to Spaceship and loaded the correct file content into the Jupiter editor, but could not discover a server-save action. FTP and SFTP both returned `530` access denied, and the web picker did not complete.

The retry avoided the editor and transfer protocols:

1. Used Hosting Manager File Manager.
2. Overwrote `/hire/index.html` with the staged source.
3. Created `/hire/ops/`.
4. Uploaded `ops/index.html`.
5. Verified the public hire, operations, and trace pages.

## Production proof

- `https://netie.ai/hire/ops/` returns the committed source byte-for-byte.
- The page labels itself synthetic and browser-only, with no API, login, customer data, integration, production workflow, or deployment claim.
- Browser testing selected a work item and changed its local status successfully.
- `https://netie.ai/hire/trace/` remained live.

Use File Manager upload for later hire-subdirectory static deployments; do not rely on the Jupiter HTML editor as a save path.
