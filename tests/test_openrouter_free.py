import os
import runpy
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import Mock, patch


class OpenRouterTests(unittest.TestCase):
    def run_script(self, responses):
        output = StringIO()
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}), \
                patch("requests.post", side_effect=responses) as post, \
                redirect_stdout(output), redirect_stderr(output):
            try:
                runpy.run_path("ai_providers/openrouter_free_chat.py", run_name="__main__")
            except SystemExit as exc:
                self.assertEqual(exc.code, 1)
        return output.getvalue(), post

    def test_api_error_reports_message(self):
        response = Mock(status_code=401, ok=False)
        response.json.return_value = {"error": {"message": "Invalid API key"}}
        output, post = self.run_script([response])
        self.assertIn("Invalid API key", output)
        self.assertEqual(post.call_count, 1)

    def test_follow_up_is_authenticated_and_preserves_reasoning(self):
        first = Mock(status_code=200, ok=True)
        first.json.return_value = {"choices": [{"message": {"role": "assistant", "content": "Three", "reasoning_details": [{"type": "reasoning.text", "text": "count"}]}}]}
        second = Mock(status_code=200, ok=True)
        second.json.return_value = {"choices": [{"message": {"role": "assistant", "content": "Yes, three."}}]}
        output, post = self.run_script([first, second])
        self.assertIn("Yes, three.", output)
        self.assertEqual(post.call_count, 2)
        self.assertEqual(post.call_args.kwargs["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(post.call_args.kwargs["json"]["messages"][1]["reasoning_details"], first.json.return_value["choices"][0]["message"]["reasoning_details"])


if __name__ == "__main__":
    unittest.main()