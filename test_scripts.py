"""Tests for the bundled helper scripts. Run: python -m unittest discover -s tests"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "from-need-to-market" / "scripts"
EXAMPLE = ROOT / "examples" / "whatsapp-quotation"
TEMPLATES = ROOT / "skills" / "from-need-to-market" / "assets" / "templates"
sys.path.insert(0, str(SCRIPTS))

import create_research_directory as crd  # noqa: E402
import validate_research_output as vro  # noqa: E402


class CreateDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_slugify_keeps_cjk_and_strips_unsafe_characters(self):
        self.assertEqual(crd.slugify(" WhatsApp 询盘/转报价: test? "), "WhatsApp-询盘-转报价-test")
        self.assertEqual(crd.slugify("..\\..\\evil"), "evil")
        self.assertEqual(crd.slugify("???"), "research")
        self.assertLessEqual(len(crd.slugify("长" * 200)), 72)

    def test_repeat_run_gets_suffix_and_keeps_old_files(self):
        first = crd.create_research_directory(self.tmp, "topic", "2026-11-12")
        (first / "marker.txt").write_text("keep", encoding="utf-8")
        second = crd.create_research_directory(self.tmp, "topic", "2026-11-12")
        third = crd.create_research_directory(self.tmp, "topic", "2026-11-12")
        self.assertEqual(first.name, "2026-11-12-topic")
        self.assertEqual(second.name, "2026-11-12-topic-02")
        self.assertEqual(third.name, "2026-11-12-topic-03")
        self.assertEqual((first / "marker.txt").read_text(encoding="utf-8"), "keep")

    def test_exact_output_dir_collision_and_file_error(self):
        target = self.tmp / "a" / "b"
        self.assertEqual(crd.create_unique_directory(target).name, "b")
        self.assertEqual(crd.create_unique_directory(target).name, "b-02")
        plain = self.tmp / "plain.txt"
        plain.write_text("x", encoding="utf-8")
        with self.assertRaises(NotADirectoryError):
            crd.create_unique_directory(plain)

    def test_invalid_date_is_rejected(self):
        with self.assertRaises(ValueError):
            crd.create_research_directory(self.tmp, "topic", "2026-13-40")

    def test_cli_prints_only_the_path_on_stdout(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "create_research_directory.py"),
             "--output-dir", str(self.tmp / "exact"), "--date", "2026-01-01"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(Path(result.stdout.strip()).name, "exact")
        self.assertIn("--date", result.stderr)


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.copy = self.tmp / "run"
        shutil.copytree(EXAMPLE, self.copy)

    def edit(self, name, old, new, count=1):
        path = self.copy / name
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, count), encoding="utf-8")

    def errors(self, **kwargs):
        return "\n".join(vro.validate(self.copy, **kwargs).errors)

    def test_published_example_passes(self):
        report = vro.validate(EXAMPLE)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_templates_fail_until_placeholders_are_replaced(self):
        self.assertIn("占位符", "\n".join(vro.validate(TEMPLATES).errors))

    def test_missing_file(self):
        (self.copy / "02-evidence-log.md").unlink()
        self.assertIn("02-evidence-log.md: 文件缺失", self.errors())

    def test_results_file_is_optional(self):
        (self.copy / "04-action-results.md").unlink()
        errors = self.errors()
        self.assertNotIn("文件缺失", errors)
        # The example links to 04, so those links are now correctly reported as broken.
        self.assertIn("链接目标不存在: 04-action-results.md", errors)

    def test_free_text_research_status(self):
        self.edit("00-start-here.md", "**调研状态**：完成", "**调研状态**：基本做完了")
        self.assertIn("调研状态必须", self.errors())

    def test_duplicate_card_id(self):
        self.edit("01-market-cards.md", "### M02", "### M01")
        self.assertIn("卡片编号重复: M01", self.errors())

    def test_card_order(self):
        self.edit("01-market-cards.md", "### C01", "### M09")
        self.assertIn("卡片顺序", self.errors())

    def test_dangling_card_reference_including_ranges(self):
        self.edit("03-action-plan.md", "## 当前决策", "## 当前决策\n\n参见 P40 和 E01–E09。")
        errors = self.errors()
        self.assertIn("不存在的卡片 P40", errors)
        self.assertIn("不存在的卡片 E09", errors)

    def test_prices_are_not_card_ids(self):
        self.edit("00-start-here.md", "## 原始需求", "## 原始需求\n\n起价 R799/月。")
        self.assertEqual(self.errors(), "")

    def test_evidence_card_must_be_traceable(self):
        path = self.copy / "02-evidence-log.md"
        path.write_text(path.read_text(encoding="utf-8").replace("E07", "证据七"), encoding="utf-8")
        self.assertIn("找不到 E07", self.errors())

    def test_action_missing_field_and_bad_status(self):
        self.edit("03-action-plan.md", "- **验收条件**", "- **其他**")
        self.edit("03-action-plan.md", "- **状态**：等待材料", "- **状态**：随缘")
        errors = self.errors()
        self.assertIn("A01 缺少字段：验收条件", errors)
        self.assertIn("A01 的状态", errors)

    def test_results_entry_must_point_at_existing_action(self):
        self.edit("04-action-results.md", "｜A03｜待执行", "｜A07｜待执行")
        self.assertIn("不存在的 A07", self.errors())

    def test_broken_link_and_anchor(self):
        self.edit("00-start-here.md", "(03-action-plan.md#a01)", "(03-action-plan.md#a99)")
        self.edit("00-start-here.md", "(02-evidence-log.md#e07)", "(missing.md)")
        errors = self.errors()
        self.assertIn("锚点不存在", errors)
        self.assertIn("链接目标不存在", errors)

    def test_offline_run_needs_no_queries(self):
        path = self.copy / "02-evidence-log.md"
        import re
        path.write_text(re.sub(r"Q\d{2}", "查询", path.read_text(encoding="utf-8")), encoding="utf-8")
        self.assertIn("实际查询", self.errors())
        self.assertNotIn("实际查询", self.errors(offline=True))


if __name__ == "__main__":
    unittest.main()
