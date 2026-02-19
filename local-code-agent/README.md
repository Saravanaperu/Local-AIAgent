# Local Code Agent

A custom AI agent that can understand, query, and modify your local codebase using Google's Gemini models.

## Features

- **Code Indexing**: Parses and indexes your code (Python, JS, TS, Java, C++, C, etc.) using Tree-sitter and ChromaDB for semantic search.
- **Smart Tools**: Can search code, read/write files, list directories, and run shell commands.
- **Safety First**: Asks for confirmation before modifying files or running commands. Creates backups before writing.
- **ReAct Loop**: Uses Gemini to reason step-by-step and solve complex tasks.

## Prerequisites

- Python 3.9+
- Google Gemini API Key

## Installation

1. Navigate to this directory.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Set your Gemini API Key. You can export it as an environment variable:
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```
   Or modify `config.py`.

2. (Optional) Adjust `PROJECT_ROOT` in `config.py` if you want to run the agent on a specific project by default. By default, it uses the current directory.

## Usage

1. **Index your codebase**:
   Before asking questions, index the code to enable semantic search.
   ```bash
   python -m agent.indexer /path/to/your/project
   ```
   To index the current directory:
   ```bash
   python -m agent.indexer .
   ```
   This creates a `chroma_db` directory containing the embeddings.

2. **Run the Agent**:
   Interactive mode:
   ```bash
   python run.py
   ```
   Or provide a query directly:
   ```bash
   python run.py "How does the authentication middleware work?"
   ```

## Available Tools

- `search_code(query)`: Semantic search for code snippets.
- `read_file(path)`: Read file content.
- `write_file(path, content)`: Write file (with confirmation and backup).
- `list_directory(path)`: List files in a directory.
- `run_command(command)`: Run shell commands (whitelisted: pytest, git, python, npm, node, make). Secure execution without shell.
- `get_code_structure()`: Get a tree view of the project.
- `ask_user(question)`: Ask the user for input.

## Troubleshooting

- **ImportError: ... tree_sitter ...**: Ensure you have `tree-sitter==0.21.3` installed as specified in `requirements.txt`.
- **API Key Error**: Make sure `GEMINI_API_KEY` is set correctly.
