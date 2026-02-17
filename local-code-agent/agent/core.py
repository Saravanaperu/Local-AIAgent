import os
import google.generativeai as genai
from google.ai.generativelanguage import FunctionDeclaration, Tool, Schema, Type, Part, FunctionResponse, Content
import config
from agent.tools import TOOL_FUNCTIONS, execute_tool, search_code

def get_tool_schemas():
    search_code_func = FunctionDeclaration(
        name="search_code",
        description="Search the codebase for relevant code snippets using semantic search.",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "query": Schema(type=Type.STRING, description="The natural language search query.")
            },
            required=["query"]
        )
    )

    read_file_func = FunctionDeclaration(
        name="read_file",
        description="Read the content of a file.",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "path": Schema(type=Type.STRING, description="The path to the file to read.")
            },
            required=["path"]
        )
    )

    write_file_func = FunctionDeclaration(
        name="write_file",
        description="Write content to a file. Overwrites if exists (creates backup).",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "path": Schema(type=Type.STRING, description="The path to the file to write."),
                "content": Schema(type=Type.STRING, description="The content to write.")
            },
            required=["path", "content"]
        )
    )

    run_command_func = FunctionDeclaration(
        name="run_command",
        description="Run a shell command (whitelisted: pytest, git, python, npm, node, make).",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "command": Schema(type=Type.STRING, description="The command to run.")
            },
            required=["command"]
        )
    )

    list_directory_func = FunctionDeclaration(
        name="list_directory",
        description="List files and directories in a given path.",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "path": Schema(type=Type.STRING, description="The directory path to list.")
            },
            required=["path"]
        )
    )

    get_code_structure_func = FunctionDeclaration(
        name="get_code_structure",
        description="Get a tree-like view of the project structure.",
        parameters=Schema(
            type=Type.OBJECT,
            properties={},
        )
    )

    ask_user_func = FunctionDeclaration(
        name="ask_user",
        description="Ask the user for input or clarification.",
        parameters=Schema(
            type=Type.OBJECT,
            properties={
                "question": Schema(type=Type.STRING, description="The question to ask the user.")
            },
            required=["question"]
        )
    )

    return [Tool(function_declarations=[
        search_code_func,
        read_file_func,
        write_file_func,
        run_command_func,
        list_directory_func,
        get_code_structure_func,
        ask_user_func
    ])]

def get_model():
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        print("Warning: GEMINI_API_KEY is not set. Please set it in config.py or environment variables.")

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

    max_iterations = 10

    for i in range(max_iterations):
        print(f"Iteration {i+1}/{max_iterations}")
        try:
            response = call_gemini_with_history(history)
        except Exception as e:
            return f"Error calling Gemini: {e}"

        # Check for function calls
        # response.parts is a list of Part objects.
        if not response.parts:
            return "Error: Empty response from Gemini."

        part = response.parts[0]

        # Check if function call
        if hasattr(part, 'function_call') and part.function_call:
            fc = part.function_call
            tool_name = fc.name
            tool_args = dict(fc.args)

            print(f"Agent: Calling tool {tool_name} with args {tool_args}")

            # Append model's tool call to history
            # Use the Content object from response
            history.append(response.candidates[0].content)

            # Execute tool
            result = execute_tool(tool_name, tool_args)
            print(f"Tool Result: {result[:200]}..." if len(result) > 200 else f"Tool Result: {result}")

            # Append tool response to history
            func_response_part = Part(
                function_response=FunctionResponse(
                    name=tool_name,
                    response={"result": result}
                )
            )

            # Use Content object for consistency if possible, or dict
            # 'function' role is standard for tool outputs in this SDK context?
            # Actually SDK often uses 'function' role.
            history.append({"role": "function", "parts": [func_response_part]})

        elif hasattr(part, 'text') and part.text:
            # Final answer
            history.append(response.candidates[0].content)
            return part.text
        else:
            # Fallback for text if part.text is missing but it's text
             try:
                text = response.text
                history.append(response.candidates[0].content)
                return text
             except:
                return "Error: Unexpected response format."

    return "Agent: Maximum iterations reached without final answer."
