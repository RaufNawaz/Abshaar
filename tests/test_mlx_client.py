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
            # a caller-chosen timeout must survive the hop, or the judge's
            # longer budget silently reverts to 180s
            mlx_client.run_chat("mlx:run2", "sys", "user", timeout=600)
        self.assertEqual(to_mlx.call_args_list[-1].kwargs["timeout"], 600)
        self.assertEqual(to_mlx.call_args_list[0], mock.call("mlx:run2", "sys", "user", timeout=180))
        to_ollama.assert_not_called()

    def test_plain_model_goes_to_ollama_and_not_mlx(self):
        with mock.patch.object(mlx_client, "run_mlx_chat", return_value="A") as to_mlx, \
             mock.patch("abshaar.ollama_client.run_ollama_chat", return_value="B") as to_ollama:
            self.assertEqual(mlx_client.run_chat("qwen3:8b", "sys", "user"), "B")
        to_ollama.assert_called_once_with("qwen3:8b", "sys", "user", timeout=180)
        to_mlx.assert_not_called()


class PayloadTests(unittest.TestCase):
    def test_payload_names_a_real_model_and_mirrors_ollama_sampling(self):
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

        # The server RESOLVES this field as a model path and loads it -- it
        # does not serve whatever it was started with. Sending the run label
        # made it request huggingface.co/api/models/run2 and 404, which is how
        # a tuned eval "answered" 50 probes in 20 minutes and scored 0.0.
        self.assertEqual(seen["body"]["model"], mlx_client.DEFAULT_MLX_MODEL)
        self.assertNotEqual(seen["body"]["model"], "run2")
        self.assertIn("/", seen["body"]["model"], "must be a model path, not a label")
        self.assertEqual(seen["body"]["messages"][0]["role"], "system")
        # same sampling as run_ollama_chat, so tuned-vs-base is like for like
        self.assertEqual(seen["body"]["temperature"], 0.3)
        self.assertEqual(seen["body"]["top_p"], 0.9)


if __name__ == "__main__":
    unittest.main()


class SpecialTokenTests(unittest.TestCase):
    """mlx returns the chat template's end markers; Ollama does not.

    Left in, they reach the judge and the token-F1 scorer as extra tokens, so
    the tuned and base runs would not be scored on equal terms -- and the
    comparison between them is the entire point.
    """

    def test_end_markers_are_stripped(self):
        self.assertEqual(
            mlx_client._strip_special_tokens("An answer.<|im_end|>"), "An answer."
        )
        self.assertEqual(
            mlx_client._strip_special_tokens("<|im_start|>hi<|endoftext|>"), "hi"
        )

    def test_ordinary_text_is_untouched(self):
        text = "Bulleh Shah was a Punjabi Sufi poet [kb:bio_claim_bulleh_name]."
        self.assertEqual(mlx_client._strip_special_tokens(text), text)

    def test_stripping_happens_on_the_response_path(self):
        class FakeResponse:
            def read(self_inner):
                return b'{"choices":[{"message":{"content":"graded<|im_end|>"}}]}'

            def __enter__(self_inner):
                return self_inner

            def __exit__(self_inner, *a):
                return False

        with mock.patch.object(
            mlx_client.urllib.request, "urlopen", lambda r, timeout=None: FakeResponse()
        ):
            self.assertEqual(mlx_client.run_mlx_chat("mlx:run2", "s", "u"), "graded")
