"""Optional operational signals. No newsletter or mailbox data leaves the pipeline."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from pipeline_http import request_json
from poll_mailbox import ADDRESS


def validate_config() -> None:
    ping = os.environ.get("HEALTHCHECKS_PING_URL", "")
    if ping and not re.fullmatch(r"https://hc-ping\.com/[0-9a-fA-F-]{36}", ping):
        raise ValueError("HEALTHCHECKS_PING_URL must be an HTTPS hc-ping.com UUID URL")
    resend = [os.environ.get(name, "") for name in ("RESEND_API_KEY", "RESEND_FROM", "RESEND_TO")]
    if any(resend) and not all(resend):
        raise ValueError("Configure all three Resend secrets or leave all unset")
    if all(resend) and not all(ADDRESS.fullmatch(value) for value in resend[1:]):
        raise ValueError("Resend sender and operator recipient must be single email addresses")
    for name in ("RESEND_NOTIFY_IDLE", "RESEND_NOTIFY_START"):
        if os.environ.get(name, "false") not in {"true", "false"}:
            raise ValueError("Notification switches must be true or false")


def signal(status: str, report: dict[str, Any] | None = None) -> None:
    validate_config()
    failures = 0
    ping = os.environ.get("HEALTHCHECKS_PING_URL", "")
    if ping:
        suffix = {"start": "/start", "success": "", "failure": "/fail"}[status]
        try:
            request_json(ping + suffix, host="hc-ping.com", expect_json=False)
            print("PASS: Healthchecks signal delivered")
        except Exception:
            print("FAIL: Healthchecks delivery; publishing result is unchanged")
            failures += 1
    resend_key = os.environ.get("RESEND_API_KEY", "")
    should_notify = (
        status == "failure"
        or (status == "start" and os.environ.get("RESEND_NOTIFY_START") == "true")
        or (
            status == "success"
            and (
                ((report or {}).get("created", 0) > 0 or (report or {}).get("repaired", False))
                or os.environ.get("RESEND_NOTIFY_IDLE") == "true"
            )
        )
    )
    if resend_key and should_notify:
        repository = os.environ.get("GITHUB_REPOSITORY", "")
        run_id = os.environ.get("GITHUB_RUN_ID", "")
        run_url = f"https://github.com/{repository}/actions/runs/{run_id}"
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) or not run_id.isdigit():
            raise ValueError("Resend operational notifications require a GitHub workflow run")
        # Public run URL and numeric counts only; no email content, addresses or subjects.
        text = f"Newsletter publishing: {status}.\nRun: {run_url}\n"
        if report:
            for key in ("scanned", "created", "duplicates", "rejected", "remaining"):
                if key in report:
                    text += f"{key}: {int(report[key])}\n"
        try:
            request_json(
                "https://api.resend.com/emails",
                host="api.resend.com",
                method="POST",
                headers={
                    "Authorization": "Bearer " + resend_key,
                    "Idempotency-Key": f"newsletter/{run_id}/{os.environ.get('GITHUB_RUN_ATTEMPT', '1')}/{status}",
                },
                data={
                    "from": os.environ["RESEND_FROM"],
                    "to": [os.environ["RESEND_TO"]],
                    "subject": f"SmartDrivingCar publishing {status}",
                    "text": text,
                },
            )
            print("PASS: Resend operational notification delivered")
        except Exception:
            print("FAIL: Resend delivery; inspect provider dashboard")
            failures += 1
    if not ping and not resend_key:
        print("INFO: external monitoring is disabled; workflow status remains available")
    if failures:
        raise RuntimeError("One or more monitoring signals could not be delivered")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("status", choices=["validate", "start", "success", "failure"])
    args = parser.parse_args()
    validate_config()
    if args.status == "validate":
        print("PASS: monitoring configuration valid")
        return
    report_path = Path("pipeline-result.json")
    report = json.loads(report_path.read_text()) if report_path.exists() else None
    signal(args.status, report)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(
            f"FAIL: operational monitoring ({type(error).__name__}); check optional secrets and provider status"
        )
        raise SystemExit(1) from None
