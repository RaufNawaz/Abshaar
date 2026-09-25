"""The routing invariant: an `mlx:` model must never reach Ollama, and a plain
model name must never reach mlx-lm.

Getting this wrong is silent and expensive -- `run-eval --model mlx:run2` would
cheerfully grade Ollama's qwen3:8b and write the score into eval_baseline.md as
if it were the tuned model's, which is the kind of wrong number that survives
for weeks.
"""

from __future__ import annotations

import json
import unittest
from unittest import mock

from abshaar import mlx_client


class MlxPrefixTests(unittest.TestCase):
    def test_prefix_detection(self):
        self.assertTrue(mlx_client.is_mlx_model("mlx:run2"))
        self.assertTrue(mlx_client.is_mlx_model("mlx:"))
        self.assertFalse(mlx_client.is_mlx_model("qwen3:8b"))
        self.assertFalse(mlx_client.is_mlx_model("qwen3:4b"))


class RoutingTests(unittest.TestCase):
    def test_mlx_model_goes_to_mlx_and_not_ollama(self):
        with mock.patch.object(mlx_client, "run_mlx_chat", return_value="A") as to_mlx, \
             mock.patch("abshaar.ollama_client.run_ollama_chat", return_value="B") as to_ollama:
            self.assertEqual(mlx_client.run_chat("mlx:run2", "sys", "user"), "A")
        to_mlx.assert_called_once_with("mlx:run2", "sys", "user")
        to_ollama.assert_not_called()

    def test_plain_model_goes_to_ollama_and_not_mlx(self):
        with mock.patch.object(mlx_client, "run_mlx_chat", return_value="A") as to_mlx, \
             mock.patch("abshaar.ollama_client.run_ollama_chat", return_value="B") as to_ollama:
            self.assertEqual(mlx_client.run_chat("qwen3:8b", "sys", "user"), "B")
        to_ollama.assert_called_once_with("qwen3:8b", "sys", "user")
        to_mlx.assert_not_called()


class PayloadTests(unittest.TestCase):
    def test_payload_strips_the_prefix_and_mirrors_ollama_sampling(self):
        seen = {}

        class FakeResponse:
            def read(self_inner):
                return b'{"choices":[{"message":{"content":"ok"}}]}'

            def __enter__(self_inner):
                return self_inner

            def __exit__(self_inner, *a):
                return False

        def fake_urlopen(request, timeout=None):
            seen["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse()

        with mock.patch.object(mlx_client.urllib.request, "urlopen", fake_urlopen):
            self.assertEqual(mlx_client.run_mlx_chat("mlx:run2", "sys", "user"), "ok")

        # the server gets a clean name, not the routing prefix
        self.assertEqual(seen["body"]["model"], "run2")
        self.assertEqual(seen["body"]["messages"][0]["role"], "system")
        # same sampling as run_ollama_chat, so tuned-vs-base is like for like
        self.assertEqual(seen["body"]["temperature"], 0.3)
        self.assertEqual(seen["body"]["top_p"], 0.9)


if __name__ == "__main__":
    unittest.main()
