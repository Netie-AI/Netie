"""DMS Space ACL. Not AnythingLLM over the warehouse."""

from __future__ import annotations

import netie._scripts  # noqa: F401

from dms_space_acl import answer_or_abstain, browse_or_abstain

__all__ = ("answer_or_abstain", "browse_or_abstain")
