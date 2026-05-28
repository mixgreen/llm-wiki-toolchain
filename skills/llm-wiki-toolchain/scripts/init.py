#!/usr/bin/env python3
"""
Initialize an LLM Wiki directory structure within an Obsidian vault or parent directory.

Usage:
    python3 init.py <vault_path> <wiki_name> [--topic "Topic description"]

Creates:
    <vault_path>/<wiki_name>/
    ├── raw/
    ├── wiki/entities/
    ├── wiki/concepts/
    ├── wiki/topics/
    ├── wiki/comparisons/
    ├── wiki/queries/
    ├── _archive/
    ├── _meta/topic-map.md
    ├── index.md
    ├── log.md
    └── SCHEMA.md

Templates are copied from the skill's templates/ directory.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path


def skill_dir() -> Path:
    """Find the skill directory (where this script lives)."""
    return Path(__file__).resolve().parent.parent


def load_template(name: str) -> str:
    """Load a template file from the templates/ directory."""
    template_path = skill_dir() / "templates" / name
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    print(f"Warning: template '{name}' not found at {template_path}, using empty placeholder")
    return f"# {name}\n"


def replace_placeholders(text: str, wiki_name: str, topic: str = "", today: str = "") -> str:
    """Replace template placeholders with actual values."""
    if not today:
        today = date.today().isoformat()
    topic_value = topic or f"Research wiki for {wiki_name}"
    return (
        text
        .replace("<WIKI_NAME>", wiki_name)
        .replace("<YYYY-MM-DD>", today)
        .replace("<Topic description — what this wiki is about, scope, boundaries>", topic_value)
        .replace("<Topic description>", topic_value)
    )


def init_wiki(vault_path: Path, wiki_name: str, topic: str = "") -> dict:
    """Initialize the wiki structure. Returns stats dict."""
    # Reject path traversal or absolute path components in wiki_name
    if "/" in wiki_name or "\\" in wiki_name or wiki_name.startswith("."):
        return {"error": f"Invalid wiki name (must not contain path separators or start with '.'): {wiki_name}"}

    wiki_root = vault_path / wiki_name
    # Ensure the resolved path is actually inside vault_path
    try:
        wiki_root.resolve().relative_to(vault_path.resolve())
    except ValueError:
        return {"error": f"Wiki path escapes parent directory: {wiki_root}"}

    today = date.today().isoformat()

    if wiki_root.exists():
        existing = list(wiki_root.rglob("*"))
        if existing:
            return {"error": f"Directory already exists and is not empty: {wiki_root}"}

    dirs = [
        "raw",
        "wiki/entities",
        "wiki/concepts",
        "wiki/topics",
        "wiki/comparisons",
        "wiki/queries",
        "_archive",
        "_meta",
    ]

    dirs_created = []
    for subdir in dirs:
        d = wiki_root / subdir
        d.mkdir(parents=True, exist_ok=True)
        dirs_created.append(str(d.relative_to(vault_path)))

    files_written = []
    for template_name, output_name in [
        ("SCHEMA.md", "SCHEMA.md"),
        ("index.md", "index.md"),
        ("log.md", "log.md"),
        ("topic-map.md", "_meta/topic-map.md"),
    ]:
        content = load_template(template_name)
        content = replace_placeholders(content, wiki_name, topic, today)
        out_path = wiki_root / output_name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        files_written.append(f"{wiki_name}/{output_name}")

    return {
        "vault_path": str(vault_path),
        "wiki_name": wiki_name,
        "wiki_root": str(wiki_root),
        "topic": topic or "(not specified)",
        "dirs_created": dirs_created,
        "files_written": files_written,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Initialize an LLM Wiki inside an Obsidian vault or parent directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 init.py ~/Documents/MyVault my-research-wiki --topic "Quantum Computing"
  python3 init.py "$VAULT_PATH" "读书笔记-三体" --topic "三体三部曲深度分析"
        """,
    )
    parser.add_argument("vault_path", help="Parent path where the wiki directory will be created")
    parser.add_argument("wiki_name", help="Name of the wiki directory to create")
    parser.add_argument("--topic", default="", help="Brief topic description for the schema")

    args = parser.parse_args()
    vault_path = Path(args.vault_path).expanduser().resolve()

    if not vault_path.exists():
        print(f"ERROR: Parent path does not exist: {vault_path}", file=sys.stderr)
        sys.exit(1)

    has_obsidian = (vault_path / ".obsidian").is_dir()
    has_md_files = any(vault_path.rglob("*.md"))
    if not has_obsidian and not has_md_files:
        print(f"WARNING: {vault_path} doesn't look like an Obsidian vault", file=sys.stderr)
        print("  (no .obsidian/ directory and no .md files found)", file=sys.stderr)
        print("  Continuing anyway because wiki may be stored beside existing vaults...", file=sys.stderr)

    result = init_wiki(vault_path, args.wiki_name, args.topic)

    if "error" in result:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ LLM Wiki initialized: {result['wiki_root']}")
    print(f"   Parent: {result['vault_path']}")
    print(f"   Wiki:   {result['wiki_name']}")
    print(f"   Topic:  {result['topic']}")
    print()
    print("Directories created:")
    for d in result["dirs_created"]:
        print(f"   📁 {d}")
    print()
    print("Files seeded:")
    for f in result["files_written"]:
        print(f"   📄 {f}")
    print()
    print("Next steps:")
    print("   1. Review and customize SCHEMA.md for your domain")
    print(f"   2. Add source documents to {result['wiki_name']}/raw/ with sha256 metadata")
    print("   3. Use single-source ingest for important sources, batch ingest for directories")
    print("   4. Open _meta/topic-map.md to sketch major reading routes")


if __name__ == "__main__":
    main()
