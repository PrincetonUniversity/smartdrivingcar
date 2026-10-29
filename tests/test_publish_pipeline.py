"""Regression and trust-boundary tests for unattended publishing."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from publish_newsletter import parse_newsletter, safe_html, write_issue

BODY = (
    "<h2>Transport news</h2><p>"
    + "Useful commentary about safe and accessible autonomous mobility. " * 3
    + "</p>"
)
SUBJECT = "SmartDrivingCars_14.16-badMedia-10.22.26"


def test_safe_render_blocks_active_content_and_liquid():
    output = safe_html(
        '<script>secret()</script><iframe src="https://evil.test"></iframe>'
        '<p onclick="bad()">{{ site.github }} {% endraw %}</p>'
        '<a href="javascript:alert(1)">unsafe</a>'
        '<a href="data:text/html,bad">data</a>'
    )
    assert "script" not in output and "iframe" not in output and "onclick" not in output
    assert "javascript:" not in output and "data:" not in output
    assert "{{" not in output and "{%" not in output
    assert "unsafe" in output


def test_safelinks_are_unwrapped_without_recipient_tracking():
    output = safe_html(
        '<p><a href="https://nam12.safelinks.protection.outlook.com/?url=https%3A%2F%2Fexample.org%2Fstory%3Fa%3D1%26b%3D2&data=private">Story</a></p>'
    )
    assert 'href="https://example.org/story?a=1&amp;b=2"' in output
    assert "private" not in output and "safelinks" not in output


def test_preserves_structure_and_never_hotlinks_email_images():
    result = safe_html(
        "<h2>Headline</h2><p><strong>Commentary</strong></p>"
        '<ol><li>First</li></ol><img src="cid:one" alt="Chart">'
    )
    assert "<h2>Headline</h2>" in result
    assert "<strong>Commentary</strong>" in result
    assert "<ol><li>First</li></ol>" in result
    assert "Chart" in result and "<img" not in result


def test_metadata_and_idempotence(tmp_path):
    issue = parse_newsletter(BODY, SUBJECT, "2026-10-22T22:17:13Z")
    assert issue["slug"] == "14.16-badMedia-10.22.26"
    assert issue["date"] == "2026-10-22"
    assert write_issue(issue, tmp_path) == "created"
    assert write_issue(issue, tmp_path) == "duplicate"
    changed = parse_newsletter(BODY + "<p>Correction</p>", SUBJECT, "2026-10-22")
    with pytest.raises(ValueError, match="conflict"):
        write_issue(changed, tmp_path)


@pytest.mark.parametrize(
    "subject", ["Hello", "../../escape", "SmartDrivingCars_14.16-../../escape-10.22.26"]
)
def test_rejects_invalid_subject(subject):
    with pytest.raises(ValueError):
        parse_newsletter(BODY, subject, "2026-10-22")


def test_empty_and_invalid_dates_fail():
    with pytest.raises(ValueError):
        parse_newsletter("<p>Empty</p>", SUBJECT, "2026-10-22")
    with pytest.raises(ValueError):
        parse_newsletter(BODY, "SmartDrivingCars_14.16-badMedia-99.99.26", "2026-10-22")


def test_existing_legacy_issue_never_overwritten(tmp_path):
    issue = parse_newsletter(BODY, SUBJECT, "2026-10-22")
    path = tmp_path / "_newsletters" / issue["slug"] / "index.md"
    path.parent.mkdir(parents=True)
    path.write_text("Legacy curated issue")
    assert write_issue(issue, tmp_path) == "duplicate"
    assert path.read_text() == "Legacy curated issue"


def test_dispatch_does_not_trust_paths_or_frontmatter(tmp_path):
    from publish_newsletter import receive_dispatch

    payload = {
        "slug": "../../escape",
        "date": "2026-10-22",
        "markdown": "---\nlayout: evil\n---\nx",
    }
    with pytest.raises(ValueError):
        receive_dispatch(payload, tmp_path)
    assert not (tmp_path / "_newsletters").exists()


def test_legacy_trigger_splits_message_array():
    template = json.loads(Path("azure/logic-app/workflow.json").read_text())
    trigger = template["resources"][0]["properties"]["definition"]["triggers"][
        "When_a_new_email_arrives"
    ]
    assert trigger["splitOn"] == "@triggerBody()?['value']"


def test_mime_body_ignores_html_attachments(tmp_path):
    from email.message import EmailMessage

    from import_newsletter import extract_body_from_eml

    message = EmailMessage()
    message["Subject"] = SUBJECT
    message.make_mixed()
    attachment = EmailMessage()
    attachment.set_content("<p>Attachment is not the newsletter</p>", subtype="html")
    attachment["Content-Disposition"] = 'attachment; filename="unrelated.html"'
    message.attach(attachment)
    body = EmailMessage()
    body.set_content(BODY, subtype="html")
    message.attach(body)
    path = tmp_path / "message.eml"
    path.write_bytes(message.as_bytes())
    assert "Useful commentary" in extract_body_from_eml(str(path))
    assert "Attachment" not in extract_body_from_eml(str(path))


def test_literal_html_and_template_text_stays_inert():
    result = safe_html("<p>&lt;script&gt;alert(1)&lt;/script&gt; {{ site.title }}</p>")
    assert "<script>" not in result
    assert "&lt;script&gt;" in result
    assert "{{" not in result


def test_malformed_payload_cannot_enable_markdown_html():
    result = parse_newsletter(
        "<p>" + "[click](javascript:alert(1)) " * 5 + "</p>", SUBJECT, "2026-10-22"
    )
    assert 'markdown="0"' in result["markdown"]
    assert '<a href="javascript:' not in result["markdown"]


@pytest.mark.parametrize(
    "subject,slug",
    [
        ("SmartDrivingCar.com/13.01-Welcome Back -2/2/24", "13.01-Welcome-Back-2-2-24"),
        (
            "SmartDrivingCars eLetter...14.11-BocaRatonAV_Conference-6.02.26",
            "14.11-BocaRatonAV-Conference-6.02.26",
        ),
        ("SmartDrivingCar-14.10-SevalOz-5.23.26", "14.10-SevalOz-5.23.26"),
    ],
)
def test_established_professor_subject_formats(subject, slug):
    issue = parse_newsletter(BODY, subject, "2026-10-22")
    assert issue["slug"] == slug


def test_duplicate_keeps_existing_public_url_case(tmp_path):
    issue = parse_newsletter(BODY, SUBJECT, "2026-10-22")
    write_issue(issue, tmp_path)
    incoming = parse_newsletter(BODY, SUBJECT.lower(), "2026-10-22")
    assert write_issue(incoming, tmp_path) == "duplicate"
    assert incoming["slug"] == issue["slug"]


def test_minified_security_banner_does_not_erase_newsletter():
    banner = "<table><tr><td><p>SECURITY WARNING</p><p>Report suspicious mail to the Phish Bowl.</p></td></tr></table>"
    result = safe_html("<html><body>" + banner + BODY + "</body></html>")
    assert "Useful commentary" in result
    assert "SECURITY WARNING" not in result
    assert "Phish Bowl" not in result


def test_listserv_macro_on_same_html_line_does_not_erase_newsletter():
    result = safe_html("<html><body>" + BODY + "<p>TICKET_URL(SIGNOFF)</p></body></html>")
    assert "Useful commentary" in result
    assert "TICKET_URL" not in result


def test_author_words_and_cross_references_are_preserved():
    from bs4 import BeautifulSoup

    source = '<p>Earlier analysis at <a href="https://smartdrivingcar.com/14.15-Godfather-9.26.26/">the previous issue</a> still matters.</p><p>Visit smartdrivingcar.com for context.</p>'
    result = safe_html(source)
    assert (
        BeautifulSoup(result, "html.parser").get_text()
        == BeautifulSoup(source, "html.parser").get_text()
    )
    assert 'href="https://smartdrivingcar.com/14.15-Godfather-9.26.26/"' in result


def test_word_emphasis_is_semantic_and_idempotent():
    from bs4 import BeautifulSoup

    source = '<p><span style="font-weight:700;font-style:italic;color:#C00000">Hmmmm… “Exact words”—Alain.</span></p>'
    result = safe_html(source)
    soup = BeautifulSoup(result, "html.parser")
    assert soup.find("strong") and soup.find("em")
    assert soup.find(class_="newsletter-accent")
    assert soup.get_text() == BeautifulSoup(source, "html.parser").get_text()
    assert "style=" not in result
    assert safe_html(result) == result


def test_large_linked_article_title_becomes_scannable_heading():
    from bs4 import BeautifulSoup

    source = '<p><b><span style="font-size:18.0pt"><a href="https://example.org/story">The next chapter in accessible autonomous transport</a></span></b></p><p>Article quotation.</p>'
    result = safe_html(source)
    soup = BeautifulSoup(result, "html.parser")
    assert soup.find("h3", class_="newsletter-article-title")
    assert soup.get_text() == BeautifulSoup(source, "html.parser").get_text()


def test_generic_inline_spans_and_spacer_paragraphs_do_not_bloat_layout():
    result = safe_html(
        '<p>&nbsp;</p><p><span style="position:fixed;background:url(https://bad.test)">Keep these words.</span></p>'
    )
    assert result == "<p>Keep these words.</p>"


def test_email_date_is_not_promoted_to_an_article_heading():
    from bs4 import BeautifulSoup

    result = safe_html(
        '<p style="font-size:20pt"><a href="https://smartdrivingcar.com/">Thursday, October 22, 2026</a></p>'
    )
    assert not BeautifulSoup(result, "html.parser").find("h3")
    assert "Thursday, October 22, 2026" in result


def test_styled_empty_image_link_still_has_a_visible_destination():
    from bs4 import BeautifulSoup

    result = safe_html(
        '<p><a href="https://example.org/event"><span style="font-weight:bold"><img src="cid:poster" alt=""></span></a></p>'
    )
    anchor = BeautifulSoup(result, "html.parser").find("a")
    assert anchor and anchor.get_text(strip=True) == "https://example.org/event"


def test_explicit_word_emphasis_resets_remain_visible():
    from bs4 import BeautifulSoup

    result = safe_html(
        '<p><i><b>Emphasis <span style="font-style:normal;font-weight:400">ordinary quoted words</span></b></i></p>'
    )
    span = BeautifulSoup(result, "html.parser").find("span")
    assert span and {"newsletter-upright", "newsletter-normal-weight"} <= set(span["class"])
    assert safe_html(result) == result


def test_short_centered_masthead_is_compact_without_changing_words():
    from bs4 import BeautifulSoup

    source = (
        '<p align="center"><b>SmartDrivingCars eLetter</b></p><h3>Article</h3><p>Commentary.</p>'
    )
    result = safe_html(source)
    soup = BeautifulSoup(result, "html.parser")
    assert soup.find("p", class_="newsletter-intro")
    assert soup.get_text() == BeautifulSoup(source, "html.parser").get_text()
    assert safe_html(result) == result


def test_image_alternative_text_is_kept_as_a_subtle_caption():
    from bs4 import BeautifulSoup

    result = safe_html('<p><img src="cid:logo" alt="TNY"> Article headline.</p>')
    assert (
        BeautifulSoup(result, "html.parser").find("span", class_="newsletter-image-alt").get_text()
        == "TNY"
    )
    assert safe_html(result) == result


def test_malformed_date_permalink_does_not_create_a_broken_header_link():
    from bs4 import BeautifulSoup

    source = '<p><a href="https://smartdrivingcar.com/Thursday,%20October%2022,%202026">Thursday, October 22, 2026</a></p>'
    result = safe_html(source)
    assert BeautifulSoup(result, "html.parser").get_text() == "Thursday, October 22, 2026"
    assert not BeautifulSoup(result, "html.parser").find("a")


def test_empty_unlinked_images_do_not_change_the_next_render_fingerprint():
    source = '<p><b><span style="color:#C00000"><img src="cid:empty" alt=""></span></b></p>' + BODY
    rendered = safe_html(source)
    assert safe_html(rendered) == rendered


def test_word_wrapper_whitespace_has_a_stable_fingerprint():
    source = (
        '<div><span style="font-family:Arial">\n</span><span style="font-family:Arial">\n</span>'
        + BODY
        + "</div>"
    )
    rendered = safe_html(source)
    assert safe_html(rendered) == rendered
