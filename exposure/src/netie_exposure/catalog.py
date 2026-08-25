"""Merge frozen facts with the live GitHub org. Never invent a repo."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

FACTS_PATH = Path(__file__).resolve().parent / "data" / "facts.json"
USER_AGENT = "netie-exposure/0.1 (+https://github.com/Netie-AI)"


def load_facts(path: Path | None = None) -> dict[str, Any]:
    return json.loads((path or FACTS_PATH).read_text(encoding="utf-8"))


def _get_json(url: str, timeout: float = 12.0) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_github_org(login: str = "Netie-AI") -> dict[str, Any] | None:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    url = f"https://api.github.com/orgs/{login}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=12.0) as resp:
            org = json.loads(resp.read().decode("utf-8"))
        repos_url = f"https://api.github.com/orgs/{login}/repos?per_page=100&type=public"
        req2 = urllib.request.Request(
            repos_url, headers={"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
        )
        if token:
            req2.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req2, timeout=12.0) as resp:
            repos = json.loads(resp.read().decode("utf-8"))
        return {"org": org, "repos": repos}
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def fetch_hire_catalog(url: str) -> dict[str, Any] | None:
    try:
        payload = _get_json(url)
        return payload if isinstance(payload, dict) else None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def merge_catalog(
    facts: dict[str, Any] | None = None,
    *,
    live: bool = False,
) -> dict[str, Any]:
    """Return a catalog. Live fetch overlays stars and GitHub descriptions only."""
    catalog = json.loads(json.dumps(facts or load_facts()))  # deep copy
    catalog["live"] = False
    catalog["github_stars_total"] = 0
    if not live:
        return catalog

    gh = fetch_github_org(catalog["org"]["login"])
    hire = fetch_hire_catalog(catalog["org"]["hire_catalog"])
    if gh:
        catalog["live"] = True
        org = gh["org"]
        catalog["org"]["description"] = org.get("description") or catalog["org"]["description"]
        catalog["org"]["blog"] = org.get("blog") or catalog["org"]["blog"]
        catalog["org"]["public_repos"] = org.get("public_repos")
        catalog["org"]["followers"] = org.get("followers")
        by_name = {r["name"]: r for r in gh["repos"]}
        stars = 0
        for product in catalog["products"]:
            gh_url = product.get("github") or ""
            name = gh_url.rstrip("/").split("/")[-1] if gh_url else ""
            repo = by_name.get(name)
            if repo:
                product["stargazers_count"] = repo.get("stargazers_count", 0)
                product["github_description"] = repo.get("description") or ""
                stars += int(product["stargazers_count"] or 0)
        catalog["github_stars_total"] = stars
        catalog["public_repos"] = [
            {
                "name": r["name"],
                "description": r.get("description") or "",
                "html_url": r["html_url"],
                "stargazers_count": r.get("stargazers_count", 0),
            }
            for r in sorted(gh["repos"], key=lambda x: (-x.get("stargazers_count", 0), x["name"]))
        ]
    if hire and "offers" in hire:
        catalog["hire_offers_live"] = hire["offers"]
    return catalog


def product_by_id(catalog: dict[str, Any], pid: str) -> dict[str, Any]:
    for item in catalog["products"]:
        if item["id"] == pid:
            return item
    raise KeyError(pid)
