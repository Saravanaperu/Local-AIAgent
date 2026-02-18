import os
import subprocess
import shutil
import datetime
from agent import indexer, utils

ALLOWED_COMMANDS = ["pytest", "git", "python", "npm", "node", "make"]

def search_code(query: str) -> str:
    try:
        return indexer.search_code(query)
    except Exception as e:
        return f"Error searching code: {e}"

def read_file(path: str) -> str:
    if not utils.is_path_safe(path):
        return f"Error: Path {path} is unsafe or outside project root."

    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File {path} not found."
    except Exception as e:
        return f"Error reading file {path}: {e}"

def write_file(path: str, content: str) -> str:
    if not utils.is_path_safe(path):
        return f"Error: Path {path} is unsafe or outside project root."

    # Preview content for user confirmation
    preview_lines = content.splitlines()[:10]
    preview = "\n".join(preview_lines)
    if len(content.splitlines()) > 10:
        preview += "\n... (truncated)"

    print(f"\n[CONFIRMATION REQUIRED] Agent wants to write to file: {path}")
    print("--- CONTENT PREVIEW ---")
    print(preview)
    print("-----------------------")

    confirm = input("Proceed with writing file? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        return "Action cancelled by user."

    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        # Create backup if file exists
        if os.path.exists(path):
            backup_dir = os.path.join(utils.get_project_root(), ".backups")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = os.path.basename(path)
            backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}")
            shutil.copy2(path, backup_path)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file {path}: {e}"

def run_command(command: str) -> str:
    parts = command.split()
    if not parts:
        return "Error: Empty command."

    exe = parts[0]
    if exe not in ALLOWED_COMMANDS:
        return f"Error: Command '{exe}' is not allowed. Allowed: {ALLOWED_COMMANDS}"

    print(f"\n[CONFIRMATION REQUIRED] Agent wants to run command:")
    print(f"Command: {command}")

    confirm = input("Proceed with execution? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        return "Command cancelled by user."

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=utils.get_project_root(),
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += "\nSTDERR:\n" + result.stderr
        return output
    except subprocess.TimeoutExpired:
        return "Error: Command timed out."
    except Exception as e:
        return f"Error running command: {e}"

def list_directory(path: str) -> str:
    if not utils.is_path_safe(path):
        return f"Error: Path {path} is unsafe."

    try:
        items = os.listdir(path)
        # Separate dirs and files
        dirs = [d + "/" for d in items if os.path.isdir(os.path.join(path, d))]
        files = [f for f in items if os.path.isfile(os.path.join(path, f))]
        return "\n".join(sorted(dirs + files))
    except Exception as e:
        return f"Error listing directory {path}: {e}"

def get_code_structure() -> str:
    root = utils.get_project_root()
    output = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Filter hidden dirs
        dirnames[:] = [d for d in dirnames if not d.startswith('.') and d not in ['venv', '__pycache__', 'chroma_db', 'site-packages']]

        rel_path = os.path.relpath(dirpath, root)
        if rel_path == ".":
            output.append(f"{os.path.basename(root)}/")
        else:
            indent = "  " * rel_path.count(os.sep)
            output.append(f"{indent}{os.path.basename(dirpath)}/")

        indent = "  " * (rel_path.count(os.sep) + 1)
        for f in filenames:
            if f.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.h', '.c', '.md', '.txt')):
                output.append(f"{indent}{f}")

    return "\n".join(output)

def ask_user(question: str) -> str:
    print(f"Agent asks: {question}")
    return input("Your answer: ")

def ask_orchestrator(action: str, **kwargs) -> str:
    """
    Ask the orchestrator for something. This tool should be intercepted by the orchestrator.
    The request should be a JSON string with fields 'action' and other parameters.
    """
    # This function will never be called directly; it's just a placeholder.
    # The orchestrator will detect its name and handle it.
    return "Error: This tool is only available when running under the Orchestrator."

TOOL_FUNCTIONS = {
    "search_code": search_code,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
    "list_directory": list_directory,
    "get_code_structure": get_code_structure,
    "ask_user": ask_user,
    "ask_orchestrator": ask_orchestrator
}

def execute_tool(name: str, args: dict) -> str:
    if name not in TOOL_FUNCTIONS:
        return f"Error: Tool {name} not found."

    func = TOOL_FUNCTIONS[name]
    try:
        return func(**args)
    except TypeError as e:
        return f"Error executing tool {name}: {e}"
    except Exception as e:
        return f"Error executing tool {name}: {e}"
