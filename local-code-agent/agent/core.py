import os
import google.generativeai as genai
from google.ai.generativelanguage import FunctionDeclaration, Tool, Schema, Type, Part, FunctionResponse, Content
import config
from agent.tools import TOOL_FUNCTIONS, execute_tool, search_code
from agent.tool_schemas import TOOL_SCHEMAS
from agent.execution import execute_agent_loop

def get_tool_schemas():
    return [Tool(function_declarations=[
        TOOL_SCHEMAS["search_code"],
        TOOL_SCHEMAS["read_file"],
        TOOL_SCHEMAS["write_file"],
        TOOL_SCHEMAS["run_command"],
        TOOL_SCHEMAS["list_directory"],
        TOOL_SCHEMAS["get_code_structure"],
        TOOL_SCHEMAS["ask_user"]
    ])]

def get_model():
    if not config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set. Please set it as an environment variable.")

    genai.configure(api_key=config.GEMINI_API_KEY)

    model = genai.GenerativeModel(
        model_name=config.GEMINI_MODEL,
        tools=get_tool_schemas()
    )
    return model

def call_gemini_with_history(history):
    model = get_model()

    if not history:
        return None

    past_history = history[:-1]
    current_message = history[-1]

    chat = model.start_chat(history=past_history)

    # Check if current_message is a dict or Content object
    if isinstance(current_message, dict):
        parts = current_message['parts']
    else:
        parts = current_message.parts

    response = chat.send_message(parts)
    return response

def run_agent(user_query):
    # System prompt
    system_prompt = """You are an AI assistant that helps developers with their local codebase.
You have access to the following tools: search_code, read_file, write_file, run_command, list_directory, get_code_structure, ask_user.
Always think step by step. Use tools to gather information. When you have enough information, provide a final answer.
"""

    history = [
        {"role": "user", "parts": [system_prompt]}
    ]

    # Initial search
    print(f"Agent: Searching code for context...")
    try:
        context = search_code(user_query)
        if context:
            history.append({"role": "user", "parts": [f"Context found from codebase:\n{context}"]})
    except Exception as e:
        print(f"Initial search failed: {e}")

    # Add user query
    history.append({"role": "user", "parts": [user_query]})

    return execute_agent_loop(
        call_gemini_with_history,
        history,
        execute_tool,
        max_iterations=10,
        log_func=print
    )
