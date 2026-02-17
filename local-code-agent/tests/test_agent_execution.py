import sys
import unittest
from unittest.mock import MagicMock

# Mock google.ai.generativelanguage before importing agent.execution
mock_google = MagicMock()
mock_genai = MagicMock()
mock_generativelanguage = MagicMock()

# Mock Part and FunctionResponse
class MockPart:
    def __init__(self, function_response=None, text=None, function_call=None):
        self.function_response = function_response
        self.text = text
        self.function_call = function_call

class MockFunctionResponse:
    def __init__(self, name, response):
        self.name = name
        self.response = response

mock_generativelanguage.Part = MockPart
mock_generativelanguage.FunctionResponse = MockFunctionResponse

sys.modules["google"] = mock_google
sys.modules["google.ai"] = mock_genai
sys.modules["google.ai.generativelanguage"] = mock_generativelanguage

# Add local-code-agent to path
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

from agent.execution import execute_agent_loop

class TestExecuteAgentLoop(unittest.TestCase):
    def setUp(self):
        self.history = []
        self.mock_response_fn = MagicMock()
        self.mock_tool_executor = MagicMock()

    def test_text_response(self):
        # Setup mock response
        mock_response = MagicMock()
        mock_part = MockPart(text="Hello world")
        mock_response.parts = [mock_part]
        mock_response.candidates = [MagicMock(content="Hello world content")]
        self.mock_response_fn.return_value = mock_response

        result = execute_agent_loop(
            self.mock_response_fn,
            self.history,
            self.mock_tool_executor,
            max_iterations=1
        )

        self.assertEqual(result, "Hello world")
        self.assertEqual(len(self.history), 1)
        self.assertEqual(self.history[0], "Hello world content")

    def test_tool_call_then_text(self):
        # Iteration 1: Tool call
        mock_response_1 = MagicMock()
        mock_fc = MagicMock()
        mock_fc.name = "my_tool"
        mock_fc.args = {"arg": "val"}
        mock_part_1 = MockPart(function_call=mock_fc)
        mock_response_1.parts = [mock_part_1]
        mock_response_1.candidates = [MagicMock(content="Tool Call Content")]

        # Iteration 2: Final text
        mock_response_2 = MagicMock()
        mock_part_2 = MockPart(text="Final Answer")
        mock_response_2.parts = [mock_part_2]
        mock_response_2.candidates = [MagicMock(content="Final Answer Content")]

        self.mock_response_fn.side_effect = [mock_response_1, mock_response_2]
        self.mock_tool_executor.return_value = "Tool Output"

        result = execute_agent_loop(
            self.mock_response_fn,
            self.history,
            self.mock_tool_executor,
            max_iterations=5
        )

        self.assertEqual(result, "Final Answer")
        self.mock_tool_executor.assert_called_with("my_tool", {"arg": "val"})

        # Check history
        # 1. Tool Call Content
        # 2. Tool Response (FunctionResponse)
        # 3. Final Answer Content
        self.assertEqual(len(self.history), 3)
        self.assertEqual(self.history[0], "Tool Call Content")
        self.assertEqual(self.history[1]["role"], "function")
        self.assertIsInstance(self.history[1]["parts"][0], MockPart)
        self.assertEqual(self.history[1]["parts"][0].function_response.name, "my_tool")
        self.assertEqual(self.history[1]["parts"][0].function_response.response, {"result": "Tool Output"})
        self.assertEqual(self.history[2], "Final Answer Content")

    def test_max_iterations(self):
        # Always return tool call
        mock_response = MagicMock()
        mock_fc = MagicMock()
        mock_fc.name = "my_tool"
        mock_fc.args = {}
        mock_part = MockPart(function_call=mock_fc)
        mock_response.parts = [mock_part]
        mock_response.candidates = [MagicMock(content="Tool Call")]

        self.mock_response_fn.return_value = mock_response
        self.mock_tool_executor.return_value = "Result"

        result = execute_agent_loop(
            self.mock_response_fn,
            self.history,
            self.mock_tool_executor,
            max_iterations=3
        )

        self.assertEqual(result, "Agent: Maximum iterations reached without final answer.")
        self.assertEqual(self.mock_response_fn.call_count, 3)

    def test_exception_in_response(self):
        self.mock_response_fn.side_effect = Exception("API Error")

        result = execute_agent_loop(
            self.mock_response_fn,
            self.history,
            self.mock_tool_executor
        )

        self.assertTrue("Error calling agent: API Error" in result)

if __name__ == "__main__":
    unittest.main()
