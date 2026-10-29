"""Operational notification and public verification tests use mock HTTP only."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import pipeline_observe
import verify_publication
from check_site import check_site
from publish_newsletter import parse_newsletter, write_issue


@pytest.fixture(autouse=True)
def isolated_optional_config(monkeypatch):
    for name in (
        "HEALTHCHECKS_PING_URL",
        "RESEND_API_KEY",
        "RESEND_FROM",
        "RESEND_TO",
        "RESEND_NOTIFY_IDLE",
        "RESEND_NOTIFY_START",
    ):
        monkeypatch.delenv(name, raising=False)


def test_disabled_monitoring_never_calls_network(capsys):
    with patch.object(pipeline_observe, "request_json") as request:
        pipeline_observe.signal("success")
    request.assert_not_called()
    assert "disabled" in capsys.readouterr().out


@pytest.mark.parametrize(
    "status,suffix", [("start", "/start"), ("success", ""), ("failure", "/fail")]
)
def test_healthchecks_signal_meanings(monkeypatch, status, suffix):
    ping = "https://hc-ping.com/00000000-0000-0000-0000-000000000000"
    monkeypatch.setenv("HEALTHCHECKS_PING_URL", ping)
    with patch.object(pipeline_observe, "request_json") as request:
        pipeline_observe.signal(status)
    assert request.call_args.args[0] == ping + suffix


def resend_settings(monkeypatch):
    for name, value in {
        "RESEND_API_KEY": "secret",
        "RESEND_FROM": "status@example.org",
        "RESEND_TO": "operator@example.org",
        "GITHUB_REPOSITORY": "org/repo",
        "GITHUB_RUN_ID": "123",
        "GITHUB_RUN_ATTEMPT": "1",
    }.items():
        monkeypatch.setenv(name, value)


def test_resend_only_notifies_operators_and_deduplicates(monkeypatch):
    resend_settings(monkeypatch)
    with patch.object(pipeline_observe, "request_json") as request:
        pipeline_observe.signal("success", {"created": 1})
    assert request.call_args.kwargs["data"]["to"] == ["operator@example.org"]
    assert request.call_args.kwargs["headers"]["Idempotency-Key"] == "newsletter/123/1/success"
    assert "created: 1" in request.call_args.kwargs["data"]["text"]


def test_idle_notifications_are_opt_in(monkeypatch):
    resend_settings(monkeypatch)
    with patch.object(pipeline_observe, "request_json") as request:
        pipeline_observe.signal("success", {"created": 0})
    request.assert_not_called()


def test_partial_resend_config_fails(monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", "secret")
    with pytest.raises(ValueError, match="all three"):
        pipeline_observe.validate_config()


def test_provider_failure_is_visible_and_other_provider_is_attempted(monkeypatch):
    resend_settings(monkeypatch)
    monkeypatch.setenv(
        "HEALTHCHECKS_PING_URL", "https://hc-ping.com/00000000-0000-0000-0000-000000000000"
    )
    with patch.object(
        pipeline_observe, "request_json", side_effect=[RuntimeError("outage"), {}]
    ) as request:
        with pytest.raises(RuntimeError, match="monitoring signals"):
            pipeline_observe.signal("failure")
    assert request.call_count == 2


def test_public_success_requires_matching_fingerprint(tmp_path):
    issue = parse_newsletter(
        "<p>" + "Original newsletter commentary. " * 4 + "</p>",
        "SmartDrivingCars_14.16-badMedia-10.22.26",
        "2026-10-22",
    )
    write_issue(issue, tmp_path)
    with (
        patch.object(verify_publication, "build_opener") as opener,
        patch.object(verify_publication.time, "sleep"),
    ):
        response = opener.return_value.open.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = b'<html><meta name="newsletter-permalink" content="/14.16-badMedia-10.22.26/"><meta name="newsletter-source" content="wrong"></html>'
        with pytest.raises(RuntimeError, match="verification failed"):
            verify_publication.verify("https://example.org", [issue["slug"]], root=tmp_path)
    assert opener.return_value.open.call_count == 6


def test_public_page_verifies_expected_identity(tmp_path):
    path = tmp_path / "_newsletters" / "14.16-badMedia-10.22.26" / "index.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\nlayout: newsletter\n---\nHello")
    with patch.object(verify_publication, "build_opener") as opener:
        response = opener.return_value.open.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = (
            b'<meta name="newsletter-permalink" content="/14.16-badMedia-10.22.26/">'
        )
        verify_publication.verify("https://example.org", ["14.16-badMedia-10.22.26"], root=tmp_path)
    assert opener.return_value.open.call_count == 1


def test_built_site_cannot_expose_raw_email(tmp_path):
    (tmp_path / "index.html").write_text("Homepage")
    (tmp_path / "private.eml").write_text("Private mail headers")
    with pytest.raises(ValueError, match="Private source file"):
        check_site(tmp_path)
