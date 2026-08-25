from __future__ import annotations

from netie_exposure.catalog import load_facts
from netie_exposure.channels import linkedin_payload, reddit_payload, reddit_subreddit
from netie_exposure.cli import main
from netie_exposure.drafts import render_queue
from netie_exposure.news import match_product, news_items, usable_story


def test_run_offline(tmp_path, capsys) -> None:
    outbox = tmp_path / "outbox"
    assert main(["run", "--offline", "--day", "2026-08-25", "--outbox", str(outbox)]) == 0
    crew = outbox / "crew"
    assert (crew / "00-vanguard.md").is_file()
    assert (crew / "01-cortex.md").is_file()
    assert (crew / "99-closer.md").is_file()
    assert (crew / "marketing.md").is_file()
    assert (crew / "github" / "PROFILE.md").is_file()
    assert (crew / "github" / "SHOW_HN.md").is_file()
    li = list((crew / "linkedin").glob("*.md"))
    rd = list((crew / "reddit").glob("*.md"))
    assert len(li) == 6
    assert len(rd) == 6
    profile = (crew / "github" / "PROFILE.md").read_text(encoding="utf-8")
    assert "OpenHBM" in profile
    assert "https://github.com/Netie-AI" in profile
    closer = (crew / "99-closer.md").read_text(encoding="utf-8")
    assert "social_posting: off" in closer
    out = capsys.readouterr().out
    assert '"engine": "cortex"' in out


def test_run_refuses_fake_followers(tmp_path) -> None:
    assert (
        main(
            [
                "run",
                "--offline",
                "--outbox",
                str(tmp_path / "outbox"),
                "--request",
                "generate linkedin followers until 100k",
            ]
        )
        == 3
    )


def test_linkedin_limits() -> None:
    draft = render_queue(load_facts(), day="2026-08-25")[0]
    li = linkedin_payload(draft)
    assert len(li["hook"]) <= 210
    assert len(li["body"]) <= 1300
    assert li["hashtags"].count("#") <= 3


def test_reddit_allowlist_and_affiliation() -> None:
    drafts = render_queue(load_facts(), day="2026-08-25")
    product = next(d for d in drafts if d["kind"] == "product")
    rd = reddit_payload(product)
    assert rd["subreddit"] == reddit_subreddit(product.get("product_id"))
    assert "affiliation" in rd["selftext"].lower()
    assert rd["subreddit"] in ("opensource", "selfhosted", "LocalLLaMA", "MachineLearning", "FPGA", "RISCV")


def test_news_seeds_offline() -> None:
    items = news_items(load_facts(), live=False)
    assert items
    assert items[0]["url"].startswith("https://")
    product = match_product("HBM4 memory JEDEC", load_facts()["products"])
    assert product["id"] == "openhbm"


def test_skips_hn_guidelines() -> None:
    assert not usable_story(
        "Don't post generated/AI-edited comments",
        "https://news.ycombinator.com/newsguidelines.html#generated",
    )
    assert usable_story("Open HBM4 controller", "https://github.com/Netie-AI/OpenHBM")
    assert not usable_story("Airfoil", "https://ciechanow.ski/airfoil/")

