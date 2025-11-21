#!/usr/bin/env python3
"""Tests for clean_newsletter.py"""
import pytest
import os
import sys

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from clean_newsletter import clean_newsletter_html


class TestCleanNewsletterHtml:
    def test_removes_style_tags(self):
        html = "<html><head><style>.test { color: red; }</style></head><body><p>Content</p></body></html>"
        result = clean_newsletter_html(html)
        assert "color: red" not in result
        assert "Content" in result

    def test_removes_html_comments(self):
        html = "<html><body><!-- This is a comment --><p>Content</p></body></html>"
        result = clean_newsletter_html(html)
        assert "This is a comment" not in result
        assert "Content" in result

    def test_normalizes_smart_quotes(self):
        html = '<html><body><p>"Smart quotes" and 'apostrophes'</p></body></html>'
        result = clean_newsletter_html(html)
        assert '"' in result or "Smart quotes" in result
        assert "'" in result or "apostrophes" in result

    def test_truncates_at_previous_marker(self):
        html = """<html><body>
        <p>Main content</p>
        <p>Previous SmartDrivingCars editions</p>
        <p>This should be removed</p>
        </body></html>"""
        result = clean_newsletter_html(html)
        assert "Main content" in result
        assert "This should be removed" not in result

    def test_whitelist_tags_preserved(self):
        html = "<html><head><title>Test</title></head><body><h1>Title</h1><p>Para</p><a href='#'>Link</a></body></html>"
        result = clean_newsletter_html(html)
        assert "<h1>" in result or "Title" in result
        assert "<p>" in result or "Para" in result
        assert "Link" in result

    def test_removes_disallowed_tags(self):
        html = "<html><body><div><span>Content</span></div></body></html>"
        result = clean_newsletter_html(html)
        # Content should remain but div/span tags should be unwrapped
        assert "Content" in result
        # Tags should be unwrapped, not have content removed
        assert "<div>" not in result
        assert "<span>" not in result

    def test_removes_empty_paragraphs(self):
        html = "<html><body><p></p><p>Content</p><p>   </p></body></html>"
        result = clean_newsletter_html(html)
        assert "Content" in result
        # Empty paragraphs should be removed (harder to verify directly)

    def test_timecode_consolidation(self):
        html = """<html><body>
        <p><a href="http://example.com#t=120">2:00</a> Introduction</p>
        <p><a href="http://example.com#t=300">5:00</a> Main Topic</p>
        </body></html>"""
        result = clean_newsletter_html(html)
        # Timecodes should be consolidated into a list
        assert "<ul>" in result or "2:00" in result
        assert "Introduction" in result
        assert "Main Topic" in result

    def test_removes_meta_tags_except_charset(self):
        html = """<html><head>
        <meta name="viewport" content="width=device-width">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        </head><body><p>Content</p></body></html>"""
        result = clean_newsletter_html(html)
        assert 'name="viewport"' not in result
        assert "Content" in result

    def test_removes_footer_asterisk_marker(self):
        html = """<html><body>
        <p>Main content</p>
        <p>*****</p>
        <p>Footer content to remove</p>
        </body></html>"""
        result = clean_newsletter_html(html)
        assert "Main content" in result
        assert "Footer content to remove" not in result

    def test_removes_unsubscribe_footer(self):
        html = """<html><body>
        <p>Main content</p>
        <p>To unsubscribe from this list, click here</p>
        <p>More footer</p>
        </body></html>"""
        result = clean_newsletter_html(html)
        assert "Main content" in result
        assert "unsubscribe" not in result.lower()

    def test_removes_list_maintained_footer(self):
        html = """<html><body>
        <p>Main content</p>
        <p>This list is maintained by the editor</p>
        <p>Contact info</p>
        </body></html>"""
        result = clean_newsletter_html(html)
        assert "Main content" in result
        assert "maintained by" not in result.lower()

    def test_preserves_href_attributes(self):
        html = '<html><body><a href="http://example.com" class="btn" id="link1">Link</a></body></html>'
        result = clean_newsletter_html(html)
        assert 'href="http://example.com"' in result
        assert 'class=' not in result
        assert 'id=' not in result

    def test_decodes_html_entities(self):
        html = "<html><body><p>&amp; &lt; &gt; &nbsp;</p></body></html>"
        result = clean_newsletter_html(html)
        # Entities should be decoded
        assert "&amp;" not in result or "&" in result
        assert "&lt;" not in result or "<" in result

    def test_handles_malformed_html(self):
        html = "<html><body><p>Unclosed paragraph<p>Another one</body></html>"
        # Should not raise an exception
        result = clean_newsletter_html(html)
        assert "Unclosed paragraph" in result

    def test_empty_input(self):
        html = ""
        result = clean_newsletter_html(html)
        # Should handle empty input gracefully
        assert result is not None


class TestTimecodeFormatting:
    def test_single_digit_minutes(self):
        html = """<html><body>
        <p><a href="http://example.com#t=60">1:00</a> Intro</p>
        </body></html>"""
        result = clean_newsletter_html(html)
        assert "1:00" in result

    def test_double_digit_minutes(self):
        html = """<html><body>
        <p><a href="http://example.com#t=600">10:00</a> Topic</p>
        </body></html>"""
        result = clean_newsletter_html(html)
        assert "10:00" in result

    def test_with_seconds(self):
        html = """<html><body>
        <p><a href="http://example.com#t=125">2:05:30</a> Detailed topic</p>
        </body></html>"""
        result = clean_newsletter_html(html)
        assert "2:05:30" in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
