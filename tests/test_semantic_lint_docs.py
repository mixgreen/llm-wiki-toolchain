from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class SemanticLintDocsTest(unittest.TestCase):
    def test_skill_has_independent_semantic_lint_section(self) -> None:
        skill = read("skills/llm-wiki-toolchain/SKILL.md")

        self.assertIn("### Semantic Lint：知识健康审查", skill)
        self.assertIn("LLM-assisted knowledge health review", skill)
        self.assertIn("不是 `lint.py` 的替代品", skill)
        self.assertIn("V1 不提供 `semantic_lint.py`", skill)
        self.assertIn("不添加 `lint.py --semantic`", skill)
        self.assertIn("references/semantic-lint-workflow.md", skill)

    def test_reference_defines_taxonomy_shape_report_and_no_auto_fix(self) -> None:
        reference = read("skills/llm-wiki-toolchain/references/semantic-lint-workflow.md")

        for finding_type in (
            "Contradiction Candidate",
            "Missing Page Candidate",
            "Stale Claim Candidate",
            "Weak Evidence Candidate",
            "Index Summary Drift",
            "Overgrown Page Candidate",
        ):
            self.assertIn(finding_type, reference)

        for field in (
            "type:",
            "title:",
            "affected_pages:",
            "evidence:",
            "confidence:",
            "severity:",
            "recommended_action:",
            "rationale:",
            "confirmation_question:",
        ):
            self.assertIn(field, reference)

        for section in (
            "## Summary",
            "## High Severity Findings",
            "## Medium / Low Severity Findings",
            "## Confirmation Queue",
            "## Suggested Maintenance Actions",
            "## Machine Data",
        ):
            self.assertIn(section, reference)

        self.assertIn("Focused Semantic Lint", reference)
        self.assertIn("Topic Semantic Lint", reference)
        self.assertIn("Wiki-Wide Semantic Lint", reference)
        self.assertIn("overload-prone", reference)
        self.assertIn("Semantic Lint does not modify wiki pages automatically", reference)
        self.assertIn("Query Archive is optional follow-up only", reference)
        self.assertIn("confidence` and `severity` are separate", reference)

    def test_schema_carries_semantic_lint_convention(self) -> None:
        schema = read("skills/llm-wiki-toolchain/templates/SCHEMA.md")

        self.assertIn("## Semantic Lint Conventions", schema)
        self.assertIn("knowledge health review", schema)
        self.assertIn("Mechanical lint output is Mechanical Lint Signal", schema)
        self.assertIn("Stale Page", schema)
        self.assertIn("Stale Claim Candidate", schema)
        self.assertIn("Confidence and severity are separate", schema)
        self.assertIn("until the finding is confirmed", schema)

    def test_readmes_describe_semantic_lint_without_full_automation_claim(self) -> None:
        zh = read("README.md")
        en = read("docs/README.en.md")

        self.assertIn("Semantic Lint 知识健康审查", zh)
        self.assertIn("结构化待确认项", zh)
        self.assertIn("Semantic Lint knowledge health review", en)
        self.assertIn("structured findings for confirmation", en)
        self.assertIn("not deterministic lint errors or automatic fixes", en)

    def test_lint_script_does_not_define_semantic_cli_mode(self) -> None:
        lint_py = read("skills/llm-wiki-toolchain/scripts/lint.py")

        self.assertNotIn("--semantic", lint_py)
        self.assertNotIn("semantic-lint", lint_py)
        self.assertNotIn("Semantic Lint", lint_py)

    def test_package_and_plugin_versions_match(self) -> None:
        package = json.loads(read("package.json"))
        plugin = json.loads(read(".claude-plugin/plugin.json"))

        self.assertEqual(package["version"], plugin["version"])


if __name__ == "__main__":
    unittest.main()
