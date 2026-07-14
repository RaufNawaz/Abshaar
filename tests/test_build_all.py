from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class BuildAllWrapperTest(unittest.TestCase):
    def test_build_wrappers_include_placeholder_entries(self) -> None:
        expected_commands = {
            "scripts/build_all.sh": "invoke_abshaar build-data --include-placeholders",
            "scripts/build_all.ps1": "Invoke-Abshaar build-data --include-placeholders",
        }

        for relative_path, expected_command in expected_commands.items():
            with self.subTest(wrapper=relative_path):
                wrapper = (REPO_ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIn(expected_command, wrapper)


if __name__ == "__main__":
    unittest.main()
