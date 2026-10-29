"""Reproduce and exercise the existing Azure newsletter connector resources.

Secure parameter files and deployment packages exist only in private temporary
storage. OAuth connections, mailbox grants and the resource group are not deleted.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
import time
import uuid
import zipfile
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

REPO = Path(__file__).resolve().parents[1]


def command(args: list[str], *, json_result: bool = True, timeout: int = 900) -> Any:
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
    if result.returncode:
        codes = re.findall(r'"code"\s*:\s*"([A-Za-z0-9_.-]+)"', result.stderr)
        code = codes[0] if codes else "CLIError"
        raise RuntimeError(f"{' '.join(args[:4])} failed ({code}); inspect Azure activity history")
    return (
        json.loads(result.stdout)
        if json_result and result.stdout.strip()
        else result.stdout.strip()
    )


def load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text())
    uuid.UUID(config["subscription"])
    if not re.fullmatch(r"[A-Za-z0-9_-]+", config["resourceGroup"]):
        raise ValueError("Invalid resource group")
    params = config["parameters"]
    for name in (
        "functionAppName",
        "workflowName",
        "office365ConnectionName",
        "githubConnectionName",
    ):
        if not re.fullmatch(r"[A-Za-z0-9-]+", params[name]):
            raise ValueError("Invalid Azure resource name")
    if params["mode"] not in ("test", "production") or not params["folderName"]:
        raise ValueError("Invalid mode or folder")
    if params["mode"] == "test" and params["workflowName"] == "orfe-dept-azure-sdc-logic":
        raise ValueError("Test workflow cannot replace the original production trigger")
    return config


def resource_url(config: dict[str, Any]) -> str:
    return f"https://management.azure.com/subscriptions/{config['subscription']}/resourceGroups/{config['resourceGroup']}/providers/Microsoft.Logic/workflows/{config['parameters']['workflowName']}"


def az_args(config: dict[str, Any]) -> list[str]:
    return ["--subscription", config["subscription"], "--resource-group", config["resourceGroup"]]


def check_connections(config: dict[str, Any]) -> None:
    for key in ("office365ConnectionName", "githubConnectionName"):
        data = command(
            [
                "az",
                "resource",
                "show",
                *az_args(config),
                "--resource-type",
                "Microsoft.Web/connections",
                "--name",
                config["parameters"][key],
                "-o",
                "json",
            ]
        )
        statuses = data.get("properties", {}).get("statuses", [])
        if not any(item.get("status") == "Connected" for item in statuses):
            raise ValueError(
                "Existing connector requires reauthorization in Azure; no app-only grant is needed"
            )
    print("PASS: existing Outlook and GitHub connections are authorized")


def package_functions(destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in (
            "function_app.py",
            "connector_handler.py",
            "newsletter_processor.py",
            "process_newsletter.py",
            "host.json",
            "requirements.txt",
        ):
            archive.write(REPO / "azure/functions" / name, name)
        for name in (
            "connector_batch.py",
            "publish_newsletter.py",
            "import_newsletter.py",
            "clean_newsletter.py",
            "poll_mailbox.py",
            "pipeline_http.py",
        ):
            archive.write(REPO / "scripts" / name, "lib/" + name)


def smoke_processor(config: dict[str, Any], key: str) -> None:
    host = config["parameters"]["functionAppName"] + ".azurewebsites.net"
    fixture = {
        "mode": "test",
        "correlation_id": str(uuid.uuid4()),
        "message_limit": 100,
        "messages": [
            {
                "from": config["parameters"]["allowedAuthor"],
                "toRecipients": config["parameters"]["listAddress"],
                "subject": "SmartDrivingCars_1.01-ConnectorSmoke-1.1.00",
                "receivedDateTime": "2000-01-01T00:00:00Z",
                "isHtml": True,
                "body": "<p>" + "Deterministic safe parser commissioning fixture. " * 5 + "</p>",
            }
        ],
    }
    request = Request(
        "https://" + host + "/api/prepare-connector-batch",
        data=json.dumps(fixture).encode(),
        headers={"Content-Type": "application/json", "x-functions-key": key},
        method="POST",
    )
    for attempt in range(12):
        try:
            with urlopen(request, timeout=30) as response:
                result = json.load(response)
            if result.get("mode") != "test" or len(result.get("issues", [])) != 1:
                raise ValueError("Function smoke receipt did not validate the fixture")
            print("PASS: deployed Function parsed a test fixture; no mail or dispatch was sent")
            return
        except Exception:
            if attempt == 11:
                raise RuntimeError(
                    "Function smoke check failed; inspect Function startup/configuration"
                ) from None
            time.sleep(5)


def deploy(
    config: dict[str, Any], *, plan: bool, probe: bool, enable: bool, skip_code: bool = False
) -> None:
    check_connections(config)
    key = command(
        [
            "az",
            "functionapp",
            "keys",
            "list",
            *az_args(config),
            "--name",
            config["parameters"]["functionAppName"],
            "--query",
            "functionKeys.default",
            "-o",
            "tsv",
        ],
        json_result=False,
    )
    if not key:
        raise ValueError("Existing Function default key is unavailable")
    with tempfile.TemporaryDirectory(prefix="sdc-deployment-") as private:
        directory = Path(private)
        parameters = {name: {"value": value} for name, value in config["parameters"].items()}
        parameters["mode"] = {"value": "probe" if probe else config["parameters"]["mode"]}
        parameters["enabled"] = {"value": False}
        current_settings = command(
            [
                "az",
                "functionapp",
                "config",
                "appsettings",
                "list",
                *az_args(config),
                "--name",
                config["parameters"]["functionAppName"],
                "-o",
                "json",
            ]
        )
        parameters["existingAppSettings"] = {
            "value": {item["name"]: item["value"] for item in current_settings}
        }
        parameters["functionKey"] = {"value": key}
        parameters["healthchecksPingUrl"] = {
            "value": os.environ.get("SDC_HEALTHCHECKS_PING_URL", "")
            if config["parameters"]["mode"] == "production"
            else ""
        }
        params_file = directory / "parameters.json"
        params_file.write_text(json.dumps({"parameters": parameters}))
        params_file.chmod(0o600)
        template = directory / "main.json"
        command(
            [
                "az",
                "bicep",
                "build",
                "--file",
                str(REPO / "azure/connector/main.bicep"),
                "--outfile",
                str(template),
            ],
            json_result=False,
        )
        if plan:
            result = command(
                [
                    "az",
                    "deployment",
                    "group",
                    "what-if",
                    *az_args(config),
                    "--template-file",
                    str(template),
                    "--parameters",
                    "@" + str(params_file),
                    "--result-format",
                    "ResourceIdOnly",
                    "--no-pretty-print",
                    "-o",
                    "json",
                ]
            )
            for change in result.get("changes", []):
                print(f"PLAN: {change['changeType']} {change['resourceId']}")
            print("PASS: Azure what-if complete; secure parameter values were not printed")
            return
        command(
            [
                "az",
                "deployment",
                "group",
                "create",
                *az_args(config),
                "--name",
                "sdc-connector-" + config["parameters"]["mode"],
                "--template-file",
                str(template),
                "--parameters",
                "@" + str(params_file),
                "--output",
                "none",
            ],
            json_result=False,
        )
        print("PASS: Bicep deployed a disabled reconciler and preserved connector authorization")
        if not probe and not skip_code:
            command(
                [
                    "az",
                    "functionapp",
                    "update",
                    *az_args(config),
                    "--name",
                    config["parameters"]["functionAppName"],
                    "--set",
                    "httpsOnly=true",
                    "--output",
                    "none",
                ],
                json_result=False,
            )
            package = directory / "function.zip"
            package_functions(package)
            print("INFO: deploying Function package with remote dependency build")
            command(
                [
                    "az",
                    "functionapp",
                    "deployment",
                    "source",
                    "config-zip",
                    *az_args(config),
                    "--name",
                    config["parameters"]["functionAppName"],
                    "--src",
                    str(package),
                    "--build-remote",
                    "true",
                    "--timeout",
                    "600",
                    "--output",
                    "none",
                ],
                json_result=False,
            )
            smoke_processor(config, key)
        elif skip_code and not probe:
            smoke_processor(config, key)
        if enable:
            command(
                [
                    "az",
                    "rest",
                    "--method",
                    "post",
                    "--url",
                    resource_url(config) + "/enable?api-version=2016-06-01",
                    "--output",
                    "none",
                ],
                json_result=False,
            )
            print("PASS: selected reconciler enabled")


def status(config: dict[str, Any]) -> None:
    response = command(
        [
            "az",
            "rest",
            "--method",
            "get",
            "--url",
            resource_url(config) + "/runs?api-version=2016-06-01&$top=3",
        ]
    )
    if not response.get("value"):
        print(
            "INFO: no run history yet; invoke the selected workflow before evaluating its receipt"
        )
    for run in response.get("value", []):
        props = run["properties"]
        print(f"RUN: {run['name']} {props['status']} {props.get('startTime', '')}")
        actions = command(
            [
                "az",
                "rest",
                "--method",
                "get",
                "--url",
                resource_url(config) + "/runs/" + run["name"] + "/actions?api-version=2016-06-01",
            ]
        )
        for action in actions.get("value", []):
            detail = action["properties"]
            if detail.get("status") == "Failed":
                print(f"FAIL: action={action['name']} code={detail.get('code', 'unknown')}")
            if (
                action["name"] in ("Probe_receipt", "Batch_receipt", "Rejected_receipt")
                and detail.get("status") == "Succeeded"
            ):
                url = detail.get("outputsLink", {}).get("uri")
                if url:
                    with urlopen(url, timeout=30) as receipt:
                        result = json.load(receipt)
                    if isinstance(result, dict):
                        print(
                            "RECEIPT: "
                            + json.dumps(
                                {
                                    key: result[key]
                                    for key in (
                                        "mode",
                                        "correlation_id",
                                        "message_count",
                                        "scanned",
                                        "accepted",
                                        "rejected",
                                        "remaining",
                                        "github_dispatch_accepted",
                                        "reason",
                                    )
                                    if key in result
                                }
                            )
                        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["plan", "deploy", "run", "status", "disable"])
    parser.add_argument("--mode", choices=["test", "production"], default="test")
    parser.add_argument("--config", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--skip-code", action="store_true")
    args = parser.parse_args()
    config = load_config(args.config or REPO / "azure/connector" / (args.mode + ".json"))
    if config["parameters"]["mode"] != args.mode:
        raise ValueError("Configuration mode does not match command mode")
    if args.probe and args.mode != "test":
        raise ValueError("Probes use only the test workflow")
    if args.dry_run:
        print(
            f"DRY RUN: {args.action} mode={args.mode}; workflow={config['parameters']['workflowName']}; probe={args.probe}; enable={args.enable}"
        )
        print(
            "DRY RUN: reference existing authorized connections; no Exchange grants, app registration or resource group deletion"
        )
        return
    if args.action == "deploy" and args.mode == "production" and args.enable:
        gate = command(
            [
                "gh",
                "variable",
                "get",
                "NEWSLETTER_CONNECTOR_ENABLED",
                "--repo",
                config["parameters"]["repository"],
            ],
            json_result=False,
        )
        if gate != "true":
            raise ValueError("Set NEWSLETTER_CONNECTOR_ENABLED=true only after test acceptance")
    if args.action in ("plan", "deploy"):
        deploy(
            config,
            plan=args.action == "plan",
            probe=args.probe,
            enable=args.enable,
            skip_code=args.skip_code,
        )
    elif args.action == "status":
        status(config)
    else:
        path = "/triggers/Poll/run" if args.action == "run" else "/disable"
        if args.action == "run" and args.mode == "test":
            callback = command(
                [
                    "az",
                    "rest",
                    "--method",
                    "post",
                    "--url",
                    resource_url(config) + "/triggers/Poll/listCallbackUrl?api-version=2016-06-01",
                ]
            )
            request = Request(
                callback["value"],
                data=b"{}",
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=30) as response:
                if response.status != 202:
                    raise RuntimeError("Test callback was not accepted")
        else:
            command(
                [
                    "az",
                    "rest",
                    "--method",
                    "post",
                    "--url",
                    resource_url(config) + path + "?api-version=2016-06-01",
                    "--output",
                    "none",
                ],
                json_result=False,
            )
        print(f"PASS: {args.action} requested for selected workflow")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        detail = str(error) if isinstance(error, RuntimeError) else type(error).__name__
        print(
            f"FAIL: Azure connector operation ({detail}); inspect Azure activity/run history and the runbook"
        )
        raise SystemExit(1) from None
