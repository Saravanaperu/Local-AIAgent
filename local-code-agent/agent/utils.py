import os
import config
import json
import re

def get_project_root():
    return config.PROJECT_ROOT

def is_path_safe(requested_path, base_dir=None):
    if base_dir is None:
        base_dir = get_project_root()

    # Resolve absolute paths
    # Handle relative paths properly relative to CWD if not absolute
    if not os.path.isabs(requested_path):
        requested_path = os.path.abspath(requested_path)

    base_dir = os.path.abspath(base_dir)

    # Check if requested path is inside base_dir
    return os.path.commonpath([base_dir, requested_path]) == base_dir

def extract_json_from_text(text):
    """
    Robustly extracts JSON from text, handling markdown code blocks and mixed content.
    """
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in markdown
    # Look for ```json ... ``` or just ``` ... ```
    # Using regex to find the content inside the blocks
    # Flags: DOTALL to match newlines
    json_block_pattern = r"```(?:json)?\s*(.*?)\s*```"
    match = re.search(json_block_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # If regex fails (e.g. unclosed block or no block but just braces), try to find the outermost braces
    # This is a fallback
    # Find first '{' or '['
    start_brace = text.find('{')
    start_bracket = text.find('[')

    if start_brace == -1 and start_bracket == -1:
        return None

    # Determine which one comes first
    if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
        start_index = start_brace
        end_char = '}'
    else:
        start_index = start_bracket
        end_char = ']'

    # Find the last matching closing brace
    # This simple logic might fail with nested structures if not careful, but json.loads will validate it.
    # Actually, rfind is better for the last occurrence.
    end_index = text.rfind(end_char)

    if end_index != -1 and end_index > start_index:
        candidate = text[start_index:end_index+1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

    return None
