"""Channel adapters. Draft files. Official APIs only after --approve."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from netie_exposure.drafts import to_markdown
from netie_exposure.refuse import refuse


def write_outbox(outbox: Path, draft: dict[str, Any]) -> Path:
    outbox.mkdir(parents=True, exist_ok=True)
    path = outbox / f"{draft['id']}.md"
    path.write_text(to_markdown(draft), encoding="utf-8", newline="\n")
    return path


def publish(draft: dict[str, Any], *, approved_id: str | None) -> str:
    """Never hits the network. Returns a dry-run note or refuses."""
    if approved_id != draft["id"]:
        refuse("publish_without_approve")
    return (
        f"DRY-RUN approved {draft['id']} for {draft['channel']}. "
        f"Wire LinkedIn/Reddit official APIs here later. No scrape. No fake audience."
    )
