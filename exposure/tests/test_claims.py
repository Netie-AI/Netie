from __future__ import annotations

import pytest

from netie_exposure.claims import assert_clean, find_denied, laptop_ascii


def test_strips_em_dash() -> None:
    assert laptop_ascii("a\u2014b") == "a-b"


def test_denies_suite_film_and_wasm() -> None:
    hits = find_denied("We apply Wasm sandboxing and closed TechCorp at $45k")
    assert "wasm sandboxing" in hits
    assert "$45k" in hits


def test_assert_clean_raises() -> None:
    with pytest.raises(ValueError, match="denied claims"):
        assert_clean("guaranteed followers overnight")


def test_honest_openhbm_passes() -> None:
    assert_clean("OpenHBM is an open HBM4 controller. Source: https://github.com/Netie-AI/OpenHBM")


def test_negated_inference_server_is_allowed() -> None:
    assert_clean("Cortex is not an inference server. Source: https://netie.ai/")
    assert find_denied("Not an auto-trader. Source: https://github.com/Netie-AI/Cassandra") == []

