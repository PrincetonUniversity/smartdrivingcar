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


def test_connector_report_fails_on_invalid_newsletters_after_publishing_the_rest():
    text = Path(".github/workflows/receive-connector.yml").read_text()
    assert "int(report.get('invalid', 0)) == 0" in text


def deploy_steps():
    import yaml

    workflow = yaml.safe_load(Path(".github/workflows/deploy-site.yml").read_text())
    return workflow, workflow["jobs"]["deploy"]["steps"]


def step_index(steps, needle):
    return next(
        i for i, step in enumerate(steps) if needle in (step.get("run", "") + step.get("uses", ""))
    )


def test_newsletter_links_are_repaired_before_lychee_and_upload():
    _, steps = deploy_steps()
    links = step_index(steps, "scripts/newsletter_links.py")
    assert step_index(steps, "restyle_archive.py") < links
    assert links < step_index(steps, "lycheeverse/lychee-action")
    assert links < step_index(steps, "upload-pages-artifact")
    assert "--lychee-ignore .lycheeignore" in steps[links]["run"]
    assert "$RUNNER_TEMP/link-report.json" in steps[links]["run"]  # never inside _site


def test_broken_link_warning_is_sent_after_publishing():
    _, steps = deploy_steps()
    warn = step_index(steps, "pipeline_observe.py warning")
    assert warn > step_index(steps, "deploy-pages")
    for name in ("RESEND_API_KEY", "RESEND_FROM", "RESEND_TO"):
        assert steps[warn]["env"][name] == "${{ secrets." + name + " }}"


def test_every_site_deploy_caller_passes_only_the_email_secrets():
    workflow, _ = deploy_steps()
    declared = workflow[True]["workflow_call"]["secrets"]  # PyYAML reads `on` as True
    assert set(declared) == {"RESEND_API_KEY", "RESEND_FROM", "RESEND_TO"}
    assert all(spec["required"] is False for spec in declared.values())
    import yaml

    callers = 0
    for path in Path(".github/workflows").glob("*.yml"):
        for job in yaml.safe_load(path.read_text())["jobs"].values():
            if job.get("uses") == "./.github/workflows/deploy-site.yml":
                callers += 1
                assert job.get("secrets") == {n: "${{ secrets." + n + " }}" for n in declared}, path
    assert callers == 5


def archive_front_matter():
    import yaml

    for source in sorted(Path("_newsletters").glob("*/index.md")):
        yield source, yaml.safe_load(source.read_text().split("---", 2)[1])


def test_no_archived_issue_has_html_entities_in_its_address_or_titles():
    """9.40 was archived as /9.40-AEB&amp;FSD-110621/: links to it 404ed and its
    title rendered as 'AEB&amp;FSD'."""
    import re

    entity = re.compile(r"&(?:[A-Za-z]+|#\d+|#x[0-9A-Fa-f]+);")
    for source, meta in archive_front_matter():
        for key in ("permalink", "title", "display_name", "presentation_title"):
            assert not entity.search(str(meta.get(key, ""))), (source.parent.name, key)
        assert "&" not in meta["permalink"], source.parent.name
        assert source.parent.name == meta["permalink"].strip("/"), source.parent.name


def test_issue_9_40_keeps_both_of_its_old_addresses():
    meta = dict(archive_front_matter())[Path("_newsletters/9.40-AEBFSD-110621/index.md")]
    assert meta["permalink"] == "/9.40-AEBFSD-110621/"
    assert sorted(meta["redirect_from"]) == ["/9.40-AEB&FSD-110621/", "/9.40-AEB&amp;FSD-110621/"]
    assert meta["presentation_title"] == "9.40 - AEB&FSD"
