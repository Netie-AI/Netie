# Exposure crew

Canonical prompts live with the public pack: [`../../exposure/AGENTS.md`](../../exposure/AGENTS.md)

Run the crew:

```
python -m netie_exposure run
```

Contract: `exposure/crew.yaml`. Cortex is the only engine. Social posting stays off
until `python -m netie_exposure approve <id>` or `auto --grant-auto` plus
official tokens (`TOKENS.md`). Chat grant is not OAuth.
