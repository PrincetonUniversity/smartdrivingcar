#!/usr/bin/env python3
"""Tests for process_newsletter Azure Function."""
import json
import os
import sys
import pytest

# Add azure/functions to path for importing newsletter_processor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the pure processing logic (no azure.functions dependency)
from newsletter_processor import process, parse_date_to_iso, build_display_name


SAMPLE_HTML = """<html><body>
<p>Thursday, Aug. 28, 2025</p>
<p><a href="https://smartdrivingcar.com/13.17-Irene-08.28.25">SmartDrivingCar.Com/13.17-Irene-08.28.25</a></p>
<h1>Newsletter Title</h1>
<p>Some content about autonomous vehicles.</p>
<ul><li>Item one</li><li>Item two</li></ul>
<p>*****</p>
<p>This list is maintained by Princeton University.</p>
</body></html>"""


class TestProcessFunction:
    """Tests for the main process() function."""

    def test_valid_newsletter_returns_correct_structure(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert "slug" in result
        assert "title" in result
        assert "date" in result
        assert "markdown" in result
        assert "display_name" in result
        assert "is_duplicate" in result

    def test_valid_newsletter_correct_slug(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert result["slug"] == "13.17-Irene-08.28.25"

    def test_valid_newsletter_correct_date(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert result["date"] == "2025-08-28"

    def test_front_matter_contains_layout(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert "layout: newsletter" in result["markdown"]

    def test_front_matter_contains_title(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert 'title: "Weekly Update"' in result["markdown"]

    def test_front_matter_contains_date(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert "date: 2025-08-28" in result["markdown"]

    def test_front_matter_contains_permalink(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert "permalink: /13.17-Irene-08.28.25/" in result["markdown"]

    def test_author_slug_extraction(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert result["slug"] == "13.17-Irene-08.28.25"

    def test_display_name_from_author_slug(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert result["display_name"] == "13.17 Irene"

    def test_display_name_empty_when_no_author_slug(self):
        html = "<html><body><h1>Simple Newsletter</h1><p>Content</p></body></html>"
        result = process(html, "Simple", "2025-01-15")
        assert result["display_name"] == ""

    def test_footer_removed(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert "This list is maintained" not in result["markdown"]

    def test_sdc_self_links_removed(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert "smartdrivingcar.com" not in result["markdown"].lower()

    def test_html_to_markdown_headings(self):
        html = "<html><body><h2>Section Title</h2><p>Paragraph text</p></body></html>"
        result = process(html, "Test", "2025-01-01")
        assert "## Section Title" in result["markdown"]

    def test_html_to_markdown_lists(self):
        html = "<html><body><ul><li>First</li><li>Second</li></ul></body></html>"
        result = process(html, "Test", "2025-01-01")
        assert "* First" in result["markdown"]
        assert "* Second" in result["markdown"]

    def test_date_extraction_from_content(self):
        """Date in content takes priority over received_date."""
        html = "<html><body><p>Friday, Nov. 14, 2025</p><p>Content</p></body></html>"
        result = process(html, "Test", "2025-12-01")
        assert result["date"] == "2025-11-14"

    def test_fallback_to_received_date(self):
        """When no date in content, use received_date."""
        html = "<html><body><p>Content without date</p></body></html>"
        result = process(html, "Test", "2025-06-15")
        assert result["date"] == "2025-06-15"


class TestParseDateToIso:
    def test_abbreviated_month(self):
        assert parse_date_to_iso("Thursday, Aug. 28, 2025") == "2025-08-28"

    def test_iso_passthrough(self):
        assert parse_date_to_iso("2025-01-15") == "2025-01-15"

    def test_nov_date(self):
        assert parse_date_to_iso("Friday, Nov. 14, 2025") == "2025-11-14"


class TestDeduplication:
    def test_not_duplicate_without_known_slugs(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28")
        assert result["is_duplicate"] is False

    def test_not_duplicate_with_empty_known_slugs(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28", known_slugs=[])
        assert result["is_duplicate"] is False

    def test_duplicate_when_slug_in_known_slugs(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28",
                         known_slugs=["13.17-Irene-08.28.25"])
        assert result["is_duplicate"] is True

    def test_not_duplicate_when_slug_not_in_known_slugs(self):
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28",
                         known_slugs=["different-slug", "another-slug"])
        assert result["is_duplicate"] is False

    def test_duplicate_still_returns_full_result(self):
        """Even when duplicate, the full result is returned for logging/debugging."""
        result = process(SAMPLE_HTML, "Weekly Update", "2025-08-28",
                         known_slugs=["13.17-Irene-08.28.25"])
        assert result["is_duplicate"] is True
        assert result["slug"] == "13.17-Irene-08.28.25"
        assert result["markdown"]  # Still populated
        assert result["date"] == "2025-08-28"


class TestBuildDisplayName:
    def test_with_date_suffix(self):
        assert build_display_name("13.17-Irene-11.14.25") == "13.17 Irene"

    def test_without_date_suffix(self):
        assert build_display_name("13.17-Irene") == "13.17 Irene"

    def test_simple_slug(self):
        assert build_display_name("newsletter-title") == "newsletter title"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
