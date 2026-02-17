import os
import config

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
