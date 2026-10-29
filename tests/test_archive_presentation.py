"""Archive presentation must improve structure without rewriting authored prose."""

import sys
from pathlib import Path

import pytest
import yaml
from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from restyle_archive import restyle_document, restyle_markdown, visible_text


def test_indented_email_prose_becomes_readable_paragraphs():
    source = "### [An authored headline for this issue](https://example.org/story)\n\n"
    source += " " * 58 + 'A. Writer, June 3, "First line\n'
    source += " " * 58 + 'of this quotation."\n\n'
    source += " " * 58 + "A second paragraph.\n"
    rendered, report = restyle_markdown(source)
    soup = BeautifulSoup(rendered, "html.parser")
    assert not soup.find("pre")
    assert 'A. Writer, June 3, "First line of this quotation."' in visible_text(soup)
    assert report["dedented_lines"] == 3
    assert soup.select_one("h3.newsletter-article-title a")["href"] == "https://example.org/story"


def test_editorial_marker_separates_commentary_without_removing_prose():
    source = (
        "[A full article headline to read](https://example.org/story)\n\n"
        'Reporter: "Quoted passage." [Read more](https://example.org/story) '
        "Hmmmm… My observation.\n\nAnother thought. Alain\n\n"
        "### Next article\n\nIts independent quotation."
    )
    rendered, _ = restyle_markdown(source)
    soup = BeautifulSoup(rendered, "html.parser")
    comments = soup.select(".newsletter-commentary")
    assert [visible_text(p) for p in comments] == [
        "Hmmmm… My observation.",
        "Another thought. Alain",
    ]
    assert not soup.find(string="Its independent quotation.").parent.get("class")
    assert 'Reporter: "Quoted passage." Read more Hmmmm… My observation.' in visible_text(soup)


def test_links_emphasis_mail_and_image_are_preserved_without_active_html():
    source = (
        "**Important** and *emphasis*. [Mail](mailto:author@example.org) "
        "[Previous](/older-issue/) [section](#section)\n\n"
        "![Source poster](https://example.org/poster.jpg)\n\n"
        '<script>alert(1)</script><p onclick="evil()">Literal {{ dangerous }} '
        '<a href="javascript:evil()">unsafe destination</a></p>'
    )
    rendered, _ = restyle_markdown(source)
    soup = BeautifulSoup(rendered, "html.parser")
    assert soup.find("strong").get_text() == "Important"
    assert soup.find("em").get_text() == "emphasis"
    assert [a["href"] for a in soup.find_all("a")] == [
        "mailto:author@example.org",
        "/older-issue/",
        "#section",
    ]
    assert soup.img["alt"] == "Source poster"
    assert soup.img["loading"] == "lazy"
    assert soup.img["referrerpolicy"] == "no-referrer"
    assert not soup.find("script")
    assert not soup.select("[onclick], [style]")
    assert "{{" not in rendered
    assert "unsafe destination" in visible_text(soup)


def test_date_and_bare_url_do_not_become_article_headings():
    source = (
        "[Monday, June 3, 2024](https://example.org/date)\n\n"
        "[https://example.org/very-long-reference](https://example.org/very-long-reference)\n\n"
        "[An actual article headline for reading](https://example.org/story)"
    )
    rendered, _ = restyle_markdown(source)
    soup = BeautifulSoup(rendered, "html.parser")
    assert [p.get_text() for p in soup.select(".newsletter-article-title")] == [
        "An actual article headline for reading"
    ]


def test_decorative_footer_becomes_a_rule_and_tiny_issue_still_improves():
    rendered, _ = restyle_markdown("I am here. Love to see you!!!!!\n\nAlain\n\n" + "*" * 110)
    soup = BeautifulSoup(rendered, "html.parser")
    assert soup.hr
    assert "*" * 20 not in rendered
    assert visible_text(soup) == "I am here. Love to see you!!!!! Alain"


def test_markup_trailing_whitespace_is_clean_but_literal_code_is_preserved():
    rendered, _ = restyle_markdown("Just Published!!! \nNext line.\n\n```text\ntrail  \n```")
    assert "!!! \n" not in rendered
    assert "trail  \n" in BeautifulSoup(rendered, "html.parser").pre.get_text()


def test_existing_frontmatter_permalinks_dates_and_source_are_not_rewritten():
    original = (
        "---\nlayout: newsletter\ntitle: Original\ndate: 2020-01-02\n"
        "permalink: /original/\n---\n\nA short **original** announcement.\n"
    )
    updated, report = restyle_document(original)
    before = yaml.safe_load(original.split("---", 2)[1])
    after = yaml.safe_load(updated.split("---", 2)[1])
    assert all(after[k] == v for k, v in before.items())
    assert after["presentation_version"] == 1
    assert '<div class="email-newsletter newsletter-archive-edition" markdown="0">' in updated
    assert report["text_preserved"] is True
    assert restyle_document(updated)[0] == updated


def test_current_email_renderer_remains_the_reference():
    reference = Path("_newsletters/14.16-badMedia-10.22.26/index.md").read_text()
    updated, report = restyle_document(reference)
    assert updated == reference
    assert report["reference"] is True


def test_reader_title_removes_machine_separators_and_redundant_date():
    original = (
        "---\nlayout: newsletter\ntitle: Original\ndate: 2022-01-08\n"
        "permalink: /10.01-Happy_2022-010822/\n---\n\nOriginal prose."
    )
    updated, _ = restyle_document(original)
    meta = yaml.safe_load(updated.split("---", 2)[1])
    assert meta["presentation_title"] == "10.01 - Happy 2022"
    assert meta["title"] == "Original"
    assert meta["permalink"] == "/10.01-Happy_2022-010822/"


@pytest.mark.parametrize(
    "heading", ["# Top heading", "## Section", "### Article", "#### Subsection"]
)
def test_heading_hierarchy_follows_issue_title(heading):
    rendered, _ = restyle_markdown(heading + "\n\nThe authored text.")
    soup = BeautifulSoup(rendered, "html.parser")
    assert not soup.find(["h1", "h2"])
    assert soup.find(["h3", "h4"]).get("id")


def test_real_code_fences_and_nested_lists_are_not_dedented():
    source = '```python\n    print("literal")\n```\n\n- Parent\n    - Child\n'
    rendered, _ = restyle_markdown(source)
    soup = BeautifulSoup(rendered, "html.parser")
    assert '    print("literal")' in soup.pre.get_text()
    assert soup.select_one("ul li ul li").get_text() == "Child"


def test_email_indentation_after_a_list_does_not_become_code():
    source = (
        "- A previous list item\n\n        In October, quoted prose.\n"
        "        [Read more](https://example.org/story) Hmmmm… Comment. Alain\n\n"
        "          [Another substantial article title](https://example.org/next)\n"
    )
    rendered, _ = restyle_markdown(source)
    soup = BeautifulSoup(rendered, "html.parser")
    assert not soup.pre
    assert soup.find("a", href="https://example.org/story")
    assert soup.select_one(".newsletter-commentary")


def test_inline_literal_angle_brackets_are_not_eaten_as_html():
    rendered, _ = restyle_markdown(
        "Contact <[author@example.org](mailto:author@example.org)>; <->.\n"
    )
    assert "author@example.org" in visible_text(BeautifulSoup(rendered, "html.parser"))


def test_build_outputs_are_excluded_from_publication(tmp_path):
    from check_site import check_site

    (tmp_path / "index.html").write_text("Homepage")
    (tmp_path / "build").mkdir()
    with pytest.raises(ValueError, match="Private"):
        check_site(tmp_path)
    config = yaml.safe_load(Path("_config.yml").read_text())
    assert "build" in config["exclude"]


def test_previous_heading_anchors_are_preserved():
    rendered, _ = restyle_markdown(
        "### Existing article\n\nProse.", anchors={"Existing article": ["existing-article"]}
    )
    assert BeautifulSoup(rendered, "html.parser").h3["id"] == "existing-article"


def test_reference_build_handles_encoded_and_jekyll_dot_routes(tmp_path):
    from restyle_archive import reference_anchors

    first = tmp_path / "Han’s Best" / "index.html"
    first.parent.mkdir()
    first.write_text('<div class="newsletter-main"><h3 id="old">Headline</h3></div>')
    assert reference_anchors(tmp_path, "/Han%E2%80%99s%20Best/") == {"Headline": ["old"]}
    other = tmp_path / "title" / ".-date" / "index.html"
    other.parent.mkdir(parents=True)
    other.write_text(
        '<meta name="newsletter-permalink" content="/title...-date/">'
        '<div class="newsletter-main"><h3 id="second">Another</h3></div>'
    )
    assert reference_anchors(tmp_path, "/title...-date/") == {"Another": ["second"]}


def test_compiled_archive_route_is_repaired_and_prose_is_verified(tmp_path):
    from restyle_archive import check_archive_site, text_fingerprint

    collection = tmp_path / "_newsletters" / "old"
    collection.mkdir(parents=True)
    body = '<div class="email-newsletter"><p>Authored words.</p></div>'
    fingerprint = text_fingerprint(BeautifulSoup(body, "html.parser"))
    collection.joinpath("index.md").write_text(
        "---\ntitle: Original title\npermalink: /title...-date/\npresentation_version: 1\n"
        + "presentation_text_sha256: "
        + fingerprint
        + "\n---\n"
        + body
    )
    site = tmp_path / "site"
    original = site / "title" / ".-date" / "index.html"
    original.parent.mkdir(parents=True)
    original.write_text(
        '<meta name="newsletter-permalink" content="/title...-date/">'
        '<h2 id="issue-title">Original title</h2>' + body
    )
    with pytest.raises(ValueError, match="preserve.*route"):
        check_archive_site(tmp_path, site)
    assert check_archive_site(tmp_path, site, repair_routes=True) == 1
    repaired = site / "title...-date" / "index.html"
    assert repaired.is_file()
    assert not original.exists()
    repaired.write_text(repaired.read_text().replace("Authored words.", "Altered words."))
    with pytest.raises(ValueError, match="prose"):
        check_archive_site(tmp_path, site)


@pytest.mark.parametrize(
    "route",
    ["/../escape/", "/%2e%2e/escape/", "//evil.test/", "https://evil.test/", "/bad/?query=1"],
)
def test_route_repair_cannot_write_outside_site(tmp_path, route):
    from restyle_archive import route_path

    with pytest.raises(ValueError):
        route_path(tmp_path, route)


@pytest.mark.parametrize(
    "path", sorted(Path("_newsletters").rglob("index.md")), ids=lambda path: path.parent.name
)
def test_every_archived_issue_has_current_presentation_and_preserved_text(path):
    from restyle_archive import text_fingerprint

    source = path.read_text()
    _, frontmatter, body = source.split("---", 2)
    metadata = yaml.safe_load(frontmatter)
    soup = BeautifulSoup(body, "html.parser")
    content = soup.select_one(".email-newsletter")
    assert content is not None, f"Unstyled newsletter: {path}"
    assert visible_text(content), f"Empty newsletter: {path}"
    if metadata.get("parser_version") == 2:
        assert metadata.get("source_sha256")
        return
    assert metadata.get("presentation_version") == 1
    assert "newsletter-archive-edition" in content.get("class", [])
    assert metadata["presentation_text_sha256"] == text_fingerprint(content)
    assert not content.select("h1,h2,script,iframe,[style],[onclick]")
    headings = content.find_all(["h3", "h4", "h5", "h6"])
    ids = [heading.get("id") for heading in headings]
    assert len(ids) == len(set(ids))
    assert all(ids)
    for link in soup.select(".newsletter-contents a"):
        assert content.find(id=link["href"].removeprefix("#"))
