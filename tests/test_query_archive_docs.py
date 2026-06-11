from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class QueryArchiveDocsTest(unittest.TestCase):
    def test_skill_routes_query_archives_to_queries_directory(self) -> None:
        skill = read("skills/llm-wiki-toolchain/SKILL.md")

        self.assertIn("Query Archive", skill)
        self.assertIn("wiki/queries/", skill)
        self.assertNotIn("如果同意，写入 `wiki/topics/` 或 `wiki/concepts/`", skill)

    def test_query_archive_reference_documents_boundaries(self) -> None:
        reference = read("skills/llm-wiki-toolchain/references/query-archive-workflow.md")

        self.assertIn("Archive-Worthy Query", reference)
        self.assertIn("Archive Confirmation", reference)
        self.assertIn("does not create a separate Query Plan", reference)
        self.assertIn("does not save chat answers into `raw/`", reference)
        self.assertIn("open", reference)
        self.assertIn("done", reference)
        self.assertIn("dropped", reference)

    def test_query_template_contains_required_metadata_and_sections(self) -> None:
        template = read("skills/llm-wiki-toolchain/templates/page-templates/query.md")

        for token in ("answer_version:", "indexed:", "basis_pages:"):
            self.assertIn(token, template)
        for heading in (
            "## 原始问题",
            "## Canonical Question",
            "## Question Context",
            "## 答案摘要",
            "## 综合回答",
            "## 依据页面",
            "## Raw Evidence",
            "## Review Notes",
            "## 后续动作",
            "## Related / Upgraded Pages",
            "## 修订记录",
        ):
            self.assertIn(heading, template)
        self.assertIn("[open]", template)
        self.assertIn("[done]", template)
        self.assertIn("[dropped]", template)

    def test_schema_index_and_log_define_query_archive_lifecycle(self) -> None:
        schema = read("skills/llm-wiki-toolchain/templates/SCHEMA.md")
        index = read("skills/llm-wiki-toolchain/templates/index.md")
        log = read("skills/llm-wiki-toolchain/templates/log.md")

        self.assertIn("Query Archive", schema)
        self.assertIn("Basis Pages are required", schema)
        self.assertIn("Raw Evidence is required", schema)
        self.assertIn("indexed: false", schema)
        self.assertIn("Answer Version", schema)
        self.assertIn("v1", index)
        self.assertIn("reviewed/medium", index)
        self.assertIn("query |", log)
        self.assertIn("answer_version", log)
        self.assertIn("Basis Pages", log)

    def test_readmes_describe_query_archive_discovery(self) -> None:
        zh = read("README.md")
        en = read("docs/README.en.md")

        self.assertIn("Query Archive", zh)
        self.assertIn("wiki/queries/", zh)
        self.assertIn("Query Archive", en)
        self.assertIn("wiki/queries/", en)

    def test_package_and_plugin_versions_match(self) -> None:
        package = json.loads(read("package.json"))
        plugin = json.loads(read(".claude-plugin/plugin.json"))

        self.assertEqual(package["version"], plugin["version"])


if __name__ == "__main__":
    unittest.main()
