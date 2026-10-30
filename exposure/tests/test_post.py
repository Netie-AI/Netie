from __future__ import annotations

import json

from netie_exposure.cli import main
from netie_exposure.post import MissingTokens, post_draft
from netie_exposure.tokens import init_env, ready_to_post, social_ready, status


def test_tokens_status_prints_no_secrets(capsys, monkeypatch) -> None:
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    assert main(["tokens"]) == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["linkedin"] is False
    assert data["reddit"] is False
    assert "Bearer" not in out
    assert "LINKEDIN_ACCESS_TOKEN=" not in out


def test_init_env_is_not_a_linkedin_token(tmp_path) -> None:
    path = init_env(tmp_path / ".env")
    text = path.read_text(encoding="utf-8")
    assert "EXPOSURE_GATE=" in text
    assert "LINKEDIN_ACCESS_TOKEN=" in text
    assert "sk-" not in text


def test_auto_without_grant_refuses(tmp_path) -> None:
    assert main(["auto", "--offline", "--outbox", str(tmp_path / "o")]) == 3


def test_auto_live_without_tokens_exits_4(tmp_path, capsys, monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghs_not_linkedin")
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    code = main(
        [
            "auto",
            "--offline",
            "--grant-auto",
            "--live",
            "--day",
            "2026-08-25",
            "--outbox",
            str(tmp_path / "o"),
        ]
    )
    assert code == 4
    err = capsys.readouterr().err
    assert "missing_tokens" in err


def test_auto_dry_run_with_grant(tmp_path, capsys) -> None:
    code = main(
        [
            "auto",
            "--offline",
            "--grant-auto",
            "--day",
            "2026-08-25",
            "--outbox",
            str(tmp_path / "o"),
        ]
    )
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["live"] is False
    assert data["posted"]
    assert data["posted"][0]["dry_run"] is True


def test_post_draft_missing_linkedin(monkeypatch) -> None:
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    draft = {"id": "x", "channel": "linkedin", "text": "hello https://netie.ai/", "hook": "hello"}
    try:
        post_draft(draft, live=True, approved_id="x")
        raise AssertionError("expected MissingTokens")
    except MissingTokens as exc:
        assert "linkedin" in exc.missing


def test_status_booleans_only() -> None:
    s = status()
    assert set(s) >= {"linkedin", "reddit", "github", "auto_post", "note"}
    assert s["linkedin"] in (True, False)


def test_github_token_is_not_social(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghs_not_linkedin")
    monkeypatch.delenv("LINKEDIN_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
    assert "github" in ready_to_post()
    assert social_ready() == []
