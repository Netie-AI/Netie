"""Live AI news (HN) plus frozen seeds. Cassandra stays a research note, not a trade."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from netie_exposure.catalog import USER_AGENT

HN_URL = (
    "https://hn.algolia.com/api/v1/search"
    "?query=LLM&tags=story&hitsPerPage=20"
)

_TITLE_NEEDLES = (
    "ai",
    "llm",
    "gpt",
    "model",
    "gpu",
    "hbm",
    "openai",
    "anthropic",
    "nvidia",
    "agent",
    "open source",
    "riscv",
    "risc-v",
    "semiconductor",
)


def _title_is_ai_news(title: str) -> bool:
    t = title.lower()
    for k in _TITLE_NEEDLES:
        if " " in k:
            if k in t:
                return True
            continue
        if k == "ai":
            if re.search(r"\bai\b", t):
                return True
            continue
        if k in t:
            return True
    return False


def usable_story(title: str, url: str) -> bool:
    if not url.startswith("http") or not title.strip():
        return False
    lowered = (title + " " + url).lower()
    if "newsguidelines" in lowered:
        return False
    if "ycombinator.com" in url and "/item" not in url:
        return False
    if not _title_is_ai_news(title):
        return False
    return True

_KEYWORD_PRODUCT: tuple[tuple[tuple[str, ...], str], ...] = (
    (("hbm", "high bandwidth", "risc-v", "riscv", "jedec"), "openhbm"),
    (("n8n", "workflow", "agent graph", "langgraph"), "constructor"),
    (("analog", "spice", "asic", "schematic"), "openforge"),
    (("sentiment", "semiconductor", "bubble", "nvidia"), "cassandra"),
    (("manufactur", "defect", "factory", "predictive maintenance"), "vertex"),
    (("local llm", "ollama", "on-device", "laptop ai"), "airgpt"),
)


def _get_json(url: str, timeout: float = 12.0) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_hn_stories() -> list[dict[str, str]]:
    try:
        payload = _get_json(HN_URL)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
        return []
    hits = payload.get("hits") or []
    out: list[dict[str, str]] = []
    for hit in hits:
        url = hit.get("url") or ""
        title = hit.get("title") or ""
        if not usable_story(title, url):
            continue
        object_id = str(hit.get("objectID") or url)
        out.append({"id": f"hn-{object_id}", "headline": title, "url": url})
    return out


def match_product(headline: str, products: list[dict[str, Any]]) -> dict[str, Any]:
    lowered = headline.lower()
    by_id = {p["id"]: p for p in products}
    for needles, pid in _KEYWORD_PRODUCT:
        if any(n in lowered for n in needles) and pid in by_id:
            return by_id[pid]
    featured = next((p for p in products if p.get("featured")), None)
    return featured or products[0]


def news_items(catalog: dict[str, Any], *, live: bool) -> list[dict[str, str]]:
    """Prefer live HN stories; fall back to facts.json seeds. Always URL-bearing."""
    if live:
        stories = fetch_hn_stories()
        if stories:
            return stories
    seeds = catalog.get("news_seeds") or []
    return [
        {"id": s["id"], "headline": s["headline"], "url": s["url"], "relevant_product": s.get("relevant_product")}
        for s in seeds
        if str(s.get("url", "")).startswith("http")
    ]
