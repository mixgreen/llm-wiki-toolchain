from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "llm-wiki-toolchain" / "scripts" / "ingest_plan.py"

spec = importlib.util.spec_from_file_location("ingest_plan", SCRIPT)
ingest_plan = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["ingest_plan"] = ingest_plan
spec.loader.exec_module(ingest_plan)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def basic_wiki(root: Path) -> None:
    write(root / "index.md", "# Index\n\n- [[Existing Source]]\n- [[Agent沙盒安全模型]]\n")
    write(root / "log.md", "# Log\n")
    write(root / "SCHEMA.md", "# Schema\n")
    write(
        root / "wiki" / "topics" / "Existing Source.md",
        """---
tags: [topic]
aliases: [Existing Alias]
created: 2026-06-11
updated: 2026-06-11
status: draft
---
# Existing Source
""",
    )
    write(
        root / "wiki" / "concepts" / "Agent沙盒安全模型.md",
        """---
tags: [concept]
created: 2026-06-11
updated: 2026-06-11
status: draft
---
# Agent沙盒安全模型
""",
    )


class IngestPlanTest(unittest.TestCase):
    def test_text_source_reports_identity_and_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            basic_wiki(root)
            source = Path(tmp) / "paper-notes.md"
            write(source, "# Paper Notes\n\nImportant content.\n")
            before = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())

            plan = ingest_plan.build_plan(root, [str(source)])

            after = sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())
            self.assertEqual(before, after)
            first = plan["sources"][0]
            self.assertEqual(first["readiness"], "text-ready")
            self.assertEqual(first["identity"]["status"], "new-source")
            self.assertTrue(first["sha256"])
            self.assertEqual(first["proposed_raw_destination"], "raw/notes/paper-notes.md")

    def test_matching_raw_hash_is_already_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            basic_wiki(root)
            body = "# Same Source\n\nKnown body.\n"
            digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
            write(
                root / "raw" / "notes" / "same-source.md",
                f"""---
source_type: note
sha256: {digest}
---
{body}""",
            )
            source = Path(tmp) / "same-source.md"
            write(source, body)

            plan = ingest_plan.build_plan(root, [str(source)])

            self.assertEqual(plan["sources"][0]["identity"]["status"], "already-present")
            self.assertEqual(plan["sources"][0]["identity"]["matches"][0]["basis"], "sha256")

    def test_same_url_different_hash_reports_source_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            basic_wiki(root)
            old_body = "# URL Source\n\nOld body.\n"
            old_digest = hashlib.sha256(old_body.encode("utf-8")).hexdigest()
            write(
                root / "raw" / "web" / "url-source.md",
                f"""---
source_url: "https://example.com/paper"
source_type: article
sha256: {old_digest}
---
{old_body}""",
            )
            new_source = Path(tmp) / "new-url-source.md"
            write(
                new_source,
                """---
source_url: "https://example.com/paper"
source_type: article
---
# URL Source

New body.
""",
            )

            plan = ingest_plan.build_plan(root, [str(new_source)])

            identity = plan["sources"][0]["identity"]
            self.assertEqual(identity["status"], "source-drift")
            self.assertTrue(identity["requires_confirmation"])

    def test_url_without_hash_is_possible_existing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            basic_wiki(root)
            write(
                root / "raw" / "web" / "article.md",
                """---
source_url: "https://example.com/article"
source_type: article
sha256: abc
---
# Article
""",
            )

            plan = ingest_plan.build_plan(root, ["https://example.com/article"])

            identity = plan["sources"][0]["identity"]
            self.assertEqual(identity["status"], "possible-existing")
            self.assertTrue(identity["requires_confirmation"])

    def test_conservative_page_matching(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            basic_wiki(root)
            inventory = ingest_plan.page_inventory(root)

            exact = ingest_plan.match_page_title("Agent沙盒安全模型", inventory)
            near = ingest_plan.match_page_title("Agent 沙盒安全模型", inventory)
            alias = ingest_plan.match_page_title("Existing Alias", inventory)

            self.assertEqual(exact["operation"], "update")
            self.assertEqual(exact["match_type"], "exact-stem")
            self.assertEqual(near["operation"], "needs-confirmation")
            self.assertEqual(alias["operation"], "update")
            self.assertEqual(alias["match_type"], "explicit-alias")

    def test_overload_prone_batch_and_markdown_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            basic_wiki(root)
            sources = []
            for idx in range(6):
                source = Path(tmp) / f"source-{idx}.md"
                write(source, f"# Source {idx}\n\nBody.\n")
                sources.append(str(source))

            plan = ingest_plan.build_plan(root, sources)
            markdown = ingest_plan.format_markdown(plan)

            self.assertTrue(plan["overload_prone"])
            self.assertEqual(plan["recommended_next_step"], "narrow-scope")
            expected_order = [
                "## Source Summary",
                "## Candidate Knowledge Items",
                "## Page Impact",
                "## Risks and Confirmations",
                "## Recommended Next Step",
                "## Machine Data",
            ]
            positions = [markdown.index(section) for section in expected_order]
            self.assertEqual(positions, sorted(positions))
            self.assertIn("overload-prone", markdown)

    def test_json_cli_and_missing_path_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            basic_wiki(root)
            source = Path(tmp) / "source.md"
            write(source, "# Source\n")

            ok = subprocess.run(
                [sys.executable, str(SCRIPT), str(root), str(source), "--json"],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(ok.returncode, 0, ok.stderr)
            parsed = json.loads(ok.stdout)
            self.assertIn("sources", parsed)
            self.assertIn("page_impact", parsed)

            missing = subprocess.run(
                [sys.executable, str(SCRIPT), str(root), str(Path(tmp) / "missing.md")],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(missing.returncode, 2)
            self.assertIn("Source path not found", missing.stderr)

    def test_paper_lens_placeholder_for_pdf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            basic_wiki(root)
            source = Path(tmp) / "research.pdf"
            source.write_bytes(b"%PDF fake bytes")

            plan = ingest_plan.build_plan(root, [str(source)])
            markdown = ingest_plan.format_markdown(plan)

            self.assertEqual(plan["sources"][0]["readiness"], "text-extractable")
            self.assertIn("Paper Lens", markdown)
            self.assertIn("Research Question", markdown)


if __name__ == "__main__":
    unittest.main()
