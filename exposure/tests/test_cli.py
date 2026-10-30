from __future__ import annotations

from netie_exposure.cli import main


def test_crew_cli(capsys) -> None:
    assert main(["crew"]) == 0
    out = capsys.readouterr().out
    assert '"engine": "cortex"' in out
    assert "linkedin" in out


def test_catalog_offline(capsys) -> None:
    assert main(["catalog", "--offline"]) == 0
    out = capsys.readouterr().out
    assert "Netie.AI" in out
    assert "OpenHBM" in out
    assert "MYR 1500" in out


def test_refuse_cli(capsys) -> None:
    assert main(["refuse", "generate linkedin followers until 100k"]) == 0
    assert "fake_followers" in capsys.readouterr().out


def test_queue_writes(tmp_path, capsys) -> None:
    outbox = tmp_path / "outbox"
    assert main(["queue", "--offline", "--day", "2026-08-25", "--outbox", str(outbox)]) == 0
    files = list(outbox.glob("*.md"))
    assert len(files) == 6
    text = files[0].read_text(encoding="utf-8")
    assert "https://" in text
    assert "status: draft" in text


def test_growth_cli(capsys) -> None:
    assert main(["growth", "--offline", "--followers", "0"]) == 0
    out = capsys.readouterr().out
    assert "100000" in out
    assert "organic_only" in out
