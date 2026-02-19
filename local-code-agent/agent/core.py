import config
from agent.tools import execute_tool, search_code
from agent.execution import execute_agent_loop
from agent.agents import create_agent

"""
This module contains the single-agent implementation.
It uses the shared `create_agent` utility and delegates execution to `execute_agent_loop`.
"""

# Define constants for clarity and maintainability
SYSTEM_PROMPT = """You are an AI assistant that helps developers with their local codebase.
You have access to the following tools: search_code, read_file, write_file, run_command, list_directory, get_code_structure, ask_user.
Always think step by step. Use tools to gather information. When you have enough information, provide a final answer.
"""

TOOL_NAMES = [
    "search_code",
    "read_file",
    "write_file",
    "run_command",
    "list_directory",
    "get_code_structure",
    "ask_user"
]

def run_agent(user_query):
    """
    Runs the single-agent loop.
    """
    # Create the agent function
    agent = create_agent(SYSTEM_PROMPT, TOOL_NAMES)

    history = []

    # Initial search to provide context
    print(f"Agent: Searching code for context...")
    try:
        context = search_code(user_query)
        if context:
            history.append({"role": "user", "parts": [f"Context found from codebase:\n{context}"]})
    except Exception as e:
        print(f"Initial search failed: {e}")

    # We do NOT append user_query to history here, because agent_fn appends it at the end of every prompt.
    # This acts as a reminder of the task.

    def get_response_fn(hist):
        # Calls the agent which interacts with Gemini
        return agent(user_query, hist)

    # Delegate the execution loop to the shared utility
    # This replaces any manual loop implementation that might have existed previously.
    return execute_agent_loop(
        get_response_fn,
        history,
        execute_tool,
        max_iterations=10,
        log_func=print
    )
