"""Archive navigation survives cosmetic filters without duplicate controls."""

import sys
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

ARCHIVE_TEMPLATES = [Path("newsletter/index.html"), Path("_layouts/newsletter-archive.html")]


def template_dom(path):
    source = path.read_text()
    include = "{% include archive-links.html %}"
    if include in source:
        source = source.replace(include, Path("_includes/archive-links.html").read_text())
    return BeautifulSoup(source, "html.parser")


@pytest.mark.parametrize("path", ARCHIVE_TEMPLATES, ids=lambda path: str(path))
def test_cosmetic_newsletter_filter_does_not_hide_archive_navigation(path):
    soup = template_dom(path)
    # EasyList's newsletter annoyance filter targets these signup-widget selectors.
    # https://github.com/easylist/easylist/blob/master/fanboy-addon/fanboy_newsletter_general_hide.txt
    for hidden in soup.select(".newsletter-sidebar, #newsletter-sidebar"):
        hidden.decompose()
    nav = soup.find("nav", attrs={"aria-label": "Newsletter archive navigation"})
    assert nav is not None, "Archive browsing was mistaken for a newsletter signup widget"
    links = nav.select("a[href]")
    assert links, "Archive links must be ordinary HTML anchors"
    assert all("/newsletter/" in link["href"] for link in links)


@pytest.mark.parametrize("path", ARCHIVE_TEMPLATES, ids=lambda path: str(path))
def test_archive_navigation_has_no_duplicate_browse_disclosure(path):
    soup = template_dom(path)
    assert not soup.select(".archive-browser"), "The disclosure duplicates the sidebar"
    assert soup.select_one(".archive-sidebar nav a[href]")


def built_archive():
    links = '<h3>Browse by Year</h3><ul><li><a href="/newsletter/2026/">2026</a></li></ul>'
    return (
        '<div class="archive-layout"><section class="archive-issues">'
        '<ul class="archive-issue-list"><li>An issue</li></ul></section>'
        '<aside class="archive-sidebar"><nav aria-label="Newsletter archive navigation">'
        + links
        + "</nav></aside></div>"
    )


def test_compiled_archive_guard_validates_sidebar_navigation(tmp_path):
    from check_site import check_archive_navigation

    page = tmp_path / "newsletter" / "index.html"
    page.parent.mkdir()
    page.write_text(built_archive())
    assert check_archive_navigation(tmp_path) == 1


@pytest.mark.parametrize(
    "defect",
    ["missing_navigation", "signup_selector", "invalid_destination", "duplicate_disclosure"],
)
def test_compiled_archive_guard_rejects_lost_or_misclassified_navigation(tmp_path, defect):
    from check_site import check_archive_navigation

    page = tmp_path / "newsletter" / "index.html"
    page.parent.mkdir()
    soup = BeautifulSoup(built_archive(), "html.parser")
    if defect == "missing_navigation":
        soup.aside.nav.decompose()
    elif defect == "signup_selector":
        soup.aside.nav["class"] = "newsletter-sidebar"
    elif defect == "invalid_destination":
        soup.aside.nav.a["href"] = "https://example.org/"
    else:
        soup.section.append(soup.new_tag("details", attrs={"class": "archive-browser"}))
    page.write_text(str(soup))
    with pytest.raises(ValueError, match="[Aa]rchive"):
        check_archive_navigation(tmp_path)
