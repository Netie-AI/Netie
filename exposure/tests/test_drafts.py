from __future__ import annotations

from netie_exposure.catalog import load_facts
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


def test_product_lead_is_openhbm() -> None:
    drafts = render_queue(load_facts(), day="2026-08-25")
    product = next(d for d in drafts if d["kind"] == "product")
    assert product["product_id"] == "openhbm"
    assert "OpenHBM" in product["text"]
