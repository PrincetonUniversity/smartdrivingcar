"""Verify deployed issue routes and source fingerprints before signaling success."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, build_opener

import yaml
from bs4 import BeautifulSoup
from pipeline_http import NoRedirect
from publish_newsletter import validate_slug


def verify(base: str, issues: list[str], *, root: Path = Path(".")) -> None:
    parsed = urlsplit(base)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
        or parsed.port
    ):
        raise ValueError("NEWSLETTER_PUBLIC_URL must be an HTTPS origin without a path")
    targets = issues or [""]
    for slug in targets:
        if slug:
            validate_slug(slug)
        expected = None
        if slug:
            source = (root / "_newsletters" / slug / "index.md").read_text()
            expected = yaml.safe_load(source.split("---", 2)[1]).get("source_sha256")
        for attempt in range(6):
            try:
                request = Request(
                    base.rstrip("/") + "/" + slug + ("/" if slug else ""),
                    headers={
                        "Cache-Control": "no-cache",
                        "User-Agent": "SmartDrivingCar-Publisher/1",
                    },
                )
                with build_opener(NoRedirect()).open(request, timeout=20) as response:
                    if response.status != 200:
                        raise ValueError("Public route did not return 200")
                    raw = response.read(5_000_001)
                    if len(raw) > 5_000_000:
                        raise ValueError("Public response is too large")
                soup = BeautifulSoup(raw, "html.parser")
                if slug:
                    marker = soup.find("meta", attrs={"name": "newsletter-permalink"})
                    if not marker or marker.get("content") != f"/{slug}/":
                        raise ValueError("Public route contains the wrong issue")
                if expected:
                    marker = soup.find("meta", attrs={"name": "newsletter-source"})
                    if not marker or marker.get("content") != expected:
                        raise ValueError("Public source fingerprint is stale")
                break
            except Exception:
                if attempt == 5:
                    raise RuntimeError(
                        "Public publication verification failed; rerun to rebuild and recover"
                    ) from None
                time.sleep(10)
    print(f"PASS: {len(targets)} public route(s) verified over HTTPS")


if __name__ == "__main__":
    report = (
        json.loads(Path("pipeline-result.json").read_text())
        if Path("pipeline-result.json").exists()
        else {}
    )
    base = (
        os.environ.get("NEWSLETTER_PUBLIC_URL")
        or yaml.safe_load(Path("_config_prod.yml").read_text())["url"]
    )
    verify(base, report.get("issues", []))
