"""Validate queued input files. Delete local source only after successful publication."""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from import_newsletter import (
    ensure_archive_pages,
    extract_body_from_eml,
    extract_date_from_eml_header,
    extract_subject_from_eml,
)
from publish_newsletter import parse_newsletter, write_issue


def import_pending() -> None:
    count = 0
    for directory in ("inbox", "import"):
        for path in sorted(Path(directory).glob("*")):
            if path.suffix.lower() == ".eml":
                issue = parse_newsletter(
                    extract_body_from_eml(str(path)),
                    extract_subject_from_eml(str(path)),
                    extract_date_from_eml_header(str(path)) or "",
                    curated=True,
                )
            elif path.suffix.lower() == ".html":
                subject = path.stem
                if re.match(r"^\d+\.\d+", subject):
                    subject = "SmartDrivingCars_" + subject
                issue = parse_newsletter(
                    path.read_text(), subject, date.today().isoformat(), curated=True
                )
            else:
                continue
            result = write_issue(issue)
            ensure_archive_pages(issue["date"])
            path.unlink()
            count += 1
            print(f"PASS: queued newsletter {result}")
    print(f"PASS: {count} queued newsletter(s) processed")


if __name__ == "__main__":
    import_pending()
