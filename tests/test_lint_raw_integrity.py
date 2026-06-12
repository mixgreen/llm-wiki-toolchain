from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "llm-wiki-toolchain" / "scripts" / "lint.py"
SCHEMA = ROOT / "skills" / "llm-wiki-toolchain" / "templates" / "SCHEMA.md"

spec = importlib.util.spec_from_file_location("lint", SCRIPT)
lint = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["lint"] = lint
spec.loader.exec_module(lint)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


class RawIntegritySidecarTest(unittest.TestCase):
    def test_binary_pdf_with_valid_sidecar_passes_raw_integrity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            data = b"%PDF-1.7\nbinary body\n\xff\n%%EOF"
            digest = hashlib.sha256(data).hexdigest()
            pdf = root / "raw" / "papers" / "paper.pdf"
            write_bytes(pdf, data)
            write_text(Path(f"{pdf}.sha256"), f"{digest}\n")

            result = lint.run_lint(root, checks={"raw"})

            self.assertEqual([], result["raw_integrity"])
            self.assertEqual(0, result["raw_integrity_count"])

    def test_missing_binary_sidecar_reports_actionable_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            write_bytes(root / "raw" / "papers" / "paper.pdf", b"%PDF-1.7\nbinary body\n\xff")

            issues = lint.check_raw_integrity(root)

            self.assertEqual(1, len(issues))
            self.assertEqual("missing_sha256_sidecar", issues[0]["issue"])
            self.assertEqual("raw/papers/paper.pdf.sha256", issues[0]["sidecar"])

            cli = subprocess.run(
                [sys.executable, str(SCRIPT), str(root), "--raw"],
                check=False,
                text=True,
                capture_output=True,
            )
            self.assertEqual(1, cli.returncode)
            self.assertIn("missing_sha256_sidecar", cli.stdout)
            self.assertIn("raw/papers/paper.pdf.sha256", cli.stdout)

    def test_mismatched_binary_sidecar_reports_sha256_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            data = b"%PDF-1.7\nbinary body\n\xff"
            pdf = root / "raw" / "papers" / "paper.pdf"
            write_bytes(pdf, data)
            write_text(Path(f"{pdf}.sha256"), f"{'0' * 64}\n")

            issues = lint.check_raw_integrity(root)

            self.assertEqual(1, len(issues))
            self.assertEqual("sha256_mismatch", issues[0]["issue"])
            self.assertEqual("raw/papers/paper.pdf.sha256", issues[0]["sidecar"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), issues[0]["actual"])

    def test_text_raw_frontmatter_validation_continues_to_use_body_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "wiki"
            body = "# Source\n\nKnown body.\n"
            digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
            write_text(
                root / "raw" / "notes" / "valid.md",
                f"""---
sha256: {digest}
---
{body}""",
            )
            without_frontmatter = root / "raw" / "notes" / "without-frontmatter.md"
            write_text(without_frontmatter, body)
            write_text(Path(f"{without_frontmatter}.sha256"), f"{hashlib.sha256(body.encode('utf-8')).hexdigest()}\n")

            issues = lint.check_raw_integrity(root)

            self.assertEqual([{"path": "raw/notes/without-frontmatter.md", "issue": "missing_sha256"}], issues)

    def test_schema_documents_binary_sidecar_format(self) -> None:
        schema = SCHEMA.read_text(encoding="utf-8")

        self.assertIn("raw/papers/example.pdf.sha256", schema)
        self.assertIn("missing_sha256_sidecar", schema)
        self.assertIn("sha256_mismatch", schema)


if __name__ == "__main__":
    unittest.main()
