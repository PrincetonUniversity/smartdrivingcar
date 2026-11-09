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
        result = prepare_batch([MESSAGE], "production", CORRELATION, SETTINGS)
    assert len(result["invalid_details"]) == 1
    assert result["invalid_details"] == [
        {"reason": "content_conflict", "received": MESSAGE["receivedDateTime"]}
    ]
    assert result["verify_slugs"] == []


def test_renderer_is_stable_across_function_and_receiver():
    from publish_newsletter import parse_newsletter, safe_html

    direct = parse_newsletter(BODY, SUBJECT, "2026-10-22")
    via_function = parse_newsletter(safe_html(BODY), SUBJECT, "2026-10-22")
    assert direct == via_function


def test_function_returns_safe_validation_reason_for_operators(monkeypatch):
    import importlib.util

    import azure.functions as func

    for key, value in {
        "SDC_ALLOWED_AUTHOR": SETTINGS["author"],
        "SDC_LIST_ADDRESS": SETTINGS["list"],
        "SDC_GITHUB_REPOSITORY": SETTINGS["repository"],
    }.items():
        monkeypatch.setenv(key, value)
    spec = importlib.util.spec_from_file_location(
        "connector_handler_reason_test", "azure/functions/connector_handler.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    handler = module.prepare_connector_batch.build().get_user_function()
    invalid = {**MESSAGE, "subject": "SmartDrivingCars_14.16-Date-99.99.26"}
    request = func.HttpRequest(
        method="POST",
        url="/api/prepare-connector-batch",
        body=json.dumps(
            {"messages": [invalid], "mode": "test", "correlation_id": CORRELATION}
        ).encode(),
    )
    response = handler(request)
    # A bad newsletter is reported per message; the rest of the batch proceeds.
    assert response.status_code == 200
    assert json.loads(response.get_body())["invalid_details"] == [
        {"reason": "invalid_issue_date", "received": MESSAGE["receivedDateTime"]}
    ]
    # A problem with the batch itself still rejects it with a safe reason code.
    whole = func.HttpRequest(
        method="POST",
        url="/api/prepare-connector-batch",
        body=json.dumps(
            {
                "messages": [MESSAGE],
                "mode": "test",
                "correlation_id": CORRELATION,
                "message_limit": 1,
            }
        ).encode(),
    )
    rejected = handler(whole)
    assert rejected.status_code == 400
    assert json.loads(rejected.get_body())["reason"] == "connector_limit_reached"


# ── Punctuation in issue titles (14.17-M&E-11.8.26 stalled every batch) ──

PUNCTUATED = [
    ("SmartDrivingCars_14.17-M&E-11.8.26", "14.17-ME-11.8.26", "14.17 - M&E"),
    (
        "SmartDrivingCars_14.18-Waymo's Turn-11.15.26",
        "14.18-Waymos-Turn-11.15.26",
        "14.18 - Waymo's Turn",
    ),
    (
        "SmartDrivingCars 14.19-Tesla, Waymo!-11.22.26",
        "14.19-Tesla-Waymo-11.22.26",
        "14.19 - Tesla, Waymo!",
    ),
    (
        "SmartDrivingCars 14.20-Q&A (Part 2)?-11.29.26",
        "14.20-QA-Part-2-11.29.26",
        "14.20 - Q&A (Part 2)?",
    ),
]


@pytest.mark.parametrize("subject, slug, title", PUNCTUATED)
def test_punctuation_is_dropped_from_identifier_but_kept_in_title(subject, slug, title):
    from publish_newsletter import parse_newsletter

    issue = parse_newsletter(BODY, subject, "2026-12-01")
    assert issue["slug"] == slug
    assert f"permalink: /{slug}/" in issue["markdown"]
    assert title in issue["markdown"]


def test_existing_identifiers_are_unchanged():
    from publish_newsletter import parse_newsletter

    assert parse_newsletter(BODY, SUBJECT, "2026-10-22")["slug"] == "14.16-badMedia-10.22.26"


def test_real_m_and_e_issue_passes_the_connector_batch():
    """The exact Nov 8 subject must not reject the batch (identifier_invalid)."""
    message = {
        **copy.deepcopy(MESSAGE),
        "subject": "SmartDrivingCars_14.17-M&E-11.8.26",
        "receivedDateTime": "2026-11-08T21:50:00Z",
    }
    with patch("connector_batch.request_json", side_effect=AssertionError("no network in tests")):
        result = batch("production", messages=[message], known={"14.16-badMedia-10.22.26"})
    assert (result["accepted"], result["rejected"]) == (1, 0)
    assert result["verify_slugs"] == ["14.17-ME-11.8.26"]


@pytest.mark.parametrize(
    "subject",
    [
        "SmartDrivingCars_14.17-&&&-11.8.26",  # nothing left after stripping
        "SmartDrivingCars_14.17-<script>-11.8.26",  # stripped, but must not smuggle markup into the title unescaped
    ],
)
def test_degenerate_or_hostile_titles_are_still_safe(subject):
    from publish_newsletter import parse_newsletter

    try:
        issue = parse_newsletter(BODY, subject, "2026-12-01")
    except ValueError:
        return
    assert "<script>" not in issue["markdown"].split("---\n", 2)[1]


# ── One bad newsletter must not block the others (Nov 8 outage) ──────────


def candidate(subject, received="2026-11-08T21:50:00Z", **overrides):
    return {**copy.deepcopy(MESSAGE), "subject": subject, "receivedDateTime": received, **overrides}


GOOD = candidate("SmartDrivingCars_14.17-ME-11.8.26")
FUTURE = candidate("SmartDrivingCars_14.18-Future-12.31.26")  # issue date after receipt
NOT_HTML = candidate("SmartDrivingCars_14.19-Plain-11.8.26", isHtml=False)


def test_bad_candidate_is_reported_and_good_one_still_published():
    result = batch("production", messages=[FUTURE, GOOD, NOT_HTML], known=set())
    assert [item["subject"] for item in result["issues"]] == [GOOD["subject"]]
    assert result["verify_slugs"] == ["14.17-ME-11.8.26"]
    assert (result["accepted"], len(result["invalid_details"]), result["rejected"]) == (1, 2, 0)
    assert result["invalid_details"] == [
        {"reason": "invalid_issue_date", "received": FUTURE["receivedDateTime"]},
        {"reason": "html_body_required", "received": NOT_HTML["receivedDateTime"]},
    ]


def test_invalid_details_carry_no_content_or_subjects():
    result = batch("production", messages=[FUTURE], known=set())
    dumped = json.dumps(result["invalid_details"])
    assert "Future" not in dumped and "commentary" not in dumped and "@" not in dumped
    assert all(set(item) == {"reason", "received"} for item in result["invalid_details"])


def test_clean_batch_reports_zero_invalid():
    result = batch("production", messages=[GOOD], known=set())
    assert result["invalid_details"] == []


def test_single_oversized_newsletter_is_reported_without_blocking_others():
    huge = candidate(
        "SmartDrivingCars_14.15-Huge-11.1.26",
        received="2026-11-01T12:00:00Z",
        body="<p>" + "x" * 70_000 + "</p>",
    )
    result = batch("production", messages=[huge, GOOD], known=set())
    assert [item["subject"] for item in result["issues"]] == [GOOD["subject"]]
    assert result["invalid_details"] == [
        {"reason": "dispatch_too_large", "received": huge["receivedDateTime"]}
    ]
    assert result["remaining"] == 0


def test_batch_level_problems_still_reject_the_whole_batch():
    with pytest.raises(ValueError, match="limit"):
        prepare_batch([GOOD] * 100, "production", CORRELATION, SETTINGS, set())
    with pytest.raises(ValueError):
        prepare_batch([GOOD], "production", "not-a-uuid", SETTINGS, set())
    with pytest.raises(ValueError):
        prepare_batch("not a list", "production", CORRELATION, SETTINGS, set())


def test_upstream_inventory_failure_is_not_mistaken_for_a_bad_message():
    with (
        patch("connector_batch.known_newsletters", return_value={"14.16-badMedia-10.22.26"}),
        patch("connector_batch.public_metadata", side_effect=RuntimeError("API down")),
    ):
        with pytest.raises(RuntimeError):
            prepare_batch([MESSAGE], "production", CORRELATION, SETTINGS)


def test_receiver_carries_invalid_report(tmp_path):
    payload = batch("production", messages=[FUTURE, GOOD], known=set())
    report = receive_batch(payload, mode="production", root=tmp_path)
    assert report["created"] == 1
    assert report["invalid"] == 1
    assert report["invalid_details"] == [
        {"reason": "invalid_issue_date", "received": FUTURE["receivedDateTime"]}
    ]


@pytest.mark.parametrize(
    "details",
    [
        [{"reason": "made_up", "received": "2026-11-08T21:50:00Z"}],
        [{"reason": "identifier_invalid", "received": "<script>"}],
        [{"reason": "identifier_invalid", "received": "2026-11-08T21:50:00Z", "subject": "x"}],
        [{"reason": "identifier_invalid", "received": "2026-11-08T21:50:00Z"}] * 101,
        "not a list",
    ],
)
def test_receiver_rejects_malformed_invalid_report(tmp_path, details):
    payload = {**batch("production", messages=[GOOD], known=set()), "invalid_details": details}
    with pytest.raises(ValueError, match="invalid report"):
        receive_batch(payload, mode="production", root=tmp_path)


def test_dispatch_payload_fits_githubs_property_limit():
    """repository_dispatch allows at most 10 top-level client_payload properties
    (422 "No more than 10 properties are allowed; 11 were supplied", Nov 9)."""
    for messages in ([GOOD], [FUTURE, GOOD], [MESSAGE]):
        result = batch("production", messages=messages, known=set())
        assert len(result) <= 10, sorted(result)
