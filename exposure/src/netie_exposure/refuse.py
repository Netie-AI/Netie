"""Named refusals. Growth tactics that manufacture audience are not tickets."""

from __future__ import annotations


class ExposureRefusal(Exception):
    """A requested tactic is disallowed. Do not write an outbox file."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


REFUSALS: dict[str, str] = {
    "fake_followers": (
        "Will not create fake LinkedIn accounts, bots, or inflated follower counts. "
        "100k is an organic north star. Draft posts; a human approves."
    ),
    "buy_followers": (
        "Will not buy LinkedIn followers, engagement pods, or like-for-like rings."
    ),
    "follow_unfollow": (
        "Will not auto-follow, auto-unfollow, or mass-invite connections. That is spam."
    ),
    "scrape_linkedin": (
        "Will not scrape LinkedIn. Official API after human approve only, or markdown drafts."
    ),
    "buy_stars": (
        "Will not buy GitHub stars, join star exchanges, or click-farm. Earn them with public work."
    ),
    "reddit_brigade": (
        "Will not vote-brigade, multi-dump the same link, or use unofficial Reddit clients."
    ),
    "invent_customer": (
        "Will not invent customers, revenue, or case studies. Suite films are not proof."
    ),
    "invent_price": (
        "Will not invent Hire prices. Use catalog.json / facts.json only."
    ),
    "second_engine": (
        "Will not start a second orchestrator. Cortex is the only engine. This pack drafts."
    ),
    "cassandra_trade": (
        "Cassandra does not place orders. News drafts are research notes, not trade signals."
    ),
    "publish_without_approve": (
        "Social posting is off unless EXPOSURE_AUTO_POST=1 or --grant-auto, "
        "plus official tokens. Pass --approve <id> for a single post."
    ),
    "mint_oauth": (
        "Will not mint LinkedIn or Reddit OAuth tokens. Create them in the "
        "official developer consoles. Chat grant is not OAuth."
    ),
}

# Phrases that map a user/agent request onto a refusal code.
TRIGGERS: tuple[tuple[str, str], ...] = (
    ("fake follower", "fake_followers"),
    ("generate followers", "fake_followers"),
    ("generate linkedin follower", "fake_followers"),
    ("bot farm", "fake_followers"),
    ("buy follower", "buy_followers"),
    ("purchase follower", "buy_followers"),
    ("engagement pod", "buy_followers"),
    ("follow unfollow", "follow_unfollow"),
    ("auto follow", "follow_unfollow"),
    ("mass invite", "follow_unfollow"),
    ("scrape linkedin", "scrape_linkedin"),
    ("unofficial linkedin", "scrape_linkedin"),
    ("buy star", "buy_stars"),
    ("star exchange", "buy_stars"),
    ("star farm", "buy_stars"),
    ("upvote brigade", "reddit_brigade"),
    ("vote brigade", "reddit_brigade"),
    ("techcorp", "invent_customer"),
    ("named client", "invent_customer"),
    ("n8n clone", "second_engine"),
    ("new orchestrator", "second_engine"),
    ("place trade", "cassandra_trade"),
    ("auto-trader", "cassandra_trade"),
    ("just post it", "publish_without_approve"),
    ("publish now", "publish_without_approve"),
    ("mint oauth", "mint_oauth"),
    ("fake api key", "mint_oauth"),
    ("generate linkedin token", "mint_oauth"),
    ("create linkedin token", "mint_oauth"),
    ("create reddit token", "mint_oauth"),
)

# Word-pair ANDs so "generate linkedin followers until 100k" still matches.
COMBOS: tuple[tuple[tuple[str, str], str], ...] = (
    (("generate", "follower"), "fake_followers"),
    (("buy", "follower"), "buy_followers"),
    (("buy", "star"), "buy_stars"),
    (("scrape", "linkedin"), "scrape_linkedin"),
)


def check_request(text: str) -> None:
    """Raise ExposureRefusal if the request is a disallowed growth tactic."""
    lowered = text.lower()
    for needle, code in TRIGGERS:
        if needle in lowered:
            raise ExposureRefusal(code, REFUSALS[code])
    for (a, b), code in COMBOS:
        if a in lowered and b in lowered:
            raise ExposureRefusal(code, REFUSALS[code])


def refuse(code: str) -> None:
    if code not in REFUSALS:
        raise KeyError(code)
    raise ExposureRefusal(code, REFUSALS[code])
