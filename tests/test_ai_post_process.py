"""Tests for AI post-processing of newsletter markdown.

All tests are fully mocked — no real API calls are made.
"""
import os
import sys
import tempfile
import textwrap
from unittest import mock

import pytest

# Import the module under test
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import ai_post_process


# --- split_front_matter tests ---

class TestSplitFrontMatter:
    def test_valid_front_matter(self):
        content = "---\ntitle: Test\ndate: 2024-01-01\n---\nBody content here"
        fm, body = ai_post_process.split_front_matter(content)
        assert fm == "---\ntitle: Test\ndate: 2024-01-01\n---\n"
        assert body == "Body content here"

    def test_no_front_matter(self):
        content = "Just some body content"
        fm, body = ai_post_process.split_front_matter(content)
        assert fm == ''
        assert body == "Just some body content"

    def test_empty_body(self):
        content = "---\ntitle: Test\n---\n"
        fm, body = ai_post_process.split_front_matter(content)
        assert fm == "---\ntitle: Test\n---\n"
        assert body == ""

    def test_preserves_yaml_exactly(self):
        yaml_block = "---\nlayout: newsletter\ntitle: \"Hello: World\"\ndate: 2024-01-15\npermalink: /newsletter/hello-world/\n---\n"
        content = yaml_block + "# Newsletter body"
        fm, body = ai_post_process.split_front_matter(content)
        assert fm == yaml_block
        assert body == "# Newsletter body"

    def test_front_matter_with_multiline_body(self):
        content = "---\ntitle: Test\n---\nLine 1\n\nLine 2\n\n---\n\nLine 3"
        fm, body = ai_post_process.split_front_matter(content)
        assert fm == "---\ntitle: Test\n---\n"
        # Body should include everything after front matter, including --- in body
        assert "Line 1" in body
        assert "---" in body
        assert "Line 3" in body


# --- get_client tests ---

class TestGetClient:
    def test_returns_none_without_any_key(self):
        env = {k: v for k, v in os.environ.items()
               if k not in ('AI_SANDBOX_KEY', 'OPENAI_API_KEY')}
        with mock.patch.dict(os.environ, env, clear=True):
            client = ai_post_process.get_client()
            assert client is None

    def test_returns_none_without_packages(self):
        """With OPENAI_API_KEY set but openai not installed, returns None."""
        env = {k: v for k, v in os.environ.items() if k != 'AI_SANDBOX_KEY'}
        env['OPENAI_API_KEY'] = 'test-key'
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.dict(sys.modules, {'portkey_ai': None, 'openai': None}):
                client = ai_post_process.get_client()
                assert client is None

    def test_portkey_preferred_over_openai(self):
        """When both keys set and portkey available, uses Portkey."""
        mock_client = mock.MagicMock()
        with mock.patch.dict(os.environ, {'AI_SANDBOX_KEY': 'pk-key', 'OPENAI_API_KEY': 'sk-key'}):
            with mock.patch('ai_post_process.get_client', return_value=mock_client):
                result = ai_post_process.get_client()
                assert result is mock_client

    def test_openai_fallback(self):
        """When only OPENAI_API_KEY is set, uses OpenAI client."""
        mock_openai_cls = mock.MagicMock()
        mock_client = mock.MagicMock()
        mock_openai_cls.return_value = mock_client
        mock_module = mock.MagicMock()
        mock_module.OpenAI = mock_openai_cls

        env = {k: v for k, v in os.environ.items() if k != 'AI_SANDBOX_KEY'}
        env['OPENAI_API_KEY'] = 'test-key'
        env['OPENAI_BASE_URL'] = 'https://api.example.com/v1'
        with mock.patch.dict(os.environ, env, clear=True):
            with mock.patch.dict(sys.modules, {'openai': mock_module}):
                # Force re-import inside get_client
                result = ai_post_process.get_client()
                assert result is not None


# --- process_file tests ---

class TestProcessFile:
    def test_skips_without_api_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            os.environ.pop('AI_SANDBOX_KEY', None)
            result = ai_post_process.process_file('/nonexistent/path.md')
            assert result is False

    def test_processes_with_mock_ai(self):
        content = "---\ntitle: Test\n---\nBody with color: rgb(0,0,0); artifact"
        cleaned = "Body with artifact"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            tmp_path = f.name

        try:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.choices = [mock.MagicMock()]
            mock_response.choices[0].message.content = cleaned
            mock_client.chat.completions.create.return_value = mock_response

            with mock.patch('ai_post_process.get_client', return_value=mock_client):
                result = ai_post_process.process_file(tmp_path)

            assert result is True

            with open(tmp_path, 'r') as f:
                final = f.read()

            assert final.startswith("---\ntitle: Test\n---\n")
            assert "Body with artifact" in final
            assert "color: rgb" not in final
        finally:
            os.unlink(tmp_path)

    def test_dry_run_does_not_modify_file(self):
        content = "---\ntitle: Test\n---\nOriginal body"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            tmp_path = f.name

        try:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.choices = [mock.MagicMock()]
            mock_response.choices[0].message.content = "Cleaned body"
            mock_client.chat.completions.create.return_value = mock_response

            with mock.patch('ai_post_process.get_client', return_value=mock_client):
                result = ai_post_process.process_file(tmp_path, dry_run=True)

            assert result is True

            with open(tmp_path, 'r') as f:
                final = f.read()

            assert final == content  # Unchanged
        finally:
            os.unlink(tmp_path)

    def test_preserves_front_matter(self):
        yaml_block = "---\nlayout: newsletter\ntitle: \"Special: Edition\"\ndate: 2024-01-15\n---\n"
        content = yaml_block + "Body text"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            tmp_path = f.name

        try:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.choices = [mock.MagicMock()]
            mock_response.choices[0].message.content = "Cleaned body text"
            mock_client.chat.completions.create.return_value = mock_response

            with mock.patch('ai_post_process.get_client', return_value=mock_client):
                ai_post_process.process_file(tmp_path)

            with open(tmp_path, 'r') as f:
                final = f.read()

            assert final.startswith(yaml_block)
        finally:
            os.unlink(tmp_path)

    def test_skips_empty_body(self):
        content = "---\ntitle: Test\n---\n   \n  \n"

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            tmp_path = f.name

        try:
            mock_client = mock.MagicMock()
            with mock.patch('ai_post_process.get_client', return_value=mock_client):
                result = ai_post_process.process_file(tmp_path)
            assert result is False
            mock_client.chat.completions.create.assert_not_called()
        finally:
            os.unlink(tmp_path)

    def test_file_not_found(self):
        mock_client = mock.MagicMock()
        with mock.patch('ai_post_process.get_client', return_value=mock_client):
            result = ai_post_process.process_file('/nonexistent/path.md')
        assert result is False


# --- sanitize_body tests ---

class TestSanitizeBody:
    def test_unwraps_safelinks(self):
        body = '[Click here](https://nam12.safelinks.protection.outlook.com/?url=https%3A%2F%2Fwww.example.com%2Fpage&data=05%7C01%7C&sdata=abc&reserved=0)'
        result = ai_post_process.sanitize_body(body)
        assert 'safelinks.protection.outlook.com' not in result
        assert 'https://www.example.com/page' in result

    def test_joins_multiline_link_text(self):
        body = '[NHTSA\n      Releases Initial Data](http://example.com)'
        result = ai_post_process.sanitize_body(body)
        assert result == '[NHTSA Releases Initial Data](http://example.com)'

    def test_joins_deeply_wrapped_link_text(self):
        body = '[First\n   Second\n   Third](http://example.com)'
        result = ai_post_process.sanitize_body(body)
        assert '\n' not in result.split('](')[0]
        assert 'First' in result
        assert 'Third' in result

    def test_fixes_broken_url_schemes(self):
        body = 'Visit ttp://example.com and ttps://secure.example.com'
        result = ai_post_process.sanitize_body(body)
        assert 'http://example.com' in result
        assert 'https://secure.example.com' in result

    def test_does_not_break_valid_http(self):
        body = 'Visit http://example.com and https://secure.example.com'
        result = ai_post_process.sanitize_body(body)
        assert 'http://example.com' in result
        assert 'https://secure.example.com' in result

    def test_collapses_excessive_spaces(self):
        body = 'Hello     world    here'
        result = ai_post_process.sanitize_body(body)
        assert result == 'Hello world here'

    def test_preserves_code_indentation(self):
        body = '    code block with    spaces'
        result = ai_post_process.sanitize_body(body)
        assert result == '    code block with    spaces'

    def test_collapses_excessive_blank_lines(self):
        body = 'Para 1\n\n\n\n\nPara 2'
        result = ai_post_process.sanitize_body(body)
        assert result == 'Para 1\n\n\nPara 2'

    def test_removes_empty_links(self):
        body = 'Text [](http://example.com) more text'
        result = ai_post_process.sanitize_body(body)
        assert '[](http://example.com)' not in result
        assert 'Text  more text' in result

    def test_removes_whitespace_only_links(self):
        body = 'Text [ ](http://example.com) more'
        result = ai_post_process.sanitize_body(body)
        assert '[ ](' not in result

    def test_combined_fixes(self):
        """Real-world-like input with multiple issues."""
        body = (
            '[NHTSA\n      Releases Data]'
            '(https://nam12.safelinks.protection.outlook.com/?url=https%3A%2F%2Fwww.nhtsa.gov%2Fpress&data=05&sdata=x&reserved=0)'
            '\n\n\n\n\n'
            'Some     text with ttp://broken.url'
        )
        result = ai_post_process.sanitize_body(body)
        assert '[NHTSA Releases Data]' in result
        assert 'https://www.nhtsa.gov/press' in result
        assert 'safelinks' not in result
        assert 'Some text with http://broken.url' in result
        assert '\n\n\n\n' not in result


# --- process_body tests ---

class TestProcessBody:
    def test_single_chunk_processing(self):
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.choices = [mock.MagicMock()]
        mock_response.choices[0].message.content = "cleaned text"
        mock_client.chat.completions.create.return_value = mock_response

        result = ai_post_process.process_body("dirty text", mock_client)
        assert result == "cleaned text"
        mock_client.chat.completions.create.assert_called_once()

    def test_model_parameter_passed(self):
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.choices = [mock.MagicMock()]
        mock_response.choices[0].message.content = "cleaned"
        mock_client.chat.completions.create.return_value = mock_response

        ai_post_process.process_body("text", mock_client, model="custom-model")

        call_kwargs = mock_client.chat.completions.create.call_args
        assert call_kwargs[1]['model'] == "custom-model"
        assert call_kwargs[1]['temperature'] == 0.0


# --- chunking tests ---

class TestChunking:
    def test_small_body_not_chunked(self):
        chunks = ai_post_process._chunk_body("small text", threshold=100)
        assert len(chunks) == 1
        assert chunks[0] == "small text"

    def test_large_body_chunked(self):
        # Create text larger than threshold
        para1 = "A" * 60
        para2 = "B" * 60
        body = para1 + "\n\n" + para2
        chunks = ai_post_process._chunk_body(body, threshold=80)
        assert len(chunks) == 2


# --- CLI tests ---

class TestCLI:
    def test_multiple_files(self):
        files = []
        for i in range(3):
            f = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False)
            f.write(f"---\ntitle: Test {i}\n---\nBody {i}")
            f.close()
            files.append(f.name)

        try:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.choices = [mock.MagicMock()]
            mock_response.choices[0].message.content = "cleaned"
            mock_client.chat.completions.create.return_value = mock_response

            with mock.patch('ai_post_process.get_client', return_value=mock_client):
                with mock.patch('sys.argv', ['ai_post_process.py'] + files):
                    ai_post_process.main()

            assert mock_client.chat.completions.create.call_count == 3
        finally:
            for f in files:
                os.unlink(f)

    def test_exit_code_on_failure(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("---\ntitle: Test\n---\nBody")
            tmp_path = f.name

        try:
            mock_client = mock.MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API error")

            with mock.patch('ai_post_process.get_client', return_value=mock_client):
                with mock.patch('sys.argv', ['ai_post_process.py', tmp_path]):
                    with pytest.raises(SystemExit) as exc_info:
                        ai_post_process.main()
                    assert exc_info.value.code == 1
        finally:
            os.unlink(tmp_path)
