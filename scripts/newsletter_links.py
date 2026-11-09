"""Check, and where possible repair, links to this site inside newsletters.

Runs on the built site before upload, so an issue built in the same deploy
(newsletters routinely link to themselves) counts as existing. Only links in
newsletter bodies (.email-newsletter) are this check's concern; site
navigation stays with lychee, which still blocks the deploy.

* A link whose target exists (page or redirect) is fine. http/https, www.,
  a missing trailing slash, percent-encoding, queries and #anchors are all
  treated as the same page; letter case must match, as on GitHub Pages.
* A broken link whose address cleans up, by the parser's own rule, to exactly
  one issue gets a redirect page in the built site (regenerated each deploy).
* Anything else is reported as a warning. Publishing never blocks on it.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote, unquote, urljoin, urlsplit

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parent))
from publish_newsletter import clean_identifier  # noqa: E402

SITE_URL = "https://smartdrivingcar.com"
SITE_HOSTS = {"smartdrivingcar.com", "www.smartdrivingcar.com"}

REDIRECT = """<!DOCTYPE html>
<html lang="en-US">
  <meta charset="utf-8">
  <title>Redirecting&hellip;</title>
  <link rel="canonical" href="{url}">
  <script>location={script}</script>
  <meta http-equiv="refresh" content="0; url={url}">
  <meta name="robots" content="noindex">
  <h1>Redirecting&hellip;</h1>
  <a href="{url}">Click here if you are not redirected.</a>
</html>
"""


def issue_pages(site: Path) -> dict[Path, str]:
    """Built newsletter pages and their permalinks."""
    pages = {}
    for path in site.rglob("index.html"):
        soup = BeautifulSoup(path.read_text(errors="replace"), "html.parser")
        marker = soup.find("meta", attrs={"name": "newsletter-permalink"})
        if marker and marker.get("content"):
            pages[path] = str(marker["content"])
    return pages


def site_route(href: str, base: str) -> str | None:
    """The decoded path on this site an href points to, or None if not ours."""
    parts = urlsplit(href.strip())
    if parts.scheme in ("http", "https"):
        if (parts.hostname or "").lower() not in SITE_HOSTS:
            return None
        path = parts.path or "/"
    elif parts.scheme or parts.netloc:
        return None  # mailto:, ftp:, protocol-relative to elsewhere, ...
    elif not parts.path:
        return None  # in-page #anchor
    else:
        path = urlsplit(urljoin(base, parts.path)).path
    return unquote(path)


def safe(route: str) -> bool:
    return (
        route.startswith("/")
        and not re.search(r"[\x00-\x1f\x7f\\]", route)
        and not any(part in {".", ".."} for part in route.split("/"))
    )


def exists(site: Path, route: str) -> bool:
    """Exact-case lookup, as GitHub Pages serves it (macOS disks ignore case)."""
    parts = [part for part in route.split("/") if part]
    candidates = [parts + ["index.html"]]
    if parts and not route.endswith("/"):
        candidates.append(parts)  # a file such as /feed.xml
    for candidate in candidates:
        current = site
        for name in candidate:
            if not current.is_dir() or name not in os.listdir(current):
                break
            current = current / name
        else:
            if current.is_file():
                return True
    return False


def resolve(route: str, issues: set[str]) -> str | None:
    """The one issue an as-written single-segment address means, or None."""
    segments = [part for part in route.split("/") if part]
    if len(segments) != 1:
        return None
    cleaned = clean_identifier(segments[0])
    if not cleaned:
        return None
    if f"/{cleaned}/" in issues:
        return f"/{cleaned}/"
    folded = [
        permalink for permalink in issues if permalink.casefold() == f"/{cleaned}/".casefold()
    ]
    return folded[0] if len(folded) == 1 else None


def write_redirect(site: Path, route: str, target: str) -> None:
    path = site.joinpath(*[part for part in route.split("/") if part], "index.html")
    if site.resolve() not in path.resolve().parents:
        raise ValueError("Redirect would escape the site directory")
    url = SITE_URL + target
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(REDIRECT.format(url=html.escape(url, quote=True), script=json.dumps(url)))


def check(site: Path) -> dict[str, Any]:
    pages = issue_pages(site)
    issues = set(pages.values())
    report: dict[str, Any] = {"checked": 0, "repaired": [], "broken": []}
    seen: set[tuple[str, str]] = set()
    for path, permalink in sorted(pages.items()):
        soup = BeautifulSoup(path.read_text(errors="replace"), "html.parser")
        for body in soup.select(".email-newsletter"):
            for anchor in body.find_all("a", href=True):
                route = site_route(str(anchor["href"]), permalink)
                if route is None:
                    continue
                report["checked"] += 1
                if safe(route) and exists(site, route):
                    continue
                key = (permalink, route.rstrip("/") + "/")
                if key in seen:
                    continue
                seen.add(key)
                link = key[1]
                target = resolve(link, issues) if safe(route) else None
                if target is not None:
                    write_redirect(site, link, target)
                    report["repaired"].append({"issue": permalink, "link": link, "target": target})
                else:
                    report["broken"].append({"issue": permalink, "link": link})
    return report


def lychee_ignore(report: dict[str, Any]) -> list[str]:
    """Regexes so lychee doesn't block on links already reported as warnings."""
    patterns = []
    for entry in report["broken"]:
        stem = entry["link"].rstrip("/")
        for form in sorted({stem, quote(stem, safe="/")}):
            patterns.append(re.escape(form) + r"/?(?:index\.html)?(?:[?#].*)?$")
    return patterns


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--lychee-ignore", type=Path, required=True)
    args = parser.parse_args()
    report = check(args.site)
    args.report.write_text(json.dumps(report, indent=2))
    # Append: the repository commits its own .lycheeignore.
    patterns = lychee_ignore(report)
    if patterns:
        with args.lychee_ignore.open("a") as stream:
            stream.write("\n# Reported by newsletter_links.py (published with a warning)\n")
            stream.write("".join(p + "\n" for p in patterns))
    for entry in report["repaired"]:
        print(
            f"::notice::Redirected {entry['link']} to {entry['target']} (linked from {entry['issue']})"
        )
    for entry in report["broken"]:
        print(f"::warning::Broken link {entry['link']} in {entry['issue']}; published anyway")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary and (report["repaired"] or report["broken"]):
        with open(summary, "a") as stream:
            stream.write("### Newsletter links\n")
            for entry in report["repaired"]:
                stream.write(
                    f"- repaired `{entry['link']}` → `{entry['target']}` ({entry['issue']})\n"
                )
            for entry in report["broken"]:
                stream.write(f"- **broken** `{entry['link']}` in {entry['issue']}\n")
    print(
        f"PASS: {report['checked']} newsletter link(s) to this site checked; "
        f"{len(report['repaired'])} repaired, {len(report['broken'])} reported"
    )


if __name__ == "__main__":
    main()
