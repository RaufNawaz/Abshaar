from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from abshaar.status import next_poem_id


class StatusTest(unittest.TestCase):
    def test_next_poem_id_from_working_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            working = root / "data" / "working"
            working.mkdir(parents=True)
            (working / "bulleh_shah_0001.md").write_text("", encoding="utf-8")
            (working / "bulleh_shah_0003.md").write_text("", encoding="utf-8")

            self.assertEqual(next_poem_id(root, "bulleh_shah"), "bulleh_shah_0004")


if __name__ == "__main__":
    unittest.main()
