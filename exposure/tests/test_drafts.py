from __future__ import annotations

from netie_exposure.catalog import load_facts
from netie_exposure.cli import main
from netie_exposure.drafts import KINDS, render_queue, to_markdown


def test_queue_has_sources_and_kinds() -> None:
    drafts = render_queue(load_facts(), day="2026-08-25")
    assert len(drafts) == 6
    kinds = {d["kind"] for d in drafts}
    assert kinds == set(KINDS)
    for d in drafts:
        assert d["status"] == "draft"
        assert all(s.startswith("https://") for s in d["sources"])
        md = to_markdown(d)
        assert d["id"] in md
        assert "Sources" in md


def test_ids_are_stable() -> None:
    a = render_queue(load_facts(), day="2026-08-25")
    b = render_queue(load_facts(), day="2026-08-25")
    assert [d["id"] for d in a] == [d["id"] for d in b]


def test_rotate_changes_product() -> None:
    a = next(d for d in render_queue(load_facts(), day="2026-08-25", rotate=0) if d["kind"] == "product")
    b = next(d for d in render_queue(load_facts(), day="2026-08-25", rotate=1) if d["kind"] == "product")
    assert a["product_id"] == "openhbm"
    assert b["product_id"] != a["product_id"]


def test_calendar_week(tmp_path, capsys) -> None:
    outbox = tmp_path / "cal"
    assert main(["calendar", "--offline", "--days", "3", "--day", "2026-08-25", "--outbox", str(outbox)]) == 0
    assert (outbox / "2026-08-25" / "crew" / "marketing.md").is_file()
    assert (outbox / "2026-08-26" / "crew" / "linkedin").is_dir()
    assert (outbox / "2026-08-27" / "crew" / "reddit").is_dir()
    out = capsys.readouterr().out
    assert '"linkedin_target": 100000' in out
    assert '"social_posting": "off"' in out
