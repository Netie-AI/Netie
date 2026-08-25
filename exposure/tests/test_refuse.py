from __future__ import annotations

import pytest

from netie_exposure.refuse import ExposureRefusal, check_request, refuse


@pytest.mark.parametrize(
    "text,code",
    [
        ("generate linkedin followers until 100k", "fake_followers"),
        ("buy followers for the company page", "buy_followers"),
        ("auto follow then unfollow", "follow_unfollow"),
        ("scrape linkedin for leads", "scrape_linkedin"),
        ("buy github stars", "buy_stars"),
        ("upvote brigade r/opensource", "reddit_brigade"),
        ("just post it", "publish_without_approve"),
        ("place trade from Cassandra", "cassandra_trade"),
    ],
)
def test_named_refusals(text: str, code: str) -> None:
    with pytest.raises(ExposureRefusal) as ei:
        check_request(text)
    assert ei.value.code == code


def test_refuse_helper() -> None:
    with pytest.raises(ExposureRefusal) as ei:
        refuse("buy_stars")
    assert "star" in str(ei.value).lower()


def test_clean_request_passes() -> None:
    check_request("draft a LinkedIn hook about OpenHBM and wait for approve")
