"""Links to this site inside newsletter bodies (scripts/newsletter_links.py).

Runs on the built site before upload. A link whose target exists is fine;
one whose target can be identified unambiguously gets a redirect page; any
other broken link is reported and never blocks publishing.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import newsletter_links  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "newsletter_links.py"


def page(site: Path, route: str, *, permalink: str | None = None, body: str = "", chrome: str = ""):
    path = site / route.strip("/") / "index.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = f'<meta name="newsletter-permalink" content="{permalink}">' if permalink else ""
    newsletter = f'<div class="email-newsletter">{body}</div>' if permalink else body
    path.write_text(f"<html><head>{meta}</head><body><nav>{chrome}</nav>{newsletter}</body></html>")
    return path


@pytest.fixture
def site(tmp_path):
    root = tmp_path / "_site"
    page(root, "/", body="Home")
    page(
        root, "/14.16-badMedia-10.22.26/", permalink="/14.16-badMedia-10.22.26/", body="<p>Old</p>"
    )
    page(root, "/about/", body="About")
    return root


def issue(site: Path, body: str, chrome: str = "") -> Path:
    return page(
        site, "/14.17-ME-11.8.26/", permalink="/14.17-ME-11.8.26/", body=body, chrome=chrome
    )


def run(site: Path) -> dict:
    return newsletter_links.check(site)


def redirect_target(site: Path, route: str) -> str | None:
    path = site / route.strip("/") / "index.html"
    if not path.is_file():
        return None
    text = path.read_text()
    marker = 'rel="canonical" href="'
    return text.split(marker, 1)[1].split('"', 1)[0] if marker in text else None


# ── links that already work ──────────────────────────────────────────────


@pytest.mark.parametrize(
    "href",
    [
        "https://smartdrivingcar.com/14.17-ME-11.8.26/",  # self-link: built in this deploy
        "https://smartdrivingcar.com/14.17-ME-11.8.26",  # no trailing slash
        "http://www.smartdrivingcar.com/14.16-badMedia-10.22.26/#section",  # www, http, anchor
        "/14.16-badMedia-10.22.26/?utm=x",  # relative with query
        "/about/",
        "https://example.com/not-ours/",  # other sites are not ours to check
        "mailto:editor@example.edu",
        "#top",
    ],
)
def test_working_and_foreign_links_are_left_alone(site, href):
    issue(site, f'<a href="{href}">x</a>')
    before = sorted(p for p in site.rglob("*"))
    report = run(site)
    assert report["repaired"] == [] and report["broken"] == []
    assert sorted(p for p in site.rglob("*")) == before


# ── unambiguous targets are repaired with a redirect ─────────────────────


@pytest.mark.parametrize(
    "href, route",
    [
        ("https://smartdrivingcar.com/14.17-M&E-11.8.26", "/14.17-M&E-11.8.26/"),
        ("https://smartdrivingcar.com/14.17-M%26E-11.8.26/", "/14.17-M&E-11.8.26/"),
        ("/14.16-badMedia!-10.22.26/", "/14.16-badMedia!-10.22.26/"),
        ("https://smartdrivingcar.com/14.16-BADMEDIA-10.22.26/", "/14.16-BADMEDIA-10.22.26/"),
    ],
)
def test_unambiguous_broken_link_gets_a_redirect(site, href, route):
    issue(site, f'<a href="{href}">x</a>')
    report = run(site)
    assert report["broken"] == []
    (fixed,) = report["repaired"]
    assert fixed["issue"] == "/14.17-ME-11.8.26/"
    assert fixed["link"] == route
    target = fixed["target"]
    assert redirect_target(site, route) == "https://smartdrivingcar.com" + target
    redirect = (site / route.strip("/") / "index.html").read_text()
    assert 'http-equiv="refresh"' in redirect and 'name="robots" content="noindex"' in redirect


def test_repair_is_idempotent(site):
    issue(site, '<a href="https://smartdrivingcar.com/14.17-M&E-11.8.26">x</a>')
    run(site)
    assert run(site)["repaired"] == []  # the redirect now exists


# ── everything else is reported, never blocking, never written ───────────


@pytest.mark.parametrize(
    "href",
    [
        "https://smartdrivingcar.com/14.18-NextWeek-11.15.26/",  # a future issue
        "/no-such-page/",
        "https://smartdrivingcar.com/../../etc/passwd",  # must never escape the site
    ],
)
def test_unfixable_broken_link_is_reported_without_writing(site, href):
    issue(site, f'<a href="{href}">x</a>')
    before = sorted(p for p in site.rglob("*"))
    report = run(site)
    assert report["repaired"] == []
    assert [b["issue"] for b in report["broken"]] == ["/14.17-ME-11.8.26/"]
    assert sorted(p for p in site.rglob("*")) == before


def test_resolver_matches_exactly_one_issue_or_none():
    issues = {"/14.16-badMedia-10.22.26/", "/14.17-ME-11.8.26/"}
    assert newsletter_links.resolve("/14.17-M&E-11.8.26/", issues) == "/14.17-ME-11.8.26/"
    assert (
        newsletter_links.resolve("/14.16-BADMEDIA-10.22.26/", issues) == "/14.16-badMedia-10.22.26/"
    )
    assert newsletter_links.resolve("/nested/14.17-ME-11.8.26/", issues) is None
    assert newsletter_links.resolve("/14.18-Next-11.15.26/", issues) is None
    # Two issues differing only in case: never guess.
    ambiguous = {"/14.16-badMedia-10.22.26/", "/14.16-BadMedia-10.22.26/"}
    assert newsletter_links.resolve("/14.16-badmedia-10.22.26/", ambiguous) is None


def test_only_newsletter_bodies_are_this_checks_concern(site):
    """Site navigation stays lychee's job, and lychee still blocks on it."""
    issue(site, "<p>ok</p>", chrome='<a href="/broken-nav/">nav</a>')
    report = run(site)
    assert report["broken"] == [] and report["checked"] == 0


def test_lychee_ignores_exactly_the_reported_relative_links(site, tmp_path):
    issue(site, '<a href="/no-such-page/">x</a><a href="/about/">ok</a>')
    report = run(site)
    patterns = newsletter_links.lychee_ignore(report)
    import re

    assert any(re.search(p, "file:///w/_site/no-such-page/") for p in patterns)
    assert not any(re.search(p, "file:///w/_site/about/") for p in patterns)
    assert not any(re.search(p, "file:///w/_site/no-such-page-2/") for p in patterns)


# ── CLI ───────────────────────────────────────────────────────────────────


def test_cli_writes_report_and_succeeds_even_with_broken_links(site, tmp_path):
    issue(
        site,
        '<a href="https://smartdrivingcar.com/14.17-M&E-11.8.26">fix</a><a href="/nope/">bad</a>',
    )
    out = tmp_path / "link-report.json"
    ignore = tmp_path / ".lycheeignore"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(site),
            "--report",
            str(out),
            "--lychee-ignore",
            str(ignore),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    report = json.loads(out.read_text())
    assert len(report["repaired"]) == 1 and len(report["broken"]) == 1
    assert "::warning" in result.stdout and "/nope/" in result.stdout
    assert ignore.read_text().strip()
    assert not (site / "link-report.json").exists()  # nothing private in the artifact


def test_cli_appends_to_an_existing_lychee_ignore_file(site, tmp_path):
    """The repository commits its own .lycheeignore; it must never be overwritten."""
    issue(site, '<a href="/nope/">bad</a>')
    ignore = tmp_path / ".lycheeignore"
    ignore.write_text("# committed rules\n^mailto:\n")
    subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            str(site),
            "--report",
            str(tmp_path / "r.json"),
            "--lychee-ignore",
            str(ignore),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=60,
    )
    text = ignore.read_text()
    assert text.startswith("# committed rules\n^mailto:\n")
    assert "nope" in text
