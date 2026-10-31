"""Create a source-only ZIP and file-by-file code document from an explicit allow-list."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parent.parent


def export() -> None:
    """Exclude all secrets, databases, caches, recordings and development environments."""
    names = [
        "app.py",
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        ".gitignore",
        ".dockerignore",
        "Dockerfile",
        "compose.yaml",
        "README.md",
        ".streamlit/config.toml",
        ".streamlit/secrets.toml.example",
        ".github/workflows/ci.yml",
    ]
    for directory, suffix in (
        ("core", ".py"),
        ("pages", ".py"),
        ("data", ".json"),
        ("tests", ".py"),
        ("scripts", ".py"),
    ):
        names.extend(
            path.relative_to(ROOT).as_posix()
            for path in sorted((ROOT / directory).glob("*" + suffix))
        )
    document = [
        "# Deutsch-Tutor — vollständiger Code, Datei für Datei\n",
        "Alle Quelldateien stehen zusätzlich unverändert im ZIP. "
        "Einrichtung und Deployment: siehe README.md.\n",
    ]
    for name in names:
        language = {
            ".py": "python",
            ".json": "json",
            ".toml": "toml",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
        }.get(Path(name).suffix, "text")
        document.extend(
            [
                f"\n## {name}\n",
                f"~~~~{language}\n",
                (ROOT / name).read_text(encoding="utf-8"),
                "\n~~~~\n",
            ]
        )
    (ROOT / "CODE.md").write_text("\n".join(document), encoding="utf-8")
    with ZipFile(ROOT.parent / "deutsch-tutor.zip", "w", ZIP_DEFLATED) as archive:
        for name in [*names, "CODE.md"]:
            archive.write(ROOT / name, "deutsch-tutor/" + name)
    print(f"Exported {len(names)} source files and CODE.md")


if __name__ == "__main__":
    export()
