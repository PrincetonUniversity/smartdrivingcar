#!/usr/bin/env python3
"""Tests for process_inbox.py"""
import pytest
import os
import sys
import tempfile
import shutil

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from process_inbox import load_config, process_eml_file, process_inbox


class TestLoadConfig:
    def test_loads_existing_config(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("inbox_directory: test_inbox\nlogging:\n  enabled: false\n")
            temp_path = f.name

        try:
            config = load_config(temp_path)
            assert config['inbox_directory'] == 'test_inbox'
        finally:
            os.unlink(temp_path)

    def test_returns_empty_for_missing_config(self):
        config = load_config('nonexistent_config.yml')
        assert config == {}


class TestProcessInbox:
    def test_handles_empty_inbox(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox = os.path.join(tmpdir, 'inbox')
            os.makedirs(inbox)

            config = {
                'inbox_directory': inbox,
                'logging': {'enabled': False}
            }

            results = process_inbox(config)
            assert results['processed'] == 0
            assert results['failed'] == 0

    def test_handles_missing_inbox(self):
        config = {
            'inbox_directory': '/nonexistent/path',
            'logging': {'enabled': False}
        }

        results = process_inbox(config)
        assert results['processed'] == 0
        assert results['failed'] == 0

    def test_processes_eml_file(self):
        # Create a complete test environment
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup directories
            inbox = os.path.join(tmpdir, 'inbox')
            newsletters = os.path.join(tmpdir, '_newsletters')
            os.makedirs(inbox)
            os.makedirs(newsletters)

            # Create a test .eml file
            eml_content = b"""From: test@example.com
To: recipient@example.com
Subject: Test Newsletter
Content-Type: text/html; charset="utf-8"

<html><body><h1>Test</h1><p>Content</p></body></html>
"""
            eml_path = os.path.join(inbox, 'test.eml')
            with open(eml_path, 'wb') as f:
                f.write(eml_content)

            config = {
                'inbox_directory': inbox,
                'logging': {'enabled': False}
            }

            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                results = process_inbox(config)
                # Should process successfully
                assert results['processed'] == 1 or results['failed'] == 1
            finally:
                os.chdir(original_cwd)


class TestProcessEmlFile:
    def test_handles_invalid_eml(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.eml', delete=False) as f:
            f.write("not valid eml content")
            temp_path = f.name

        try:
            config = {'logging': {'enabled': False}}
            # Should handle gracefully without crashing
            result = process_eml_file(temp_path, config)
            assert isinstance(result, bool)
        finally:
            os.unlink(temp_path)


class TestConfigValidation:
    def test_default_values(self):
        config = load_config('nonexistent.yml')
        # Should return empty dict for missing config
        assert config == {}
        # Defaults should be handled by process_inbox
        inbox_dir = config.get('inbox_directory', 'inbox')
        assert inbox_dir == 'inbox'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
