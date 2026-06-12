from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class SourceSummaryQualityDocsTest(unittest.TestCase):
    def test_skill_defines_source_summary_quality_workflow(self) -> None:
        skill = read("skills/llm-wiki-toolchain/SKILL.md")

        self.assertIn("## 来源摘要：Source Summary Quality", skill)
        self.assertIn("2-3 分钟内理解来源主线", skill)
        self.assertIn("Problem、Approach、Key Claim、Limitation、Wiki Impact", skill)
        self.assertIn("按来源论证顺序排列", skill)
        self.assertIn("references/source-summary-quality.md", skill)
        self.assertIn("详细解释放 Reading Guide", skill)

    def test_reference_documents_spine_evidence_and_boundaries(self) -> None:
        reference = read("skills/llm-wiki-toolchain/references/source-summary-quality.md")

        self.assertIn("Source Summary is the compact source-entry page", reference)
        self.assertIn("## Source Spine", reference)
        for token in ("Problem", "Approach", "Key Claim", "Limitation", "Wiki Impact"):
            self.assertIn(token, reference)
        self.assertIn("research question -> method / system -> main result -> limitation -> wiki impact", reference)
        self.assertIn("Core points should be ordered by the source's logic", reference)
        self.assertIn("Raw locators are required for:", reference)
        self.assertIn("numeric details", reference)
        self.assertIn("paper conclusions", reference)
        self.assertIn("Reading Guides can explain why a claim matters", reference)
        self.assertIn("not the proof path", reference)
        self.assertIn("Do not migrate every old Source Summary", reference)

    def test_template_and_schema_define_source_spine(self) -> None:
        schema = read("skills/llm-wiki-toolchain/templates/SCHEMA.md")
        template = read("skills/llm-wiki-toolchain/templates/page-templates/source-summary.md")

        self.assertIn("### Source Summary Pages (`wiki/topics/`)", schema)
        self.assertIn("2-3 minute view", schema)
        self.assertIn("Source Spine", schema)
        self.assertIn("Order `核心要点` by the source's logic", schema)
        self.assertIn("A Source Summary may link to a Reading Guide", schema)

        self.assertIn("## 来源主线", template)
        for token in ("Problem:", "Approach:", "Key Claim:", "Limitation:", "Wiki Impact:"):
            self.assertIn(token, template)
        self.assertIn("按来源逻辑排序", template)
        self.assertIn("强 claim、数值、论文结论", template)
        self.assertIn("## Raw Evidence", template)
        self.assertIn("## 详细解读", template)

    def test_readmes_expose_source_summary_quality(self) -> None:
        zh = read("README.md")
        en = read("docs/README.en.md")

        self.assertIn("Source Summary", zh)
        self.assertIn("来源主线", zh)
        self.assertIn("2-3 分钟读懂问题、方法、结论、局限和 wiki 影响", zh)
        self.assertIn("Source Summary quality standard", en)
        self.assertIn("Source Spine", en)
        self.assertIn("problem, approach, key claim, limitation, and wiki impact", en)

    def test_package_and_plugin_versions_match(self) -> None:
        package = json.loads(read("package.json"))
        plugin = json.loads(read(".claude-plugin/plugin.json"))

        self.assertEqual(package["version"], plugin["version"])


if __name__ == "__main__":
    unittest.main()
