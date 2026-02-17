from google.ai.generativelanguage import FunctionDeclaration, Schema, Type, Tool

search_code_schema = FunctionDeclaration(
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

read_file_schema = FunctionDeclaration(
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

write_file_schema = FunctionDeclaration(
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

run_command_schema = FunctionDeclaration(
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

list_directory_schema = FunctionDeclaration(
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

get_code_structure_schema = FunctionDeclaration(
    name="get_code_structure",
    description="Get a tree-like view of the project structure.",
    parameters=Schema(
        type=Type.OBJECT,
        properties={},
    )
)

ask_user_schema = FunctionDeclaration(
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

ask_orchestrator_schema = FunctionDeclaration(
    name="ask_orchestrator",
    description="Request the orchestrator to perform an action (e.g., search, read file) and return the result.",
    parameters=Schema(
        type=Type.OBJECT,
        properties={
            "action": Schema(
                type=Type.STRING,
                description="The action to perform (e.g., search, read_file, list_dir, get_state, run_test, etc.)."
            ),
            "query": Schema(type=Type.STRING, description="The query for search action."),
            "path": Schema(type=Type.STRING, description="The path for read_file or list_dir action."),
            "command": Schema(type=Type.STRING, description="The command for run_test action (optional, usually inferred).")
        },
        required=["action"]
    )
)

TOOL_SCHEMAS = {
    "search_code": search_code_schema,
    "read_file": read_file_schema,
    "write_file": write_file_schema,
    "run_command": run_command_schema,
    "list_directory": list_directory_schema,
    "get_code_structure": get_code_structure_schema,
    "ask_user": ask_user_schema,
    "ask_orchestrator": ask_orchestrator_schema
}
