import sys
from unittest.mock import MagicMock
import unittest

# Mock google
sys.modules["google"] = MagicMock()
sys.modules["google.generativeai"] = MagicMock()
sys.modules["google.ai"] = MagicMock()
sys.modules["google.ai.generativelanguage"] = MagicMock()

import os
# Set dummy API key for testing
os.environ["GEMINI_API_KEY"] = "fake_key_for_test"

# Add local-code-agent to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

# Mock config
import config
config.GEMINI_API_KEY = "fake_key"
config.GEMINI_MODEL = "gemini-pro"

# Mock tools
sys.modules["agent.tools"] = MagicMock()
sys.modules["agent.tools"].search_code = MagicMock(return_value="def foo(): pass")
sys.modules["agent.tools"].execute_tool = MagicMock()

# Mock execution
sys.modules["agent.execution"] = MagicMock()
mock_execute_loop = MagicMock(return_value="Agent Result")
sys.modules["agent.execution"].execute_agent_loop = mock_execute_loop

# Mock agent.agents
sys.modules["agent.agents"] = MagicMock()
mock_agent_instance = MagicMock(return_value="Model Response")
sys.modules["agent.agents"].create_agent = MagicMock(return_value=mock_agent_instance)

from agent.core import run_agent

class TestCore(unittest.TestCase):
    def test_run_agent(self):
        result = run_agent("test query")
        self.assertEqual(result, "Agent Result")

        # Verify execute_agent_loop called
        mock_execute_loop.assert_called_once()
        args, kwargs = mock_execute_loop.call_args

        get_response_fn = args[0]
        history = args[1]

        # Verify history initialized with context
        self.assertEqual(len(history), 1)
        self.assertIn("Context found", history[0]["parts"][0])

        # Verify get_response_fn calls agent instance with user_query and history
        get_response_fn(history)
        mock_agent_instance.assert_called_with("test query", history)

if __name__ == "__main__":
    unittest.main()
