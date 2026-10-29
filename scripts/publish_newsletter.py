"""Deterministic newsletter rendering and validated, idempotent publication.

Untrusted email content is never interpreted as Liquid, YAML, or executable HTML.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlsplit

import yaml
from bs4 import BeautifulSoup, Comment, Doctype, NavigableString, Tag
from import_newsletter import ensure_archive_pages

SLUG = re.compile(r"\d{1,3}\.\d{1,3}-[A-Za-z0-9]+(?:[-.][A-Za-z0-9]+)*")
SUBJECT = re.compile(
    r"^SmartDrivingCars?(?:\.com[/ ]|\s+eLetter\.*\s*|[ _/-]+)(\d{1,3}\.\d{1,3}[- _].+)$", re.I
)
ALLOWED = {
    "p",
    "span",
    "div",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "br",
    "hr",
    "strong",
    "b",
    "em",
    "i",
    "u",
    "blockquote",
    "ul",
    "ol",
    "li",
    "a",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "sup",
    "sub",
    "pre",
    "code",
}
DROP = {
    "script",
    "style",
    "iframe",
    "object",
    "embed",
    "form",
    "input",
    "button",
    "textarea",
    "select",
    "svg",
    "math",
    "head",
    "meta",
    "link",
    "template",
}
MAX_BODY = 2_000_000


def safe_url(value: str) -> str | None:
    """Unwrap Outlook Safe Links without a network request; allow web links only."""
    value = value.strip()
    for _ in range(4):
        if len(value) > 8192 or re.search(r"[\s\x00-\x1f\x7f\\]", value):
            return None
        try:
            url = urlsplit(value)
            if (
                url.scheme.lower() not in {"https", "http"}
                or not url.hostname
                or url.username
                or url.password
            ):
                return None
            if url.hostname.lower().endswith(".safelinks.protection.outlook.com"):
                value = parse_qs(url.query).get("url", [""])[0]
                continue
            return value
        except ValueError:
            return None
    return None


def escape(value: str) -> str:
    # Liquid executes before Markdown; HTML entity encoding prevents template execution.
    return html.escape(value, quote=True).replace("{", "&#123;").replace("}", "&#125;")


def remove_html_gateway_banner(soup: BeautifulSoup) -> None:
    """Remove the bounded warning block using DOM boundaries, not source lines."""
    start = re.compile(r"^\W*SECURITY\s+WARNING\b", re.I)
    end = re.compile(r"phish\s*bowl", re.I)
    for block in list(soup.find_all(["table", "td", "div", "p"])):
        if block.parent is None or getattr(block, "decomposed", False):
            continue
        text = block.get_text(" ", strip=True)
        if not start.search(text):
            continue
        nodes = [str(node).strip() for node in block.find_all(string=True) if str(node).strip()]
        # Do not remove an enclosing article container that continues past the warning.
        if len(text) <= 2000 and any(end.search(node) for node in nodes[-2:]):
            block.decompose()
            continue
        if block.name != "p":
            continue
        bounded = [block] + list(block.find_next_siblings())[:14]
        chars = 0
        for index, sibling in enumerate(bounded):
            content = sibling.get_text(" ", strip=True)
            chars += len(content)
            if chars > 2000:
                break
            if end.search(content):
                for warning in bounded[: index + 1]:
                    warning.decompose()
                break


PRESENTATION_CLASSES = {
    "newsletter-accent",
    "newsletter-blue-emphasis",
    "newsletter-article-title",
    "newsletter-intro",
    "newsletter-upright",
    "newsletter-normal-weight",
    "newsletter-image-alt",
}
RED_INK = {"red", "#ff0000", "#c00000", "#c82613", "rgb(192,0,0)", "rgb(200,38,19)"}
BLUE_INK = {"blue", "#0000ff", "#0563c1", "rgb(0,0,255)"}


def word_style(node: Tag) -> dict[str, str]:
    """Interpret only semantic cues, never pass email CSS to the web page."""
    return {
        key.strip().lower(): value.strip().lower()
        for declaration in str(node.get("style", "")).split(";")
        if ":" in declaration
        for key, value in [declaration.split(":", 1)]
    }


def article_heading(node: Tag) -> bool:
    if node.name != "p":
        return False
    text = node.get_text(" ", strip=True)
    links = node.find_all("a")
    if not 20 <= len(text) <= 240 or len(links) != 1:
        return False
    if len(links[0].get_text(" ", strip=True)) < len(text) * 0.9:
        return False
    if not safe_url(str(links[0].get("href", ""))):
        return False
    if re.search(
        r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+[A-Za-z]+\.?\s+\d{1,2},\s+\d{4}",
        text,
        re.I,
    ):
        return False
    for styled in [node, *node.find_all(style=True)]:
        size = word_style(styled).get("font-size", "")
        match = re.fullmatch(r"(\d+(?:\.\d+)?)pt", size)
        if match and float(match.group(1)) >= 14:
            return True
    return False


def safe_html(body: str) -> str:
    if not isinstance(body, str) or len(body.encode()) > MAX_BODY:
        raise ValueError("Newsletter body is missing or too large")
    soup = BeautifulSoup(body, "html.parser")
    remove_html_gateway_banner(soup)
    for node in list(soup.find_all(string=lambda text: isinstance(text, (Comment, Doctype)))):
        node.extract()
    for tag in list(soup.find_all(list(DROP))):
        tag.decompose()
    for node in soup.find_all(string=re.compile(r"TICKET_URL\(", re.I)):
        node.replace_with(re.sub(r"TICKET_URL\([^)]*\)", "", str(node), flags=re.I))
    for paragraph in list(soup.find_all("p")):
        if not paragraph.get_text(strip=True) and not paragraph.find(["img", "hr"]):
            paragraph.decompose()
    # Remove per-recipient Listserv subscription tickets and historical appendices.
    for tag in list(soup.find_all(["p", "div"])):
        if tag.parent is None:
            continue
        text = tag.get_text(" ", strip=True)
        if re.match(
            r"^(Previous SmartDrivingCars|To unsubscribe from this list|This list is maintained by)",
            text,
            re.I,
        ):
            for sibling in list(tag.find_next_siblings()):
                sibling.extract()
            tag.extract()
    for tag in list(soup.find_all("a")):
        href = str(tag.get("href", ""))
        if "TICKET_URL(" in href or (
            "lists.princeton.edu" in href.lower()
            and re.search(r"[?&](?:TICKET|SUBED1|SIGNOFF)=", href, re.I)
        ):
            tag.extract()

    intro_count = 0
    for paragraph in soup.find_all(["p", "h1", "h2", "h3"]):
        if paragraph.name != "p" or article_heading(paragraph) or intro_count >= 5:
            break
        centered = (
            str(paragraph.get("align", "")).lower() == "center"
            or word_style(paragraph).get("text-align") == "center"
        )
        if centered and 0 < len(paragraph.get_text(" ", strip=True)) <= 160:
            paragraph["class"] = "newsletter-intro"
            intro_count += 1

    def render(node: Any) -> str:
        if isinstance(node, NavigableString):
            return escape(str(node))
        if not isinstance(node, Tag):
            return ""
        if node.name == "img":
            # CID images and tracking pixels cannot load; retain descriptive alt text.
            alternative = escape(str(node.get("alt", "")))
            return (
                '<span class="newsletter-image-alt">' + alternative + "</span>"
                if alternative.strip()
                else ""
            )
        content = "".join(render(child) for child in node.children)
        if (
            node.name == "p"
            and not BeautifulSoup("<div>" + content + "</div>", "html.parser").get_text(strip=True)
            and not re.search(r"<(?:br|hr)\b", content)
        ):
            return ""
        style = word_style(node)
        if style.get("font-weight") in {"bold", "700", "800", "900"} and node.name not in {
            "b",
            "strong",
        }:
            content = "<strong>" + content + "</strong>"
        if style.get("font-style") == "italic" and node.name not in {"i", "em"}:
            content = "<em>" + content + "</em>"
        if style.get("text-decoration") == "underline" and node.name != "u":
            content = "<u>" + content + "</u>"
        raw_classes = node.get("class")
        class_names = (
            raw_classes
            if isinstance(raw_classes, list)
            else (raw_classes.split() if isinstance(raw_classes, str) else [])
        )
        classes = set(class_names) & PRESENTATION_CLASSES
        if style.get("font-style") == "normal":
            classes.add("newsletter-upright")
        if style.get("font-weight") in {"normal", "400"}:
            classes.add("newsletter-normal-weight")
        color = re.sub(r"\s+", "", style.get("color", ""))
        if color in RED_INK:
            classes.add("newsletter-accent")
        elif color in BLUE_INK and node.name != "a":
            classes.add("newsletter-blue-emphasis")
        name = node.name
        if article_heading(node):
            name = "h3"
            classes.add("newsletter-article-title")
        if name not in ALLOWED or (name == "span" and not classes):
            return content
        attrs = ""
        if name == "a":
            target = safe_url(str(node.get("href", "")))
            if not target:
                return content
            parsed = urlsplit(target)
            if parsed.hostname in {"smartdrivingcar.com", "www.smartdrivingcar.com"} and re.match(
                r"^/(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s",
                unquote(parsed.path),
                re.I,
            ):
                return content
            if not BeautifulSoup("<div>" + content + "</div>", "html.parser").get_text(strip=True):
                content = escape(target)
            attrs = f' href="{escape(target)}" rel="noopener noreferrer"'
        if classes:
            attrs += ' class="' + " ".join(sorted(classes)) + '"'
        if name in {"br", "hr"}:
            return f"<{name}>"
        return f"<{name}{attrs}>{content}</{name}>"

    rendered = "".join(render(child) for child in soup.children).strip()
    # Unwrapping Word's spans can join whitespace nodes. Canonicalize once so
    # Function and receiver fingerprints agree, while preserving preformatted text.
    canonical = BeautifulSoup("<div>" + rendered + "</div>", "html.parser").div
    if canonical is None:
        raise ValueError("Newsletter HTML normalization failed")
    return canonical.decode_contents().replace("{", "&#123;").replace("}", "&#125;")


def validate_slug(slug: Any) -> str:
    if not isinstance(slug, str) or len(slug) > 160 or not SLUG.fullmatch(slug):
        raise ValueError("Invalid newsletter identifier")
    return slug


def parse_newsletter(
    body: str, subject: str, received: str, *, curated: bool = False
) -> dict[str, str]:
    if not isinstance(subject, str) or len(subject) > 240 or "\n" in subject or "\r" in subject:
        raise ValueError("Invalid newsletter subject")
    match = SUBJECT.fullmatch(subject.strip())
    if not match:
        raise ValueError("Subject is not a newsletter issue")
    slug = validate_slug(re.sub(r"[ _/-]+", "-", match.group(1)))
    suffix = re.search(r"-(\d{1,2})[.-](\d{1,2})[.-](\d{2}|\d{4})$", slug)
    if not suffix:
        raise ValueError("Newsletter identifier must include its issue date")
    month, day, year = map(int, suffix.groups())
    issue_date = date(year + 2000 if year < 100 else year, month, day)
    received_date = date.fromisoformat(received[:10])
    if issue_date > received_date:
        raise ValueError("Issue date is later than mailbox receipt date")
    rendered = safe_html(body)
    if len(BeautifulSoup(rendered, "html.parser").get_text(strip=True)) < 80:
        raise ValueError("Newsletter body is empty or unexpectedly short")
    display = re.sub(r"-\d{1,2}[.-]\d{1,2}[.-]\d{2,4}$", "", slug).replace("-", " ")
    display = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", display)
    display = re.sub(r"^(\d+\.\d+ )(.)", lambda m: m.group(1) + m.group(2).upper(), display)
    title = re.sub(r"^(\d+\.\d+) ", r"\1 - ", display)
    metadata = {
        "layout": "newsletter",
        "title": title,
        "date": issue_date.isoformat(),
        "permalink": f"/{slug}/",
        "display_name": title,
        "source_sha256": hashlib.sha256(rendered.encode()).hexdigest(),
        "parser_version": 2,
        "source_authority": "curated" if curated else "mailbox",
    }
    markdown = "---\n" + yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True) + "---\n\n"
    # A block element prevents Markdown from reinterpreting literal email text as links/HTML.
    markdown += '<div class="email-newsletter" markdown="0">\n' + rendered + "\n</div>\n"
    return {"slug": slug, "date": issue_date.isoformat(), "markdown": markdown}


def write_issue(issue: dict[str, str], root: Path = Path(".")) -> str:
    slug = validate_slug(issue["slug"])
    destination = root / "_newsletters" / slug / "index.md"
    # Case-insensitive deduplication also works on Linux CI.
    collection = root / "_newsletters"
    if collection.exists():
        for path in collection.iterdir():
            if path.name.casefold() == slug.casefold() and (path / "index.md").exists():
                existing = (path / "index.md").read_text()
                metadata = (
                    yaml.safe_load(existing.split("---", 2)[1])
                    if existing.startswith("---\n")
                    else {}
                )
                incoming = yaml.safe_load(issue["markdown"].split("---", 2)[1])
                if (
                    (metadata or {}).get("source_authority") != "curated"
                    and (metadata or {}).get("source_sha256")
                    and metadata["source_sha256"] != incoming["source_sha256"]
                ):
                    raise ValueError("Newsletter content conflict: manual review required")
                issue["slug"] = path.name
                return "duplicate"
    if destination.parent.is_symlink() or collection.is_symlink():
        raise ValueError("Symlink output directory is not allowed")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as stream:
        stream.write(issue["markdown"])
    return "created"


def receive_dispatch(payload: Any, root: Path = Path(".")) -> dict[str, str]:
    """Re-render legacy dispatch Markdown as untrusted content, never trust YAML."""
    if not isinstance(payload, dict):
        raise ValueError("Invalid dispatch payload")
    slug = validate_slug(payload.get("slug"))
    source = payload.get("markdown", "")
    if not isinstance(source, str) or len(source.encode()) > MAX_BODY:
        raise ValueError("Invalid dispatch body")
    if source.startswith("---\n"):
        parts = source.split("---", 2)
        if len(parts) != 3:
            raise ValueError("Invalid dispatch front matter")
        source = parts[2]
    # Markdown is converted to HTML before the same strict sanitizer is applied.
    import markdown

    issue = parse_newsletter(
        markdown.markdown(source, extensions=["tables"]),
        "SmartDrivingCars_" + slug,
        payload.get("date", ""),
    )
    write_issue(issue, root)
    return issue


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eml", type=Path)
    parser.add_argument("--dispatch", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dispatch:
        if args.dry_run:
            parser.error("Dispatch dry run is not supported; use local EML preview")
        payload = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())["client_payload"]
        issue = receive_dispatch(payload)
    elif args.eml:
        from import_newsletter import (
            extract_body_from_eml,
            extract_date_from_eml_header,
            extract_subject_from_eml,
        )

        issue = parse_newsletter(
            extract_body_from_eml(str(args.eml)),
            extract_subject_from_eml(str(args.eml)),
            extract_date_from_eml_header(str(args.eml)) or "",
            curated=True,
        )
        if args.dry_run:
            print(issue["markdown"], end="")
            return
        print(write_issue(issue))
    else:
        parser.error("Choose --eml or --dispatch")
    ensure_archive_pages(issue["date"])
    Path("pipeline-result.json").write_text(json.dumps({"issues": [issue["slug"]]}))
    print("PASS: newsletter validated")


if __name__ == "__main__":
    main()
