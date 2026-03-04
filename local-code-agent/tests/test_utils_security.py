import unittest
import os
import shutil
import tempfile
import sys

# Add local-code-agent to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from agent.utils import is_path_safe

class TestUtilsSecurity(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.base_dir = os.path.join(self.test_dir, "base")
        os.makedirs(self.base_dir)

        self.outside_dir = os.path.join(self.test_dir, "outside")
        os.makedirs(self.outside_dir)

        self.secret_file = os.path.join(self.outside_dir, "secret.txt")
        with open(self.secret_file, "w") as f:
            f.write("sensitive data")

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_is_path_safe_blocks_symlink_traversal(self):
        # Create a symlink inside base_dir pointing to outside_dir
        symlink_path = os.path.join(self.base_dir, "malicious_link")
        os.symlink(self.outside_dir, symlink_path)

        path_to_check = os.path.join(symlink_path, "secret.txt")

        # This should be False if the vulnerability is fixed
        self.assertFalse(is_path_safe(path_to_check, self.base_dir),
                         "is_path_safe should block paths through symlinks pointing outside base_dir")

    def test_is_path_safe_allows_normal_paths(self):
        safe_file = os.path.join(self.base_dir, "safe.txt")
        with open(safe_file, "w") as f:
            f.write("safe data")

        self.assertTrue(is_path_safe(safe_file, self.base_dir))
        self.assertTrue(is_path_safe("safe.txt", self.base_dir))

    def test_is_path_safe_blocks_dot_dot_traversal(self):
        traversal_path = os.path.join(self.base_dir, "..", "outside", "secret.txt")
        self.assertFalse(is_path_safe(traversal_path, self.base_dir))

if __name__ == "__main__":
    unittest.main()
