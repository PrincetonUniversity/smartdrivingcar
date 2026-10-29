"""Fail the deployment if private implementation or source mail leaks into Pages."""

from pathlib import Path


def check_site(root: Path = Path("_site")) -> None:
    if not (root / "index.html").is_file():
        raise ValueError("Built site is missing its homepage")
    for directory in (
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


if __name__ == "__main__":
    check_site()
