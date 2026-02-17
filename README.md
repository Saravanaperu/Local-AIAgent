# Local-AIAgent
Tasks for Jules AI Agent: Build a Local Codebase AI Agent with Gemini

Below is a structured set of tasks for Jules to automatically develop a custom AI agent that can understand, query, and modify your local codebase using Google's Gemini models. Each task includes clear goals, step‑by‑step instructions, and expected outcomes. Jules should execute them sequentially.

---

Task 1: Project Setup and Dependencies

Goal: Create the project directory, set up a Python virtual environment, and install all required packages.

Steps:

1. Create a new directory named local-code-agent (or any name you prefer) and navigate into it.
2. Initialize a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. Create a requirements.txt file with the following content:
   ```
   google-generativeai
   chromadb
   sentence-transformers
   tree-sitter
   tree-sitter-languages
   ```
4. Install the packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Create a basic folder structure:
   ```
   local-code-agent/
   ├── agent/
   │   ├── __init__.py
   │   ├── core.py          # Main agent loop
   │   ├── tools.py          # Tool implementations
   │   ├── indexer.py        # Code indexing logic
   │   └── utils.py          # Helper functions (path validation, etc.)
   ├── config.py             # Configuration (API key, project root)
   ├── run.py                # Entry point script
   └── tests/                # For testing later
   ```
6. Initialize a Git repository (optional but recommended):
   ```bash
   git init
   echo "venv/" > .gitignore
   echo "__pycache__/" >> .gitignore
   echo "*.pyc" >> .gitignore
   echo "chroma_db/" >> .gitignore
   ```

Expected Outcome: A clean Python environment with all dependencies installed and a basic project skeleton.

---

Task 2: Code Indexing System

Goal: Implement a module that can scan a local codebase, parse source files into meaningful chunks (functions, classes, etc.), generate embeddings, and store them in ChromaDB for semantic search.

Files to create/modify:

· agent/indexer.py
· config.py

Steps:

1. In config.py, define:
   ```python
   import os
   
   PROJECT_ROOT = os.path.abspath(".")  # Will be overridden by user input later
   CHROMA_PERSIST_DIR = "./chroma_db"
   EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # or use Gemini embeddings later
   ```
2. In agent/indexer.py, write a function get_parser_for_file(ext) that returns a tree‑sitter parser for the given file extension. Use tree_sitter_languages.get_language(ext).
3. Implement extract_chunks(file_path) that:
   · Reads the file content.
   · Uses the appropriate parser to obtain an AST.
   · Traverses the AST to extract:
     · Function definitions (including docstrings and body)
     · Class definitions
     · Top‑level comments or large blocks (if needed)
   · For each chunk, store:
     · id: unique string (e.g., filepath:start_line)
     · text: the source code snippet
     · metadata: file path, start/end lines, type (function/class/block)
4. Implement index_codebase(directory) that:
   · Recursively walks directory (ignore .git, venv, __pycache__).
   · For each file with a supported extension (.py, .js, .java, etc. – start with Python only for simplicity), call extract_chunks.
   · For each chunk, generate an embedding using sentence_transformers.SentenceTransformer(EMBEDDING_MODEL).encode(chunk_text).
   · Add the chunk to ChromaDB (persist to CHROMA_PERSIST_DIR).
5. Write a function search_code(query, n_results=5) that:
   · Embeds the query using the same model.
   · Queries ChromaDB for the most similar chunks.
   · Returns a formatted string with the results (file, lines, snippet).
6. Add a if __name__ == "__main__": block to indexer.py that indexes a given directory (e.g., sys.argv[1]) for testing.

Testing: Run python -m agent.indexer /path/to/small/test/project and verify that ChromaDB is populated and search returns relevant snippets.

Expected Outcome: A working code index that can retrieve relevant code chunks given a natural language query.

---

Task 3: Implement Core Tools

Goal: Create the set of tools that the agent can use to interact with the codebase and the system. Each tool must be a Python function with clear input/output, and include safety validations.

Files to create/modify:

· agent/tools.py
· agent/utils.py (for helper functions)

Steps:

1. In agent/utils.py, implement:
   · is_path_safe(requested_path, base_dir): ensures requested_path is within base_dir (use os.path.abspath and os.path.commonpath).
   · get_project_root(): read from config.PROJECT_ROOT or allow override.
2. In agent/tools.py, define the following functions (all return a string result):
   a. search_code(query: str) -> str
   · Calls indexer.search_code(query) and returns formatted results.
   b. read_file(path: str) -> str
   · Validate path with is_path_safe relative to project root.
   · Read the file and return its content (or error if not found/unsafe).
   c. write_file(path: str, content: str) -> str
   · Validate path.
   · Create a backup of the original file (if exists) in a .backups/ folder.
   · Write the new content.
   · Return success message with the path.
   d. run_command(command: str) -> str
   · Important: Whitelist allowed commands (e.g., pytest, git, python, npm, make). Use a list ALLOWED_COMMANDS = ["pytest", "git", "python", "npm", "node", "make"].
   · Parse the command to extract the base executable; reject if not in whitelist.
   · Use subprocess.run(command, shell=True, cwd=project_root, capture_output=True, text=True, timeout=30).
   · Return stdout/stderr or timeout message.
   e. list_directory(path: str) -> str
   · Validate path, list files/directories (non‑recursive), return as bullet list.
   f. get_code_structure() -> str
   · Use os.walk to generate a tree‑like view of the project (optionally using tree command if available, else simple indented list).
   g. ask_user(question: str) -> str
   · Print the question to the console and wait for user input. Return the input string.
3. Create a dictionary TOOL_FUNCTIONS that maps tool names to the functions above.
4. Write a function execute_tool(name: str, args: dict) -> str that looks up the function, calls it with **args, and returns the result string.

Testing: Manually test each tool by calling execute_tool from a Python shell with appropriate arguments.

Expected Outcome: A complete set of tools that can be invoked by the agent, with proper safety checks and error handling.

---

Task 4: Integrate Gemini API and Function Calling

Goal: Set up the Gemini client, define the tool schemas for Gemini’s function calling, and create the dispatch mechanism.

Files to create/modify:

· config.py (add API key)
· agent/core.py

Steps:

1. In config.py, add:
   ```python
   GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")  # User will set env var or edit
   GEMINI_MODEL = "gemini-1.5-pro"  # or "gemini-1.5-flash"
   ```
2. In agent/core.py, import the Gemini library and tools.
3. Write a function get_tool_schemas() that returns a list of function declarations in the format expected by Gemini:
   ```python
   {
       "name": "search_code",
       "description": "Search the codebase for relevant code snippets.",
       "parameters": {
           "type": "object",
           "properties": {
               "query": {"type": "string", "description": "The search query."}
           },
           "required": ["query"]
       }
   }
   ```
   Do this for all tools defined in Task 3. For tools with complex parameters (e.g., write_file), include all properties.
4. Initialize the Gemini model with the tools:
   ```python
   import google.generativeai as genai
   genai.configure(api_key=config.GEMINI_API_KEY)
   model = genai.GenerativeModel(
       model_name=config.GEMINI_MODEL,
       tools=get_tool_schemas()
   )
   ```
5. Write a function call_gemini_with_history(history) that sends the conversation history to Gemini and returns the response.

Testing: Try a simple call to Gemini with a tool declaration and verify that the model returns a function_call when appropriate.

Expected Outcome: Gemini is properly integrated and can propose tool calls based on the user’s request.

---

Task 5: Build the Agent Loop

Goal: Implement the main ReAct loop that:

· Accepts a user query.
· Retrieves initial context using search_code.
· Enters a loop (max N iterations) of: call Gemini, execute any tool calls, append results to history, continue until Gemini returns a final text answer.

Files to create/modify:

· agent/core.py
· run.py

Steps:

1. In core.py, define a class CodeAgent (or just a function run_agent(user_query)).
2. Inside the function:
   · Initialize an empty history list (list of dicts with role and parts).
   · Add a system prompt (as a separate message with role user or system – Gemini doesn't have a system role, so prepend it as a user message). Example:
     ```
     You are an AI assistant that helps developers with their local codebase. You have access to the following tools: ... Always think step by step. Use tools to gather information. When you have enough information, provide a final answer.
     ```
   · Perform an initial search using the user query: context = search_code(user_query). If context is not empty, add it to the history as a system/user message.
   · Append the actual user query as a user message.
   · Set max_iterations = 10.
   · For i in range(max_iterations):
     · Call call_gemini_with_history(history).
     · Get the response part.
     · If there is a function_call:
       · Extract name and args.
       · Execute the tool via execute_tool(name, args) to get a result string.
       · Append the function call part to history.
       · Append a new message with role function, name, and result as content.
       · Continue loop.
     · Else (text response):
       · Return the text as final answer.
   · If loop exits without final answer, return a message asking user to refine query.
3. In run.py, create a simple command‑line interface:
   ```python
   from agent.core import run_agent
   import sys
   
   if __name__ == "__main__":
       if len(sys.argv) > 1:
           query = " ".join(sys.argv[1:])
       else:
           query = input("Ask me about your codebase: ")
       answer = run_agent(query)
       print("\n=== Agent Answer ===\n")
       print(answer)
   ```

Testing: Run a simple query like run.py "What functions are in utils.py?" and watch the agent interact. Initially, it may not work perfectly, but the loop should function.

Expected Outcome: A working agent that can handle multi‑turn interactions, call tools, and return answers.

---

Task 6: Add User Interaction and Safety Confirmations

Goal: Enhance the agent with interactive confirmations for dangerous operations (file writes, command execution) and improve path validation.

Files to modify:

· agent/tools.py (update write_file, run_command)
· agent/core.py (maybe add a confirmation step before executing sensitive tools)

Steps:

1. Modify write_file to:
   · Show a preview of the changes (first few lines) and ask for confirmation using input().
   · Only proceed if user types 'y' or 'yes'.
   · Return a message indicating cancellation if user refuses.
2. Modify run_command to:
   · Display the full command and ask for confirmation before executing.
   · If not confirmed, return "Command cancelled by user."
3. In core.py, before executing any tool, you could optionally print which tool is about to be called and its arguments, and ask for confirmation (but this might be too intrusive). Instead, rely on the tool‑level confirmations for sensitive actions.
4. Ensure all file operations create backups before overwriting (implement backup function in utils.py).

Testing: Try asking the agent to modify a file or run a command and verify that it prompts for confirmation.

Expected Outcome: The agent is safe to use on a real codebase, with user confirmation for any destructive or external actions.

---

Task 7: Testing and Debugging

Goal: Thoroughly test the agent on a small, controlled codebase (e.g., a simple Python script or a small project) and fix any bugs.

Steps:

1. Create a tests/ directory with a sample project (e.g., a few Python files with functions, classes, and a test file).
2. Write test queries that cover all tools and common scenarios:
   · "Show me the content of main.py"
   · "Search for functions that handle user input"
   · "Add a docstring to the function calculate in math_utils.py"
   · "Run the tests"
   · "List all Python files"
3. Run the agent with each query and verify:
   · Correct tool calls
   · Proper handling of errors (e.g., file not found)
   · Correct final answers
   · Safety confirmations appear when expected
4. Fix any issues encountered:
   · If Gemini misuses tools, refine tool descriptions.
   · If context retrieval is insufficient, adjust chunking or embedding model.
   · If loops get stuck, implement a timeout or better prompt.

Expected Outcome: A robust agent that reliably handles a variety of tasks on a test codebase.

---

Task 8: Documentation and Usage Instructions

Goal: Write clear documentation so that you (and others) can easily use the agent.

Files to create:

· README.md
· example_queries.md (optional)

Steps:

1. In README.md, include:
   · Project overview and capabilities.
   · Prerequisites (Python 3.9+, Google API key with Gemini access).
   · Installation steps (clone, virtual env, install deps).
   · Configuration: how to set the API key (environment variable or edit config.py) and the target codebase path (modify config.PROJECT_ROOT or pass as argument).
   · Usage: python run.py "your query" or interactive mode.
   · List of available tools and their safety features.
   · Examples of common tasks.
   · Troubleshooting tips.
2. If desired, create example_queries.md with a list of sample queries to try.
3. Update config.py to read PROJECT_ROOT from an environment variable or command line argument for flexibility (optional improvement).

Expected Outcome: A well‑documented project that anyone can set up and use.

---

Final Notes for Jules

· After completing all tasks, ensure the agent runs without errors and performs as expected.
· If any step is unclear, make reasonable assumptions (e.g., default project root as the current directory) and document them.
· Commit changes frequently with meaningful messages.
· When done, provide a summary of the completed project and any outstanding issues or future improvements.

Now, Jules, proceed with Task 1 and let me know when you’ve completed it, or if you need clarification on any step.
