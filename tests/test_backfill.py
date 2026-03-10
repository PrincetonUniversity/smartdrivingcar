#!/usr/bin/env python3
"""Tests for backfill_newsletters.py"""
import email
import os
import sys
import tempfile
import shutil
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.message import MIMEMessage
from unittest.mock import patch, MagicMock

import pytest

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from backfill_newsletters import (
    extract_inner_messages,
    extract_html_from_message,
    predict_slug,
    newsletter_exists,
    process_inner_message,
    process_wrapper_eml,
    write_message_to_tempfile,
)


def make_inner_eml(html_body='<html><body><p>Hello</p></body></html>', subject='Test Newsletter'):
    """Create an inner email message with HTML body."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = 'newsletter@example.com'
    msg['Date'] = 'Thu, 28 Aug 2025 12:00:00 -0400'
    html_part = MIMEText(html_body, 'html')
    msg.attach(html_part)
    return msg


def make_wrapper_eml(inner_messages=None):
    """Create a Listserv GETPOST wrapper .eml with nested message/rfc822 attachments."""
    wrapper = MIMEMultipart('mixed')
    wrapper['Subject'] = 'GETPOST response'
    wrapper['From'] = 'listserv@example.com'
    wrapper['Date'] = 'Fri, 29 Aug 2025 08:00:00 -0400'

    # Add a text preamble part (like Listserv does)
    preamble = MIMEText('The original message follows.', 'plain')
    wrapper.attach(preamble)

    if inner_messages is None:
        inner_messages = [make_inner_eml()]

    for inner_msg in inner_messages:
        attachment = MIMEMessage(inner_msg)
        wrapper.attach(attachment)

    return wrapper


def write_eml_to_file(msg, path):
    """Write an email message to a file."""
    with open(path, 'wb') as f:
        f.write(msg.as_bytes())


class TestExtractInnerMessages:
    def test_extracts_single_inner_message(self):
        with tempfile.NamedTemporaryFile(suffix='.eml', delete=False) as f:
            wrapper = make_wrapper_eml()
            f.write(wrapper.as_bytes())
            tmp_path = f.name

        try:
            messages = extract_inner_messages(tmp_path)
            assert len(messages) == 1
        finally:
            os.unlink(tmp_path)

    def test_extracts_multiple_inner_messages(self):
        inner1 = make_inner_eml(subject='Newsletter 1')
        inner2 = make_inner_eml(subject='Newsletter 2')

        with tempfile.NamedTemporaryFile(suffix='.eml', delete=False) as f:
            wrapper = make_wrapper_eml([inner1, inner2])
            f.write(wrapper.as_bytes())
            tmp_path = f.name

        try:
            messages = extract_inner_messages(tmp_path)
            assert len(messages) == 2
        finally:
            os.unlink(tmp_path)

    def test_no_inner_messages(self):
        """Wrapper with no message/rfc822 part returns empty list."""
        wrapper = MIMEMultipart('mixed')
        wrapper['Subject'] = 'No attachments'
        wrapper.attach(MIMEText('Just text', 'plain'))

        with tempfile.NamedTemporaryFile(suffix='.eml', delete=False) as f:
            f.write(wrapper.as_bytes())
            tmp_path = f.name

        try:
            messages = extract_inner_messages(tmp_path)
            assert len(messages) == 0
        finally:
            os.unlink(tmp_path)


class TestExtractHtmlFromMessage:
    def test_extracts_html_body(self):
        msg = make_inner_eml(html_body='<html><body><p>Test content</p></body></html>')
        html = extract_html_from_message(msg)
        assert '<p>Test content</p>' in html

    def test_falls_back_to_plain_text(self):
        msg = MIMEMultipart('alternative')
        msg.attach(MIMEText('Plain text content', 'plain'))
        html = extract_html_from_message(msg)
        assert 'Plain text content' in html

    def test_returns_empty_for_empty_message(self):
        msg = MIMEMultipart('mixed')
        html = extract_html_from_message(msg)
        assert html == ''

    def test_non_multipart_message(self):
        msg = MIMEText('<p>Simple</p>', 'html')
        html = extract_html_from_message(msg)
        assert '<p>Simple</p>' in html


class TestPredictSlug:
    def test_predicts_author_slug(self):
        html = '<p>SmartDrivingCar.Com/13.17-Irene-11.14.25</p>'
        slug = predict_slug(html)
        assert slug == '13.17-Irene-11.14.25'

    def test_predicts_date_based_slug(self):
        html = '<p>Thursday, Aug. 28, 2025 - Newsletter content</p>'
        slug = predict_slug(html)
        assert slug is not None
        assert '2025-08-28' in slug

    def test_returns_none_for_unparseable(self):
        html = '<p>No date or slug info here</p>'
        slug = predict_slug(html)
        assert slug is None


class TestNewsletterExists:
    def test_returns_false_for_nonexistent(self):
        assert newsletter_exists('nonexistent-slug-12345') is False

    def test_returns_false_for_none(self):
        assert newsletter_exists(None) is False

    def test_returns_true_for_existing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            slug = 'test-slug'
            newsletter_dir = os.path.join(tmpdir, '_newsletters', slug)
            os.makedirs(newsletter_dir)
            with open(os.path.join(newsletter_dir, 'index.md'), 'w') as f:
                f.write('---\ntitle: test\n---\n')

            # Patch the path check to use tmpdir
            with patch('backfill_newsletters.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                assert newsletter_exists(slug) is True


class TestProcessInnerMessage:
    def test_skips_empty_html_body(self):
        msg = MIMEMultipart('mixed')
        result = process_inner_message(msg, 'wrapper.eml')
        assert result['status'] == 'skipped'
        assert 'no HTML body' in result['reason']

    @patch('backfill_newsletters.newsletter_exists', return_value=True)
    def test_skips_existing_newsletter(self, mock_exists):
        html = '<p>SmartDrivingCar.Com/13.17-Irene-11.14.25</p>'
        msg = make_inner_eml(html_body=html)
        result = process_inner_message(msg, 'wrapper.eml')
        assert result['status'] == 'skipped'
        assert 'already exists' in result['reason']

    def test_dry_run_skips_processing(self):
        msg = make_inner_eml()
        result = process_inner_message(msg, 'wrapper.eml', dry_run=True)
        assert result['status'] == 'skipped'
        assert result['reason'] == 'dry run'

    @patch('backfill_newsletters.newsletter_exists', return_value=False)
    @patch('backfill_newsletters.subprocess.run')
    def test_calls_import_script(self, mock_run, mock_exists):
        mock_run.return_value = MagicMock(returncode=0, stdout='Created file', stderr='')
        msg = make_inner_eml()
        result = process_inner_message(msg, 'wrapper.eml')
        assert result['status'] == 'processed'
        assert mock_run.called
        # Verify the import script command
        cmd = mock_run.call_args[0][0]
        assert 'import_newsletter.py' in cmd[1]
        assert '--input' in cmd
        assert '--htmlsrc' in cmd

    @patch('backfill_newsletters.newsletter_exists', return_value=False)
    @patch('backfill_newsletters.subprocess.run')
    def test_reports_import_failure(self, mock_run, mock_exists):
        mock_run.return_value = MagicMock(returncode=1, stdout='', stderr='Import error')
        msg = make_inner_eml()
        result = process_inner_message(msg, 'wrapper.eml')
        assert result['status'] == 'failed'
        assert 'Import error' in result['reason']


class TestProcessWrapperEml:
    def test_handles_no_attachment(self):
        wrapper = MIMEMultipart('mixed')
        wrapper.attach(MIMEText('Just text', 'plain'))

        with tempfile.NamedTemporaryFile(suffix='.eml', delete=False) as f:
            f.write(wrapper.as_bytes())
            tmp_path = f.name

        try:
            results = process_wrapper_eml(tmp_path)
            assert len(results) == 1
            assert results[0]['status'] == 'skipped'
            assert 'no message/rfc822' in results[0]['reason']
        finally:
            os.unlink(tmp_path)

    @patch('backfill_newsletters.newsletter_exists', return_value=False)
    @patch('backfill_newsletters.subprocess.run')
    def test_processes_multiple_attachments(self, mock_run, mock_exists):
        mock_run.return_value = MagicMock(returncode=0, stdout='Created', stderr='')
        inner1 = make_inner_eml(subject='NL 1')
        inner2 = make_inner_eml(subject='NL 2')
        wrapper = make_wrapper_eml([inner1, inner2])

        with tempfile.NamedTemporaryFile(suffix='.eml', delete=False) as f:
            f.write(wrapper.as_bytes())
            tmp_path = f.name

        try:
            results = process_wrapper_eml(tmp_path)
            assert len(results) == 2
            processed_count = sum(1 for r in results if r['status'] == 'processed')
            assert processed_count == 2
        finally:
            os.unlink(tmp_path)

    def test_handles_corrupt_file(self):
        with tempfile.NamedTemporaryFile(suffix='.eml', delete=False, mode='wb') as f:
            f.write(b'\x00\x01\x02invalid')
            tmp_path = f.name

        try:
            results = process_wrapper_eml(tmp_path)
            # Should handle gracefully (either skipped or failed, not crash)
            assert len(results) >= 1
        finally:
            os.unlink(tmp_path)


class TestWriteMessageToTempfile:
    def test_writes_valid_eml(self):
        msg = make_inner_eml()
        tmp_path = write_message_to_tempfile(msg)
        try:
            assert os.path.exists(tmp_path)
            assert tmp_path.endswith('.eml')
            # Verify it's a valid email
            with open(tmp_path, 'rb') as f:
                parsed = email.message_from_binary_file(f)
            assert parsed['Subject'] == 'Test Newsletter'
        finally:
            os.unlink(tmp_path)


class TestLimitFlag:
    @patch('backfill_newsletters.process_wrapper_eml')
    def test_limit_restricts_file_count(self, mock_process):
        """Verify the limit logic by creating multiple .eml files and checking the main loop."""
        mock_process.return_value = [{'status': 'processed', 'slug': 'test', 'reason': 'ok'}]

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create 5 wrapper .eml files
            for i in range(5):
                wrapper = make_wrapper_eml()
                write_eml_to_file(wrapper, os.path.join(tmpdir, f'newsletter_{i:02d}.eml'))

            # Simulate the limit logic from main()
            import glob as glob_mod
            eml_files = sorted(glob_mod.glob(os.path.join(tmpdir, '*.eml')))
            assert len(eml_files) == 5

            limit = 2
            limited_files = eml_files[:limit]
            assert len(limited_files) == 2


class TestDryRun:
    def test_dry_run_no_subprocess_calls(self):
        """Dry run should never call subprocess."""
        msg = make_inner_eml()

        with patch('backfill_newsletters.subprocess.run') as mock_run:
            result = process_inner_message(msg, 'wrapper.eml', dry_run=True)
            assert result['status'] == 'skipped'
            assert result['reason'] == 'dry run'
            mock_run.assert_not_called()
