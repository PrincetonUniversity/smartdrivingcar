"""macOS-native setup scripts are exercised with deliberately unusable cloud CLIs."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize("script", ["deploy.zsh", "update.zsh", "teardown.zsh"])
def test_admin_dry_run_does_not_touch_cloud(script, tmp_path):
    zsh = shutil.which("zsh")
    assert zsh, "zsh is required to test the macOS administration scripts"
    for cli in ("az", "gh"):
        stub = tmp_path / cli
        stub.write_text('#!/bin/sh\necho "unexpected cloud mutation" >&2\nexit 99\n')
        stub.chmod(0o755)
    env = {
        **os.environ,
        "PATH": str(tmp_path) + ":" + os.environ["PATH"],
        "NEWSLETTER_APP_NAME": "sdc-test-publisher",
        "NEWSLETTER_GITHUB_REPOSITORY": "test/repo",
        "NEWSLETTER_AZURE_TENANT_ID": "00000000-0000-0000-0000-000000000000",
        "NEWSLETTER_AZURE_CLIENT_ID": "00000000-0000-0000-0000-000000000000",
    }
    result = subprocess.run(
        [zsh, str(Path("azure/pipeline") / script), "--dry-run"],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "DRY RUN:" in result.stdout
    assert "unexpected cloud mutation" not in result.stderr


def test_admin_rejects_invalid_repository_before_cloud(tmp_path):
    zsh = shutil.which("zsh")
    assert zsh
    result = subprocess.run(
        [zsh, "azure/pipeline/deploy.zsh", "--dry-run"],
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "NEWSLETTER_APP_NAME": "test-app",
            "NEWSLETTER_GITHUB_REPOSITORY": "invalid;input",
            "NEWSLETTER_AZURE_TENANT_ID": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert result.returncode != 0
    assert "Invalid repository" in result.stderr
