from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import json
import tempfile
import unittest

from hmode.cli import cmd_add, cmd_export, cmd_import, cmd_init, cmd_list, cmd_set, cmd_session, cmd_status, cmd_template_add


class HModeTests(unittest.TestCase):
    def test_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            source = Path(tmp) / "import.json"

            self.assertEqual(cmd_init(path), 0)
            self.assertEqual(cmd_add("fast", "gpt-4.1-mini", path), 0)
            self.assertEqual(cmd_add("best", "claude-opus-4", path), 0)
            self.assertEqual(cmd_set("best", path), 0)
            self.assertEqual(cmd_template_add("review", "Give me a concise review.", path), 0)
            self.assertEqual(cmd_session("Swapped to best", path), 0)

            buf = StringIO()
            with redirect_stdout(buf):
                self.assertEqual(cmd_list(path, show_templates=True), 0)
            out = buf.getvalue()
            self.assertIn("fast", out)
            self.assertIn("best", out)
            self.assertIn("review", out)

            buf = StringIO()
            with redirect_stdout(buf):
                self.assertEqual(cmd_status(path), 0)
            self.assertIn("best: claude-opus-4", buf.getvalue())

            buf = StringIO()
            with redirect_stdout(buf):
                self.assertEqual(cmd_export(path), 0)
            data = json.loads(buf.getvalue())
            self.assertEqual(data["active"], "best")

            source.write_text(json.dumps(data))
            imported = Path(tmp) / "imported.json"
            self.assertEqual(cmd_import(source, imported), 0)
            buf = StringIO()
            with redirect_stdout(buf):
                self.assertEqual(cmd_status(imported), 0)
            self.assertIn("best: claude-opus-4", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
