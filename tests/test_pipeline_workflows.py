"""Workflow regressions that previously allowed missed publication."""

import json
from pathlib import Path


def test_legacy_trigger_splits_message_array():
    template = json.loads(Path("azure/logic-app/workflow.json").read_text())
    trigger = template["resources"][0]["properties"]["definition"]["triggers"][
        "When_a_new_email_arrives"
    ]
    assert trigger["splitOn"] == "@triggerBody()?['value']"


def test_receiver_deploys_explicitly_after_bot_commit():
    workflow = Path(".github/workflows/receive-newsletter.yml").read_text()
    assert "uses: ./.github/workflows/deploy-site.yml" in workflow
    assert "GITHUB_EVENT_PATH" in workflow
    assert "${{ github.event.client_payload" not in workflow
