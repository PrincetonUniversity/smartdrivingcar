"""Azure adoption, test isolation, and packaging contracts without cloud credentials."""

import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from azure_connector_admin import load_config, package_functions


def test_existing_connections_are_referenced_not_recreated():
    source = Path("azure/connector/main.bicep").read_text()
    assert "resource outlook 'Microsoft.Web/connections@2016-06-01' existing" in source
    assert "resource github 'Microsoft.Web/connections@2016-06-01' existing" in source
    assert "union(existingAppSettings," in source
    assert "@secure()\nparam functionKey string" in source


def test_test_and_production_are_separate_resources_and_folders():
    test = load_config(Path("azure/connector/test.json"))
    prod = load_config(Path("azure/connector/production.json"))
    assert test["subscription"] == "996314b4-bcc8-45e5-a21f-8f7096e7e71e"
    assert test["resourceGroup"] == "orfe-dept-azure-alaink-sdc-rg"
    assert test["parameters"]["workflowName"] != prod["parameters"]["workflowName"]
    assert test["parameters"]["folderName"] == "SDC Testing"
    assert prod["parameters"]["folderName"] == "SmartDrivingCars Newsletters for Processing"


@pytest.mark.parametrize("field", ["subscription", "resourceGroup"])
def test_documentation_does_not_publish_deployment_identifiers(field):
    config = json.loads(Path("azure/connector/production.json").read_text())
    identifier = config[field].casefold()
    assert identifier
    candidates = list(Path(".").glob("*.md"))
    for root in (Path("docs"), Path("azure"), Path(".github")):
        candidates.extend(root.rglob("*.md"))
    for path in candidates:
        if identifier in path.read_text().casefold():
            pytest.fail(f"Deployment-specific {field} must stay out of documentation: {path}")


def test_reconciler_reads_read_messages_without_modifying_mail():
    definition = json.loads(Path("azure/connector/workflow.definition.json").read_text())
    action = definition["actions"]["Read_retained_messages"]
    assert action["inputs"]["path"] == "/v3/Mail"
    assert action["inputs"]["method"] == "get"
    assert action["inputs"]["queries"]["fetchOnlyUnread"] is False
    assert "searchQuery" in action["inputs"]["queries"]
    assert action["runtimeConfiguration"]["secureData"]["properties"] == ["inputs", "outputs"]
    encoded = json.dumps(definition)
    assert "SendEmail" not in encoded and "MarkAsRead" not in encoded and "/Move" not in encoded
    assert definition["triggers"]["Poll"]["runtimeConfiguration"]["concurrency"]["runs"] == 1


def test_dispatch_receives_array_as_data_not_string():
    definition = json.loads(Path("azure/connector/workflow.definition.json").read_text())
    prepare = definition["actions"]["Probe_or_process"]["else"]["actions"]["Prepare_batch"]
    assert prepare["inputs"]["body"]["messages"] == "@body('Read_retained_messages')?['value']"


def test_read_only_test_job_has_no_commit_or_publication_surface():
    source = Path(".github/workflows/receive-connector.yml").read_text()
    test_job = source.split("  test:", 1)[1].split("  receive:", 1)[0]
    assert "git push" not in test_job
    assert "deploy-pages@" not in test_job
    assert "contents: write" not in test_job
    assert "upload-artifact@" not in test_job
    assert "--mode test" in test_job
    assert "needs: receive" in source


def test_function_zip_contains_shared_parser_and_no_credentials(tmp_path):
    archive = tmp_path / "function.zip"
    package_functions(archive)
    with zipfile.ZipFile(archive) as package:
        names = package.namelist()
    assert "connector_handler.py" in names
    assert "lib/publish_newsletter.py" in names
    assert "lib/connector_batch.py" in names
    assert not any("local.settings" in name or ".env" in name for name in names)


@pytest.mark.parametrize("wrapper", ["deploy", "update", "teardown", "test"])
def test_azure_admin_dry_runs_use_no_cloud_credentials(wrapper, tmp_path):
    stub = tmp_path / "az"
    stub.write_text("#!/bin/sh\necho unexpected cloud call >&2\nexit 99\n")
    stub.chmod(0o755)
    env = {
        **os.environ,
        "PATH": str(tmp_path) + ":" + os.environ["PATH"],
        "PYTHON_BIN": sys.executable,
    }
    result = subprocess.run(
        ["zsh", f"azure/connector/{wrapper}.zsh", "--dry-run"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "DRY RUN:" in result.stdout
    assert "unexpected cloud call" not in result.stderr


def test_template_uses_shallow_trigger_replacement_and_private_settings_snapshot():
    source = Path("azure/connector/main.bicep").read_text()
    assert "definition: shallowMerge(" in source
    assert "param existingAppSettings object" in source
    assert "list('${processor.id}/config/appsettings'" not in source
    definition = json.loads(Path("azure/connector/workflow.definition.json").read_text())

    def check(value):
        if isinstance(value, dict):
            if value.get("type") == "SetVariable":
                assert "runtimeConfiguration" not in value
            for child in value.values():
                check(child)
        elif isinstance(value, list):
            for child in value:
                check(child)

    check(definition)


def test_handled_validation_error_still_fails_the_workflow():
    definition = json.loads(Path("azure/connector/workflow.definition.json").read_text())
    actions = definition["actions"]["Probe_or_process"]["else"]["actions"]
    assert actions["Reject_batch"]["inputs"]["runStatus"] == "Failed"
    assert actions["Reject_batch"]["runAfter"] == {
        "Signal_rejection": ["Succeeded", "Failed", "TimedOut"]
    }


# ── Healthchecks URL: never silently dropped, survives a wiped laptop ────

PING = "https://hc-ping.com/00000000-0000-0000-0000-000000000000"
SETTING = "SDC_HEALTHCHECKS_PING_URL"


def ping_url(**kwargs):
    import azure_connector_admin

    defaults = {"mode": "production", "environ": {}, "current": {}, "allow_missing": False}
    return azure_connector_admin.healthchecks_ping_url(**{**defaults, **kwargs})


def test_production_ping_url_comes_from_the_environment_first():
    assert ping_url(environ={SETTING: PING}, current={SETTING: PING.replace("0", "1")}) == PING


def test_production_ping_url_is_recovered_from_azure_when_not_exported():
    """After a fresh clone nothing is exported; the Function's settings remember it."""
    assert ping_url(current={SETTING: PING}) == PING


def test_production_without_any_ping_url_refuses_to_deploy():
    with pytest.raises(ValueError, match="SDC_HEALTHCHECKS_PING_URL"):
        ping_url()


def test_operator_can_deliberately_deploy_without_healthchecks():
    assert ping_url(allow_missing=True) == ""


def test_malformed_ping_url_is_rejected_without_echoing_it():
    with pytest.raises(ValueError) as error:
        ping_url(environ={SETTING: "https://evil.example/secret-token"})
    assert "secret-token" not in str(error.value)


def test_test_mode_never_pings_production_healthchecks():
    assert ping_url(mode="test", environ={SETTING: PING}) == ""


def test_ping_url_is_persisted_into_function_settings():
    import azure_connector_admin

    merged = azure_connector_admin.with_ping_setting({"OTHER": "x"}, PING)
    assert merged == {"OTHER": "x", SETTING: PING}
    assert azure_connector_admin.with_ping_setting({"OTHER": "x"}, "") == {"OTHER": "x"}


def test_no_healthchecks_flag_exists():
    text = Path("scripts/azure_connector_admin.py").read_text()
    assert '"--no-healthchecks"' in text


# ── Older azure/deploy scripts act only on the newsletter subscription ──


def run_subscription_guard(tmp_path, current):
    # A shell function, not a stub file: CI mounts /tmp without exec permission.
    script = (
        f'az() {{ echo "$*" >> "{tmp_path}/calls"; echo {current}; }}; '
        "source azure/deploy/subscription.sh && require_newsletter_subscription"
    )
    return subprocess.run(["bash", "-c", script], capture_output=True, text=True)


def test_wrong_default_subscription_stops_the_older_scripts(tmp_path):
    result = run_subscription_guard(tmp_path, "1d966cca-b59d-49a0-ba86-39c4a1c85c0f")
    assert result.returncode != 0
    expected = json.loads(Path("azure/connector/production.json").read_text())["subscription"]
    assert f"az account set --subscription {expected}" in result.stderr


def test_newsletter_subscription_passes_the_guard(tmp_path):
    expected = json.loads(Path("azure/connector/production.json").read_text())["subscription"]
    assert run_subscription_guard(tmp_path, expected).returncode == 0


@pytest.mark.parametrize("script", ["deploy.sh", "update.sh", "teardown.sh"])
def test_older_scripts_check_the_subscription_before_changing_anything(script):
    lines = Path("azure/deploy", script).read_text().splitlines()
    guard = next(i for i, line in enumerate(lines) if "require_newsletter_subscription" in line)
    mutating = re.compile(
        r"\baz\b.*\b(create|delete|update|set|deploy|publish|restart|start|stop)\b"
    )
    first_change = next(
        i for i, line in enumerate(lines) if mutating.search(line) and "account set" not in line
    )
    assert guard < first_change, (
        f"{script}: guard on line {guard + 1}, change on {first_change + 1}"
    )
