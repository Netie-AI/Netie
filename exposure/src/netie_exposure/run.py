"""Execute the Cortex-crew graph. Channel agents fan out in-process. Nobody publishes."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from netie_exposure.catalog import merge_catalog
from netie_exposure.channels import github_profile_markdown, write_channel_files, write_outbox
from netie_exposure.claims import assert_clean
from netie_exposure.crew import ENGINE, NORTH_STAR_LINKEDIN, ROLES, SOCIAL_POSTING
from netie_exposure.drafts import draft_news, render_queue
from netie_exposure.growth import render as render_growth
from netie_exposure.growth import snapshot
from netie_exposure.news import match_product, news_items


def _write(path: Path, body: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(assert_clean(body), encoding="utf-8", newline="\n")
    return path


def run_crew(
    *,
    outbox: Path,
    live: bool = False,
    day: str | None = None,
    followers: int | None = None,
) -> dict[str, Any]:
    """Vanguard -> Cortex -> channel specialists -> Closer + marketing. Posting stays off."""
    day = day or date.today().isoformat()
    catalog = merge_catalog(live=live)
    crew_dir = outbox / "crew"
    crew_dir.mkdir(parents=True, exist_ok=True)

    items = news_items(catalog, live=live)
    catalog["news_live"] = items
    if items:
        top = items[0]
        product = (
            next((p for p in catalog["products"] if p["id"] == top.get("relevant_product")), None)
            or match_product(top["headline"], catalog["products"])
        )
        # Prefer live/seeded news as the queue's news slot by rewriting seeds.
        catalog["news_seeds"] = [
            {
                "id": top["id"],
                "headline": top["headline"],
                "url": top["url"],
                "relevant_product": product["id"],
            }
        ]

    drafts = render_queue(catalog, day=day)
    row = snapshot(
        linkedin_followers=followers,
        github_stars_total=int(catalog.get("github_stars_total") or 0),
        drafts_written=len(drafts),
        target_linkedin=int(catalog["growth"]["linkedin_followers_target"]),
    )

    vanguard = _write(
        crew_dir / "00-vanguard.md",
        "# Vanguard\n\n"
        f"engine: {ENGINE}\n"
        f"live_fetch: {catalog.get('live')}\n"
        f"github_stars_total: {catalog.get('github_stars_total')}\n"
        f"news_items: {len(items)}\n\n"
        "## Growth\n\n"
        f"{render_growth(row)}\n"
        "## Products watched\n\n"
        + "\n".join(f"- {p['name']} {p.get('github') or p['url']}" for p in catalog["products"])
        + "\n",
    )

    ranked = [d["id"] for d in drafts]
    cortex = _write(
        crew_dir / "01-cortex.md",
        "# Cortex (mix)\n\n"
        "Social posting stays off. Ranked draft ids for Closer:\n\n"
        + "\n".join(f"{i+1}. {did}" for i, did in enumerate(ranked))
        + "\n",
    )

    channel_paths: list[Path] = []
    for draft in drafts:
        write_outbox(outbox, draft)
        channel_paths.extend(write_channel_files(crew_dir, draft))

    gh_dir = crew_dir / "github"
    gh_dir.mkdir(parents=True, exist_ok=True)
    profile = _write(gh_dir / "PROFILE.md", github_profile_markdown(catalog))
    show_hn = _write(
        gh_dir / "SHOW_HN.md",
        "# Show HN draft\n\n"
        "Show HN: OpenHBM - open JEDEC HBM4 controller + RISC-V LPU\n\n"
        "https://github.com/Netie-AI/OpenHBM\n\n"
        "Apache-2.0 RTL. Laptop-sim with Verilator. Not a star-market post.\n",
    )

    closer = _write(
        crew_dir / "99-closer.md",
        "# Closer\n\n"
        f"social_posting: {SOCIAL_POSTING}\n"
        f"north_star_linkedin: {NORTH_STAR_LINKEDIN}\n"
        f"drafts: {len(drafts)}\n\n"
        "Nothing is posted. Human next step:\n\n"
        "```\npython -m netie_exposure approve <id>\n```\n\n"
        "Still a dry-run after approve.\n",
    )

    marketing = _write(
        crew_dir / "marketing.md",
        "# Marketing kit (after Cortex-crew)\n\n"
        "This layer combines channel agents. It does not replace Cortex.\n\n"
        f"- LinkedIn files: {crew_dir / 'linkedin'}\n"
        f"- Reddit files: {crew_dir / 'reddit'}\n"
        f"- GitHub profile: {profile}\n"
        f"- Show HN: {show_hn}\n"
        f"- Closer: {closer}\n"
        f"- Vanguard: {vanguard}\n"
        f"- Cortex: {cortex}\n\n"
        "Roles: " + ", ".join(ROLES + ("marketing",)) + "\n",
    )

    return {
        "day": day,
        "drafts": len(drafts),
        "ids": ranked,
        "crew_dir": str(crew_dir),
        "vanguard": str(vanguard),
        "cortex": str(cortex),
        "closer": str(closer),
        "marketing": str(marketing),
        "github_profile": str(profile),
        "channel_files": len(channel_paths),
        "social_posting": SOCIAL_POSTING,
        "engine": ENGINE,
    }
