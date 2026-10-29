"""Exercise actual OIDC mailbox isolation and a read-only newsletter preview."""

import os
from urllib.parse import quote

from pipeline_http import APIError, request_json
from poll_mailbox import ADDRESS, GRAPH, config, graph_token, reconcile


def commission() -> None:
    settings = config()
    other = os.environ.get("NEWSLETTER_NEGATIVE_TEST_MAILBOX", "")
    if not ADDRESS.fullmatch(other) or other.casefold() == settings["mailbox"].casefold():
        raise ValueError("A different, existing negative-control mailbox must be configured")
    token = graph_token()
    headers = {"Authorization": "Bearer " + token}
    for mailbox in (settings["mailbox"], other):
        url = GRAPH + "/users/" + quote(mailbox, safe="") + "/messages?$top=1&$select=id"
        try:
            request_json(url, host="graph.microsoft.com", headers=headers)
        except APIError as error:
            if mailbox == other and error.status_code == 403:
                print("PASS: negative-control mailbox denied by live Graph API")
                continue
            raise RuntimeError(
                "Commissioning access test failed; check mailbox identity and scope"
            ) from None
        if mailbox == other:
            raise RuntimeError(
                "Isolation failure: publisher can access another mailbox; do not enable"
            )
        print("PASS: target mailbox accessible with dedicated publisher identity")
    report = reconcile(settings, token, dry_run=True)
    if not report["issues"]:
        raise ValueError("No known newsletter matched; check retained mail and delivery metadata")
    print(
        f"PASS: dry-run matched {len(report['issues'])} newsletter issue(s); no mail or repository content modified"
    )


if __name__ == "__main__":
    try:
        commission()
    except Exception as error:
        print(f"FAIL: commissioning ({type(error).__name__}); consult administrator setup runbook")
        raise SystemExit(1) from None
