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
    remove_security_banner,
    add_margins_to_markdown,
    extract_slug_from_subject,
    extract_author_slug,
    extract_slug_from_filename,
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


BANNER = (
    "\u26a0 SECURITY WARNING\n\n"
    "This email links to a Google Form.\n\n"
    "Do not\xa0enter your password or Duo code\xa0in the form.\n\n"
    "Princeton University will never ask for your login credentials. "
    "If the message is suspicious, report it to the Phish Bowl at phishbowl@princeton.edu\n\n"
)


class TestRemoveSecurityBanner:
    def test_removes_banner_at_top(self):
        md = BANNER + "Hello from Peru\n\nMore text\n"
        result = remove_security_banner(md)
        assert "SECURITY WARNING" not in result
        assert "phishbowl" not in result.lower()
        assert "Google Form" not in result
        assert result.startswith("Hello from Peru")
        assert "More text" in result

    def test_removes_banner_mid_document(self):
        md = "Intro\n\n" + BANNER + "Body\n"
        result = remove_security_banner(md)
        assert "SECURITY WARNING" not in result
        assert result == "Intro\n\nBody\n"

    def test_keeps_lone_security_warning_text(self):
        md = "A SECURITY WARNING was issued by NHTSA.\n\nDetails follow.\n"
        assert remove_security_banner(md) == md

    def test_keeps_text_when_end_marker_too_far(self):
        md = "SECURITY WARNING\n" + "line\n" * 20 + "Phish Bowl\n"
        assert remove_security_banner(md) == md

    def test_no_banner_unchanged(self):
        md = "Line 1\nLine 2\n"
        assert remove_security_banner(md) == md


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

    def test_eml_import_strips_security_banner(self):
        """A Princeton gateway banner in an .eml must not reach the published page."""
        with tempfile.TemporaryDirectory() as tmpdir:
            eml_path = os.path.join(tmpdir, 'SmartDrivingCars_14.99-Banner-9.30.26.eml')
            html = (
                "<html><body>"
                "<table><tr><td><p><b>\u26a0 SECURITY WARNING</b></p>"
                "<p>This email links to a Google Form.</p>"
                "<p>Do not enter your password or Duo code in the form.</p>"
                "<p>Princeton University will never ask for your login credentials. "
                "If the message is suspicious, report it to the Phish Bowl at "
                "<a href=\"mailto:phishbowl@princeton.edu\">phishbowl@princeton.edu</a></p>"
                "</td></tr></table>"
                "<p>Hello from Peru</p><p>Newsletter body text</p>"
                "</body></html>"
            )
            eml = (
                "From: sender@example.com\n"
                "Subject: SmartDrivingCars_14.99-Banner-9.30.26\n"
                "Date: Wed, 30 Sep 2026 12:00:00 +0000\n"
                "MIME-Version: 1.0\n"
                "Content-Type: text/html; charset=\"utf-8\"\n\n" + html + "\n"
            )
            with open(eml_path, 'w', encoding='utf-8') as f:
                f.write(eml)

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                import subprocess
                result = subprocess.run([
                    sys.executable,
                    os.path.join(original_cwd, 'scripts', 'import_newsletter.py'),
                    '--input', eml_path,
                ], capture_output=True, text=True)
                assert result.returncode == 0, result.stderr
                out = os.path.join(tmpdir, '_newsletters', '14.99-Banner-9.30.26', 'index.md')
                assert os.path.exists(out), result.stdout + result.stderr
                with open(out, encoding='utf-8') as f:
                    content = f.read()
                assert "Newsletter body text" in content
                assert "SECURITY WARNING" not in content
                assert "Google Form" not in content
                assert "phishbowl" not in content.lower()
            finally:
                os.chdir(original_cwd)


class TestExtractSlugFromSubject:
    def test_extract_slug_with_domain_prefix(self):
        subject = "SmartDrivingCar.com/13.01-Welcome Back -2/2/24"
        assert extract_slug_from_subject(subject) == "13.01-Welcome-Back-2-2-24"

    def test_extract_slug_direct_patterns(self):
        subject1 = "SmartDrivingCar-14.10-SevalOz-5.23.26"
        assert extract_slug_from_subject(subject1) == "14.10-SevalOz-5.23.26"

        subject2 = "SmartDrivingCars eLetter...14.11-BocaRatonAV_Conference-6.02.26"
        assert extract_slug_from_subject(subject2) == "14.11-BocaRatonAV-Conference-6.02.26"

        # Subject with spaces after prefix
        subject3 = "SmartDrivingCars_14.12-Last Straw-6.26.26"
        assert extract_slug_from_subject(subject3) == "14.12-Last-Straw-6.26.26"

    def test_extract_slug_invalid_or_missing(self):
        assert extract_slug_from_subject("Hello World") is None
        assert extract_slug_from_subject("SmartDrivingCars Newsletter - Aug. 28, 2025") is None


class TestExtractSlugFromFilename:
    def test_extract_slug_html(self):
        assert extract_slug_from_filename("import/14.12-Last Straw-6.26.26.html") == "14.12-Last-Straw-6.26.26"

    def test_extract_slug_eml(self):
        assert extract_slug_from_filename("import/SmartDrivingCars_14.12-Last Straw-6.26.26.eml") == "14.12-Last-Straw-6.26.26"
        assert extract_slug_from_filename("inbox/SmartDrivingCars eLetter...14.11-BocaRatonAV_Conference-6.02.26.eml") == "14.11-BocaRatonAV-Conference-6.02.26"

    def test_extract_slug_invalid(self):
        assert extract_slug_from_filename("import/random-file.html") is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
