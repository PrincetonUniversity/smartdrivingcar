"""Bounded publishing batches from the already-authorized Outlook connector.

This module needs no Graph token. It never sends, modifies or deletes mail.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import shutil
import uuid
from email.utils import getaddresses
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml
from import_newsletter import ensure_archive_pages
from pipeline_http import request_json
from poll_mailbox import ADDRESS, validate_list_headers
from publish_newsletter import SUBJECT, parse_newsletter, safe_html, validate_slug, write_issue

MAX_DISPATCH = 58_000  # Entire GitHub dispatch body must stay below 64 KiB.
MODES = {"test", "production"}


def addresses(value: Any) -> set[str]:
    if isinstance(value, dict):
        return addresses(value.get("emailAddress", {}).get("address", ""))
    if isinstance(value, list):
        return set().union(*(addresses(item) for item in value))
    if not isinstance(value, str):
        return set()
    return {address.casefold() for _, address in getaddresses([value.replace(";", ",")]) if address}


def settings_from_env() -> dict[str, Any]:
    author = os.environ.get("SDC_ALLOWED_AUTHOR", "")
    list_address = os.environ.get("SDC_LIST_ADDRESS", "")
    repository = os.environ.get("SDC_GITHUB_REPOSITORY", "")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Configure SDC_GITHUB_REPOSITORY")
    if not ADDRESS.fullmatch(author):
        raise ValueError("Configure SDC_ALLOWED_AUTHOR")
    if not ADDRESS.fullmatch(list_address):
        raise ValueError("Configure SDC_LIST_ADDRESS")
    return {
        "author": author.casefold(),
        "list": list_address.casefold(),
        "repository": repository,
        "limit": 100,
    }


def known_newsletters(repository: str) -> set[str]:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Invalid configured GitHub repository")
    result = request_json(
        f"https://api.github.com/repos/{repository}/git/trees/main?recursive=1",
        host="api.github.com",
    )
    if (
        not isinstance(result, dict)
        or result.get("truncated")
        or not isinstance(result.get("tree"), list)
    ):
        raise ValueError("GitHub inventory is unavailable or truncated; no cursor advanced")
    return {
        item["path"].split("/")[1]
        for item in result["tree"]
        if re.fullmatch(r"_newsletters/[^/]+/index\.md", item.get("path", ""))
    }


def public_metadata(repository: str, slug: str) -> dict[str, Any]:
    path = quote(slug, safe="")
    result = request_json(
        f"https://api.github.com/repos/{repository}/contents/_newsletters/{path}/index.md?ref=main",
        host="api.github.com",
    )
    if not isinstance(result, dict) or result.get("encoding") != "base64":
        raise ValueError("Existing newsletter metadata unavailable")
    source = base64.b64decode(result["content"], validate=False).decode("utf-8")
    if not source.startswith("---\n"):
        return {}
    metadata = yaml.safe_load(source.split("---", 2)[1])
    if not isinstance(metadata, dict):
        raise ValueError("Invalid existing newsletter metadata")
    return metadata


def prepare_batch(
    messages: Any,
    mode: str,
    correlation_id: str,
    settings: dict[str, Any],
    known: set[str] | None = None,
) -> dict[str, Any]:
    if mode not in MODES:
        raise ValueError("Invalid publishing mode")
    uuid.UUID(correlation_id)
    limit = settings["limit"]
    if not isinstance(messages, list) or not 1 <= limit <= 1000 or len(messages) >= limit:
        raise ValueError(
            "Connector result reached limit or is invalid; narrow lookback or increase limit"
        )
    lookup_metadata = known is None and mode == "production"
    known = (
        known
        if known is not None
        else (set() if mode == "test" else known_newsletters(settings["repository"]))
    )
    canonical = {slug.casefold(): slug for slug in known}
    result: dict[str, Any] = {
        "version": 1,
        "mode": mode,
        "correlation_id": correlation_id,
        "scanned": len(messages),
        "accepted": 0,
        "rejected": 0,
        "remaining": 0,
        "issues": [],
        "verify_slugs": [],
    }
    pending: list[dict[str, str]] = []
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("Invalid connector message")
        subject = message.get("subject", "")
        if (
            addresses(message.get("from")) != {settings["author"]}
            or settings["list"] not in addresses(message.get("toRecipients"))
            or not isinstance(subject, str)
            or not SUBJECT.fullmatch(subject.strip())
        ):
            result["rejected"] += 1
            continue
        # Some connector versions omit RFC headers. When supplied, validate the Listserv marker.
        if message.get("internetMessageHeaders"):
            validate_list_headers(message, settings)
        body = message.get("body", "")
        if isinstance(body, dict):
            if body.get("contentType", "").casefold() != "html":
                raise ValueError("Candidate requires an HTML body")
            body = body.get("content", "")
        if message.get("isHtml") is False:
            raise ValueError("Candidate requires an HTML body")
        received = message.get("receivedDateTime", "")
        if not isinstance(received, str):
            raise ValueError("Invalid received date")
        issue = parse_newsletter(body, subject, received)
        result["accepted"] += 1
        existing = canonical.get(issue["slug"].casefold())
        if existing and mode == "production":
            if lookup_metadata:
                metadata = public_metadata(settings["repository"], existing)
                incoming = yaml.safe_load(issue["markdown"].split("---", 2)[1])
                if (
                    metadata.get("source_authority") != "curated"
                    and metadata.get("source_sha256")
                    and metadata["source_sha256"] != incoming["source_sha256"]
                ):
                    raise ValueError("Newsletter content conflict requires manual review")
            result["verify_slugs"].append(existing)
            continue
        pending.append({"subject": subject, "received": received, "body_html": safe_html(body)})
    # Oldest first: backlog drains across later sweeps after authoritative Git commits.
    pending.sort(key=lambda item: (item["received"], item["subject"]))
    for item in pending:
        tentative = {**result, "issues": result["issues"] + [item]}
        if (
            len(
                json.dumps(
                    {"event_type": "newsletter-connector-batch", "client_payload": tentative}
                ).encode()
            )
            > MAX_DISPATCH
        ):
            if not result["issues"]:
                raise ValueError(
                    "A single newsletter exceeds GitHub dispatch size; use reviewed local import"
                )
            break
        result["issues"].append(item)
        slug = parse_newsletter(item["body_html"], item["subject"], item["received"])["slug"]
        result["verify_slugs"].append(slug)
    result["remaining"] = len(pending) - len(result["issues"])
    result["verify_slugs"] = sorted(set(result["verify_slugs"]))
    if (
        len(
            json.dumps(
                {"event_type": "newsletter-connector-batch", "client_payload": result}
            ).encode()
        )
        > MAX_DISPATCH
    ):
        raise ValueError("Verification manifest exceeds dispatch limit")
    return result


def receive_batch(
    payload: Any, *, mode: str, root: Path = Path("."), preview: Path | None = None
) -> dict[str, Any]:
    if (
        not isinstance(payload, dict)
        or payload.get("version") != 1
        or payload.get("mode") != mode
        or mode not in MODES
    ):
        raise ValueError("Invalid connector version or mode")
    uuid.UUID(payload.get("correlation_id", ""))
    items = payload.get("issues")
    if not isinstance(items, list) or len(items) > 100:
        raise ValueError("Invalid issue batch")
    manifest = payload.get("verify_slugs", [])
    if not isinstance(manifest, list) or len(manifest) > 1000:
        raise ValueError("Invalid verification manifest")
    manifest = [validate_slug(slug) for slug in manifest]
    prepared = [
        parse_newsletter(item["body_html"], item["subject"], item["received"]) for item in items
    ]
    if mode == "test":
        if (
            preview is None
            or preview.resolve() == root.resolve()
            or root.resolve() in preview.resolve().parents
        ):
            raise ValueError("Test preview must be outside the repository")
        if preview.exists():
            raise ValueError("Use a fresh test preview directory")
        preview.mkdir(parents=True)
        for name in ("_layouts", "_includes", "assets"):
            if (root / name).exists():
                shutil.copytree(root / name, preview / name)
        for name in ("_config.yml", "_config_prod.yml"):
            if (root / name).exists():
                shutil.copy2(root / name, preview / name)
        destination = preview
    else:
        destination = root
    report = {
        "mode": mode,
        "correlation_id": payload["correlation_id"],
        "created": 0,
        "validated": len(prepared),
        "scanned": int(payload.get("scanned", 0)),
        "remaining": int(payload.get("remaining", 0)),
        "issues": manifest if mode == "production" else [],
    }
    for issue in prepared:
        status = write_issue(issue, destination)
        report["created"] += status == "created"
        if mode == "production":
            # CLI runs from project root; archive generation consumes only the validated ISO date.
            ensure_archive_pages(issue["date"])
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=sorted(MODES))
    parser.add_argument("--preview", type=Path)
    args = parser.parse_args()
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    expected = "newsletter-connector-test" if args.mode == "test" else "newsletter-connector-batch"
    if event.get("action") != expected:
        raise ValueError("Event type does not match receiver mode")
    report = receive_batch(event.get("client_payload"), mode=args.mode, preview=args.preview)
    Path("pipeline-result.json").write_text(json.dumps(report))
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as stream:
            stream.write(f"### Newsletter connector {args.mode} receipt\n\n")
            for key in ("correlation_id", "scanned", "validated", "created", "remaining"):
                stream.write(f"- {key}: {report[key]}\n")
            stream.write(
                "\nTest mode never commits or deploys newsletter content.\n"
                if args.mode == "test"
                else "\nPublic verification follows in the deployment stage.\n"
            )
    print(
        f"PASS: connector batch validated; mode={args.mode}, validated={report['validated']}, remaining={report['remaining']}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"FAIL: connector batch ({type(error).__name__}); see the operator runbook")
        raise SystemExit(1) from None
