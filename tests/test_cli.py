from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from hmode.cli import cmd_add, cmd_init, cmd_list, cmd_set, cmd_status


class HModeTests(unittest.TestCase):
    def test_init_add_set_list_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"

            self.assertEqual(cmd_init(path), 0)
            self.assertTrue(path.exists())

            self.assertEqual(cmd_add("fast", "gpt-4.1-mini", path), 0)
            self.assertEqual(cmd_add("best", "claude-opus-4", path), 0)
            self.assertEqual(cmd_set("best", path), 0)

            buf = StringIO()
            with redirect_stdout(buf):
                self.assertEqual(cmd_list(path), 0)
            out = buf.getvalue()
            self.assertIn("fast", out)
            self.assertIn("best", out)

            buf = StringIO()
            with redirect_stdout(buf):
                self.assertEqual(cmd_status(path), 0)
            out = buf.getvalue()
            self.assertIn("best: claude-opus-4", out)


if __name__ == "__main__":
    unittest.main()
