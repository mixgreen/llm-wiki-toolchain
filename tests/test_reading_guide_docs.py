from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT_SCRIPT = ROOT / "skills" / "llm-wiki-toolchain" / "scripts" / "init.py"

spec = importlib.util.spec_from_file_location("init_wiki_script", INIT_SCRIPT)
init_wiki_script = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["init_wiki_script"] = init_wiki_script
spec.loader.exec_module(init_wiki_script)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class ReadingGuideDocsTest(unittest.TestCase):
    def test_skill_defines_reading_guide_workflow(self) -> None:
        skill = read("skills/llm-wiki-toolchain/SKILL.md")

        self.assertIn("## 详细解读：Reading Guide", skill)
        self.assertIn("wiki/readings/", skill)
        self.assertIn("普通 ingest 不自动创建 Reading Guide", skill)
        self.assertIn("<来源标题> - Reading Guide.md", skill)
        self.assertIn("相同 raw sha256", skill)
        self.assertIn("相同 source_url", skill)
        self.assertIn("references/reading-guide-workflow.md", skill)
        self.assertIn("Readable Wiki Page pass", skill)
        self.assertIn("references/readable-wiki-page-standard.md", skill)

    def test_reference_documents_match_evidence_and_boundaries(self) -> None:
        reference = read("skills/llm-wiki-toolchain/references/reading-guide-workflow.md")
        readable = read("skills/llm-wiki-toolchain/references/readable-wiki-page-standard.md")

        self.assertIn("does not add a generator script", reference)
        self.assertIn("does not automatically create Reading Guides during ordinary ingest", reference)
        self.assertIn("The default destination is `wiki/readings/`", reference)
        self.assertIn("<source title> - Reading Guide.md", reference)
        self.assertIn("same raw sha256", reference)
        self.assertIn("same source URL", reference)
        self.assertIn("explicit Source Summary link", reference)
        self.assertIn("explicit alias", reference)
        self.assertIn("not the primary evidence source", reference)
        self.assertIn("Readings section", reference)
        self.assertIn("Readability Pass", reference)
        self.assertIn("readable-wiki-page-standard.md", reference)
        self.assertIn("Readable Wiki Page is the writing standard", readable)
        self.assertIn("`wiki/readings/` | Required", readable)
        self.assertIn("`raw/` | None", readable)
        self.assertIn("Do not rewrite:", readable)
        self.assertIn("Humanizer-Style Checklist", readable)
        self.assertIn("inflated significance language", readable)

    def test_templates_and_schema_define_reading_guides(self) -> None:
        schema = read("skills/llm-wiki-toolchain/templates/SCHEMA.md")
        guide = read("skills/llm-wiki-toolchain/templates/page-templates/reading-guide.md")
        summary = read("skills/llm-wiki-toolchain/templates/page-templates/source-summary.md")

        self.assertIn("wiki/readings/", schema)
        self.assertIn("Reading Guide Pages", schema)
        self.assertIn("Do not put agent-authored Reading Guides in `raw/`", schema)
        self.assertIn("Readability Conventions", schema)
        self.assertIn("Raw sources are never humanized or rewritten", schema)
        for token in (
            "source_title:",
            "source_type:",
            "source_url:",
            "source_summary:",
            "raw_path:",
            "raw_sha256:",
            "indexed:",
        ):
            self.assertIn(token, guide)
        for heading in (
            "## 阅读入口",
            "## 这篇来源想解决什么问题",
            "## 核心思想",
            "## Trade-off 与局限",
            "## 和已有 wiki 知识的关系",
            "## Evidence Boundary",
            "## Readability Pass",
        ):
            self.assertIn(heading, guide)
        self.assertIn("每段只承担一个任务", guide)
        self.assertIn("direct quote、公式、代码", guide)
        self.assertIn("## 详细解读", summary)
        self.assertIn("- [[<来源标题> - Reading Guide]]", summary)

    def test_index_log_and_readmes_expose_reading_guides(self) -> None:
        index = read("skills/llm-wiki-toolchain/templates/index.md")
        log = read("skills/llm-wiki-toolchain/templates/log.md")
        zh = read("README.md")
        en = read("docs/README.en.md")

        self.assertIn("## Readings", index)
        self.assertIn("ReadingGuidePage", index)
        self.assertIn("reading | Reading Guide Title", log)
        self.assertIn("wiki/readings/", log)
        self.assertIn("Reading Guide", zh)
        self.assertIn("wiki/readings/", zh)
        self.assertIn("可读性标准", zh)
        self.assertIn("Reading Guide workflow", en)
        self.assertIn("wiki/readings/", en)
        self.assertIn("Ordinary ingest does not create Reading Guides automatically", en)
        self.assertIn("Readable Wiki Page standard", en)

    def test_init_creates_readings_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = init_wiki_script.init_wiki(Path(tmp), "reading-wiki", "Reading test")
            root = Path(tmp) / "reading-wiki"

            self.assertNotIn("error", result)
            self.assertTrue((root / "wiki" / "readings").is_dir())
            self.assertIn("reading-wiki/wiki/readings", result["dirs_created"])
            self.assertIn("wiki/readings/", (root / "SCHEMA.md").read_text(encoding="utf-8"))
            self.assertIn("## Readings", (root / "index.md").read_text(encoding="utf-8"))
            self.assertIn("wiki/readings/", (root / "log.md").read_text(encoding="utf-8"))

    def test_package_and_plugin_versions_are_1_5_0(self) -> None:
        package = json.loads(read("package.json"))
        plugin = json.loads(read(".claude-plugin/plugin.json"))

        self.assertEqual(package["version"], "1.5.0")
        self.assertEqual(plugin["version"], "1.5.0")
        self.assertEqual(package["version"], plugin["version"])


if __name__ == "__main__":
    unittest.main()
