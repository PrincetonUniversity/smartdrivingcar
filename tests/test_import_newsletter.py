#!/usr/bin/env python3
"""Tests for import_newsletter.py"""
import pytest
import os
import sys
import tempfile
import shutil

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from import_newsletter import (
    slugify,
    html_to_markdown,
    extract_body_from_eml,
    extract_first_date,
    remove_sdc_line,
    add_margins_to_markdown
)


class TestSlugify:
    def test_basic_slug(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_characters(self):
        assert slugify("Test!@#$%^&*()Title") == "test-title"

    def test_preserves_dots(self):
        assert slugify("Version 1.2.3") == "version-1.2.3"

    def test_empty_string(self):
        assert slugify("") == "issue"

    def test_unicode_normalization(self):
        assert slugify("Café résumé") == "cafe-resume"


class TestHtmlToMarkdown:
    def test_basic_paragraph(self):
        html = "<p>Hello World</p>"
        result = html_to_markdown(html)
        assert "Hello World" in result

    def test_heading_conversion(self):
        html = "<h1>Title</h1>"
        result = html_to_markdown(html)
        assert "# Title" in result

    def test_link_conversion(self):
        html = '<a href="http://example.com">Example</a>'
        result = html_to_markdown(html)
        assert "[Example](http://example.com)" in result

    def test_list_conversion(self):
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        result = html_to_markdown(html)
        assert "* Item 1" in result
        assert "* Item 2" in result

    def test_br_conversion(self):
        html = "Line 1<br>Line 2"
        result = html_to_markdown(html)
        assert "Line 1\nLine 2" in result

    def test_entity_decoding(self):
        html = "<p>Hello &amp; World</p>"
        result = html_to_markdown(html)
        assert "Hello & World" in result

    def test_removes_script_tags(self):
        html = "<script>alert('test');</script><p>Content</p>"
        result = html_to_markdown(html)
        assert "alert" not in result
        assert "Content" in result

    def test_removes_style_tags(self):
        html = "<style>.test { color: red; }</style><p>Content</p>"
        result = html_to_markdown(html)
        assert "color" not in result
        assert "Content" in result


class TestExtractFirstDate:
    def test_finds_date(self):
        text = "Newsletter for Thursday, Aug. 28, 2025"
        result = extract_first_date(text)
        assert result == "Thursday, Aug. 28, 2025"

    def test_no_date_returns_none(self):
        text = "No date here"
        result = extract_first_date(text)
        assert result is None

    def test_various_days(self):
        text = "Published Monday, Jan. 1, 2025"
        result = extract_first_date(text)
        assert result == "Monday, Jan. 1, 2025"


class TestRemoveSdcLine:
    def test_removes_markdown_link(self):
        text = "Line 1\n[Visit us](https://smartdrivingcar.com)\nLine 2"
        result = remove_sdc_line(text)
        assert "smartdrivingcar.com" not in result
        assert "Line 1" in result
        assert "Line 2" in result

    def test_removes_html_link(self):
        text = 'Line 1\n<a href="https://smartdrivingcar.com">Visit</a>\nLine 2'
        result = remove_sdc_line(text)
        assert "smartdrivingcar.com" not in result

    def test_preserves_other_lines(self):
        text = "Line 1\nLine 2\nLine 3"
        result = remove_sdc_line(text)
        assert result == text


class TestAddMarginsToMarkdown:
    def test_strips_whitespace(self):
        md = "  Content  \n\n"
        result = add_margins_to_markdown(md)
        assert result == "Content\n"


class TestExtractBodyFromEml:
    def test_simple_eml(self):
        # Create a simple .eml file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.eml', delete=False) as f:
            eml_content = b"""From: sender@example.com
To: recipient@example.com
Subject: Test Newsletter
Content-Type: text/html; charset="utf-8"

<html><body><p>Test content</p></body></html>
"""
            f.write(eml_content)
            temp_path = f.name

        try:
            result = extract_body_from_eml(temp_path)
            assert "Test content" in result
        finally:
            os.unlink(temp_path)

    def test_multipart_eml(self):
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.eml', delete=False) as f:
            eml_content = b"""From: sender@example.com
To: recipient@example.com
Subject: Test Newsletter
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="boundary123"

--boundary123
Content-Type: text/plain; charset="utf-8"

Plain text version

--boundary123
Content-Type: text/html; charset="utf-8"

<html><body><p>HTML version</p></body></html>

--boundary123--
"""
            f.write(eml_content)
            temp_path = f.name

        try:
            result = extract_body_from_eml(temp_path)
            # Should prefer HTML over plain text
            assert "HTML version" in result
        finally:
            os.unlink(temp_path)


class TestIntegration:
    """Integration tests that run the main script"""

    def test_creates_newsletter_file(self):
        # Create a temporary directory to act as the project root
        with tempfile.TemporaryDirectory() as tmpdir:
            newsletters_dir = os.path.join(tmpdir, '_newsletters')
            os.makedirs(newsletters_dir)

            # Create test HTML input
            html_input = "<html><body><h1>Test Newsletter</h1><p>Content here</p></body></html>"
            input_file = os.path.join(tmpdir, 'test.html')
            with open(input_file, 'w') as f:
                f.write(html_input)

            # Change to temp directory and run script
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                import subprocess
                result = subprocess.run([
                    sys.executable,
                    os.path.join(original_cwd, 'scripts', 'import_newsletter.py'),
                    '--date', '2025-01-15',
                    '--title', 'Test Issue',
                    '--input', input_file
                ], capture_output=True, text=True)

                # Check that a file was created
                assert "Created" in result.stdout
                # Check newsletter directory exists
                assert os.path.exists(newsletters_dir)
            finally:
                os.chdir(original_cwd)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
