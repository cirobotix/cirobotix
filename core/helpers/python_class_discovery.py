import ast
from pathlib import Path


class PythonClassDiscovery:
    def find_primary_class_name(self, file_path: Path) -> str:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

        for node in tree.body:
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                return node.name

        raise ValueError(f"No public class found in file: {file_path}")
