"""Fail the deployment if private implementation or source mail leaks into Pages."""

from pathlib import Path

from bs4 import BeautifulSoup


def check_site(root: Path = Path("_site")) -> None:
    if not (root / "index.html").is_file():
        raise ValueError("Built site is missing its homepage")
    for directory in (
        "build",
        "azure",
        "scripts",
        "config",
        "docs",
        "tests",
        "import",
        "inbox",
        "logs",
        "example-email",
        "pipeline",
        ".venv",
    ):
        if (root / directory).exists():
            raise ValueError("Private source directory found in Pages artifact")
    for file in root.rglob("*"):
        if file.is_file() and (
            file.suffix in {".eml", ".py", ".lock", ".db"} or file.name.startswith(".env")
        ):
            raise ValueError("Private source file found in Pages artifact")
    print("PASS: site contains no source emails or private pipeline directories")


def check_archive_navigation(root: Path = Path("_site")) -> int:
    pages = sorted((root / "newsletter").rglob("index.html"))
    if not pages:
        raise ValueError("Archive indexes are missing")
    for page in pages:
        soup = BeautifulSoup(page.read_text(), "html.parser")
        # Model the common cosmetic newsletter-signup filter in addition to
        # checking the rendered HTML, so navigation cannot adopt its selectors.
        for blocked in soup.select(".newsletter-sidebar, #newsletter-sidebar"):
            blocked.decompose()
        sidebar = soup.select_one(".archive-sidebar nav")
        if sidebar is None:
            raise ValueError("Archive navigation is missing")
        if soup.select(".archive-browser"):
            raise ValueError("Archive navigation has a duplicate disclosure")
        sidebar_links = {str(link["href"]) for link in sidebar.select("a[href]")}
        if not sidebar_links:
            raise ValueError("Archive navigation links are missing")
        if any(not target.startswith("/newsletter/") for target in sidebar_links):
            raise ValueError("Archive navigation contains a non-archive destination")
        if sidebar.select("script,form,input,button,[onclick],[onchange],[hidden]"):
            raise ValueError("Archive navigation must use ordinary native HTML")
        if sidebar.get("hidden") is not None or sidebar.get("aria-hidden") == "true":
            raise ValueError("Archive navigation was explicitly hidden")
    print(f"PASS: all {len(pages)} archive indexes retain native navigation without duplication")
    return len(pages)


if __name__ == "__main__":
    check_site()
    check_archive_navigation()
