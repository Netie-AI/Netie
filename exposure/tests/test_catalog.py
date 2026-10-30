from __future__ import annotations

from netie_exposure.catalog import load_facts, merge_catalog, product_by_id


def test_facts_have_org_and_hire() -> None:
    facts = load_facts()
    assert facts["org"]["login"] == "Netie-AI"
    assert facts["growth"]["linkedin_followers_target"] == 100000
    assert len(facts["hire_offers"]) >= 3
    assert product_by_id(facts, "openhbm")["github"].endswith("OpenHBM")


def test_offline_merge_does_not_invent_live() -> None:
    catalog = merge_catalog(live=False)
    assert catalog["live"] is False
    assert catalog["github_stars_total"] == 0
    ids = {p["id"] for p in catalog["products"]}
    assert "cortex" in ids
    assert "constructor" in ids
    assert "aim" in ids
