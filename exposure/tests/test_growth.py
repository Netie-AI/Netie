from __future__ import annotations

import pytest

from netie_exposure.channels import publish
from netie_exposure.growth import snapshot
from netie_exposure.refuse import ExposureRefusal


def test_remaining_math() -> None:
    row = snapshot(linkedin_followers=12, github_stars_total=24, drafts_written=6)
    assert row["linkedin_target"] == 100_000
    assert row["linkedin_remaining"] == 100_000 - 12
    assert row["organic_only"] is True


def test_unknown_followers() -> None:
    row = snapshot(linkedin_followers=None, github_stars_total=0, drafts_written=0)
    assert row["linkedin_remaining"] is None


def test_publish_requires_approve() -> None:
    draft = {"id": "abc", "channel": "linkedin"}
    with pytest.raises(ExposureRefusal) as ei:
        publish(draft, approved_id=None)
    assert ei.value.code == "publish_without_approve"
    note = publish(draft, approved_id="abc")
    assert "DRY-RUN" in note
