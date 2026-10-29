"""Reconcile retained Listserv newsletters using mailbox-scoped Graph Mail.Read."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, urlencode, urlsplit

from import_newsletter import ensure_archive_pages
from pipeline_http import request_json
from publish_newsletter import SUBJECT, parse_newsletter, write_issue

GRAPH = "https://graph.microsoft.com/v1.0"
ADDRESS = re.compile(r"[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def address(value: Any) -> str:
    return str((value or {}).get("emailAddress", {}).get("address", "")).casefold()


def config() -> dict[str, Any]:
    mailbox = os.environ.get("NEWSLETTER_MAILBOX", "")
    author = os.environ.get("NEWSLETTER_ALLOWED_AUTHOR", "")
    list_address = os.environ.get("NEWSLETTER_LIST_ADDRESS", "")
    if not all(ADDRESS.fullmatch(value) for value in (mailbox, author, list_address)):
        raise ValueError(
            "Set valid NEWSLETTER_MAILBOX, NEWSLETTER_ALLOWED_AUTHOR and NEWSLETTER_LIST_ADDRESS"
        )
    days = int(os.environ.get("NEWSLETTER_LOOKBACK_DAYS", "90"))
    if not 1 <= days <= 3650:
        raise ValueError("NEWSLETTER_LOOKBACK_DAYS must be between 1 and 3650")
    max_age = int(os.environ.get("NEWSLETTER_MAX_AGE_DAYS", "0"))
    if not 0 <= max_age <= days:
        raise ValueError("NEWSLETTER_MAX_AGE_DAYS must be zero or within the lookback window")
    return {
        "max_age_days": max_age,
        "mailbox": mailbox,
        "author": author.casefold(),
        "list": list_address.casefold(),
        "days": days,
    }


def candidate(message: dict[str, Any], settings: dict[str, Any]) -> bool:
    return (
        address(message.get("from")) == settings["author"]
        and address(message.get("sender")) == settings["list"]
        and settings["list"]
        in {address(recipient) for recipient in message.get("toRecipients", [])}
        and isinstance(message.get("subject"), str)
        and SUBJECT.fullmatch(message["subject"].strip()) is not None
    )


def validate_list_headers(message: dict[str, Any], settings: dict[str, Any]) -> None:
    expected_list = settings["list"].split("@")[0]
    for header in message.get("internetMessageHeaders", []):
        if header.get("name", "").lower() == "list-help":
            for target in re.findall(r"<([^>]+)>", header.get("value", "")):
                parsed = urlsplit(target)
                query = {key.lower(): value for key, value in parse_qs(parsed.query).items()}
                if (
                    parsed.scheme == "https"
                    and parsed.hostname == "lists.princeton.edu"
                    and query.get("list", [""])[0].casefold() == expected_list
                ):
                    return
    raise ValueError("Newsletter candidate is missing the expected Princeton Listserv headers")


def reconcile(
    settings: dict[str, Any], token: str, *, root: Path = Path("."), dry_run: bool = False
) -> dict[str, Any]:
    headers = {"Authorization": "Bearer " + token, "Prefer": 'outlook.body-content-type="html"'}
    prefix = GRAPH + "/users/" + quote(settings["mailbox"], safe="")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=settings["days"])).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    query = urlencode(
        {
            "$filter": "receivedDateTime ge " + cutoff,
            "$select": "id,subject,from,sender,toRecipients,receivedDateTime",
            "$orderby": "receivedDateTime asc",
            "$top": "50",
        }
    )
    url = prefix + "/messages?" + query
    report: dict[str, Any] = {
        "scanned": 0,
        "created": 0,
        "duplicates": 0,
        "issues": [],
        "dry_run": dry_run,
    }
    seen: set[str] = set()
    pending: list[dict[str, str]] = []
    newest_receipt: datetime | None = None
    while url:
        if url in seen or len(seen) >= 200:
            raise ValueError("Mailbox pagination limit reached; narrow lookback or investigate")
        seen.add(url)
        page = request_json(url, host="graph.microsoft.com", headers=headers)
        if not isinstance(page, dict) or not isinstance(page.get("value"), list):
            raise ValueError("Invalid Graph mailbox response")
        for message in page["value"]:
            report["scanned"] += 1
            if not candidate(message, settings):
                continue
            detail_url = (
                prefix
                + "/messages/"
                + quote(message["id"], safe="")
                + "?"
                + urlencode({"$select": "body,internetMessageHeaders"})
            )
            detail = request_json(detail_url, host="graph.microsoft.com", headers=headers)
            validate_list_headers(detail, settings)
            body = detail.get("body", {})
            if body.get("contentType", "").lower() != "html":
                raise ValueError("Newsletter candidate has no HTML body; manual import required")
            receipt = datetime.fromisoformat(message["receivedDateTime"].replace("Z", "+00:00"))
            newest_receipt = max(newest_receipt, receipt) if newest_receipt else receipt
            pending.append(
                parse_newsletter(
                    body.get("content", ""), message["subject"], message["receivedDateTime"]
                )
            )
        url = page.get("@odata.nextLink", "")
        # nextLink is validated by the HTTP client before any bearer token is sent.
    # Validate every candidate before writing any files. Failure never advances a cursor.
    for issue in pending:
        result = "preview" if dry_run else write_issue(issue, root)
        if result == "created":
            ensure_archive_pages(issue["date"])
            report["created"] += 1
        elif result == "duplicate":
            report["duplicates"] += 1
        if issue["slug"] not in report["issues"]:
            report["issues"].append(issue["slug"])
    max_age = settings.get("max_age_days", 0)
    if max_age and (
        newest_receipt is None
        or datetime.now(timezone.utc) - newest_receipt > timedelta(days=max_age)
    ):
        raise ValueError(
            "Newsletter freshness threshold exceeded; check list delivery and mailbox subscription"
        )
    return report


def graph_token() -> str:
    token = os.environ.get("GRAPH_ACCESS_TOKEN")
    if not token:
        result = subprocess.run(
            [
                "az",
                "account",
                "get-access-token",
                "--resource-type",
                "ms-graph",
                "--query",
                "accessToken",
                "-o",
                "tsv",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode or not result.stdout.strip():
            raise RuntimeError(
                "Graph token unavailable; check OIDC login and mailbox-scoped authorization"
            )
        token = result.stdout.strip()
    return token


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    settings = config()  # Fail before obtaining credentials on invalid configuration.
    token = graph_token()
    report = reconcile(settings, token, dry_run=args.dry_run)
    if not args.dry_run:
        Path("pipeline-result.json").write_text(json.dumps(report))
    print(
        f"PASS: mailbox reconciled; scanned={report['scanned']}, created={report['created']}, duplicates={report['duplicates']}, preview={args.dry_run}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        # Never print API response bodies, tokens, subjects, mailbox addresses or mail contents.
        print(
            f"FAIL: mailbox reconciliation ({type(error).__name__}); inspect configuration and operator runbook"
        )
        raise SystemExit(1) from None
