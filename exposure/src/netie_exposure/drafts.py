"""Deterministic drafts from the catalog. Every draft carries a source URL."""

from __future__ import annotations

import hashlib
from datetime import date
from typing import Any

from netie_exposure.claims import assert_clean

KINDS = ("hook", "product", "news", "hire", "invite", "github")


def _id(kind: str, key: str, day: str) -> str:
    digest = hashlib.sha256(f"{kind}:{key}:{day}".encode("utf-8")).hexdigest()[:10]
    return f"{day}-{kind}-{digest}"


def _source(item: dict[str, Any]) -> str:
    return item.get("url") or item.get("github") or item.get("proof") or ""


def draft_hook(product: dict[str, Any], day: str) -> dict[str, Any]:
    name = product["name"]
    blurb = product["blurb"]
    url = _source(product)
    hook = f"{name}: {blurb.split('.')[0]}."
    if len(hook) > 210:
        hook = hook[:207] + "..."
    body = (
        f"{hook}\n\n"
        f"{blurb}\n\n"
        f"Source: {url}\n"
        f"Org: https://github.com/Netie-AI\n"
        f"Site: https://netie.ai/"
    )
    return {
        "id": _id("hook", product["id"], day),
        "kind": "hook",
        "channel": "linkedin",
        "product_id": product["id"],
        "hook": assert_clean(hook),
        "text": assert_clean(body),
        "sources": [url],
        "status": "draft",
    }


def draft_product(product: dict[str, Any], day: str) -> dict[str, Any]:
    url = _source(product)
    text = (
        f"New from Netie.AI: {product['name']}\n\n"
        f"{product['blurb']}\n\n"
        f"Open the public page: {url}\n"
        f"GitHub org: https://github.com/Netie-AI"
    )
    if product.get("shipped_installer") is False and product.get("kind") != "oss":
        text += "\n\nNo installer on the marketing site yet. Waitlist / hire / public GitHub only."
    return {
        "id": _id("product", product["id"], day),
        "kind": "product",
        "channel": "linkedin",
        "product_id": product["id"],
        "text": assert_clean(text),
        "sources": [url],
        "status": "draft",
    }


def draft_news(seed: dict[str, Any], product: dict[str, Any], day: str) -> dict[str, Any]:
    url = seed["url"]
    text = (
        f"AI news, tied to a thing we actually shipped:\n\n"
        f"{seed['headline']}\n\n"
        f"Relevant product: {product['name']} - {product['blurb']}\n"
        f"Source: {url}"
    )
    return {
        "id": _id("news", seed["id"], day),
        "kind": "news",
        "channel": "linkedin",
        "product_id": product["id"],
        "text": assert_clean(text),
        "sources": [url, _source(product)],
        "status": "draft",
    }


def draft_hire(offer: dict[str, Any], day: str) -> dict[str, Any]:
    url = offer["url"]
    text = (
        f"Hire (Penang, scoped work - not a SaaS licence):\n\n"
        f"{offer['name']}. {offer['price']}.\n"
        f"Written plan before you pay.\n"
        f"Brief: {url}\n"
        f"Catalog: https://netie.ai/hire/catalog.json\n"
        f"Email: oojianhongg@gmail.com"
    )
    return {
        "id": _id("hire", offer["id"], day),
        "kind": "hire",
        "channel": "linkedin",
        "offer_id": offer["id"],
        "text": assert_clean(text),
        "sources": [url, "https://netie.ai/hire/catalog.json"],
        "status": "draft",
    }


def draft_invite(org: dict[str, Any], day: str) -> dict[str, Any]:
    text = (
        f"{org['tagline']}\n\n"
        f"{org['description']}\n\n"
        f"Laptop apps + waitlist: {org['home']}\n"
        f"Constructor sketch (no login): {org['constructor_pages']}\n"
        f"Suite: {org['suite']}\n"
        f"GitHub: {org['github']}\n"
        f"Hire: {org['hire']}\n\n"
        f"No installer on the site yet. Engine is https://app.netie.ai/cortex . "
        f"Do not invent a constructor hostname."
    )
    return {
        "id": _id("invite", "waitlist", day),
        "kind": "invite",
        "channel": "linkedin",
        "text": assert_clean(text),
        "sources": [org["home"], org["github"], org["constructor_pages"]],
        "status": "draft",
    }


def draft_github(part: dict[str, Any], day: str) -> dict[str, Any]:
    url = part["url"]
    text = (
        f"Cool part (public, star-able):\n\n"
        f"{part['title']}\n"
        f"{part['why']}\n\n"
        f"{url}\n"
        f"Org profile: https://github.com/Netie-AI"
    )
    reddit = (
        f"{part['title']}\n\n{part['why']}\n\n{url}\n\n"
        f"(I work on this. Affiliation disclosed. Not a paid-star market.)"
    )
    return {
        "id": _id("github", part["id"], day),
        "kind": "github",
        "channel": "reddit",
        "text": assert_clean(text),
        "reddit_text": assert_clean(reddit),
        "sources": [url],
        "status": "draft",
    }


def _lead_oss(products: list[dict[str, Any]], rotate: int = 0) -> dict[str, Any] | None:
    with_gh = [p for p in products if p.get("github")]
    if not with_gh:
        return None
    ranked = sorted(
        with_gh,
        key=lambda p: (
            0 if p.get("featured") else 1,
            -int(p.get("stargazers_count") or 0),
            0 if p.get("kind") == "oss" else 1,
            p["id"],
        ),
    )
    return ranked[rotate % len(ranked)]


def render_queue(
    catalog: dict[str, Any],
    *,
    day: str | None = None,
    n: int = 6,
    rotate: int = 0,
) -> list[dict[str, Any]]:
    """Today's mix. rotate walks products/hire so a week is not the same post."""
    day = day or date.today().isoformat()
    products = catalog["products"]
    oss = _lead_oss(products, rotate=rotate)
    laptop = [p for p in products if p.get("kind") in ("laptop", "crew", "canvas", "company")]
    drafts: list[dict[str, Any]] = []
    if laptop:
        drafts.append(draft_hook(laptop[rotate % len(laptop)], day))
    if oss:
        drafts.append(draft_product(oss, day))
    if catalog.get("news_seeds") and oss:
        seed = catalog["news_seeds"][rotate % len(catalog["news_seeds"])]
        match = next((p for p in products if p["id"] == seed["relevant_product"]), oss)
        drafts.append(draft_news(seed, match, day))
    offers = catalog.get("hire_offers") or []
    if offers:
        drafts.append(draft_hire(offers[rotate % len(offers)], day))
    drafts.append(draft_invite(catalog["org"], day))
    parts = catalog.get("cool_parts") or []
    if parts:
        drafts.append(draft_github(parts[rotate % len(parts)], day))
    for item in drafts:
        for src in item["sources"]:
            if not src.startswith("http"):
                raise ValueError(f"draft {item['id']} missing http source")
    return drafts[:n]


def to_markdown(draft: dict[str, Any]) -> str:
    sources = "\n".join(f"- {s}" for s in draft["sources"])
    extra = ""
    if draft.get("hook"):
        extra = f"\n**Hook (first line):** {draft['hook']}\n"
    reddit = ""
    if draft.get("reddit_text"):
        reddit = f"\n## Reddit variant\n\n{draft['reddit_text']}\n"
    return assert_clean(
        f"# {draft['id']}\n\n"
        f"kind: {draft['kind']}\n"
        f"channel: {draft['channel']}\n"
        f"status: {draft['status']}\n\n"
        f"## Sources\n\n{sources}\n"
        f"{extra}\n"
        f"## Body\n\n{draft['text']}\n"
        f"{reddit}"
    )
