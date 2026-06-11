#!/usr/bin/env python3
"""
LLM Wiki Ingest Plan — pre-write source-to-wiki impact report.

Usage:
    python3 ingest_plan.py <wiki-root> <source> [<source> ...]
    python3 ingest_plan.py <wiki-root> <source> --json

Exit codes: 0 = plan generated, 2 = input error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from lint import extract_wikilinks, find_wiki_pages, parse_frontmatter, read_text, unique_pages

PAGE_OPERATIONS = {"create", "update", "merge", "skip", "needs-confirmation"}
TEXT_READY_EXTENSIONS = {".md", ".markdown", ".txt", ".text", ".rst", ".csv", ".json", ".yaml", ".yml", ".py", ".js", ".ts"}
TEXT_EXTRACTABLE_EXTENSIONS = {".pdf", ".docx", ".html", ".htm", ".epub"}
REQUIRES_DERIVED_TEXT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ppt", ".pptx", ".mp4", ".mov", ".mp3", ".wav"}
PAPER_EXTENSIONS = {".pdf"}
SOURCE_TYPE_BY_EXT = {
    ".pdf": "paper",
    ".md": "note",
    ".markdown": "note",
    ".txt": "note",
    ".text": "note",
    ".html": "article",
    ".htm": "article",
    ".docx": "article",
    ".py": "code",
    ".js": "code",
    ".ts": "code",
}


class InputError(Exception):
    """Raised for hard input errors that should stop plan generation."""


def slugify(value: str, fallback: str = "source") -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff.-]+", "-", value.strip(), flags=re.UNICODE)
    slug = re.sub(r"-{2,}", "-", slug).strip("-.")
    return slug or fallback


def normalize_title(value: str) -> str:
    return re.sub(r"[\s_\-]+", "", value).lower()


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def looks_like_missing_path(value: str) -> bool:
    if is_url(value):
        return False
    path = Path(value).expanduser()
    if path.exists():
        return False
    if "/" in value or "\\" in value:
        return True
    suffix = path.suffix.lower()
    return bool(suffix and suffix in TEXT_READY_EXTENSIONS | TEXT_EXTRACTABLE_EXTENSIONS | REQUIRES_DERIVED_TEXT_EXTENSIONS)


def source_type_for_path(path: Path) -> str:
    return SOURCE_TYPE_BY_EXT.get(path.suffix.lower(), "other")


def readiness_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in TEXT_READY_EXTENSIONS:
        return "text-ready"
    if suffix in TEXT_EXTRACTABLE_EXTENSIONS:
        return "text-extractable"
    if suffix in REQUIRES_DERIVED_TEXT_EXTENSIONS:
        return "requires-derived-text"
    return "text-ready"


def body_hash_for_file(path: Path) -> tuple[str | None, int]:
    data = path.read_bytes()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return hashlib.sha256(data).hexdigest(), len(data)
    _, body, has_fm = parse_frontmatter(text)
    body_bytes = body.encode("utf-8") if has_fm else data
    return hashlib.sha256(body_bytes).hexdigest(), len(data)


def raw_destination(source: dict[str, Any]) -> str:
    source_type = source["source_type"]
    ext = source.get("extension") or ".md"
    title = source.get("title") or "source"
    slug = slugify(title)
    if source_type == "paper":
        return f"raw/papers/{slug}{ext if ext else '.md'}"
    if source_type == "article":
        return f"raw/web/{slug}.md"
    if source_type == "code":
        return f"raw/code/{slug}{ext if ext else '.md'}"
    return f"raw/notes/{slug}.md"


def build_source(input_value: str, sequence: int) -> dict[str, Any]:
    if is_url(input_value):
        parsed = urlparse(input_value)
        title = slugify(parsed.path.rsplit("/", 1)[-1] or parsed.netloc, fallback=f"url-{sequence}")
        source = {
            "input": input_value,
            "kind": "url",
            "title": title,
            "source_type": "article",
            "readiness": "text-extractable",
            "sha256": None,
            "source_url": input_value,
            "extension": ".md",
            "size_bytes": None,
            "notes": ["URL source requires extraction during approved ingest; this plan does not fetch or write it."],
        }
        source["proposed_raw_destination"] = raw_destination(source)
        return source

    path = Path(input_value).expanduser()
    if path.exists():
        if not path.is_file():
            raise InputError(f"Source is not a file: {input_value}")
        try:
            digest, size = body_hash_for_file(path)
        except OSError as exc:
            raise InputError(f"Cannot read source: {input_value}: {exc}") from exc
        text = read_text(path) if readiness_for_path(path) == "text-ready" else ""
        fm, _, has_fm = parse_frontmatter(text) if text else ({}, "", False)
        source_url = fm.get("source_url") if has_fm else None
        source_type = str(fm.get("source_type") or source_type_for_path(path)) if has_fm else source_type_for_path(path)
        title = str(fm.get("title") or path.stem) if has_fm else path.stem
        source = {
            "input": input_value,
            "kind": "file",
            "path": str(path),
            "title": title,
            "source_type": source_type,
            "readiness": readiness_for_path(path),
            "sha256": digest,
            "source_url": source_url,
            "extension": path.suffix.lower() or ".md",
            "size_bytes": size,
            "notes": [],
        }
        source["proposed_raw_destination"] = raw_destination(source)
        return source

    if looks_like_missing_path(input_value):
        raise InputError(f"Source path not found: {input_value}")

    text_bytes = input_value.encode("utf-8")
    title = f"pasted-note-{sequence}"
    source = {
        "input": input_value,
        "kind": "pasted",
        "title": title,
        "source_type": "note",
        "readiness": "text-ready",
        "sha256": hashlib.sha256(text_bytes).hexdigest(),
        "source_url": None,
        "extension": ".md",
        "size_bytes": len(text_bytes),
        "notes": ["Pasted content is treated as a source candidate; Tiny Note Exception still requires explicit user intent."],
    }
    source["proposed_raw_destination"] = raw_destination(source)
    return source


def raw_records(wiki_root: Path) -> list[dict[str, Any]]:
    raw_dir = wiki_root / "raw"
    if not raw_dir.is_dir():
        return []
    records = []
    for path in sorted(p for p in raw_dir.rglob("*") if p.is_file() and not p.name.startswith(".")):
        record: dict[str, Any] = {"path": str(path.relative_to(wiki_root)), "title": path.stem}
        try:
            digest, _ = body_hash_for_file(path)
        except OSError as exc:
            record["error"] = str(exc)
            records.append(record)
            continue
        record["actual_sha256"] = digest
        text = read_text(path)
        fm, _, has_fm = parse_frontmatter(text)
        if has_fm:
            record["sha256"] = str(fm.get("sha256") or "")
            record["source_url"] = fm.get("source_url")
            record["source_type"] = fm.get("source_type")
        records.append(record)
    return records


def source_identity(source: dict[str, Any], records: list[dict[str, Any]]) -> dict[str, Any]:
    digest = source.get("sha256")
    source_url = source.get("source_url")
    matches: list[dict[str, Any]] = []
    drift: list[dict[str, Any]] = []
    weak_hints: list[dict[str, Any]] = []
    possible_existing: list[dict[str, Any]] = []

    for record in records:
        recorded_hash = (record.get("sha256") or record.get("actual_sha256") or "").lower()
        actual_hash = (record.get("actual_sha256") or "").lower()
        if digest and digest.lower() in {recorded_hash, actual_hash}:
            matches.append({"path": record["path"], "basis": "sha256"})
            continue
        if source_url and record.get("source_url") == source_url:
            if digest and recorded_hash and digest.lower() != recorded_hash:
                drift.append({"path": record["path"], "basis": "same source_url with different sha256"})
            elif not digest:
                possible_existing.append({"path": record["path"], "basis": "same source_url without source sha256"})
            else:
                matches.append({"path": record["path"], "basis": "same source_url"})
            continue
        if normalize_title(source["title"]) == normalize_title(record["title"]) and source["title"] != record["title"]:
            weak_hints.append({"path": record["path"], "basis": "similar filename"})

    if drift:
        status = "source-drift"
        requires_confirmation = True
    elif matches:
        status = "already-present"
        requires_confirmation = False
    elif possible_existing:
        status = "possible-existing"
        requires_confirmation = True
    elif weak_hints:
        status = "possible-duplicate"
        requires_confirmation = True
    else:
        status = "new-source"
        requires_confirmation = False
    return {
        "status": status,
        "matches": matches,
        "possible_existing": possible_existing,
        "source_drift": drift,
        "weak_duplicate_hints": weak_hints,
        "requires_confirmation": requires_confirmation,
    }


def page_inventory(wiki_root: Path) -> dict[str, Any]:
    pages = unique_pages(find_wiki_pages(wiki_root, include_archive=False))
    exact_stems: dict[str, str] = {}
    normalized_stems: dict[str, list[dict[str, str]]] = {}
    aliases: dict[str, str] = {}
    wikilinks: dict[str, str] = {}

    for path in pages:
        rel = str(path.relative_to(wiki_root))
        exact_stems[path.stem] = rel
        normalized_stems.setdefault(normalize_title(path.stem), []).append({"title": path.stem, "path": rel})
        content = read_text(path)
        fm, _, has_fm = parse_frontmatter(content)
        if has_fm:
            raw_aliases = fm.get("aliases") or fm.get("alias") or []
            if isinstance(raw_aliases, str):
                raw_aliases = [raw_aliases]
            if isinstance(raw_aliases, list):
                for alias in raw_aliases:
                    aliases[str(alias)] = rel
        for link in extract_wikilinks(content):
            wikilinks[link] = exact_stems.get(link, rel)

    index_path = wiki_root / "index.md"
    if index_path.exists():
        for link in extract_wikilinks(read_text(index_path)):
            if link in exact_stems:
                wikilinks[link] = exact_stems[link]

    return {
        "exact_stems": exact_stems,
        "normalized_stems": normalized_stems,
        "aliases": aliases,
        "wikilinks": wikilinks,
        "page_count": len(pages),
    }


def match_page_title(title: str, inventory: dict[str, Any]) -> dict[str, Any]:
    if title in inventory["exact_stems"]:
        return {"operation": "update", "match_type": "exact-stem", "title": title, "path": inventory["exact_stems"][title]}
    if title in inventory["wikilinks"]:
        return {"operation": "update", "match_type": "exact-wikilink", "title": title, "path": inventory["wikilinks"][title]}
    if title in inventory["aliases"]:
        return {"operation": "update", "match_type": "explicit-alias", "title": title, "path": inventory["aliases"][title]}

    near = inventory["normalized_stems"].get(normalize_title(title), [])
    if len(near) > 1:
        return {"operation": "merge", "match_type": "multiple-near-matches", "title": title, "candidates": near}
    if len(near) == 1:
        return {"operation": "needs-confirmation", "match_type": "near-title", "title": title, "candidates": near}
    return {"operation": "create", "match_type": "none", "title": title, "path": f"wiki/topics/{slugify(title)}.md"}


def source_summary_impact(source: dict[str, Any], inventory: dict[str, Any]) -> dict[str, Any]:
    title = source["title"]
    match = match_page_title(title, inventory)
    match["kind"] = "source-summary"
    match["source_title"] = title
    return match


def semantic_placeholders() -> dict[str, list[dict[str, Any]]]:
    return {
        "entities": [{"status": "semantic-review-required", "required_fields": ["name", "reason", "operation"]}],
        "concepts": [{"status": "semantic-review-required", "required_fields": ["name", "reason", "operation"]}],
        "claims": [{"status": "semantic-review-required", "required_fields": ["claim", "excerpt_or_locator", "operation"]}],
    }


def paper_lens(source: dict[str, Any]) -> dict[str, str] | None:
    if source["source_type"] != "paper" and source.get("extension") not in PAPER_EXTENSIONS:
        return None
    return {
        "research_question": "To complete during Semantic Plan Review.",
        "method": "To complete during Semantic Plan Review.",
        "main_contribution": "To complete during Semantic Plan Review.",
        "limitations": "To complete during Semantic Plan Review.",
        "follow_up_value": "To complete during Semantic Plan Review.",
    }


def build_plan(wiki_root: Path, source_inputs: list[str]) -> dict[str, Any]:
    if not wiki_root.is_dir():
        raise InputError(f"Wiki root not found: {wiki_root}")
    records = raw_records(wiki_root)
    inventory = page_inventory(wiki_root)
    sources = []
    page_impact = []
    risks = []

    for idx, source_input in enumerate(source_inputs, start=1):
        source = build_source(source_input, idx)
        source["identity"] = source_identity(source, records)
        lens = paper_lens(source)
        if lens:
            source["paper_lens"] = lens
        sources.append(source)
        impact = source_summary_impact(source, inventory)
        page_impact.append(impact)
        if source["readiness"] == "requires-derived-text":
            risks.append({"severity": "medium", "kind": "source-readiness", "message": f"{source['title']} requires derived text before semantic review."})
        if source["identity"]["status"] == "source-drift":
            risks.append({"severity": "high", "kind": "source-drift", "message": f"{source['title']} has the same source_url as an existing raw file but a different sha256."})
        if source["identity"]["status"] == "possible-duplicate":
            risks.append({"severity": "medium", "kind": "possible-duplicate", "message": f"{source['title']} has weak filename-level duplicate hints."})
        if impact["operation"] in {"needs-confirmation", "merge"}:
            risks.append({"severity": "medium", "kind": "page-match", "message": f"{source['title']} has ambiguous page impact: {impact['match_type']}."})

    overload = len(sources) > 5 or len(page_impact) > 10
    if overload:
        risks.append({"severity": "medium", "kind": "overload-prone-review", "message": "Review covers more than five sources or more than ten impacted pages."})

    recommended = "proceed-after-semantic-review"
    if overload:
        recommended = "narrow-scope"
    elif risks:
        recommended = "revise-or-confirm"

    return {
        "generated_at": date.today().isoformat(),
        "wiki_root": str(wiki_root),
        "mode": "single-source" if len(sources) == 1 else "batch",
        "boundary": "plan-only-no-writes",
        "sources": sources,
        "candidate_knowledge_items": semantic_placeholders(),
        "page_impact": page_impact,
        "overload_prone": overload,
        "risks": risks,
        "recommended_next_step": recommended,
        "allowed_page_operations": sorted(PAGE_OPERATIONS),
    }


def format_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Ingest Plan Report",
        "",
        f"**Boundary:** {plan['boundary']}",
        f"**Mode:** {plan['mode']}",
        f"**Generated:** {plan['generated_at']}",
        "",
        "## Source Summary",
        "",
    ]
    for idx, source in enumerate(plan["sources"], start=1):
        identity = source["identity"]
        lines.extend([
            f"### {idx}. {source['title']}",
            f"- Input kind: `{source['kind']}`",
            f"- Source type: `{source['source_type']}`",
            f"- Readiness: `{source['readiness']}`",
            f"- sha256: `{source['sha256'] or 'unavailable-before-extraction'}`",
            f"- Source identity: `{identity['status']}`",
            f"- Proposed Raw Destination: `{source['proposed_raw_destination']}`",
        ])
        if source.get("source_url"):
            lines.append(f"- Source URL: {source['source_url']}")
        for match in identity.get("matches", []):
            lines.append(f"- Existing raw match: `{match['path']}` ({match['basis']})")
        for possible in identity.get("possible_existing", []):
            lines.append(f"- Possible existing raw source: `{possible['path']}` ({possible['basis']})")
        for drift in identity.get("source_drift", []):
            lines.append(f"- Source Drift: `{drift['path']}` ({drift['basis']})")
        for hint in identity.get("weak_duplicate_hints", []):
            lines.append(f"- Weak duplicate hint: `{hint['path']}` ({hint['basis']})")
        if source.get("paper_lens"):
            lines.extend(["", "**Paper Lens**"])
            for key, value in source["paper_lens"].items():
                label = key.replace("_", " ").title()
                lines.append(f"- {label}: {value}")
        lines.append("")

    lines.extend([
        "## Candidate Knowledge Items",
        "",
        "> Deterministic skeleton only. The agent must complete Semantic Plan Review before writes.",
        "",
        "- Entities: name, reason, operation.",
        "- Concepts: name, reason, operation.",
        "- Claims: claim, excerpt or locator, operation.",
        "",
        "## Page Impact",
        "",
    ])
    for item in plan["page_impact"]:
        detail = item.get("path") or ", ".join(c["path"] for c in item.get("candidates", [])) or "new page"
        lines.append(f"- Source Summary `{item['source_title']}` -> `{item['operation']}` ({item['match_type']}): `{detail}`")
    lines.extend(["", "## Risks and Confirmations", ""])
    if plan["risks"]:
        for risk in plan["risks"]:
            lines.append(f"- `{risk['severity']}` `{risk['kind']}`: {risk['message']}")
    else:
        lines.append("- No deterministic risks found. Semantic review may still add confirmations.")
    lines.extend([
        "",
        "## Recommended Next Step",
        "",
    ])
    if plan["recommended_next_step"] == "narrow-scope":
        lines.append("Narrow the source or page scope before ingest. This review is overload-prone.")
    elif plan["recommended_next_step"] == "revise-or-confirm":
        lines.append("Resolve confirmations or revise the plan before approved ingest writes.")
    else:
        lines.append("Complete Semantic Plan Review, then ask for explicit Plan Approval before any writes.")
    lines.extend([
        "",
        "## Machine Data",
        "",
        "Run with `--json` for the machine-readable mirror of this report.",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LLM Wiki Ingest Plan — pre-write source-to-wiki impact report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 ingest_plan.py ~/vaults/my-wiki paper.md
  python3 ingest_plan.py ~/vaults/my-wiki paper.md https://example.com/article --json
        """,
    )
    parser.add_argument("wiki_root", help="Path to the LLM Wiki root directory")
    parser.add_argument("sources", nargs="+", help="Source paths, URLs, or pasted content")
    parser.add_argument("--json", action="store_true", help="Output JSON for tests and automation")
    args = parser.parse_args()

    try:
        plan = build_plan(Path(args.wiki_root).expanduser(), args.sources)
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(plan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
