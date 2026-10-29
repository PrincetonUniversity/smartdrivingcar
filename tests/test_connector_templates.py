"""Azure adoption, test isolation, and packaging contracts without cloud credentials."""

import json
import os
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
