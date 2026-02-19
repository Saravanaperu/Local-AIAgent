import sys
import unittest
from unittest.mock import MagicMock

# 1. Mock google.ai.generativelanguage BEFORE importing agent.execution
mock_google = MagicMock()
mock_genai = MagicMock()
mock_generativelanguage = MagicMock()

class MockPart:
    def __init__(self, function_response=None, text=None, function_call=None):
        self.function_response = function_response
        self.text = text
        self.function_call = function_call

class MockFunctionResponse:
    def __init__(self, name, response):
        self.name = name
        self.response = response

class MockContent:
    def __init__(self, role=None, parts=None):
        self.role = role
        self.parts = parts

mock_generativelanguage.Part = MockPart
mock_generativelanguage.FunctionResponse = MockFunctionResponse
mock_generativelanguage.Content = MockContent

sys.modules["google"] = mock_google
sys.modules["google.ai"] = mock_genai
sys.modules["google.ai.generativelanguage"] = mock_generativelanguage

# 2. Mock agent.tools BEFORE importing agent.core
mock_tools = MagicMock()
mock_tools.search_code = MagicMock(return_value="def foo(): pass")
mock_tools.execute_tool = MagicMock(return_value="Tool Output")
sys.modules["agent.tools"] = mock_tools

# 3. Mock agent.agents BEFORE importing agent.core
mock_agents = MagicMock()
sys.modules["agent.agents"] = mock_agents

# Add project root to path
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

# 4. Import modules
# We want to test agent.core using the REAL agent.execution (but mocked google deps)
# So we do NOT mock agent.execution here.
from agent.core import run_agent

class TestCoreIntegration(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        mock_tools.execute_tool.reset_mock()
        mock_tools.search_code.reset_mock()

        # Setup mock agent response
        self.mock_agent_fn = MagicMock()
        mock_agents.create_agent.return_value = self.mock_agent_fn

    def test_run_agent_integration(self):
        # Scenario: Agent calls a tool, then provides final answer.

        # Response 1: Tool Call
        mock_response_1 = MagicMock()
        mock_fc = MagicMock()
        mock_fc.name = "my_tool"
        mock_fc.args = {"arg": "val"}
        mock_part_1 = MockPart(function_call=mock_fc)
        mock_response_1.parts = [mock_part_1]
        mock_response_1.candidates = [MagicMock(content="Tool Call Content")]

        # Response 2: Final Answer
        mock_response_2 = MagicMock()
        mock_part_2 = MockPart(text="Final Answer")
        mock_response_2.parts = [mock_part_2]
        mock_response_2.candidates = [MagicMock(content="Final Answer Content")]

        self.mock_agent_fn.side_effect = [mock_response_1, mock_response_2]

        # Run agent
        result = run_agent("test query")

        # Assertions
        self.assertEqual(result, "Final Answer")

        # Verify tool executed
        mock_tools.execute_tool.assert_called_with("my_tool", {"arg": "val"})

        # Verify create_agent called
        mock_agents.create_agent.assert_called_once()

        # Verify search_code called (initial search)
        mock_tools.search_code.assert_called_with("test query")

if __name__ == "__main__":
    unittest.main()
