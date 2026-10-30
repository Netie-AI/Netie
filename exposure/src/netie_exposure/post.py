"""Official LinkedIn / Reddit / GitHub posts. No scrape. No unofficial clients."""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from netie_exposure.catalog import USER_AGENT
from netie_exposure.channels import linkedin_payload, reddit_payload
from netie_exposure.refuse import refuse
from netie_exposure.tokens import github_token, ready_to_post, social_ready, status


class MissingTokens(Exception):
    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(
            "missing_tokens: " + ", ".join(missing) + ". "
            "I cannot mint LinkedIn/Reddit OAuth from chat. See TOKENS.md."
        )


def _json_request(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    timeout: float = 20.0,
) -> tuple[int, Any]:
    hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            payload = json.loads(raw) if raw.strip() else {}
            return resp.status, payload
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(body) if body.strip() else {"error": body}
        except json.JSONDecodeError:
            payload = {"error": body[:500]}
        return exc.code, payload


def post_linkedin(draft: dict[str, Any]) -> dict[str, Any]:
    token = os.environ.get("LINKEDIN_ACCESS_TOKEN") or ""
    if not token:
        raise MissingTokens(["linkedin"])
    code, me = _json_request(
        "https://api.linkedin.com/v2/userinfo",
        headers={"Authorization": f"Bearer {token}"},
    )
    person = me.get("sub") or me.get("id")
    if code >= 400 or not person:
        code, me = _json_request(
            "https://api.linkedin.com/v2/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        person = me.get("id")
    if not person:
        return {"ok": False, "channel": "linkedin", "error": "linkedin_person_urn_missing", "http": code}
    li = linkedin_payload(draft)
    text = f"{li['hook']}\n\n{li['body']}\n\n{li['hashtags']}"
    body = {
        "author": f"urn:li:person:{person}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text[:3000]},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    raw = json.dumps(body).encode("utf-8")
    code, payload = _json_request(
        "https://api.linkedin.com/v2/ugcPosts",
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        },
        data=raw,
    )
    return {
        "ok": 200 <= code < 300,
        "channel": "linkedin",
        "http": code,
        "id": payload.get("id") or payload.get("ugcPost"),
        "error": None if 200 <= code < 300 else payload,
    }


def _reddit_access_token() -> str:
    cid = os.environ.get("REDDIT_CLIENT_ID") or ""
    secret = os.environ.get("REDDIT_CLIENT_SECRET") or ""
    user = os.environ.get("REDDIT_USERNAME") or ""
    password = os.environ.get("REDDIT_PASSWORD") or ""
    if not all((cid, secret, user, password)):
        raise MissingTokens(["reddit"])
    data = urllib.parse.urlencode(
        {"grant_type": "password", "username": user, "password": password}
    ).encode("utf-8")
    auth = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=data,
        headers={"User-Agent": USER_AGENT},
        method="POST",
    )
    token_basic = base64.b64encode(f"{cid}:{secret}".encode("ascii")).decode("ascii")
    auth.add_header("Authorization", f"Basic {token_basic}")
    with urllib.request.urlopen(auth, timeout=20.0) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    access = payload.get("access_token")
    if not access:
        raise MissingTokens(["reddit"])
    return str(access)


def post_reddit(draft: dict[str, Any]) -> dict[str, Any]:
    token = _reddit_access_token()
    rd = reddit_payload(draft)
    form = urllib.parse.urlencode(
        {
            "api_type": "json",
            "kind": "self",
            "sr": rd["subreddit"],
            "title": rd["title"][:300],
            "text": rd["selftext"][:40000],
        }
    ).encode("utf-8")
    code, payload = _json_request(
        "https://oauth.reddit.com/api/submit",
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data=form,
    )
    j = payload.get("json") or payload
    errors = j.get("errors") if isinstance(j, dict) else None
    ok = 200 <= code < 300 and not errors
    return {
        "ok": ok,
        "channel": "reddit",
        "http": code,
        "subreddit": rd["subreddit"],
        "error": errors or (None if ok else payload),
    }


def post_github_issue_skip(draft: dict[str, Any]) -> dict[str, Any]:
    """GitHub channel earns stars via PROFILE.md, not issue spam."""
    _ = github_token()
    return {
        "ok": True,
        "channel": "github",
        "skipped": True,
        "reason": "GitHub posting is PROFILE.md / Show HN, not issue spam.",
        "draft_id": draft.get("id"),
    }


def post_draft(draft: dict[str, Any], *, live: bool, approved_id: str | None) -> dict[str, Any]:
    if approved_id != draft["id"]:
        refuse("publish_without_approve")
    if not live:
        return {
            "ok": True,
            "dry_run": True,
            "id": draft["id"],
            "channel": draft.get("channel"),
            "ready": ready_to_post(),
            "tokens": {k: v for k, v in status().items() if k != "note"},
        }
    missing = [c for c in ("linkedin", "reddit") if c not in social_ready()]
    channel = draft.get("channel") or "linkedin"
    if channel == "linkedin":
        if "linkedin" in missing:
            raise MissingTokens(["linkedin"])
        return post_linkedin(draft)
    if channel == "reddit":
        if "reddit" in missing:
            raise MissingTokens(["reddit"])
        return post_reddit(draft)
    return post_github_issue_skip(draft)
