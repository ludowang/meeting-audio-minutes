import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "deepseek_minutes.py"
SPEC = importlib.util.spec_from_file_location("deepseek_minutes", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MinutesPipelineTest(unittest.TestCase):
    def test_four_stage_pipeline_and_context_boundaries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            transcript = root / "transcript.md"
            outline = root / "outline.md"
            notes = root / "notes.md"
            minutes_md = root / "测试会议_会议纪要.md"
            minutes_docx = root / "测试会议_会议纪要.docx"
            transcript.write_text("逐字稿唯一内容：H1 实际八点二，H2 计划另行申请。", encoding="utf-8")
            outline.write_text("提纲唯一内容：预算与计划。", encoding="utf-8")
            notes.write_text("速记唯一内容：不要混淆实际与计划。", encoding="utf-8")

            calls = []
            responses = {
                "step1_extract": "# 有效信息清单\n\n### I001\n- 内容：H1 实际八点二\n",
                "step2_structure": "# 逻辑结构\n\n## 一、实际与计划\n- 必须保留：I001\n",
                "step3_draft": "# 会议纪要\n\n## 核心结论\n- 初稿\n",
                "step4_audit_repair": "# 会议纪要\n\n## 核心结论\n- H1 实际八点二；H2 仍是计划。\n",
            }

            def fake_call(stage, system_prompt, user_prompt, temperature):
                calls.append((stage, user_prompt))
                return responses[stage], {
                    "stage": stage,
                    "model": "test-model",
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15,
                }

            argv = [
                "deepseek_minutes.py",
                "--transcript", str(transcript),
                "--outline", str(outline),
                "--notes", str(notes),
                "--minutes-md", str(minutes_md),
                "--minutes-docx", str(minutes_docx),
                "--topic", "测试会议",
            ]
            with patch.object(MODULE, "call_deepseek", side_effect=fake_call), patch.object(sys, "argv", argv):
                self.assertEqual(MODULE.main(), 0)

            self.assertEqual([call[0] for call in calls], [
                "step1_extract", "step2_structure", "step3_draft", "step4_audit_repair"
            ])
            self.assertIn("逐字稿唯一内容", calls[0][1])
            self.assertIn("提纲唯一内容", calls[0][1])
            self.assertIn("速记唯一内容", calls[0][1])
            for _, prompt in calls[1:]:
                self.assertNotIn("逐字稿唯一内容", prompt)

            self.assertTrue((root / "测试会议_信息清单.md").exists())
            self.assertTrue((root / "测试会议_逻辑结构.md").exists())
            self.assertTrue((root / "测试会议_纪要初稿.md").exists())
            self.assertTrue(minutes_md.exists())
            self.assertTrue(minutes_docx.exists())
            usage = json.loads((root / "测试会议_模型用量.json").read_text(encoding="utf-8"))
            self.assertEqual(usage["total"]["total_tokens"], 60)
            self.assertIn("H2 仍是计划", minutes_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
