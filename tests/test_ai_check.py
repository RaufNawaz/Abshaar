"""ai-check must import each optional package, not merely locate it.

On 2026-08-31 `torch` was installed but raised on import. find_spec found the
files, ai-check reported the RAG stack healthy, and the real breakage surfaced
only when build-index was attempted. The repair was equally invisible: when the
venv started working again, find_spec had no way to say so, and the RAG half of
the pipeline stayed parked on a blocker that had already gone.
"""

from __future__ import annotations

import unittest
from unittest import mock

from abshaar import ollama_client


class AiCheckImportTests(unittest.TestCase):
    def test_package_that_is_present_but_unimportable_is_reported_broken(self):
        def boom(name):
            if name == "torch":
                raise ImportError("cannot import name 'fetch' from partially initialized module")
            return mock.Mock()

        with mock.patch.object(ollama_client.importlib.util, "find_spec", return_value=object()), \
             mock.patch.object(ollama_client.importlib, "import_module", side_effect=boom), \
             mock.patch.object(ollama_client.shutil, "which", return_value=None), \
             mock.patch.object(ollama_client.urllib.request, "urlopen", side_effect=OSError):
            status = ollama_client.check_ollama()

        self.assertFalse(status["optional_packages"]["torch"])
        self.assertIn("torch", status.get("import_errors", {}))
        self.assertIn("ImportError", status["import_errors"]["torch"])
        # the others imported fine and must not be dragged down with it
        self.assertTrue(status["optional_packages"]["chromadb"])

    def test_importable_packages_are_reported_installed(self):
        with mock.patch.object(ollama_client.importlib.util, "find_spec", return_value=object()), \
             mock.patch.object(ollama_client.importlib, "import_module", return_value=mock.Mock()), \
             mock.patch.object(ollama_client.shutil, "which", return_value=None), \
             mock.patch.object(ollama_client.urllib.request, "urlopen", side_effect=OSError):
            status = ollama_client.check_ollama()

        self.assertTrue(all(status["optional_packages"].values()))
        self.assertEqual(status.get("import_errors", {}), {})

    def test_absent_package_is_missing_not_an_import_error(self):
        with mock.patch.object(ollama_client.importlib.util, "find_spec", return_value=None), \
             mock.patch.object(ollama_client.shutil, "which", return_value=None), \
             mock.patch.object(ollama_client.urllib.request, "urlopen", side_effect=OSError):
            status = ollama_client.check_ollama()

        self.assertFalse(any(status["optional_packages"].values()))
        self.assertEqual(status.get("import_errors", {}), {})


if __name__ == "__main__":
    unittest.main()
