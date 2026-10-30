"""Channel adapters. Distinct LinkedIn / Reddit / GitHub artifacts. Publish is dry-run."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from netie_exposure.claims import assert_clean, find_denied, laptop_ascii
from netie_exposure.drafts import to_markdown
from netie_exposure.refuse import refuse

REDDIT_ALLOWLIST = ("opensource", "selfhosted", "LocalLLaMA", "MachineLearning", "FPGA", "RISCV")

_SUB_FOR_PRODUCT = {
    "openhbm": "RISCV",
    "openforge": "FPGA",
    "analogcrawler": "FPGA",
    "constructor": "LocalLLaMA",
    "cassandra": "MachineLearning",
    "vertex": "opensource",
    "airgpt": "LocalLLaMA",
    "cortex": "LocalLLaMA",
    "space": "selfhosted",
    "openvault": "selfhosted",
    "ci-doctor": "opensource",
}


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


def linkedin_payload(draft: dict[str, Any]) -> dict[str, str]:
    hook = laptop_ascii(str(draft.get("hook") or draft["text"].split("\n", 1)[0]))
    if len(hook) > 210:
        hook = hook[:207] + "..."
    body = laptop_ascii(draft["text"])
    if len(body) > 1300:
        body = body[:1297] + "..."
    tags = ["#OpenSource", "#NetieAI"]
    if draft.get("product_id") == "openhbm":
        tags.append("#RISCV")
    elif draft.get("kind") == "hire":
        tags.append("#Penang")
    else:
        tags.append("#AI")
    return {
        "hook": assert_clean(hook),
        "body": assert_clean(body),
        "hashtags": " ".join(tags[:3]),
        "channel": "linkedin",
    }


def reddit_subreddit(product_id: str | None) -> str:
    if product_id and product_id in _SUB_FOR_PRODUCT:
        sub = _SUB_FOR_PRODUCT[product_id]
        if sub in REDDIT_ALLOWLIST:
            return sub
    return "opensource"


def reddit_payload(draft: dict[str, Any]) -> dict[str, str]:
    title = laptop_ascii(str(draft.get("hook") or draft["text"].split("\n", 1)[0]))[:300]
    body = laptop_ascii(draft.get("reddit_text") or draft["text"])
    body += "\n\nI work on this (affiliation). Not selling anything in the comments."
    sub = reddit_subreddit(draft.get("product_id"))
    return {
        "title": assert_clean(title),
        "selftext": assert_clean(body),
        "subreddit": sub,
        "channel": "reddit",
    }


def github_profile_markdown(catalog: dict[str, Any]) -> str:
    org = catalog["org"]
    lines = [
        f"# {org['name']}",
        "",
        org["description"],
        "",
        f"**{org['tagline']}**",
        "",
        f"- Site: {org['home']}",
        f"- Suite: {org['suite']}",
        f"- Hire: {org['hire']}",
        f"- Constructor: {org['constructor_pages']}",
        f"- Contact: {org['contact_email']}",
        "",
        "## Public repos (star these)",
        "",
    ]
    repos = catalog.get("public_repos") or [
        {
            "name": p["name"],
            "html_url": p.get("github"),
            "description": p.get("blurb", ""),
            "stargazers_count": p.get("stargazers_count") or 0,
        }
        for p in catalog["products"]
        if p.get("github")
    ]
    repos = sorted(repos, key=lambda r: (-int(r.get("stargazers_count") or 0), r["name"]))
    for repo in repos:
        url = repo.get("html_url") or repo.get("github")
        if not url:
            continue
        stars = repo.get("stargazers_count") or 0
        desc = repo.get("description") or ""
        if find_denied(desc):
            desc = ""
        lines.append(f"- **[{repo['name']}]({url})** ({stars} stars) - {desc}".rstrip(" -"))
    lines += [
        "",
        "Laptop apps (AirGPT, Space, Cortex crew) live on the site. No installer there yet.",
        "",
        "Stars are earned with public work. Do not buy them.",
        "",
    ]
    return assert_clean("\n".join(lines))


def write_channel_files(root: Path, draft: dict[str, Any]) -> list[Path]:
    """Write LinkedIn and Reddit variants of one draft into channel folders."""
    written: list[Path] = []
    li_dir = root / "linkedin"
    li_dir.mkdir(parents=True, exist_ok=True)
    li = linkedin_payload(draft)
    li_path = li_dir / f"{draft['id']}.md"
    li_path.write_text(
        assert_clean(
            f"# {draft['id']} (linkedin)\n\n"
            f"status: draft\n"
            f"hashtags: {li['hashtags']}\n\n"
            f"## Hook (<=210 chars)\n\n{li['hook']}\n\n"
            f"## Body (<=1300 chars)\n\n{li['body']}\n"
        ),
        encoding="utf-8",
        newline="\n",
    )
    written.append(li_path)

    rd_dir = root / "reddit"
    rd_dir.mkdir(parents=True, exist_ok=True)
    rd = reddit_payload(draft)
    rd_path = rd_dir / f"{draft['id']}.md"
    rd_path.write_text(
        assert_clean(
            f"# {draft['id']} (reddit)\n\n"
            f"status: draft\n"
            f"subreddit: r/{rd['subreddit']}\n\n"
            f"## Title\n\n{rd['title']}\n\n"
            f"## Selftext\n\n{rd['selftext']}\n"
        ),
        encoding="utf-8",
        newline="\n",
    )
    written.append(rd_path)
    return written
