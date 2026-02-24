import os
import sys
import chromadb
from agent.embedding import get_embedding_model
from tree_sitter_languages import get_language, get_parser
import config

# Initialize ChromaDB client and collection
chroma_client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
# Initialize embedding model
# Load model once
print("Loading embedding model...")
embedding_model = get_embedding_model(config.EMBEDDING_MODEL)

collection = chroma_client.get_or_create_collection(name="code_chunks")

def get_parser_for_file(ext):
    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
    }
    lang_name = ext_map.get(ext)
    if not lang_name:
        return None, None

    try:
        language = get_language(lang_name)
        parser = get_parser(lang_name)
        return parser, language
    except Exception as e:
        # print(f"No parser found for extension {ext} ({lang_name}): {e}")
        return None, None

def extract_chunks(file_path):
    ext = os.path.splitext(file_path)[1]
    parser, language = get_parser_for_file(ext)
    if not parser:
        return []

    try:
        if os.path.getsize(file_path) > config.MAX_FILE_SIZE:
            print(f"Warning: Skipping file {file_path} because it exceeds the maximum size of {config.MAX_FILE_SIZE} bytes.")
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []

    tree = parser.parse(bytes(content, "utf8"))
    root_node = tree.root_node

    chunks = []

    # Query for Python
    if ext == ".py":
        query_scm = """
        (function_definition) @function
        (class_definition) @class
        """
    elif ext in [".js", ".ts", ".jsx", ".tsx"]:
         query_scm = """
        (function_declaration) @function
        (class_declaration) @class
        (method_definition) @method
        """
    elif ext == ".java":
        query_scm = """
        (method_declaration) @function
        (class_declaration) @class
        """
    elif ext in [".cpp", ".c", ".h"]:
        query_scm = """
        (function_definition) @function
        (class_specifier) @class
        (struct_specifier) @struct
        """
    else:
        # Fallback for other supported languages or unexpected ones
        chunks.append({
            "id": f"{file_path}:0",
            "text": content,
            "metadata": {
                "file_path": file_path,
                "start_line": 0,
                "end_line": len(content.splitlines()),
                "type": "file"
            }
        })
        return chunks

    try:
        query = language.query(query_scm)
        captures = query.captures(root_node)

        # Deduplicate captures if needed, or handle overlaps
        # For now, simplistic approach

        processed_ranges = set()

        for node, _ in captures:
            start_line = node.start_point[0]
            end_line = node.end_point[0]

            # Avoid duplicates if multiple captures point to same node
            if (start_line, end_line) in processed_ranges:
                continue
            processed_ranges.add((start_line, end_line))

            text = content[node.start_byte:node.end_byte]

            chunks.append({
                "id": f"{file_path}:{start_line}",
                "text": text,
                "metadata": {
                    "file_path": file_path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "type": node.type
                }
            })

    except Exception as e:
        print(f"Error querying AST for {file_path}: {e}")

    # If no chunks found (e.g. script without functions), add whole file
    if not chunks:
         chunks.append({
            "id": f"{file_path}:0",
            "text": content,
            "metadata": {
                "file_path": file_path,
                "start_line": 0,
                "end_line": len(content.splitlines()),
                "type": "file"
            }
        })

    return chunks

def index_codebase(directory):
    for root, dirs, files in os.walk(directory):
        # Ignore hidden directories and venv
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__', 'chroma_db', 'site-packages']]

        dir_chunks = []
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.h', '.c')):
                file_path = os.path.join(root, file)
                chunks = extract_chunks(file_path)
                dir_chunks.extend(chunks)

        if dir_chunks:
            # Batch encoding and upserting for the whole directory
            # Using a batch size of 100 to stay within common API limits
            batch_size = 100
            for i in range(0, len(dir_chunks), batch_size):
                batch = dir_chunks[i:i + batch_size]
                ids = [c["id"] for c in batch]
                documents = [c["text"] for c in batch]
                metadatas = [c["metadata"] for c in batch]
                embeddings = embedding_model.encode(documents, task_type="retrieval_document").tolist()

                collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas,
                    embeddings=embeddings
                )

def search_code(query, n_results=5):
    query_embedding = embedding_model.encode(query, task_type="retrieval_query").tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    formatted_results = []
    if results['documents']:
        for i, doc in enumerate(results['documents'][0]):
            meta = results['metadatas'][0][i]
            formatted_results.append(f"File: {meta['file_path']}\nLines: {meta['start_line']}-{meta['end_line']}\nSnippet:\n{doc}\n")

    return "\n".join(formatted_results)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
        print(f"Indexing directory: {directory}")
        index_codebase(directory)
        print("Indexing complete.")

        # Test search
        test_query = "function to parse file"
        print(f"\nTesting search '{test_query}':")
        print(search_code(test_query))
    else:
        print("Usage: python -m agent.indexer <directory_to_index>")
