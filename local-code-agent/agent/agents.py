from agent.tool_schemas import TOOL_SCHEMAS
import config
import google.generativeai as genai
from google.ai.generativelanguage import Tool

def create_agent(system_prompt, tool_names):
    """
    Returns a function that can be called with a user message and conversation history.
    This function will invoke Gemini with the appropriate tools.
    """
    # Create the tool list from schemas
    tool_declarations = [TOOL_SCHEMAS[name] for name in tool_names if name in TOOL_SCHEMAS]

    # Only create tools object if there are declarations
    tools = [Tool(function_declarations=tool_declarations)] if tool_declarations else None

    genai.configure(api_key=config.GEMINI_API_KEY)

    model = genai.GenerativeModel(model_name=config.GEMINI_MODEL, tools=tools)

    def agent_fn(user_input, history=None):
        if history is None:
            history = []

        # Combine system prompt as a user message (since Gemini has no system role)
        # We assume history contains the previous turn's messages
        messages = [{"role": "user", "parts": [system_prompt]}] + history + [{"role": "user", "parts": [user_input]}]

        try:
            response = model.generate_content(messages)
            return response
        except Exception as e:
            print(f"Error in agent generation: {e}")
            raise e

    return agent_fn

# Define agents

code_reader = create_agent(
    "You are a Code Reader. Your job is to understand and explain the existing codebase. "
    "You have tools to search, read files, and list directories. "
    "Do not modify any files. Provide clear explanations based on the code.",
    ["search_code", "read_file", "list_directory", "get_code_structure", "ask_orchestrator"]
)

code_writer = create_agent(
    "You are a Code Writer. Your job is to modify the codebase. "
    "You can write files, and run commands (like linters or formatters). "
    "Always ask for user confirmation before writing files. "
    "You can also ask the orchestrator to read files or search code if you need more context.",
    ["write_file", "run_command", "ask_user", "ask_orchestrator"]
)

tester = create_agent(
    "You are a Tester. Your job is to run tests and report results. "
    "You can run test commands. Do not modify code. "
    "If you need to know what tests exist, you can list directories or ask the orchestrator.",
    ["run_command", "list_directory", "ask_orchestrator"]
)

debugger = create_agent(
    "You are a Debugger. You analyse error messages and test failures, "
    "and suggest fixes. You can call the Code Writer to apply fixes via the orchestrator. "
    "You can ask the orchestrator to read files or run tests.",
    ["ask_orchestrator", "read_file"]
)

planner = create_agent(
    "You are a Planner. Given a user request, break it down into a sequence of subtasks that can be handled by specialised agents. "
    "Available agents: reader (understands code), writer (modifies code), tester (runs tests), debugger (fixes errors). "
    "Output a JSON list of objects, each with 'agent' and 'task' fields. "
    "Example: [{'agent': 'reader', 'task': '...'}, {'agent': 'writer', 'task': '...'}]",
    []
)
