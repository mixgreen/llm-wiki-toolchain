#!/usr/bin/env python3
"""
LLM Wiki Lint — automated health check for an LLM Wiki vault.

Usage:
    python3 lint.py <wiki-root>                 # Full check
    python3 lint.py <wiki-root> --orphans       # Orphan pages only
    python3 lint.py <wiki-root> --broken        # Broken links only
    python3 lint.py <wiki-root> --index         # Index consistency only
    python3 lint.py <wiki-root> --raw           # Raw sha256 only
    python3 lint.py <wiki-root> --quality       # Frontmatter quality signals only
    python3 lint.py <wiki-root> --pages A,B     # Focus checks on touched pages
    python3 lint.py <wiki-root> --json          # JSON output

Exit codes: 0 = clean, 1 = issues found, 2 = error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
LOG_HEADER_RE = re.compile(r"^## \[(\d{4})-\d{2}-\d{2}\]", re.MULTILINE)
VALID_STATUS = {"draft", "reviewed", "stable"}
VALID_CONFIDENCE = {"low", "medium", "high"}
QUALITY_DIRS = {"concepts", "topics", "comparisons", "queries"}
TAG_TAXONOMY_RE = re.compile(r"## Tag Taxonomy(?P<body>.*?)(?:\n## |\Z)", re.DOTALL | re.IGNORECASE)
TAG_LIST_RE = re.compile(r"tags\s*:\s*\[([^\]]*)\]")



def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False


def _parse_frontmatter_fallback(raw: str) -> dict[str, Any]:
    """Line-level parser for environments without PyYAML.
    Supports: scalars, booleans, null, single-line lists. Does NOT support
    multi-line values, nested objects, or commas inside quoted list items."""
    data: dict[str, Any] = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value in {"", "null", "None"}:
            data[key] = None
        elif value.lower() == "true":
            data[key] = True
        elif value.lower() == "false":
            data[key] = False
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            data[key] = [] if not inner else [x.strip().strip('"\'') for x in inner.split(",")]
        else:
            data[key] = value.strip('"\'')
    return data


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str, bool]:
    """Parse YAML frontmatter. Uses PyYAML when available, falls back to a
    line-level parser that handles the common subset used by LLM Wiki pages."""
    match = FRONTMATTER_RE.match(content)
    if not match:
        return {}, content, False
    raw = match.group(1)
    body = content[match.end():]
    if _HAS_YAML:
        try:
            data = yaml.safe_load(raw)
            if not isinstance(data, dict):
                data = {}
        except yaml.YAMLError:
            data = _parse_frontmatter_fallback(raw)
    else:
        data = _parse_frontmatter_fallback(raw)
    return data, body, True


def extract_wikilinks(content: str) -> list[str]:
    return [m.group(1).strip() for m in WIKILINK_RE.finditer(content)]


def unique_pages(page_map: dict[str, Path]) -> list[Path]:
    seen = set()
    out = []
    for path in page_map.values():
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            out.append(path)
    return sorted(out, key=lambda p: str(p))


def find_wiki_pages(wiki_root: Path, include_archive: bool = False) -> dict[str, Path]:
    """Build a map of page stem -> Path. Case-insensitive lookup uses a separate key."""
    pages: dict[str, Path] = {}
    search_roots = []
    wiki_dir = wiki_root / "wiki"
    if wiki_dir.is_dir():
        search_roots.append(wiki_dir)
    if include_archive and (wiki_root / "_archive").is_dir():
        search_roots.append(wiki_root / "_archive")

    for root in search_roots:
        for md in root.rglob("*.md"):
            stem = md.stem
            pages[stem] = md
            # Only store lowercase fallback if it doesn't collide with an exact-match entry
            lower = stem.lower()
            if lower not in pages:
                pages[lower] = md
    return pages


def resolve_link(link_target: str, known_pages: dict[str, Path]) -> Path | None:
    if link_target in known_pages:
        return known_pages[link_target]
    if link_target.lower() in known_pages:
        return known_pages[link_target.lower()]
    return None


def normalize_page_filters(wiki_root: Path, pages_arg: str | None) -> set[str] | None:
    if not pages_arg:
        return None
    filters = set()
    for item in pages_arg.split(","):
        item = item.strip()
        if not item:
            continue
        filters.add(item)
        filters.add(Path(item).stem)
        try:
            p = (wiki_root / item).resolve()
            filters.add(str(p))
            filters.add(str(p.relative_to(wiki_root)))
        except Exception:
            pass
    return filters


def page_matches_filter(path: Path, wiki_root: Path, filters: set[str] | None) -> bool:
    if filters is None:
        return True
    rel = str(path.relative_to(wiki_root))
    return path.stem in filters or rel in filters or str(path.resolve()) in filters


def check_orphans(wiki_root: Path, all_pages: dict[str, Path], filters: set[str] | None = None) -> list[dict]:
    inbound = defaultdict(int)
    for path in unique_pages(all_pages):
        content = read_text(path)
        for link in extract_wikilinks(content):
            resolved = resolve_link(link, all_pages)
            if resolved:
                inbound[resolved.resolve()] += 1

    orphans = []
    for path in unique_pages(all_pages):
        if not page_matches_filter(path, wiki_root, filters):
            continue
        if path.stem in {"index", "log", "topic-map"}:
            continue
        if inbound.get(path.resolve(), 0) == 0:
            orphans.append({
                "page": path.stem,
                "path": str(path.relative_to(wiki_root)),
                "inbound_links": 0,
            })
    return sorted(orphans, key=lambda x: x["page"])


def check_broken_links(wiki_root: Path, all_pages: dict[str, Path], filters: set[str] | None = None) -> list[dict]:
    broken = []
    seen = set()
    for path in unique_pages(all_pages):
        if not page_matches_filter(path, wiki_root, filters):
            continue
        content = read_text(path)
        for link in extract_wikilinks(content):
            if link in {"index", "log"}:
                continue
            if resolve_link(link, all_pages) is None:
                key = (str(path), link)
                if key not in seen:
                    seen.add(key)
                    broken.append({
                        "source_page": path.stem,
                        "source_path": str(path.relative_to(wiki_root)),
                        "broken_link": link,
                    })
    return sorted(broken, key=lambda x: (x["source_page"], x["broken_link"]))


def check_index(wiki_root: Path, all_pages: dict[str, Path], filters: set[str] | None = None) -> dict:
    index_path = wiki_root / "index.md"
    if not index_path.exists():
        return {"error": "index.md not found", "missing_from_index": [], "stale_in_index": []}

    index_links = set(extract_wikilinks(read_text(index_path)))
    actual_pages = set()
    for path in unique_pages(all_pages):
        if path.stem in {"index", "log", "topic-map"}:
            continue
        if filters is not None and not page_matches_filter(path, wiki_root, filters):
            continue
        # Only current wiki pages should be in index, archive is excluded by default via all_pages.
        actual_pages.add(path.stem)

    missing_from_index = actual_pages - index_links
    stale_in_index = set()
    if filters is None:
        stale_in_index = index_links - {p.stem for p in unique_pages(all_pages)} - {"index", "log", "topic-map"}

    return {
        "missing_from_index": sorted(missing_from_index),
        "stale_in_index": sorted(stale_in_index),
    }


def check_quality(wiki_root: Path, all_pages: dict[str, Path], filters: set[str] | None = None) -> list[dict]:
    issues = []
    for path in unique_pages(all_pages):
        if not page_matches_filter(path, wiki_root, filters):
            continue
        rel_parts = path.relative_to(wiki_root).parts
        page_type = rel_parts[1] if len(rel_parts) >= 3 and rel_parts[0] == "wiki" else "unknown"
        content = read_text(path)
        fm, _, has_fm = parse_frontmatter(content)
        if not has_fm:
            issues.append({"page": path.stem, "path": str(path.relative_to(wiki_root)), "issue": "missing_frontmatter"})
            continue
        for required in ("tags", "created", "updated"):
            if required not in fm:
                issues.append({"page": path.stem, "path": str(path.relative_to(wiki_root)), "issue": f"missing_{required}"})
        if page_type in QUALITY_DIRS:
            status = fm.get("status")
            if status not in VALID_STATUS:
                issues.append({"page": path.stem, "path": str(path.relative_to(wiki_root)), "issue": "invalid_or_missing_status", "value": status})
        confidence = fm.get("confidence")
        if confidence is not None and confidence not in VALID_CONFIDENCE:
            issues.append({"page": path.stem, "path": str(path.relative_to(wiki_root)), "issue": "invalid_confidence", "value": confidence})
        if fm.get("contested") is True and not fm.get("contradictions"):
            issues.append({"page": path.stem, "path": str(path.relative_to(wiki_root)), "issue": "contested_without_contradictions"})
    return sorted(issues, key=lambda x: (x["page"], x["issue"]))


def check_raw_integrity(wiki_root: Path) -> list[dict]:
    issues = []
    raw_dir = wiki_root / "raw"
    if not raw_dir.is_dir():
        return issues
    for path in sorted(p for p in raw_dir.rglob("*") if p.is_file()):
        if path.name.startswith("."):
            continue
        try:
            data = path.read_bytes()
        except OSError as e:
            issues.append({"path": str(path.relative_to(wiki_root)), "issue": "unreadable", "error": str(e)})
            continue
        text = None
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            pass
        recorded = None
        body_bytes = data
        if text is not None:
            fm, body, has_fm = parse_frontmatter(text)
            recorded = fm.get("sha256") if has_fm else None
            if has_fm:
                body_bytes = body.encode("utf-8")
        # Binary files can carry sidecar hashes later; for now report missing metadata.
        if not recorded:
            issues.append({"path": str(path.relative_to(wiki_root)), "issue": "missing_sha256"})
            continue
        actual = hashlib.sha256(body_bytes).hexdigest()
        if str(recorded).lower() != actual.lower():
            issues.append({
                "path": str(path.relative_to(wiki_root)),
                "issue": "sha256_mismatch",
                "recorded": recorded,
                "actual": actual,
                "note": "sha256 is computed on body content (after frontmatter), not the entire file",
            })
    return issues


def check_page_size(wiki_root: Path, all_pages: dict[str, Path], filters: set[str] | None = None, limit: int = 200) -> list[dict]:
    issues = []
    for path in unique_pages(all_pages):
        if not page_matches_filter(path, wiki_root, filters):
            continue
        lines = read_text(path).splitlines()
        if len(lines) > limit:
            issues.append({"page": path.stem, "path": str(path.relative_to(wiki_root)), "lines": len(lines), "limit": limit})
    return sorted(issues, key=lambda x: -x["lines"])


def parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def check_stale_pages(wiki_root: Path, all_pages: dict[str, Path], filters: set[str] | None = None, days: int = 90) -> list[dict]:
    issues = []
    cutoff = date.today() - timedelta(days=days)
    for path in unique_pages(all_pages):
        if not page_matches_filter(path, wiki_root, filters):
            continue
        fm, _, has_fm = parse_frontmatter(read_text(path))
        if not has_fm:
            continue
        updated = parse_date(fm.get("updated"))
        if updated and updated < cutoff:
            age_days = (date.today() - updated).days
            issues.append({
                "page": path.stem,
                "path": str(path.relative_to(wiki_root)),
                "updated": updated.isoformat(),
                "age_days": age_days,
                "threshold_days": days,
            })
    return sorted(issues, key=lambda x: -x["age_days"])


def extract_schema_tags(wiki_root: Path) -> set[str]:
    schema_path = wiki_root / "SCHEMA.md"
    if not schema_path.exists():
        return set()
    content = read_text(schema_path)
    match = TAG_TAXONOMY_RE.search(content)
    if not match:
        return set()
    body = match.group("body")
    tags: set[str] = set()
    for list_match in TAG_LIST_RE.finditer(body):
        inner = list_match.group(1)
        tags.update(t.strip().strip('"\'') for t in inner.split(",") if t.strip())
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line.startswith("-"):
            continue
        # Supports "- tag", "- tag: description", and "- Group: tag, tag" forms.
        item = line.lstrip("-").strip()
        if not item or item.startswith("["):
            continue
        if ":" in item:
            _, rhs = item.split(":", 1)
            for token in re.split(r"[,，/、]", rhs):
                token = token.strip().strip("` ")
                if token and re.match(r"^[\w\-\u4e00-\u9fff]+$", token):
                    tags.add(token)
        else:
            token = item.split()[0].strip("` ")
            if token and re.match(r"^[\w\-\u4e00-\u9fff]+$", token):
                tags.add(token)
    return tags


def page_tags(frontmatter: dict[str, Any]) -> list[str]:
    tags = frontmatter.get("tags")
    if tags is None:
        return []
    if isinstance(tags, list):
        return [str(t).strip() for t in tags if str(t).strip()]
    return [t.strip() for t in str(tags).strip("[]").split(",") if t.strip()]


def check_tags(wiki_root: Path, all_pages: dict[str, Path], filters: set[str] | None = None) -> list[dict]:
    taxonomy = extract_schema_tags(wiki_root)
    if not taxonomy:
        return [{"issue": "missing_or_empty_tag_taxonomy", "path": "SCHEMA.md"}]
    issues = []
    for path in unique_pages(all_pages):
        if not page_matches_filter(path, wiki_root, filters):
            continue
        fm, _, has_fm = parse_frontmatter(read_text(path))
        if not has_fm:
            continue
        for tag in page_tags(fm):
            if tag not in taxonomy:
                issues.append({
                    "page": path.stem,
                    "path": str(path.relative_to(wiki_root)),
                    "issue": "tag_not_in_taxonomy",
                    "tag": tag,
                })
    return sorted(issues, key=lambda x: (x.get("tag", ""), x.get("page", "")))


def check_log_rotation(wiki_root: Path) -> list[dict]:
    issues = []
    log_path = wiki_root / "log.md"
    if not log_path.exists():
        return [{"issue": "missing_log", "path": "log.md"}]
    content = read_text(log_path)
    years = LOG_HEADER_RE.findall(content)
    if not years:
        return issues
    counts = Counter(years)
    current_year = str(date.today().year)
    old_years = sorted(y for y in counts if y != current_year)
    if old_years:
        issues.append({"issue": "log_contains_previous_years", "years": old_years})
    for year, count in sorted(counts.items()):
        if count > 500:
            issues.append({"issue": "log_year_exceeds_500_entries", "year": year, "entries": count})
    return issues


def check_topic_map(wiki_root: Path) -> list[dict]:
    path = wiki_root / "_meta" / "topic-map.md"
    if not path.exists():
        return [{"issue": "missing_topic_map", "path": "_meta/topic-map.md"}]
    return []


def run_lint(wiki_root: Path, checks: set[str] | None = None, include_archive: bool = False, pages: str | None = None) -> dict:
    if checks is None:
        checks = {"orphans", "broken", "index", "quality", "raw", "size", "stale", "tags", "log", "topic_map"}
    if not wiki_root.is_dir():
        return {"error": f"Wiki root not found: {wiki_root}"}

    filters = normalize_page_filters(wiki_root, pages)
    all_pages = find_wiki_pages(wiki_root, include_archive=include_archive)
    current_page_count = len(unique_pages(find_wiki_pages(wiki_root, include_archive=False)))
    results: dict[str, Any] = {
        "wiki_root": str(wiki_root),
        "total_pages": current_page_count,
        "include_archive": include_archive,
        "page_filter": pages or "",
    }

    if "orphans" in checks:
        results["orphans"] = check_orphans(wiki_root, all_pages, filters)
        results["orphan_count"] = len(results["orphans"])
    if "broken" in checks:
        results["broken_links"] = check_broken_links(wiki_root, all_pages, filters)
        results["broken_count"] = len(results["broken_links"])
    if "index" in checks:
        results["index"] = check_index(wiki_root, all_pages, filters)
    if "quality" in checks:
        results["quality"] = check_quality(wiki_root, all_pages, filters)
        results["quality_count"] = len(results["quality"])
    if "raw" in checks:
        results["raw_integrity"] = check_raw_integrity(wiki_root)
        results["raw_integrity_count"] = len(results["raw_integrity"])
    if "size" in checks:
        results["oversized_pages"] = check_page_size(wiki_root, all_pages, filters)
        results["oversized_count"] = len(results["oversized_pages"])
    if "stale" in checks:
        results["stale_pages"] = check_stale_pages(wiki_root, all_pages, filters)
        results["stale_count"] = len(results["stale_pages"])
    if "tags" in checks:
        results["tag_audit"] = check_tags(wiki_root, all_pages, filters)
        results["tag_audit_count"] = len(results["tag_audit"])
    if "log" in checks:
        results["log_rotation"] = check_log_rotation(wiki_root)
        results["log_rotation_count"] = len(results["log_rotation"])
    if "topic_map" in checks:
        results["topic_map"] = check_topic_map(wiki_root)
        results["topic_map_count"] = len(results["topic_map"])
    return results


def format_report(results: dict) -> str:
    lines = ["# LLM Wiki Lint Report", "", f"**Wiki:** `{results['wiki_root']}`", f"**Pages:** {results.get('total_pages', '?')}"]
    if results.get("page_filter"):
        lines.append(f"**Focused pages:** `{results['page_filter']}`")
    lines.append("")
    has_issues = False

    def section(title: str, items: list, ok: str, formatter):
        nonlocal has_issues
        if items is None:
            return
        lines.append(f"## {title}")
        if items:
            has_issues = True
            for item in items:
                lines.append(formatter(item))
            lines.append(f"")
            lines.append(f"**共 {len(items)} 项**")
        else:
            lines.append(f"✅ {ok}")
        lines.append("")

    section("孤页（无入链）", results.get("orphans"), "未发现孤页", lambda o: f"- ⚠️ [[{o['page']}]] — `{o['path']}`")
    section("断链（指向不存在的页面）", results.get("broken_links"), "未发现断链", lambda b: f"- 🔗 [[{b['source_page']}]] → `[[{b['broken_link']}]]`（不存在）")

    if "index" in results:
        idx = results["index"]
        lines.append("## 索引一致性")
        if "error" in idx:
            has_issues = True
            lines.append(f"- ⚠️ {idx['error']}")
        else:
            missing = idx.get("missing_from_index", [])
            stale = idx.get("stale_in_index", [])
            if missing or stale:
                has_issues = True
                for m in missing:
                    lines.append(f"- ➕ [[{m}]]（wiki 中存在但 index 未列）")
                for s in stale:
                    lines.append(f"- ➖ [[{s}]]（index 中列出但页面不存在）")
            else:
                lines.append("✅ index.md 与实际一致")
        lines.append("")

    section("页面质量信号", results.get("quality"), "页面 frontmatter / 质量信号通过", lambda q: f"- ⚠️ [[{q['page']}]] `{q['path']}` — {q['issue']}" + (f"（{q.get('value')}）" if 'value' in q else ""))

    raw_items = results.get("raw_integrity")
    if raw_items is not None:
        lines.append("## raw 完整性")
        lines.append("")
        lines.append("> 注：sha256 是对 body 内容（去掉 YAML frontmatter 后）计算的，不是整个文件。")
        lines.append("")
        if raw_items:
            has_issues = True
            for r in raw_items:
                lines.append(f"- ⚠️ `{r['path']}` — {r['issue']}")
            lines.append(f"")
            lines.append(f"**共 {len(raw_items)} 项**")
        else:
            lines.append("✅ raw/ sha256 检查通过")
        lines.append("")

    section("页面大小", results.get("oversized_pages"), "未发现超过 200 行的页面", lambda p: f"- 📄 [[{p['page']}]] `{p['path']}` — {p['lines']} 行（建议拆分）")
    section("过时候选页", results.get("stale_pages"), "未发现超过阈值的过时候选页", lambda p: f"- 🕰️ [[{p['page']}]] `{p['path']}` — updated={p['updated']}，{p['age_days']} 天未更新")
    section("标签审计", results.get("tag_audit"), "所有 tags 均在 taxonomy 中", lambda t: f"- 🏷️ [[{t.get('page', 'SCHEMA')}]] `{t.get('path', '')}` — {t['issue']}" + (f"：{t.get('tag')}" if t.get('tag') else ""))
    section("日志轮转", results.get("log_rotation"), "log.md 不需要轮转", lambda l: f"- 🕒 {l['issue']} " + ", ".join(f"{k}={v}" for k, v in l.items() if k != 'issue'))
    section("主题地图", results.get("topic_map"), "_meta/topic-map.md 存在", lambda t: f"- 🗺️ {t['issue']} — `{t.get('path', '')}`")

    if not has_issues:
        lines.append("## 🎉 全部通过")
        lines.append("")
        lines.append("未发现本次检查范围内的问题。")
    return "\n".join(lines)


def has_issues(results: dict) -> bool:
    if "error" in results:
        return True
    if results.get("orphan_count", 0) > 0 or results.get("broken_count", 0) > 0:
        return True
    idx = results.get("index", {})
    if idx.get("missing_from_index") or idx.get("stale_in_index") or idx.get("error"):
        return True
    for key in ("quality_count", "raw_integrity_count", "oversized_count", "stale_count", "tag_audit_count", "log_rotation_count", "topic_map_count"):
        if results.get(key, 0) > 0:
            return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="LLM Wiki Lint — automated health check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 lint.py ~/vaults/my-wiki
  python3 lint.py ~/vaults/my-wiki --orphans --broken
  python3 lint.py ~/vaults/my-wiki --pages "wiki/concepts/MS门.md,wiki/topics/某论文.md"
  python3 lint.py ~/vaults/my-wiki --json
        """,
    )
    parser.add_argument("wiki_root", help="Path to the LLM Wiki root directory")
    parser.add_argument("--orphans", action="store_true", help="Check orphan pages only")
    parser.add_argument("--broken", action="store_true", help="Check broken links only")
    parser.add_argument("--index", action="store_true", help="Check index consistency only")
    parser.add_argument("--raw", action="store_true", help="Check raw/ sha256 integrity only")
    parser.add_argument("--quality", action="store_true", help="Check frontmatter quality signals only")
    parser.add_argument("--size", action="store_true", help="Check oversized pages only")
    parser.add_argument("--stale", action="store_true", help="Check pages whose updated date is older than the threshold")
    parser.add_argument("--tags", action="store_true", help="Audit page tags against SCHEMA.md Tag Taxonomy")
    parser.add_argument("--log", action="store_true", help="Check log rotation only")
    parser.add_argument("--topic-map", action="store_true", help="Check _meta/topic-map.md only")
    parser.add_argument("--include-archive", action="store_true", help="Include _archive/ pages in page checks")
    parser.add_argument("--pages", default="", help="Comma-separated page names or relative paths for focused lint")
    parser.add_argument("--json", action="store_true", help="Output JSON for programmatic use")
    args = parser.parse_args()

    flag_map = {
        "orphans": args.orphans,
        "broken": args.broken,
        "index": args.index,
        "raw": args.raw,
        "quality": args.quality,
        "size": args.size,
        "stale": args.stale,
        "tags": args.tags,
        "log": args.log,
        "topic_map": args.topic_map,
    }
    selected = {name for name, enabled in flag_map.items() if enabled}
    checks = selected or None

    wiki_root = Path(args.wiki_root).expanduser().resolve()
    results = run_lint(wiki_root, checks=checks, include_archive=args.include_archive, pages=args.pages or None)

    if "error" in results:
        print(f"ERROR: {results['error']}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(format_report(results))

    sys.exit(1 if has_issues(results) else 0)


if __name__ == "__main__":
    main()
