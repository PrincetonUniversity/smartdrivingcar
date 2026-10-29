"""Contract tests for the existing authorized Outlook connector publishing path."""

import copy
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from connector_batch import prepare_batch, receive_batch

BODY = (
    "<h2>Accessible transport</h2><p>"
    + "Original newsletter commentary about accessible autonomous mobility. " * 4
    + "</p>"
)
SUBJECT = "SmartDrivingCars_14.16-badMedia-10.22.26"
MESSAGE = {
    "subject": SUBJECT,
    "body": BODY,
    "receivedDateTime": "2026-10-22T22:17:13Z",
    "from": "alaink@princeton.edu",
    "toRecipients": "smartdrivingcars@princeton.edu",
    "internetMessageHeaders": [
        {
            "name": "List-Help",
            "value": "<https://lists.princeton.edu/cgi-bin/wa?LIST=SmartDrivingCars>",
        }
    ],
}
SETTINGS = {
    "author": "alaink@princeton.edu",
    "list": "smartdrivingcars@princeton.edu",
    "repository": "PrincetonUniversity/smartdrivingcar",
    "limit": 100,
}
CORRELATION = "12345678-1234-4234-8234-123456789abc"


def batch(mode="test", messages=None, known=None):
    return prepare_batch(
        messages if messages is not None else [MESSAGE],
        mode,
        CORRELATION,
        SETTINGS,
        known if known is not None else set(),
    )


def test_test_mode_exercises_existing_issue_without_network():
    with patch("connector_batch.request_json") as api:
        result = batch(known={"14.16-badMedia-10.22.26"})
    api.assert_not_called()
    assert result["mode"] == "test"
    assert len(result["issues"]) == 1
    assert result["correlation_id"] == CORRELATION


def test_production_duplicate_uses_verification_manifest():
    result = batch("production", known={"14.16-badMedia-10.22.26"})
    assert result["issues"] == []
    assert result["verify_slugs"] == ["14.16-badMedia-10.22.26"]


def test_test_receiver_never_writes_to_repository(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    preview = tmp_path / "preview"
    result = receive_batch(batch(), mode="test", root=repo, preview=preview)
    assert not (repo / "_newsletters").exists()
    assert (preview / "_newsletters" / "14.16-badMedia-10.22.26" / "index.md").is_file()
    assert result["validated"] == 1


def test_test_event_cannot_be_received_as_production(tmp_path):
    with pytest.raises(ValueError, match="mode"):
        receive_batch(batch(), mode="production", root=tmp_path)
    assert not (tmp_path / "_newsletters").exists()


def test_bounded_batch_does_not_silently_drop_backlog():
    messages = []
    for issue in range(1, 6):
        msg = copy.deepcopy(MESSAGE)
        msg["subject"] = f"SmartDrivingCars_14.{issue}-Article-10.22.26"
        msg["body"] = "<p>" + ("Large commentary. " * 1200) + "</p>"
        messages.append(msg)
    result = batch("production", messages)
    assert 0 < len(result["issues"]) < len(messages)
    assert result["remaining"] == len(messages) - len(result["issues"])
    assert (
        len(
            json.dumps(
                {"event_type": "newsletter-connector-batch", "client_payload": result}
            ).encode()
        )
        < 60_000
    )


def test_full_connector_page_fails_instead_of_skipping_older_messages():
    with pytest.raises(ValueError, match="limit"):
        prepare_batch([MESSAGE] * 100, "test", CORRELATION, SETTINGS, set())


def test_sender_and_list_are_validated_before_publication():
    bad = {**MESSAGE, "from": "unapproved@example.org"}
    result = batch(messages=[bad])
    assert not result["issues"] and result["rejected"] == 1


def test_email_html_is_sanitized_on_both_sides(tmp_path):
    msg = {**MESSAGE, "body": BODY + "<script>bad()</script><p>{{ site.title }}</p>"}
    payload = batch(messages=[msg])
    assert "<script>" not in json.dumps(payload)
    receive_batch(payload, mode="test", root=tmp_path / "repo", preview=tmp_path / "preview")
    content = next((tmp_path / "preview" / "_newsletters").glob("*/index.md")).read_text()
    assert "<script>" not in content and "{{ site.title }}" not in content


def test_no_content_in_test_report(tmp_path):
    report = receive_batch(
        batch(), mode="test", root=tmp_path / "repo", preview=tmp_path / "preview"
    )
    encoded = json.dumps(report)
    assert "Original newsletter commentary" not in encoded
    assert "alaink@" not in encoded
    assert report["mode"] == "test"


def test_function_handler_rejects_malformed_batches_without_logging_body(monkeypatch, caplog):
    import importlib.util

    import azure.functions as func

    for key, value in {
        "SDC_ALLOWED_AUTHOR": SETTINGS["author"],
        "SDC_LIST_ADDRESS": SETTINGS["list"],
        "SDC_GITHUB_REPOSITORY": SETTINGS["repository"],
    }.items():
        monkeypatch.setenv(key, value)
    spec = importlib.util.spec_from_file_location(
        "connector_handler_test", "azure/functions/connector_handler.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    handler = module.prepare_connector_batch.build().get_user_function()
    request = func.HttpRequest(
        method="POST",
        url="/api/prepare-connector-batch",
        body=b'{"messages":"private mail body","mode":"invalid"}',
    )
    response = handler(request)
    assert response.status_code == 400
    assert "private mail body" not in caplog.text
    request = func.HttpRequest(
        method="POST",
        url="/api/prepare-connector-batch",
        body=json.dumps(
            {"messages": [MESSAGE], "mode": "test", "correlation_id": CORRELATION}
        ).encode(),
    )
    response = handler(request)
    assert response.status_code == 200
    assert json.loads(response.get_body())["accepted"] == 1


def test_managed_existing_issue_conflict_is_visible():
    with (
        patch("connector_batch.known_newsletters", return_value={"14.16-badMedia-10.22.26"}),
        patch(
            "connector_batch.public_metadata",
            return_value={"source_sha256": "old", "source_authority": "mailbox"},
        ),
    ):
        with pytest.raises(ValueError, match="conflict"):
            prepare_batch([MESSAGE], "production", CORRELATION, SETTINGS)


def test_renderer_is_stable_across_function_and_receiver():
    from publish_newsletter import parse_newsletter, safe_html

    direct = parse_newsletter(BODY, SUBJECT, "2026-10-22")
    via_function = parse_newsletter(safe_html(BODY), SUBJECT, "2026-10-22")
    assert direct == via_function
