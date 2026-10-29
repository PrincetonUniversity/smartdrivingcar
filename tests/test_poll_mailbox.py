"""Graph reconciliation uses mock services; no mailbox credentials needed."""

import sys
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import pipeline_http
import poll_mailbox
from publish_newsletter import parse_newsletter, write_issue

SETTINGS = {
    "mailbox": "mailbox@example.org",
    "author": "author@example.org",
    "list": "smartdrivingcars@princeton.edu",
    "days": 90,
}
BODY = (
    "<h2>Headline</h2><p>"
    + "An accessible mobility newsletter with original commentary. " * 4
    + "</p>"
)
MESSAGE = {
    "id": "opaque/id",
    "subject": "SmartDrivingCars_14.16-badMedia-10.22.26",
    "from": {"emailAddress": {"address": SETTINGS["author"]}},
    "sender": {"emailAddress": {"address": SETTINGS["list"]}},
    "toRecipients": [{"emailAddress": {"address": SETTINGS["list"]}}],
    "receivedDateTime": "2026-10-22T22:17:13Z",
    "isRead": True,
}
DETAIL = {
    "body": {"contentType": "html", "content": BODY},
    "internetMessageHeaders": [
        {
            "name": "List-Help",
            "value": "<https://lists.princeton.edu/cgi-bin/wa?LIST=SmartDrivingCars>",
        }
    ],
}


def test_reconcile_includes_read_messages_and_follows_pages(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with patch.object(
        poll_mailbox,
        "request_json",
        side_effect=[
            {"value": [MESSAGE], "@odata.nextLink": "https://graph.microsoft.com/v1.0/next"},
            DETAIL,
            {"value": []},
        ],
    ) as api:
        report = poll_mailbox.reconcile(SETTINGS, "token", root=tmp_path)
    assert report["created"] == 1
    assert report["scanned"] == 1
    assert api.call_count == 3
    first_url = api.call_args_list[0].args[0]
    assert "isRead" not in first_url
    assert "/users/mailbox%40example.org/messages?" in first_url
    assert "opaque%2Fid" in api.call_args_list[1].args[0]


def test_poll_retries_do_not_overwrite_or_duplicate(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    for expected in [1, 0]:
        with patch.object(poll_mailbox, "request_json", side_effect=[{"value": [MESSAGE]}, DETAIL]):
            report = poll_mailbox.reconcile(SETTINGS, "token", root=tmp_path)
        assert report["created"] == expected
    assert len(list((tmp_path / "_newsletters").glob("*/index.md"))) == 1
    assert report["duplicates"] == 1


def test_unrelated_or_spoofed_mail_is_never_published(tmp_path):
    wrong = {**MESSAGE, "from": {"emailAddress": {"address": "evil@example.org"}}}
    with patch.object(poll_mailbox, "request_json", return_value={"value": [wrong]}) as api:
        report = poll_mailbox.reconcile(SETTINGS, "token", root=tmp_path)
    assert report["scanned"] == 1 and report["created"] == 0
    assert api.call_count == 1
    assert not (tmp_path / "_newsletters").exists()


def test_missing_list_headers_fail_without_writing(tmp_path):
    with patch.object(
        poll_mailbox,
        "request_json",
        side_effect=[{"value": [MESSAGE]}, {**DETAIL, "internetMessageHeaders": []}],
    ):
        with pytest.raises(ValueError, match="Listserv headers"):
            poll_mailbox.reconcile(SETTINGS, "token", root=tmp_path)
    assert not (tmp_path / "_newsletters").exists()


def test_dry_run_does_not_write_or_mark_mail_read(tmp_path):
    with patch.object(poll_mailbox, "request_json", side_effect=[{"value": [MESSAGE]}, DETAIL]):
        report = poll_mailbox.reconcile(SETTINGS, "token", root=tmp_path, dry_run=True)
    assert report["dry_run"] is True
    assert report["issues"] == ["14.16-badMedia-10.22.26"]
    assert not (tmp_path / "_newsletters").exists()


def test_content_conflict_fails(tmp_path):
    write_issue(parse_newsletter(BODY, MESSAGE["subject"], MESSAGE["receivedDateTime"]), tmp_path)
    with patch.object(
        poll_mailbox,
        "request_json",
        side_effect=[
            {"value": [MESSAGE]},
            {**DETAIL, "body": {"contentType": "html", "content": BODY + "<p>Different</p>"}},
        ],
    ):
        with pytest.raises(ValueError, match="conflict"):
            poll_mailbox.reconcile(SETTINGS, "token", root=tmp_path)


def test_malicious_pagination_url_never_receives_token():
    with patch.object(pipeline_http, "build_opener") as opener:
        with pytest.raises(ValueError, match="Disallowed"):
            pipeline_http.request_json(
                "https://evil.example/v1.0/next",
                host="graph.microsoft.com",
                headers={"Authorization": "Bearer private"},
            )
    opener.assert_not_called()


def test_graph_retries_throttling_and_transient_failures():
    error = HTTPError("https://graph.microsoft.com/", 429, "throttled", {"Retry-After": "1"}, None)
    with (
        patch.object(pipeline_http, "build_opener") as factory,
        patch.object(pipeline_http.time, "sleep") as sleep,
    ):
        response = factory.return_value.open.return_value.__enter__.return_value
        response.read.return_value = b'{"value": []}'
        factory.return_value.open.side_effect = [error, factory.return_value.open.return_value]
        result = pipeline_http.request_json(
            "https://graph.microsoft.com/v1.0/users", host="graph.microsoft.com"
        )
    assert result == {"value": []}
    sleep.assert_called_once_with(1)


def test_bad_config_fails_before_token_lookup(monkeypatch):
    monkeypatch.delenv("NEWSLETTER_MAILBOX", raising=False)
    with pytest.raises(ValueError, match="Set valid"):
        poll_mailbox.config()


def test_optional_freshness_detects_stopped_list_delivery(tmp_path):
    with patch.object(poll_mailbox, "request_json", return_value={"value": []}):
        with pytest.raises(ValueError, match="freshness"):
            poll_mailbox.reconcile({**SETTINGS, "max_age_days": 21}, "token", root=tmp_path)


def test_commissioning_requires_actual_negative_control_denial(monkeypatch):
    import commission_mailbox
    from pipeline_http import APIError

    monkeypatch.setenv("NEWSLETTER_NEGATIVE_TEST_MAILBOX", "control@example.org")
    with (
        patch.object(commission_mailbox, "config", return_value=SETTINGS),
        patch.object(commission_mailbox, "graph_token", return_value="private-token"),
        patch.object(commission_mailbox, "request_json", side_effect=[{}, APIError(403)]),
        patch.object(
            commission_mailbox, "reconcile", return_value={"issues": ["14.16-badMedia-10.22.26"]}
        ) as preview,
    ):
        commission_mailbox.commission()
    assert preview.call_args.kwargs["dry_run"] is True


def test_commissioning_rejects_tenant_wide_access(monkeypatch):
    import commission_mailbox

    monkeypatch.setenv("NEWSLETTER_NEGATIVE_TEST_MAILBOX", "control@example.org")
    with (
        patch.object(commission_mailbox, "config", return_value=SETTINGS),
        patch.object(commission_mailbox, "graph_token", return_value="private-token"),
        patch.object(commission_mailbox, "request_json", return_value={}),
    ):
        with pytest.raises(RuntimeError, match="Isolation failure"):
            commission_mailbox.commission()
