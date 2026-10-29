"""Restyle each curated archive entry without changing its prose or public route.

This is a reviewed migration for legacy Markdown, not the unattended mail parser.
Use --reference-site to preserve anchors from a previous Jekyll build. A complete
dry run validates all documents before --write changes any source file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import markdown
import yaml
from bs4 import BeautifulSoup, Comment, NavigableString, Tag
from publish_newsletter import ALLOWED, DROP, escape, safe_url

VERSION = 1
COMMENT = re.compile(r"\bHmm{2,}(?:\s*[.…!]+)", re.I)
DATE = re.compile(
    r"^(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|"
    r"January|February|March|April|May|June|July|August|September|October|November|December)\b",
    re.I,
)


def visible_text(node: BeautifulSoup | Tag) -> str:
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()


def text_fingerprint(node: BeautifulSoup | Tag) -> str:
    text = re.sub(r"\s+", "", node.get_text()).replace("\ufeff", "")
    return hashlib.sha256(text.encode()).hexdigest()


def heading_key(text: str) -> str:
    # Kramdown applies smart punctuation while the legacy Markdown source may not.
    return re.sub(r"[\W_]+", "", text).casefold()


def normalize_indentation(source: str) -> tuple[str, int]:
    lines = []
    changed = 0
    fence = ""
    in_list = False
    for original in source.splitlines():
        line = original.expandtabs(4)
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            if not fence:
                fence = marker[1][0]
            elif marker[1][0] == fence:
                fence = ""
            lines.append(line)
            continue
        if fence:
            lines.append(line)
            continue
        indent = len(line) - len(line.lstrip())
        list_item = bool(re.match(r"^\s*(?:[-*+] |\d+[.)] )", line))
        if line.strip() and indent == 0:
            in_list = list_item
        if in_list and indent >= 8 and not list_item and lines and not lines[-1].strip():
            in_list = False
        if line.strip() and indent >= 4 and (indent >= 12 or not in_list):
            line = line.lstrip()
            changed += 1
        lines.append(line)
    return "\n".join(lines), changed


def archive_url(value: str) -> str | None:
    if not value or re.search(r"[\x00-\x20\x7f\\]", value):
        return None
    if value.startswith("#"):
        return value
    if value.startswith("/") and not value.startswith("//"):
        return value if ".." not in unquote(urlsplit(value).path).split("/") else None
    if re.fullmatch(r"mailto:[^@<>\s?]+@[^@<>\s?]+\.[^@<>\s?]+", value, re.I):
        return value
    if re.fullmatch(r"tel:\+?[0-9().-]{3,40}", value, re.I):
        return value
    return safe_url(value)


def sanitize(soup: BeautifulSoup) -> int:
    repaired = 0
    for node in list(soup.find_all(string=lambda text: isinstance(text, Comment))):
        node.extract()
    for tag in list(soup.find_all(list(DROP))):
        tag.decompose()
    for tag in list(soup.find_all(True)):
        name = tag.name
        if name not in ALLOWED | {"img"}:
            tag.unwrap()
            continue
        attrs: dict[str, Any] = {}
        if name == "a":
            original = str(tag.get("href", ""))
            target = archive_url(original)
            if not target:
                tag.unwrap()
                continue
            repaired += target != original
            attrs = {"href": target, "rel": "noopener noreferrer"}
            if not tag.get_text(strip=True) and not tag.find("img"):
                attrs["aria-label"] = "Linked resource"
        elif name == "img":
            source = archive_url(str(tag.get("src", "")))
            if not source or source.startswith(("mailto:", "tel:", "#")):
                tag.replace_with(str(tag.get("alt", "")))
                continue
            attrs = {
                "src": source,
                "alt": str(tag.get("alt", "")),
                "loading": "lazy",
                "decoding": "async",
                "referrerpolicy": "no-referrer",
            }
        elif name == "ol" and str(tag.get("start", "")).isdigit():
            attrs["start"] = str(tag["start"])
        tag.attrs = attrs
    return repaired


def add_class(node: Tag, name: str) -> None:
    current = node.get("class", "")
    names = current if isinstance(current, list) else str(current).split()
    node["class"] = " ".join(dict.fromkeys([*names, name]))


def mark_commentary(soup: BeautifulSoup) -> int:
    count = 0
    active = False
    for node in list(soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])):
        if node.name != "p":
            active = False
            continue
        marker_node = None
        marker = None
        for text in node.find_all(string=True):
            candidate = COMMENT.search(str(text))
            if candidate:
                marker_node, marker = text, candidate
                break
        if marker is not None and marker_node is not None:
            # Split only a direct text child. Never flatten or damage nested links/emphasis.
            if marker_node.parent is node:
                editorial = soup.new_tag("p")
                prefix, rest = (
                    str(marker_node)[: marker.start()],
                    str(marker_node)[marker.start() :],
                )
                for sibling in list(marker_node.next_siblings):
                    editorial.append(sibling.extract())
                editorial.insert(0, NavigableString(rest))
                marker_node.replace_with(prefix)
                node.insert_after(editorial)
                if not node.get_text(strip=True) and not node.find("img"):
                    node.extract()
                node = editorial
            active = True
        if active:
            add_class(node, "newsletter-commentary")
            count += 1
        if re.search(r"\bAlain[.!…\s]*$", visible_text(node)):
            active = False
    return count


def restyle_markdown(
    source: str, *, anchors: dict[str, list[str]] | None = None
) -> tuple[str, dict[str, Any]]:
    normalized, dedented = normalize_indentation(source)
    soup = BeautifulSoup(
        markdown.markdown(normalized, extensions=["tables", "fenced_code", "sane_lists"]),
        "html.parser",
    )
    repaired = sanitize(soup)
    before = text_fingerprint(soup)
    links_before = [str(a["href"]) for a in soup.find_all("a", href=True)]
    used: set[str] = {"issue-title", "issue-contents"}
    headings: list[dict[str, str]] = []
    known: dict[str, list[str]] = defaultdict(list)
    for key, values in (anchors or {}).items():
        known[heading_key(key)].extend(values)
    for node in list(soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"])):
        text = visible_text(node)
        links = node.find_all("a")
        linked_title = (
            node.name == "p"
            and 20 <= len(text) <= 240
            and len(links) == 1
            and len(visible_text(links[0])) >= len(text) * 0.95
            and not DATE.search(text)
            and not re.match(r"^(?:https?://|\d+:\d+)", text)
        )
        if linked_title or node.name in {"h1", "h2", "h3"}:
            node.name = "h3"
            add_class(node, "newsletter-article-title")
        if node.name.startswith("h"):
            available = known.get(heading_key(text), [])
            anchor = available.pop(0) if available else "article-" + str(len(headings) + 1)
            original_anchor = anchor
            suffix = 1
            while anchor in used:
                suffix += 1
                anchor = f"{original_anchor}-{suffix}"
            used.add(anchor)
            node["id"] = anchor
            headings.append({"id": anchor, "title": text})
    # Short masthead paragraphs use the same compact treatment as current email imports.
    for node in soup.find_all(["p", "h3", "h4"]):
        if node.name != "p":
            break
        text = visible_text(node)
        if len(text) <= 160 and (DATE.search(text) or "edition of" in text.lower()):
            add_class(node, "newsletter-intro")
    commentary = mark_commentary(soup)
    after = text_fingerprint(soup)
    if before != after or links_before != [str(a["href"]) for a in soup.find_all("a", href=True)]:
        raise ValueError("Archive transformation changed prose or link order")
    rendered = str(soup).strip().replace("{", "&#123;").replace("}", "&#125;")
    clean_lines = []
    literal = False
    for line in rendered.splitlines():
        if "<pre>" in line:
            literal = True
        clean_lines.append(line if literal else line.rstrip())
        if "</pre>" in line:
            literal = False
    rendered = "\n".join(clean_lines)
    report = {
        "dedented_lines": dedented,
        "repaired_links": repaired,
        "headings": headings,
        "commentary": commentary,
        "text_preserved": True,
        "text_sha256": after,
    }
    return rendered, report


def restyle_document(
    source: str, *, anchors: dict[str, list[str]] | None = None
) -> tuple[str, dict[str, Any]]:
    if not source.startswith("---\n"):
        raise ValueError("Newsletter front matter is missing")
    _, frontmatter, body = source.split("---", 2)
    metadata = yaml.safe_load(frontmatter)
    if not isinstance(metadata, dict) or metadata.get("layout") != "newsletter":
        raise ValueError("Invalid newsletter layout")
    if metadata.get("presentation_version") == VERSION:
        return source, {"already_current": True, "text_preserved": True}
    if 'class="email-newsletter"' in body and metadata.get("parser_version") == 2:
        return source, {"reference": True, "text_preserved": True}
    rendered, report = restyle_markdown(body, anchors=anchors)
    # Preserve the original front matter byte-for-byte, including dates and public routes.
    extra = f"presentation_version: {VERSION}\npresentation_text_sha256: {report['text_sha256']}\n"
    route = unquote(str(metadata.get("permalink", ""))).strip("/")
    numbered = re.fullmatch(r"(\d{1,3}\.\d{1,3})¬?[- _](.+)", route)
    if numbered:
        label = re.sub(r"[-_](?:\d{6,8}|\d{1,2}[.-]\d{1,2}[.-]\d{2,4})$", "", numbered[2])
        label = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", label)
        label = re.sub(r"[-_]+", " ", label).strip(" .")
        if label:
            title = numbered[1] + " - " + label[0].upper() + label[1:]
            extra += yaml.safe_dump({"presentation_title": title}, allow_unicode=True)
    updated = "---\n" + frontmatter.lstrip("\n").rstrip() + "\n" + extra + "---\n\n"
    topics = [item for item in report["headings"] if item["title"]]
    if len(topics) >= 3:
        updated += '<nav class="newsletter-contents" aria-label="In this issue" markdown="0">\n'
        updated += (
            "<details><summary>In this issue <span>"
            + str(len(topics))
            + " sections</span></summary><ol>\n"
        )
        for topic in topics:
            updated += (
                '<li><a href="#'
                + escape(topic["id"])
                + '">'
                + escape(topic["title"])
                + "</a></li>\n"
            )
        updated += "</ol></details>\n</nav>\n\n"
    updated += '<div class="email-newsletter newsletter-archive-edition" markdown="0">\n'
    updated += rendered + "\n</div>\n"
    report["changed"] = updated != source
    return updated, report


def route_path(site: Path, permalink: str) -> Path:
    parsed = urlsplit(permalink)
    decoded = unquote(parsed.path)
    if (
        parsed.scheme
        or parsed.netloc
        or parsed.query
        or parsed.fragment
        or not decoded.startswith("/")
        or not decoded.endswith("/")
        or any(part in {".", ".."} for part in decoded.split("/"))
        or re.search(r"[\x00-\x1f\x7f\\]", decoded)
    ):
        raise ValueError("Invalid archived permalink")
    target = site / decoded.lstrip("/") / "index.html"
    if site.resolve() not in target.resolve().parents:
        raise ValueError("Archived route escaped its site directory")
    return target


def site_documents(site: Path) -> dict[str, Path]:
    result = {}
    for page in site.rglob("index.html"):
        soup = BeautifulSoup(page.read_text(), "html.parser")
        marker = soup.find("meta", attrs={"name": "newsletter-permalink"})
        if marker:
            permalink = str(marker["content"])
            if permalink in result:
                raise ValueError("Duplicate built newsletter route")
            result[permalink] = page
    return result


def reference_anchors(
    site: Path | None, permalink: str, *, pages: dict[str, Path] | None = None
) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    if site is None:
        return result
    page = route_path(site, permalink)
    if not page.is_file():
        page = (pages if pages is not None else site_documents(site)).get(permalink, page)
        if not page.is_file():
            raise ValueError("Previous build is missing an issue")
    soup = BeautifulSoup(page.read_text(), "html.parser")
    for heading in soup.select(
        ".newsletter-main h1, .newsletter-main h2, .newsletter-main h3, .newsletter-main h4, .newsletter-main h5, .newsletter-main h6"
    ):
        if heading.get("id"):
            result[visible_text(heading)].append(str(heading["id"]))
    return result


def check_archive_site(root: Path, site: Path, *, repair_routes: bool = False) -> int:
    pages = site_documents(site)
    count = 0
    for source in sorted((root / "_newsletters").rglob("index.md")):
        metadata = yaml.safe_load(source.read_text().split("---", 2)[1])
        permalink = metadata["permalink"]
        expected = route_path(site, permalink)
        actual = pages.get(permalink)
        if actual is None:
            raise ValueError("Newsletter missing from compiled site: " + source.parent.name)
        if actual != expected:
            if not repair_routes:
                raise ValueError("Jekyll did not preserve a newsletter route")
            if expected.exists():
                raise ValueError("Newsletter route repair would overwrite another document")
            expected.parent.mkdir(parents=True, exist_ok=True)
            actual.replace(expected)
        soup = BeautifulSoup(expected.read_text(), "html.parser")
        title = metadata.get(
            "presentation_title", metadata.get("display_name", metadata.get("title"))
        )
        header = soup.select_one("#issue-title")
        if header is None or visible_text(header) != re.sub(r"\s+", " ", str(title)).strip():
            raise ValueError("Compiled newsletter has an incorrect reader title")
        body = soup.select_one(".email-newsletter")
        if body is None or not visible_text(body):
            raise ValueError("Newsletter presentation is missing or empty")
        fingerprint = metadata.get("presentation_text_sha256")
        if fingerprint and fingerprint != text_fingerprint(body):
            raise ValueError("Compiled newsletter changed authored prose")
        for anchor in soup.select(".newsletter-contents a[href]"):
            target = str(anchor["href"]).removeprefix("#")
            if not body.find(id=target):
                raise ValueError("Newsletter contents link is broken")
        if body.select("script,iframe,object,embed,[style],[onclick]") or (
            metadata.get("presentation_version") and body.find(["h1", "h2"])
        ):
            raise ValueError("Newsletter contains unsafe or inconsistent presentation")
        count += 1
        print(f"PASS: compiled {source.parent.name}; route, prose and presentation verified")
    if count == 0:
        raise ValueError("No compiled newsletters checked")
    print(f"PASS: all {count} compiled newsletters verified")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--reference-site", type=Path)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--check-site", type=Path)
    parser.add_argument("--repair-routes", action="store_true")
    args = parser.parse_args()
    if args.check_site:
        check_archive_site(args.root, args.check_site, repair_routes=args.repair_routes)
        return
    paths = sorted((args.root / "_newsletters").rglob("index.md"))
    if not paths:
        raise ValueError("No newsletters found")
    pending = []
    receipts = []
    pages = site_documents(args.reference_site) if args.reference_site else None
    for path in paths:
        source = path.read_text()
        metadata = yaml.safe_load(source.split("---", 2)[1])
        anchors = reference_anchors(args.reference_site, metadata["permalink"], pages=pages)
        updated, report = restyle_document(source, anchors=anchors)
        pending.append((path, updated))
        receipts.append({"path": str(path), "permalink": metadata["permalink"], **report})
        print(
            f"PASS: {path.parent.name}; text preserved; headings={len(report.get('headings', []))}"
        )
    if args.write:
        for path, updated in pending:
            path.write_text(updated)
    if args.report:
        args.report.write_text(json.dumps(receipts, indent=2))
    print(
        f"PASS: completed all {len(paths)} issues; changed={sum(item.get('changed', False) for item in receipts)}; write={args.write}"
    )


if __name__ == "__main__":
    main()
